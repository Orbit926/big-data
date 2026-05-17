"""
Permission helpers for the JAMs domain.

These functions are the single source of truth for JAM access control.
Future modules (itinerary, votes, expenses, catalog) must import from
here rather than querying JamMember directly, to avoid logic drift.

Usage example (in a future itinerary view):

    from apps.jams.services import can_view_jam, is_jam_admin

    if not can_view_jam(request.user, jam):
        raise PermissionDenied
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from .models import Jam


def _active_membership(user, jam):
    """Return the active JamMember record for user in jam, or None."""
    from .models import JamMember  # local import avoids circular deps

    return (
        JamMember.objects
        .filter(jam=jam, user=user, status=JamMember.Status.ACTIVE)
        .first()
    )


# ── Core predicates ────────────────────────────────────────────────────────────


def get_user_jam_role(user, jam) -> str | None:
    """
    Return the role string ('admin' | 'member') of an *active* member,
    or None if the user has no active membership.
    """
    membership = _active_membership(user, jam)
    return membership.role if membership else None


def is_jam_admin(user, jam) -> bool:
    """True if the user is an *active* admin of the JAM."""
    return get_user_jam_role(user, jam) == "admin"


def is_jam_member(user, jam) -> bool:
    """
    True if the user has an *active* membership (admin OR member).
    Removed / invited members return False.
    """
    return _active_membership(user, jam) is not None


def can_view_jam(user, jam) -> bool:
    """
    A user can view a JAM if they have an active membership.

    Extension point: trip organizers could also be granted access here
    once the policy is clarified.
    """
    return is_jam_member(user, jam)


def can_manage_jam(user, jam) -> bool:
    """
    A user can edit/archive/delete a JAM iff they are an active admin.
    """
    return is_jam_admin(user, jam)


def can_manage_jam_members(user, jam) -> bool:
    """
    A user can add, change role, or remove members iff they are an active admin.
    """
    return is_jam_admin(user, jam)


# ── Trip-access guard (isolation layer) ───────────────────────────────────────


def user_has_trip_access(user, trip) -> bool:
    """
    Return True if the user has access to the underlying Trip.

    Currently: organizer OR participant.
    If Trip membership evolves, update only this function and all downstream
    JAM permission checks remain correct.

    # TODO: when trip roles become more complex, extend this helper.
    """
    return (
        trip.organizer == user
        or trip.participants.filter(pk=user.pk).exists()
    )
