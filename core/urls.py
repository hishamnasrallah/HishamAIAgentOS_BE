"""
HishamOS URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Root redirect to API docs
    # path('', RedirectView.as_view(url='/api/docs/', permanent=False), name='root'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # DRF Browseable API authentication
    path('api-auth/', include('rest_framework.urls')),
    
    # API Documentation (publicly accessible)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),  # Organizations (SaaS multi-tenancy)
    path('api/v1/agents/', include('apps.agents.urls')),
    path('api/v1/commands/', include('apps.commands.urls')),
    path('api/v1/workflows/', include('apps.workflows.urls')),
    path('api/v1/projects/', include('apps.projects.urls')),
    path('api/v1/integrations/', include('apps.integrations.urls')),
    path('api/v1/integrations-external/', include('apps.integrations_external.urls')),
    path('api/v1/results/', include('apps.results.urls')),
    path('api/v1/monitoring/', include('apps.monitoring.urls')),
    path('api/v1/chat/', include('apps.chat.urls')),  # Phase 13-14
    path('api/v1/core/', include('apps.core.urls')),  # System settings and feature flags
    path('api/v1/', include('apps.docs.urls')),  # Documentation viewer
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Customize admin site
admin.site.site_header = "HishamOS Administration"
admin.site.site_title = "HishamOS Admin"
admin.site.index_title = "Welcome to HishamOS Administration"
