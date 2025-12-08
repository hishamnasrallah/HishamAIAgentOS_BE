"""
Views for monitoring app.
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SystemMetric, HealthCheck, AuditLog, AuditConfiguration
from .serializers import (
    SystemMetricSerializer, 
    HealthCheckSerializer, 
    AuditLogSerializer,
    AuditConfigurationSerializer
)


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


class AuditConfigurationViewSet(viewsets.ModelViewSet):
    """Audit configuration viewset."""
    
    queryset = AuditConfiguration.objects.all()
    serializer_class = AuditConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['configuration_type', 'is_active', 'is_default']
    search_fields = ['name', 'description']
    ordering_fields = ['priority', 'name', 'created_at']
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        queryset = AuditConfiguration.objects.all()
        
        # Admins can see all, others see only active ones
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('-priority', 'name')
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a configuration."""
        config = self.get_object()
        config.is_active = True
        config.save()
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a configuration."""
        config = self.get_object()
        config.is_active = False
        config.save()
        return Response({'status': 'deactivated'})
    
    @action(detail=True, methods=['post'])
    def set_as_default(self, request, pk=None):
        """Set configuration as default for its type."""
        config = self.get_object()
        
        # Unset other defaults of the same type
        AuditConfiguration.objects.filter(
            configuration_type=config.configuration_type,
            is_default=True
        ).exclude(id=config.id).update(is_default=False)
        
        config.is_default = True
        config.save()
        return Response({'status': 'set as default'})
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active configurations."""
        configs = AuditConfiguration.objects.filter(is_active=True).order_by('-priority', 'name')
        serializer = self.get_serializer(configs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def defaults(self, request):
        """Get all default configurations."""
        configs = AuditConfiguration.objects.filter(is_default=True).order_by('-priority', 'name')
        serializer = self.get_serializer(configs, many=True)
        return Response(serializer.data)
