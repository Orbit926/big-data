"""
URL configuration for the Trips app.

Registered routes (mounted at /api/trips/ in config/urls.py):
  GET    /api/trips/               → list
  POST   /api/trips/               → create
  GET    /api/trips/<id>/          → retrieve
  PUT    /api/trips/<id>/          → full update
  PATCH  /api/trips/<id>/          → partial update
  DELETE /api/trips/<id>/          → destroy

  ── Nested JAM (one JAM per trip) ──────────────────────────────────────────
  GET    /api/trips/<trip_id>/jam/ → get the JAM of this trip
  POST   /api/trips/<trip_id>/jam/ → create the JAM for this trip
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.jams.views import TripJamView

from .views import TripViewSet

router = DefaultRouter()
router.register(r"", TripViewSet, basename="trips")

urlpatterns = router.urls + [
    path("<int:trip_id>/jam/", TripJamView.as_view(), name="trip-jam"),
]
