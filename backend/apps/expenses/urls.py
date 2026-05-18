"""
URL routing for the Expenses app.

Two separate pattern groups so config/urls.py can mount them independently:

  jams_urlpatterns  → include under /api/jams/
  urlpatterns       → include under /api/expenses/
"""

from django.urls import path

from .views import (
    ExpenseDetailView,
    ExpenseSplitListView,
    JamExpenseListCreateView,
    JamExpenseSummaryView,
    MarkExpenseSplitPaidView,
    MarkExpenseSplitPendingView,
)

# Mounted by config/urls.py under: /api/jams/
jams_urlpatterns = [
    path("<int:jam_id>/expenses/", JamExpenseListCreateView.as_view(), name="jam-expense-list-create"),
    path("<int:jam_id>/expenses/summary/", JamExpenseSummaryView.as_view(), name="jam-expense-summary"),
]

# Mounted by config/urls.py under: /api/expenses/
urlpatterns = [
    path("<int:expense_id>/", ExpenseDetailView.as_view(), name="expense-detail"),
    path("<int:expense_id>/splits/", ExpenseSplitListView.as_view(), name="expense-split-list"),
    path(
        "<int:expense_id>/splits/<int:split_id>/mark-paid/",
        MarkExpenseSplitPaidView.as_view(),
        name="expense-split-mark-paid",
    ),
    path(
        "<int:expense_id>/splits/<int:split_id>/mark-pending/",
        MarkExpenseSplitPendingView.as_view(),
        name="expense-split-mark-pending",
    ),
]
