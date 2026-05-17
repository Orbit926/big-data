"""
Views for the Users app.

Responsibility: profile management of authenticated users and public profile lookup.
Authentication flows (register, login, logout, refresh) live in apps.authentication.

Endpoints
---------
GET  /api/users/me/          → authenticated user's full profile
PATCH /api/users/me/         → update own profile (bio, avatar, first_name, last_name)
GET  /api/users/<id>/        → public profile of any user (read-only)
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserProfileSerializer, UserPublicSerializer

User = get_user_model()


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/users/me/   → return the authenticated user's full profile.
    PATCH /api/users/me/ → update writable profile fields.

    PUT is disabled intentionally — use PATCH for partial updates.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]  # no PUT

    def get_object(self):
        return self.request.user


class UserDetailView(generics.RetrieveAPIView):
    """
    GET /api/users/<id>/ → public, read-only profile of any user.
    Requires authentication so anonymous users cannot enumerate accounts.
    """

    serializer_class = UserPublicSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(is_active=True)
