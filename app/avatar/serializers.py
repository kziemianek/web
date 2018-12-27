from rest_framework import serializers

from .models import CustomAvatar


class CustomAvatarSerializer(serializers.ModelSerializer):
    """Handle serializing the CustomAvatar object."""

    class Meta:
        """Define the milestone serializer metadata."""

        model = CustomAvatar
        fields = ('pk', 'avatar_url')