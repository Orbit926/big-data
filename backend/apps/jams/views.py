"""
Views for the JAMs app.

Route layout (see urls.py for exact patterns):

  Nested under /api/trips/{trip_id}/:
    POST   /api/trips/{trip_id}/jam/          → TripJamView.post   (create)
    GET    /api/trips/{trip_id}/jam/          → TripJamView.get    (retrieve via trip)

  Standalone JAM:
    GET    /api/jams/{jam_id}/               → JamDetailView.get
    PATCH  /api/jams/{jam_id}/               → JamDetailView.patch
    DELETE /api/jams/{jam_id}/               → JamDetailView.delete

  Members:
    GET    /api/jams/{jam_id}/members/               → JamMemberListCreateView.get
    POST   /api/jams/{jam_id}/members/               → JamMemberListCreateView.post
    PATCH  /api/jams/{jam_id}/members/{member_id}/  → JamMemberDetailView.patch
    DELETE /api/jams/{jam_id}/members/{member_id}/  → JamMemberDetailView.delete

Permission matrix (enforced per-view):
  - Unauthenticated           → 401 (IsAuthenticated)
  - No trip access            → 403 (user_has_trip_access check)
  - JAM outsider              → 403 / 404 depending on endpoint
  - JAM member (SAFE_METHODS) → 200
  - JAM admin (all methods)   → 200
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.trips.models import Trip

from .models import Jam, JamMember
from .serializers import (
    JamCreateUpdateSerializer,
    JamDetailSerializer,
    JamMemberCreateSerializer,
    JamMemberSerializer,
    JamMemberUpdateSerializer,
)
from .services import (
    can_manage_jam,
    can_manage_jam_members,
    can_view_jam,
    guard_last_admin_or_raise,
    user_has_trip_access,
)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _get_trip_or_403(trip_id, user):
    """Return the Trip if user has access, else 403."""
    trip = get_object_or_404(Trip, pk=trip_id)
    if not user_has_trip_access(user, trip):
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("You do not have access to this trip.")
    return trip


def _get_jam_or_404(jam_id):
    return get_object_or_404(Jam, pk=jam_id)


# ── Trip-scoped JAM view ───────────────────────────────────────────────────────


class TripJamView(APIView):
    """
    GET  /api/trips/{trip_id}/jam/  → retrieve the JAM of this trip
    POST /api/trips/{trip_id}/jam/  → create the JAM for this trip
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, trip_id):
        trip = _get_trip_or_403(trip_id, request.user)

        jam = getattr(trip, "jam", None)
        if jam is None:
            return Response(
                {"detail": "This trip does not have a JAM yet."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only active JAM members can see the detail.
        if not can_view_jam(request.user, jam):
            return Response(
                {"detail": "You are not a member of this JAM."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(JamDetailSerializer(jam).data)

    def post(self, request, trip_id):
        trip = _get_trip_or_403(trip_id, request.user)

        # Enforce one JAM per trip.
        if hasattr(trip, "jam"):
            return Response(
                {"detail": "This trip already has a JAM."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = JamCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        jam = serializer.save(trip=trip, created_by=request.user)

        return Response(JamDetailSerializer(jam).data, status=status.HTTP_201_CREATED)


# ── Standalone JAM view ────────────────────────────────────────────────────────


class JamDetailView(APIView):
    """
    GET    /api/jams/{jam_id}/  → retrieve JAM detail
    PATCH  /api/jams/{jam_id}/  → partial update (admin only)
    DELETE /api/jams/{jam_id}/  → soft-delete / hard delete (admin only)
    """

    permission_classes = [IsAuthenticated]

    def _get_jam_with_permission(self, jam_id, user, require_admin=False):
        jam = _get_jam_or_404(jam_id)
        if require_admin:
            if not can_manage_jam(user, jam):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Only JAM admins can perform this action.")
        else:
            if not can_view_jam(user, jam):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You are not a member of this JAM.")
        return jam

    def get(self, request, jam_id):
        jam = self._get_jam_with_permission(jam_id, request.user)
        return Response(JamDetailSerializer(jam).data)

    def patch(self, request, jam_id):
        jam = self._get_jam_with_permission(jam_id, request.user, require_admin=True)
        serializer = JamCreateUpdateSerializer(jam, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(JamDetailSerializer(jam).data)

    def delete(self, request, jam_id):
        jam = self._get_jam_with_permission(jam_id, request.user, require_admin=True)
        jam.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── JAM Members ────────────────────────────────────────────────────────────────


class JamMemberListCreateView(APIView):
    """
    GET  /api/jams/{jam_id}/members/  → list all active members (member+)
    POST /api/jams/{jam_id}/members/  → add a member (admin only)
    """

    permission_classes = [IsAuthenticated]

    def _get_jam(self, jam_id, user, require_admin=False):
        jam = _get_jam_or_404(jam_id)
        if require_admin:
            if not can_manage_jam_members(user, jam):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Only JAM admins can manage members.")
        else:
            if not can_view_jam(user, jam):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You are not a member of this JAM.")
        return jam

    def get(self, request, jam_id):
        jam = self._get_jam(jam_id, request.user)
        members = jam.memberships.select_related("user").all()
        return Response(JamMemberSerializer(members, many=True).data)

    def post(self, request, jam_id):
        jam = self._get_jam(jam_id, request.user, require_admin=True)

        serializer = JamMemberCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_to_add = serializer.validated_data["user"]

        # Guard: no duplicate members.
        if JamMember.objects.filter(jam=jam, user=user_to_add).exists():
            return Response(
                {"detail": "This user is already a member of this JAM."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Guard: validate trip access (isolated — can be hardened later).
        # TODO: when trip membership is more strictly enforced, replace
        # user_has_trip_access with a stricter check.
        if not user_has_trip_access(user_to_add, jam.trip):
            return Response(
                {"detail": "User does not have access to the underlying trip."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member = JamMember.objects.create(
            jam=jam,
            user=user_to_add,
            role=serializer.validated_data.get("role", JamMember.Role.MEMBER),
            status=JamMember.Status.ACTIVE,
        )
        return Response(JamMemberSerializer(member).data, status=status.HTTP_201_CREATED)


class JamMemberDetailView(APIView):
    """
    PATCH  /api/jams/{jam_id}/members/{member_id}/  → change role/status (admin)
    DELETE /api/jams/{jam_id}/members/{member_id}/  → remove member (admin)
    """

    permission_classes = [IsAuthenticated]

    def _get_membership(self, jam_id, member_id, user):
        jam = _get_jam_or_404(jam_id)
        if not can_manage_jam_members(user, jam):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only JAM admins can manage members.")
        membership = get_object_or_404(JamMember, pk=member_id, jam=jam)
        return jam, membership

    def patch(self, request, jam_id, member_id):
        jam, membership = self._get_membership(jam_id, member_id, request.user)

        serializer = JamMemberUpdateSerializer(
            membership, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        new_role = serializer.validated_data.get("role")
        new_status = serializer.validated_data.get("status")

        # Guard last-admin constraint — delegated to services.py.
        guard_last_admin_or_raise(
            jam,
            membership,
            new_role=new_role,
            removing=(new_status == JamMember.Status.REMOVED),
        )

        serializer.save()
        membership.refresh_from_db()
        return Response(JamMemberSerializer(membership).data)

    def delete(self, request, jam_id, member_id):
        jam, membership = self._get_membership(jam_id, member_id, request.user)
        guard_last_admin_or_raise(jam, membership, removing=True)
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
