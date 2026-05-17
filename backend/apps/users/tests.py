"""
Tests for the Users app.

Covers:
  - GET  /api/users/me/    → returns authenticated user's profile
  - PATCH /api/users/me/   → updates writable profile fields
  - GET  /api/users/<id>/  → public profile (authenticated required)
  - Security: unauthenticated requests blocked, cross-user updates not possible
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.tokens import generate_access_token

User = get_user_model()


# ── Helpers ────────────────────────────────────────────────────────────────────


def make_user(username, email=None, password="StrongPass123!"):
    return User.objects.create_user(
        username=username,
        email=email or f"{username}@example.com",
        password=password,
    )


def auth_client(client, user):
    """Inject a valid access cookie into the test client."""
    token = generate_access_token(user)
    client.cookies["move_access_token"] = token
    return client


# ── Profile (own user) ─────────────────────────────────────────────────────────


class ProfileViewTests(APITestCase):
    """GET + PATCH /api/users/me/"""

    def setUp(self):
        self.user = make_user("alice", "alice@example.com")
        auth_client(self.client, self.user)
        self.url = reverse("user-profile")

    def test_get_own_profile_returns_200(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_own_profile_returns_correct_fields(self):
        res = self.client.get(self.url)
        self.assertEqual(res.data["username"], "alice")
        self.assertEqual(res.data["email"], "alice@example.com")
        self.assertIn("bio", res.data)
        self.assertIn("avatar", res.data)
        self.assertIn("first_name", res.data)
        self.assertIn("last_name", res.data)

    def test_patch_bio_updates_correctly(self):
        res = self.client.patch(self.url, {"bio": "Hello world"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "Hello world")

    def test_patch_avatar_updates_correctly(self):
        url = "https://example.com/avatar.png"
        res = self.client.patch(self.url, {"avatar": url}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar, url)

    def test_patch_first_and_last_name(self):
        res = self.client.patch(
            self.url,
            {"first_name": "Alice", "last_name": "Smith"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Alice")
        self.assertEqual(self.user.last_name, "Smith")

    def test_patch_username_is_read_only(self):
        """username cannot be changed via profile endpoint."""
        self.client.patch(self.url, {"username": "hacker"}, format="json")
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "alice")

    def test_patch_email_is_read_only(self):
        """email cannot be changed via profile endpoint."""
        self.client.patch(self.url, {"email": "hacked@evil.com"}, format="json")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "alice@example.com")

    def test_put_not_allowed(self):
        """PUT is disabled on profile endpoint."""
        res = self.client.put(self.url, {"bio": "test"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthenticated_returns_401(self):
        self.client.cookies.clear()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ── Public profile ──────────────────────────────────────────────────────────────


class UserDetailViewTests(APITestCase):
    """GET /api/users/<id>/"""

    def setUp(self):
        self.viewer = make_user("viewer")
        self.target = make_user("target", "target@example.com")
        auth_client(self.client, self.viewer)
        self.url = reverse("user-detail", kwargs={"pk": self.target.pk})

    def test_authenticated_user_can_view_public_profile(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], "target")

    def test_public_profile_exposes_only_safe_fields(self):
        """Public profile should NOT expose email or bio."""
        res = self.client.get(self.url)
        self.assertNotIn("email", res.data)
        self.assertNotIn("bio", res.data)
        self.assertIn("username", res.data)
        self.assertIn("avatar", res.data)
        self.assertIn("date_joined", res.data)

    def test_unauthenticated_returns_401(self):
        self.client.cookies.clear()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_user_returns_404(self):
        url = reverse("user-detail", kwargs={"pk": 99999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
