from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DestinationViewSet, HotelSearchView

router = DefaultRouter()
router.register(r"destinations", DestinationViewSet, basename="destinations")

urlpatterns = [
    path("hotels/", HotelSearchView.as_view(), name="hotel-search"),
] + router.urls
