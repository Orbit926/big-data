"""
Migration: replace the initial stub Jam model with the full
Jam + JamMember schema.

Changes vs 0001_initial:
  - Jam.trip: ForeignKey → OneToOneField
  - Jam: add description, is_active, updated_at fields
  - Jam: remove old M2M 'members' field (replaced by JamMember)
  - Add JamMember model (role, status, joined_at, created_at, updated_at)
"""

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jams", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("trips", "0001_trips_organizer_participants"),
    ]

    operations = [
        # 1. Drop old M2M members table (it lives in jams_jam_members).
        migrations.RemoveField(
            model_name="jam",
            name="members",
        ),

        # 2. Remove old FK trip field so we can re-add it as OneToOne.
        migrations.RemoveField(
            model_name="jam",
            name="trip",
        ),

        # 3. Add the OneToOne trip field.
        migrations.AddField(
            model_name="jam",
            name="trip",
            field=models.OneToOneField(
                help_text="The trip this JAM belongs to. One trip → one JAM.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="jam",
                to="trips.trip",
                null=True,  # temporary null to allow the migration to run
            ),
        ),

        # 4. Make trip non-nullable.
        migrations.AlterField(
            model_name="jam",
            name="trip",
            field=models.OneToOneField(
                help_text="The trip this JAM belongs to. One trip → one JAM.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="jam",
                to="trips.trip",
            ),
        ),

        # 5. Add description field.
        migrations.AddField(
            model_name="jam",
            name="description",
            field=models.TextField(blank=True),
        ),

        # 6. Add is_active field.
        migrations.AddField(
            model_name="jam",
            name="is_active",
            field=models.BooleanField(default=True),
        ),

        # 7. Add updated_at field.
        migrations.AddField(
            model_name="jam",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),

        # 8. Update verbose_name on Jam.
        migrations.AlterModelOptions(
            name="jam",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "JAM",
                "verbose_name_plural": "JAMs",
            },
        ),

        # 9. Create JamMember model.
        migrations.CreateModel(
            name="JamMember",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[("admin", "Admin"), ("member", "Member")],
                        default="member",
                        max_length=10,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("invited", "Invited"),
                            ("active", "Active"),
                            ("removed", "Removed"),
                        ],
                        default="active",
                        max_length=10,
                    ),
                ),
                (
                    "joined_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True),
                ),
                (
                    "jam",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="memberships",
                        to="jams.jam",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="jam_memberships",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "JAM Member",
                "verbose_name_plural": "JAM Members",
                "ordering": ["joined_at"],
                "unique_together": {("jam", "user")},
            },
        ),
    ]
