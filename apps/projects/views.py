"""
Project Management API Views

API endpoints for AI-powered project management features.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db import models
import asyncio

from apps.projects.models import Project, Sprint, Story, Epic
from apps.projects.serializers import (
    ProjectSerializer,
    SprintSerializer,
    StoryGenerationRequestSerializer,
    StorySerializer,
    SprintPlanningRequestSerializer,
    EstimationRequestSerializer,
    EstimationResponseSerializer,
    EpicSerializer,
    TaskSerializer
)
from apps.projects.services.story_generator import story_generator
from apps.projects.services.sprint_planner import sprint_planner
from apps.projects.services.estimation_engine import estimation_engine
from apps.projects.services.analytics import analytics
from apps.authentication.permissions import IsProjectMember, IsProjectMemberOrReadOnly, IsProjectOwner


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Project management ViewSet with AI capabilities.
    
    Access Control:
    - List: Only shows projects where user is owner or member (admins see all)
    - Create: Any authenticated user can create projects (becomes owner)
    - Retrieve/Update/Delete: Only project owners and members can access
    """
    
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    # IMPORTANT: Do not set queryset here - always use get_queryset() for filtering
    
    def get_queryset(self):
        """
        Filter projects to only show those where the user is owner or member.
        Admins can see all projects.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Project.objects.none()
        
        # Admins can see all projects
        if user.role == 'admin':
            return Project.objects.all().select_related('owner').prefetch_related('members')
        
        # Regular users can only see projects they own or are members of
        # Use members__id for ManyToMany field to ensure proper filtering
        user_projects = Project.objects.filter(
            models.Q(owner=user) | models.Q(members__id=user.id)
        ).distinct()
        
        return user_projects.select_related('owner').prefetch_related('members')
    
    def perform_create(self, serializer):
        """Set the current user as the project owner when creating."""
        serializer.save(owner=self.request.user)
    
    @extend_schema(
        request=StoryGenerationRequestSerializer,
        responses={200: StorySerializer(many=True)},
        description="Generate user stories from product vision using AI"
    )
    @action(detail=True, methods=['post'], url_path='generate-stories')
    def generate_stories(self, request, pk=None):
        """Generate user stories from product vision."""
        project = self.get_object()
        
        serializer = StoryGenerationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            stories = asyncio.run(story_generator.generate_stories(
                product_vision=serializer.validated_data['product_vision'],
                context=serializer.validated_data.get('context', {}),
                project_id=str(project.id),
                epic_id=serializer.validated_data.get('epic_id')
            ))
            
            return Response(
                StorySerializer(stories, many=True).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Get project velocity metrics"
    )
    @action(detail=True, methods=['get'], url_path='velocity')
    def velocity(self, request, pk=None):
        """Get velocity metrics for project."""
        project = self.get_object()
        
        num_sprints = int(request.query_params.get('num_sprints', 5))
        
        try:
            velocity_data = asyncio.run(analytics.calculate_velocity(
                project_id=str(project.id),
                num_sprints=num_sprints
            ))
            
            return Response(velocity_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SprintViewSet(viewsets.ModelViewSet):
    """
    Sprint management ViewSet with AI planning.
    
    Access Control:
    - Only accessible to users who are members/owners of the sprint's project.
    """
    
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    filterset_fields = ['project', 'status']  # Enable filtering
    
    def get_queryset(self):
        """
        Filter sprints to only show those from projects where the user is owner or member.
        Admins can see all sprints.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Sprint.objects.none()
        
        # Admins can see all sprints
        if user.role == 'admin':
            return Sprint.objects.all().select_related('project', 'project__owner').prefetch_related('project__members')
        
        # Regular users can only see sprints from projects they own or are members of
        return Sprint.objects.filter(
            models.Q(project__owner=user) | models.Q(project__members__id=user.id)
        ).distinct().select_related('project', 'project__owner').prefetch_related('project__members')
    
    @extend_schema(
        request=SprintPlanningRequestSerializer,
        description="Auto-plan sprint using AI"
    )
    @action(detail=True, methods=['post'], url_path='auto-plan')
    def auto_plan(self, request, pk=None):
        """Auto-plan sprint with AI."""
        sprint = self.get_object()
        
        serializer = SprintPlanningRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Get backlog stories
            if 'backlog_ids' in serializer.validated_data:
                backlog = Story.objects.filter(
                    id__in=serializer.validated_data['backlog_ids']
                )
            else:
                backlog = Story.objects.filter(
                    project=sprint.project,
                    status='backlog'
                )
            
            backlog_list = list(backlog)
            
            plan = asyncio.run(sprint_planner.plan_sprint(
                sprint_id=str(sprint.id),
                backlog_stories=backlog_list,
                team_velocity=serializer.validated_data['team_velocity'],
                constraints=serializer.validated_data.get('constraints', {})
            ))
            
            return Response(plan, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Get sprint burndown chart"
    )
    @action(detail=True, methods=['get'], url_path='burndown')
    def burndown(self, request, pk=None):
        """Get burndown chart data."""
        sprint = self.get_object()
        
        try:
            burndown_data = asyncio.run(analytics.calculate_burndown(
                sprint_id=str(sprint.id)
            ))
            
            return Response(burndown_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Get sprint health metrics"
    )
    @action(detail=True, methods=['get'], url_path='health')
    def health(self, request, pk=None):
        """Get sprint health metrics."""
        sprint = self.get_object()
        
        try:
            health_data = asyncio.run(analytics.calculate_sprint_health(
                sprint_id=str(sprint.id)
            ))
            
            return Response(health_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StoryViewSet(viewsets.ModelViewSet):
    """
    Story management ViewSet with AI estimation.
    
    Access Control:
    - Only accessible to users who are members/owners of the story's project.
    """
    
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    filterset_fields = ['project', 'sprint', 'status', 'priority']  # Enable filtering
    
    def get_queryset(self):
        """
        Filter stories to only show those from projects where the user is owner or member.
        Admins can see all stories.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Story.objects.none()
        
        # Admins can see all stories
        if user.role == 'admin':
            return Story.objects.all().select_related('project', 'project__owner', 'sprint', 'epic', 'assigned_to', 'created_by').prefetch_related('project__members')
        
        # Regular users can only see stories from projects they own or are members of
        return Story.objects.filter(
            models.Q(project__owner=user) | models.Q(project__members__id=user.id)
        ).distinct().select_related('project', 'project__owner', 'sprint', 'epic', 'assigned_to', 'created_by').prefetch_related('project__members')
    
    def perform_create(self, serializer):
        """Set the current user as the story creator when creating."""
        serializer.save(created_by=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Override update to log request data."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[StoryViewSet] Update request for story {kwargs.get('pk')}")
        logger.info(f"[StoryViewSet] Request data: {request.data}")
        return super().update(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Override create to log request data."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[StoryViewSet] Create request")
        logger.info(f"[StoryViewSet] Request data: {request.data}")
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        request=EstimationRequestSerializer,
        responses={200: EstimationResponseSerializer},
        description="Estimate story points using AI"
    )
    @action(detail=True, methods=['post'], url_path='estimate')
    def estimate(self, request, pk=None):
        """Estimate story points."""
        story = self.get_object()
        
        serializer = EstimationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            estimation = asyncio.run(estimation_engine.estimate_story(
                story=story,
                use_historical=serializer.validated_data.get('use_historical', True)
            ))
            
            return Response(estimation, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Backward compatibility - UserStoryViewSet is an alias for StoryViewSet
UserStoryViewSet = StoryViewSet


class EpicViewSet(viewsets.ModelViewSet):
    """
    Epic management ViewSet.
    
    Access Control:
    - Only accessible to users who are members/owners of the epic's project.
    """
    
    serializer_class = EpicSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    filterset_fields = ['project', 'status']  # Enable filtering
    
    def get_queryset(self):
        """
        Filter epics to only show those from projects where the user is owner or member.
        Admins can see all epics.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Epic.objects.none()
        
        # Admins can see all epics
        if user.role == 'admin':
            return Epic.objects.all().select_related('project', 'project__owner').prefetch_related('project__members')
        
        # Regular users can only see epics from projects they own or are members of
        return Epic.objects.filter(
            models.Q(project__owner=user) | models.Q(project__members__id=user.id)
        ).distinct().select_related('project', 'project__owner').prefetch_related('project__members')


class TaskViewSet(viewsets.ModelViewSet):
    """
    Task management ViewSet.
    
    Provides CRUD for tasks within user stories.
    
    Access Control:
    - Only accessible to users who are members/owners of the task's story's project.
    """
    
    from apps.projects.models import Task
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    filterset_fields = ['story', 'status', 'assigned_to']  # Enable filtering
    
    def get_queryset(self):
        """
        Filter tasks to only show those from stories in projects where the user is owner or member.
        Admins can see all tasks.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Task.objects.none()
        
        # Admins can see all tasks
        if user.role == 'admin':
            return Task.objects.all().select_related('story', 'story__project', 'story__project__owner', 'assigned_to').prefetch_related('story__project__members')
        
        # Regular users can only see tasks from stories in projects they own or are members of
        return Task.objects.filter(
            models.Q(story__project__owner=user) | models.Q(story__project__members__id=user.id)
        ).distinct().select_related('story', 'story__project', 'story__project__owner', 'assigned_to').prefetch_related('story__project__members')
