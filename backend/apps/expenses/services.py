"""
Business logic for the Expenses app.

All permission checks delegate to apps.jams.services so that the source
of truth for JAM membership stays in one place.

Modules importing from here:
    from apps.expenses.services import (
        create_equal_expense,
        create_custom_expense,
        calculate_jam_expense_summary,
        can_view_expense,
        can_manage_expense,
        can_mark_split_paid,
        can_mark_split_pending,
        mark_split_paid,
        mark_split_pending,
    )
"""

from __future__ import annotations

import decimal
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django.db import transaction
from django.utils import timezone

# ── JAM permission helpers (single source of truth) ───────────────────────────
from apps.jams.services import is_jam_admin, is_jam_member


# ── Validation helpers ─────────────────────────────────────────────────────────


def validate_active_jam_member(user, jam) -> None:
    """
    Raise PermissionDenied (403) if the user is not an active JAM member.
    Used before any write operation on expenses.
    """
    from rest_framework.exceptions import PermissionDenied

    if not is_jam_member(user, jam):
        raise PermissionDenied("You must be an active JAM member to perform this action.")


def validate_expense_participants(jam, user_ids: list[int]) -> list:
    """
    Given a list of user PKs, return the corresponding User objects,
    validating that every one of them is an active JAM member.

    Raises ValidationError if any user is not in the JAM or does not exist.
    """
    from django.contrib.auth import get_user_model
    from rest_framework.exceptions import ValidationError
    from apps.jams.models import JamMember

    User = get_user_model()

    if not user_ids:
        raise ValidationError("At least one participant is required.")

    users = list(User.objects.filter(pk__in=user_ids))
    if len(users) != len(set(user_ids)):
        raise ValidationError("One or more user IDs are invalid.")

    active_member_ids = set(
        JamMember.objects
        .filter(jam=jam, status=JamMember.Status.ACTIVE)
        .values_list("user_id", flat=True)
    )

    non_members = [u for u in users if u.pk not in active_member_ids]
    if non_members:
        bad = [u.username for u in non_members]
        raise ValidationError(
            f"The following users are not active JAM members: {', '.join(bad)}"
        )

    return users


# ── Split math ─────────────────────────────────────────────────────────────────


def calculate_equal_splits(amount: Decimal, participant_count: int) -> list[Decimal]:
    """
    Divide `amount` equally among `participant_count` people.

    Returns a list of Decimal values where each element is the share for one
    participant.  The last element absorbs any rounding remainder so that
    sum(result) == amount exactly.
    """
    if participant_count <= 0:
        return []

    unit = Decimal("0.01")
    base = (amount / participant_count).quantize(unit, rounding=ROUND_HALF_UP)
    total_assigned = base * (participant_count - 1)
    last = amount - total_assigned

    return [base] * (participant_count - 1) + [last]


# ── Expense creation ────────────────────────────────────────────────────────────


@transaction.atomic
def create_equal_expense(jam, validated_data: dict, created_by) -> "Expense":
    """
    Create an Expense with split_type=EQUAL.

    Expected keys in validated_data:
      - title, description, amount, currency, category, paid_by
      - participant_ids: list[int]  (must all be active JAM members)

    The split for paid_by is auto-set to status=paid.
    """
    from .models import Expense, ExpenseSplit

    participant_ids = validated_data.pop("participant_ids")
    participants = validate_expense_participants(jam, participant_ids)

    # Remove split_type from data dict before spreading to avoid duplicate kwarg
    validated_data.pop("split_type", None)

    expense = Expense.objects.create(
        jam=jam,
        created_by=created_by,
        split_type=Expense.SplitType.EQUAL,
        **validated_data,
    )

    paid_by = validated_data["paid_by"]
    shares = calculate_equal_splits(validated_data["amount"], len(participants))

    for user, share in zip(participants, shares):
        status = ExpenseSplit.Status.PAID if user == paid_by else ExpenseSplit.Status.PENDING
        paid_at = timezone.now() if status == ExpenseSplit.Status.PAID else None
        ExpenseSplit.objects.create(
            expense=expense,
            user=user,
            amount_owed=share,
            status=status,
            paid_at=paid_at,
        )

    return expense


