"""
Expenses models — split-based expense tracking within a JAM.

Expense
───────
  Belongs to a JAM. Tracks who paid, how much, and how the cost is split.
  Soft-delete via is_active=False; hard DELETE is not exposed by the API.

ExpenseSplit
────────────
  One record per participant per expense. Tracks each person's share and
  whether they've settled (status=paid).

NOTE: mark-paid / mark-pending are manual tracking only.
No payment processing, Stripe, SPEI or wallets are implemented here.

Future modules: import helpers from apps.expenses.services, not this file.
"""

from django.conf import settings
from django.db import models


class Expense(models.Model):
    """A shared cost within a JAM, split among participants."""

    class SplitType(models.TextChoices):
        EQUAL = "equal", "Equal"
        CUSTOM = "custom", "Custom"

    class Category(models.TextChoices):
        FOOD = "food", "Food"
        LODGING = "lodging", "Lodging"
        TRANSPORT = "transport", "Transport"
        ACTIVITY = "activity", "Activity"
        NIGHTLIFE = "nightlife", "Nightlife"
        SHOPPING = "shopping", "Shopping"
        OTHER = "other", "Other"

    # ── Relationships ──────────────────────────────────────────────────────
    jam = models.ForeignKey(
        "jams.Jam",
        on_delete=models.CASCADE,
        related_name="expenses",
        help_text="The JAM this expense belongs to.",
    )
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="paid_expenses",
        help_text="Who fronted the money.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_expenses",
        help_text="Who registered the expense (may differ from paid_by).",
    )

    # ── Core fields ────────────────────────────────────────────────────────
    title = models.CharField(max_length=255, help_text="Short label, e.g. 'Dinner at Belcanto'.")
    description = models.TextField(blank=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total amount in the expense currency.",
    )
    currency = models.CharField(max_length=3, default="MXN")
    split_type = models.CharField(
        max_length=10,
        choices=SplitType.choices,
        default=SplitType.EQUAL,
    )
    category = models.CharField(
        max_length=12,
        choices=Category.choices,
        default=Category.OTHER,
    )

    # ── Soft-delete ────────────────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        help_text="False = soft-deleted; excluded from lists and summaries.",
    )

    # ── Timestamps ─────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="expense_amount_positive",
            )
        ]

    def __str__(self) -> str:  # noqa: D105
        return f"{self.title} — {self.amount} {self.currency}"


class ExpenseSplit(models.Model):
    """Individual share of an Expense for one participant."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"

    # ── Relationships ──────────────────────────────────────────────────────
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name="splits",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expense_splits",
    )

    # ── Split detail ───────────────────────────────────────────────────────
    amount_owed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount this user owes for this expense.",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the split was marked as paid (manual tracking only).",
    )

    # ── Timestamps ─────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("expense", "user")]
        ordering = ["expense", "user"]
        verbose_name = "Expense Split"
        verbose_name_plural = "Expense Splits"
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount_owed__gte=0),
                name="split_amount_owed_non_negative",
            )
        ]

    def __str__(self) -> str:  # noqa: D105
        return f"{self.user} owes {self.amount_owed} for '{self.expense.title}'"
