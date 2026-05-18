"""
Django Admin registration for the JAMs app.

Provides management of Jam and JamMember from the Django Admin panel.
"""

from django.contrib import admin

from .models import Jam, JamMember


class JamMemberInline(admin.TabularInline):
    """Show JamMember records inline inside the Jam admin page."""

    model = JamMember
    extra = 0
    fields = ["user", "role", "status", "joined_at"]
    readonly_fields = ["joined_at"]


@admin.register(Jam)
class JamAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "trip", "created_by", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "trip__name", "created_by__username"]
    readonly_fields = ["created_at", "updated_at", "created_by"]
    inlines = [JamMemberInline]

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "trip",
                    "name",
                    "description",
                    "is_active",
                ],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_by", "created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(JamMember)
class JamMemberAdmin(admin.ModelAdmin):
    list_display = ["id", "jam", "user", "role", "status", "joined_at"]
    list_filter = ["role", "status"]
    search_fields = ["jam__name", "user__username"]
    readonly_fields = ["joined_at", "created_at", "updated_at"]
