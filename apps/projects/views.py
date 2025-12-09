"""
Project Management API Views

API endpoints for AI-powered project management features.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db import models
from django.db.models import Q
from django.utils import timezone
import asyncio
import json

from apps.projects.models import (
    Project, Sprint, UserStory, Epic, Task, Bug, Issue, TimeLog, ProjectConfiguration, 
    Mention, StoryComment, StoryDependency, StoryAttachment, Notification, Watcher, Activity, EditHistory, SavedSearch,
    StatusChangeApproval
)
# Alias for backward compatibility
Story = UserStory
from apps.projects.serializers import (
    ProjectSerializer,
    SprintSerializer,
    StoryGenerationRequestSerializer,
    StorySerializer,
    SprintPlanningRequestSerializer,
    EstimationRequestSerializer,
    EstimationResponseSerializer,
    EpicSerializer,
    TaskSerializer,
    BugSerializer,
    IssueSerializer,
    TimeLogSerializer,
    WatcherSerializer,
    ProjectConfigurationSerializer,
    MentionSerializer,
    StoryCommentSerializer,
    StoryDependencySerializer,
    StoryAttachmentSerializer,
    NotificationSerializer,
    ActivitySerializer,
    EditHistorySerializer,
    SavedSearchSerializer
)
from apps.projects.serializers_approval import StatusChangeApprovalSerializer
from apps.projects.services.story_generator import story_generator
from apps.projects.services.sprint_planner import sprint_planner
from apps.projects.services.estimation_engine import estimation_engine
from apps.projects.services.analytics import analytics
from apps.authentication.permissions import IsProjectMember, IsProjectMemberOrReadOnly, IsProjectOwner
from apps.authentication.serializers import UserSerializer


def filter_by_tags(queryset, tags_list, tags_field='tags'):
    """
    Filter queryset by tags in a database-agnostic way.
    For SQLite, uses a workaround since contains lookup is not supported.
    For PostgreSQL and other databases, uses contains lookup.
    """
    from django.db import connection
    
    if connection.vendor == 'sqlite':
        # For SQLite, we need to filter in Python or use a workaround
        # Since filtering in Python is inefficient, we'll use a simple workaround:
        # Check if the JSON string contains the tag (less precise but works)
        tag_filters = Q()
        for tag in tags_list:
            # Use icontains on the JSON string representation
            # This is a workaround and may have false positives
            tag_filters |= Q(**{f'{tags_field}__icontains': tag})
        return queryset.filter(tag_filters)
    else:
        # For PostgreSQL and other databases, use contains lookup
        tag_filters = Q()
        for tag in tags_list:
            tag_filters |= Q(**{f'{tags_field}__contains': [tag]})
        return queryset.filter(tag_filters)


def filter_by_labels(queryset, label_names, labels_field='labels'):
    """
    Filter queryset by label names in a database-agnostic way.
    Labels are stored as JSONField: [{'name': 'Urgent', 'color': '#red'}, ...]
    """
    from django.db import connection
    
    if connection.vendor == 'sqlite':
        # For SQLite, use icontains on JSON string
        label_filters = Q()
        for label_name in label_names:
            # Check if JSON string contains the label name
            label_filters |= Q(**{f'{labels_field}__icontains': label_name})
        return queryset.filter(label_filters)
    else:
        # For PostgreSQL, use JSON path queries
        label_filters = Q()
        for label_name in label_names:
            # Check if any label object has this name
            # Using JSON path: labels[*].name
            label_filters |= Q(**{f'{labels_field}__contains': [{'name': label_name}]})
        return queryset.filter(label_filters)


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
        Supports tag filtering via ?tags=tag1,tag2 query parameter.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Project.objects.none()
        
        # Base queryset
        if user.role == 'admin':
            queryset = Project.objects.all()
        else:
            queryset = Project.objects.filter(
            models.Q(owner=user) | models.Q(members__id=user.id)
        ).distinct()
        
        # Tag filtering
        tags_param = self.request.query_params.get('tags', None)
        if tags_param:
            tags_list = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
            if tags_list:
                queryset = filter_by_tags(queryset, tags_list)
        
        return queryset.select_related('owner').prefetch_related('members')
    
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
    
    @extend_schema(
        description="Get project members (owner + members)",
        responses={200: UserSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='members')
    def members(self, request, pk=None):
        """Get all project members including the owner."""
        project = self.get_object()
        
        # Get all members (owner + members)
        members_list = list(project.members.all())
        if project.owner and project.owner not in members_list:
            members_list.insert(0, project.owner)
        
        serializer = UserSerializer(members_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Add a member to the project",
        request={'type': 'object', 'properties': {'user_id': {'type': 'string', 'format': 'uuid'}}},
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['post'], url_path='members/add')
    def add_member(self, request, pk=None):
        """Add a member to the project."""
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.authentication.models import User
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Don't add the owner as a member
        if project.owner == user:
            return Response(
                {'error': 'Project owner is already a member'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add member if not already a member
        if not project.members.filter(id=user.id).exists():
            project.members.add(user)
        
        return Response(
            {'message': 'Member added successfully', 'user_id': str(user.id)},
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        description="Remove a member from the project",
        request={'type': 'object', 'properties': {'user_id': {'type': 'string', 'format': 'uuid'}}},
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['post'], url_path='members/remove')
    def remove_member(self, request, pk=None):
        """Remove a member from the project."""
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.authentication.models import User
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Don't allow removing the owner
        if project.owner == user:
            return Response(
                {'error': 'Cannot remove project owner'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Remove member if they are a member
        if project.members.filter(id=user.id).exists():
            project.members.remove(user)
        
        return Response(
            {'message': 'Member removed successfully', 'user_id': str(user.id)},
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        description="Get all tags used in projects accessible to the user",
        responses={200: {'type': 'object', 'properties': {'tags': {'type': 'array', 'items': {'type': 'string'}}}}}
    )
    @action(detail=False, methods=['get'], url_path='tags')
    def tags(self, request):
        """Get all unique tags from projects accessible to the user."""
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'tags': []}, status=status.HTTP_200_OK)
        
        # Get accessible projects
        if user.role == 'admin':
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(
                models.Q(owner=user) | models.Q(members__id=user.id)
            ).distinct()
        
        # Collect all tags
        all_tags = set()
        for project in projects:
            if project.tags and isinstance(project.tags, list):
                all_tags.update(project.tags)
        
        return Response({
            'tags': sorted(list(all_tags))
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Get tag suggestions (autocomplete)",
        parameters=[{
            'name': 'q',
            'in': 'query',
            'description': 'Search query',
            'required': False,
            'schema': {'type': 'string'}
        }],
        responses={200: {'type': 'object', 'properties': {'tags': {'type': 'array', 'items': {'type': 'string'}}}}}
    )
    @action(detail=False, methods=['get'], url_path='tags/autocomplete')
    def tags_autocomplete(self, request):
        """Get tag suggestions for autocomplete."""
        query = request.query_params.get('q', '').strip().lower()
        
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'tags': []}, status=status.HTTP_200_OK)
        
        # Get accessible projects
        if user.role == 'admin':
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(
                models.Q(owner=user) | models.Q(members__id=user.id)
            ).distinct()
        
        # Collect matching tags
        matching_tags = set()
        for project in projects:
            if project.tags and isinstance(project.tags, list):
                for tag in project.tags:
                    if isinstance(tag, str) and (not query or query in tag.lower()):
                        matching_tags.add(tag)
        
        return Response({
            'tags': sorted(list(matching_tags))[:20]  # Limit to 20 suggestions
        }, status=status.HTTP_200_OK)


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
    
    def perform_create(self, serializer):
        """Set default sprint values from project configuration."""
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        project = serializer.validated_data.get('project')
        if project:
            try:
                config = project.configuration
                if config:
                    # Use default sprint duration if not provided
                    if 'start_date' in serializer.validated_data and 'end_date' not in serializer.validated_data:
                        start_date = serializer.validated_data['start_date']
                        duration_days = config.default_sprint_duration_days or 14
                        end_date = start_date + timedelta(days=duration_days - 1)
                        serializer.validated_data['end_date'] = end_date
                    
                    # Use default sprint start day if dates not provided
                    if 'start_date' not in serializer.validated_data:
                        sprint_start_day = config.sprint_start_day or 0  # 0 = Monday
                        today = timezone.now().date()
                        days_until_start = (sprint_start_day - today.weekday()) % 7
                        if days_until_start == 0:
                            days_until_start = 7  # Next week if today is the start day
                        start_date = today + timedelta(days=days_until_start)
                        serializer.validated_data['start_date'] = start_date
                        
                        # Set end date based on duration
                        duration_days = config.default_sprint_duration_days or 14
                        end_date = start_date + timedelta(days=duration_days - 1)
                        serializer.validated_data['end_date'] = end_date
            except ProjectConfiguration.DoesNotExist:
                pass  # No configuration, use defaults from serializer
        
        serializer.save(created_by=self.request.user)
    
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
    filterset_fields = ['sprint', 'status', 'priority', 'story_type', 'component']  # Enable filtering (project handled manually)
    
    def get_queryset(self):
        """
        Filter stories to only show those from projects where the user is owner or member.
        Admins can see all stories.
        Supports tag filtering via ?tags=tag1,tag2 query parameter.
        Supports project filtering via ?project=uuid query parameter.
        Supports due date filtering via ?overdue=true, ?due_today=true, ?due_soon=true, ?due_date__gte=YYYY-MM-DD, ?due_date__lte=YYYY-MM-DD
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Story.objects.none()
        
        # Base queryset
        if user.role == 'admin':
            queryset = Story.objects.all()
        else:
            queryset = Story.objects.filter(
            models.Q(project__owner=user) | models.Q(project__members__id=user.id)
            ).distinct()
        
        # Project filtering (handle manually to ensure permission checking)
        project_id = self.request.query_params.get('project', None)
        if project_id:
            try:
                # Validate UUID format
                import uuid as uuid_lib
                project_uuid = uuid_lib.UUID(project_id)
                # Filter by project, but only if user has access (already filtered above)
                queryset = queryset.filter(project_id=project_uuid)
            except (ValueError, TypeError):
                # Invalid UUID format - return empty queryset
                return Story.objects.none()
        
        # Tag filtering
        tags_param = self.request.query_params.get('tags', None)
        if tags_param:
            tags_list = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
            if tags_list:
                queryset = filter_by_tags(queryset, tags_list)
        
        # Label filtering
        labels_param = self.request.query_params.get('labels', None)
        if labels_param:
            labels_list = [label.strip() for label in labels_param.split(',') if label.strip()]
            if labels_list:
                queryset = filter_by_labels(queryset, labels_list)
        
        # Due date filtering
        today = timezone.now().date()
        overdue_param = self.request.query_params.get('overdue', None)
        due_today_param = self.request.query_params.get('due_today', None)
        due_soon_param = self.request.query_params.get('due_soon', None)
        due_date_gte = self.request.query_params.get('due_date__gte', None)
        due_date_lte = self.request.query_params.get('due_date__lte', None)
        
        if overdue_param and overdue_param.lower() == 'true':
            queryset = queryset.filter(due_date__lt=today)
        elif due_today_param and due_today_param.lower() == 'true':
            queryset = queryset.filter(due_date=today)
        elif due_soon_param and due_soon_param.lower() == 'true':
            # Due within next 3 days
            from datetime import timedelta
            soon_date = today + timedelta(days=3)
            queryset = queryset.filter(due_date__gte=today, due_date__lte=soon_date)
        
        if due_date_gte:
            try:
                from datetime import datetime
                gte_date = datetime.strptime(due_date_gte, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__gte=gte_date)
            except (ValueError, TypeError):
                pass  # Invalid date format, ignore
        
        if due_date_lte:
            try:
                from datetime import datetime
                lte_date = datetime.strptime(due_date_lte, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__lte=lte_date)
            except (ValueError, TypeError):
                pass  # Invalid date format, ignore
        
        return queryset.select_related('project', 'project__owner', 'sprint', 'epic', 'assigned_to', 'created_by').prefetch_related('project__members')
    
    def perform_create(self, serializer):
        """Set the current user as the story creator when creating."""
        # Check project-level permissions
        project = serializer.validated_data.get('project')
        if project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(project)
            has_perm, error = perm_service.can_create_story(self.request.user)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to create stories in this project")
        
        serializer.save(created_by=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Override update to log request data and check permissions."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[StoryViewSet] Update request for story {kwargs.get('pk')}")
        logger.info(f"[StoryViewSet] Request data: {request.data}")
        
        # Check project-level permissions
        story = self.get_object()
        if story and story.project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(story.project)
            
            # Check edit permission
            has_perm, error = perm_service.can_edit_story(request.user, story)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to edit this story")
            
            # Check status change permission if status is being changed
            if 'status' in request.data and request.data['status'] != story.status:
                has_perm, error = perm_service.can_change_status(request.user, story)
                if not has_perm:
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied(error or "You don't have permission to change the status of this story")
            
            # Check assignment permission if assigned_to is being changed
            if 'assigned_to' in request.data:
                has_perm, error = perm_service.can_assign_story(request.user)
                if not has_perm:
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied(error or "You don't have permission to assign stories")
        
        return super().update(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Override create to log request data and check permissions."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[StoryViewSet] Create request")
        logger.info(f"[StoryViewSet] Request data: {request.data}")
        
        # Permission check is done in perform_create
        return super().create(request, *args, **kwargs)
    
    def perform_destroy(self, instance):
        """Check permissions before destroying."""
        if instance.project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(instance.project)
            has_perm, error = perm_service.can_delete_story(self.request.user, instance)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to delete this story")
        
        super().perform_destroy(instance)
    
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
    
    @extend_schema(
        description="Get all tags used in stories accessible to the user",
        responses={200: {'type': 'object', 'properties': {'tags': {'type': 'array', 'items': {'type': 'string'}}}}}
    )
    @action(detail=False, methods=['get'], url_path='tags')
    def tags(self, request):
        """Get all unique tags from stories accessible to the user."""
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'tags': []}, status=status.HTTP_200_OK)
        
        # Get accessible stories
        if user.role == 'admin':
            stories = Story.objects.all()
        else:
            stories = Story.objects.filter(
                models.Q(project__owner=user) | models.Q(project__members__id=user.id)
            ).distinct()
        
        # Collect all tags
        all_tags = set()
        for story in stories:
            if story.tags and isinstance(story.tags, list):
                all_tags.update(story.tags)
        
        return Response({
            'tags': sorted(list(all_tags))
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Get tag suggestions for stories (autocomplete)",
        parameters=[{
            'name': 'q',
            'in': 'query',
            'description': 'Search query',
            'required': False,
            'schema': {'type': 'string'}
        }, {
            'name': 'project',
            'in': 'query',
            'description': 'Filter by project ID',
            'required': False,
            'schema': {'type': 'string', 'format': 'uuid'}
        }],
        responses={200: {'type': 'object', 'properties': {'tags': {'type': 'array', 'items': {'type': 'string'}}}}}
    )
    @action(detail=False, methods=['get'], url_path='tags/autocomplete')
    def tags_autocomplete(self, request):
        """Get tag suggestions for autocomplete."""
        query = request.query_params.get('q', '').strip().lower()
        project_id = request.query_params.get('project', None)
        
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'tags': []}, status=status.HTTP_200_OK)
        
        # Get accessible stories
        if user.role == 'admin':
            stories = Story.objects.all()
        else:
            stories = Story.objects.filter(
                models.Q(project__owner=user) | models.Q(project__members__id=user.id)
            ).distinct()
        
        # Filter by project if specified
        if project_id:
            stories = stories.filter(project_id=project_id)
        
        # Collect matching tags
        matching_tags = set()
        for story in stories:
            if story.tags and isinstance(story.tags, list):
                for tag in story.tags:
                    if isinstance(tag, str) and (not query or query in tag.lower()):
                        matching_tags.add(tag)
        
        return Response({
            'tags': sorted(list(matching_tags))[:20]  # Limit to 20 suggestions
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Get component suggestions for stories (autocomplete)",
        parameters=[{
            'name': 'q',
            'in': 'query',
            'description': 'Search query',
            'required': False,
            'schema': {'type': 'string'}
        }, {
            'name': 'project',
            'in': 'query',
            'description': 'Filter by project ID',
            'required': False,
            'schema': {'type': 'string', 'format': 'uuid'}
        }],
        responses={200: {'type': 'object', 'properties': {'components': {'type': 'array', 'items': {'type': 'string'}}}}}
    )
    @action(detail=False, methods=['get'], url_path='components/autocomplete')
    def components_autocomplete(self, request):
        """Get component suggestions for autocomplete."""
        query = request.query_params.get('q', '').strip().lower()
        project_id = request.query_params.get('project', None)
        
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'components': []}, status=status.HTTP_200_OK)
        
        # Get accessible stories
        if user.role == 'admin':
            stories = Story.objects.all()
        else:
            stories = Story.objects.filter(
                models.Q(project__owner=user) | models.Q(project__members__id=user.id)
            ).distinct()
        
        # Filter by project if specified
        if project_id:
            stories = stories.filter(project_id=project_id)
        
        # Collect matching components (non-null, non-empty)
        matching_components = set()
        for story in stories:
            if story.component and story.component.strip():
                component = story.component.strip()
                if not query or query in component.lower():
                    matching_components.add(component)
        
        return Response({
            'components': sorted(list(matching_components))[:20]  # Limit to 20 suggestions
        }, status=status.HTTP_200_OK)


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
    filterset_fields = ['project', 'status', 'owner']  # Enable filtering
    
    def get_queryset(self):
        """
        Filter epics to only show those from projects where the user is owner or member.
        Admins can see all epics.
        Supports tag filtering via ?tags=tag1,tag2 query parameter.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Epic.objects.none()
        
        # Base queryset
        if user.role == 'admin':
            queryset = Epic.objects.all()
        else:
            queryset = Epic.objects.filter(
            models.Q(project__owner=user) | models.Q(project__members__id=user.id)
            ).distinct()
        
        # Tag filtering
        tags_param = self.request.query_params.get('tags', None)
        if tags_param:
            tags_list = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
            if tags_list:
                queryset = filter_by_tags(queryset, tags_list)
        
        return queryset.select_related('project', 'project__owner', 'owner').prefetch_related('project__members')
    
    def perform_create(self, serializer):
        """Check permissions before creating epic."""
        project = serializer.validated_data.get('project')
        if project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(project)
            has_perm, error = perm_service.can_create_epic(self.request.user)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to create epics in this project")
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Check permissions before updating epic."""
        epic = serializer.instance
        if epic and epic.project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(epic.project)
            has_perm, error = perm_service.can_edit_epic(self.request.user, epic)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to edit this epic")
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Check permissions before destroying epic."""
        if instance.project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(instance.project)
            has_perm, error = perm_service.can_delete_epic(self.request.user)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to delete this epic")
        super().perform_destroy(instance)


class TaskViewSet(viewsets.ModelViewSet):
    """
    Task management ViewSet.
    
    Provides CRUD for tasks within user stories.
    
    Access Control:
    - Only accessible to users who are members/owners of the task's story's project.
    """
    
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    filterset_fields = ['story', 'status', 'assigned_to']  # Enable filtering
    queryset = Task.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """
        Filter tasks to only show those from stories in projects where the user is owner or member.
        Admins can see all tasks.
        Supports tag filtering via ?tags=tag1,tag2 query parameter.
        Supports due date filtering via ?overdue=true, ?due_today=true, ?due_soon=true, ?due_date__gte=YYYY-MM-DD, ?due_date__lte=YYYY-MM-DD
        """
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()
        
        user = self.request.user
        if not user or not user.is_authenticated:
            return Task.objects.none()
        
        # Base queryset
        if user.role == 'admin':
            queryset = Task.objects.all()
        else:
            queryset = Task.objects.filter(
            models.Q(story__project__owner=user) | models.Q(story__project__members__id=user.id)
            ).distinct()
        
        # Tag filtering
        tags_param = self.request.query_params.get('tags', None)
        if tags_param:
            tags_list = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
            if tags_list:
                queryset = filter_by_tags(queryset, tags_list)
        
        # Label filtering
        labels_param = self.request.query_params.get('labels', None)
        if labels_param:
            labels_list = [label.strip() for label in labels_param.split(',') if label.strip()]
            if labels_list:
                queryset = filter_by_labels(queryset, labels_list)
        
        # Due date filtering
        today = timezone.now().date()
        overdue_param = self.request.query_params.get('overdue', None)
        due_today_param = self.request.query_params.get('due_today', None)
        due_soon_param = self.request.query_params.get('due_soon', None)
        due_date_gte = self.request.query_params.get('due_date__gte', None)
        due_date_lte = self.request.query_params.get('due_date__lte', None)
        
        if overdue_param and overdue_param.lower() == 'true':
            queryset = queryset.filter(due_date__lt=today)
        elif due_today_param and due_today_param.lower() == 'true':
            queryset = queryset.filter(due_date=today)
        elif due_soon_param and due_soon_param.lower() == 'true':
            # Due within next 3 days
            from datetime import timedelta
            soon_date = today + timedelta(days=3)
            queryset = queryset.filter(due_date__gte=today, due_date__lte=soon_date)
        
        if due_date_gte:
            try:
                from datetime import datetime
                gte_date = datetime.strptime(due_date_gte, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__gte=gte_date)
            except (ValueError, TypeError):
                pass  # Invalid date format, ignore
        
        if due_date_lte:
            try:
                from datetime import datetime
                lte_date = datetime.strptime(due_date_lte, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__lte=lte_date)
            except (ValueError, TypeError):
                pass  # Invalid date format, ignore
        
        return queryset.select_related('story', 'story__project', 'story__project__owner', 'assigned_to').prefetch_related('story__project__members')


class BugViewSet(viewsets.ModelViewSet):
    """
    Bug management ViewSet.
    
    Access Control:
    - Only accessible to users who are members/owners of the bug's project.
    """
    
    serializer_class = BugSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    filterset_fields = ['project', 'status', 'severity', 'priority', 'assigned_to', 'reporter', 'environment']
    queryset = Bug.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """
        Filter bugs to only show those from projects where the user is owner or member.
        Admins can see all bugs.
        Supports tag filtering via ?tags=tag1,tag2 query parameter.
        Supports due date filtering via ?overdue=true, ?due_today=true, ?due_soon=true, ?due_date__gte=YYYY-MM-DD, ?due_date__lte=YYYY-MM-DD
        """
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Bug.objects.none()
        
        user = self.request.user
        if not user or not user.is_authenticated:
            return Bug.objects.none()
        
        # Base queryset
        if user.role == 'admin':
            queryset = Bug.objects.all()
        else:
            queryset = Bug.objects.filter(
                models.Q(project__owner=user) | models.Q(project__members__id=user.id)
            ).distinct()
        
        # Tag filtering
        tags_param = self.request.query_params.get('tags', None)
        if tags_param:
            tags_list = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
            if tags_list:
                queryset = filter_by_tags(queryset, tags_list)
        
        # Label filtering
        labels_param = self.request.query_params.get('labels', None)
        if labels_param:
            labels_list = [label.strip() for label in labels_param.split(',') if label.strip()]
            if labels_list:
                queryset = filter_by_labels(queryset, labels_list)
        
        # Due date filtering
        today = timezone.now().date()
        overdue_param = self.request.query_params.get('overdue', None)
        due_today_param = self.request.query_params.get('due_today', None)
        due_soon_param = self.request.query_params.get('due_soon', None)
        due_date_gte = self.request.query_params.get('due_date__gte', None)
        due_date_lte = self.request.query_params.get('due_date__lte', None)
        
        if overdue_param and overdue_param.lower() == 'true':
            queryset = queryset.filter(due_date__lt=today)
        elif due_today_param and due_today_param.lower() == 'true':
            queryset = queryset.filter(due_date=today)
        elif due_soon_param and due_soon_param.lower() == 'true':
            # Due within next 3 days
            from datetime import timedelta
            soon_date = today + timedelta(days=3)
            queryset = queryset.filter(due_date__gte=today, due_date__lte=soon_date)
        
        if due_date_gte:
            try:
                from datetime import datetime
                gte_date = datetime.strptime(due_date_gte, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__gte=gte_date)
            except (ValueError, TypeError):
                pass  # Invalid date format, ignore
        
        if due_date_lte:
            try:
                from datetime import datetime
                lte_date = datetime.strptime(due_date_lte, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__lte=lte_date)
            except (ValueError, TypeError):
                pass  # Invalid date format, ignore
        
        return queryset.select_related(
            'project', 'project__owner', 'reporter', 'assigned_to', 'duplicate_of'
        ).prefetch_related('project__members', 'linked_stories', 'duplicates')
    
    def perform_create(self, serializer):
        """Set created_by and reporter on bug creation."""
        user = self.request.user
        serializer.save(created_by=user, reporter=user if not serializer.validated_data.get('reporter') else None)
    
    def perform_update(self, serializer):
        """Set updated_by on bug update."""
        serializer.save(updated_by=self.request.user)


class IssueViewSet(viewsets.ModelViewSet):
    """
    Issue management ViewSet.
    
    Provides CRUD for issues within projects.
    
    Access Control:
    - Only accessible to users who are members/owners of the issue's project.
    """
    
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    filterset_fields = ['project', 'status', 'issue_type', 'priority', 'assigned_to', 'reporter']
    queryset = Issue.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """
        Filter issues to only show those from projects where the user is owner or member.
        Admins can see all issues.
        Supports tag filtering via ?tags=tag1,tag2 query parameter.
        Supports due date filtering via ?overdue=true, ?due_today=true, ?due_soon=true, ?due_date__gte=YYYY-MM-DD, ?due_date__lte=YYYY-MM-DD
        """
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Issue.objects.none()
        
        user = self.request.user
        if not user or not user.is_authenticated:
            return Issue.objects.none()
        
        # Base queryset
        if user.role == 'admin':
            queryset = Issue.objects.all()
        else:
            queryset = Issue.objects.filter(
                models.Q(project__owner=user) | models.Q(project__members__id=user.id)
            ).distinct()
        
        # Tag filtering
        tags_param = self.request.query_params.get('tags', None)
        if tags_param:
            tags_list = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
            if tags_list:
                queryset = filter_by_tags(queryset, tags_list)
        
        # Label filtering
        labels_param = self.request.query_params.get('labels', None)
        if labels_param:
            labels_list = [label.strip() for label in labels_param.split(',') if label.strip()]
            if labels_list:
                queryset = filter_by_labels(queryset, labels_list)
        
        # Due date filtering
        today = timezone.now().date()
        overdue_param = self.request.query_params.get('overdue', None)
        due_today_param = self.request.query_params.get('due_today', None)
        due_soon_param = self.request.query_params.get('due_soon', None)
        due_date_gte = self.request.query_params.get('due_date__gte', None)
        due_date_lte = self.request.query_params.get('due_date__lte', None)
        
        if overdue_param and overdue_param.lower() == 'true':
            queryset = queryset.filter(due_date__lt=today)
        elif due_today_param and due_today_param.lower() == 'true':
            queryset = queryset.filter(due_date=today)
        elif due_soon_param and due_soon_param.lower() == 'true':
            # Due within next 3 days
            from datetime import timedelta
            soon_date = today + timedelta(days=3)
            queryset = queryset.filter(due_date__gte=today, due_date__lte=soon_date)
        
        if due_date_gte:
            try:
                from datetime import datetime
                gte_date = datetime.strptime(due_date_gte, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__gte=gte_date)
            except (ValueError, TypeError):
                pass  # Invalid date format, ignore
        
        if due_date_lte:
            try:
                from datetime import datetime
                lte_date = datetime.strptime(due_date_lte, '%Y-%m-%d').date()
                queryset = queryset.filter(due_date__lte=lte_date)
            except (ValueError, TypeError):
                pass  # Invalid date format, ignore
        
        return queryset.select_related(
            'project', 'project__owner', 'reporter', 'assigned_to', 'duplicate_of'
        ).prefetch_related(
            'project__members', 'linked_stories', 'linked_tasks', 'linked_bugs', 
            'watchers', 'duplicates'
        )
    
    def perform_create(self, serializer):
        """Check permissions before creating issue."""
        project = serializer.validated_data.get('project')
        if project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(project)
            has_perm, error = perm_service.can_create_issue(self.request.user)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to create issues in this project")
        serializer.save(created_by=self.request.user, reporter=self.request.user)
    
    def perform_update(self, serializer):
        """Check permissions before updating issue."""
        issue = serializer.instance
        if issue and issue.project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(issue.project)
            has_perm, error = perm_service.can_edit_issue(self.request.user, issue)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to edit this issue")
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Check permissions before destroying issue."""
        if instance.project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(instance.project)
            has_perm, error = perm_service.can_delete_issue(self.request.user)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to delete this issue")
        super().perform_destroy(instance)


