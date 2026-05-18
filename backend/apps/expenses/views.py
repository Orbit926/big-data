"""
Views for the Expenses app.

All views require JWT cookie authentication (IsAuthenticated).
Permission logic is delegated to apps.expenses.services.

Route table (see urls.py):

  JAM-scoped (mounted at /api/jams/):
    GET    /api/jams/{jam_id}/expenses/          → JamExpenseListCreateView.get
    POST   /api/jams/{jam_id}/expenses/          → JamExpenseListCreateView.post
    GET    /api/jams/{jam_id}/expenses/summary/  → JamExpenseSummaryView.get

  Expense-scoped (mounted at /api/expenses/):
    GET    /api/expenses/{expense_id}/                                 → ExpenseDetailView.get
    PATCH  /api/expenses/{expense_id}/                                 → ExpenseDetailView.patch
    DELETE /api/expenses/{expense_id}/                                 → ExpenseDetailView.delete (soft)
    GET    /api/expenses/{expense_id}/splits/                          → ExpenseSplitListView.get
    PATCH  /api/expenses/{expense_id}/splits/{split_id}/mark-paid/    → MarkExpenseSplitPaidView.patch
    PATCH  /api/expenses/{expense_id}/splits/{split_id}/mark-pending/ → MarkExpenseSplitPendingView.patch
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.jams.models import Jam
from apps.jams.services import is_jam_member

from .models import Expense, ExpenseSplit
from .serializers import (
    ExpenseCreateSerializer,
    ExpenseDetailSerializer,
    ExpenseListSerializer,
    ExpenseSplitSerializer,
    ExpenseUpdateSerializer,
)
from .services import (
    calculate_jam_expense_summary,
    can_manage_expense,
    can_mark_split_paid,
    can_mark_split_pending,
    create_custom_expense,
    create_equal_expense,
    mark_split_paid,
    mark_split_pending,
    validate_active_jam_member,
)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _get_jam_or_404(jam_id):
    return get_object_or_404(Jam, pk=jam_id)


def _require_jam_member(user, jam):
    if not is_jam_member(user, jam):
        raise PermissionDenied("You are not an active member of this JAM.")


def _get_active_expense_or_404(expense_id):
    """Return the expense; 404 if it doesn't exist (active or not)."""
    return get_object_or_404(Expense, pk=expense_id)


# ── JAM-scoped views ───────────────────────────────────────────────────────────


class JamExpenseListCreateView(APIView):
    """
    GET  /api/jams/{jam_id}/expenses/  → list active expenses (member+)
    POST /api/jams/{jam_id}/expenses/  → create expense (member+)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, jam_id):
        jam = _get_jam_or_404(jam_id)
        _require_jam_member(request.user, jam)

        expenses = (
            Expense.objects
            .filter(jam=jam, is_active=True)
            .select_related("paid_by", "created_by")
            .order_by("-created_at")
        )
        return Response(ExpenseListSerializer(expenses, many=True).data)

    def post(self, request, jam_id):
        jam = _get_jam_or_404(jam_id)
        # Validate membership BEFORE reading the body so outsider gets 403
        validate_active_jam_member(request.user, jam)

        serializer = ExpenseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Default paid_by to the requesting user
        if "paid_by" not in data:
            data["paid_by"] = request.user

        split_type = data.get("split_type", Expense.SplitType.EQUAL)

        if split_type == Expense.SplitType.EQUAL:
            expense = create_equal_expense(jam, data, created_by=request.user)
        else:
            expense = create_custom_expense(jam, data, created_by=request.user)

        expense.refresh_from_db()
        return Response(ExpenseDetailSerializer(expense).data, status=status.HTTP_201_CREATED)


class JamExpenseSummaryView(APIView):
    """
    GET /api/jams/{jam_id}/expenses/summary/
    Returns financial summary of all active expenses in the JAM.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, jam_id):
        jam = _get_jam_or_404(jam_id)
        _require_jam_member(request.user, jam)

        summary = calculate_jam_expense_summary(jam)
        return Response(summary)


# ── Expense-scoped views ───────────────────────────────────────────────────────


class ExpenseDetailView(APIView):
    """
    GET    /api/expenses/{expense_id}/  → detail (member+)
    PATCH  /api/expenses/{expense_id}/  → update title/desc/category (admin or creator)
    DELETE /api/expenses/{expense_id}/  → soft-delete (admin or creator)
    """

    permission_classes = [IsAuthenticated]

    def _get_expense(self, expense_id, user, require_manage=False):
        expense = _get_active_expense_or_404(expense_id)
        if require_manage:
            if not can_manage_expense(user, expense):
                raise PermissionDenied("Only the expense creator or a JAM admin can perform this action.")
        else:
            if not is_jam_member(user, expense.jam):
                raise PermissionDenied("You are not a member of this JAM.")
        return expense

    def get(self, request, expense_id):
        expense = self._get_expense(expense_id, request.user)
        return Response(ExpenseDetailSerializer(expense).data)

    def patch(self, request, expense_id):
        expense = self._get_expense(expense_id, request.user, require_manage=True)
        serializer = ExpenseUpdateSerializer(expense, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        expense.refresh_from_db()
        return Response(ExpenseDetailSerializer(expense).data)

    def delete(self, request, expense_id):
        expense = self._get_expense(expense_id, request.user, require_manage=True)
        # Soft delete
        expense.is_active = False
        expense.save(update_fields=["is_active", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Split views ────────────────────────────────────────────────────────────────


class ExpenseSplitListView(APIView):
    """
    GET /api/expenses/{expense_id}/splits/  → list splits (member+)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, expense_id):
        expense = _get_active_expense_or_404(expense_id)
        if not is_jam_member(request.user, expense.jam):
            raise PermissionDenied("You are not a member of this JAM.")
        splits = expense.splits.select_related("user").all()
        return Response(ExpenseSplitSerializer(splits, many=True).data)


class MarkExpenseSplitPaidView(APIView):
    """
    PATCH /api/expenses/{expense_id}/splits/{split_id}/mark-paid/
    Split owner or JAM admin can mark a split as paid.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, expense_id, split_id):
        expense = _get_active_expense_or_404(expense_id)
        split = get_object_or_404(ExpenseSplit, pk=split_id, expense=expense)

        if not can_mark_split_paid(request.user, split):
            raise PermissionDenied("Only the split owner or a JAM admin can mark this as paid.")

        if split.status == ExpenseSplit.Status.PAID:
            return Response({"detail": "Split is already marked as paid."}, status=status.HTTP_400_BAD_REQUEST)

        mark_split_paid(split, marked_by=request.user)
        return Response(ExpenseSplitSerializer(split).data)


class MarkExpenseSplitPendingView(APIView):
    """
    PATCH /api/expenses/{expense_id}/splits/{split_id}/mark-pending/
    JAM admin or expense creator can revert a split to pending.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, expense_id, split_id):
        expense = _get_active_expense_or_404(expense_id)
        split = get_object_or_404(ExpenseSplit, pk=split_id, expense=expense)

        if not can_mark_split_pending(request.user, split):
            raise PermissionDenied("Only a JAM admin or the expense creator can revert this split.")

        if split.status == ExpenseSplit.Status.PENDING:
            return Response({"detail": "Split is already pending."}, status=status.HTTP_400_BAD_REQUEST)

        mark_split_pending(split, marked_by=request.user)
        return Response(ExpenseSplitSerializer(split).data)
