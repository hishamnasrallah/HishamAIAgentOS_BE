"""
URL configuration for integrations app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIPlatformViewSet, PlatformUsageViewSet

router = DefaultRouter()
router.register(r'platforms', AIPlatformViewSet, basename='aiplatform')
router.register(r'usage', PlatformUsageViewSet, basename='platformusage')

urlpatterns = [
    path('', include(router.urls)),
]
