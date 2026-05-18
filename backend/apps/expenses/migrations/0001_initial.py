"""
Initial migration for the Expenses app.

Replaces the previous 0001_initial.py + 0002_initial.py stubs that used
a ManyToMany `split_between` field and lacked ExpenseSplit, title, split_type, etc.

⚠️  If you applied the old migrations locally, reset your DB:
      docker compose exec backend python manage.py migrate expenses zero
      docker compose exec backend python manage.py migrate expenses
    Or drop and recreate the SQLite file if no important data exists.
"""

import django.db.models.deletion
import django.db.models.functions.comparison
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("jams", "0002_jam_upgrade_jammember"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="Short label, e.g. 'Dinner at Belcanto'.", max_length=255)),
                ("description", models.TextField(blank=True)),
                ("amount", models.DecimalField(decimal_places=2, help_text="Total amount in the expense currency.", max_digits=10)),
                ("currency", models.CharField(default="MXN", max_length=3)),
                ("split_type", models.CharField(choices=[("equal", "Equal"), ("custom", "Custom")], default="equal", max_length=10)),
                ("category", models.CharField(choices=[("food", "Food"), ("lodging", "Lodging"), ("transport", "Transport"), ("activity", "Activity"), ("nightlife", "Nightlife"), ("shopping", "Shopping"), ("other", "Other")], default="other", max_length=12)),
                ("is_active", models.BooleanField(default=True, help_text="False = soft-deleted; excluded from lists and summaries.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("jam", models.ForeignKey(help_text="The JAM this expense belongs to.", on_delete=django.db.models.deletion.CASCADE, related_name="expenses", to="jams.jam")),
                ("paid_by", models.ForeignKey(help_text="Who fronted the money.", on_delete=django.db.models.deletion.CASCADE, related_name="paid_expenses", to=settings.AUTH_USER_MODEL)),
                ("created_by", models.ForeignKey(help_text="Who registered the expense (may differ from paid_by).", on_delete=django.db.models.deletion.CASCADE, related_name="created_expenses", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Expense",
                "verbose_name_plural": "Expenses",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ExpenseSplit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount_owed", models.DecimalField(decimal_places=2, help_text="Amount this user owes for this expense.", max_digits=10)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("paid", "Paid")], default="pending", max_length=10)),
                ("paid_at", models.DateTimeField(blank=True, help_text="When the split was marked as paid (manual tracking only).", null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("expense", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="splits", to="expenses.expense")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="expense_splits", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Expense Split",
                "verbose_name_plural": "Expense Splits",
                "ordering": ["expense", "user"],
            },
        ),
        migrations.AddConstraint(
            model_name="expense",
            constraint=models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="expense_amount_positive",
            ),
        ),
        migrations.AddConstraint(
            model_name="expensesplit",
            constraint=models.CheckConstraint(
                check=models.Q(amount_owed__gte=0),
                name="split_amount_owed_non_negative",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="expensesplit",
            unique_together={("expense", "user")},
        ),
    ]
