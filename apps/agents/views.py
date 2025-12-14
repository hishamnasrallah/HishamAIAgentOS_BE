"""
Views for agents app.
"""

from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.core.cache import cache
from django.conf import settings
from asgiref.sync import async_to_sync
import logging
from .models import Agent, AgentExecution
from .serializers import (
    AgentSerializer, AgentListSerializer,
    AgentExecutionSerializer, AgentExecutionCreateSerializer
)
from apps.core.services.roles import RoleService
from apps.organizations.services import OrganizationStatusService, SubscriptionService

logger = logging.getLogger(__name__)


class AgentViewSet(viewsets.ModelViewSet):
    """
    Agent viewset.
    
    Access Control:
    - All authenticated users can view agents (read-only for non-admins)
    - Only admins can create/update/delete agents
    """
    
    serializer_class = AgentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'preferred_platform']
    search_fields = ['name', 'agent_id', 'description']
    ordering_fields = ['created_at', 'name', 'total_invocations', 'success_rate']
    
    def get_queryset(self):
        """All authenticated users can view agents."""
        return Agent.objects.all().only(
            'id', 'agent_id', 'name', 'description', 'status',
            'preferred_platform', 'capabilities', 'total_invocations',
            'success_rate', 'created_at'
        )
    
    def list(self, request, *args, **kwargs):
        """List agents with caching."""
        cache_key = 'agents_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, settings.CACHE_TIMEOUT_MEDIUM)
            return response
        
        return Response(cached_data)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AgentListSerializer
        return AgentSerializer
    
    def get_permissions(self):
        """Override to allow read-only for non-admins."""
        if self.action in ['list', 'retrieve', 'execute']:
            return [permissions.IsAuthenticated()]
        # Create/update/delete require admin
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
    
    def perform_create(self, serializer):
        """
        Create agent with organization status and subscription validation.
        Also check if tier allows custom agent creation.
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
            
            # Check if tier allows custom agent creation (Professional+ only)
            SubscriptionService.check_tier_feature(organization, 'allows_custom_agents', user=user)
        
        serializer.save(created_by=user)
    
    def perform_update(self, serializer):
        """
        Update agent with organization status and subscription validation.
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
        
        serializer.save(updated_by=user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """
        Execute an agent with a prompt.
        
        Request body:
        {
            "prompt": "string",
            "context": {} (optional)
        }
        """
        from .services.execution_engine import ExecutionEngine
        
        agent = self.get_object()
        prompt = request.data.get('prompt', '')
        context = request.data.get('context', {})
        
        if not prompt:
            return Response(
                {'error': 'Prompt is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user's organization and validate
        user = request.user
        organization = RoleService.get_user_organization(user)
        
        # Super admins can bypass checks (but we still track usage if they have an org)
        if not RoleService.is_super_admin(user) and organization:
            try:
                # Check organization status
                OrganizationStatusService.require_active_organization(organization, user=user)
                
                # Check subscription active
                OrganizationStatusService.require_subscription_active(organization, user=user)
                
                # Check tier-based usage limit
                SubscriptionService.check_usage_limit(organization, 'agent_executions', user=user)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Execute agent
        execution_engine = ExecutionEngine()
        
        try:
            # Use async_to_sync to properly handle async code in sync view
            # In ASGI context, this will create a new event loop in a thread
            async def run_execution():
                return await execution_engine.execute_agent(
                    agent=agent,
                    input_data={'prompt': prompt},
                    user=request.user,
                    context=context or {}
                )
            
            # async_to_sync handles event loop creation automatically
            # It will create a new loop if one doesn't exist or if we're in ASGI
            result = async_to_sync(run_execution)()
            
            # Increment usage count after successful execution (only if organization exists)
            if organization:
                try:
                    SubscriptionService.increment_usage(organization, 'agent_executions')
                except Exception as e:
                    logger.warning(f"Failed to increment usage count: {e}")
            
            # AgentResult is a dataclass with: success, output, error, tokens_used, cost, execution_time, etc.
            return Response({
                'success': result.success,
                'output': result.output or '',
                'response': result.output or '',
                'execution_time': (result.execution_time or 0) * 1000,  # Convert to ms
                'cost': float(result.cost or 0),
                'token_usage': {
                    'tokens_used': result.tokens_used or 0
                },
                'agent_used': agent.name
            })
        except Exception as e:
            import traceback
            logger.error(f"Agent execution error: {str(e)}\n{traceback.format_exc()}")
            return Response({
                'success': False,
                'error': str(e),
                'output': '',
                'response': '',
                'execution_time': 0,
                'cost': 0,
                'token_usage': {'tokens_used': 0},
                'agent_used': agent.name
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AgentExecutionViewSet(viewsets.ModelViewSet):
    """
    Agent execution viewset.
    
    Access Control:
    - Users can only see their own executions (admins see all)
    - Users can create executions
    - Only admins can update/delete executions
    """
    
    serializer_class = AgentExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['agent', 'user', 'status', 'platform_used']
    search_fields = ['agent__name']
    ordering_fields = ['created_at', 'execution_time', 'cost']
    
    def get_queryset(self):
        """
        Filter executions to only show those created by the current user.
        Admins can see all executions.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return AgentExecution.objects.none()
        
        # Admins can see all executions
        if RoleService.is_admin(user):
            return AgentExecution.objects.select_related('agent', 'user').all()
        
        # Regular users can only see their own executions
        return AgentExecution.objects.filter(user=user).select_related('agent', 'user')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AgentExecutionCreateSerializer
        return AgentExecutionSerializer
    
    def perform_create(self, serializer):
        """
        Set the current user as the execution creator.
        Also validate organization status, subscription, and tier limits.
        """
        user = self.request.user
        
        # Get user's organization
        from apps.core.services.roles import RoleService
        organization = RoleService.get_user_organization(user)
        
        # Super admins can bypass checks (but we still track usage if they have an org)
        if not RoleService.is_super_admin(user) and organization:
            # Check organization status
            OrganizationStatusService.require_active_organization(organization)
            
            # Check subscription active
            OrganizationStatusService.require_subscription_active(organization)
            
            # Check tier-based usage limit
            SubscriptionService.check_usage_limit(organization, 'agent_executions')
        
        # Save execution
        execution = serializer.save(user=user)
        
        # Increment usage count (only if organization exists)
        if organization:
            try:
                SubscriptionService.increment_usage(organization, 'agent_executions')
            except Exception as e:
                logger.warning(f"Failed to increment usage count: {e}")
        
        return execution
    
    def get_permissions(self):
        """Override to allow create for all authenticated users, but restrict update/delete to admins."""
        if self.action in ['list', 'retrieve', 'create']:
            return [permissions.IsAuthenticated()]
        # Update/delete require admin
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
