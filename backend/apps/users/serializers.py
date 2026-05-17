"""
Serializers for the Users app.

Responsibility: expose and update user *profile* data only.
Authentication logic lives in apps.authentication.

UserPublicSerializer   — read-only public profile (for other users to see)
UserProfileSerializer  — full profile of the authenticated user (read + write)
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Read-only representation of a user's public profile.
    Used for endpoints that other users can query (e.g. GET /api/users/<id>/).
    """

    class Meta:
        model = User
        fields = ["id", "username", "avatar", "date_joined"]
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Full profile serializer for the authenticated user.
    Allows updating first_name, last_name, bio and avatar.
    username and email are read-only to prevent accidental overwrites
    (a dedicated change-email/change-username flow should exist separately).
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "avatar",
            "created_at",
            "date_joined",
            "is_staff",
        ]
        read_only_fields = ["id", "username", "email", "created_at", "date_joined", "is_staff"]
