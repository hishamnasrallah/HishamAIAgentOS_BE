"""
URL configuration for commands app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommandCategoryViewSet, CommandTemplateViewSet

router = DefaultRouter()
router.register(r'categories', CommandCategoryViewSet, basename='commandcategory')
router.register(r'templates', CommandTemplateViewSet, basename='commandtemplate')

urlpatterns = [
    path('', include(router.urls)),
]
