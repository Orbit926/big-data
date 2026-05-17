"""
Permissions for the Trips app.

IsOrganizerOrReadOnly
─────────────────────
- SAFE_METHODS (GET, HEAD, OPTIONS): allowed for any authenticated user
  who is either the organizer or a participant.
- Mutating methods (POST, PUT, PATCH, DELETE): restricted to the organizer only.

Note: Object-level permission is checked by DRF only when
``get_object()`` is called (i.e., detail endpoints).
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizerOrReadOnly(BasePermission):
    """
    Allow read access to organizer and participants;
    restrict write access exclusively to the organizer.
    """

    message = "Only the trip organizer can perform this action."

    def has_permission(self, request, view) -> bool:
        # List / create — must be authenticated (IsAuthenticated handles this).
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        # Read permissions: organizer or any participant.
        if request.method in SAFE_METHODS:
            return (
                obj.organizer == request.user
                or obj.participants.filter(pk=request.user.pk).exists()
            )

        # Write permissions: organizer only.
        return obj.organizer == request.user
