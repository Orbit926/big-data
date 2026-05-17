"""
Authentication views for MOVE.

Endpoints
---------
POST /api/auth/register/ – create account + auto-login (issue JWT cookies)
POST /api/auth/login/    – issue access + refresh tokens via HTTP-only cookies
POST /api/auth/logout/   – clear both cookies
POST /api/auth/refresh/  – rotate access token using refresh cookie
GET  /api/auth/me/       – return the authenticated user's profile
"""

from __future__ import annotations

import logging

import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .backends import JWTCookieAuthentication
from .serializers import LoginSerializer, RegisterSerializer, UserMeSerializer
from .tokens import (
    clear_auth_cookies,
    decode_token,
    generate_access_token,
    generate_refresh_token,
    set_auth_cookies,
)

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """
    POST /api/auth/login/

    Body: { "login": "<email or username>", "password": "<password>" }

    On success sets two HTTP-only cookies:
        move_access_token  – short-lived access JWT
        move_refresh_token – long-lived refresh JWT
    """

    authentication_classes = []  # No auth required to log in
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        response = Response(
            {
                "detail": "Login successful.",
                "user": UserMeSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
        set_auth_cookies(response, access_token, refresh_token)
        logger.info("User %s logged in.", user.username)
        return response


class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Clears both JWT cookies. Works whether the user is authenticated or not
    (idempotent logout).
    """

    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        clear_auth_cookies(response)
        if request.user and request.user.is_authenticated:
            logger.info("User %s logged out.", request.user.username)
        return response


class RefreshView(APIView):
    """
    POST /api/auth/refresh/

    Reads the refresh cookie, validates it, and issues a new access token.
    Does NOT rotate the refresh token to avoid invalidating long sessions.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)

        if not refresh_token:
            return Response(
                {"code": "no_refresh_token", "detail": "Refresh token cookie is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = decode_token(refresh_token)
        except jwt.ExpiredSignatureError:
            response = Response(
                {"code": "refresh_expired", "detail": "Refresh token has expired. Please log in again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            clear_auth_cookies(response)
            return response
        except jwt.InvalidTokenError:
            response = Response(
                {"code": "refresh_invalid", "detail": "Refresh token is invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            clear_auth_cookies(response)
            return response

        if payload.get("token_type") != "refresh":
            return Response(
                {"code": "token_type_error", "detail": "Expected a refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(pk=payload["user_id"])
        except User.DoesNotExist:
            response = Response(
                {"code": "user_not_found", "detail": "User no longer exists."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            clear_auth_cookies(response)
            return response

        if not user.is_active:
            response = Response(
                {"code": "user_inactive", "detail": "This account has been deactivated."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            clear_auth_cookies(response)
            return response

        new_access_token = generate_access_token(user)
        response = Response({"detail": "Token refreshed."}, status=status.HTTP_200_OK)
        # Only update the access cookie — keep the existing refresh cookie.
        from .tokens import _set_cookie

        _set_cookie(
            response,
            settings.JWT_ACCESS_COOKIE_NAME,
            new_access_token,
            settings.JWT_ACCESS_MINUTES * 60,
        )
        logger.debug("Access token refreshed for user %s.", user.username)
        return response


class MeView(APIView):
    """
    GET /api/auth/me/

    Returns the authenticated user's profile.
    Requires a valid access token cookie (IsAuthenticated).
    """

    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """
    POST /api/auth/register/

    Body:
        username        – required, unique
        email           – required, unique
        password        – required, min 8 chars
        password_confirm – required, must match password
        first_name      – optional
        last_name       – optional

    On success:
        - Creates the user via apps.users.User (get_user_model()).
        - Immediately issues JWT cookies so the user is logged in.
        - Returns 201 with the new user's session profile.

    Error responses:
        400 – validation errors (duplicate username/email, password mismatch, etc.)
    """

    authentication_classes = []  # No auth required to register
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)

        response = Response(
            {
                "detail": "Account created successfully.",
                "user": UserMeSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
        set_auth_cookies(response, access_token, refresh_token)
        logger.info("New user registered: %s", user.username)
        return response
