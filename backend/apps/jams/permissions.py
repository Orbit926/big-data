"""
DRF permission classes for the JAMs app.

These are thin wrappers around the helpers in apps.jams.services so that
views stay clean and the actual logic stays in one place.
"""

from rest_framework.permissions import BasePermission

from .services import can_manage_jam, can_manage_jam_members, can_view_jam


class IsJamAdmin(BasePermission):
    """Allow access only to active JAM admins."""

    message = "Only JAM admins can perform this action."

    def has_object_permission(self, request, view, obj):
        # obj can be Jam or JamMember — derive the jam in either case.
        jam = obj if hasattr(obj, "memberships") else obj.jam
        return can_manage_jam(request.user, jam)


class IsJamMemberReadOnly(BasePermission):
    """
    Allow read (SAFE_METHODS) to any active JAM member;
    write operations require admin status.
    """

    message = "You must be an active JAM member to access this resource."

    def has_object_permission(self, request, view, obj):
        from rest_framework.permissions import SAFE_METHODS

        jam = obj if hasattr(obj, "memberships") else obj.jam

        if request.method in SAFE_METHODS:
            return can_view_jam(request.user, jam)
        return can_manage_jam(request.user, jam)
