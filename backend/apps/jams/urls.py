from rest_framework.routers import DefaultRouter
from .views import JamViewSet

router = DefaultRouter()
router.register(r"", JamViewSet, basename="jams")

urlpatterns = router.urls
