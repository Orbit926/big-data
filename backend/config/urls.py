from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({"status": "ok", "service": "move-backend"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/auth/", include("apps.authentication.urls", namespace="authentication")),
    path("api/users/", include("apps.users.urls")),
    path("api/trips/", include("apps.trips.urls")),
    path("api/jams/", include("apps.jams.urls")),
    path("api/expenses/", include("apps.expenses.urls")),
    path("api/search/", include("apps.search_engine.urls")),
]
