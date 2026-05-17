"""
URL configuration for the JAMs app.

Mounted in config/urls.py at:
  /api/trips/  → includes apps.trips.urls  (adds nested /{trip_id}/jam/)
  /api/jams/   → includes apps.jams.urls   (standalone JAM + members)

Full route table:

  POST   /api/trips/{trip_id}/jam/                       → TripJamView (create)
  GET    /api/trips/{trip_id}/jam/                       → TripJamView (get jam of trip)

  GET    /api/jams/{jam_id}/                             → JamDetailView
  PATCH  /api/jams/{jam_id}/                             → JamDetailView
  DELETE /api/jams/{jam_id}/                             → JamDetailView

  GET    /api/jams/{jam_id}/members/                     → JamMemberListCreateView
  POST   /api/jams/{jam_id}/members/                     → JamMemberListCreateView
  PATCH  /api/jams/{jam_id}/members/{member_id}/        → JamMemberDetailView
  DELETE /api/jams/{jam_id}/members/{member_id}/        → JamMemberDetailView
"""

from django.urls import path

from .views import (
    JamDetailView,
    JamMemberDetailView,
    JamMemberListCreateView,
)

# Patterns mounted at /api/jams/
urlpatterns = [
    path(
        "<int:jam_id>/",
        JamDetailView.as_view(),
        name="jam-detail",
    ),
    path(
        "<int:jam_id>/members/",
        JamMemberListCreateView.as_view(),
        name="jam-members",
    ),
    path(
        "<int:jam_id>/members/<int:member_id>/",
        JamMemberDetailView.as_view(),
        name="jam-member-detail",
    ),
]
