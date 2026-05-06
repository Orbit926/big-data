from django.db import models
from django.conf import settings


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("transport", "Transport"),
        ("accommodation", "Accommodation"),
        ("food", "Food"),
        ("activities", "Activities"),
        ("other", "Other"),
    ]

    jam = models.ForeignKey(
        "jams.Jam",
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="paid_expenses",
    )
    split_between = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="shared_expenses",
        blank=True,
    )
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.description} - ${self.amount}"
