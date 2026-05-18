"""
Serializers for the Expenses app.

ExpenseUserSerializer        — minimal non-sensitive user info (consistent with JamUserSerializer)
ExpenseSplitSerializer       — read-only split with nested user
ExpenseListSerializer        — compact view for list endpoints
ExpenseDetailSerializer      — full view with embedded splits
ExpenseCreateSerializer      — handles both equal and custom split creation
ExpenseUpdateSerializer      — allows editing title/description/category only
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Expense, ExpenseSplit

User = get_user_model()


# ── Nested user (non-sensitive) ───────────────────────────────────────────────


class ExpenseUserSerializer(serializers.ModelSerializer):
    """Minimal, non-sensitive user info — consistent with JamUserSerializer."""

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]
        read_only_fields = fields


# ── Split serializers ─────────────────────────────────────────────────────────


class ExpenseSplitSerializer(serializers.ModelSerializer):
    """Read-only representation of a single split."""

    user = ExpenseUserSerializer(read_only=True)

    class Meta:
        model = ExpenseSplit
        fields = ["id", "user", "amount_owed", "status", "paid_at", "created_at", "updated_at"]
        read_only_fields = fields


# ── Expense serializers ───────────────────────────────────────────────────────


class ExpenseListSerializer(serializers.ModelSerializer):
    """Compact representation used in list responses."""

    paid_by = ExpenseUserSerializer(read_only=True)
    created_by = ExpenseUserSerializer(read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id", "jam", "title", "amount", "currency",
            "split_type", "category", "paid_by", "created_by",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = fields


class ExpenseDetailSerializer(serializers.ModelSerializer):
    """Full representation with embedded splits."""

    paid_by = ExpenseUserSerializer(read_only=True)
    created_by = ExpenseUserSerializer(read_only=True)
    splits = ExpenseSplitSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id", "jam", "title", "description", "amount", "currency",
            "split_type", "category", "paid_by", "created_by",
            "is_active", "splits", "created_at", "updated_at",
        ]
        read_only_fields = fields


# ── Custom split input ────────────────────────────────────────────────────────


class SplitInputSerializer(serializers.Serializer):
    """One entry in a custom split list: user_id + amount_owed."""

    user_id = serializers.IntegerField()
    amount_owed = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.00"))


# ── Create serializer ─────────────────────────────────────────────────────────


class ExpenseCreateSerializer(serializers.Serializer):
    """
    Write-only serializer for creating an Expense.

    For equal splits:    provide `participant_ids` (list of user PKs).
    For custom splits:   provide `splits` (list of {user_id, amount_owed}).

    `paid_by` defaults to the requesting user if omitted.
    `jam` and `created_by` are injected by the view — never accepted from the client.
    """

    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    currency = serializers.CharField(max_length=3, required=False, default="MXN")
    split_type = serializers.ChoiceField(choices=Expense.SplitType.choices, default=Expense.SplitType.EQUAL)
    category = serializers.ChoiceField(choices=Expense.Category.choices, default=Expense.Category.OTHER)
    paid_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="paid_by",
        required=False,
        help_text="Defaults to the requesting user.",
    )

    # equal-split mode
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Required when split_type=equal.",
    )

    # custom-split mode
    splits = SplitInputSerializer(
        many=True,
        required=False,
        help_text="Required when split_type=custom.",
    )

    def validate(self, data):
        split_type = data.get("split_type", Expense.SplitType.EQUAL)

        if split_type == Expense.SplitType.EQUAL:
            if not data.get("participant_ids"):
                raise serializers.ValidationError(
                    {"participant_ids": "Required when split_type is 'equal'."}
                )
            data.pop("splits", None)

        elif split_type == Expense.SplitType.CUSTOM:
            if not data.get("splits"):
                raise serializers.ValidationError(
                    {"splits": "Required when split_type is 'custom'."}
                )
            data.pop("participant_ids", None)

        return data


# ── Update serializer ─────────────────────────────────────────────────────────


class ExpenseUpdateSerializer(serializers.ModelSerializer):
    """
    Partial-update serializer.
    Only title, description and category are editable after creation.
    Amount, paid_by, split_type and splits are immutable to avoid
    financial inconsistencies.
    """

    class Meta:
        model = Expense
        fields = ["title", "description", "category"]
