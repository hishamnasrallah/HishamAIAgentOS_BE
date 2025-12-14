"""
Workflow API Views

ViewSets for workflow management and execution.
"""

from rest_framework import viewsets, status, serializers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db import models
from django.conf import settings
from django.core.cache import cache
from asgiref.sync import async_to_sync
import uuid
import logging
import traceback

logger = logging.getLogger(__name__)

from apps.workflows.models import Workflow, WorkflowExecution, WorkflowStep
from apps.workflows.serializers import (
    WorkflowListSerializer,
    WorkflowDetailSerializer,
    WorkflowExecutionRequestSerializer,
    WorkflowExecutionStatusSerializer,
    WorkflowExecutionResponseSerializer
)
from apps.workflows.services.workflow_executor import workflow_executor
from apps.core.services.roles import RoleService
from apps.organizations.services import OrganizationStatusService, SubscriptionService


class WorkflowViewSet(viewsets.ModelViewSet):
    """
    Workflow management ViewSet.
    
    Provides CRUD operations for workflows plus execution endpoints.
    
    Access Control:
    - All authenticated users can view and execute workflows
    - Only admins can create/update/delete workflows
    """
    
    serializer_class = WorkflowDetailSerializer  # Default for schema generation
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """All authenticated users can view workflows."""
        queryset = Workflow.objects.all().only(
            'id', 'name', 'slug', 'description', 'version', 'status',
            'is_template', 'execution_count', 'created_at', 'updated_at'
        )
        
        # Filter by is_template if requested
        is_template = self.request.query_params.get('is_template', None)
        if is_template is not None:
            is_template_bool = is_template.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_template=is_template_bool)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List workflows with caching."""
        is_template = request.query_params.get('is_template', None)
        cache_key = f'workflows_list_{is_template or "all"}'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, settings.CACHE_TIMEOUT_MEDIUM)
            return response
        
        return Response(cached_data)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WorkflowListSerializer
        elif self.action == 'execute':
            return WorkflowExecutionRequestSerializer
        return WorkflowDetailSerializer
    
    def get_permissions(self):
        """Override to allow read/execute for all authenticated users, but restrict create/update/delete to admins."""
        if self.action in ['list', 'retrieve', 'execute', 'templates', 'create_from_template']:
            return [permissions.IsAuthenticated()]
        # Create/update/delete require admin
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
    
    def perform_create(self, serializer):
        """
        Create workflow with organization status and subscription validation.
        Also check if tier allows custom workflow creation.
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
            
            # Check if tier allows custom workflow creation (Professional+ only)
            SubscriptionService.check_tier_feature(organization, 'allows_custom_workflows', user=user)
        
        serializer.save(created_by=user)
    
    def perform_update(self, serializer):
        """
        Update workflow with organization status and subscription validation.
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
    
    @extend_schema(
        request=WorkflowExecutionRequestSerializer,
        responses={200: WorkflowExecutionResponseSerializer},
        description="Execute a workflow with provided input data"
    )
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a workflow."""
        workflow = self.get_object()
        
        # Validate request
        serializer = WorkflowExecutionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get user's organization and validate
        user = request.user
        organization = RoleService.get_user_organization(user)
        
        # Super admins can bypass checks (but we still track usage if they have an org)
        if organization:
            try:
                # Check organization status
                OrganizationStatusService.require_active_organization(organization, user=user)
                
                # Check subscription active
                OrganizationStatusService.require_subscription_active(organization, user=user)
                
                # Check tier-based usage limit
                SubscriptionService.check_usage_limit(organization, 'workflow_executions', user=user)
            except Exception as e:
                return Response(
                    {'error': str(e), 'success': False},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        input_data = serializer.validated_data['input_data']
        user_id = str(request.user.id) if request.user.is_authenticated else None
        
        try:
            # Execute workflow asynchronously using async_to_sync for ASGI compatibility
            async def run_execution():
                return await workflow_executor.execute(
                    workflow_id=str(workflow.id),
                    input_data=input_data,
                    user_id=user_id
                )
            
            result = async_to_sync(run_execution)()
            
            # Increment usage count after successful execution (only if organization exists)
            if organization and result.get('success', True):
                try:
                    SubscriptionService.increment_usage(organization, 'workflow_executions')
                except Exception as e:
                    logger.warning(f"Failed to increment usage count: {e}")
            
            # Return execution_id in response for WebSocket connection
            # The execution_id is already in the result from workflow_executor.execute()
            response_data = {
                'success': result.get('success', True),
                'execution_id': result.get('execution_id'),
                'output': result.get('output'),
                'completed_at': result.get('completed_at'),
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Workflow execution error: {str(e)}\n{error_trace}")
            
            # Try to extract execution_id if it was created
            execution_id = None
            try:
                from apps.workflows.models import WorkflowExecution
                # Get the most recent execution for this workflow
                latest_execution = WorkflowExecution.objects.filter(
                    workflow_id=workflow.id
                ).order_by('-created_at').first()
                if latest_execution:
                    execution_id = str(latest_execution.id)
            except Exception:
                pass
            
            error_message = str(e)
            # Extract the most relevant error message
            if 'WorkflowExecutionError' in error_message:
                # Remove the exception class name for cleaner message
                error_message = error_message.replace('WorkflowExecutionError: ', '')
            elif 'WorkflowParseError' in error_message:
                error_message = error_message.replace('WorkflowParseError: ', '')
            
            response_data = {
                'success': False,
                'execution_id': execution_id,
                'output': None,
                'completed_at': None,
                'error': error_message,
                'message': error_message,  # Also include as 'message' for consistency
            }
            
            # Include traceback in DEBUG mode
            if settings.DEBUG:
                response_data['traceback'] = error_trace
                response_data['error_type'] = type(e).__name__
            
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        description="List workflow templates",
        responses={200: WorkflowListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get all workflow templates with caching."""
        cache_key = 'workflow_templates_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is None:
            templates = Workflow.objects.filter(
                is_template=True, status='active'
            ).only('id', 'name', 'slug', 'description', 'version')
            serializer = self.get_serializer(templates, many=True)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, settings.CACHE_TIMEOUT_LONG)
        
        return Response(cached_data)
    
    @extend_schema(
        description="Create a workflow from a template",
        request=serializers.Serializer,
        responses={201: WorkflowDetailSerializer}
    )
    @action(detail=True, methods=['post'])
    def create_from_template(self, request, pk=None):
        """Create a new workflow instance from a template."""
        template = self.get_object()
        
        if not template.is_template:
            return Response(
                {'error': 'This workflow is not a template'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new workflow from template
        new_workflow = Workflow.objects.create(
            name=f"{template.name} (Copy)",
            slug=f"{template.slug}-{uuid.uuid4().hex[:8]}",
            description=template.description,
            definition=template.definition,
            version=template.version,
            status='draft',
            is_template=False,
            created_by=request.user if request.user.is_authenticated else None
        )
        
        serializer = WorkflowDetailSerializer(new_workflow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Workflow Execution ViewSet.
    
    Provides read access to workflow executions plus control endpoints.
    
    Access Control:
    - Users can only see their own executions (admins see all)
    - Users can control (pause/resume/cancel) their own executions
    - Admins can control any execution
    """
    
    serializer_class = WorkflowExecutionStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter executions to only show those created by the current user.
        Admins can see all executions.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return WorkflowExecution.objects.none()
        
        # Use select_related to load workflow relationship
        queryset = WorkflowExecution.objects.select_related('workflow', 'user')
        
        # Admins can see all executions
        if RoleService.is_admin(user):
            return queryset.all()
        
        # Regular users can only see their own executions
        return queryset.filter(user=user)
    
    @extend_schema(
        description="Pause a running workflow execution"
    )
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause workflow execution."""
        execution = self.get_object()
        
        try:
            async def run_pause():
                return await workflow_executor.pause(str(execution.id))
            
            async_to_sync(run_pause)()
            
            return Response({
                'success': True,
                'message': 'Workflow execution paused'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        description="Resume a paused workflow execution"
    )
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume workflow execution."""
        execution = self.get_object()
        
        try:
            async def run_resume():
                return await workflow_executor.resume(str(execution.id))
            
            async_to_sync(run_resume)()
            
            return Response({
                'success': True,
                'message': 'Workflow execution resumed'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        description="Cancel a workflow execution"
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel workflow execution."""
        execution = self.get_object()
        
        try:
            async def run_cancel():
                return await workflow_executor.cancel(str(execution.id))
            
            async_to_sync(run_cancel)()
            
            return Response({
                'success': True,
                'message': 'Workflow execution cancelled'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkflowStepSerializer(serializers.ModelSerializer):
    """Serializer for WorkflowStep model."""
    
    class Meta:
        model = WorkflowStep
        fields = '__all__'


class WorkflowStepViewSet(viewsets.ReadOnlyModelViewSet):
    """
    WorkflowStep ViewSet - Read-only access to workflow steps.
    
    Provides viewing of individual workflow steps within executions.
    
    Access Control:
    - Users can only see steps from their own executions (admins see all)
    """
    
    serializer_class = WorkflowStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter steps to only show those from executions created by the current user.
        Admins can see all steps.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return WorkflowStep.objects.none()
        
        # Admins can see all steps
        if RoleService.is_admin(user):
            return WorkflowStep.objects.all()
        
        # Regular users can only see steps from their own executions
        return WorkflowStep.objects.filter(execution__user=user)
