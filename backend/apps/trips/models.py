"""
Trip model — core entity representing a travel experience.

A Trip is owned by an organizer (FK → User) and can have many
participants (M2M → User).  Only the organizer can mutate it;
participants (and the organizer) may read it.
"""

from django.conf import settings
from django.db import models


class Trip(models.Model):
    """Represents a shared travel experience."""

    # ── Ownership ──────────────────────────────────────────────────────────
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_trips",
        help_text="The user who created and owns this trip.",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participating_trips",
        blank=True,
        help_text="Users invited to this trip (organizer excluded from this set).",
    )

    # ── Core fields ────────────────────────────────────────────────────────
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # ── Timestamps ─────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Trip"
        verbose_name_plural = "Trips"

    def __str__(self) -> str:  # noqa: D105
        return self.name
