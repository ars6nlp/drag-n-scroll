"""
URL configuration for core app
"""
from django.urls import path
from .views import UserProfileView, UserDetailView, UserByIdView, health_check, run_migrations, debug_auth

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('by-id/<int:user_id>/', UserByIdView.as_view(), name='user-by-id'),
    path('debug/auth/', debug_auth, name='debug-auth'),
]

# Health check endpoint (no auth required)
# This is included in the main urls.py, not in this urlpatterns
