"""
Test suite for the Trips app.

Coverage
────────
1. Create trip  → verify organizer auto-assigned, participants writable.
2. List trips   → user sees only their own trips (organized + participating).
3. Retrieve trip → organizer and participant can read; stranger cannot.
4. Update trip  → only organizer allowed; participant gets 403.
5. Delete trip  → only organizer allowed; stranger gets 403.

Authentication is faked via force_authenticate so the JWT cookie stack
is not exercised here — that is covered in apps.authentication.tests.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Trip

User = get_user_model()

# ── Helpers ────────────────────────────────────────────────────────────────


def make_user(username: str, password: str = "StrongPass123!") -> User:
    return User.objects.create_user(username=username, password=password)


def make_trip(organizer: User, name: str = "Test Trip", **kwargs) -> Trip:
    trip = Trip.objects.create(organizer=organizer, name=name, **kwargs)
    return trip


# ── Test cases ─────────────────────────────────────────────────────────────


class TripCreateTests(APITestCase):
    """POST /api/trips/"""

    def setUp(self):
        self.organizer = make_user("alice")
        self.participant = make_user("bob")
        self.url = reverse("trips-list")

    def test_create_trip_assigns_organizer(self):
        """Organizer field is set to the requesting user."""
        self.client.force_authenticate(user=self.organizer)
        payload = {"name": "Summer Adventure", "description": "Beach trip"}
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["organizer"], self.organizer.username)
        trip = Trip.objects.get(pk=response.data["id"])
        self.assertEqual(trip.organizer, self.organizer)

    def test_create_trip_with_participants(self):
        """Participants can be set via participant_ids at creation time."""
        self.client.force_authenticate(user=self.organizer)
        payload = {
            "name": "Group Trek",
            "participant_ids": [self.participant.pk],
        }
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        trip = Trip.objects.get(pk=response.data["id"])
        self.assertIn(self.participant, trip.participants.all())
        # participants field returns usernames
        self.assertIn(self.participant.username, response.data["participants"])

    def test_create_trip_unauthenticated_returns_401(self):
        """Unauthenticated requests are rejected."""
        response = self.client.post(self.url, {"name": "Secret"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TripListTests(APITestCase):
    """GET /api/trips/"""

    def setUp(self):
        self.alice = make_user("alice")
        self.bob = make_user("bob")
        self.carol = make_user("carol")

        # Alice organizes trip_a
        self.trip_a = make_trip(organizer=self.alice, name="Alice's Trip")
        # Bob organizes trip_b and adds alice as participant
        self.trip_b = make_trip(organizer=self.bob, name="Bob's Trip")
        self.trip_b.participants.add(self.alice)
        # Carol organizes trip_c — completely unrelated to alice
        self.trip_c = make_trip(organizer=self.carol, name="Carol's Trip")

        self.url = reverse("trips-list")

    def test_user_sees_organized_and_participating_trips(self):
        """Alice should see trip_a (organized) and trip_b (participant)."""
        self.client.force_authenticate(user=self.alice)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [t["name"] for t in response.data]
        self.assertIn("Alice's Trip", names)
        self.assertIn("Bob's Trip", names)

    def test_user_does_not_see_unrelated_trips(self):
        """Alice must NOT see Carol's trip."""
        self.client.force_authenticate(user=self.alice)
        response = self.client.get(self.url)

        names = [t["name"] for t in response.data]
        self.assertNotIn("Carol's Trip", names)

    def test_list_unauthenticated_returns_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TripRetrieveTests(APITestCase):
    """GET /api/trips/<id>/"""

    def setUp(self):
        self.organizer = make_user("alice")
        self.participant = make_user("bob")
        self.stranger = make_user("carol")
        self.trip = make_trip(organizer=self.organizer, name="Secret Getaway")
        self.trip.participants.add(self.participant)
        self.url = reverse("trips-detail", kwargs={"pk": self.trip.pk})

    def test_organizer_can_retrieve(self):
        self.client.force_authenticate(user=self.organizer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Secret Getaway")

    def test_participant_can_retrieve(self):
        self.client.force_authenticate(user=self.participant)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stranger_cannot_retrieve(self):
        """Carol is neither organizer nor participant → 404 (not in queryset)."""
        self.client.force_authenticate(user=self.stranger)
        response = self.client.get(self.url)
        # The scoped queryset returns 404, not 403, to avoid leaking existence.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TripUpdateTests(APITestCase):
    """PUT / PATCH /api/trips/<id>/"""

    def setUp(self):
        self.organizer = make_user("alice")
        self.participant = make_user("bob")
        self.trip = make_trip(organizer=self.organizer, name="Original Name")
        self.trip.participants.add(self.participant)
        self.url = reverse("trips-detail", kwargs={"pk": self.trip.pk})

    def test_organizer_can_update(self):
        self.client.force_authenticate(user=self.organizer)
        response = self.client.patch(self.url, {"name": "Updated Name"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.name, "Updated Name")

    def test_participant_cannot_update_returns_403(self):
        """Participant attempting to edit receives 403 Forbidden."""
        self.client.force_authenticate(user=self.participant)
        response = self.client.patch(self.url, {"name": "Hijacked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_update_returns_404(self):
        """Stranger not in queryset gets 404."""
        stranger = make_user("carol")
        self.client.force_authenticate(user=stranger)
        response = self.client.patch(self.url, {"name": "Hijacked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_cannot_update(self):
        response = self.client.patch(self.url, {"name": "Hijacked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TripDeleteTests(APITestCase):
    """DELETE /api/trips/<id>/"""

    def setUp(self):
        self.organizer = make_user("alice")
        self.participant = make_user("bob")
        self.trip = make_trip(organizer=self.organizer, name="To Be Deleted")
        self.trip.participants.add(self.participant)
        self.url = reverse("trips-detail", kwargs={"pk": self.trip.pk})

    def test_organizer_can_delete(self):
        self.client.force_authenticate(user=self.organizer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Trip.objects.filter(pk=self.trip.pk).exists())

    def test_participant_cannot_delete_returns_403(self):
        self.client.force_authenticate(user=self.participant)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_delete_returns_404(self):
        stranger = make_user("carol")
        self.client.force_authenticate(user=stranger)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
