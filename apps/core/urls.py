"""
URL configuration for core app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SystemSettingsViewSet, FeatureFlagViewSet

router = DefaultRouter()
router.register(r'settings', SystemSettingsViewSet, basename='systemsettings')
router.register(r'feature-flags', FeatureFlagViewSet, basename='featureflag')

urlpatterns = [
    path('', include(router.urls)),
]

