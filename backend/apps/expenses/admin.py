"""
Django Admin registration for the Expenses app.
"""

from django.contrib import admin

from .models import Expense, ExpenseSplit


class ExpenseSplitInline(admin.TabularInline):
    model = ExpenseSplit
    extra = 0
    fields = ["user", "amount_owed", "status", "paid_at"]
    readonly_fields = ["paid_at"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["title", "jam", "amount", "currency", "split_type", "category", "paid_by", "is_active", "created_at"]
    list_filter = ["split_type", "category", "is_active", "currency"]
    search_fields = ["title", "jam__name", "paid_by__username"]
    readonly_fields = ["created_by", "created_at", "updated_at"]
    inlines = [ExpenseSplitInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("jam", "paid_by", "created_by")
