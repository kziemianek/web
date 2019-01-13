# -*- coding: utf-8 -*-
"""Define the Avatar models.

Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
import logging
from secrets import token_hex
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext_lazy as _
from .exceptions import AvatarDuplicateError

from economy.models import SuperModel
from svgutils.compose import Figure, Line
from PIL import Image

from .utils import build_avatar_component, convert_img, convert_wand, get_upload_filename, get_temp_image_file, dhash

logger = logging.getLogger(__name__)


class BaseAvatar(SuperModel):
    """Store the options necessary to render a Gitcoin avatar."""

    ICON_SIZE = (215, 215)

    active = models.BooleanField(default=False)
    profile = models.ForeignKey(
        'dashboard.Profile', null=True, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_related", blank=True
    )
    svg = models.FileField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The avatar SVG.')
    )
    png = models.ImageField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The avatar PNG.'),
    )
    hash= models.CharField(max_length=16)

    @property
    def avatar_url(self):
        """Return the appropriate avatar URL."""
        if self.png:
            return self.png.url
        if self.svg:
            return self.svg.url
        return ''

    def get_avatar_url(self):
        """Get the Avatar URL.

        """
        try:
            self.svg.url
        except ValueError:
            pass

        try:
            handle = self.profile.handle
        except Exception:
            handle = 'Self'

        return f'{settings.BASE_URL}dynamic/avatar/{handle}'

    @staticmethod
    def calculate_hash(image):
        return dhash(image)

    def convert_field(self, source, input_fmt, output_fmt):
        """Handle converting from the source field to the target based on format."""
        try:
            # Convert the provided source to the specified output and store in BytesIO.
            if output_fmt == 'svg':
                tmpfile_io = convert_wand(source, input_fmt=input_fmt, output_fmt=output_fmt)
            else:
                tmpfile_io = convert_img(source, input_fmt=input_fmt, output_fmt=output_fmt)
            if self.profile:
                png_name = self.profile.handle
            else:
                png_name = token_hex(8)

            if tmpfile_io:
                converted_avatar = ContentFile(tmpfile_io.getvalue())
                converted_avatar.name = f'{png_name}.{output_fmt}'
                return converted_avatar
        except Exception as e:
            logger.error('Error: (%s) - Avatar PK: (%s)', str(e), self.id)

    def determine_response(self, use_svg=True):
        """Determine the content type and file to serve.

        Args:
            use_svg (bool): Whether or not to use SVG format.

        """
        if not use_svg:
            return self.png.file, 'image/png'
        else:
            return self.svg.file, 'image/svg+xml'


class CustomAvatar(BaseAvatar):
    recommended_by_staff = models.BooleanField(default=False)
    config = JSONField(default=dict, help_text=_('The JSON configuration.'))

    @classmethod
    def create(cls, profile, config_json):
        avatar = cls(
            profile=profile,
            config=config_json,
        )
        avatar.create_from_config()
        avatar.png = avatar.convert_field(avatar.svg, 'svg', 'png')
        return avatar

    def create_from_config(self):
        """Create an avatar SVG from the configuration.

        TODO:
            * Deprecate in favor of request param based view using templates.

        """
        payload = self.config
        icon_width = self.ICON_SIZE[0]
        icon_height = self.ICON_SIZE[1]

        components = [
            icon_width, icon_height,
            Line([(0, icon_height / 2), (icon_width, icon_height / 2)],
                 width=f'{icon_height}px',
                 color=f"#{payload.get('Background')}")
        ]

        for k, v in payload.items():
            if k not in ['Background', 'ClothingColor', 'HairColor', 'SkinTone']:
                components.append(
                    build_avatar_component(f"{v.get('component_type')}/{v.get('svg_asset')}", self.ICON_SIZE)
                )

        with NamedTemporaryFile(mode='w+', suffix='.svg') as tmp:
            profile = None
            avatar = Figure(*components)
            avatar.save(tmp.name)
            with open(tmp.name) as file:
                # what if there is no profile ?
                if self.profile:
                    profile = self.profile

                svg_name = profile.handle if profile and profile.handle else token_hex(8)
                self.svg.save(f"{svg_name}.svg", File(file), save=True)

    # do we need fields below ?
    def get_color(self, key='Background', with_hashbang=False):
        if key not in ['Background', 'ClothingColor', 'HairColor', 'ClothingColor', 'SkinTone']:
            return None
        return f"{'#' if with_hashbang else ''}{self.config.get(key)}"

    @property
    def background_color(self):
        return self.get_color() or 'FFF'

    @property
    def clothing_color(self):
        return self.get_color(key='ClothingColor') or 'CCC'

    @property
    def hair_color(self):
        return self.get_color(key='HairColor') or '4E3521'

    @property
    def skin_tone(self):
        return self.get_color(key='SkinTone') or 'EEE3C1'

    def to_dict(self):
        return self.config
#     end do we need


class SocialAvatar(BaseAvatar):
    source = models.CharField(max_length=255, db_index=True)

    @classmethod
    def github_avatar(cls, profile, avatar_img):
        hash = BaseAvatar.calculate_hash(avatar_img)
        if BaseAvatar.objects.filter(profile=profile, hash=hash):
            raise AvatarDuplicateError()
        avatar = cls(
            profile=profile,
            source='GITHUB',
            hash = BaseAvatar.calculate_hash(avatar_img)
        )
        avatar.png.save(f'{profile.handle}.png', ContentFile(get_temp_image_file(avatar_img).getvalue()), save=True)        
        avatar.svg = avatar.convert_field(avatar.png, 'png', 'svg')
        return avatar

class Avatar(SuperModel):
    """Store the options necessary to render a Gitcoin avatar."""

    class Meta:
        """Define the metadata associated with Avatar."""

        verbose_name_plural = 'Avatars'

    config = JSONField(default=dict, help_text=_('The JSON configuration of the custom avatar.'), )
    # Github Avatar
    github_svg = models.FileField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The Github avatar SVG.')
    )
    png = models.ImageField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The Github avatar PNG.'),
    )
    # Custom Avatar
    custom_avatar_png = models.ImageField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The custom avatar PNG.'),
    )
    svg = models.FileField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The custom avatar SVG.'),
    )

    use_github_avatar = models.BooleanField(default=True)

    # Change tracking attributes
    __previous_svg = None
    __previous_png = None

    def __init__(self, *args, **kwargs):
        super(Avatar, self).__init__(*args, **kwargs)
        self.__previous_svg = self.svg
        self.__previous_png = self.png

    def __str__(self):
        """Define the string representation of Avatar."""
        return f"Avatar ({self.pk}) - Profile: {self.profile_set.last().handle if self.profile_set.exists() else 'N/A'}"
