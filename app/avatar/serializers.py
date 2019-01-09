from rest_framework import serializers

from .models import BaseAvatar


class BaseAvatarSerializer(serializers.ModelSerializer):
    """Handle serializing the BaseAvatar object."""

    class Meta:
        """Define the milestone serializer metadata."""

        model = BaseAvatar
        fields = ('pk', 'avatar_url', 'active')


class CustomAvatarSerializer(serializers.ModelSerializer):
    """Handle serializing the CustomAvatar object."""

    class Meta:
        """Define the milestone serializer metadata."""

        model = BaseAvatar
        fields = ('pk', 'avatar_url', 'active')
