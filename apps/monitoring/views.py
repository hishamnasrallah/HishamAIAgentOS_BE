"""
Views for monitoring app.
"""

from rest_framework import viewsets
from .models import SystemMetric, HealthCheck, AuditLog
from .serializers import SystemMetricSerializer, HealthCheckSerializer, AuditLogSerializer


class SystemMetricViewSet(viewsets.ReadOnlyModelViewSet):
    """System metric viewset (read-only)."""
    
    queryset = SystemMetric.objects.all()
    serializer_class = SystemMetricSerializer
    filterset_fields = ['metric_type']
    ordering_fields = ['timestamp']


class HealthCheckViewSet(viewsets.ReadOnlyModelViewSet):
    """Health check viewset (read-only)."""
    
    queryset = HealthCheck.objects.all()
    serializer_class = HealthCheckSerializer
    filterset_fields = ['component', 'status']
    ordering_fields = ['timestamp']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Audit log viewset (read-only)."""
    
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    filterset_fields = ['user', 'action', 'resource_type']
    search_fields = ['description', 'resource_type']
    ordering_fields = ['timestamp']
    
    def get_queryset(self):
        return AuditLog.objects.select_related('user')