class TimeLogViewSet(viewsets.ModelViewSet):
    """
    Time log management ViewSet.
    
    Provides CRUD for time logs within projects.
    
    Access Control:
    - Users can only see/edit their own time logs unless they're project owners/admins.
    """
    
    serializer_class = TimeLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    filterset_fields = ['user', 'story', 'task', 'bug', 'issue', 'is_billable']
    queryset = TimeLog.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """
        Filter time logs based on user permissions.
        Users can see their own time logs and time logs from projects they're members of.
        Admins can see all time logs.
        """
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return TimeLog.objects.none()
        
        user = self.request.user
        if not user or not user.is_authenticated:
            return TimeLog.objects.none()
        
        # Base queryset
        if user.role == 'admin':
            queryset = TimeLog.objects.all()
        else:
            # Users can see their own time logs or time logs from projects they're members of
            queryset = TimeLog.objects.filter(
                models.Q(user=user) |
                models.Q(story__project__owner=user) |
                models.Q(story__project__members__id=user.id) |
                models.Q(task__story__project__owner=user) |
                models.Q(task__story__project__members__id=user.id) |
                models.Q(bug__project__owner=user) |
                models.Q(bug__project__members__id=user.id) |
                models.Q(issue__project__owner=user) |
                models.Q(issue__project__members__id=user.id)
            ).distinct()
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)
        
        return queryset.select_related(
            'user', 'story', 'task', 'bug', 'issue',
            'story__project', 'task__story__project', 'bug__project', 'issue__project'
        )
    
    def perform_create(self, serializer):
        """Set created_by and user on time log creation."""
        user = self.request.user
        
        serializer.save(
            created_by=user,
            user=user,  # Always set to current user
        )
    
    def perform_update(self, serializer):
        """Set updated_by on time log update."""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def start_timer(self, request):
        """Start a new timer for a work item."""
        from django.utils import timezone
        
        story_id = request.data.get('story')
        task_id = request.data.get('task')
        bug_id = request.data.get('bug')
        issue_id = request.data.get('issue')
        description = request.data.get('description', '')
        
        if not any([story_id, task_id, bug_id, issue_id]):
            return Response(
                {'error': 'At least one work item (story, task, bug, or issue) must be specified.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already has an active timer
        active_timer = TimeLog.objects.filter(
            user=request.user,
            end_time__isnull=True
        ).first()
        
        if active_timer:
            return Response(
                {'error': 'You already have an active timer. Please stop it first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new time log
        time_log_data = {
            'user': request.user.id,
            'start_time': timezone.now(),
            'description': description,
            'created_by': request.user.id,
        }
        
        if story_id:
            time_log_data['story'] = story_id
        if task_id:
            time_log_data['task'] = task_id
        if bug_id:
            time_log_data['bug'] = bug_id
        if issue_id:
            time_log_data['issue'] = issue_id
        
        serializer = self.get_serializer(data=time_log_data)
        serializer.is_valid(raise_exception=True)
        time_log = serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def stop_timer(self, request, pk=None):
        """Stop an active timer."""
        from django.utils import timezone
        
        time_log = self.get_object()
        
        if time_log.end_time:
            return Response(
                {'error': 'This timer is already stopped.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if time_log.user != request.user:
            return Response(
                {'error': 'You can only stop your own timers.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        time_log.end_time = timezone.now()
        time_log.updated_by = request.user
        time_log.save()
        
        serializer = self.get_serializer(time_log)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_timer(self, request):
        """Get the current user's active timer."""
        active_timer = TimeLog.objects.filter(
            user=request.user,
            end_time__isnull=True
        ).first()
        
        if not active_timer:
            return Response({'active_timer': None})
        
        serializer = self.get_serializer(active_timer)
        return Response({'active_timer': serializer.data})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get time log summary for the current user."""
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta
        
        user = request.user
        project_id = request.query_params.get('project', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        queryset = TimeLog.objects.filter(user=user)
        
        # Filter by project if provided
        if project_id:
            queryset = queryset.filter(
                models.Q(story__project_id=project_id) |
                models.Q(task__story__project_id=project_id) |
                models.Q(bug__project_id=project_id) |
                models.Q(issue__project_id=project_id)
            )
        
        # Filter by date range
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)
        
        # Calculate totals
        total_minutes = queryset.aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0
        
        total_hours = round(total_minutes / 60, 2)
        
        # Count entries
        total_entries = queryset.count()
        
        # Billable vs non-billable
        billable_minutes = queryset.filter(is_billable=True).aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0
        billable_hours = round(billable_minutes / 60, 2)
        
        return Response({
            'total_hours': total_hours,
            'total_minutes': total_minutes,
            'total_entries': total_entries,
            'billable_hours': billable_hours,
            'billable_minutes': billable_minutes,
            'non_billable_hours': round((total_minutes - billable_minutes) / 60, 2),
        })


class ProjectConfigurationViewSet(viewsets.ModelViewSet):
    """
    Project configuration management ViewSet.
    
    Access Control:
    - Only project owners and admins can modify configurations.
    - Project members can view configurations.
    """
    
    serializer_class = ProjectConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter configurations to only show those from projects where user is member/owner."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return ProjectConfiguration.objects.none()
        
        # Admins can see all configurations
        if user.role == 'admin':
            return ProjectConfiguration.objects.all().select_related('project', 'project__owner', 'updated_by').prefetch_related('project__members')
        
        # Regular users can only see configurations from projects they own or are members of
        return ProjectConfiguration.objects.filter(
            models.Q(project__owner=user) | models.Q(project__members__id=user.id)
        ).distinct().select_related('project', 'project__owner', 'updated_by').prefetch_related('project__members')
    
    def get_permissions(self):
        """Override to check if user can modify configuration."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only project owners and admins can modify
            return [permissions.IsAuthenticated(), IsProjectOwner()]
        return [permissions.IsAuthenticated()]
    
    def get_object(self):
        """Get configuration by project ID instead of configuration ID. Creates it if it doesn't exist."""
        project_id = self.kwargs.get('pk')
        
        # Get or create configuration
        try:
            config = ProjectConfiguration.objects.get(project_id=project_id)
        except ProjectConfiguration.DoesNotExist:
            # Configuration doesn't exist - create it
            try:
                from apps.projects.models import Project
                project = Project.objects.get(pk=project_id)
                
                # Check permissions before creating
                user = self.request.user
                if user.role != 'admin' and project.owner != user and user not in project.members.all():
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied("You don't have access to this project's configuration.")
                
                # Create configuration
                config = ProjectConfiguration.objects.create(project=project)
                config.initialize_defaults()
                config.save()
            except Project.DoesNotExist:
                from rest_framework.exceptions import NotFound
                raise NotFound("Project not found.")
        
        # Check permissions
        project = config.project
        user = self.request.user
        
        if user.role != 'admin' and project.owner != user and user not in project.members.all():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have access to this project's configuration.")
        
        return config
    
    def perform_create(self, serializer):
        """Set updated_by when creating."""
        serializer.save(updated_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by when updating."""
        serializer.save(updated_by=self.request.user)
    
    @extend_schema(
        description="Get configuration by project ID",
        responses={200: ProjectConfigurationSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve configuration by project ID."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        description="Reset configuration to defaults",
        responses={200: ProjectConfigurationSerializer}
    )
    @action(detail=True, methods=['post'], url_path='reset-to-defaults')
    def reset_to_defaults(self, request, pk=None):
        """Reset configuration to default values."""
        config = self.get_object()
        
        # Check if user is project owner or admin
        if request.user.role != 'admin' and config.project.owner != request.user:
            return Response(
                {'error': 'Only project owners and admins can reset configuration.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Initialize defaults
        config.initialize_defaults()
        config.updated_by = request.user
        config.save()
        
        return Response(
            ProjectConfigurationSerializer(config).data,
            status=status.HTTP_200_OK
        )


class MentionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing mentions.
    Users can only see their own mentions.
    """
    serializer_class = MentionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Mention.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """Return mentions for the current user."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Mention.objects.none()
        
        user = self.request.user
        if not user or not user.is_authenticated:
            return Mention.objects.none()
        
        queryset = Mention.objects.filter(mentioned_user=user)
        
        # Filter by read status
        read_status = self.request.query_params.get('read', None)
        if read_status is not None:
            read_status = read_status.lower() == 'true'
            queryset = queryset.filter(read=read_status)
        
        # Filter by story
        story_id = self.request.query_params.get('story', None)
        if story_id:
            queryset = queryset.filter(story_id=story_id)
        
        return queryset.order_by('-created_at')
    
    @extend_schema(
        description="Mark a mention as read",
        responses={200: MentionSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a mention as read."""
        mention = self.get_object()
        mention.mark_as_read()
        serializer = self.get_serializer(mention)
        return Response(serializer.data)
    
    @extend_schema(
        description="Mark all mentions as read",
        responses={200: {'type': 'object', 'properties': {'count': {'type': 'integer'}}}}
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all mentions for the current user as read."""
        from django.utils import timezone
        count = Mention.objects.filter(
            mentioned_user=request.user,
            read=False
        ).update(read=True, read_at=timezone.now())
        return Response({'count': count})


class StoryCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for story comments with threading support.
    """
    serializer_class = StoryCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Return comments for a story."""
        story_id = self.request.query_params.get('story', None)
        if not story_id:
            return StoryComment.objects.none()
        
        queryset = StoryComment.objects.filter(
            story_id=story_id,
            deleted=False
        )
        
        # Filter by parent for threading
        parent_id = self.request.query_params.get('parent', None)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        else:
            # Top-level comments only
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset.order_by('created_at')
    
    def perform_create(self, serializer):
        """Set author to current user and check permissions."""
        story = serializer.validated_data.get('story')
        if story and story.project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(story.project)
            has_perm, error = perm_service.can_add_comment(self.request.user)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to add comments")
        serializer.save(author=self.request.user)
    
    @extend_schema(
        description="Add a reaction to a comment",
        request={'type': 'object', 'properties': {'emoji': {'type': 'string'}}},
        responses={200: StoryCommentSerializer}
    )
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add or remove a reaction to a comment."""
        comment = self.get_object()
        emoji = request.data.get('emoji', '')
        user_id = str(request.user.id)
        
        if not emoji:
            return Response(
                {'error': 'emoji is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reactions = comment.reactions or {}
        emoji_reactions = reactions.get(emoji, [])
        
        if user_id in emoji_reactions:
            # Remove reaction
            emoji_reactions.remove(user_id)
        else:
            # Add reaction
            emoji_reactions.append(user_id)
        
        if emoji_reactions:
            reactions[emoji] = emoji_reactions
        else:
            reactions.pop(emoji, None)
        
        comment.reactions = reactions
        comment.save()
        
        serializer = self.get_serializer(comment)
        return Response(serializer.data)


class StoryDependencyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for story dependencies.
    """
    serializer_class = StoryDependencySerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Return dependencies for stories in accessible projects."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return StoryDependency.objects.none()
        
        # Filter by story if provided
        story_id = self.request.query_params.get('story', None)
        if story_id:
            queryset = StoryDependency.objects.filter(
                models.Q(source_story_id=story_id) | models.Q(target_story_id=story_id)
            )
        else:
            queryset = StoryDependency.objects.all()
        
        # Filter by project access
        if user.role != 'admin':
            queryset = queryset.filter(
                models.Q(source_story__project__owner=user) | 
                models.Q(source_story__project__members__id=user.id) |
                models.Q(target_story__project__owner=user) | 
                models.Q(target_story__project__members__id=user.id)
            ).distinct()
        
        return queryset.select_related(
            'source_story', 'target_story', 'source_story__project', 
            'target_story__project', 'resolved_by'
        )
    
    def perform_create(self, serializer):
        """Set created_by when creating and check permissions."""
        source_story = serializer.validated_data.get('source_story')
        if source_story and source_story.project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(source_story.project)
            has_perm, error = perm_service.can_manage_dependencies(self.request.user)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to manage dependencies")
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by and handle resolution."""
        instance = serializer.save(updated_by=self.request.user)
        
        # If marking as resolved, set resolved_by and resolved_at
        if 'resolved' in serializer.validated_data and serializer.validated_data['resolved']:
            if not instance.resolved:
                from django.utils import timezone
                instance.resolved = True
                instance.resolved_at = timezone.now()
                instance.resolved_by = self.request.user
                instance.save()
    
    @extend_schema(
        description="Check for circular dependencies",
        responses={200: {'type': 'object', 'properties': {'has_circular': {'type': 'boolean'}}}}
    )
    @action(detail=False, methods=['post'])
    def check_circular(self, request):
        """Check if adding a dependency would create a circular dependency."""
        source_story_id = request.data.get('source_story')
        target_story_id = request.data.get('target_story')
        
        if not source_story_id or not target_story_id:
            return Response(
                {'error': 'source_story and target_story are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if target_story already depends on source_story (directly or indirectly)
        has_circular = self._check_circular_dependency(source_story_id, target_story_id)
        
        return Response({'has_circular': has_circular})
    
    def _check_circular_dependency(self, source_id, target_id):
        """Recursively check for circular dependencies."""
        if source_id == target_id:
            return True
        
        # Get all stories that target_story depends on
        dependencies = StoryDependency.objects.filter(
            source_story_id=target_id,
            resolved=False
        ).select_related('target_story')
        
        for dep in dependencies:
            if dep.target_story_id == source_id:
                return True
            # Recursively check
            if self._check_circular_dependency(source_id, dep.target_story_id):
                return True
        
        return False


class StoryAttachmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for story attachments.
    """
    serializer_class = StoryAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Return attachments for stories in accessible projects."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return StoryAttachment.objects.none()
        
        # Filter by story if provided
        story_id = self.request.query_params.get('story', None)
        if story_id:
            queryset = StoryAttachment.objects.filter(story_id=story_id)
        else:
            queryset = StoryAttachment.objects.all()
        
        # Filter by project access
        if user.role != 'admin':
            queryset = queryset.filter(
                models.Q(story__project__owner=user) | 
                models.Q(story__project__members__id=user.id)
            ).distinct()
        
        return queryset.select_related('story', 'story__project', 'uploaded_by')
    
    def get_serializer_context(self):
        """Add request to serializer context for file URLs."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        """Set uploaded_by and file metadata when creating and check permissions."""
        story = serializer.validated_data.get('story')
        if story and story.project:
            from apps.projects.services.permissions import get_permission_service
            perm_service = get_permission_service(story.project)
            has_perm, error = perm_service.can_add_attachment(self.request.user)
            if not has_perm:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(error or "You don't have permission to add attachments")
        
        file = serializer.validated_data.get('file')
        if file:
            serializer.save(
                uploaded_by=self.request.user,
                file_name=file.name,
                file_size=file.size,
                file_type=file.content_type or 'application/octet-stream'
            )
        else:
            serializer.save(uploaded_by=self.request.user)
    
    @extend_schema(
        description="Download attachment file",
        responses={200: {'type': 'file'}}
    )
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download the attachment file."""
        attachment = self.get_object()
        
        if not attachment.file:
            return Response(
                {'error': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from django.http import FileResponse
        
        response = FileResponse(
            attachment.file.open('rb'),
            content_type=attachment.file_type
        )
        response['Content-Disposition'] = f'attachment; filename="{attachment.file_name}"'
        return response


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user notifications.
    
    Users can only see their own notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return notifications for the current user only."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return Notification.objects.none()
        
        queryset = Notification.objects.filter(recipient=user)
        
        # Filter by read status if provided
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        # Filter by notification type if provided
        notification_type = self.request.query_params.get('type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter by project if provided
        project_id = self.request.query_params.get('project', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.select_related(
            'recipient', 'project', 'story', 'comment', 'mention', 'created_by'
        )
    
    @extend_schema(
        description="Mark notification as read",
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @extend_schema(
        description="Mark all notifications as read",
        responses={200: {'type': 'object', 'properties': {'count': {'type': 'integer'}}}}
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all unread notifications as read."""
        user = request.user
        count = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'count': count})
    
    @extend_schema(
        description="Get unread notification count",
        responses={200: {'type': 'object', 'properties': {'count': {'type': 'integer'}}}}
    )
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        user = request.user
        count = Notification.objects.filter(
            recipient=user,
            is_read=False
        ).count()
        return Response({'count': count})


class WatcherViewSet(viewsets.ModelViewSet):
    """
    Watcher management ViewSet.

    Allows users to subscribe to (watch) and unsubscribe from (unwatch) various
    content objects (e.g., UserStories, Tasks, Bugs, Issues, Epics, Projects).
    """
    serializer_class = WatcherSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    queryset = Watcher.objects.none()  # Default queryset for schema generation

    def get_queryset(self):
        """
        Filter watchers to only show those related to projects where the user is owner or member,
        or watchers created by the user.
        Admins can see all watchers.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Watcher.objects.none()

        user = self.request.user
        if not user or not user.is_authenticated:
            return Watcher.objects.none()

        if user.role == 'admin':
            return Watcher.objects.all().select_related('user', 'content_type')

        # Get projects the user is a member of
        accessible_projects = Project.objects.filter(
            Q(owner=user) | Q(members__id=user.id)
        ).values_list('id', flat=True)

        # Filter watchers related to accessible projects or created by the user
        return Watcher.objects.filter(
            Q(user=user) |
            Q(content_type__model='project', object_id__in=accessible_projects) |
            Q(content_type__model='userstory', userstory__project__id__in=accessible_projects) |
            Q(content_type__model='task', task__story__project__id__in=accessible_projects) |
            Q(content_type__model='bug', bug__project__id__in=accessible_projects) |
            Q(content_type__model='issue', issue__project__id__in=accessible_projects) |
            Q(content_type__model='epic', epic__project__id__in=accessible_projects)
        ).distinct().select_related('user', 'content_type')

    def perform_create(self, serializer):
        """Set created_by on watcher creation."""
        serializer.save(user=self.request.user)

    @extend_schema(
        description="Start watching a content object",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'content_type_app': {'type': 'string'},
                    'content_type_model': {'type': 'string'},
                    'object_id': {'type': 'string', 'format': 'uuid'},
                },
                'required': ['content_type_app', 'content_type_model', 'object_id']
            }
        },
        responses={201: WatcherSerializer, 200: WatcherSerializer}
    )
    @action(detail=False, methods=['post'], url_path='watch')
    def watch(self, request):
        """
        Start watching a content object.
        Requires 'content_type_app', 'content_type_model', and 'object_id' in request data.
        """
        from django.contrib.contenttypes.models import ContentType
        from rest_framework.exceptions import ValidationError
        
        user = request.user
        app_label = request.data.get('content_type_app')
        model_name = request.data.get('content_type_model')
        object_id = request.data.get('object_id')

        if not all([app_label, model_name, object_id]):
            raise ValidationError("content_type_app, content_type_model, and object_id are required.")

        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        except ContentType.DoesNotExist:
            raise ValidationError(f"Content type {app_label}.{model_name} not found.")

        # Check if the object exists and user has permission to view it
        try:
            model_class = content_type.model_class()
            if not model_class:
                raise ValidationError(f"Model class not found for {app_label}.{model_name}.")
            content_object = model_class.objects.get(pk=object_id)
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            # Handle DoesNotExist or other exceptions
            from django.core.exceptions import ObjectDoesNotExist
            if isinstance(e, ObjectDoesNotExist):
                raise ValidationError(f"Object with ID {object_id} not found for model {model_name}.")
            raise ValidationError(f"Error accessing object: {str(e)}")

            # Check project-level permissions for the content object
            project = None
            if hasattr(content_object, 'project'):
                project = content_object.project
            elif hasattr(content_object, 'story') and hasattr(content_object.story, 'project'):
                project = content_object.story.project

            if project:
                # Check permissions - user must be owner, member, or admin
                if user.role != 'admin':
                    if project.owner != user and not project.members.filter(id=user.id).exists():
                        return Response(
                            {'error': 'You do not have permission to watch objects in this project.'},
                            status=status.HTTP_403_FORBIDDEN
                        )
        else:
            # For non-project related objects, ensure user has general access or is admin
            if user.role != 'admin' and hasattr(content_object, 'created_by') and content_object.created_by != user:
                return Response(
                    {'error': 'You do not have permission to watch this object.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        watcher, created = Watcher.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=object_id,
            defaults={}
        )

        if not created:
            return Response({'message': 'Already watching this object.'}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(watcher)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Stop watching a content object",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'content_type_app': {'type': 'string'},
                    'content_type_model': {'type': 'string'},
                    'object_id': {'type': 'string', 'format': 'uuid'},
                },
                'required': ['content_type_app', 'content_type_model', 'object_id']
            }
        },
        responses={204: None, 200: {'type': 'object'}}
    )
    @action(detail=False, methods=['post'], url_path='unwatch')
    def unwatch(self, request):
        """
        Stop watching a content object.
        Requires 'content_type_app', 'content_type_model', and 'object_id' in request data.
        """
        from django.contrib.contenttypes.models import ContentType
        from rest_framework.exceptions import ValidationError
        
        user = request.user
        app_label = request.data.get('content_type_app')
        model_name = request.data.get('content_type_model')
        object_id = request.data.get('object_id')

        if not all([app_label, model_name, object_id]):
            raise ValidationError("content_type_app, content_type_model, and object_id are required.")

        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        except ContentType.DoesNotExist:
            raise ValidationError(f"Content type {app_label}.{model_name} not found.")

        try:
            watcher = Watcher.objects.get(
                user=user,
                content_type=content_type,
                object_id=object_id
            )
            watcher.delete()
            return Response({'message': 'Successfully un-watched object.'}, status=status.HTTP_204_NO_CONTENT)
        except Watcher.DoesNotExist:
            return Response({'message': 'Not currently watching this object.'}, status=status.HTTP_200_OK)


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for activity feed.
    
    Provides read-only access to activity logs with comprehensive filtering.
    Users can only see activities for projects they have access to.
    """
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    queryset = Activity.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """
        Filter activities to only show those related to projects where the user is owner or member.
        Admins can see all activities.
        Supports filtering by:
        - project: Filter by project ID
        - activity_type: Filter by activity type
        - user: Filter by user ID (who performed the activity)
        - content_type: Filter by content type (e.g., 'userstory', 'task', 'bug')
        - object_id: Filter by specific object ID
        - date_from: Filter activities from this date (YYYY-MM-DD)
        - date_to: Filter activities to this date (YYYY-MM-DD)
        """
        if getattr(self, 'swagger_fake_view', False):
            return Activity.objects.none()
        
        user = self.request.user
        if not user or not user.is_authenticated:
            return Activity.objects.none()
        
        # Base queryset - filter by project access
        if user.role == 'admin':
            queryset = Activity.objects.all()
        else:
            # Get projects the user is a member of
            accessible_projects = Project.objects.filter(
                Q(owner=user) | Q(members__id=user.id)
            ).values_list('id', flat=True)
            
            queryset = Activity.objects.filter(
                Q(project_id__in=accessible_projects) | Q(project__isnull=True)
            )
        
        # Filter by project
        project_id = self.request.query_params.get('project', None)
        if project_id:
            try:
                queryset = queryset.filter(project_id=project_id)
            except (ValueError, TypeError):
                # Invalid UUID
                queryset = queryset.none()
        
        # Filter by activity type
        activity_type = self.request.query_params.get('activity_type', None)
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Filter by user (who performed the activity)
        user_id = self.request.query_params.get('user', None)
        if user_id:
            try:
                queryset = queryset.filter(user_id=user_id)
            except (ValueError, TypeError):
                queryset = queryset.none()
        
        # Filter by content type
        content_type = self.request.query_params.get('content_type', None)
        if content_type:
            from django.contrib.contenttypes.models import ContentType
            try:
                ct = ContentType.objects.get(model=content_type.lower())
                queryset = queryset.filter(content_type=ct)
            except ContentType.DoesNotExist:
                queryset = queryset.none()
        
        # Filter by object ID
        object_id = self.request.query_params.get('object_id', None)
        if object_id:
            try:
                queryset = queryset.filter(object_id=object_id)
            except (ValueError, TypeError):
                queryset = queryset.none()
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from_obj)
            except ValueError:
                pass  # Invalid date format, ignore
        
        date_to = self.request.query_params.get('date_to', None)
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to_obj)
            except ValueError:
                pass  # Invalid date format, ignore
        
        return queryset.select_related(
            'user', 'project', 'content_type'
        ).order_by('-created_at')


class EditHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for edit history.
    
    Provides read-only access to edit history with version comparison.
    Users can only see edit history for objects in projects they have access to.
    """
    serializer_class = EditHistorySerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    queryset = EditHistory.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """
        Filter edit history to only show those related to projects where the user is owner or member.
        Admins can see all edit history.
        Supports filtering by:
        - project: Filter by project ID
        - content_type: Filter by content type (e.g., 'userstory', 'task', 'bug')
        - object_id: Filter by specific object ID
        - user: Filter by user ID (who made the edit)
        - version: Filter by specific version number
        """
        if getattr(self, 'swagger_fake_view', False):
            return EditHistory.objects.none()
        
        user = self.request.user
        if not user or not user.is_authenticated:
            return EditHistory.objects.none()
        
        # Base queryset - filter by project access
        if user.role == 'admin':
            queryset = EditHistory.objects.all()
        else:
            # Get projects the user is a member of
            accessible_projects = Project.objects.filter(
                Q(owner=user) | Q(members__id=user.id)
            ).values_list('id', flat=True)
            
            queryset = EditHistory.objects.filter(
                Q(project_id__in=accessible_projects) | Q(project__isnull=True)
            )
        
        # Filter by project
        project_id = self.request.query_params.get('project', None)
        if project_id:
            try:
                queryset = queryset.filter(project_id=project_id)
            except (ValueError, TypeError):
                queryset = queryset.none()
        
        # Filter by content type
        content_type = self.request.query_params.get('content_type', None)
        if content_type:
            from django.contrib.contenttypes.models import ContentType
            try:
                ct = ContentType.objects.get(model=content_type.lower())
                queryset = queryset.filter(content_type=ct)
            except ContentType.DoesNotExist:
                queryset = queryset.none()
        
        # Filter by object ID
        object_id = self.request.query_params.get('object_id', None)
        if object_id:
            try:
                queryset = queryset.filter(object_id=object_id)
            except (ValueError, TypeError):
                queryset = queryset.none()
        
        # Filter by user
        user_id = self.request.query_params.get('user', None)
        if user_id:
            try:
                queryset = queryset.filter(user_id=user_id)
            except (ValueError, TypeError):
                queryset = queryset.none()
        
        # Filter by version
        version = self.request.query_params.get('version', None)
        if version:
            try:
                queryset = queryset.filter(version=int(version))
            except (ValueError, TypeError):
                queryset = queryset.none()
        
        return queryset.select_related(
            'user', 'project', 'content_type'
        ).order_by('-version', '-created_at')
    
    @extend_schema(
        description="Compare two versions of an object",
        parameters=[
            {
                'name': 'version1',
                'in': 'query',
                'required': True,
                'schema': {'type': 'integer'},
                'description': 'First version number'
            },
            {
                'name': 'version2',
                'in': 'query',
                'required': True,
                'schema': {'type': 'integer'},
                'description': 'Second version number'
            },
        ],
        responses={200: EditHistorySerializer}
    )
    @action(detail=False, methods=['get'], url_path='compare')
    def compare_versions(self, request):
        """
        Compare two versions of an object.
        Requires content_type and object_id query parameters, plus version1 and version2.
        """
        from apps.projects.services.edit_history import EditHistoryService
        from django.contrib.contenttypes.models import ContentType
        
        content_type_name = request.query_params.get('content_type', None)
        object_id = request.query_params.get('object_id', None)
        version1 = request.query_params.get('version1', None)
        version2 = request.query_params.get('version2', None)
        
        if not all([content_type_name, object_id, version1, version2]):
            return Response(
                {'error': 'content_type, object_id, version1, and version2 are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ct = ContentType.objects.get(model=content_type_name.lower())
            model_class = ct.model_class()
            obj = model_class.objects.get(pk=object_id)
            
            # Check permissions
            project = None
            if hasattr(obj, 'project'):
                project = obj.project
            elif hasattr(obj, 'story') and hasattr(obj.story, 'project'):
                project = obj.story.project
            
            if project:
                # Check permissions - user must be owner, member, or admin
                user = request.user
                if user.role != 'admin':
                    if project.owner != user and not project.members.filter(id=user.id).exists():
                        return Response(
                            {'error': 'You do not have permission to view this object.'},
                            status=status.HTTP_403_FORBIDDEN
                        )
            
            from apps.projects.services.edit_history import EditHistoryService
            comparison = EditHistoryService.compare_versions(obj, int(version1), int(version2))
            
            return Response({
                'version1': EditHistorySerializer(comparison['version1']).data if comparison['version1'] else None,
                'version2': EditHistorySerializer(comparison['version2']).data if comparison['version2'] else None,
                'differences': comparison['differences']
            })
        except ContentType.DoesNotExist:
            return Response(
                {'error': f'Content type {content_type_name} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SearchViewSet(viewsets.ViewSet):
    """
    Advanced search ViewSet.
    
    Provides unified search across multiple content types with operators and filters.
    """
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    @extend_schema(
        description="Perform advanced search across multiple content types",
        parameters=[
            {
                'name': 'q',
                'in': 'query',
                'required': True,
                'schema': {'type': 'string'},
                'description': 'Search query (supports operators: AND, OR, NOT, quotes, field:value)'
            },
            {
                'name': 'content_types',
                'in': 'query',
                'required': False,
                'schema': {'type': 'array', 'items': {'type': 'string'}},
                'description': 'Content types to search (e.g., userstory,task,bug)'
            },
            {
                'name': 'project',
                'in': 'query',
                'required': False,
                'schema': {'type': 'string', 'format': 'uuid'},
                'description': 'Project ID to limit search to'
            },
            {
                'name': 'status',
                'in': 'query',
                'required': False,
                'schema': {'type': 'string'},
                'description': 'Filter by status'
            },
            {
                'name': 'limit',
                'in': 'query',
                'required': False,
                'schema': {'type': 'integer'},
                'description': 'Limit results per content type'
            },
        ],
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='')
    def search(self, request):
        """
        Perform advanced search.
        
        Query examples:
        - Simple: "bug fix"
        - Quoted phrase: "critical bug"
        - Field-specific: title:bug, status:open
        - Operators: bug AND fix, bug OR issue
        - Negation: -status:closed
        """
        from apps.projects.services.search import SearchService
        
        query = request.query_params.get('q', '')
        content_types_param = request.query_params.get('content_types', '')
        project_id = request.query_params.get('project', None)
        limit = request.query_params.get('limit', None)
        
        # Parse content types
        content_types = None
        if content_types_param:
            content_types = [ct.strip() for ct in content_types_param.split(',') if ct.strip()]
        
        # Get project if specified
        project = None
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
                # Check permissions - user must be owner, member, or admin
                user = request.user
                if user.role != 'admin':
                    if project.owner != user and not project.members.filter(id=user.id).exists():
                        return Response(
                            {'error': 'You do not have permission to search in this project.'},
                            status=status.HTTP_403_FORBIDDEN
                        )
            except (Project.DoesNotExist, ValueError):
                return Response(
                    {'error': 'Invalid project ID.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Parse additional filters
        filters = {}
        status_filter = request.query_params.get('status', None)
        if status_filter:
            filters['status'] = status_filter
        
        # Perform search
        results = SearchService.search(
            query=query,
            content_types=content_types,
            filters=filters,
            project=project,
            user=request.user,
            limit=int(limit) if limit else None
        )
        
        return Response({
            'query': query,
            'results': results,
            'total_count': sum(len(items) for items in results.values())
        })
    
    @extend_schema(
        description="Perform unified search (single sorted list)",
        parameters=[
            {
                'name': 'q',
                'in': 'query',
                'required': True,
                'schema': {'type': 'string'},
                'description': 'Search query'
            },
            {
                'name': 'content_types',
                'in': 'query',
                'required': False,
                'schema': {'type': 'array', 'items': {'type': 'string'}},
                'description': 'Content types to search'
            },
            {
                'name': 'project',
                'in': 'query',
                'required': False,
                'schema': {'type': 'string', 'format': 'uuid'},
                'description': 'Project ID to limit search to'
            },
            {
                'name': 'limit',
                'in': 'query',
                'required': False,
                'schema': {'type': 'integer'},
                'description': 'Total limit on results'
            },
        ],
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='unified')
    def unified_search(self, request):
        """Perform unified search returning a single sorted list."""
        from apps.projects.services.search import SearchService
        
        query = request.query_params.get('q', '')
        content_types_param = request.query_params.get('content_types', '')
        project_id = request.query_params.get('project', None)
        limit = request.query_params.get('limit', None)
        
        # Parse content types
        content_types = None
        if content_types_param:
            content_types = [ct.strip() for ct in content_types_param.split(',') if ct.strip()]
        
        # Get project if specified
        project = None
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
                # Check permissions - user must be owner, member, or admin
                user = request.user
                if user.role != 'admin':
                    if project.owner != user and not project.members.filter(id=user.id).exists():
                        return Response(
                            {'error': 'You do not have permission to search in this project.'},
                            status=status.HTTP_403_FORBIDDEN
                        )
            except (Project.DoesNotExist, ValueError):
                return Response(
                    {'error': 'Invalid project ID.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Perform unified search
        try:
            results = SearchService.search_unified(
                query=query,
                content_types=content_types,
                project=project,
                user=request.user,
                limit=int(limit) if limit else None
            )
            
            return Response({
                'query': query,
                'results': results,
                'total_count': len(results)
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Search failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SavedSearchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing saved searches.
    
    Users can save frequently used search queries for quick access.
    """
    serializer_class = SavedSearchSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = SavedSearch.objects.none()  # Default queryset for schema generation
    
    def get_queryset(self):
        """Return saved searches for the current user only."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return SavedSearch.objects.none()
        
        queryset = SavedSearch.objects.filter(user=user)
        
        # Filter by project if provided
        project_id = self.request.query_params.get('project', None)
        if project_id:
            try:
                queryset = queryset.filter(project_id=project_id)
            except (ValueError, TypeError):
                queryset = queryset.none()
        
        return queryset.select_related('user', 'project').order_by('-last_used_at', '-created_at')
    
    def perform_create(self, serializer):
        """Set user on saved search creation and handle duplicate names."""
        user = self.request.user
        name = serializer.validated_data.get('name')
        
        # Check if a saved search with the same name already exists for this user
        existing_search = SavedSearch.objects.filter(user=user, name=name).first()
        if existing_search:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'name': [f'A saved search with the name "{name}" already exists. Please choose a different name.']
            })
        
        serializer.save(user=user)
    
    @extend_schema(
        description="Execute a saved search",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a saved search and mark it as used."""
        from apps.projects.services.search import SearchService
        
        saved_search = self.get_object()
        
        # Mark as used
        saved_search.mark_used()
        
        # Execute the search
        results = SearchService.search_unified(
            query=saved_search.query,
            content_types=saved_search.content_types if saved_search.content_types else None,
            filters=saved_search.filters if saved_search.filters else {},
            project=saved_search.project,
            user=request.user
        )
        
        return Response({
            'saved_search': SavedSearchSerializer(saved_search).data,
            'results': results,
            'total_count': len(results)
        })


class StatusChangeApprovalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing status change approval requests.
    
    When require_approval_for_status_change is enabled in project configuration,
    status changes must be approved before being applied.
    """
    serializer_class = StatusChangeApprovalSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    queryset = StatusChangeApproval.objects.none()  # Default for schema generation
    
    def get_queryset(self):
        """Filter approvals based on user's role and project membership."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return StatusChangeApproval.objects.none()
        
        queryset = StatusChangeApproval.objects.select_related(
            'requested_by', 'approver', 'approved_by', 'project', 'content_type'
        )
        
        # Filter by project if provided
        project_id = self.request.query_params.get('project', None)
        if project_id:
            try:
                queryset = queryset.filter(project_id=project_id)
            except (ValueError, TypeError):
                queryset = queryset.none()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Users can see:
        # 1. Approvals they requested
        # 2. Approvals they need to approve (as approver)
        # 3. All approvals if they're project owner or admin
        if user.is_staff or user.is_superuser:
            # Admins see all
            pass
        else:
            # Regular users see their own requests and requests they need to approve
            queryset = queryset.filter(
                Q(requested_by=user) | Q(approver=user) | Q(project__owner=user)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create an approval request."""
        from django.contrib.contenttypes.models import ContentType
        
        # Get work item from request data
        work_item_type = self.request.data.get('work_item_type')  # 'userstory', 'task', 'bug', 'issue'
        work_item_id = self.request.data.get('work_item_id')
        
        if not work_item_type or not work_item_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'work_item_type': ['This field is required.'],
                'work_item_id': ['This field is required.']
            })
        
        # Map work item type to model
        model_map = {
            'userstory': UserStory,
            'task': Task,
            'bug': Bug,
            'issue': Issue,
        }
        
        model_class = model_map.get(work_item_type.lower())
        if not model_class:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'work_item_type': [f'Invalid work item type: {work_item_type}']
            })
        
        # Get work item
        try:
            work_item = model_class.objects.get(id=work_item_id)
        except model_class.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(f'{work_item_type} with id {work_item_id} not found')
        
        # Get project from work item
        project = work_item.project
        
        # Check if approval is required
        try:
            config = project.configuration
            if not config or not config.permission_settings.get('require_approval_for_status_change', False):
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'error': ['Approval workflow is not enabled for this project.']
                })
        except ProjectConfiguration.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': ['Project configuration not found.']
            })
        
        # Determine approver (default to project owner, can be overridden)
        approver = project.owner
        if 'approver' in serializer.validated_data and serializer.validated_data['approver']:
            approver = serializer.validated_data['approver']
        
        # Get content type
        content_type = ContentType.objects.get_for_model(model_class)
        
        # Save approval request
        serializer.save(
            requested_by=self.request.user,
            approver=approver,
            project=project,
            content_type=content_type,
            object_id=work_item_id
        )
    
    @extend_schema(
        description="Approve a status change request",
        request=None,
        responses={200: StatusChangeApprovalSerializer}
    )
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a status change request."""
        approval = self.get_object()
        
        if approval.status != 'pending':
            return Response(
                {'error': 'Only pending approvals can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is the approver or project owner/admin
        if approval.approver != request.user and approval.project.owner != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to approve this request.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        comment = request.data.get('comment', '')
        approval.approve(request.user, comment)
        
        serializer = self.get_serializer(approval)
        return Response(serializer.data)
    
    @extend_schema(
        description="Reject a status change request",
        request={'type': 'object', 'properties': {'reason': {'type': 'string'}}},
        responses={200: StatusChangeApprovalSerializer}
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a status change request."""
        approval = self.get_object()
        
        if approval.status != 'pending':
            return Response(
                {'error': 'Only pending approvals can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is the approver or project owner/admin
        if approval.approver != request.user and approval.project.owner != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You do not have permission to reject this request.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reason = request.data.get('reason', '')
        if not reason:
            return Response(
                {'error': 'Rejection reason is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval.reject(request.user, reason)
        
        serializer = self.get_serializer(approval)
        return Response(serializer.data)
    
    @extend_schema(
        description="Cancel a status change request",
        request=None,
        responses={200: StatusChangeApprovalSerializer}
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a status change request (only by requester)."""
        approval = self.get_object()
        
        if approval.status != 'pending':
            return Response(
                {'error': 'Only pending approvals can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Only the requester can cancel
        if approval.requested_by != request.user:
            return Response(
                {'error': 'Only the requester can cancel this request.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        approval.cancel()
        
        serializer = self.get_serializer(approval)
        return Response(serializer.data)
