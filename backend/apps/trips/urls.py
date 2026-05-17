"""
URL configuration for the Trips app.

Registered routes (mounted at /api/trips/ in config/urls.py):
  GET    /api/trips/        → list
  POST   /api/trips/        → create
  GET    /api/trips/<id>/   → retrieve
  PUT    /api/trips/<id>/   → full update
  PATCH  /api/trips/<id>/   → partial update
  DELETE /api/trips/<id>/   → destroy
"""

from rest_framework.routers import DefaultRouter

from .views import TripViewSet

router = DefaultRouter()
router.register(r"", TripViewSet, basename="trips")

urlpatterns = router.urls
