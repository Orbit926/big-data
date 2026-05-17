"""
Custom DRF authentication backend.

Reads the JWT access token from the HTTP-only cookie and authenticates
the request transparently — the frontend never needs to send headers.

Usage in settings.py:
    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "apps.authentication.backends.JWTCookieAuthentication",
        ],
        ...
    }
"""

from __future__ import annotations

import logging

import jwt
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .tokens import decode_token

User = get_user_model()
logger = logging.getLogger(__name__)


class JWTCookieAuthentication(BaseAuthentication):
    """
    Authenticate requests using the access JWT stored in an HTTP-only cookie.

    Defines ``authenticate_header`` so DRF returns HTTP 401 (not 403) for
    unauthenticated requests — required by the WWW-Authenticate spec.
    """

    def authenticate_header(self, request) -> str:
        """Return a non-empty string so DRF sends 401, not 403."""
        return 'Bearer realm="move-api"'

    def authenticate(self, request):
        token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE_NAME)

        if not token:
            # No cookie → anonymous request; let permission classes decide.
            return None

        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed(
                {"code": "token_expired", "detail": "Access token has expired. Please refresh."}
            )
        except jwt.InvalidTokenError as exc:
            logger.warning("Invalid JWT received: %s", exc)
            raise AuthenticationFailed(
                {"code": "token_invalid", "detail": "Token is invalid or tampered."}
            )

        if payload.get("token_type") != "access":
            raise AuthenticationFailed(
                {"code": "token_type_error", "detail": "Expected an access token."}
            )

        user = self._get_user(payload)
        return (user, token)

    # ------------------------------------------------------------------

    @staticmethod
    def _get_user(payload: dict):
        user_id = payload.get("user_id")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed(
                {"code": "user_not_found", "detail": "No user matches this token."}
            )

        if not user.is_active:
            raise AuthenticationFailed(
                {"code": "user_inactive", "detail": "This account has been deactivated."}
            )

        return user
