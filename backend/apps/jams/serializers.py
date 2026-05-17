"""
Serializers for the JAMs app.

JamDetailSerializer         → read-only rich representation of a JAM.
JamCreateUpdateSerializer   → write-only (create / PATCH).
JamMemberSerializer         → read-only representation of a membership.
JamMemberCreateSerializer   → add a member to a JAM.
JamMemberUpdateSerializer   → change role or status of an existing member.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Jam, JamMember

User = get_user_model()


# ── Nested user representation (non-sensitive) ────────────────────────────────


class JamUserSerializer(serializers.ModelSerializer):
    """Minimal, non-sensitive user info embedded in JAM responses."""

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "avatar"]
        read_only_fields = fields


# ── JamMember serializers ─────────────────────────────────────────────────────


class JamMemberSerializer(serializers.ModelSerializer):
    """Read-only membership record — safe to expose."""

    user = JamUserSerializer(read_only=True)

    class Meta:
        model = JamMember
        fields = ["id", "user", "role", "status", "joined_at"]
        read_only_fields = fields


class JamMemberCreateSerializer(serializers.ModelSerializer):
    """
    Add a new member to a JAM.

    The `jam` field is injected by the view (from the URL); do not expose it
    for free-form client input.
    """

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        help_text="PK of the user to add.",
    )

    class Meta:
        model = JamMember
        fields = ["user_id", "role"]
        extra_kwargs = {
            "role": {"required": False},
        }

    def validate_role(self, value):
        allowed = [JamMember.Role.ADMIN, JamMember.Role.MEMBER]
        if value not in allowed:
            raise serializers.ValidationError(
                f"role must be one of {[r.value for r in allowed]}."
            )
        return value


class JamMemberUpdateSerializer(serializers.ModelSerializer):
    """Change role or status of an existing JamMember."""

    class Meta:
        model = JamMember
        fields = ["role", "status"]

    def validate_role(self, value):
        allowed = [JamMember.Role.ADMIN, JamMember.Role.MEMBER]
        if value not in allowed:
            raise serializers.ValidationError(
                f"role must be one of {[r.value for r in allowed]}."
            )
        return value

    def validate_status(self, value):
        allowed = [
            JamMember.Status.INVITED,
            JamMember.Status.ACTIVE,
            JamMember.Status.REMOVED,
        ]
        if value not in allowed:
            raise serializers.ValidationError(
                f"status must be one of {[s.value for s in allowed]}."
            )
        return value


# ── JAM serializers ───────────────────────────────────────────────────────────


class JamDetailSerializer(serializers.ModelSerializer):
    """
    Rich, read-only representation of a JAM.
    Embeds created_by as non-sensitive public data.
    """

    created_by = JamUserSerializer(read_only=True)
    trip_id = serializers.IntegerField(source="trip.id", read_only=True)

    class Meta:
        model = Jam
        fields = [
            "id",
            "trip_id",
            "name",
            "description",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class JamCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Writable serializer for create and partial-update.

    `trip` is never accepted from the request body — it is always
    injected by the view from the URL parameter.
    `created_by` is always set from request.user.
    """

    class Meta:
        model = Jam
        fields = ["name", "description", "is_active"]
        extra_kwargs = {
            "name": {"required": True},
            "description": {"required": False},
            "is_active": {"required": False},
        }
