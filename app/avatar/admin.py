# -*- coding: utf-8 -*-
"""Define the Avatar admin layout.

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
from django.contrib import admin
from django.utils.safestring import mark_safe

from dashboard.models import Profile
from avatar.models import CustomAvatar

class GeneralAdmin(admin.ModelAdmin):
    """Define the GeneralAdmin administration layout."""

    ordering = ['-id']
    list_display = ['created_on', '__str__']


class AvatarAdmin(GeneralAdmin):
    """Define the Avatar administration layout."""

    ordering = ['-id']
    fields = [
        'config', 'svg_asset', 'png_asset', 'created_on', 'modified_on', 'profile'
    ]
    readonly_fields = ['svg_asset', 'png_asset', 'created_on', 'modified_on']
    search_fields = ['profile__handle']

    def svg_asset(self, instance):
        """Define the avatar SVG tag to be displayed in the admin."""
        if instance.svg and instance.svg.url:
            return mark_safe(f'<img src="{instance.svg.url}" width="150" height="150" />')
        return mark_safe('N/A')

    def png_asset(self, instance):
        """Define the avatar PNG tag to be displayed in the admin."""
        if instance.png and instance.png.url:
            return mark_safe(f'<img src="{instance.png.url}" width="150" height="150" />')
        return mark_safe('N/A')

    svg_asset.short_description = 'SVG Asset'
    png_asset.short_description = 'PNG Asset'


admin.site.register(CustomAvatar, AvatarAdmin)
