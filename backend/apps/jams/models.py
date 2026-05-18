"""
Jams models — collaborative space for a Trip.

Jam
───
  OneToOne with Trip; each Trip has at most one JAM.
  The creator is automatically added as an active admin via a post_save signal
  (see bottom of file).

JamMember
─────────
  Tracks membership, role (admin | member) and status (invited | active | removed).
  Uniqueness constraint prevents duplicate memberships per JAM.

Future modules (itinerary, votes, expenses, catalog) must import helpers from
apps.jams.services to validate permissions rather than query JamMember directly.
"""

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Jam(models.Model):
    """Collaborative space attached to exactly one Trip."""

    # ── Relationship ───────────────────────────────────────────────────────
    trip = models.OneToOneField(
        "trips.Trip",
        on_delete=models.CASCADE,
        related_name="jam",
        help_text="The trip this JAM belongs to. One trip → one JAM.",
    )

    # ── Core fields ────────────────────────────────────────────────────────
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # ── Ownership (set from request.user, never from frontend payload) ─────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_jams",
        help_text="User who created this JAM.",
    )

    # ── Status ─────────────────────────────────────────────────────────────
    is_active = models.BooleanField(default=True)

    # ── Timestamps ─────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "JAM"
        verbose_name_plural = "JAMs"

    def __str__(self) -> str:  # noqa: D105
        return f"{self.name} (trip={self.trip_id})"


class JamMember(models.Model):
    """Membership record linking a User to a JAM with a role and status."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        ACTIVE = "active", "Active"
        REMOVED = "removed", "Removed"

    # ── Relationships ──────────────────────────────────────────────────────
    jam = models.ForeignKey(
        Jam,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jam_memberships",
    )

    # ── Role & status ──────────────────────────────────────────────────────
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    # ── Timestamps ─────────────────────────────────────────────────────────
    joined_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("jam", "user")]
        ordering = ["joined_at"]
        verbose_name = "JAM Member"
        verbose_name_plural = "JAM Members"

    def __str__(self) -> str:  # noqa: D105
        return f"{self.user} — {self.role} in {self.jam}"


# ── Signal: auto-add creator as admin ─────────────────────────────────────────

@receiver(post_save, sender=Jam)
def add_creator_as_admin(sender, instance, created, **kwargs):
    """
    When a new JAM is created, automatically create a JamMember record
    for the creator with role=admin and status=active.

    This fires only on initial creation (``created=True``) and is idempotent
    thanks to get_or_create — safe to call even if the record already exists.
    """
    if created:
        JamMember.objects.get_or_create(
            jam=instance,
            user=instance.created_by,
            defaults={
                "role": JamMember.Role.ADMIN,
                "status": JamMember.Status.ACTIVE,
            },
        )
