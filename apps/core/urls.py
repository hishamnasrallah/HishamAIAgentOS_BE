"""
URL configuration for core app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SystemSettingsViewSet, FeatureFlagViewSet
from .search_views import global_search
from .presence_views import online_users, update_presence, remove_presence
from .secrets_views import (
    store_secret, get_secret, delete_secret, rotate_secret, list_secrets
)
from .api_doc_views import (
    export_postman_collection, generate_python_sdk, generate_javascript_sdk
)

router = DefaultRouter()
router.register(r'settings', SystemSettingsViewSet, basename='systemsettings')
router.register(r'feature-flags', FeatureFlagViewSet, basename='featureflag')

urlpatterns = [
    path('', include(router.urls)),
    # Global search
    path('search/', global_search, name='global_search'),
    # User presence
    path('presence/online/', online_users, name='online_users'),
    path('presence/update/', update_presence, name='update_presence'),
    path('presence/remove/', remove_presence, name='remove_presence'),
    # Secrets management
    path('secrets/', store_secret, name='store_secret'),
    path('secrets/<str:path>/', get_secret, name='get_secret'),
    path('secrets/<str:path>/delete/', delete_secret, name='delete_secret'),
    path('secrets/<str:path>/rotate/', rotate_secret, name='rotate_secret'),
    path('secrets-list/', list_secrets, name='list_secrets'),
    # API Documentation
    path('api-docs/postman/', export_postman_collection, name='export_postman'),
    path('api-docs/python-sdk/', generate_python_sdk, name='generate_python_sdk'),
    path('api-docs/javascript-sdk/', generate_javascript_sdk, name='generate_javascript_sdk'),
]
