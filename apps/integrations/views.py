"""
Views for integrations app.
"""

from rest_framework import viewsets
from .models import AIPlatform, PlatformUsage
from .serializers import AIPlatformSerializer, PlatformUsageSerializer


class AIPlatformViewSet(viewsets.ModelViewSet):
    """AI Platform viewset."""
    
    queryset = AIPlatform.objects.all()
    serializer_class = AIPlatformSerializer
    filterset_fields = ['platform_name', 'status', 'is_default', 'is_healthy']
    search_fields = ['name', 'display_name']
    ordering_fields = ['priority', 'created_at', 'total_requests']


class PlatformUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """Platform usage viewset (read-only)."""
    
    queryset = PlatformUsage.objects.all()
    serializer_class = PlatformUsageSerializer
    filterset_fields = ['platform', 'user', 'success', 'model']
    ordering_fields = ['timestamp', 'cost', 'response_time']
    
    def get_queryset(self):
        return PlatformUsage.objects.select_related('platform', 'user')
