"""
Views for commands app.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from asgiref.sync import async_to_sync
from django.core.cache import cache
from django.conf import settings
import asyncio
import logging

from .models import CommandCategory, CommandTemplate
from .serializers import (
    CommandCategorySerializer, CommandTemplateSerializer,
    CommandTemplateListSerializer, CommandExecutionRequestSerializer,
    CommandExecutionResponseSerializer, CommandPreviewRequestSerializer,
    CommandPreviewResponseSerializer
)
from .services import command_executor
from .services.template_renderer import TemplateRenderer
from .services.parameter_validator import ParameterValidator
from apps.agents.models import Agent
from apps.authentication.permissions import IsAdminUser
from apps.core.services.roles import RoleService
from apps.organizations.services import OrganizationStatusService, SubscriptionService

# Instantiate services
template_renderer = TemplateRenderer()
parameter_validator = ParameterValidator()

# Logger
logger = logging.getLogger(__name__)


class CommandCategoryViewSet(viewsets.ModelViewSet):
    """
    Command category viewset.
    
    Access Control:
    - All authenticated users can view categories (read-only)
    - Only admins can create/update/delete categories
    """
    
    queryset = CommandCategory.objects.all()
    serializer_class = CommandCategorySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    
    def get_permissions(self):
        """Override to allow read-only for all authenticated users, but restrict create/update/delete to admins."""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        # Create/update/delete require admin
        return [IsAuthenticated(), IsAdminUser()]
    
    def list(self, request, *args, **kwargs):
        """List categories with caching."""
        cache_key = 'command_categories_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, settings.CACHE_TIMEOUT_MEDIUM)
            return response
        
        return Response(cached_data)


class CommandTemplateViewSet(viewsets.ModelViewSet):
    """
    Command template viewset with execute and preview actions.
    
    Access Control:
    - All authenticated users can view and execute commands
    - Only admins can create/update/delete command templates
    """
    
    queryset = CommandTemplate.objects.all()
    serializer_class = CommandTemplateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['created_at', 'usage_count', 'name', 'success_rate', 'estimated_cost']
    # Enable pagination for better performance
    # pagination_class = None  # Disable pagination - return all commands at once
    
    def get_permissions(self):
        """Override to allow read/execute for all authenticated users, but restrict create/update/delete to admins."""
        if self.action in ['list', 'retrieve', 'execute', 'preview']:
            return [IsAuthenticated()]
        # Create/update/delete require admin
        return [IsAuthenticated(), IsAdminUser()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CommandTemplateListSerializer
        elif self.action == 'execute':
            return CommandExecutionRequestSerializer
        elif self.action == 'preview':
            return CommandPreviewRequestSerializer
        return CommandTemplateSerializer
    
    def get_queryset(self):
        """Optimized queryset with select_related and prefetch_related."""
        return CommandTemplate.objects.select_related(
            'category', 'recommended_agent'
        ).only(
            'id', 'name', 'slug', 'description', 'category', 'recommended_agent',
            'is_active', 'usage_count', 'success_rate', 'estimated_cost',
            'tags', 'version'
        )
    
    def list(self, request, *args, **kwargs):
        """List commands with caching and pagination."""
        # Check cache for command list
        cache_key = f'command_templates_list_{request.query_params.get("category", "all")}'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            response = super().list(request, *args, **kwargs)
            # Cache for 5 minutes
            cache.set(cache_key, response.data, settings.CACHE_TIMEOUT_MEDIUM)
            return response
        
        return Response(cached_data)
    
    @extend_schema(
        request=CommandExecutionRequestSerializer,
        responses={200: CommandExecutionResponseSerializer},
        description="Execute a command template with provided parameters"
    )
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a command template."""
        command = self.get_object()
        
        # Validate request
        serializer = CommandExecutionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get user's organization and validate
        user = request.user if request.user.is_authenticated else None
        organization = None
        if user:
            organization = RoleService.get_user_organization(user)
            
            # Super admins can bypass checks (but we still track usage if they have an org)
            if organization:
                try:
                    # Check organization status
                    OrganizationStatusService.require_active_organization(organization, user=user)
                    
                    # Check subscription active
                    OrganizationStatusService.require_subscription_active(organization, user=user)
                    
                    # Check tier-based usage limit
                    SubscriptionService.check_usage_limit(organization, 'command_executions', user=user)
                except Exception as e:
                    return Response({
                        'success': False,
                        'output': '',
                        'execution_time': 0,
                        'cost': 0,
                        'token_usage': {},
                        'agent_used': '',
                        'error': str(e)
                    }, status=status.HTTP_403_FORBIDDEN)
        
        parameters = serializer.validated_data['parameters']
        agent_id = serializer.validated_data.get('agent_id')
        
        try:
            # Get agent if agent_id provided
            agent = None
            if agent_id:
                try:
                    agent = Agent.objects.get(agent_id=agent_id)
                except Agent.DoesNotExist:
                    return Response({
                        'success': False,
                        'output': '',
                        'execution_time': 0,
                        'cost': 0,
                        'token_usage': {},
                        'agent_used': '',
                        'error': f'Agent with ID {agent_id} not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Execute command asynchronously with timeout protection
            # Use async_to_sync to properly handle event loop in Django
            try:
                # Wrap in a timeout to prevent indefinite hanging
                async def execute_with_timeout():
                    return await asyncio.wait_for(
                        command_executor.execute(
                            command=command,
                            parameters=parameters,
                            agent=agent,
                            user=request.user if request.user.is_authenticated else None
                        ),
                        timeout=240.0  # 4 minute timeout
                    )
                
                result = async_to_sync(execute_with_timeout)()
            except asyncio.TimeoutError:
                return Response({
                    'success': False,
                    'output': '',
                    'execution_time': 0,
                    'cost': 0,
                    'token_usage': {},
                    'agent_used': '',
                    'error': 'Command execution timed out after 4 minutes'
                }, status=status.HTTP_408_REQUEST_TIMEOUT)
            
            # Increment usage count after successful execution (only if organization exists)
            if organization and result.success:
                try:
                    SubscriptionService.increment_usage(organization, 'command_executions')
                except Exception as e:
                    logger.warning(f"Failed to increment usage count: {e}")
            
            # Prepare response
            response_data = {
                'success': result.success,
                'output': result.output,
                'execution_time': result.execution_time,
                'cost': float(result.cost) if result.cost else 0.0,
                'token_usage': {'tokens_used': result.tokens_used} if result.tokens_used else {},
                'agent_used': result.agent_id or '',
                'error': result.error
            }
            
            # Trigger external integration notifications
            if request.user.is_authenticated:
                try:
                    from apps.integrations_external.signals import trigger_command_execution_notifications
                    trigger_command_execution_notifications(
                        command_id=str(command.id),
                        command_name=command.name,
                        status='success' if result.success else 'failed',
                        user=request.user,
                        result_summary=result.output[:200] if result.output else None,
                        execution_time=result.execution_time,
                        cost=float(result.cost) if result.cost else 0.0,
                        error=result.error
                    )
                except Exception as e:
                    logger.error(f"Failed to trigger command execution notifications: {e}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_response = {
                'success': False,
                'output': '',
                'execution_time': 0,
                'cost': 0,
                'token_usage': {},
                'agent_used': '',
                'error': str(e)
            }
            
            # Trigger external integration notifications for error case
            if request.user.is_authenticated:
                try:
                    from apps.integrations_external.signals import trigger_command_execution_notifications
                    trigger_command_execution_notifications(
                        command_id=str(command.id),
                        command_name=command.name,
                        status='failed',
                        user=request.user,
                        result_summary=None,
                        execution_time=0,
                        cost=0,
                        error=str(e)
                    )
                except Exception as notification_error:
                    logger.error(f"Failed to trigger command execution notifications: {notification_error}")
            
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        request=CommandPreviewRequestSerializer,
        responses={200: CommandPreviewResponseSerializer},
        description="Preview a rendered command template without executing"
    )
    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Preview a command template with parameters."""
        command = self.get_object()
        
        # Validate request
        serializer = CommandPreviewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        parameters = serializer.validated_data['parameters']
        
        try:
            # Validate parameters
            validation_result = parameter_validator.validate(
                parameters_schema=command.parameters,
                provided_parameters=parameters
            )
            
            if not validation_result.is_valid:
                return Response({
                    'rendered_template': '',
                    'validation_errors': validation_result.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Merge with defaults
            final_params = parameter_validator.merge_with_defaults(
                parameters_schema=command.parameters,
                provided_parameters=parameters
            )
            
            # Render template (not async, no need for asyncio.run)
            rendered = template_renderer.render(
                template=command.template,
                parameters=final_params
            )
            
            return Response({
                'rendered_template': rendered,
                'validation_errors': []
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'rendered_template': '',
                'validation_errors': [str(e)]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        description="Get popular commands based on usage and success rate"
    )
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular commands."""
        commands = self.get_queryset().filter(
            is_active=True
        ).order_by('-success_rate', '-usage_count')[:10]
        
        serializer = CommandTemplateListSerializer(commands, many=True)
        return Response(serializer.data)
