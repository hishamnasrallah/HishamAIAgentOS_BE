"""
URL configuration for monitoring app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SystemMetricViewSet, 
    HealthCheckViewSet, 
    AuditLogViewSet,
    AuditConfigurationViewSet
)
from .analytics_views import AnalyticsViewSet
from .dashboard_views import dashboard_stats, agent_status_list, recent_workflows, system_health
from .admin_views import admin_stats, admin_recent_activity
from .prometheus_metrics import metrics_view

router = DefaultRouter()
router.register(r'metrics', SystemMetricViewSet, basename='systemmetric')
router.register(r'health', HealthCheckViewSet, basename='healthcheck')
router.register(r'audit', AuditLogViewSet, basename='auditlog')
router.register(r'audit-configurations', AuditConfigurationViewSet, basename='auditconfiguration')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    # Dashboard API endpoints
    path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    path('dashboard/agents/', agent_status_list, name='dashboard_agents'),
    path('dashboard/workflows/', recent_workflows, name='dashboard_workflows'),
    path('dashboard/health/', system_health, name='dashboard_health'),
    
    # Admin API endpoints
    path('admin/stats/', admin_stats, name='admin_stats'),
    path('admin/activity/', admin_recent_activity, name='admin_activity'),
    
    # Router URLs
    path('', include(router.urls)),
    
    # Prometheus metrics endpoint
    path('prometheus/metrics/', metrics_view, name='prometheus_metrics'),
]
