"""
DRF permission classes for the Expenses app.
Thin wrappers around the helpers in apps.expenses.services.
"""

from rest_framework.permissions import BasePermission

from .services import can_manage_expense, can_view_expense


class IsJamMemberForExpense(BasePermission):
    """Allow read access to any active JAM member."""

    message = "You must be an active JAM member to access this expense."

    def has_object_permission(self, request, view, obj):
        # obj is an Expense instance
        return can_view_expense(request.user, obj)


class CanManageExpense(BasePermission):
    """Allow write access to JAM admin or expense creator."""

    message = "Only the expense creator or a JAM admin can modify this expense."

    def has_object_permission(self, request, view, obj):
        return can_manage_expense(request.user, obj)
