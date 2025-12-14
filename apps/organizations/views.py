"""
Views for organizations app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema
from django.db import models
from django.db.models import Q
from django.http import Http404 as DjangoHttp404

from .models import Organization, OrganizationMember
from .serializers import (
    OrganizationSerializer,
    OrganizationCreateSerializer,
    OrganizationMemberSerializer,
    OrganizationMemberAddSerializer,
    OrganizationMemberUpdateSerializer,
)
from apps.core.services.roles import RoleService
from apps.monitoring.mixins import AuditLoggingMixin
from apps.organizations.services import OrganizationStatusService, SubscriptionService


class OrganizationViewSet(AuditLoggingMixin, viewsets.ModelViewSet):
    """
    API endpoints for managing organizations.
    
    - Super admins: Can access all organizations
    - Org admins: Can access and manage their own organization
    - Regular users: Can only view their own organization
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizationSerializer
    
    def get_queryset(self):
        """Filter organizations based on user permissions."""
        user = self.request.user
        
        # Super admins see all organizations
        if RoleService.is_super_admin(user):
            return Organization.objects.all().select_related('owner', 'created_by').prefetch_related('members', 'projects')
        
        # Get organizations user is a member of (via OrganizationMember)
        from apps.organizations.models import OrganizationMember
        member_org_ids = OrganizationMember.objects.filter(user=user).values_list('organization_id', flat=True)
        
        # Get organizations where user is the owner
        owner_org_ids = Organization.objects.filter(owner=user).values_list('id', flat=True)
        
        # Get organizations where user is org_admin (via OrganizationMember with org_admin role)
        org_admin_org_ids = OrganizationMember.objects.filter(
            user=user, 
            role='org_admin'
        ).values_list('organization_id', flat=True)
        
        # Also include user's primary organization if set
        org_ids = list(member_org_ids) + list(owner_org_ids) + list(org_admin_org_ids)
        if user.organization_id:
            org_ids.append(user.organization_id)
        
        # Remove duplicates
        org_ids = list(set(org_ids))
        
        if not org_ids:
            return Organization.objects.none()
        
        return Organization.objects.filter(id__in=org_ids).select_related('owner', 'created_by').prefetch_related('members', 'projects')
    
    def get_serializer_class(self):
        """Use create serializer for creation."""
        if self.action == 'create':
            return OrganizationCreateSerializer
        return OrganizationSerializer
    
    def perform_create(self, serializer):
        """Create organization and set creator as owner."""
        # Owner is set in serializer.create()
        serializer.save()
    
    def perform_update(self, serializer):
        """Update organization - only org admin or super admin can update."""
        organization = self.get_object()
        user = self.request.user
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only organization administrators can update organization settings.")
        
        # Org admins cannot update when organization is suspended (only super_admin can reactivate)
        if not RoleService.is_super_admin(user) and organization:
            # Allow update if org is active or trial, but block if suspended or cancelled
            if organization.status in ['suspended', 'cancelled']:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(f"Cannot update organization. Organization is {organization.get_status_display()}. Please contact support.")
            
            # Check subscription active
            if not organization.is_subscription_active():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Cannot update organization. Organization subscription has expired.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete organization - only super admin can delete."""
        user = self.request.user
        
        if not RoleService.is_super_admin(user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only super administrators can delete organizations.")
        
        instance.delete()
    
    def get_object(self):
        """Override to ensure org_admin can access their organization even if not in queryset."""
        # First try to get from queryset (normal flow)
        try:
            obj = super().get_object()
            return obj
        except (NotFound, DjangoHttp404, Organization.DoesNotExist) as e:
            # DRF raises NotFound when object is not in queryset
            # Django raises Http404, and models raise DoesNotExist
            # Check if user is org_admin for this organization
            pk = self.kwargs.get('pk')
            if not pk:
                raise NotFound("Organization not found.")
            
            try:
                organization = Organization.objects.get(pk=pk)
            except Organization.DoesNotExist:
                raise NotFound("Organization not found.")
            
            user = self.request.user
            
            # If user is super admin, they can access any organization
            if RoleService.is_super_admin(user):
                return organization
            
            # If user is org_admin for this organization, allow access
            if RoleService.is_org_admin(user, organization):
                return organization
            
            # Otherwise, raise 404
            raise NotFound("You do not have access to this organization.")
    
    @action(detail=True, methods=['get'], url_path='members')
    def members(self, request, pk=None):
        """Get all members of the organization."""
        organization = self.get_object()
        user = request.user
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can view members.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        members = OrganizationMember.objects.filter(organization=organization).select_related('user', 'invited_by')
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Add a member to the organization",
        request=OrganizationMemberAddSerializer,
        responses={201: OrganizationMemberSerializer}
    )
    @action(detail=True, methods=['post'], url_path='members/add')
    def add_member(self, request, pk=None):
        """Add a user to the organization."""
        organization = self.get_object()
        user = request.user
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can add members.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate organization status and subscription (super admins bypass in service)
        try:
            OrganizationStatusService.require_active_organization(organization, user=user)
            OrganizationStatusService.require_subscription_active(organization, user=user)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate user limit (super admins can bypass)
        if not RoleService.is_super_admin(user) and not organization.can_add_user():
            current_count = organization.get_member_count()
            return Response(
                {'error': f'Cannot add member. Organization has reached the maximum number of users ({organization.max_users}). Current: {current_count}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OrganizationMemberAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        role = serializer.validated_data.get('role', 'org_member')
        
        # Check if user is already a member
        if OrganizationMember.objects.filter(organization=organization, user_id=user_id).exists():
            return Response(
                {'error': 'User is already a member of this organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create member
        member = OrganizationMember.objects.create(
            organization=organization,
            user_id=user_id,
            role=role,
            invited_by=user
        )
        
        # Update user's primary organization if not set
        from apps.authentication.models import User
        try:
            member_user = User.objects.get(id=user_id)
            if not member_user.organization:
                member_user.organization = organization
                member_user.save(update_fields=['organization'])
        except User.DoesNotExist:
            pass
        
        return Response(OrganizationMemberSerializer(member).data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        description="Remove a member from the organization",
        request={'type': 'object', 'properties': {'user_id': {'type': 'string'}}},
        responses={204: None}
    )
    @action(detail=True, methods=['post'], url_path='members/remove')
    def remove_member(self, request, pk=None):
        """Remove a user from the organization."""
        organization = self.get_object()
        user = request.user
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can remove members.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate organization status and subscription (super admins bypass in service)
        if organization:
            try:
                OrganizationStatusService.require_active_organization(organization, user=user)
                OrganizationStatusService.require_subscription_active(organization, user=user)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            member = OrganizationMember.objects.get(organization=organization, user_id=user_id)
            # Don't allow removing the organization owner
            if organization.owner_id == user_id:
                return Response(
                    {'error': 'Cannot remove the organization owner.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except OrganizationMember.DoesNotExist:
            return Response(
                {'error': 'User is not a member of this organization.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        description="Update a member's role in the organization",
        request=OrganizationMemberUpdateSerializer,
        responses={200: OrganizationMemberSerializer}
    )
    @action(detail=True, methods=['patch'], url_path='members/(?P<member_id>[^/.]+)/update-role')
    def update_member_role(self, request, pk=None, member_id=None):
        """Update a member's role in the organization."""
        organization = self.get_object()
        user = request.user
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return Response(
                {'error': 'Only organization administrators can update member roles.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate organization status and subscription (super admins bypass in service)
        if organization:
            try:
                OrganizationStatusService.require_active_organization(organization, user=user)
                OrganizationStatusService.require_subscription_active(organization, user=user)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            member = OrganizationMember.objects.get(organization=organization, id=member_id)
        except OrganizationMember.DoesNotExist:
            return Response(
                {'error': 'Member not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = OrganizationMemberUpdateSerializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(OrganizationMemberSerializer(member).data)


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing organization members.
    """
    serializer_class = OrganizationMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter members based on user permissions."""
        organization_id = self.kwargs.get('organization_pk')
        user = self.request.user
        
        if not organization_id:
            return OrganizationMember.objects.none()
        
        try:
            organization = Organization.objects.get(pk=organization_id)
        except Organization.DoesNotExist:
            return OrganizationMember.objects.none()
        
        # Check permissions
        if not RoleService.is_super_admin(user) and not RoleService.is_org_admin(user, organization):
            return OrganizationMember.objects.none()
        
        return OrganizationMember.objects.filter(organization=organization).select_related('user', 'organization', 'invited_by')

