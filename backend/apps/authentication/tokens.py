"""
JWT token utilities for MOVE backend.

Handles creation and validation of access and refresh tokens.
Tokens are passed via HTTP-only cookies — never exposed to JS.
"""

from __future__ import annotations

import datetime
import logging
from typing import Any

import jwt
from django.conf import settings

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Public helpers
# ─────────────────────────────────────────────────────────────────────────────


def _now_utc() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)


def generate_access_token(user: Any) -> str:
    """Create a short-lived JWT access token for *user*."""
    expiry = _now_utc() + datetime.timedelta(minutes=settings.JWT_ACCESS_MINUTES)
    payload = {
        "token_type": "access",
        "user_id": user.pk,
        "username": user.username,
        "email": user.email,
        "exp": expiry,
        "iat": _now_utc(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def generate_refresh_token(user: Any) -> str:
    """Create a long-lived JWT refresh token for *user*."""
    expiry = _now_utc() + datetime.timedelta(days=settings.JWT_REFRESH_DAYS)
    payload = {
        "token_type": "refresh",
        "user_id": user.pk,
        "exp": expiry,
        "iat": _now_utc(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Raises:
        jwt.ExpiredSignatureError  – token has expired.
        jwt.InvalidTokenError      – token is malformed / invalid.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


def set_auth_cookies(response: Any, access_token: str, refresh_token: str) -> None:
    """Attach HTTP-only JWT cookies to *response*."""
    access_max_age = settings.JWT_ACCESS_MINUTES * 60
    refresh_max_age = settings.JWT_REFRESH_DAYS * 24 * 60 * 60

    _set_cookie(response, settings.JWT_ACCESS_COOKIE_NAME, access_token, access_max_age)
    _set_cookie(response, settings.JWT_REFRESH_COOKIE_NAME, refresh_token, refresh_max_age)


def clear_auth_cookies(response: Any) -> None:
    """Remove JWT cookies from *response* (logout)."""
    response.delete_cookie(settings.JWT_ACCESS_COOKIE_NAME, samesite=settings.JWT_COOKIE_SAMESITE)
    response.delete_cookie(settings.JWT_REFRESH_COOKIE_NAME, samesite=settings.JWT_COOKIE_SAMESITE)


# ─────────────────────────────────────────────────────────────────────────────
# Internal
# ─────────────────────────────────────────────────────────────────────────────


def _set_cookie(response: Any, name: str, value: str, max_age: int) -> None:
    response.set_cookie(
        key=name,
        value=value,
        max_age=max_age,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/",
    )
