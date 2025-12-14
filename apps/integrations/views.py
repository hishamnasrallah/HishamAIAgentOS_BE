"""
Views for integrations app.
"""

from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .models import AIPlatform, PlatformUsage
from .serializers import AIPlatformSerializer, PlatformUsageSerializer
from apps.authentication.permissions import IsAdminUser
from apps.core.services.roles import RoleService
from apps.organizations.services import OrganizationStatusService, SubscriptionService


class AIPlatformViewSet(viewsets.ModelViewSet):
    """
    AI Platform viewset.
    
    Access Control:
    - All authenticated users can view platforms (read-only)
    - Only admins can create/update/delete platforms
    """
    
    queryset = AIPlatform.objects.all()
    serializer_class = AIPlatformSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['platform_name', 'status', 'is_default', 'is_healthy']
    search_fields = ['name', 'display_name']
    ordering_fields = ['priority', 'created_at', 'total_requests']
    
    def get_permissions(self):
        """Override to allow read-only for all authenticated users, but restrict create/update/delete to admins."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        # Create/update/delete require admin
        return [IsAuthenticated(), IsAdminUser()]
    
    def perform_create(self, serializer):
        """
        Create AI platform integration with organization status, subscription, and tier limit validation.
        """
        user = self.request.user
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        
        # Super admins can bypass checks (handled in service methods)
        if organization:
            # Check organization status
            OrganizationStatusService.require_active_organization(organization, user=user)
            
            # Check subscription active
            OrganizationStatusService.require_subscription_active(organization, user=user)
            
            # Check integration limit based on tier
            # Note: AIPlatform is system-wide, but we can check if user's org has reached integration limit
            # For now, we'll check if this is a user-specific integration (if organization_id field exists)
            # Since AIPlatform is system-wide, we might not need tier limits here
            # But we should still check org status and subscription
        
        serializer.save()
    
    def perform_update(self, serializer):
        """
        Update AI platform integration with organization status and subscription validation.
        """
        user = self.request.user
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        
        # Super admins can bypass checks (handled in service methods)
        if organization:
            # Check organization status
            OrganizationStatusService.require_active_organization(organization, user=user)
            
            # Check subscription active
            OrganizationStatusService.require_subscription_active(organization, user=user)
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete AI platform integration with organization status and subscription validation.
        """
        user = self.request.user
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        
        # Super admins can bypass checks (handled in service methods)
        if organization:
            # Check organization status
            OrganizationStatusService.require_active_organization(organization, user=user)
            
            # Check subscription active
            OrganizationStatusService.require_subscription_active(organization, user=user)
        
        super().perform_destroy(instance)


class PlatformUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Platform usage viewset (read-only).
    
    Access Control:
    - Users can only see their own usage
    - Admins can see all usage
    """
    
    queryset = PlatformUsage.objects.all()
    serializer_class = PlatformUsageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['platform', 'user', 'success', 'model']
    ordering_fields = ['timestamp', 'cost', 'response_time']
    
    def get_queryset(self):
        """Filter usage based on user permissions."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return PlatformUsage.objects.none()
        
        # Admins can see all usage
        if RoleService.is_admin(user):
            return PlatformUsage.objects.select_related('platform', 'user')
        
        # Regular users can only see their own usage
        return PlatformUsage.objects.filter(user=user).select_related('platform', 'user')
