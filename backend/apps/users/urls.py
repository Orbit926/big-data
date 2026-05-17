"""
URL configuration for the Users app.

Routes
------
GET  /api/users/me/      → ProfileView  (own profile: read + patch)
PATCH /api/users/me/     → ProfileView
GET  /api/users/<id>/    → UserDetailView (public profile, read-only)
"""

from django.urls import path

from .views import ProfileView, UserDetailView

urlpatterns = [
    path("me/", ProfileView.as_view(), name="user-profile"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
