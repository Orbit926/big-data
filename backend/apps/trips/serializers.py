"""
Serializers for the Trips app.

TripSerializer
──────────────
Full CRUD serializer.  `organizer` and `participants` are exposed as
StringRelatedField (read-only) so the response shows usernames instead
of raw PKs.  The write-side of participants accepts a list of PKs via
the `participant_ids` write-only field.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Trip

User = get_user_model()


class TripSerializer(serializers.ModelSerializer):
    # ── Read-only display fields ───────────────────────────────────────────
    organizer = serializers.StringRelatedField(read_only=True)
    participants = serializers.StringRelatedField(many=True, read_only=True)

    # ── Write-only field to set participants by PK ─────────────────────────
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="participants",
        help_text="List of user PKs to add as participants.",
    )

    class Meta:
        model = Trip
        fields = [
            "id",
            "organizer",
            "name",
            "description",
            "start_date",
            "end_date",
            "participants",
            "participant_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organizer", "created_at", "updated_at"]
