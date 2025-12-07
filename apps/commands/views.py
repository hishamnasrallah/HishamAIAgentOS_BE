"""
Views for commands app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from asgiref.sync import async_to_sync
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

# Instantiate services
template_renderer = TemplateRenderer()
parameter_validator = ParameterValidator()


class CommandCategoryViewSet(viewsets.ModelViewSet):
    """Command category viewset."""
    
    queryset = CommandCategory.objects.all()
    serializer_class = CommandCategorySerializer
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name', 'created_at']


class CommandTemplateViewSet(viewsets.ModelViewSet):
    """Command template viewset with execute and preview actions."""
    
    queryset = CommandTemplate.objects.all()
    serializer_class = CommandTemplateSerializer
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['created_at', 'usage_count', 'name', 'success_rate', 'estimated_cost']
    pagination_class = None  # Disable pagination - return all commands at once
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CommandTemplateListSerializer
        elif self.action == 'execute':
            return CommandExecutionRequestSerializer
        elif self.action == 'preview':
            return CommandPreviewRequestSerializer
        return CommandTemplateSerializer
    
    def get_queryset(self):
        return CommandTemplate.objects.select_related('category', 'recommended_agent')
    
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
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'output': '',
                'execution_time': 0,
                'cost': 0,
                'token_usage': {},
                'agent_used': '',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
