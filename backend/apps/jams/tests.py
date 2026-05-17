"""
Test suite for the JAMs app.

Coverage
────────
1.  Services / helpers:
    - is_jam_admin, is_jam_member, can_view_jam, can_manage_jam

2.  JAM creation (POST /api/trips/{trip_id}/jam/):
    - Authenticated user with trip access can create a JAM.
    - Creator auto-added as active admin.
    - Duplicate JAM for the same trip is rejected.
    - Unauthenticated → 401.
    - User without trip access → 403.

3.  JAM retrieval via trip (GET /api/trips/{trip_id}/jam/):
    - JAM member can retrieve.
    - Non-member (even with trip access) → 403.
    - Trip without JAM → 404.

4.  Standalone JAM (GET/PATCH/DELETE /api/jams/{id}/):
    - Admin can retrieve.
    - Member can retrieve.
    - Outsider cannot retrieve.
    - Admin can edit.
    - Member cannot edit (403).
    - Admin can delete.

5.  Members (GET/POST/PATCH/DELETE /api/jams/{id}/members/):
    - Member can list members.
    - Outsider cannot list members (403).
    - Admin can add a member.
    - Member cannot add a member (403).
    - Duplicate member rejected.
    - Admin can change role.
    - Member cannot change role (403).
    - Admin can remove a member.
    - Cannot remove the last active admin.
    - Cannot demote the last active admin.

All tests use force_authenticate (not real JWT cookies) — the cookie
stack is tested in apps.authentication.tests.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.trips.models import Trip

from .models import Jam, JamMember
from .services import (
    can_manage_jam,
    can_view_jam,
    is_jam_admin,
    is_jam_member,
)

User = get_user_model()


# ── Factories ──────────────────────────────────────────────────────────────────


def make_user(username: str, password: str = "StrongPass123!") -> User:
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password=password,
    )


def make_trip(organizer: User, **kwargs) -> Trip:
    kwargs.setdefault("name", f"{organizer.username}'s trip")
    return Trip.objects.create(organizer=organizer, **kwargs)


def make_jam(trip: Trip, created_by: User, **kwargs) -> Jam:
    kwargs.setdefault("name", f"JAM for {trip.name}")
    # Creating Jam via ORM triggers post_save signal → adds creator as admin.
    return Jam.objects.create(trip=trip, created_by=created_by, **kwargs)


def add_member(jam: Jam, user: User, role=JamMember.Role.MEMBER) -> JamMember:
    return JamMember.objects.create(
        jam=jam,
        user=user,
        role=role,
        status=JamMember.Status.ACTIVE,
    )


# ── 1. Services / helpers ─────────────────────────────────────────────────────


class ServiceTests(APITestCase):
    """Unit tests for apps.jams.services helpers."""

    def setUp(self):
        self.organizer = make_user("organizer")
        self.trip = make_trip(organizer=self.organizer)
        self.jam = make_jam(trip=self.trip, created_by=self.organizer)
        # organizer is now auto-admin via signal.

        self.member_user = make_user("member_user")
        add_member(self.jam, self.member_user, role=JamMember.Role.MEMBER)

        self.outsider = make_user("outsider")

    def test_is_jam_admin_true_for_creator(self):
        self.assertTrue(is_jam_admin(self.organizer, self.jam))

    def test_is_jam_admin_false_for_member(self):
        self.assertFalse(is_jam_admin(self.member_user, self.jam))

    def test_is_jam_admin_false_for_outsider(self):
        self.assertFalse(is_jam_admin(self.outsider, self.jam))

    def test_is_jam_member_true_for_admin(self):
        self.assertTrue(is_jam_member(self.organizer, self.jam))

    def test_is_jam_member_true_for_member(self):
        self.assertTrue(is_jam_member(self.member_user, self.jam))

    def test_is_jam_member_false_for_outsider(self):
        self.assertFalse(is_jam_member(self.outsider, self.jam))

    def test_can_view_jam_true_for_active_member(self):
        self.assertTrue(can_view_jam(self.member_user, self.jam))

    def test_can_view_jam_false_for_removed_member(self):
        membership = JamMember.objects.get(jam=self.jam, user=self.member_user)
        membership.status = JamMember.Status.REMOVED
        membership.save()
        self.assertFalse(can_view_jam(self.member_user, self.jam))

    def test_can_manage_jam_true_for_admin(self):
        self.assertTrue(can_manage_jam(self.organizer, self.jam))

    def test_can_manage_jam_false_for_member(self):
        self.assertFalse(can_manage_jam(self.member_user, self.jam))


# ── 2. JAM creation ────────────────────────────────────────────────────────────


class JamCreateTests(APITestCase):
    """POST /api/trips/{trip_id}/jam/"""

    def setUp(self):
        self.organizer = make_user("alice")
        self.stranger = make_user("stranger")
        self.trip = make_trip(organizer=self.organizer)
        self.url = reverse("trip-jam", kwargs={"trip_id": self.trip.pk})

    def test_organizer_can_create_jam(self):
        self.client.force_authenticate(user=self.organizer)
        res = self.client.post(self.url, {"name": "Lisbon JAM"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], "Lisbon JAM")
        self.assertTrue(Jam.objects.filter(trip=self.trip).exists())

    def test_creator_auto_added_as_active_admin(self):
        self.client.force_authenticate(user=self.organizer)
        self.client.post(self.url, {"name": "Lisbon JAM"}, format="json")
        jam = Jam.objects.get(trip=self.trip)
        membership = JamMember.objects.get(jam=jam, user=self.organizer)
        self.assertEqual(membership.role, JamMember.Role.ADMIN)
        self.assertEqual(membership.status, JamMember.Status.ACTIVE)

    def test_cannot_create_second_jam_for_same_trip(self):
        make_jam(trip=self.trip, created_by=self.organizer)
        self.client.force_authenticate(user=self.organizer)
        res = self.client.post(self.url, {"name": "Second JAM"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_returns_401(self):
        res = self.client.post(self.url, {"name": "JAM"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_without_trip_access_returns_403(self):
        self.client.force_authenticate(user=self.stranger)
        res = self.client.post(self.url, {"name": "Hijack JAM"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_participant_can_create_jam(self):
        participant = make_user("participant")
        self.trip.participants.add(participant)
        self.client.force_authenticate(user=participant)
        res = self.client.post(self.url, {"name": "Participant JAM"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_created_by_from_request_not_body(self):
        """Ensure `created_by` cannot be spoofed via request body."""
        self.client.force_authenticate(user=self.organizer)
        res = self.client.post(
            self.url,
            {"name": "Spoofed", "created_by": self.stranger.pk},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        jam = Jam.objects.get(trip=self.trip)
        self.assertEqual(jam.created_by, self.organizer)


# ── 3. GET /api/trips/{trip_id}/jam/ ─────────────────────────────────────────


class TripJamGetTests(APITestCase):
    """GET /api/trips/{trip_id}/jam/"""

    def setUp(self):
        self.organizer = make_user("alice")
        self.trip = make_trip(organizer=self.organizer)
        self.jam = make_jam(trip=self.trip, created_by=self.organizer)
        self.url = reverse("trip-jam", kwargs={"trip_id": self.trip.pk})

    def test_jam_admin_can_get_trip_jam(self):
        self.client.force_authenticate(user=self.organizer)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], self.jam.pk)

    def test_jam_member_can_get_trip_jam(self):
        member = make_user("bob")
        self.trip.participants.add(member)
        add_member(self.jam, member)
        self.client.force_authenticate(user=member)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_non_jam_member_cannot_get_trip_jam(self):
        """User has trip access but is not in the JAM."""
        participant = make_user("participant")
        self.trip.participants.add(participant)
        self.client.force_authenticate(user=participant)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_trip_without_jam_returns_404(self):
        trip2 = make_trip(organizer=self.organizer, name="Empty Trip")
        url = reverse("trip-jam", kwargs={"trip_id": trip2.pk})
        self.client.force_authenticate(user=self.organizer)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ── 4. Standalone JAM detail ───────────────────────────────────────────────────


class JamDetailTests(APITestCase):
    """GET / PATCH / DELETE /api/jams/{jam_id}/"""

    def setUp(self):
        self.admin_user = make_user("admin_user")
        self.member_user = make_user("member_user")
        self.outsider = make_user("outsider")

        self.trip = make_trip(organizer=self.admin_user)
        self.jam = make_jam(trip=self.trip, created_by=self.admin_user)
        add_member(self.jam, self.member_user, role=JamMember.Role.MEMBER)

        self.url = reverse("jam-detail", kwargs={"jam_id": self.jam.pk})

    def test_admin_can_retrieve_jam(self):
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], self.jam.name)

    def test_member_can_retrieve_jam(self):
        self.client.force_authenticate(user=self.member_user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_outsider_cannot_retrieve_jam(self):
        self.client.force_authenticate(user=self.outsider)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_edit_jam(self):
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.patch(self.url, {"name": "Updated Name"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.jam.refresh_from_db()
        self.assertEqual(self.jam.name, "Updated Name")

    def test_member_cannot_edit_jam(self):
        self.client.force_authenticate(user=self.member_user)
        res = self.client.patch(self.url, {"name": "Hijacked"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_cannot_edit_jam(self):
        self.client.force_authenticate(user=self.outsider)
        res = self.client.patch(self.url, {"name": "Hijacked"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_jam(self):
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Jam.objects.filter(pk=self.jam.pk).exists())

    def test_unauthenticated_returns_401(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ── 5. Members ─────────────────────────────────────────────────────────────────


class JamMemberListTests(APITestCase):
    """GET /api/jams/{jam_id}/members/"""

    def setUp(self):
        self.admin_user = make_user("admin_user")
        self.member_user = make_user("member_user")
        self.outsider = make_user("outsider")

        self.trip = make_trip(organizer=self.admin_user)
        self.jam = make_jam(trip=self.trip, created_by=self.admin_user)
        add_member(self.jam, self.member_user)

        self.url = reverse("jam-members", kwargs={"jam_id": self.jam.pk})

    def test_admin_can_list_members(self):
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)  # admin + member

    def test_member_can_list_members(self):
        self.client.force_authenticate(user=self.member_user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_outsider_cannot_list_members(self):
        self.client.force_authenticate(user=self.outsider)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class JamMemberAddTests(APITestCase):
    """POST /api/jams/{jam_id}/members/"""

    def setUp(self):
        self.admin_user = make_user("admin_user")
        self.member_user = make_user("member_user")
        self.new_user = make_user("new_user")

        self.trip = make_trip(organizer=self.admin_user)
        self.trip.participants.add(self.new_user)  # give trip access
        self.jam = make_jam(trip=self.trip, created_by=self.admin_user)
        add_member(self.jam, self.member_user)

        self.url = reverse("jam-members", kwargs={"jam_id": self.jam.pk})

    def test_admin_can_add_member(self):
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.post(
            self.url, {"user_id": self.new_user.pk}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            JamMember.objects.filter(jam=self.jam, user=self.new_user).exists()
        )

    def test_member_cannot_add_member(self):
        self.client.force_authenticate(user=self.member_user)
        res = self.client.post(
            self.url, {"user_id": self.new_user.pk}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_add_duplicate_member(self):
        self.client.force_authenticate(user=self.admin_user)
        # member_user is already in the JAM
        res = self.client.post(
            self.url, {"user_id": self.member_user.pk}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_add_user_without_trip_access(self):
        no_access_user = make_user("no_access_user")
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.post(
            self.url, {"user_id": no_access_user.pk}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class JamMemberUpdateTests(APITestCase):
    """PATCH /api/jams/{jam_id}/members/{member_id}/"""

    def setUp(self):
        self.admin_user = make_user("admin_user")
        self.member_user = make_user("member_user")
        self.outsider = make_user("outsider")

        self.trip = make_trip(organizer=self.admin_user)
        self.jam = make_jam(trip=self.trip, created_by=self.admin_user)
        self.membership = add_member(self.jam, self.member_user)

        self.url = reverse(
            "jam-member-detail",
            kwargs={"jam_id": self.jam.pk, "member_id": self.membership.pk},
        )

    def test_admin_can_promote_member_to_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.patch(self.url, {"role": "admin"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.membership.refresh_from_db()
        self.assertEqual(self.membership.role, JamMember.Role.ADMIN)

    def test_member_cannot_change_roles(self):
        self.client.force_authenticate(user=self.member_user)
        res = self.client.patch(self.url, {"role": "admin"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_cannot_change_roles(self):
        self.client.force_authenticate(user=self.outsider)
        res = self.client.patch(self.url, {"role": "admin"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_demote_last_active_admin(self):
        # admin_user is the only admin
        admin_membership = JamMember.objects.get(jam=self.jam, user=self.admin_user)
        url = reverse(
            "jam-member-detail",
            kwargs={"jam_id": self.jam.pk, "member_id": admin_membership.pk},
        )
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.patch(url, {"role": "member"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class JamMemberRemoveTests(APITestCase):
    """DELETE /api/jams/{jam_id}/members/{member_id}/"""

    def setUp(self):
        self.admin_user = make_user("admin_user")
        self.member_user = make_user("member_user")
        self.outsider = make_user("outsider")

        self.trip = make_trip(organizer=self.admin_user)
        self.jam = make_jam(trip=self.trip, created_by=self.admin_user)
        self.membership = add_member(self.jam, self.member_user)

        self.url = reverse(
            "jam-member-detail",
            kwargs={"jam_id": self.jam.pk, "member_id": self.membership.pk},
        )

    def test_admin_can_remove_member(self):
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            JamMember.objects.filter(pk=self.membership.pk).exists()
        )

    def test_member_cannot_remove_member(self):
        self.client.force_authenticate(user=self.member_user)
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_remove_last_active_admin(self):
        admin_membership = JamMember.objects.get(jam=self.jam, user=self.admin_user)
        url = reverse(
            "jam-member-detail",
            kwargs={"jam_id": self.jam.pk, "member_id": admin_membership.pk},
        )
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_returns_401(self):
        res = self.client.delete(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
