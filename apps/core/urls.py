"""
URL configuration for core app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.core.views import RoleViewSet
from apps.core.presence_views import online_users, update_presence, remove_presence

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')

urlpatterns = [
    path('', include(router.urls)),
    # Presence endpoints
    path('presence/online/', online_users, name='presence-online'),
    path('presence/update/', update_presence, name='presence-update'),
    path('presence/remove/', remove_presence, name='presence-remove'),
]
