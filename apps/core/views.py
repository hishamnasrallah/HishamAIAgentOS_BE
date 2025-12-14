"""
Core API views for system-wide functionality.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from apps.core.services.roles import RoleService
from apps.projects.models import Project
from apps.organizations.models import Organization


class RoleViewSet(viewsets.ViewSet):
    """
    API endpoints for role management.
    Provides information about system roles and role validation.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        description="Get all system roles with their information",
        responses={200: {
            'type': 'object',
            'properties': {
                'roles': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'value': {'type': 'string'},
                            'label': {'type': 'string'},
                            'description': {'type': 'string'},
                            'level': {'type': 'integer'},
                            'is_system': {'type': 'boolean'},
                        }
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['get'], url_path='system')
    def system_roles(self, request):
        """Get all system roles."""
        roles = RoleService.get_roles_with_info()
        return Response({'roles': roles})
    
    @extend_schema(
        description="Get all available roles for a project (system + custom)",
        responses={200: {
            'type': 'object',
            'properties': {
                'roles': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'value': {'type': 'string'},
                            'label': {'type': 'string'},
                            'description': {'type': 'string'},
                            'level': {'type': 'integer'},
                            'is_system': {'type': 'boolean'},
                        }
                    }
                }
            }
        }}
    )
    @action(detail=False, methods=['get'], url_path='project/(?P<project_id>[^/.]+)')
    def project_roles(self, request, project_id=None):
        """Get all available roles for a specific project (system + org + custom)."""
        try:
            project = Project.objects.select_related('organization').get(pk=project_id)
            # Verify user has access to this project's organization
            if not RoleService.is_super_admin(request.user):
                user_orgs = RoleService.get_user_organizations(request.user)
                if project.organization not in user_orgs:
                    return Response(
                        {'error': 'You do not have access to this project.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            roles = RoleService.get_roles_with_info(project, project.organization)
            return Response({'roles': roles})
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        description="Get user's roles in a project",
        responses={200: {
            'type': 'object',
            'properties': {
                'roles': {
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                'is_admin': {'type': 'boolean'},
                'is_owner': {'type': 'boolean'},
            }
        }}
    )
    @action(detail=False, methods=['get'], url_path='user/(?P<project_id>[^/.]+)')
    def user_roles(self, request, project_id=None):
        """Get current user's roles in a specific project."""
        try:
            project = Project.objects.select_related('organization').get(pk=project_id)
            # Verify user has access to this project's organization
            if not RoleService.is_super_admin(request.user):
                user_orgs = RoleService.get_user_organizations(request.user)
                if project.organization not in user_orgs:
                    return Response(
                        {'error': 'You do not have access to this project.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            user = request.user
            roles = RoleService.get_user_roles(user, project, project.organization)
            is_super_admin = RoleService.is_super_admin(user)
            is_org_admin = RoleService.is_org_admin(user, project.organization)
            is_owner = project.owner == user
            
            return Response({
                'roles': roles,
                'is_super_admin': is_super_admin,
                'is_org_admin': is_org_admin,
                'is_admin': is_super_admin or is_org_admin,  # Backward compatibility
                'is_owner': is_owner,
            })
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        description="Validate if a role is valid",
        responses={200: {
            'type': 'object',
            'properties': {
                'valid': {'type': 'boolean'},
                'role': {'type': 'string'},
            }
        }}
    )
    @action(detail=False, methods=['post'], url_path='validate')
    def validate_role(self, request):
        """Validate if a role is valid (optionally for a project or organization)."""
        role = request.data.get('role')
        project_id = request.data.get('project_id')
        organization_id = request.data.get('organization_id')
        
        if not role:
            return Response(
                {'error': 'Role is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = None
        organization = None
        
        if project_id:
            try:
                project = Project.objects.select_related('organization').get(pk=project_id)
                organization = project.organization
            except Project.DoesNotExist:
                return Response(
                    {'error': 'Project not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif organization_id:
            try:
                organization = Organization.objects.get(pk=organization_id)
            except Organization.DoesNotExist:
                return Response(
                    {'error': 'Organization not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        is_valid = RoleService.is_valid_role(role, project, organization)
        return Response({
            'valid': is_valid,
            'role': role,
        })
