"""
Project Management API Views

API endpoints for AI-powered project management features.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.http import Http404
import asyncio
import json

from apps.projects.models import (
    Project, Sprint, UserStory, Epic, Task, Bug, Issue, TimeLog, ProjectConfiguration, 
    Mention, StoryComment, StoryDependency, StoryAttachment, Notification, Watcher, Activity, EditHistory, SavedSearch,
    StatusChangeApproval, ProjectLabelPreset, Milestone, TicketReference, StoryLink, CardTemplate, BoardTemplate,
    SearchHistory, FilterPreset, TimeBudget, OvertimeRecord, CardCoverImage, CardChecklist, CardVote,
    StoryArchive, StoryVersion, Webhook, StoryClone, ProjectMember, GeneratedProject, ProjectFile, RepositoryExport
)
# Alias for backward compatibility
Story = UserStory
from apps.organizations.services import OrganizationStatusService, SubscriptionService, FeatureService
from apps.core.services.roles import RoleService
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
    SavedSearchSerializer,
    ProjectLabelPresetSerializer,
    MilestoneSerializer,
    TicketReferenceSerializer,
    StoryLinkSerializer,
    CardTemplateSerializer,
    BoardTemplateSerializer,
    SearchHistorySerializer,
    FilterPresetSerializer,
    TimeBudgetSerializer,
    OvertimeRecordSerializer,
    CardCoverImageSerializer,
    CardChecklistSerializer,
    CardVoteSerializer,
    StoryArchiveSerializer,
    StoryVersionSerializer,
    WebhookSerializer,
    StoryCloneSerializer,
    GitHubIntegrationSerializer,
    JiraIntegrationSerializer,
    SlackIntegrationSerializer,
    ProjectMemberSerializer,
    GeneratedProjectSerializer,
    ProjectFileSerializer,
    RepositoryExportSerializer,
    ProjectGenerationRequestSerializer,
    GitHubExportRequestSerializer,
    GitLabExportRequestSerializer
)
from apps.projects.serializers_approval import StatusChangeApprovalSerializer
from apps.projects.services.story_generator import story_generator
from apps.projects.services.sprint_planner import sprint_planner
from apps.projects.services.estimation_engine import estimation_engine
from apps.projects.services.analytics import analytics
from apps.projects.services.reports_service import ReportsService
from apps.projects.services.enhanced_filtering import EnhancedFilteringService
from apps.projects.services.bulk_operations import BulkOperationsService
from apps.projects.services.project_generator import ProjectGenerator, ProjectGenerationError
from apps.projects.services.repository_exporter import RepositoryExporter, RepositoryExportError
from apps.workflows.services.workflow_executor import WorkflowExecutor, WorkflowExecutionError
from django.conf import settings
from pathlib import Path
import os
from apps.authentication.permissions import IsProjectMember, IsProjectMemberOrReadOnly, IsProjectOwner
from apps.core.services.roles import RoleService
from apps.organizations.models import Organization
from apps.authentication.serializers import UserSerializer


# Rate limiting for autocomplete endpoints
class AutocompleteThrottle(UserRateThrottle):
    """Throttle autocomplete endpoints to prevent abuse."""
    rate = '100/hour'  # Limit to 100 requests per hour per user


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
    
    Args:
        queryset: Django queryset to filter
        label_names: List of label names to filter by
        labels_field: Name of the JSONField containing labels
    
    Returns:
        Filtered queryset
    """
    from django.db import connection
    from django.core.exceptions import ValidationError
    import re
    
    if not label_names:
        return queryset.none()
    
    # Validate and sanitize label names
    sanitized_labels = []
    MAX_LABEL_NAME_LENGTH = 100
    LABEL_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_]+$')
    
    for label_name in label_names:
        if not isinstance(label_name, str):
            continue
        
        # Sanitize: strip whitespace and limit length
        sanitized = label_name.strip()[:MAX_LABEL_NAME_LENGTH]
        
        if not sanitized or len(sanitized) < 1:
            continue
        
        # Validate format (alphanumeric, spaces, hyphens, underscores only)
        if not LABEL_NAME_PATTERN.match(sanitized):
            continue  # Skip invalid label names
        
        sanitized_labels.append(sanitized)
    
    if not sanitized_labels:
        return queryset.none()
    
    # Database-specific filtering
    if connection.vendor == 'sqlite':
        # For SQLite, use JSON string matching (safer than icontains)
        label_filters = Q()
        for label_name in sanitized_labels:
            # Escape special JSON characters
            escaped_name = label_name.replace('"', '\\"').replace('\\', '\\\\')
            # Match JSON structure: "name":"label_name"
            label_filters |= Q(**{f'{labels_field}__icontains': f'"name":"{escaped_name}"'})
        return queryset.filter(label_filters)
    else:
        # For PostgreSQL, use JSONB containment operator
        label_filters = Q()
        for label_name in sanitized_labels:
            # Use JSONB containment: labels @> [{"name": "label_name"}]
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
        Filter projects based on user permissions and organization.
        - Super admins: See all projects across all organizations (can filter by ?organization=id)
        - Org admins: See all projects in their organization
        - Regular users: See projects where they are owner or member (within their organization)
        Supports tag filtering via ?tags=tag1,tag2 query parameter.
        Supports organization filtering via ?organization=id query parameter.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Project.objects.none()
        
        # Get organization filter from query params (if provided)
        organization_id = self.request.query_params.get('organization', None)
        
        # Super admins see everything (can filter by organization if provided)
        if RoleService.is_super_admin(user):
            queryset = Project.objects.all()
            # If organization filter is provided, apply it
            if organization_id:
                try:
                    queryset = queryset.filter(organization_id=organization_id)
                except (ValueError, TypeError):
                    # Invalid organization ID, return empty queryset
                    return Project.objects.none()
        else:
            # Get user's organizations
            user_orgs = RoleService.get_user_organizations(user)
            if not user_orgs and user.organization:
                user_orgs = [user.organization]
            
            if not user_orgs:
                # User has no organization, can't see any projects
                return Project.objects.none()
            
            # Build list of accessible organization IDs
            org_ids = [str(org.id) for org in user_orgs]
            
            # If organization filter is provided, validate it's in user's organizations
            if organization_id:
                if organization_id not in org_ids:
                    # User doesn't have access to this organization
                    return Project.objects.none()
                queryset = Project.objects.filter(organization_id=organization_id)
            else:
                # No organization filter - show projects from all user's organizations
                queryset = Project.objects.filter(organization_id__in=[org.id for org in user_orgs])
            
            # Filter by permissions within organizations
            # Org admins see all projects in their orgs
            is_org_admin = any(RoleService.is_org_admin(user, org) for org in user_orgs)
            
            if not is_org_admin:
                # Regular users see only projects where they are owner or member
                queryset = queryset.filter(
                    models.Q(owner=user) | models.Q(members__id=user.id)
                ).distinct()
        
        # Tag filtering
        tags_param = self.request.query_params.get('tags', None)
        if tags_param:
            tags_list = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
            if tags_list:
                queryset = filter_by_tags(queryset, tags_list)
        
        return queryset.select_related('owner', 'organization').prefetch_related('members')
    
    def get_object(self):
        """
        Get project instance, raising DRF's NotFound instead of Django's Http404.
        This prevents noisy ERROR-level logging when projects don't exist (expected behavior).
        Super admins can access any project directly, bypassing queryset filtering.
        """
        user = self.request.user
        
        # Super admins can access any project directly, bypassing all filters
        if user and user.is_authenticated and RoleService.is_super_admin(user):
            pk = self.kwargs.get('pk')
            try:
                # Use filter().first() to avoid DoesNotExist exception for cleaner error handling
                project = Project.objects.filter(pk=pk).first()
                if project:
                    return project
                # Project truly doesn't exist - provide clear message for super_admin
                raise NotFound(f"Project with ID '{pk}' does not exist in the database.")
            except NotFound:
                raise  # Re-raise NotFound exceptions
            except Exception:
                # Fallback for any other exceptions
                raise NotFound(f"Project with ID '{pk}' does not exist in the database.")
        
        # For non-super-admin users, use the filtered queryset
        try:
            return super().get_object()
        except Http404:
            # Project doesn't exist or user doesn't have access - return clean 404
            # Use DRF's NotFound exception instead of Django's Http404 to avoid ERROR logging
            raise NotFound("Project not found or you don't have access to it.")
    
    def perform_create(self, serializer):
        """Set the current user as the project owner and organization when creating."""
        user = self.request.user
        is_super_admin = RoleService.is_super_admin(user)
        
        # Get user's organization
        organization = RoleService.get_user_organization(user)
        if not organization:
            # Try to get from request data
            organization_id = self.request.data.get('organization')
            if organization_id:
                try:
                    from apps.organizations.models import Organization
                    organization = Organization.objects.get(pk=organization_id)
                except Organization.DoesNotExist:
                    pass
        
        if not organization:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("User must belong to an organization to create projects.")
        
        # Super admins can bypass organization status and subscription checks
        if not is_super_admin:
            # Validate organization status
            if not organization.is_active():
                from rest_framework.exceptions import ValidationError
                raise ValidationError(f'Cannot create project. Organization "{organization.name}" is {organization.get_status_display()}.')
            
            # Validate subscription
            if not organization.is_subscription_active():
                from rest_framework.exceptions import ValidationError
                raise ValidationError('Cannot create project. Organization subscription has expired.')
            
            # Validate project limit using FeatureService
            if not organization.can_add_project():
                from apps.organizations.services import FeatureService
                from rest_framework.exceptions import ValidationError
                current_count = organization.get_project_count()
                max_projects = FeatureService.get_feature_value(organization, 'projects.max_count', default=0)
                tier = organization.subscription_tier or 'trial'
                if max_projects is None or max_projects <= 0:
                    # This shouldn't happen if can_add_project is correct, but add safety check
                    pass  # Unlimited projects
                else:
                    raise ValidationError(
                        f'Cannot create project. Organization has reached the maximum number of projects ({max_projects} for {tier} tier). '
                        f'Current: {current_count}. Please upgrade your subscription to create more projects.'
                    )
            
            # Explicitly check projects.create feature availability
            from apps.organizations.services import FeatureService
            FeatureService.is_feature_available(organization, 'projects.create', user=user, raise_exception=True)
        
        serializer.save(owner=user, organization=organization)
    
    def _validate_organization_for_write(self, organization, user):
        """
        Helper method to validate organization status and subscription for write operations.
        Super admins can bypass checks.
        """
        if organization:
            OrganizationStatusService.require_active_organization(organization, user=user)
            OrganizationStatusService.require_subscription_active(organization, user=user)
    
    @staticmethod
    def _validate_project_organization_for_write(project, user):
        """
        Static helper method to validate organization status and subscription for project-based operations.
        Super admins can bypass checks.
        """
        if not project:
            return
        
        organization = project.organization if hasattr(project, 'organization') else None
        if organization:
            OrganizationStatusService.require_active_organization(organization, user=user)
            OrganizationStatusService.require_subscription_active(organization, user=user)
    
    def perform_update(self, serializer):
        """Update project with organization status and subscription validation."""
        project = serializer.instance
        user = self.request.user
        
        # Get organization from project
        organization = project.organization if project else None
        
        # Validate organization status and subscription
        self._validate_organization_for_write(organization, user)
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete project with organization status and subscription validation."""
        user = self.request.user
        
        # Get organization from project
        organization = instance.organization if instance else None
        
        # Validate organization status and subscription
        self._validate_organization_for_write(organization, user)
        
        super().perform_destroy(instance)
    
    @extend_schema(
        request=StoryGenerationRequestSerializer,
        responses={200: StorySerializer(many=True)},
        description="Generate user stories from product vision using AI"
    )
    @action(detail=True, methods=['post'], url_path='generate-stories')
    def generate_stories(self, request, pk=None):
        """Generate user stories from product vision."""
        project = self.get_object()
        
        # Validate organization status and subscription
        user = request.user
        organization = project.organization if project else None
        self._validate_organization_for_write(organization, user)
        
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
        
        # Validate organization status and subscription
        self._validate_organization_for_write(project.organization if project else None, request.user)
        
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
        
        # Validate organization status and subscription
        self._validate_organization_for_write(project.organization if project else None, request.user)
        
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
        responses={200: 'Permission details'},
        description="Get current user's permissions for this project based on permission_settings"
    )
    @action(detail=True, methods=['get'], url_path='permissions')
    def permissions(self, request, pk=None):
        """Get current user's permissions for this project."""
        from apps.projects.services.permissions import get_permission_service
        
        project = self.get_object()
        user = request.user
        
        # Get permission service
        perm_service = get_permission_service(project)
        
        # Check all permissions
        permissions = {
            # Story permissions
            'can_create_story': perm_service.can_create_story(user)[0],
            'can_edit_story': perm_service.can_edit_story(user)[0],
            'can_delete_story': perm_service.can_delete_story(user)[0],
            'can_assign_story': perm_service.can_assign_story(user)[0],
            'can_change_status': perm_service.can_change_status(user)[0],
            
            # Epic permissions
            'can_create_epic': perm_service.can_create_epic(user)[0],
            'can_edit_epic': perm_service.can_edit_epic(user)[0],
            'can_delete_epic': perm_service.can_delete_epic(user)[0],
            
            # Task permissions
            'can_create_task': perm_service.can_create_task(user)[0],
            'can_edit_task': perm_service.can_edit_task(user)[0],
            'can_delete_task': perm_service.can_delete_task(user)[0],
            
            # Issue permissions (uses story permissions by default)
            'can_create_issue': perm_service.can_create_issue(user)[0],
            
            # Collaboration permissions
            'can_add_comment': perm_service.can_add_comment(user)[0],
            'can_add_attachment': perm_service.can_add_attachment(user)[0],
            'can_manage_dependencies': perm_service.can_manage_dependencies(user)[0],
            
            # Project management permissions
            'can_manage_sprints': perm_service.can_manage_sprints(user)[0],
            'can_view_analytics': perm_service.can_view_analytics(user)[0],
        }
        
        return Response(permissions, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='members/(?P<user_id>[^/.]+)/statistics')
    def member_statistics(self, request, pk=None, user_id=None):
        """Get statistics for a specific member."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            from apps.authentication.models import User
            from django.db.models import Count, Sum, Q
            from datetime import datetime, timedelta
            
            project = self.get_object()
            
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                logger.error(f"Error fetching user {user_id}: {str(e)}")
                return Response(
                    {'error': f'Error fetching user: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify user is a member or owner
            if project.owner != user and not project.members.filter(id=user.id).exists():
                return Response(
                    {'error': 'User is not a member of this project'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get time range (default: last 30 days)
            try:
                days = int(request.query_params.get('days', 30))
            except (ValueError, TypeError):
                days = 30
            since_date = timezone.now() - timedelta(days=days)
            
            # Stories assigned
            stories_assigned = UserStory.objects.filter(project=project, assigned_to=user).count()
            stories_completed = UserStory.objects.filter(project=project, assigned_to=user, status='done').count()
            
            # Tasks assigned
            tasks_assigned = Task.objects.filter(story__project=project, assigned_to=user).count()
            tasks_completed = Task.objects.filter(story__project=project, assigned_to=user, status='done').count()
            
            # Bugs assigned
            bugs_assigned = Bug.objects.filter(project=project, assigned_to=user).count()
            bugs_resolved = Bug.objects.filter(project=project, assigned_to=user, status='resolved').count()
            
            # Issues assigned
            issues_assigned = Issue.objects.filter(project=project, assigned_to=user).count()
            issues_resolved = Issue.objects.filter(project=project, assigned_to=user, status='resolved').count()
            
            # Time logs
            time_logs = TimeLog.objects.filter(
                Q(story__project=project) | Q(task__story__project=project),
                user=user,
                created_at__gte=since_date
            )
            # Sum duration_minutes and convert to hours
            total_minutes = time_logs.aggregate(total=Sum('duration_minutes'))['total'] or 0
            total_hours = total_minutes / 60.0 if total_minutes else 0
            time_logs_count = time_logs.count()
            
            # Recent activity (last 10)
            from apps.projects.models import Activity
            recent_activities_qs = Activity.objects.filter(
                project=project,
                user=user
            ).order_by('-created_at')
            
            # If no activities found with project filter, try to find activities through related work items
            if not recent_activities_qs.exists():
                # Get activities through stories, tasks, bugs, issues
                story_ids = list(UserStory.objects.filter(project=project, assigned_to=user).values_list('id', flat=True))
                task_ids = list(Task.objects.filter(story__project=project, assigned_to=user).values_list('id', flat=True))
                bug_ids = list(Bug.objects.filter(project=project, assigned_to=user).values_list('id', flat=True))
                issue_ids = list(Issue.objects.filter(project=project, assigned_to=user).values_list('id', flat=True))
                
                from django.contrib.contenttypes.models import ContentType
                story_ct = ContentType.objects.get_for_model(UserStory)
                task_ct = ContentType.objects.get_for_model(Task)
                bug_ct = ContentType.objects.get_for_model(Bug)
                issue_ct = ContentType.objects.get_for_model(Issue)
                
                recent_activities_qs = Activity.objects.filter(
                    Q(project=project, user=user) |
                    Q(content_type=story_ct, object_id__in=story_ids, user=user) |
                    Q(content_type=task_ct, object_id__in=task_ids, user=user) |
                    Q(content_type=bug_ct, object_id__in=bug_ids, user=user) |
                    Q(content_type=issue_ct, object_id__in=issue_ids, user=user)
            ).order_by('-created_at')
            
            # Get last 10 activities
            recent_activities = list(recent_activities_qs[:10])
            
            from apps.projects.serializers import ActivitySerializer
            activity_serializer = ActivitySerializer(recent_activities, many=True)
            
            # Comments
            from apps.projects.models import StoryComment
            comments_count = StoryComment.objects.filter(
                story__project=project,
                created_by=user,
                created_at__gte=since_date
            ).count()
            
            # Epics owned
            epics_owned = Epic.objects.filter(project=project, owner=user).count()
            
            return Response({
                'user_id': str(user.id),
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                },
                'statistics': {
                    'stories': {
                        'assigned': stories_assigned,
                        'completed': stories_completed,
                        'completion_rate': round((stories_completed / stories_assigned * 100) if stories_assigned > 0 else 0, 1)
                    },
                    'tasks': {
                        'assigned': tasks_assigned,
                        'completed': tasks_completed,
                        'completion_rate': round((tasks_completed / tasks_assigned * 100) if tasks_assigned > 0 else 0, 1)
                    },
                    'bugs': {
                        'assigned': bugs_assigned,
                        'resolved': bugs_resolved,
                        'resolution_rate': round((bugs_resolved / bugs_assigned * 100) if bugs_assigned > 0 else 0, 1)
                    },
                    'issues': {
                        'assigned': issues_assigned,
                        'resolved': issues_resolved,
                        'resolution_rate': round((issues_resolved / issues_assigned * 100) if issues_assigned > 0 else 0, 1)
                    },
                    'time_tracking': {
                        'total_hours': round(total_hours, 2),
                        'time_logs_count': time_logs_count,
                        'average_per_log': round(total_hours / time_logs_count, 2) if time_logs_count > 0 else 0
                    },
                    'engagement': {
                        'comments': comments_count,
                        'epics_owned': epics_owned,
                        'activities': len(recent_activities)
                    }
                },
                'recent_activities': activity_serializer.data,
                'period_days': days
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Error in member_statistics for project {pk}, user {user_id}: {str(e)}")
            return Response(
                {'error': f'An error occurred while fetching statistics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        if RoleService.is_admin(user):
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
        if RoleService.is_admin(user):
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
        Filter sprints based on user permissions and organization.
        - Super admins: See all sprints
        - Org admins: See sprints from projects in their organization
        - Regular users: See sprints from projects where they are owner or member (within their organization)
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Sprint.objects.none()
        
        # Super admins see everything
        if RoleService.is_super_admin(user):
            return Sprint.objects.all().select_related('project', 'project__owner', 'project__organization').prefetch_related('project__members')
        
        # Get user's organizations
        user_orgs = RoleService.get_user_organizations(user)
        if not user_orgs and user.organization:
            user_orgs = [user.organization]
        
        if not user_orgs:
            return Sprint.objects.none()
        
        # Build queryset for user's organizations
        org_ids = [org.id for org in user_orgs]
        queryset = Sprint.objects.filter(project__organization_id__in=org_ids)
        
        # Filter by permissions within organizations
        is_org_admin = any(RoleService.is_org_admin(user, org) for org in user_orgs)
        
        if not is_org_admin:
            # Regular users see only sprints from projects where they are owner or member
            queryset = queryset.filter(
                models.Q(project__owner=user) | models.Q(project__members__id=user.id)
            ).distinct()
        
        return queryset.select_related('project', 'project__owner', 'project__organization').prefetch_related('project__members')
    
    def perform_create(self, serializer):
        """Set default sprint values from project configuration."""
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        project = serializer.validated_data.get('project')
        if project:
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(project, self.request.user)
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
    
    def perform_update(self, serializer):
        """Update sprint with organization status and subscription validation."""
        sprint = serializer.instance
        if sprint and sprint.project:
            ProjectViewSet._validate_project_organization_for_write(sprint.project, self.request.user)
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete sprint with organization status and subscription validation."""
        if instance.project:
            ProjectViewSet._validate_project_organization_for_write(instance.project, self.request.user)
        super().perform_destroy(instance)
    
    @extend_schema(
        request=SprintPlanningRequestSerializer,
        description="Auto-plan sprint using AI"
    )
    @action(detail=True, methods=['post'], url_path='auto-plan')
    def auto_plan(self, request, pk=None):
        """Auto-plan sprint with AI."""
        sprint = self.get_object()
        
        # Validate organization status and subscription
        if sprint and sprint.project:
            ProjectViewSet._validate_project_organization_for_write(sprint.project, request.user)
        
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
            from apps.projects.services.sprint_automation_service import SprintAutomationService
            health_data = SprintAutomationService.check_sprint_health(str(sprint.id))
            return Response(health_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Auto-assign stories to sprint"
    )
    @action(detail=True, methods=['post'], url_path='auto-assign')
    def auto_assign(self, request, pk=None):
        """Automatically assign stories to sprint."""
        sprint = self.get_object()
        
        # Validate organization status and subscription
        if sprint and sprint.project:
            ProjectViewSet._validate_project_organization_for_write(sprint.project, request.user)
        
        try:
            from apps.projects.services.sprint_automation_service import SprintAutomationService
            result = SprintAutomationService.auto_assign_stories_to_sprint(
                str(sprint.project.id),
                str(sprint.id)
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Auto-close expired sprints"
    )
    @action(detail=False, methods=['post'])
    def auto_close(self, request):
        """Automatically close expired sprints."""
        try:
            from apps.projects.services.sprint_automation_service import SprintAutomationService
            project_id = request.data.get('project')
            closed = SprintAutomationService.auto_close_sprints(project_id)
            return Response({
                'closed_count': len(closed),
                'closed_sprints': closed
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Auto-create next sprint"
    )
    @action(detail=False, methods=['post'])
    def auto_create(self, request):
        """Automatically create the next sprint."""
        try:
            from apps.projects.services.sprint_automation_service import SprintAutomationService
            project_id = request.data.get('project')
            if not project_id:
                return Response(
                    {'error': 'project is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            result = SprintAutomationService.auto_create_sprint(project_id)
            if result:
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(
                {'error': 'Failed to create sprint'},
                status=status.HTTP_400_BAD_REQUEST
            )
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
        Organization-aware filtering:
        - Super admins: See all stories across all organizations
        - Org admins: See all stories from projects in their organization
        - Regular users: See stories from projects where they are owner or member (within their organization)
        Supports tag filtering via ?tags=tag1,tag2 query parameter.
        Supports project filtering via ?project=uuid query parameter.
        Supports due date filtering via ?overdue=true, ?due_today=true, ?due_soon=true, ?due_date__gte=YYYY-MM-DD, ?due_date__lte=YYYY-MM-DD
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Story.objects.none()
        
        # Super admins see everything
        if RoleService.is_super_admin(user):
            queryset = Story.objects.all()
        else:
            # Get user's organizations
            user_orgs = RoleService.get_user_organizations(user)
            if not user_orgs and user.organization:
                user_orgs = [user.organization]
            
            if not user_orgs:
                # User has no organization, can't see any stories
                return Story.objects.none()
            
            # Build queryset for user's organizations
            org_ids = [org.id for org in user_orgs]
            queryset = Story.objects.filter(project__organization_id__in=org_ids)
            
            # Filter by permissions within organizations
            # Org admins see all stories in their orgs
            is_org_admin = any(RoleService.is_org_admin(user, org) for org in user_orgs)
            
            if not is_org_admin:
                # Regular users see only stories from projects where they are owner or member
                queryset = queryset.filter(
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
        
        # Order by story number ascending (nulls last), then by created_at
        # Simple string sort - handles alphanumeric naturally (STORY-1, STORY-2, STORY-10, etc.)
        # For proper numeric sorting, we'd need regex which isn't portable
        # This will sort alphabetically which works reasonably well for prefixed numbers
        queryset = queryset.select_related('project', 'project__owner', 'sprint', 'epic', 'assigned_to', 'created_by').prefetch_related('project__members')
        
        return queryset.order_by(
            models.F('number').asc(nulls_last=True),
            'created_at'
        )
    
    def perform_create(self, serializer):
        """Set the current user as the story creator when creating."""
        # Check project-level permissions
        project = serializer.validated_data.get('project')
        if project:
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(project, self.request.user)
            
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
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(story.project, request.user)
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
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(instance.project, self.request.user)
            
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
        
        # Validate organization status and subscription (AI operation)
        if story and story.project:
            ProjectViewSet._validate_project_organization_for_write(story.project, request.user)
        
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
        
        # Get accessible stories with optimized queries
        if RoleService.is_admin(user):
            stories = Story.objects.all().only('tags')
        else:
            stories = Story.objects.filter(
                models.Q(project__owner=user) | models.Q(project__members__id=user.id)
            ).distinct().only('tags')
        
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
    @action(detail=False, methods=['get'], url_path='tags/autocomplete', throttle_classes=[AutocompleteThrottle])
    def tags_autocomplete(self, request):
        """Get tag suggestions for autocomplete."""
        query = request.query_params.get('q', '').strip().lower()
        project_id = request.query_params.get('project', None)
        
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'tags': []}, status=status.HTTP_200_OK)
        
        # Get accessible stories with optimized queries (only fetch tags field)
        if RoleService.is_admin(user):
            stories = Story.objects.all().only('tags')
        else:
            stories = Story.objects.filter(
                models.Q(project__owner=user) | models.Q(project__members__id=user.id)
            ).distinct().only('tags')
        
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
        if RoleService.is_admin(user):
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
    
    @extend_schema(
        description="Bulk update status for multiple stories",
        request={'type': 'object', 'properties': {
            'items': {'type': 'array', 'items': {'type': 'object'}},
            'status': {'type': 'string'}
        }},
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['post'], url_path='bulk-update-status')
    def bulk_update_status(self, request):
        """Bulk update status for stories."""
        items = request.data.get('items', [])
        new_status = request.data.get('status')
        
        # Validate organization status and subscription for all affected projects
        if items:
            story_ids = [item.get('id') for item in items if item.get('id')]
            if story_ids:
                stories = Story.objects.filter(id__in=story_ids).select_related('project', 'project__organization')
                projects = {story.project for story in stories if story.project}
                for project in projects:
                    ProjectViewSet._validate_project_organization_for_write(project, request.user)
        
        if not items or not new_status:
            return Response(
                {'error': 'items and status are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add type to items
        items_with_type = [{'id': item.get('id'), 'type': 'story'} for item in items]
        result = BulkOperationsService.bulk_update_status(items_with_type, new_status, request.user)
        return Response(result)
    
    @extend_schema(
        description="Bulk assign stories to a user",
        request={'type': 'object', 'properties': {
            'items': {'type': 'array', 'items': {'type': 'object'}},
            'assignee_id': {'type': 'string', 'format': 'uuid'}
        }},
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['post'], url_path='bulk-assign')
    def bulk_assign(self, request):
        """Bulk assign stories to a user."""
        items = request.data.get('items', [])
        assignee_id = request.data.get('assignee_id')
        
        if not items or not assignee_id:
            return Response(
                {'error': 'items and assignee_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items_with_type = [{'id': item.get('id'), 'type': 'story'} for item in items]
        result = BulkOperationsService.bulk_assign(items_with_type, assignee_id, request.user)
        return Response(result)
    
    @extend_schema(
        description="Bulk add labels to stories",
        request={'type': 'object', 'properties': {
            'items': {'type': 'array', 'items': {'type': 'object'}},
            'labels': {'type': 'array', 'items': {'type': 'string'}}
        }},
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['post'], url_path='bulk-add-labels')
    def bulk_add_labels(self, request):
        """Bulk add labels to stories."""
        items = request.data.get('items', [])
        labels = request.data.get('labels', [])
        
        if not items or not labels:
            return Response(
                {'error': 'items and labels are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items_with_type = [{'id': item.get('id'), 'type': 'story'} for item in items]
        result = BulkOperationsService.bulk_add_labels(items_with_type, labels, request.user)
        return Response(result)
    
    @extend_schema(
        description="Bulk delete stories",
        request={'type': 'object', 'properties': {
            'items': {'type': 'array', 'items': {'type': 'object'}}
        }},
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """Bulk delete stories."""
        items = request.data.get('items', [])
        
        # Validate organization status and subscription for all affected projects
        if items:
            story_ids = [item.get('id') for item in items if item.get('id')]
            if story_ids:
                stories = Story.objects.filter(id__in=story_ids).select_related('project', 'project__organization')
                projects = {story.project for story in stories if story.project}
                for project in projects:
                    ProjectViewSet._validate_project_organization_for_write(project, request.user)
        
        if not items:
            return Response(
                {'error': 'items are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items_with_type = [{'id': item.get('id'), 'type': 'story'} for item in items]
        result = BulkOperationsService.bulk_delete(items_with_type, request.user)
        return Response(result)
    
    @extend_schema(
        description="Bulk move stories to a sprint",
        request={'type': 'object', 'properties': {
            'items': {'type': 'array', 'items': {'type': 'object'}},
            'sprint_id': {'type': 'string', 'format': 'uuid'}
        }},
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['post'], url_path='bulk-move-to-sprint')
    def bulk_move_to_sprint(self, request):
        """Bulk move stories to a sprint."""
        items = request.data.get('items', [])
        sprint_id = request.data.get('sprint_id')
        
        if not items or not sprint_id:
            return Response(
                {'error': 'items and sprint_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get project from first item to validate organization
        if items:
            try:
                first_item = items[0]
                story = UserStory.objects.select_related('project__organization').get(id=first_item.get('id'))
                project = story.project
                if project and project.organization:
                    self._validate_organization_for_write(project.organization, request.user)
            except UserStory.DoesNotExist:
                pass  # Will be handled by bulk operation service
        
        items_with_type = [{'id': item.get('id'), 'type': 'story'} for item in items]
        result = BulkOperationsService.bulk_move_to_sprint(items_with_type, sprint_id, request.user)
        return Response(result)


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
        Organization-aware filtering:
        - Super admins: See all epics across all organizations
        - Org admins: See all epics from projects in their organization
        - Regular users: See epics from projects where they are owner or member (within their organization)
        Supports tag filtering via ?tags=tag1,tag2 query parameter.
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return Epic.objects.none()
        
        # Super admins see everything
        if RoleService.is_super_admin(user):
            queryset = Epic.objects.all()
        else:
            # Get user's organizations
            user_orgs = RoleService.get_user_organizations(user)
            if not user_orgs and user.organization:
                user_orgs = [user.organization]
            
            if not user_orgs:
                # User has no organization, can't see any epics
                return Epic.objects.none()
            
            # Build queryset for user's organizations
            org_ids = [org.id for org in user_orgs]
            queryset = Epic.objects.filter(project__organization_id__in=org_ids)
            
            # Filter by permissions within organizations
            # Org admins see all epics in their orgs
            is_org_admin = any(RoleService.is_org_admin(user, org) for org in user_orgs)
            
            if not is_org_admin:
                # Regular users see only epics from projects where they are owner or member
                queryset = queryset.filter(
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
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(project, self.request.user)
            
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
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(epic.project, self.request.user)
            
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
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(instance.project, self.request.user)
            
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
        
        # Super admins see everything
        if RoleService.is_super_admin(user):
            queryset = Task.objects.all()
        else:
            # Get user's organizations
            user_orgs = RoleService.get_user_organizations(user)
            if not user_orgs and user.organization:
                user_orgs = [user.organization]
            
            if not user_orgs:
                # User has no organization, can't see any tasks
                return Task.objects.none()
            
            # Build queryset for user's organizations
            org_ids = [org.id for org in user_orgs]
            queryset = Task.objects.filter(story__project__organization_id__in=org_ids)
            
            # Filter by permissions within organizations
            # Org admins see all tasks in their orgs
            is_org_admin = any(RoleService.is_org_admin(user, org) for org in user_orgs)
            
            if not is_org_admin:
                # Regular users see only tasks from projects where they are owner or member
                queryset = queryset.filter(
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
    
    def perform_create(self, serializer):
        """Create task with organization status and subscription validation."""
        story = serializer.validated_data.get('story')
        if story and story.project:
            ProjectViewSet._validate_project_organization_for_write(story.project, self.request.user)
        serializer.save()
    
    def perform_update(self, serializer):
        """Update task with organization status and subscription validation."""
        task = serializer.instance
        if task and task.story and task.story.project:
            ProjectViewSet._validate_project_organization_for_write(task.story.project, self.request.user)
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete task with organization status and subscription validation."""
        if instance.story and instance.story.project:
            ProjectViewSet._validate_project_organization_for_write(instance.story.project, self.request.user)
        super().perform_destroy(instance)


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
        
        # Super admins see everything
        if RoleService.is_super_admin(user):
            queryset = Bug.objects.all()
        else:
            # Get user's organizations
            user_orgs = RoleService.get_user_organizations(user)
            if not user_orgs and user.organization:
                user_orgs = [user.organization]
            
            if not user_orgs:
                # User has no organization, can't see any bugs
                return Bug.objects.none()
            
            # Build queryset for user's organizations
            org_ids = [org.id for org in user_orgs]
            queryset = Bug.objects.filter(project__organization_id__in=org_ids)
            
            # Filter by permissions within organizations
            # Org admins see all bugs in their orgs
            is_org_admin = any(RoleService.is_org_admin(user, org) for org in user_orgs)
            
            if not is_org_admin:
                # Regular users see only bugs from projects where they are owner or member
                queryset = queryset.filter(
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
        project = serializer.validated_data.get('project')
        if project:
            ProjectViewSet._validate_project_organization_for_write(project, self.request.user)
        user = self.request.user
        serializer.save(created_by=user, reporter=user if not serializer.validated_data.get('reporter') else None)
    
    def perform_update(self, serializer):
        """Set updated_by on bug update."""
        bug = serializer.instance
        if bug and bug.project:
            ProjectViewSet._validate_project_organization_for_write(bug.project, self.request.user)
        serializer.save(updated_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Delete bug with organization status and subscription validation."""
        if instance.project:
            ProjectViewSet._validate_project_organization_for_write(instance.project, self.request.user)
        super().perform_destroy(instance)


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
        
        # Super admins see everything
        if RoleService.is_super_admin(user):
            queryset = Issue.objects.all()
        else:
            # Get user's organizations
            user_orgs = RoleService.get_user_organizations(user)
            if not user_orgs and user.organization:
                user_orgs = [user.organization]
            
            if not user_orgs:
                queryset = Issue.objects.none()
            else:
                # Build queryset for user's organizations
                org_ids = [org.id for org in user_orgs]
                queryset = Issue.objects.filter(project__organization_id__in=org_ids)
                
                # Filter by permissions within organizations
                is_org_admin = any(RoleService.is_org_admin(user, org) for org in user_orgs)
                
                if not is_org_admin:
                    # Regular users see only issues from projects where they are owner or member
                    queryset = queryset.filter(
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
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(project, self.request.user)
            
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
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(issue.project, self.request.user)
            
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
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(instance.project, self.request.user)
            
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
        Filter time logs based on user permissions and organization.
        Organization-aware filtering:
        - Super admins: See all time logs across all organizations
        - Org admins: See all time logs from projects in their organization
        - Regular users: See their own time logs or time logs from projects they're members of (within their organization)
        """
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return TimeLog.objects.none()
        
        user = self.request.user
        if not user or not user.is_authenticated:
            return TimeLog.objects.none()
        
        # Super admins see everything
        if RoleService.is_super_admin(user):
            queryset = TimeLog.objects.all()
        else:
            # Get user's organizations
            user_orgs = RoleService.get_user_organizations(user)
            if not user_orgs and user.organization:
                user_orgs = [user.organization]
            
            if not user_orgs:
                # User has no organization, can only see their own time logs
                return TimeLog.objects.filter(user=user)
            
            # Build queryset for user's organizations
            org_ids = [org.id for org in user_orgs]
            
            # Filter by organization through project relationships
            queryset = TimeLog.objects.filter(
                models.Q(story__project__organization_id__in=org_ids) |
                models.Q(task__story__project__organization_id__in=org_ids) |
                models.Q(bug__project__organization_id__in=org_ids) |
                models.Q(issue__project__organization_id__in=org_ids)
            )
            
            # Filter by permissions within organizations
            # Org admins see all time logs in their orgs
            is_org_admin = any(RoleService.is_org_admin(user, org) for org in user_orgs)
            
            if not is_org_admin:
                # Regular users see their own time logs or time logs from projects they're members of
                queryset = queryset.filter(
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
        
        # Get project from work item and validate organization
        story_id = serializer.validated_data.get('story_id') or serializer.initial_data.get('story')
        task_id = serializer.validated_data.get('task_id') or serializer.initial_data.get('task')
        bug_id = serializer.validated_data.get('bug_id') or serializer.initial_data.get('bug')
        issue_id = serializer.validated_data.get('issue_id') or serializer.initial_data.get('issue')
        
        project = None
        if story_id:
            try:
                story = Story.objects.select_related('project').get(id=story_id)
                project = story.project
            except Story.DoesNotExist:
                pass
        elif task_id:
            try:
                task = Task.objects.select_related('story__project').get(id=task_id)
                project = task.story.project if task.story else None
            except Task.DoesNotExist:
                pass
        elif bug_id:
            try:
                bug = Bug.objects.select_related('project').get(id=bug_id)
                project = bug.project
            except Bug.DoesNotExist:
                pass
        elif issue_id:
            try:
                issue = Issue.objects.select_related('project').get(id=issue_id)
                project = issue.project
            except Issue.DoesNotExist:
                pass
        
        if project:
            ProjectViewSet._validate_project_organization_for_write(project, user)
        
        serializer.save(
            created_by=user,
            user=user,  # Always set to current user
        )
    
    def perform_update(self, serializer):
        """Set updated_by on time log update."""
        time_log = serializer.instance
        # Get project from work item and validate organization
        project = None
        if time_log.story:
            project = time_log.story.project
        elif time_log.task and time_log.task.story:
            project = time_log.task.story.project
        elif time_log.bug:
            project = time_log.bug.project
        elif time_log.issue:
            project = time_log.issue.project
        
        if project:
            ProjectViewSet._validate_project_organization_for_write(project, self.request.user)
        
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def start_timer(self, request):
        """Start a new timer for a work item."""
        from django.utils import timezone
        
        # Validate organization status and subscription before starting timer
        user = request.user
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
        
        # Get project from work item and validate
        project = None
        if story_id:
            try:
                story = Story.objects.select_related('project').get(id=story_id)
                project = story.project
            except Story.DoesNotExist:
                return Response(
                    {'error': 'Story not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif task_id:
            try:
                task = Task.objects.select_related('story__project').get(id=task_id)
                project = task.story.project if task.story else None
            except Task.DoesNotExist:
                return Response(
                    {'error': 'Task not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif bug_id:
            try:
                bug = Bug.objects.select_related('project').get(id=bug_id)
                project = bug.project
            except Bug.DoesNotExist:
                return Response(
                    {'error': 'Bug not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif issue_id:
            try:
                issue = Issue.objects.select_related('project').get(id=issue_id)
                project = issue.project
            except Issue.DoesNotExist:
                return Response(
                    {'error': 'Issue not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        if project:
            try:
                ProjectViewSet._validate_project_organization_for_write(project, user)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
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
        
        # Get project from work item and validate organization
        project = None
        if time_log.story:
            project = time_log.story.project
        elif time_log.task and time_log.task.story:
            project = time_log.task.story.project
        elif time_log.bug:
            project = time_log.bug.project
        elif time_log.issue:
            project = time_log.issue.project
        
        if project:
            try:
                ProjectViewSet._validate_project_organization_for_write(project, request.user)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
        
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
        if RoleService.is_admin(user):
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
        user = self.request.user
        
        # Super admins can access any project configuration
        is_super_admin = RoleService.is_super_admin(user)
        
        # Get or create configuration
        try:
            config = ProjectConfiguration.objects.get(project_id=project_id)
        except ProjectConfiguration.DoesNotExist:
            # Configuration doesn't exist - create it
            try:
                from apps.projects.models import Project
                project = Project.objects.get(pk=project_id)
                
                # Check permissions before creating (super admin bypasses this check)
                if not is_super_admin and not RoleService.is_admin(user) and project.owner != user and user not in project.members.all():
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied("You don't have access to this project's configuration.")
                
                # Create configuration
                config = ProjectConfiguration.objects.create(project=project)
                config.initialize_defaults()
                config.save()
            except Project.DoesNotExist:
                from rest_framework.exceptions import NotFound
                raise NotFound("Project not found.")
        
        # Check permissions (super admin bypasses this check)
        if is_super_admin:
            return config
        
        project = config.project
        if not RoleService.is_admin(user) and project.owner != user and user not in project.members.all():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have access to this project's configuration.")
        
        return config
    
    def perform_create(self, serializer):
        """Set updated_by when creating."""
        serializer.save(updated_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by when updating with custom fields feature check."""
        user = self.request.user
        config = serializer.instance
        project = config.project
        organization = project.organization
        
        # Check if custom_fields are being updated
        if 'custom_fields' in serializer.validated_data:
            # Check if custom fields feature is available
            FeatureService.is_feature_available(
                organization, 
                'projects.custom_fields', 
                user=user, 
                raise_exception=True
            )
        
        serializer.save(updated_by=user)
    
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
        if not RoleService.is_admin(request.user) and config.project.owner != request.user:
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
        from django.utils import timezone
        mention = self.get_object()
        mention.read = True
        mention.read_at = timezone.now()
        mention.save()
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
        # For detail actions (update, delete, react, etc.), don't filter by story
        # This allows accessing comments by ID directly
        if self.action in ['update', 'partial_update', 'destroy', 'retrieve', 'react']:
            return StoryComment.objects.filter(deleted=False)
        
        # For list actions, filter by story
        story_id = self.request.query_params.get('story', None)
        if not story_id:
            return StoryComment.objects.filter(deleted=False)
        
        queryset = StoryComment.objects.filter(
            story_id=story_id,
            deleted=False
        )
        
        # Filter by parent for threading (if parent param is provided)
        parent_id = self.request.query_params.get('parent', None)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        # If no parent filter, return all comments (including replies) for the story
        # The frontend will organize them into a tree structure
        
        return queryset.order_by('created_at')
    
    def perform_create(self, serializer):
        """Set author to current user and check permissions."""
        story = serializer.validated_data.get('story')
        if story and story.project:
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(story.project, self.request.user)
            
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
        if not RoleService.is_admin(user):
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
        if not RoleService.is_admin(user):
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
            # Validate organization status and subscription
            ProjectViewSet._validate_project_organization_for_write(story.project, self.request.user)
            
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
        from django.utils import timezone
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
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

        if RoleService.is_admin(user):
            return Watcher.objects.all().select_related('user', 'content_type')

        # Get projects the user is a member of (considering organization context)
        user_orgs = RoleService.get_user_organizations(user)
        if user.organization:
            user_orgs.append(user.organization)
        org_ids = list(set(org.id for org in user_orgs)) if user_orgs else []
        
        # Build project filter
        project_filter = Q(owner=user) | Q(members__id=user.id)
        if org_ids:
            project_filter |= Q(organization_id__in=org_ids)
        
        accessible_projects = Project.objects.filter(project_filter).values_list('id', flat=True)

        # Get accessible object IDs for each content type
        accessible_story_ids = UserStory.objects.filter(project_id__in=accessible_projects).values_list('id', flat=True)
        accessible_task_ids = Task.objects.filter(story__project_id__in=accessible_projects).values_list('id', flat=True)
        accessible_bug_ids = Bug.objects.filter(project_id__in=accessible_projects).values_list('id', flat=True)
        accessible_issue_ids = Issue.objects.filter(project_id__in=accessible_projects).values_list('id', flat=True)
        accessible_epic_ids = Epic.objects.filter(project_id__in=accessible_projects).values_list('id', flat=True)

        # Filter watchers related to accessible objects or created by the user
        return Watcher.objects.filter(
            Q(user=user) |
            Q(content_type__model='project', object_id__in=accessible_projects) |
            Q(content_type__model='userstory', object_id__in=accessible_story_ids) |
            Q(content_type__model='task', object_id__in=accessible_task_ids) |
            Q(content_type__model='bug', object_id__in=accessible_bug_ids) |
            Q(content_type__model='issue', object_id__in=accessible_issue_ids) |
            Q(content_type__model='epic', object_id__in=accessible_epic_ids)
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
                if not RoleService.is_admin(user):
                    if project.owner != user and not project.members.filter(id=user.id).exists():
                        return Response(
                            {'error': 'You do not have permission to watch objects in this project.'},
                            status=status.HTTP_403_FORBIDDEN
                        )
        else:
            # For non-project related objects, ensure user has general access or is admin
            if not RoleService.is_admin(user) and hasattr(content_object, 'created_by') and content_object.created_by != user:
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
        if RoleService.is_admin(user):
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
        if RoleService.is_admin(user):
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
                if not RoleService.is_admin(user):
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


class QuickFiltersViewSet(viewsets.ViewSet):
    """
    ViewSet for quick filters - predefined filter configurations.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        description="Get available quick filters",
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='')
    def available(self, request):
        """Get list of available quick filters."""
        project_id = request.query_params.get('project')
        
        # Default quick filters
        default_filters = [
            {
                'id': 'my-tasks',
                'name': 'My Tasks',
                'filters': [{'field': 'assignee', 'operator': 'equals', 'value': 'me'}],
                'icon': 'user'
            },
            {
                'id': 'overdue',
                'name': 'Overdue',
                'filters': [{'field': 'due_date', 'operator': 'is_overdue', 'value': ''}],
                'icon': 'alert-circle'
            },
            {
                'id': 'due-today',
                'name': 'Due Today',
                'filters': [{'field': 'due_date', 'operator': 'due_today', 'value': ''}],
                'icon': 'calendar'
            },
            {
                'id': 'high-priority',
                'name': 'High Priority',
                'filters': [{'field': 'priority', 'operator': 'equals', 'value': 'high'}],
                'icon': 'flag'
            },
            {
                'id': 'unassigned',
                'name': 'Unassigned',
                'filters': [{'field': 'assignee', 'operator': 'is_null', 'value': ''}],
                'icon': 'user-x'
            },
            {
                'id': 'blocked',
                'name': 'Blocked',
                'filters': [{'field': 'dependencies', 'operator': 'blocked_by', 'value': ''}],
                'icon': 'lock'
            },
        ]
        
        # Get project-specific quick filters from FilterPreset
        project_filters = []
        if project_id:
            from apps.projects.models import FilterPreset
            presets = FilterPreset.objects.filter(
                project_id=project_id,
                is_default=True
            )[:5]  # Limit to 5 project-specific filters
            
            for preset in presets:
                project_filters.append({
                    'id': f'preset-{preset.id}',
                    'name': preset.name,
                    'filters': preset.filters,
                    'icon': 'filter',
                    'is_preset': True,
                    'preset_id': str(preset.id),
                })
        
        return Response({
            'default_filters': default_filters,
            'project_filters': project_filters,
            'all_filters': default_filters + project_filters,
        }, status=status.HTTP_200_OK)


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
    def list(self, request):
        """List/search endpoint - delegates to search method."""
        return self.search(request)
    
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
    @action(detail=False, methods=['get'], url_path='search')
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
                if not RoleService.is_admin(user):
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
        
        total_count = sum(len(items) for items in results.values())
        
        # Save search history
        if query.strip():
            try:
                SearchHistory.objects.create(
                    user=request.user,
                    query=query,
                    filters=filters,
                    content_types=content_types or [],
                    project=project,
                    result_count=total_count
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error saving search history: {e}")
        
        return Response({
            'query': query,
            'results': results,
            'total_count': total_count
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
                if not RoleService.is_admin(user):
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
            
            # Save search history
            if query.strip():
                try:
                    SearchHistory.objects.create(
                        user=request.user,
                        query=query,
                        filters={},
                        content_types=content_types or [],
                        project=project,
                        result_count=len(results)
                    )
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error saving search history: {e}")
            
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


class SearchHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing search history.
    Users can view their recent search queries.
    """
    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return search history for the current user only."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return SearchHistory.objects.none()
        
        queryset = SearchHistory.objects.filter(user=user)
        
        # Filter by project if provided
        project_id = self.request.query_params.get('project', None)
        if project_id:
            try:
                queryset = queryset.filter(project_id=project_id)
            except (ValueError, TypeError):
                queryset = queryset.none()
        
        # Limit to last 50 searches
        return queryset.select_related('user', 'project').order_by('-created_at')[:50]
    
    @extend_schema(
        description="Clear search history",
        responses={204: None}
    )
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all search history for the current user."""
        user = request.user
        project_id = request.query_params.get('project', None)
        
        queryset = SearchHistory.objects.filter(user=user)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        count = queryset.delete()[0]
        return Response({'deleted_count': count}, status=status.HTTP_200_OK)


class FilterPresetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing filter presets.
    Users can create, update, and delete filter presets for quick filtering.
    """
    serializer_class = FilterPresetSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Return filter presets accessible to the user."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return FilterPreset.objects.none()
        
        # Get project from URL or query params
        project_id = self.kwargs.get('project_pk') or self.request.query_params.get('project')
        
        queryset = FilterPreset.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        else:
            # Global presets or user's personal presets
            queryset = queryset.filter(
                models.Q(project__isnull=True) | models.Q(user=user) | models.Q(is_shared=True)
            )
        
        # Filter by user if specified
        user_filter = self.request.query_params.get('user')
        if user_filter:
            queryset = queryset.filter(user_id=user_filter)
        
        return queryset.select_related('project', 'user', 'created_by').order_by('is_default', 'name')
    
    def perform_create(self, serializer):
        """Set user and project on filter preset creation."""
        project_id = self.kwargs.get('project_pk') or self.request.data.get('project')
        user = self.request.user
        
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
                self.check_object_permissions(self.request, project)
                serializer.save(project=project, user=user, created_by=user)
            except Project.DoesNotExist:
                raise status.HTTP_404_NOT_FOUND
        else:
            serializer.save(user=user, created_by=user)
    
    @extend_schema(
        description="Apply a filter preset",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply a filter preset and increment usage count."""
        preset = self.get_object()
        preset.usage_count += 1
        preset.save(update_fields=['usage_count'])
        
        return Response({
            'filters': preset.filters,
            'preset_name': preset.name
        }, status=status.HTTP_200_OK)


class TimeBudgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing time budgets.
    """
    serializer_class = TimeBudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Return time budgets for the project."""
        project_id = self.request.query_params.get('project')
        sprint_id = self.request.query_params.get('sprint')
        user_id = self.request.query_params.get('user')
        
        queryset = TimeBudget.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if sprint_id:
            queryset = queryset.filter(sprint_id=sprint_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.select_related('project', 'sprint', 'story', 'task', 'epic', 'user').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by on budget creation."""
        serializer.save(created_by=self.request.user)
    
    @extend_schema(
        description="Check budgets and create overtime records",
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['post'])
    def check_budgets(self, request):
        """Check all active budgets and create overtime records."""
        from apps.projects.services.time_budget_service import TimeBudgetService
        
        project_id = request.data.get('project')
        sprint_id = request.data.get('sprint')
        
        exceeded = TimeBudgetService.check_budgets(project_id, sprint_id)
        
        return Response({
            'exceeded_count': len(exceeded),
            'exceeded_budgets': [
                {
                    'budget_id': str(b['budget'].id),
                    'spent_hours': b['spent_hours'],
                    'budget_hours': b['budget_hours'],
                    'overtime_hours': b['overtime_hours'],
                }
                for b in exceeded
            ]
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Get budget summary",
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of all budgets."""
        from apps.projects.services.time_budget_service import TimeBudgetService
        
        project_id = request.query_params.get('project')
        sprint_id = request.query_params.get('sprint')
        
        summary = TimeBudgetService.get_budget_summary(project_id, sprint_id)
        
        return Response(summary, status=status.HTTP_200_OK)


class OvertimeRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing overtime records.
    """
    serializer_class = OvertimeRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return overtime records."""
        project_id = self.request.query_params.get('project')
        user_id = self.request.query_params.get('user')
        
        queryset = OvertimeRecord.objects.all()
        
        if project_id:
            queryset = queryset.filter(time_budget__project_id=project_id)
        if user_id:
            queryset = queryset.filter(time_budget__user_id=user_id)
        
        return queryset.select_related('time_budget').order_by('-created_at')
    
    @extend_schema(
        description="Get overtime history",
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get overtime history."""
        from apps.projects.services.time_budget_service import TimeBudgetService
        
        project_id = request.query_params.get('project')
        user_id = request.query_params.get('user')
        limit = int(request.query_params.get('limit', 50))
        
        history = TimeBudgetService.get_overtime_history(project_id, user_id, limit)
        
        return Response(history, status=status.HTTP_200_OK)


class CardCoverImageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing card cover images."""
    serializer_class = CardCoverImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return cover images for the user's accessible work items."""
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        
        queryset = CardCoverImage.objects.all()
        
        if content_type and object_id:
            queryset = queryset.filter(content_type__model=content_type, object_id=object_id)
        
        return queryset.order_by('-is_primary', '-created_at')


class CardChecklistViewSet(viewsets.ModelViewSet):
    """ViewSet for managing card checklists."""
    serializer_class = CardChecklistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return checklists for the user's accessible work items."""
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        
        queryset = CardChecklist.objects.all()
        
        if content_type and object_id:
            queryset = queryset.filter(content_type__model=content_type, object_id=object_id)
        
        return queryset.select_related('created_by').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by on checklist creation."""
        serializer.save(created_by=self.request.user)


class CardVoteViewSet(viewsets.ModelViewSet):
    """ViewSet for managing card votes."""
    serializer_class = CardVoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return votes for the user's accessible work items."""
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        user_id = self.request.query_params.get('user')
        
        queryset = CardVote.objects.all()
        
        if content_type and object_id:
            queryset = queryset.filter(content_type__model=content_type, object_id=object_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.select_related('user').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set user on vote creation."""
        serializer.save(user=self.request.user)
    
    @extend_schema(
        description="Get vote summary for a work item",
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get vote summary (upvotes, downvotes, total)."""
        content_type = request.query_params.get('content_type')
        object_id = request.query_params.get('object_id')
        
        if not content_type or not object_id:
            return Response(
                {'error': 'content_type and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        votes = CardVote.objects.filter(
            content_type__model=content_type,
            object_id=object_id
        )
        
        upvotes = votes.filter(vote_type='upvote').count()
        downvotes = votes.filter(vote_type='downvote').count()
        total = votes.count()
        
        # Check if current user has voted
        user_vote = None
        if request.user.is_authenticated:
            user_vote_obj = votes.filter(user=request.user).first()
            if user_vote_obj:
                user_vote = user_vote_obj.vote_type
        
        return Response({
            'upvotes': upvotes,
            'downvotes': downvotes,
            'total': total,
            'user_vote': user_vote,
        }, status=status.HTTP_200_OK)


class StoryArchiveViewSet(viewsets.ModelViewSet):
    """ViewSet for managing archived stories."""
    serializer_class = StoryArchiveSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Return archived stories for accessible projects."""
        project_id = self.request.query_params.get('project')
        
        queryset = StoryArchive.objects.all()
        
        if project_id:
            queryset = queryset.filter(story__project_id=project_id)
        
        return queryset.select_related('story', 'archived_by').order_by('-archived_at')
    
    def perform_create(self, serializer):
        """Set archived_by on archive creation with feature check."""
        user = self.request.user
        story = serializer.validated_data.get('story')
        
        if story and story.project:
            organization = story.project.organization
            # Check if archive feature is available
            FeatureService.is_feature_available(
                organization, 
                'projects.archive', 
                user=user, 
                raise_exception=True
            )
        
        serializer.save(archived_by=user)
    
    @extend_schema(
        description="Restore an archived story",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore an archived story."""
        archive = self.get_object()
        archive.delete()  # Deleting archive restores the story
        return Response({'message': 'Story restored successfully'}, status=status.HTTP_200_OK)


class StoryVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing story versions."""
    serializer_class = StoryVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return story versions."""
        story_id = self.request.query_params.get('story')
        
        queryset = StoryVersion.objects.all()
        
        if story_id:
            queryset = queryset.filter(story_id=story_id)
        
        return queryset.select_related('story', 'created_by').order_by('-version_number')


class WebhookViewSet(viewsets.ModelViewSet):
    """ViewSet for managing webhooks."""
    serializer_class = WebhookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return webhooks for accessible projects."""
        project_id = self.request.query_params.get('project')
        
        queryset = Webhook.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.select_related('project', 'created_by').filter(is_active=True).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by on webhook creation."""
        serializer.save(created_by=self.request.user)
    
    @extend_schema(
        description="Test a webhook",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test a webhook by sending a test event."""
        webhook = self.get_object()
        
        # Send test webhook
        try:
            import requests
            import json
            import hmac
            import hashlib
            import time
            
            payload = {
                'event': 'webhook.test',
                'timestamp': time.time(),
                'data': {'message': 'Test webhook'}
            }
            
            headers = {'Content-Type': 'application/json'}
            
            # Add signature if secret is set
            if webhook.secret:
                signature = hmac.new(
                    webhook.secret.encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256
                ).hexdigest()
                headers['X-Webhook-Signature'] = f'sha256={signature}'
            
            response = requests.post(webhook.url, json=payload, headers=headers, timeout=5)
            
            return Response({
                'status_code': response.status_code,
                'success': 200 <= response.status_code < 300,
                'message': 'Webhook test completed'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Webhook test failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StoryCloneViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing story clones."""
    serializer_class = StoryCloneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return story clones."""
        story_id = self.request.query_params.get('story')
        
        queryset = StoryClone.objects.all()
        
        if story_id:
            queryset = queryset.filter(original_story_id=story_id)
        
        return queryset.select_related('original_story', 'cloned_story', 'cloned_by').order_by('-cloned_at')


class GitHubIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing GitHub integrations."""
    serializer_class = GitHubIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Return GitHub integrations for accessible projects."""
        project_id = self.request.query_params.get('project')
        
        queryset = GitHubIntegration.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.select_related('project', 'created_by').filter(is_active=True).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by on integration creation."""
        serializer.save(created_by=self.request.user)
    
    @extend_schema(
        description="Verify GitHub connection",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify GitHub connection."""
        integration = self.get_object()
        
        try:
            from apps.projects.services.github_integration_service import GitHubIntegrationService
            result = GitHubIntegrationService.verify_connection(
                integration.access_token,
                integration.repository_owner,
                integration.repository_name
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Get GitHub issues",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['get'])
    def issues(self, request, pk=None):
        """Get issues from GitHub repository."""
        integration = self.get_object()
        state = request.query_params.get('state', 'open')
        limit = int(request.query_params.get('limit', 50))
        
        try:
            from apps.projects.services.github_integration_service import GitHubIntegrationService
            issues = GitHubIntegrationService.get_issues(
                integration.access_token,
                integration.repository_owner,
                integration.repository_name,
                state,
                limit
            )
            return Response({'issues': issues}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class JiraIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Jira integrations."""
    serializer_class = JiraIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Return Jira integrations for accessible projects."""
        project_id = self.request.query_params.get('project')
        
        queryset = JiraIntegration.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.select_related('project', 'created_by').filter(is_active=True).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by on integration creation."""
        serializer.save(created_by=self.request.user)
    
    @extend_schema(
        description="Verify Jira connection",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify Jira connection."""
        integration = self.get_object()
        
        try:
            from apps.projects.services.jira_integration_service import JiraIntegrationService
            result = JiraIntegrationService.verify_connection(
                integration.base_url,
                integration.email,
                integration.api_token
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Get Jira issues",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['get'])
    def issues(self, request, pk=None):
        """Get issues from Jira project."""
        integration = self.get_object()
        jql = request.query_params.get('jql')
        limit = int(request.query_params.get('limit', 50))
        
        try:
            from apps.projects.services.jira_integration_service import JiraIntegrationService
            issues = JiraIntegrationService.get_issues(
                integration.base_url,
                integration.email,
                integration.api_token,
                integration.project_key,
                jql,
                limit
            )
            return Response({'issues': issues}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SlackIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Slack integrations."""
    serializer_class = SlackIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Return Slack integrations for accessible projects."""
        project_id = self.request.query_params.get('project')
        
        queryset = SlackIntegration.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.select_related('project', 'created_by').filter(is_active=True).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by on integration creation."""
        serializer.save(created_by=self.request.user)
    
    @extend_schema(
        description="Verify Slack connection",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify Slack connection."""
        integration = self.get_object()
        
        try:
            from apps.projects.services.slack_integration_service import SlackIntegrationService
            result = SlackIntegrationService.verify_connection(
                integration.webhook_url,
                integration.bot_token
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Send test notification",
        responses={200: {'type': 'object'}}
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send a test notification to Slack."""
        integration = self.get_object()
        message = request.data.get('message', 'Test notification from Project Management App')
        
        try:
            from apps.projects.services.slack_integration_service import SlackIntegrationService
            
            if integration.webhook_url:
                result = SlackIntegrationService.send_message(
                    integration.webhook_url,
                    message,
                    integration.channel
                )
            elif integration.bot_token:
                result = SlackIntegrationService.post_to_channel(
                    integration.bot_token,
                    integration.channel or '#general',
                    message
                )
            else:
                return Response(
                    {'error': 'Either webhook_url or bot_token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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


class MilestoneViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing project milestones.
    """
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if not project_id:
            return Milestone.objects.none()
        
        project = Project.objects.get(pk=project_id)
        self.check_object_permissions(self.request, project)
        return Milestone.objects.filter(project_id=project_id).order_by('target_date', 'name')

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = Project.objects.get(pk=project_id)
        self.check_object_permissions(self.request, project)
        serializer.save(project=project, created_by=self.request.user)


class TicketReferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing external ticket references.
    """
    serializer_class = TicketReferenceSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if not project_id:
            return TicketReference.objects.none()
        
        project = Project.objects.get(pk=project_id)
        self.check_object_permissions(self.request, project)
        return TicketReference.objects.filter(project_id=project_id).select_related('content_type').order_by('-created_at')

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = Project.objects.get(pk=project_id)
        self.check_object_permissions(self.request, project)
        serializer.save(project=project, created_by=self.request.user)


class StoryLinkViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing story links.
    """
    serializer_class = StoryLinkSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if not project_id:
            return StoryLink.objects.none()
        
        project = Project.objects.get(pk=project_id)
        self.check_object_permissions(self.request, project)
        return StoryLink.objects.filter(project_id=project_id).select_related('source_story', 'target_story').order_by('-created_at')

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        project = Project.objects.get(pk=project_id)
        self.check_object_permissions(self.request, project)
        serializer.save(project=project, created_by=self.request.user)


class CardTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing card templates.
    Supports both project-specific and global templates.
    """
    serializer_class = CardTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            project = Project.objects.get(pk=project_id)
            self.check_object_permissions(self.request, project)
            # Return project templates and global templates
            return CardTemplate.objects.filter(
                models.Q(project_id=project_id) | models.Q(scope='global')
            ).order_by('scope', 'is_default', 'name')
        else:
            # List all global templates
            return CardTemplate.objects.filter(scope='global').order_by('is_default', 'name')

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            project = Project.objects.get(pk=project_id)
            self.check_object_permissions(self.request, project)
            serializer.save(project=project, created_by=self.request.user)
        else:
            serializer.save(scope='global', created_by=self.request.user)

    @extend_schema(
        description="Use a card template to create a story",
        request={'type': 'object', 'properties': {'template_id': {'type': 'string'}}},
        responses={201: StorySerializer}
    )
    @action(detail=True, methods=['post'], url_path='apply')
    def apply_template(self, request, pk=None):
        """Apply a card template to create a new story."""
        template = self.get_object()
        project_id = self.kwargs.get('project_pk')
        
        if not project_id:
            return Response(
                {'error': 'Project ID is required to apply template.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = Project.objects.get(pk=project_id)
        self.check_object_permissions(self.request, project)
        
        # Create story from template
        story_data = template.template_fields.copy()
        story_data['project'] = project_id
        
        serializer = StorySerializer(data=story_data, context={'request': request})
        if serializer.is_valid():
            story = serializer.save(created_by=request.user)
            # Increment usage count
            template.usage_count += 1
            template.save(update_fields=['usage_count'])
            return Response(StorySerializer(story).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BoardTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing board templates.
    Supports both project-specific and global templates.
    """
    serializer_class = BoardTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]

    def get_queryset(self):
        project_id = self.kwargs.get('project_pk')
        if project_id:
            project = Project.objects.get(pk=project_id)
            self.check_object_permissions(self.request, project)
            # Return project templates and global templates
            return BoardTemplate.objects.filter(
                models.Q(project_id=project_id) | models.Q(scope='global')
            ).order_by('scope', 'is_default', 'name')
        else:
            # List all global templates
            return BoardTemplate.objects.filter(scope='global').order_by('is_default', 'name')

    def perform_create(self, serializer):
        """Create board template with feature check."""
        project_id = self.kwargs.get('project_pk')
        user = self.request.user
        
        if project_id:
            project = Project.objects.get(pk=project_id)
            self.check_object_permissions(self.request, project)
            # Check if templates feature is available
            organization = project.organization
            FeatureService.is_feature_available(
                organization, 
                'projects.templates', 
                user=user, 
                raise_exception=True
            )
            serializer.save(project=project, created_by=user)
        else:
            # Global templates - need to check user's organization
            organization = RoleService.get_user_organization(user)
            if organization:
                FeatureService.is_feature_available(
                    organization, 
                    'projects.templates', 
                    user=user, 
                    raise_exception=True
                )
            serializer.save(scope='global', created_by=user)

    @extend_schema(
        description="Apply a board template to project configuration",
        request={'type': 'object', 'properties': {'template_id': {'type': 'string'}}},
        responses={200: ProjectConfigurationSerializer}
    )
    @action(detail=True, methods=['post'], url_path='apply')
    def apply_template(self, request, pk=None):
        """Apply a board template to project configuration."""
        template = self.get_object()
        project_id = self.kwargs.get('project_pk')
        
        if not project_id:
            return Response(
                {'error': 'Project ID is required to apply template.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = Project.objects.get(pk=project_id)
        self.check_object_permissions(self.request, project)
        
        # Get or create project configuration
        config, created = ProjectConfiguration.objects.get_or_create(project=project)
        
        # Apply board template configuration
        board_config = template.board_config.copy()
        if 'board_columns' in board_config:
            config.board_columns = board_config['board_columns']
        if 'swimlane_grouping' in board_config:
            config.swimlane_grouping = board_config['swimlane_grouping']
        if 'card_display_fields' in board_config:
            config.card_display_fields = board_config['card_display_fields']
        if 'card_color_by' in board_config:
            config.card_color_by = board_config['card_color_by']
        
        config.save()
        
        # Increment usage count
        template.usage_count += 1
        template.save(update_fields=['usage_count'])
        
        return Response(ProjectConfigurationSerializer(config).data, status=status.HTTP_200_OK)


class ProjectLabelPresetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing project label presets."""
    serializer_class = ProjectLabelPresetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return label presets for projects the user has access to."""
        user = self.request.user
        project_id = self.request.query_params.get('project')
        
        # Get projects the user has access to
        user_projects = Project.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()
        
        # Start with all presets for user's projects
        queryset = ProjectLabelPreset.objects.filter(project__in=user_projects)
        
        # Filter by specific project if provided
        if project_id:
            # Verify user has access to this project
            if user_projects.filter(id=project_id).exists():
                queryset = queryset.filter(project_id=project_id)
            else:
                # User doesn't have access, return empty queryset
                return ProjectLabelPreset.objects.none()
        
        return queryset.select_related('project', 'created_by', 'updated_by').order_by('is_default', 'name')
    
    def perform_create(self, serializer):
        """Set created_by and updated_by on create."""
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set updated_by on update."""
        serializer.save(updated_by=self.request.user)


class StatisticsViewSet(viewsets.ViewSet):
    """
    API endpoints for project statistics and analytics.
    Provides various analytics for stories, components, and team performance.
    """
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    
    from apps.projects.services.statistics_service import StatisticsService
    
    def get_organization(self):
        """Get user's organization."""
        return RoleService.get_user_organization(self.request.user)
    
    def get_project(self):
        """Get and validate project from URL or query parameters."""
        # Try to get project ID from URL kwargs first (nested routes)
        project_id = self.kwargs.get('project_pk') or self.kwargs.get('pk')
        
        # If not in kwargs, try query parameters (for non-nested routes)
        if not project_id:
            project_id = self.request.query_params.get('project')
            # Also try 'project_id' as an alternative parameter name
            if not project_id:
                project_id = self.request.query_params.get('project_id')
        
        if not project_id:
            from rest_framework import serializers
            # Debug: log what we received
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"StatisticsViewSet.get_project: kwargs={self.kwargs}, query_params={dict(self.request.query_params)}")
            raise serializers.ValidationError("Project ID is required. Please provide 'project' as a query parameter or in the URL.")
        
        try:
            project = Project.objects.get(pk=project_id)
            self.check_object_permissions(self.request, project)
            return project
        except Project.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
        except ValueError:
            from rest_framework import serializers
            raise serializers.ValidationError(f"Invalid project ID format: {project_id}")
    
    @extend_schema(
        description="Get story type distribution for a project",
        responses={200: {'type': 'object', 'additionalProperties': {'type': 'integer'}}}
    )
    @action(detail=False, methods=['get'], url_path='story-type-distribution')
    def story_type_distribution(self, request, project_pk=None):
        """Get story type distribution - requires analytics.basic."""
        project = self.get_project()
        organization = self.get_organization()
        if organization:
            FeatureService.is_feature_available(
                organization, 
                'analytics.basic', 
                user=request.user, 
                raise_exception=True
            )
        from apps.projects.services.statistics_service import StatisticsService
        service = StatisticsService()
        data = service.get_story_type_distribution(str(project.id))
        return Response(data)
    
    @extend_schema(
        description="Get component distribution for a project",
        responses={200: {'type': 'object', 'additionalProperties': {'type': 'integer'}}}
    )
    @action(detail=False, methods=['get'], url_path='component-distribution')
    def component_distribution(self, request, project_pk=None):
        """Get component distribution - requires analytics.basic."""
        project = self.get_project()
        organization = self.get_organization()
        if organization:
            FeatureService.is_feature_available(
                organization, 
                'analytics.basic', 
                user=request.user, 
                raise_exception=True
            )
        from apps.projects.services.statistics_service import StatisticsService
        service = StatisticsService()
        data = service.get_component_distribution(str(project.id))
        return Response(data)
    
    @extend_schema(
        description="Get story type creation trends over time",
        parameters=[
            {'name': 'days', 'in': 'query', 'type': 'integer', 'default': 30, 'description': 'Number of days for the trend'}
        ],
        responses={200: {'type': 'array', 'items': {'type': 'object'}}}
    )
    @action(detail=False, methods=['get'], url_path='story-type-trends')
    def story_type_trends(self, request, project_pk=None):
        """Get story type trends - requires analytics.advanced."""
        project = self.get_project()
        organization = self.get_organization()
        if organization:
            FeatureService.is_feature_available(
                organization, 
                'analytics.advanced', 
                user=request.user, 
                raise_exception=True
            )
        from apps.projects.services.statistics_service import StatisticsService
        service = StatisticsService()
        days = int(request.query_params.get('days', 30))
        data = service.get_story_type_trends(str(project.id), days)
        return Response(data)
    
    @extend_schema(
        description="Get component usage trends over time",
        parameters=[
            {'name': 'days', 'in': 'query', 'type': 'integer', 'default': 30, 'description': 'Number of days for the trend'}
        ],
        responses={200: {'type': 'array', 'items': {'type': 'object'}}}
    )
    @action(detail=False, methods=['get'], url_path='component-trends')
    def component_trends(self, request, project_pk=None):
        """Get component trends."""
        project = self.get_project()
        from apps.projects.services.statistics_service import StatisticsService
        service = StatisticsService()
        days = int(request.query_params.get('days', 30))
        data = service.get_component_trends(str(project.id), days)
        return Response(data)
    
    @extend_schema(
        description="Get cycle time metrics (time from start to completion)",
        parameters=[
            {'name': 'days', 'in': 'query', 'type': 'integer', 'default': 90, 'description': 'Number of days to analyze'}
        ],
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='cycle-time')
    def cycle_time(self, request, project_pk=None):
        """Get cycle time analytics - requires analytics.advanced."""
        project = self.get_project()
        organization = self.get_organization()
        if organization:
            FeatureService.is_feature_available(
                organization, 
                'analytics.advanced', 
                user=request.user, 
                raise_exception=True
            )
        days = int(request.query_params.get('days', 90))
        data = asyncio.run(analytics.calculate_cycle_time(str(project.id), days))
        return Response(data)
    
    @extend_schema(
        description="Get lead time metrics (time from creation to completion)",
        parameters=[
            {'name': 'days', 'in': 'query', 'type': 'integer', 'default': 90, 'description': 'Number of days to analyze'}
        ],
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='lead-time')
    def lead_time(self, request, project_pk=None):
        """Get lead time analytics."""
        project = self.get_project()
        days = int(request.query_params.get('days', 90))
        data = asyncio.run(analytics.calculate_lead_time(str(project.id), days))
        return Response(data)
    
    @extend_schema(
        description="Get throughput metrics (stories completed per time period)",
        parameters=[
            {'name': 'days', 'in': 'query', 'type': 'integer', 'default': 30, 'description': 'Number of days to analyze'}
        ],
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='throughput')
    def throughput(self, request, project_pk=None):
        """Get throughput analytics."""
        project = self.get_project()
        days = int(request.query_params.get('days', 30))
        data = asyncio.run(analytics.calculate_throughput(str(project.id), days))
        return Response(data)
    
    @extend_schema(
        description="Get project health metrics",
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='project-health')
    def project_health(self, request, project_pk=None):
        """Get project health analytics."""
        project = self.get_project()
        data = asyncio.run(analytics.calculate_project_health(str(project.id)))
        return Response(data)
    
    @extend_schema(
        description="Get team performance metrics",
        parameters=[
            {'name': 'days', 'in': 'query', 'type': 'integer', 'default': 90, 'description': 'Number of days to analyze'}
        ],
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='team-performance')
    def team_performance(self, request, project_pk=None):
        """Get team performance analytics."""
        project = self.get_project()
        days = int(request.query_params.get('days', 90))
        data = asyncio.run(analytics.calculate_team_performance(str(project.id), days))
        return Response(data)
    
    @extend_schema(
        description="Get time reports for a project",
        parameters=[
            {'name': 'start_date', 'in': 'query', 'type': 'string', 'format': 'date'},
            {'name': 'end_date', 'in': 'query', 'type': 'string', 'format': 'date'},
            {'name': 'user_id', 'in': 'query', 'type': 'string', 'format': 'uuid'},
        ],
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='time-reports')
    def time_reports(self, request, project_pk=None):
        """Get time reports - requires analytics.basic."""
        organization = self.get_organization()
        if organization:
            FeatureService.is_feature_available(
                organization, 
                'analytics.basic', 
                user=request.user, 
                raise_exception=True
            )
        project = self.get_project()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        user_id = request.query_params.get('user_id')
        
        from datetime import datetime as dt
        try:
            start = dt.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else None
        except:
            try:
                start = dt.strptime(start_date, '%Y-%m-%d') if start_date else None
            except:
                start = None
        try:
            end = dt.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
        except:
            try:
                end = dt.strptime(end_date, '%Y-%m-%d') if end_date else None
            except:
                end = None
        
        data = ReportsService.get_time_reports(str(project.id), start, end, user_id)
        return Response(data)
    
    @extend_schema(
        description="Get burndown chart data for a sprint",
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='burndown-chart')
    def burndown_chart(self, request, project_pk=None):
        """Get burndown chart data - requires analytics.advanced."""
        organization = self.get_organization()
        if organization:
            FeatureService.is_feature_available(
                organization, 
                'analytics.advanced', 
                user=request.user, 
                raise_exception=True
            )
        sprint_id = request.query_params.get('sprint_id')
        if not sprint_id:
            return Response({'error': 'sprint_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = ReportsService.get_burndown_chart(sprint_id)
        if data:
            return Response(data)
        return Response({'error': 'Sprint not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @extend_schema(
        description="Get velocity tracking across sprints",
        parameters=[
            {'name': 'num_sprints', 'in': 'query', 'type': 'integer', 'default': 5},
        ],
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='velocity-tracking')
    def velocity_tracking(self, request, project_pk=None):
        """Get velocity tracking - requires analytics.advanced."""
        organization = self.get_organization()
        if organization:
            FeatureService.is_feature_available(
                organization, 
                'analytics.advanced', 
                user=request.user, 
                raise_exception=True
            )
        project = self.get_project()
        num_sprints = int(request.query_params.get('num_sprints', 5))
        data = ReportsService.get_velocity_tracking(str(project.id), num_sprints)
        return Response(data)
    
    @extend_schema(
        description="Get estimation history for stories",
        parameters=[
            {'name': 'story_id', 'in': 'query', 'type': 'string', 'format': 'uuid'},
        ],
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='estimation-history')
    def estimation_history(self, request, project_pk=None):
        """Get estimation history."""
        project = self.get_project()
        story_id = request.query_params.get('story_id')
        data = ReportsService.get_estimation_history(str(project.id), story_id)
        return Response(data)
    
    @extend_schema(
        description="Compare actual time vs estimated time",
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='actual-vs-estimated')
    def actual_vs_estimated(self, request, project_pk=None):
        """Get actual vs estimated comparison."""
        project = self.get_project()
        data = ReportsService.get_actual_vs_estimated(str(project.id))
        return Response(data)
    
    @extend_schema(
        description="Get epic progress tracking",
        parameters=[
            {'name': 'epic_id', 'in': 'query', 'type': 'string', 'format': 'uuid'},
        ],
        responses={200: {'type': 'object'}}
    )
    @action(detail=False, methods=['get'], url_path='epic-progress')
    def epic_progress(self, request, project_pk=None):
        """Get epic progress."""
        project = self.get_project()
        epic_id = request.query_params.get('epic_id')
        data = ReportsService.get_epic_progress(str(project.id), epic_id)
        return Response(data)


class ProjectMemberViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing project members and their roles.
    Supports creating, updating, and deleting project members with multiple roles.
    """
    serializer_class = ProjectMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    queryset = ProjectMember.objects.all()
    
    def get_queryset(self):
        """Filter queryset by project if project_id is provided."""
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset.select_related('project', 'user', 'added_by')
    
    def perform_create(self, serializer):
        """Set added_by to current user when creating a project member."""
        user = self.request.user
        project = serializer.validated_data.get('project')
        
        # Check if custom roles feature is required (only if custom roles are being used)
        if project:
            organization = RoleService.get_user_organization(user)
            if organization:
                # Get project configuration to check for custom roles
                try:
                    from apps.projects.models import ProjectConfiguration
                    config = ProjectConfiguration.objects.filter(project=project).first()
                    
                    # Get all available roles (system + custom)
                    available_roles = RoleService.get_all_available_roles(project)
                    system_roles = RoleService.get_all_system_roles()
                    custom_roles = [r for r in available_roles if r not in system_roles]
                    
                    # If custom roles exist and are being used, check feature
                    roles = serializer.validated_data.get('roles', [])
                    if custom_roles and any(role in custom_roles for role in roles):
                        FeatureService.is_feature_available(
                            organization, 
                            'users.roles', 
                            user=user, 
                            raise_exception=True
                        )
                except Exception:
                    # If we can't check, allow but log warning
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Could not verify custom roles feature for project {project.id}")
        
        serializer.save(added_by=user)
    
    @extend_schema(
        description="Get all members for a specific project",
        parameters=[
            {'name': 'project', 'in': 'query', 'type': 'string', 'format': 'uuid', 'required': True},
        ],
        responses={200: ProjectMemberSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='by-project')
    def by_project(self, request):
        """Get all members for a specific project."""
        project_id = request.query_params.get('project')
        if not project_id:
            return Response(
                {'error': 'project parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            project = Project.objects.get(pk=project_id)
            self.check_object_permissions(request, project)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        members = ProjectMember.objects.filter(project=project).select_related('user', 'added_by')
        serializer = self.get_serializer(members, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        description="Get all projects for a specific user",
        parameters=[
            {'name': 'user', 'in': 'query', 'type': 'string', 'format': 'uuid', 'required': True},
        ],
        responses={200: ProjectMemberSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='by-user')
    def by_user(self, request):
        """Get all projects for a specific user."""
        user_id = request.query_params.get('user')
        if not user_id:
            return Response(
                {'error': 'user parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Only allow users to see their own memberships, or admins to see any
        if str(request.user.id) != user_id and not request.user.is_superuser:
            return Response(
                {'error': 'You can only view your own project memberships'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        members = ProjectMember.objects.filter(user_id=user_id).select_related('project', 'user', 'added_by')
        serializer = self.get_serializer(members, many=True)
        return Response(serializer.data)


class GeneratedProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for GeneratedProject model.
    
    Provides CRUD operations for generated projects with proper permission filtering.
    """
    serializer_class = GeneratedProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Filter generated projects based on user permissions."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return GeneratedProject.objects.none()
        
        queryset = GeneratedProject.objects.select_related(
            'project', 'project__owner', 'project__organization',
            'workflow_execution', 'created_by'
        ).prefetch_related('files', 'exports')
        
        # Super admins see everything
        if RoleService.is_super_admin(user):
            return queryset
        
        # Filter by project access
        # Get user's accessible projects
        user_orgs = RoleService.get_user_organizations(user)
        if not user_orgs and user.organization:
            user_orgs = [user.organization]
        
        if not user_orgs:
            return GeneratedProject.objects.none()
        
        # Get projects user can access
        accessible_projects = Project.objects.filter(
            models.Q(organization_id__in=[org.id for org in user_orgs]),
            models.Q(owner=user) | models.Q(members__id=user.id)
        ).distinct()
        
        # Filter by project
        project_id = self.request.query_params.get('project')
        if project_id:
            accessible_projects = accessible_projects.filter(id=project_id)
        
        queryset = queryset.filter(project__in=accessible_projects)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)
    
    @extend_schema(
        description="Generate a new project from workflow",
        request=ProjectGenerationRequestSerializer,
        responses={201: GeneratedProjectSerializer}
    )
    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """Generate a project from a workflow."""
        from apps.workflows.models import Workflow, WorkflowExecution
        from apps.projects.tasks import generate_project_task
        import uuid
        
        serializer = ProjectGenerationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        workflow_id = serializer.validated_data['workflow_id']
        input_data = serializer.validated_data['input_data']
        
        try:
            workflow = Workflow.objects.get(id=workflow_id)
        except Workflow.DoesNotExist:
            return Response(
                {'error': 'Workflow not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get project from input_data or request
        project_id = input_data.get('project_id') or request.data.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            project = Project.objects.get(id=project_id)
            # Check permissions
            self.check_object_permissions(request, project)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create GeneratedProject
        output_dir = Path(settings.GENERATED_PROJECTS_DIR) / str(uuid.uuid4())
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_project = GeneratedProject.objects.create(
            project=project,
            output_directory=str(output_dir),
            status='pending',
            created_by=request.user
        )
        
        # Execute workflow asynchronously via Celery task
        try:
            # Start async task
            task = generate_project_task.delay(
                generated_project_id=str(generated_project.id),
                workflow_id=str(workflow.id),
                input_data=input_data,
                user_id=str(request.user.id)
            )
            
            generated_project.status = 'generating'
            generated_project.save()
            
            serializer_response = GeneratedProjectSerializer(generated_project)
            return Response(
                {
                    **serializer_response.data,
                    'task_id': task.id,
                    'message': 'Project generation started'
                },
                status=status.HTTP_202_ACCEPTED
            )
            
        except Exception as e:
            generated_project.status = 'failed'
            generated_project.error_message = str(e)
            generated_project.save()
            
            return Response(
                {'error': f'Failed to start generation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProjectFileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ProjectFile model (read-only for security).
    
    Provides read access to generated project files.
    """
    serializer_class = ProjectFileSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Filter files based on user's access to generated projects."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return ProjectFile.objects.none()
        
        queryset = ProjectFile.objects.select_related(
            'generated_project', 'generated_project__project'
        )
        
        # Get accessible generated projects (same logic as GeneratedProjectViewSet)
        if RoleService.is_super_admin(user):
            pass  # See all files
        else:
            user_orgs = RoleService.get_user_organizations(user)
            if not user_orgs and user.organization:
                user_orgs = [user.organization]
            
            if not user_orgs:
                return ProjectFile.objects.none()
            
            accessible_projects = Project.objects.filter(
                models.Q(organization_id__in=[org.id for org in user_orgs]),
                models.Q(owner=user) | models.Q(members__id=user.id)
            ).distinct()
            
            accessible_generated = GeneratedProject.objects.filter(
                project__in=accessible_projects
            )
            
            queryset = queryset.filter(generated_project__in=accessible_generated)
        
        # Filter by generated_project
        generated_project_id = self.request.query_params.get('generated_project')
        if generated_project_id:
            queryset = queryset.filter(generated_project_id=generated_project_id)
        
        # Filter by file_type
        file_type = self.request.query_params.get('file_type')
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        
        return queryset.order_by('file_path')
    
    @extend_schema(
        description="Get file content",
        responses={200: {'type': 'object', 'properties': {'content': {'type': 'string'}}}}
    )
    @action(detail=True, methods=['get'], url_path='content')
    def content(self, request, pk=None):
        """Get full file content."""
        project_file = self.get_object()
        
        # Security check - ensure user can access the generated project
        self.check_object_permissions(request, project_file.generated_project.project)
        
        # Read file from disk
        generated_project = project_file.generated_project
        file_path = Path(generated_project.output_directory) / project_file.file_path
        
        if not file_path.exists():
            return Response(
                {'error': 'File not found on disk'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return Response({
                'content': content,
                'file_path': project_file.file_path,
                'file_name': project_file.file_name,
                'file_type': project_file.file_type,
                'file_size': project_file.file_size
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to read file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RepositoryExportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RepositoryExport model.
    
    Provides CRUD operations for repository exports.
    """
    serializer_class = RepositoryExportSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrReadOnly]
    
    def get_queryset(self):
        """Filter exports based on user's access to generated projects."""
        user = self.request.user
        if not user or not user.is_authenticated:
            return RepositoryExport.objects.none()
        
        queryset = RepositoryExport.objects.select_related(
            'generated_project', 'generated_project__project', 'created_by'
        )
        
        # Get accessible generated projects
        if RoleService.is_super_admin(user):
            pass
        else:
            user_orgs = RoleService.get_user_organizations(user)
            if not user_orgs and user.organization:
                user_orgs = [user.organization]
            
            if not user_orgs:
                return RepositoryExport.objects.none()
            
            accessible_projects = Project.objects.filter(
                models.Q(organization_id__in=[org.id for org in user_orgs]),
                models.Q(owner=user) | models.Q(members__id=user.id)
            ).distinct()
            
            accessible_generated = GeneratedProject.objects.filter(
                project__in=accessible_projects
            )
            
            queryset = queryset.filter(generated_project__in=accessible_generated)
        
        # Filter by generated_project
        generated_project_id = self.request.query_params.get('generated_project')
        if generated_project_id:
            queryset = queryset.filter(generated_project_id=generated_project_id)
        
        # Filter by export_type
        export_type = self.request.query_params.get('export_type')
        if export_type:
            queryset = queryset.filter(export_type=export_type)
        
        # Filter by status
        export_status = self.request.query_params.get('status')
        if export_status:
            queryset = queryset.filter(status=export_status)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by to current user with import/export feature check."""
        user = self.request.user
        generated_project = serializer.validated_data.get('generated_project')
        
        if generated_project and generated_project.project:
            organization = generated_project.project.organization
            # Check if import/export feature is available
            FeatureService.is_feature_available(
                organization, 
                'projects.import_export', 
                user=user, 
                raise_exception=True
            )
        
        serializer.save(created_by=user)
    
    @extend_schema(
        description="Export project as ZIP archive",
        responses={201: RepositoryExportSerializer}
    )
    @action(detail=False, methods=['post'], url_path='export-zip')
    def export_zip(self, request):
        """Export a generated project as ZIP."""
        generated_project_id = request.data.get('generated_project_id')
        if not generated_project_id:
            return Response(
                {'error': 'generated_project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            generated_project = GeneratedProject.objects.get(id=generated_project_id)
            # Check permissions
            self.check_object_permissions(request, generated_project.project)
            
            # Check if import/export feature is available
            organization = generated_project.project.organization
            FeatureService.is_feature_available(
                organization, 
                'projects.import_export', 
                user=request.user, 
                raise_exception=True
            )
            # Also check analytics export feature for report exports
            FeatureService.is_feature_available(
                organization, 
                'analytics.export_reports', 
                user=request.user, 
                raise_exception=True
            )
        except GeneratedProject.DoesNotExist:
            return Response(
                {'error': 'Generated project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create export record
        export = RepositoryExport.objects.create(
            generated_project=generated_project,
            export_type='zip',
            status='exporting',
            created_by=request.user
        )
        
        # Use Celery task for async export
        from apps.projects.tasks import export_repository_task
        
        try:
            task = export_repository_task.delay(
                export_id=str(export.id),
                export_type='zip',
                config={}
            )
            
            serializer_response = RepositoryExportSerializer(export)
            return Response(
                {
                    **serializer_response.data,
                    'task_id': task.id,
                    'message': 'Export started'
                },
                status=status.HTTP_202_ACCEPTED
            )
            
        except Exception as e:
            export.status = 'failed'
            export.error_message = str(e)
            export.save()
            
            return Response(
                {'error': f'Failed to start export: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Export project to GitHub",
        request=GitHubExportRequestSerializer,
        responses={201: RepositoryExportSerializer}
    )
    @action(detail=False, methods=['post'], url_path='export-github')
    def export_github(self, request):
        """Export a generated project to GitHub."""
        serializer = GitHubExportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        generated_project_id = request.data.get('generated_project_id')
        if not generated_project_id:
            return Response(
                {'error': 'generated_project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            generated_project = GeneratedProject.objects.get(id=generated_project_id)
            self.check_object_permissions(request, generated_project.project)
            
            # Check if import/export feature is available
            organization = generated_project.project.organization
            FeatureService.is_feature_available(
                organization, 
                'projects.import_export', 
                user=request.user, 
                raise_exception=True
            )
            # Also check analytics export feature for report exports
            FeatureService.is_feature_available(
                organization, 
                'analytics.export_reports', 
                user=request.user, 
                raise_exception=True
            )
        except GeneratedProject.DoesNotExist:
            return Response(
                {'error': 'Generated project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        github_token = serializer.validated_data.get('github_token') or request.data.get('github_token')
        if not github_token:
            return Response(
                {'error': 'github_token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create export record
        export = RepositoryExport.objects.create(
            generated_project=generated_project,
            export_type='github',
            repository_name=serializer.validated_data['repository_name'],
            status='exporting',
            config={
                'github_token': github_token,
                'repository_name': serializer.validated_data['repository_name'],
                'organization': serializer.validated_data.get('organization'),
                'private': serializer.validated_data.get('private', False)
            },
            created_by=request.user
        )
        
        # Use Celery task for async export
        from apps.projects.tasks import export_repository_task
        
        try:
            task = export_repository_task.delay(
                export_id=str(export.id),
                export_type='github',
                config=export.config
            )
            
            serializer_response = RepositoryExportSerializer(export)
            return Response(
                {
                    **serializer_response.data,
                    'task_id': task.id,
                    'message': 'GitHub export started'
                },
                status=status.HTTP_202_ACCEPTED
            )
            
        except Exception as e:
            export.status = 'failed'
            export.error_message = str(e)
            export.save()
            
            return Response(
                {'error': f'Failed to start export: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Export project to GitLab",
        request=GitLabExportRequestSerializer,
        responses={202: RepositoryExportSerializer}
    )
    @action(detail=False, methods=['post'], url_path='export-gitlab')
    def export_gitlab(self, request):
        """Export a generated project to GitLab."""
        # Feature checks will be done after getting generated_project
        serializer = GitLabExportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        generated_project_id = request.data.get('generated_project_id')
        if not generated_project_id:
            return Response(
                {'error': 'generated_project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            generated_project = GeneratedProject.objects.get(id=generated_project_id)
            self.check_object_permissions(request, generated_project.project)
            
            # Check if import/export feature is available
            organization = generated_project.project.organization
            FeatureService.is_feature_available(
                organization, 
                'projects.import_export', 
                user=request.user, 
                raise_exception=True
            )
            # Also check analytics export feature for report exports
            FeatureService.is_feature_available(
                organization, 
                'analytics.export_reports', 
                user=request.user, 
                raise_exception=True
            )
        except GeneratedProject.DoesNotExist:
            return Response(
                {'error': 'Generated project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        gitlab_token = serializer.validated_data.get('gitlab_token') or request.data.get('gitlab_token')
        if not gitlab_token:
            return Response(
                {'error': 'gitlab_token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create export record
        export = RepositoryExport.objects.create(
            generated_project=generated_project,
            export_type='gitlab',
            repository_name=serializer.validated_data['project_name'],
            status='exporting',
            config={
                'gitlab_token': gitlab_token,
                'project_name': serializer.validated_data['project_name'],
                'namespace': serializer.validated_data.get('namespace'),
                'visibility': serializer.validated_data.get('visibility', 'private')
            },
            created_by=request.user
        )
        
        # Use Celery task for async export
        from apps.projects.tasks import export_repository_task
        
        try:
            task = export_repository_task.delay(
                export_id=str(export.id),
                export_type='gitlab',
                config=export.config
            )
            
            serializer_response = RepositoryExportSerializer(export)
            return Response(
                {
                    **serializer_response.data,
                    'task_id': task.id,
                    'message': 'GitLab export started'
                },
                status=status.HTTP_202_ACCEPTED
            )
            
        except Exception as e:
            export.status = 'failed'
            export.error_message = str(e)
            export.save()
            
            return Response(
                {'error': f'Failed to start export: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        description="Download export archive",
        responses={200: {'description': 'File download'}}
    )
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """Download export archive."""
        from django.http import FileResponse
        
        export = self.get_object()
        
        if export.status != 'completed' or not export.archive_path:
            return Response(
                {'error': 'Export not ready for download'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        archive_path = Path(export.archive_path)
        if not archive_path.exists():
            return Response(
                {'error': 'Archive file not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return FileResponse(
            open(archive_path, 'rb'),
            as_attachment=True,
            filename=archive_path.name
        )
