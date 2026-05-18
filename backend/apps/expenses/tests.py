"""Tests for the Expenses app."""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.trips.models import Trip
from apps.jams.models import Jam, JamMember
from apps.expenses.models import Expense, ExpenseSplit
from apps.expenses.services import (
    calculate_equal_splits,
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

User = get_user_model()


# ── Fixtures ───────────────────────────────────────────────────────────────────

def make_user(username, **kw):
    return User.objects.create_user(username=username, email=f"{username}@test.com", password="pass")


def make_jam_with_members(admin_user, member_user=None):
    trip = Trip.objects.create(name="Trip", organizer=admin_user)
    if member_user:
        trip.participants.add(member_user)
    jam = Jam.objects.create(trip=trip, name="Test JAM", created_by=admin_user)
    # signal auto-creates admin membership; add member if provided
    if member_user:
        JamMember.objects.create(jam=jam, user=member_user, role=JamMember.Role.MEMBER, status=JamMember.Status.ACTIVE)
    return jam


def make_equal_expense(jam, paid_by, participants, amount="120.00", title="Dinner"):
    data = {
        "title": title,
        "description": "",
        "amount": Decimal(amount),
        "currency": "MXN",
        "category": Expense.Category.FOOD,
        "paid_by": paid_by,
        "participant_ids": [u.pk for u in participants],
    }
    return create_equal_expense(jam, data, created_by=paid_by)


# ── Service unit tests ─────────────────────────────────────────────────────────

class CalculateEqualSplitsTests(TestCase):
    def test_even_split(self):
        shares = calculate_equal_splits(Decimal("120.00"), 3)
        self.assertEqual(len(shares), 3)
        self.assertEqual(sum(shares), Decimal("120.00"))
        self.assertEqual(shares[0], Decimal("40.00"))

    def test_remainder_goes_to_last(self):
        shares = calculate_equal_splits(Decimal("10.00"), 3)
        self.assertEqual(sum(shares), Decimal("10.00"))

    def test_single_participant(self):
        shares = calculate_equal_splits(Decimal("50.00"), 1)
        self.assertEqual(shares, [Decimal("50.00")])

    def test_zero_participants(self):
        self.assertEqual(calculate_equal_splits(Decimal("100.00"), 0), [])


class ServicePermissionTests(TestCase):
    def setUp(self):
        self.admin = make_user("admin")
        self.member = make_user("member")
        self.outsider = make_user("outsider")
        self.jam = make_jam_with_members(self.admin, self.member)
        self.expense = make_equal_expense(self.jam, self.admin, [self.admin, self.member])

    def test_can_view_expense_admin(self):
        self.assertTrue(can_view_expense(self.admin, self.expense))

    def test_can_view_expense_member(self):
        self.assertTrue(can_view_expense(self.member, self.expense))

    def test_can_view_expense_outsider_false(self):
        self.assertFalse(can_view_expense(self.outsider, self.expense))

    def test_can_manage_expense_admin(self):
        self.assertTrue(can_manage_expense(self.admin, self.expense))

    def test_can_manage_expense_creator(self):
        # admin is creator here
        self.assertTrue(can_manage_expense(self.admin, self.expense))

    def test_can_manage_expense_member_false(self):
        self.assertFalse(can_manage_expense(self.member, self.expense))

    def test_can_mark_split_paid_own_split(self):
        split = self.expense.splits.get(user=self.member)
        self.assertTrue(can_mark_split_paid(self.member, split))

    def test_can_mark_split_paid_admin(self):
        split = self.expense.splits.get(user=self.member)
        self.assertTrue(can_mark_split_paid(self.admin, split))

    def test_can_mark_split_paid_outsider_false(self):
        split = self.expense.splits.get(user=self.member)
        self.assertFalse(can_mark_split_paid(self.outsider, split))

    def test_can_mark_split_pending_admin(self):
        split = self.expense.splits.get(user=self.member)
        self.assertTrue(can_mark_split_pending(self.admin, split))

    def test_can_mark_split_pending_member_false(self):
        split = self.expense.splits.get(user=self.member)
        self.assertFalse(can_mark_split_pending(self.member, split))


class CreateEqualExpenseTests(TestCase):
    def setUp(self):
        self.admin = make_user("admin")
        self.member = make_user("member")
        self.jam = make_jam_with_members(self.admin, self.member)

    def test_creates_expense_and_splits(self):
        exp = make_equal_expense(self.jam, self.admin, [self.admin, self.member])
        self.assertEqual(exp.title, "Dinner")
        self.assertEqual(exp.splits.count(), 2)
        self.assertEqual(sum(s.amount_owed for s in exp.splits.all()), Decimal("120.00"))

    def test_paid_by_split_auto_paid(self):
        exp = make_equal_expense(self.jam, self.admin, [self.admin, self.member])
        admin_split = exp.splits.get(user=self.admin)
        member_split = exp.splits.get(user=self.member)
        self.assertEqual(admin_split.status, ExpenseSplit.Status.PAID)
        self.assertEqual(member_split.status, ExpenseSplit.Status.PENDING)

    def test_paid_by_split_has_paid_at(self):
        exp = make_equal_expense(self.jam, self.admin, [self.admin, self.member])
        self.assertIsNotNone(exp.splits.get(user=self.admin).paid_at)
        self.assertIsNone(exp.splits.get(user=self.member).paid_at)

    def test_outsider_in_participant_ids_raises(self):
        outsider = make_user("out")
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            make_equal_expense(self.jam, self.admin, [self.admin, outsider])

    def test_created_by_set_correctly(self):
        exp = make_equal_expense(self.jam, self.admin, [self.admin, self.member])
        self.assertEqual(exp.created_by, self.admin)


class CreateCustomExpenseTests(TestCase):
    def setUp(self):
        self.admin = make_user("admin")
        self.member = make_user("member")
        self.jam = make_jam_with_members(self.admin, self.member)

    def test_custom_split_creates_correct_amounts(self):
        data = {
            "title": "Custom",
            "description": "",
            "amount": Decimal("100.00"),
            "currency": "MXN",
            "category": Expense.Category.OTHER,
            "paid_by": self.admin,
            "splits": [
                {"user_id": self.admin.pk, "amount_owed": Decimal("70.00")},
                {"user_id": self.member.pk, "amount_owed": Decimal("30.00")},
            ],
        }
        exp = create_custom_expense(self.jam, data, created_by=self.admin)
        self.assertEqual(exp.split_type, Expense.SplitType.CUSTOM)
        self.assertEqual(exp.splits.get(user=self.member).amount_owed, Decimal("30.00"))

    def test_sum_mismatch_raises(self):
        from rest_framework.exceptions import ValidationError
        data = {
            "title": "Bad",
            "description": "",
            "amount": Decimal("100.00"),
            "currency": "MXN",
            "category": Expense.Category.OTHER,
            "paid_by": self.admin,
            "splits": [
                {"user_id": self.admin.pk, "amount_owed": Decimal("70.00")},
                {"user_id": self.member.pk, "amount_owed": Decimal("20.00")},
            ],
        }
        with self.assertRaises(ValidationError):
            create_custom_expense(self.jam, data, created_by=self.admin)


class SummaryTests(TestCase):
    def setUp(self):
        self.admin = make_user("admin")
        self.member = make_user("member")
        self.jam = make_jam_with_members(self.admin, self.member)

    def test_summary_totals(self):
        make_equal_expense(self.jam, self.admin, [self.admin, self.member], amount="100.00")
        summary = calculate_jam_expense_summary(self.jam)
        self.assertEqual(summary["total_expenses"], Decimal("100.00"))
        self.assertIn("admin", summary["balances"])
        self.assertIn("member", summary["balances"])

    def test_soft_deleted_excluded_from_summary(self):
        exp = make_equal_expense(self.jam, self.admin, [self.admin, self.member], amount="100.00")
        exp.is_active = False
        exp.save()
        summary = calculate_jam_expense_summary(self.jam)
        self.assertEqual(summary["total_expenses"], Decimal("0.00"))

    def test_net_balance_paid_by_positive(self):
        make_equal_expense(self.jam, self.admin, [self.admin, self.member], amount="100.00")
        summary = calculate_jam_expense_summary(self.jam)
        self.assertGreater(summary["balances"]["admin"]["net_balance"], Decimal("0"))

    def test_pending_splits_listed(self):
        make_equal_expense(self.jam, self.admin, [self.admin, self.member], amount="100.00")
        summary = calculate_jam_expense_summary(self.jam)
        self.assertEqual(len(summary["pending_splits"]), 1)
        self.assertEqual(summary["pending_splits"][0]["username"], "member")


class MarkSplitTests(TestCase):
    def setUp(self):
        self.admin = make_user("admin")
        self.member = make_user("member")
        self.jam = make_jam_with_members(self.admin, self.member)
        self.expense = make_equal_expense(self.jam, self.admin, [self.admin, self.member])
        self.split = self.expense.splits.get(user=self.member)

    def test_mark_paid(self):
        mark_split_paid(self.split, self.member)
        self.split.refresh_from_db()
        self.assertEqual(self.split.status, ExpenseSplit.Status.PAID)
        self.assertIsNotNone(self.split.paid_at)

    def test_mark_pending(self):
        mark_split_paid(self.split, self.member)
        mark_split_pending(self.split, self.admin)
        self.split.refresh_from_db()
        self.assertEqual(self.split.status, ExpenseSplit.Status.PENDING)
        self.assertIsNone(self.split.paid_at)


# ── API tests ──────────────────────────────────────────────────────────────────

def auth_client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


class ExpenseListCreateAPITests(TestCase):
    def setUp(self):
        self.admin = make_user("admin")
        self.member = make_user("member")
        self.outsider = make_user("out")
        self.jam = make_jam_with_members(self.admin, self.member)
        self.url = f"/api/jams/{self.jam.pk}/expenses/"

    def test_admin_can_list(self):
        r = auth_client(self.admin).get(self.url)
        self.assertEqual(r.status_code, 200)

    def test_member_can_list(self):
        r = auth_client(self.member).get(self.url)
        self.assertEqual(r.status_code, 200)

    def test_outsider_cannot_list(self):
        r = auth_client(self.outsider).get(self.url)
        self.assertEqual(r.status_code, 403)

    def test_unauthenticated_returns_401(self):
        r = APIClient().get(self.url)
        self.assertEqual(r.status_code, 401)

    def test_admin_can_create_equal_expense(self):
        r = auth_client(self.admin).post(self.url, {
            "title": "Dinner",
            "amount": "120.00",
            "split_type": "equal",
            "category": "food",
            "participant_ids": [self.admin.pk, self.member.pk],
        }, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["title"], "Dinner")
        self.assertEqual(len(r.data["splits"]), 2)

    def test_member_can_create_expense(self):
        r = auth_client(self.member).post(self.url, {
            "title": "Lunch",
            "amount": "60.00",
            "split_type": "equal",
            "participant_ids": [self.admin.pk, self.member.pk],
        }, format="json")
        self.assertEqual(r.status_code, 201)

    def test_outsider_cannot_create(self):
        r = auth_client(self.outsider).post(self.url, {
            "title": "Hack",
            "amount": "50.00",
            "split_type": "equal",
            "participant_ids": [self.admin.pk],
        }, format="json")
        self.assertEqual(r.status_code, 403)

    def test_missing_participant_ids_returns_400(self):
        r = auth_client(self.admin).post(self.url, {
            "title": "Dinner",
            "amount": "100.00",
            "split_type": "equal",
        }, format="json")
        self.assertEqual(r.status_code, 400)

    def test_custom_split_creates_correct_splits(self):
        r = auth_client(self.admin).post(self.url, {
            "title": "Custom",
            "amount": "100.00",
            "split_type": "custom",
            "splits": [
                {"user_id": self.admin.pk, "amount_owed": "70.00"},
                {"user_id": self.member.pk, "amount_owed": "30.00"},
            ],
        }, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["split_type"], "custom")

    def test_soft_deleted_expense_not_in_list(self):
        exp = make_equal_expense(self.jam, self.admin, [self.admin, self.member])
        exp.is_active = False
        exp.save()
        r = auth_client(self.admin).get(self.url)
        ids = [e["id"] for e in r.data]
        self.assertNotIn(exp.pk, ids)

    def test_created_by_always_request_user(self):
        r = auth_client(self.admin).post(self.url, {
            "title": "Test",
            "amount": "50.00",
            "split_type": "equal",
            "participant_ids": [self.admin.pk],
        }, format="json")
        self.assertEqual(r.status_code, 201)
        exp = Expense.objects.get(pk=r.data["id"])
        self.assertEqual(exp.created_by, self.admin)


class ExpenseSummaryAPITests(TestCase):
    def setUp(self):
        self.admin = make_user("admin")
        self.member = make_user("member")
        self.outsider = make_user("out")
        self.jam = make_jam_with_members(self.admin, self.member)
        self.url = f"/api/jams/{self.jam.pk}/expenses/summary/"

    def test_member_can_get_summary(self):
        make_equal_expense(self.jam, self.admin, [self.admin, self.member])
        r = auth_client(self.member).get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertIn("total_expenses", r.data)
        self.assertIn("balances", r.data)

    def test_outsider_gets_403(self):
        r = auth_client(self.outsider).get(self.url)
        self.assertEqual(r.status_code, 403)

    def test_unauthenticated_gets_401(self):
        r = APIClient().get(self.url)
        self.assertEqual(r.status_code, 401)

    def test_soft_deleted_excluded(self):
        exp = make_equal_expense(self.jam, self.admin, [self.admin, self.member], amount="100.00")
        exp.is_active = False
        exp.save()
        r = auth_client(self.admin).get(self.url)
        self.assertEqual(Decimal(str(r.data["total_expenses"])), Decimal("0.00"))


class ExpenseDetailAPITests(TestCase):
    def setUp(self):
        self.admin = make_user("admin")
        self.member = make_user("member")
        self.outsider = make_user("out")
        self.jam = make_jam_with_members(self.admin, self.member)
        self.expense = make_equal_expense(self.jam, self.admin, [self.admin, self.member])
        self.url = f"/api/expenses/{self.expense.pk}/"

    def test_admin_can_get(self):
        r = auth_client(self.admin).get(self.url)
        self.assertEqual(r.status_code, 200)

    def test_member_can_get(self):
        r = auth_client(self.member).get(self.url)
        self.assertEqual(r.status_code, 200)

    def test_outsider_gets_403(self):
        r = auth_client(self.outsider).get(self.url)
        self.assertEqual(r.status_code, 403)

    def test_unauthenticated_gets_401(self):
        r = APIClient().get(self.url)
        self.assertEqual(r.status_code, 401)

    def test_admin_can_patch_title(self):
        r = auth_client(self.admin).patch(self.url, {"title": "Updated"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["title"], "Updated")

    def test_member_cannot_patch(self):
        r = auth_client(self.member).patch(self.url, {"title": "Hack"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_cannot_patch_amount(self):
        r = auth_client(self.admin).patch(self.url, {"amount": "999.00"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.expense.refresh_from_db()
        self.assertNotEqual(self.expense.amount, Decimal("999.00"))

    def test_admin_soft_deletes(self):
        r = auth_client(self.admin).delete(self.url)
        self.assertEqual(r.status_code, 204)
        self.expense.refresh_from_db()
        self.assertFalse(self.expense.is_active)

    def test_member_cannot_delete(self):
        r = auth_client(self.member).delete(self.url)
        self.assertEqual(r.status_code, 403)


class SplitAPITests(TestCase):
    def setUp(self):
        self.admin = make_user("admin")
        self.member = make_user("member")
        self.outsider = make_user("out")
        self.jam = make_jam_with_members(self.admin, self.member)
        self.expense = make_equal_expense(self.jam, self.admin, [self.admin, self.member])
        self.member_split = self.expense.splits.get(user=self.member)
        self.admin_split = self.expense.splits.get(user=self.admin)
        self.splits_url = f"/api/expenses/{self.expense.pk}/splits/"
        self.mark_paid_url = f"/api/expenses/{self.expense.pk}/splits/{self.member_split.pk}/mark-paid/"
        self.mark_pending_url = f"/api/expenses/{self.expense.pk}/splits/{self.member_split.pk}/mark-pending/"

    def test_member_can_list_splits(self):
        r = auth_client(self.member).get(self.splits_url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)

    def test_outsider_cannot_list_splits(self):
        r = auth_client(self.outsider).get(self.splits_url)
        self.assertEqual(r.status_code, 403)

    def test_member_can_mark_own_split_paid(self):
        r = auth_client(self.member).patch(self.mark_paid_url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["status"], "paid")

    def test_admin_can_mark_any_split_paid(self):
        r = auth_client(self.admin).patch(self.mark_paid_url)
        self.assertEqual(r.status_code, 200)

    def test_outsider_cannot_mark_split_paid(self):
        r = auth_client(self.outsider).patch(self.mark_paid_url)
        self.assertEqual(r.status_code, 403)

    def test_mark_paid_twice_returns_400(self):
        auth_client(self.member).patch(self.mark_paid_url)
        r = auth_client(self.member).patch(self.mark_paid_url)
        self.assertEqual(r.status_code, 400)

    def test_admin_can_mark_split_pending(self):
        auth_client(self.member).patch(self.mark_paid_url)
        r = auth_client(self.admin).patch(self.mark_pending_url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["status"], "pending")
        self.assertIsNone(r.data["paid_at"])

    def test_member_cannot_mark_split_pending(self):
        auth_client(self.member).patch(self.mark_paid_url)
        r = auth_client(self.member).patch(self.mark_pending_url)
        self.assertEqual(r.status_code, 403)

    def test_mark_pending_twice_returns_400(self):
        r = auth_client(self.admin).patch(self.mark_pending_url)
        self.assertEqual(r.status_code, 400)


class ExpenseIntegrationCookieTests(TestCase):
    """
    Real JWT HTTP-Only cookie integration test.
    No force_authenticate — uses the full auth stack.
    """

    def setUp(self):
        self.client = APIClient()
        self.admin_user = make_user("cookie_admin")
        self.member_user = make_user("cookie_member")

    def _login(self, username):
        r = self.client.post(
            "/api/auth/login/",
            {"login": username, "password": "pass"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, f"Login failed for {username}: {r.data}")
        return r.cookies

    def test_full_expense_flow_with_real_cookies(self):
        # 1. Login admin → get cookie
        cookies = self._login("cookie_admin")
        self.client.cookies = cookies

        # 2. Verify auth works
        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["username"], "cookie_admin")

        # 3. Create trip
        trip = Trip.objects.create(name="Cookie Trip", organizer=self.admin_user)
        trip.participants.add(self.member_user)

        # 4. Create JAM
        r = self.client.post(f"/api/trips/{trip.pk}/jam/", {"name": "Cookie JAM"}, format="json")
        self.assertEqual(r.status_code, 201)
        jam_id = r.data["id"]

        # 5. Add member to JAM
        JamMember.objects.create(
            jam_id=jam_id, user=self.member_user,
            role=JamMember.Role.MEMBER, status=JamMember.Status.ACTIVE
        )

        # 6. Create equal expense via API with real cookie
        r = self.client.post(f"/api/jams/{jam_id}/expenses/", {
            "title": "Cookie Dinner",
            "amount": "200.00",
            "split_type": "equal",
            "participant_ids": [self.admin_user.pk, self.member_user.pk],
        }, format="json")
        self.assertEqual(r.status_code, 201)
        expense_id = r.data["id"]
        self.assertEqual(r.data["created_by"]["username"], "cookie_admin")
        self.assertEqual(len(r.data["splits"]), 2)

        # 7. Get summary with real cookie
        r = self.client.get(f"/api/jams/{jam_id}/expenses/summary/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Decimal(r.data["total_expenses"]), Decimal("200.00"))

        # 8. member logs in and marks their split paid
        member_split = ExpenseSplit.objects.get(expense_id=expense_id, user=self.member_user)
        member_cookies = self._login("cookie_member")
        self.client.cookies = member_cookies

        r = self.client.patch(
            f"/api/expenses/{expense_id}/splits/{member_split.pk}/mark-paid/"
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["status"], "paid")

        # 9. Outsider gets 401
        outsider_client = APIClient()
        r = outsider_client.get(f"/api/expenses/{expense_id}/")
        self.assertEqual(r.status_code, 401)
