"""
Views for the Trips app.

TripViewSet
───────────
ModelViewSet providing list, create, retrieve, update, and destroy
actions.  Authentication is enforced via JWTCookieAuthentication
(configured globally in settings.py); per-object authorization is
handled by IsOrganizerOrReadOnly.

Queryset scoping
────────────────
``get_queryset`` returns only trips where the authenticated user is
either the organizer or a participant, preventing data leakage.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Trip
from .permissions import IsOrganizerOrReadOnly
from .serializers import TripSerializer


class TripViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for Trip resources."""

    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsOrganizerOrReadOnly]

    # ── Queryset ───────────────────────────────────────────────────────────

    def get_queryset(self):
        """
        Return trips visible to the requesting user:
        trips they organized OR trips they participate in.
        Uses `distinct()` to avoid duplicate rows from the M2M join.
        """
        user = self.request.user
        return (
            Trip.objects.filter(organizer=user)
            | Trip.objects.filter(participants=user)
        ).distinct().order_by("-created_at")

    # ── Write helpers ──────────────────────────────────────────────────────

    def perform_create(self, serializer):
        """Automatically assign the logged-in user as organizer."""
        serializer.save(organizer=self.request.user)