@transaction.atomic
def create_custom_expense(jam, validated_data: dict, created_by) -> "Expense":
    """
    Create an Expense with split_type=CUSTOM.

    Expected keys in validated_data:
      - title, description, amount, currency, category, paid_by
      - splits: list[dict] with keys {"user_id": int, "amount_owed": Decimal}

    Validation:
      - sum(amount_owed) must equal amount (within 0.01 tolerance)
      - All user_ids must be active JAM members
      - No duplicate user_ids

    The split for paid_by is auto-set to status=paid.
    """
    from rest_framework.exceptions import ValidationError
    from .models import Expense, ExpenseSplit

    splits_data: list[dict] = validated_data.pop("splits")
    user_ids = [s["user_id"] for s in splits_data]

    if len(user_ids) != len(set(user_ids)):
        raise ValidationError("Duplicate users in splits.")

    users_by_id = {u.pk: u for u in validate_expense_participants(jam, user_ids)}

    # Validate sum
    total = sum(Decimal(str(s["amount_owed"])) for s in splits_data)
    if abs(total - validated_data["amount"]) > Decimal("0.01"):
        raise ValidationError(
            f"Sum of splits ({total}) must equal the expense amount ({validated_data['amount']})."
        )

    validated_data.pop("split_type", None)

    expense = Expense.objects.create(
        jam=jam,
        created_by=created_by,
        split_type=Expense.SplitType.CUSTOM,
        **validated_data,
    )

    paid_by = validated_data["paid_by"]
    for s in splits_data:
        user = users_by_id[s["user_id"]]
        status = ExpenseSplit.Status.PAID if user == paid_by else ExpenseSplit.Status.PENDING
        paid_at = timezone.now() if status == ExpenseSplit.Status.PAID else None
        ExpenseSplit.objects.create(
            expense=expense,
            user=user,
            amount_owed=Decimal(str(s["amount_owed"])),
            status=status,
            paid_at=paid_at,
        )

    return expense


# ── Summary ────────────────────────────────────────────────────────────────────


def calculate_jam_expense_summary(jam) -> dict:
    """
    Return a financial summary for all *active* expenses of a JAM.

    Structure:
    {
        "total_expenses": Decimal,   # sum of all active expense amounts
        "total_paid":    Decimal,    # sum of splits with status=paid
        "total_pending": Decimal,    # sum of splits with status=pending
        "balances": {
            "<username>": {
                "paid":        Decimal,  # total this user fronted (paid_by)
                "owes":        Decimal,  # total this user owes across all splits
                "net_balance": Decimal,  # paid - owes (positive = is owed money)
            },
            ...
        },
        "pending_splits": [          # list of unsettled splits
            {
                "expense_id":    int,
                "expense_title": str,
                "username":      str,
                "amount_owed":   Decimal,
            },
            ...
        ],
    }
    """
    from .models import Expense, ExpenseSplit

    active_expenses = Expense.objects.filter(jam=jam, is_active=True).select_related("paid_by")
    splits = ExpenseSplit.objects.filter(
        expense__jam=jam, expense__is_active=True
    ).select_related("user", "expense")

    total_expenses = sum(e.amount for e in active_expenses) or Decimal("0.00")
    total_paid = Decimal("0.00")
    total_pending = Decimal("0.00")
    balances: dict[str, dict] = {}
    pending_splits = []

    # Aggregate paid_by (who fronted money)
    for expense in active_expenses:
        username = expense.paid_by.username
        if username not in balances:
            balances[username] = {"paid": Decimal("0.00"), "owes": Decimal("0.00"), "net_balance": Decimal("0.00")}
        balances[username]["paid"] += expense.amount

    # Aggregate splits (who owes what)
    for split in splits:
        username = split.user.username
        if username not in balances:
            balances[username] = {"paid": Decimal("0.00"), "owes": Decimal("0.00"), "net_balance": Decimal("0.00")}

        balances[username]["owes"] += split.amount_owed

        if split.status == ExpenseSplit.Status.PAID:
            total_paid += split.amount_owed
        else:
            total_pending += split.amount_owed
            pending_splits.append({
                "expense_id": split.expense_id,
                "expense_title": split.expense.title,
                "username": username,
                "amount_owed": split.amount_owed,
            })

    for username, data in balances.items():
        data["net_balance"] = data["paid"] - data["owes"]

    return {
        "total_expenses": total_expenses,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "balances": balances,
        "pending_splits": pending_splits,
    }


# ── Permission predicates ──────────────────────────────────────────────────────


def can_view_expense(user, expense) -> bool:
    """Any active JAM member can view an expense."""
    return is_jam_member(user, expense.jam)


def can_manage_expense(user, expense) -> bool:
    """JAM admin OR the expense creator can edit/delete."""
    return is_jam_admin(user, expense.jam) or expense.created_by == user


def can_mark_split_paid(user, split) -> bool:
    """The split owner or a JAM admin can mark a split as paid."""
    return split.user == user or is_jam_admin(user, split.expense.jam)


def can_mark_split_pending(user, split) -> bool:
    """
    Only a JAM admin (or the expense creator) can revert a split to pending.
    More restrictive than mark-paid intentionally.
    """
    return is_jam_admin(user, split.expense.jam) or split.expense.created_by == user


# ── Split state transitions ────────────────────────────────────────────────────


def mark_split_paid(split, marked_by) -> "ExpenseSplit":
    """Set split.status = paid and record paid_at timestamp."""
    split.status = split.Status.PAID
    split.paid_at = timezone.now()
    split.save(update_fields=["status", "paid_at", "updated_at"])
    return split


def mark_split_pending(split, marked_by) -> "ExpenseSplit":
    """Revert split.status = pending and clear paid_at."""
    split.status = split.Status.PENDING
    split.paid_at = None
    split.save(update_fields=["status", "paid_at", "updated_at"])
    return split
