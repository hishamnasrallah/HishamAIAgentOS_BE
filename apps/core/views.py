"""
Views for core app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import SystemSettings, FeatureFlag
from .serializers import SystemSettingsSerializer, FeatureFlagSerializer

User = get_user_model()


class SystemSettingsViewSet(viewsets.ModelViewSet):
    """System settings viewset (admin only)."""
    
    queryset = SystemSettings.objects.all()
    serializer_class = SystemSettingsSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'is_public']
    search_fields = ['key', 'description']
    ordering_fields = ['category', 'key', 'updated_at']
    
    def get_queryset(self):
        """Filter based on is_public and user role."""
        user = self.request.user
        if user.role == 'admin':
            return SystemSettings.objects.all()
        # Non-admins can only see public settings
        return SystemSettings.objects.filter(is_public=True)
    
    def get_permissions(self):
        """Override to restrict create/update/delete to admins."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        # Create/update/delete require admin
        from rest_framework.permissions import IsAdminUser
        return [IsAuthenticated(), IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get settings grouped by category."""
        queryset = self.get_queryset()
        categories = {}
        for setting in queryset:
            if setting.category not in categories:
                categories[setting.category] = []
            serializer = self.get_serializer(setting)
            categories[setting.category].append(serializer.data)
        return Response(categories)
    
    @action(detail=True, methods=['post'])
    def reset_to_default(self, request, pk=None):
        """Reset setting to default value (admin only)."""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can reset settings.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        setting = self.get_object()
        # Default values would be defined elsewhere or in model
        # For now, just return current value
        return Response({
            'message': 'Reset functionality to be implemented',
            'current_value': setting.value
        })


class FeatureFlagViewSet(viewsets.ModelViewSet):
    """Feature flags viewset (admin only)."""
    
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_enabled']
    search_fields = ['key', 'name', 'description']
    ordering_fields = ['key', 'is_enabled', 'updated_at']
    
    def get_queryset(self):
        """All authenticated users can view feature flags."""
        return FeatureFlag.objects.all()
    
    def get_permissions(self):
        """Override to restrict create/update/delete to admins."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        # Create/update/delete require admin
        from rest_framework.permissions import IsAdminUser
        return [IsAuthenticated(), IsAdminUser()]
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle feature flag (admin only)."""
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can toggle feature flags.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        feature_flag = self.get_object()
        feature_flag.is_enabled = not feature_flag.is_enabled
        feature_flag.updated_by = request.user
        feature_flag.save()
        
        serializer = self.get_serializer(feature_flag)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active feature flags."""
        queryset = FeatureFlag.objects.filter(is_enabled=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

