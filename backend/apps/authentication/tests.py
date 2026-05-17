"""
Tests for the JWT authentication app.

Covers:
  - Login with valid/invalid credentials
  - Cookie presence and HTTP-only flag
  - /me/ requires authentication
  - /refresh/ issues a new access token
  - /logout/ clears cookies
  - Expired and invalid token handling
"""

from __future__ import annotations

import datetime
import time

import jwt
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.tokens import (
    generate_access_token,
    generate_refresh_token,
)

User = get_user_model()

# ─── Shared test settings ────────────────────────────────────────────────────

JWT_TEST_SETTINGS = {
    "JWT_ACCESS_MINUTES": 15,
    "JWT_REFRESH_DAYS": 7,
    "JWT_ACCESS_COOKIE_NAME": "move_access_token",
    "JWT_REFRESH_COOKIE_NAME": "move_refresh_token",
    "JWT_COOKIE_SECURE": False,
    "JWT_COOKIE_SAMESITE": "Lax",
}


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_user(username="testuser", email="test@example.com", password="strongpass123"):
    return User.objects.create_user(username=username, email=email, password=password)


@override_settings(**JWT_TEST_SETTINGS)
class LoginViewTests(TestCase):
    """POST /api/auth/login/"""

    def setUp(self):
        self.client = APIClient()
        self.user = _make_user()
        self.url = reverse("authentication:login")

    def test_login_with_username_succeeds(self):
        res = self.client.post(
            self.url,
            {"login": "testuser", "password": "strongpass123"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("user", res.data)
        self.assertIn("move_access_token", res.cookies)
        self.assertIn("move_refresh_token", res.cookies)

    def test_login_with_email_succeeds(self):
        res = self.client.post(
            self.url,
            {"login": "test@example.com", "password": "strongpass123"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_access_cookie_is_http_only(self):
        res = self.client.post(
            self.url,
            {"login": "testuser", "password": "strongpass123"},
            format="json",
        )
        self.assertTrue(res.cookies["move_access_token"]["httponly"])

    def test_refresh_cookie_is_http_only(self):
        res = self.client.post(
            self.url,
            {"login": "testuser", "password": "strongpass123"},
            format="json",
        )
        self.assertTrue(res.cookies["move_refresh_token"]["httponly"])

    def test_wrong_password_returns_400(self):
        res = self.client.post(
            self.url,
            {"login": "testuser", "password": "wrongpass"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_user_returns_400(self):
        res = self.client.post(
            self.url,
            {"login": "nobody@example.com", "password": "whatever"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_user_returns_400(self):
        self.user.is_active = False
        self.user.save()
        res = self.client.post(
            self.url,
            {"login": "testuser", "password": "strongpass123"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_fields_returns_400(self):
        res = self.client.post(self.url, {"login": "testuser"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(**JWT_TEST_SETTINGS)
class MeViewTests(TestCase):
    """GET /api/auth/me/"""

    def setUp(self):
        self.client = APIClient()
        self.user = _make_user()
        self.url = reverse("authentication:me")

    def _set_access_cookie(self, user=None):
        token = generate_access_token(user or self.user)
        self.client.cookies["move_access_token"] = token

    def test_me_returns_user_data(self):
        self._set_access_cookie()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], self.user.username)
        self.assertEqual(res.data["email"], self.user.email)

    def test_me_without_cookie_returns_401(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_with_expired_token_returns_401(self):
        # Forge an already-expired token
        payload = {
            "token_type": "access",
            "user_id": self.user.pk,
            "username": self.user.username,
            "email": self.user.email,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(seconds=1),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(minutes=16),
        }
        from django.conf import settings

        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        self.client.cookies["move_access_token"] = expired_token
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("token_expired", str(res.data))

    def test_me_with_tampered_token_returns_401(self):
        self._set_access_cookie()
        self.client.cookies["move_access_token"] = "not.a.valid.token"
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(**JWT_TEST_SETTINGS)
class RefreshViewTests(TestCase):
    """POST /api/auth/refresh/"""

    def setUp(self):
        self.client = APIClient()
        self.user = _make_user()
        self.url = reverse("authentication:refresh")

    def test_refresh_issues_new_access_token(self):
        self.client.cookies["move_refresh_token"] = generate_refresh_token(self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("move_access_token", res.cookies)

    def test_refresh_without_cookie_returns_401(self):
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.data["code"], "no_refresh_token")

    def test_refresh_with_expired_token_returns_401(self):
        payload = {
            "token_type": "refresh",
            "user_id": self.user.pk,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(seconds=1),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=8),
        }
        from django.conf import settings

        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        self.client.cookies["move_refresh_token"] = expired_token
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.data["code"], "refresh_expired")

    def test_refresh_clears_cookies_on_expired_token(self):
        payload = {
            "token_type": "refresh",
            "user_id": self.user.pk,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(seconds=1),
            "iat": datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=8),
        }
        from django.conf import settings

        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        self.client.cookies["move_refresh_token"] = expired_token
        res = self.client.post(self.url)
        # Cookie should be deleted (max_age=0 or expires in the past)
        self.assertIn("move_refresh_token", res.cookies)

    def test_refresh_with_wrong_token_type_returns_401(self):
        # Send access token where refresh is expected
        access = generate_access_token(self.user)
        self.client.cookies["move_refresh_token"] = access
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.data["code"], "token_type_error")


@override_settings(**JWT_TEST_SETTINGS)
class LogoutViewTests(TestCase):
    """POST /api/auth/logout/"""

    def setUp(self):
        self.client = APIClient()
        self.user = _make_user()
        self.url = reverse("authentication:logout")

    def test_logout_clears_cookies(self):
        self.client.cookies["move_access_token"] = generate_access_token(self.user)
        self.client.cookies["move_refresh_token"] = generate_refresh_token(self.user)
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("move_access_token", res.cookies)
        self.assertIn("move_refresh_token", res.cookies)

    def test_logout_is_idempotent(self):
        """Logout without cookies should still return 200."""
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
