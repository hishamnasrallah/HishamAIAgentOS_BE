"""
URL configuration for results app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResultViewSet, ResultFeedbackViewSet

router = DefaultRouter()
router.register(r'results', ResultViewSet, basename='result')
router.register(r'feedback', ResultFeedbackViewSet, basename='resultfeedback')

urlpatterns = [
    path('', include(router.urls)),
]
