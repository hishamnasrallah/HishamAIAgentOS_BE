"""
Project Management API Serializers

Serializers for AI Project Management endpoints.
"""

from rest_framework import serializers
from apps.projects.models import (
    Project, Sprint, UserStory, Epic, Task, Bug, Issue, TimeLog, ProjectConfiguration, 
    Mention, StoryComment, StoryDependency, StoryAttachment, Notification, Watcher, Activity, EditHistory, SavedSearch
)
# Alias for backward compatibility
Story = UserStory


class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer."""
    
    # Make slug optional - will auto-generate from name
    slug = serializers.SlugField(required=False)
    # Make description optional
    description = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True},
        }
    
    def create(self, validated_data):
        # Auto-generate slug from name if not provided
        if 'slug' not in validated_data or not validated_data.get('slug'):
            from django.utils.text import slugify
            base_slug = slugify(validated_data['name'])
            slug = base_slug
            # Handle slug uniqueness
            counter = 1
            while Project.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            validated_data['slug'] = slug
        # Ensure description defaults to empty string if not provided
        if 'description' not in validated_data:
            validated_data['description'] = ''
        return super().create(validated_data)


class SprintSerializer(serializers.ModelSerializer):
    """Sprint serializer."""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Sprint
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate sprint dates against project dates and check for overlaps."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Get project from instance (update) or validated_data (create)
        project = None
        if self.instance:
            project = self.instance.project
        elif 'project' in data:
            project = data['project']
        elif 'project' in self.initial_data:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=self.initial_data['project'])
            except (Project.DoesNotExist, ValueError):
                pass
        
        if not project:
            # If we can't get the project, let the model validation handle it
            return data
        
        # Validate sprint dates are within project dates (if project has dates)
        if project.start_date and start_date:
            if start_date < project.start_date:
                raise serializers.ValidationError({
                    'start_date': f'Sprint start date must be on or after project start date ({project.start_date}).'
                })
        
        if project.end_date and end_date:
            if end_date > project.end_date:
                raise serializers.ValidationError({
                    'end_date': f'Sprint end date must be on or before project end date ({project.end_date}).'
                })
        
        # Validate sprint start_date < end_date
        if start_date and end_date:
            if start_date >= end_date:
                raise serializers.ValidationError({
                    'end_date': 'Sprint end date must be after start date.'
                })
        
        # Check for overlapping sprints
        if start_date and end_date:
            # Get all sprints for this project (excluding the current one if updating)
            existing_sprints = Sprint.objects.filter(project=project)
            if self.instance:
                existing_sprints = existing_sprints.exclude(id=self.instance.id)
            
            # Check for overlaps
            overlapping_sprints = existing_sprints.filter(
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            if overlapping_sprints.exists():
                overlapping_sprint = overlapping_sprints.first()
                raise serializers.ValidationError({
                    'start_date': f'This sprint overlaps with "{overlapping_sprint.name}" ({overlapping_sprint.start_date} - {overlapping_sprint.end_date}).',
                    'end_date': f'This sprint overlaps with "{overlapping_sprint.name}" ({overlapping_sprint.start_date} - {overlapping_sprint.end_date}).'
                })
        
        return data


class StoryGenerationRequestSerializer(serializers.Serializer):
    """Request serializer for story generation."""
    
    product_vision = serializers.CharField(
        help_text="High-level product vision or feature description"
    )
    context = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Additional context (target users, constraints, etc.)"
    )
    epic_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Optional epic to associate stories with"
    )


class StorySerializer(serializers.ModelSerializer):
    """Story serializer."""
    
    epic_name = serializers.CharField(source='epic.title', read_only=True, allow_null=True)
    sprint_name = serializers.CharField(source='sprint.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Story
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'generated_by_ai', 'generation_workflow', 'created_by']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'acceptance_criteria': {'required': False},
            'story_points': {'required': False, 'allow_null': True},
            'status': {'required': False},
            'priority': {'required': False},
            'epic': {'required': False, 'allow_null': True},
            'sprint': {'required': False, 'allow_null': True},
            'assigned_to': {'required': False, 'allow_null': True},
            'component': {'required': False, 'allow_null': True, 'allow_blank': True},
            'due_date': {'required': False, 'allow_null': True},
            'tags': {'required': False, 'allow_null': True},
            'labels': {'required': False, 'allow_null': True},
        }
    
    def validate_status(self, value):
        """Validate status against project configuration."""
        if not value:
            return value
        
        # Get project from instance (update) or validated_data (create)
        project = None
        if self.instance:
            project = self.instance.project
        elif 'project' in self.initial_data:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=self.initial_data['project'])
            except (Project.DoesNotExist, ValueError):
                pass
        
        if project:
            try:
                config = project.configuration
                if config and config.custom_states:
                    valid_statuses = [state.get('id') for state in config.custom_states if state.get('id')]
                    if value not in valid_statuses:
                        raise serializers.ValidationError(
                            f"Invalid status '{value}'. Valid statuses for this project are: {', '.join(valid_statuses)}"
                        )
            except ProjectConfiguration.DoesNotExist:
                pass  # No configuration yet, allow default status
        
        return value
    
    def update(self, instance, validated_data):
        """Override update to ensure all fields are saved, including null values, and validate."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[StorySerializer] Updating story {instance.id}")
        logger.info(f"[StorySerializer] Validated data: {validated_data}")
        
        # Convert null component to empty string (CharField doesn't accept null)
        if 'component' in validated_data and validated_data['component'] is None:
            validated_data['component'] = ''
        
        # Validate using project validation rules before updating
        if instance.project:
            from apps.projects.services.validation import get_validation_service
            validation_service = get_validation_service(instance.project)
            
            # Check if status is being changed
            new_status = validated_data.get('status', instance.status)
            old_status = instance.status
            
            if new_status != old_status:
                is_valid, error, warnings = validation_service.validate_story_before_status_change(
                    instance,
                    new_status,
                    old_status
                )
                if not is_valid:
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError(error)
                if warnings:
                    logger.warning(f"[StorySerializer] Validation warnings: {', '.join(warnings)}")
            
            # Validate other updates
            is_valid, error, warnings = validation_service.validate_story_update(instance, validated_data)
            if not is_valid:
                from rest_framework.exceptions import ValidationError
                raise ValidationError(error)
            if warnings:
                logger.warning(f"[StorySerializer] Validation warnings: {', '.join(warnings)}")
        
        # Get raw request data to check for explicitly null fields
        request = self.context.get('request')
        raw_data = {}
        if request:
            raw_data = dict(request.data)  # Convert to dict to ensure we can iterate
            logger.info(f"[StorySerializer] Raw request data: {raw_data}")
        
        # Fields that can be null and need explicit handling
        nullable_fields = ['story_points', 'epic', 'sprint', 'assigned_to']
        all_fields = ['title', 'description', 'acceptance_criteria', 'priority', 'status', 'component', 'due_date', 'tags', 'labels', 'story_type'] + nullable_fields
        
        # Update all fields - prioritize validated_data, then check raw_data
        for field in all_fields:
            if field in validated_data:
                # Field has a value (including None if explicitly set)
                # Special handling for component: convert None to empty string
                value = validated_data[field]
                if field == 'component' and value is None:
                    value = ''
                setattr(instance, field, value)
                logger.info(f"[StorySerializer] Set {field} = {value} (from validated_data)")
            elif field in raw_data:
                # Field was in request but not in validated_data - check if it's null
                raw_value = raw_data[field]
                if raw_value is None or raw_value == '' or raw_value == 'null' or (isinstance(raw_value, str) and raw_value.lower() == 'null'):
                    if field in nullable_fields:
                        setattr(instance, field, None)
                        logger.info(f"[StorySerializer] Explicitly set {field} = None (from raw_data, was: {raw_value})")
                    elif field == 'component':
                        # Component is CharField, convert null to empty string
                        setattr(instance, field, '')
                        logger.info(f"[StorySerializer] Explicitly set {field} = '' (from raw_data, was: {raw_value})")
                else:
                    # Field has a value in raw_data but wasn't validated - try to use it
                    # This can happen if the value is valid but serializer didn't include it
                    if field in nullable_fields:
                        # For foreign keys, the value should be a UUID string
                        try:
                            setattr(instance, field, raw_value)
                            logger.info(f"[StorySerializer] Set {field} = {raw_value} (from raw_data, not in validated_data)")
                        except Exception as e:
                            logger.warning(f"[StorySerializer] Could not set {field} = {raw_value}: {e}")
                    elif field == 'component':
                        # Component is CharField
                        setattr(instance, field, str(raw_value) if raw_value else '')
                        logger.info(f"[StorySerializer] Set {field} = {raw_value} (from raw_data, not in validated_data)")
        
        instance.save()
        logger.info(f"[StorySerializer] Story saved. Story points: {instance.story_points}, Assigned to: {instance.assigned_to}, Epic: {instance.epic}, Sprint: {instance.sprint}")
        return instance
    
    def create(self, validated_data):
        """Override create to ensure all fields are saved and validate."""
        # Convert null component to empty string (CharField doesn't accept null)
        if 'component' in validated_data and validated_data['component'] is None:
            validated_data['component'] = ''
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[StorySerializer] Creating story")
        logger.info(f"[StorySerializer] Validated data: {validated_data}")
        
        # Get raw request data to ensure all fields are included
        request = self.context.get('request')
        if request:
            raw_data = dict(request.data)
            logger.info(f"[StorySerializer] Raw request data: {raw_data}")
            
            # Ensure nullable fields are included even if they're null
            nullable_fields = ['story_points', 'epic', 'sprint', 'assigned_to']
            for field in nullable_fields:
                if field in raw_data and field not in validated_data:
                    # Field was in request but not validated - add it
                    validated_data[field] = raw_data[field] if raw_data[field] not in [None, '', 'null'] else None
                    logger.info(f"[StorySerializer] Added {field} = {validated_data[field]} to validated_data")
        
        # Validate using project validation rules
        project = validated_data.get('project')
        if project:
            from apps.projects.services.validation import get_validation_service
            validation_service = get_validation_service(project)
            is_valid, error, warnings = validation_service.validate_story_creation(validated_data)
            
            if not is_valid:
                from rest_framework.exceptions import ValidationError
                raise ValidationError(error)
            
            # Log warnings
            if warnings:
                logger.warning(f"[StorySerializer] Validation warnings: {', '.join(warnings)}")
        
        instance = super().create(validated_data)
        logger.info(f"[StorySerializer] Story created. Story points: {instance.story_points}, Assigned to: {instance.assigned_to}, Epic: {instance.epic}, Sprint: {instance.sprint}")
        return instance


class SprintPlanningRequestSerializer(serializers.Serializer):
    """Request serializer for sprint planning."""
    
    team_velocity = serializers.IntegerField(
        min_value=1,
        help_text="Team's average velocity in story points"
    )
    backlog_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="Specific backlog story IDs to consider (optional)"
    )
    constraints = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Optional planning constraints"
    )


class EstimationRequestSerializer(serializers.Serializer):
    """Request serializer for story estimation."""
    
    use_historical = serializers.BooleanField(
        default=True,
        help_text="Whether to use historical data for estimation"
    )


class EstimationResponseSerializer(serializers.Serializer):
    """Response serializer for estimation."""
    
    estimated_points = serializers.IntegerField()
    confidence = serializers.FloatField()
    rationale = serializers.CharField()
    complexity_factors = serializers.ListField(child=serializers.CharField())
    risks = serializers.ListField(child=serializers.CharField(), required=False)


class EpicSerializer(serializers.ModelSerializer):
    """Epic serializer."""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Epic
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate epic dates against project dates."""
        start_date = data.get('start_date')
        target_date = data.get('target_date')
        
        # Get project from instance (update) or validated_data (create)
        project = None
        if self.instance:
            project = self.instance.project
        elif 'project' in data:
            project = data['project']
        elif 'project' in self.initial_data:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=self.initial_data['project'])
            except (Project.DoesNotExist, ValueError):
                pass
        
        if not project:
            # If we can't get the project, let the model validation handle it
            return data
        
        # Validate epic dates are within project dates (if project has dates)
        if project.start_date and start_date:
            if start_date < project.start_date:
                raise serializers.ValidationError({
                    'start_date': f'Epic start date must be on or after project start date ({project.start_date}).'
                })
        
        if project.end_date and target_date:
            if target_date > project.end_date:
                raise serializers.ValidationError({
                    'target_date': f'Epic target date must be on or before project end date ({project.end_date}).'
                })
        
        # Validate start_date < target_date (if both are provided)
        if start_date and target_date:
            if start_date > target_date:
                raise serializers.ValidationError({
                    'target_date': 'Epic target date must be on or after start date.'
                })
        
        return data


class TaskSerializer(serializers.ModelSerializer):
    """Task serializer."""
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'story': {'required': False, 'allow_null': True},
            'component': {'required': False, 'allow_blank': True},
        }
    
    def validate_status(self, value):
        """Validate status against project configuration."""
        if not value:
            return value
        
        # Get project from task's story or from validated_data
        project = None
        if self.instance:
            # For updates, get project from story
            if self.instance.story:
                project = self.instance.story.project
        elif 'story' in self.initial_data:
            # For creates, get project from story
            from apps.projects.models import UserStory
            try:
                story = UserStory.objects.get(id=self.initial_data['story'])
                project = story.project
            except (UserStory.DoesNotExist, ValueError):
                pass
        
        if project:
            try:
                config = project.configuration
                if config and config.custom_states:
                    valid_statuses = [state.get('id') for state in config.custom_states if state.get('id')]
                    if value not in valid_statuses:
                        raise serializers.ValidationError(
                            f"Invalid status '{value}'. Valid statuses for this project are: {', '.join(valid_statuses)}"
                        )
            except ProjectConfiguration.DoesNotExist:
                pass  # No configuration yet, allow default status
        
        return value


class BugSerializer(serializers.ModelSerializer):
    """Bug serializer."""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    reporter_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    linked_stories_count = serializers.SerializerMethodField()
    duplicates_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Bug
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at', 'closed_at']
        extra_kwargs = {
            'component': {'required': False, 'allow_null': True, 'allow_blank': True},
        }
    
    def validate_status(self, value):
        """Validate status against project configuration."""
        if not value:
            return value
        
        # Get project from instance (update) or validated_data (create)
        project = None
        if self.instance:
            project = self.instance.project
        elif 'project' in self.initial_data:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=self.initial_data['project'])
            except (Project.DoesNotExist, ValueError):
                pass
        
        if project:
            try:
                config = project.configuration
                if config and config.custom_states:
                    valid_statuses = [state.get('id') for state in config.custom_states if state.get('id')]
                    if value not in valid_statuses:
                        raise serializers.ValidationError(
                            f"Invalid status '{value}'. Valid statuses for this project are: {', '.join(valid_statuses)}"
                        )
            except ProjectConfiguration.DoesNotExist:
                pass  # No configuration yet, allow default status
        
        return value
    
    def create(self, validated_data):
        """Convert null values to empty strings for CharFields."""
        if 'component' in validated_data and validated_data['component'] is None:
            validated_data['component'] = ''
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Convert null values to empty strings for CharFields."""
        if 'component' in validated_data and validated_data['component'] is None:
            validated_data['component'] = ''
        return super().update(instance, validated_data)
    
    def get_reporter_name(self, obj):
        """Get reporter's full name or email."""
        if obj.reporter:
            if obj.reporter.first_name and obj.reporter.last_name:
                return f"{obj.reporter.first_name} {obj.reporter.last_name}"
            return obj.reporter.email
        return None
    
    def get_assigned_to_name(self, obj):
        """Get assignee's full name or email."""
        if obj.assigned_to:
            if obj.assigned_to.first_name and obj.assigned_to.last_name:
                return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
            return obj.assigned_to.email
        return None
    
    def get_linked_stories_count(self, obj):
        """Get count of linked stories."""
        return obj.linked_stories.count()
    
    def get_duplicates_count(self, obj):
        """Get count of duplicate bugs."""
        return obj.duplicates.count()


class IssueSerializer(serializers.ModelSerializer):
    """Issue serializer."""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    reporter_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    linked_stories_count = serializers.SerializerMethodField()
    linked_tasks_count = serializers.SerializerMethodField()
    linked_bugs_count = serializers.SerializerMethodField()
    watchers_count = serializers.SerializerMethodField()
    duplicates_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Issue
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at', 'closed_at']
        extra_kwargs = {
            'environment': {'required': False, 'allow_null': True, 'allow_blank': True},
            'component': {'required': False, 'allow_null': True, 'allow_blank': True},
        }
    
    def validate_status(self, value):
        """Validate status against project configuration."""
        if not value:
            return value
        
        # Get project from instance (update) or validated_data (create)
        project = None
        if self.instance:
            project = self.instance.project
        elif 'project' in self.initial_data:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=self.initial_data['project'])
            except (Project.DoesNotExist, ValueError):
                pass
        
        if project:
            try:
                config = project.configuration
                if config and config.custom_states:
                    valid_statuses = [state.get('id') for state in config.custom_states if state.get('id')]
                    if value not in valid_statuses:
                        raise serializers.ValidationError(
                            f"Invalid status '{value}'. Valid statuses for this project are: {', '.join(valid_statuses)}"
                        )
            except ProjectConfiguration.DoesNotExist:
                pass  # No configuration yet, allow default status
        
        return value
    
    def create(self, validated_data):
        """Convert null values to empty strings for CharFields."""
        if 'environment' in validated_data and validated_data['environment'] is None:
            validated_data['environment'] = ''
        if 'component' in validated_data and validated_data['component'] is None:
            validated_data['component'] = ''
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Convert null values to empty strings for CharFields."""
        if 'environment' in validated_data and validated_data['environment'] is None:
            validated_data['environment'] = ''
        if 'component' in validated_data and validated_data['component'] is None:
            validated_data['component'] = ''
        return super().update(instance, validated_data)
    
    def get_reporter_name(self, obj):
        """Get reporter's full name or email."""
        if obj.reporter:
            if obj.reporter.first_name and obj.reporter.last_name:
                return f"{obj.reporter.first_name} {obj.reporter.last_name}"
            return obj.reporter.email
        return None
    
    def get_assigned_to_name(self, obj):
        """Get assignee's full name or email."""
        if obj.assigned_to:
            if obj.assigned_to.first_name and obj.assigned_to.last_name:
                return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
            return obj.assigned_to.email
        return None
    
    def get_linked_stories_count(self, obj):
        """Get count of linked stories."""
        return obj.linked_stories.count() if hasattr(obj, 'linked_stories') else 0
    
    def get_linked_tasks_count(self, obj):
        """Get count of linked tasks."""
        return obj.linked_tasks.count() if hasattr(obj, 'linked_tasks') else 0
    
    def get_linked_bugs_count(self, obj):
        """Get count of linked bugs."""
        return obj.linked_bugs.count() if hasattr(obj, 'linked_bugs') else 0
    
    def get_watchers_count(self, obj):
        """Get count of watchers."""
        return obj.watchers.count() if hasattr(obj, 'watchers') else 0
    
    def get_duplicates_count(self, obj):
        """Get count of duplicate issues."""
        return obj.duplicates.count() if hasattr(obj, 'duplicates') else 0


class TimeLogSerializer(serializers.ModelSerializer):
    """TimeLog serializer."""
    
    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)
    project_name = serializers.SerializerMethodField()
    story_title = serializers.CharField(source='story.title', read_only=True, allow_null=True)
    task_title = serializers.CharField(source='task.title', read_only=True, allow_null=True)
    bug_title = serializers.CharField(source='bug.title', read_only=True, allow_null=True)
    issue_title = serializers.CharField(source='issue.title', read_only=True, allow_null=True)
    work_item_type = serializers.SerializerMethodField()
    work_item_id = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'duration_minutes', 'created_by', 'updated_by']
        extra_kwargs = {
            'user': {'required': False, 'allow_null': True, 'read_only': True},
        }
    
    def get_user_name(self, obj):
        """Get user's full name or email."""
        if obj.user:
            if obj.user.first_name and obj.user.last_name:
                return f"{obj.user.first_name} {obj.user.last_name}"
            return obj.user.email
        return None
    
    def get_project_name(self, obj):
        """Get project name from the work item."""
        if obj.story:
            return obj.story.project.name if obj.story.project else None
        elif obj.task and obj.task.story:
            return obj.task.story.project.name if obj.task.story.project else None
        elif obj.bug:
            return obj.bug.project.name if obj.bug.project else None
        elif obj.issue:
            return obj.issue.project.name if obj.issue.project else None
        return None
    
    def get_work_item_type(self, obj):
        """Get the type of work item (story, task, bug, issue)."""
        if obj.story:
            return 'story'
        elif obj.task:
            return 'task'
        elif obj.bug:
            return 'bug'
        elif obj.issue:
            return 'issue'
        return None
    
    def get_work_item_id(self, obj):
        """Get the ID of the work item."""
        if obj.story:
            return str(obj.story.id)
        elif obj.task:
            return str(obj.task.id)
        elif obj.bug:
            return str(obj.bug.id)
        elif obj.issue:
            return str(obj.issue.id)
        return None
    
    def get_duration_hours(self, obj):
        """Get duration in hours."""
        return obj.duration_hours if hasattr(obj, 'duration_hours') else None
    
    def get_is_active(self, obj):
        """Check if timer is active."""
        return obj.is_active if hasattr(obj, 'is_active') else False
    
    def validate(self, data):
        """Validate that at least one work item is provided."""
        # Ensure at least one work item is provided
        if not any([data.get('story'), data.get('task'), data.get('bug'), data.get('issue')]):
            raise serializers.ValidationError(
                "At least one work item (story, task, bug, or issue) must be provided."
            )
        
        return data


class ProjectConfigurationSerializer(serializers.ModelSerializer):
    """Project configuration serializer."""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_id = serializers.UUIDField(source='project.id', read_only=True)
    
    class Meta:
        model = ProjectConfiguration
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'project']
    
    def validate_custom_states(self, value):
        """Validate custom states structure."""
        if not isinstance(value, list):
            raise serializers.ValidationError("custom_states must be a list")
        
        state_ids = []
        for state in value:
            if not isinstance(state, dict):
                raise serializers.ValidationError("Each state must be a dictionary")
            
            required_fields = ['id', 'name', 'order']
            for field in required_fields:
                if field not in state:
                    raise serializers.ValidationError(f"State missing required field: {field}")
            
            if state['id'] in state_ids:
                raise serializers.ValidationError(f"Duplicate state id: {state['id']}")
            state_ids.append(state['id'])
        
        return value
    
    def validate_story_point_scale(self, value):
        """Validate story point scale."""
        if not isinstance(value, list):
            raise serializers.ValidationError("story_point_scale must be a list")
        
        if not all(isinstance(x, int) and x > 0 for x in value):
            raise serializers.ValidationError("All story point values must be positive integers")
        
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Story point scale must have unique values")
        
        return sorted(value)
    
    def validate_max_story_points_per_story(self, value):
        """Validate max story points per story."""
        if value < self.initial_data.get('min_story_points_per_story', 1):
            raise serializers.ValidationError(
                "max_story_points_per_story must be >= min_story_points_per_story"
            )
        return value
    
    def update(self, instance, validated_data):
        """Update configuration and initialize defaults if needed."""
        # Initialize defaults for JSON fields if they're empty
        if 'custom_states' in validated_data and not validated_data['custom_states']:
            validated_data['custom_states'] = instance.get_default_custom_states()
        if 'story_point_scale' in validated_data and not validated_data['story_point_scale']:
            validated_data['story_point_scale'] = instance.get_default_story_point_scale()
        if 'state_transitions' in validated_data and not validated_data['state_transitions']:
            validated_data['state_transitions'] = instance.get_default_state_transitions()
        
        return super().update(instance, validated_data)


class StoryCommentSerializer(serializers.ModelSerializer):
    """Serializer for StoryComment."""
    author_email = serializers.CharField(source='author.email', read_only=True)
    author_name = serializers.SerializerMethodField()
    replies_count = serializers.IntegerField(source='replies.count', read_only=True)
    
    class Meta:
        model = StoryComment
        fields = '__all__'
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'created_by', 'updated_by']
    
    def get_author_name(self, obj):
        """Get author's full name or email."""
        if obj.author:
            return obj.author.get_full_name() or obj.author.email
        return None


class MentionSerializer(serializers.ModelSerializer):
    """Serializer for Mention."""
    mentioned_user_email = serializers.CharField(source='mentioned_user.email', read_only=True)
    mentioned_user_name = serializers.SerializerMethodField()
    story_title = serializers.CharField(source='story.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Mention
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'read_at', 'created_by']
    
    def get_mentioned_user_name(self, obj):
        """Get mentioned user's full name or email."""
        if obj.mentioned_user:
            return obj.mentioned_user.get_full_name() or obj.mentioned_user.email
        return None


class StoryDependencySerializer(serializers.ModelSerializer):
    """Serializer for StoryDependency."""
    source_story_title = serializers.CharField(source='source_story.title', read_only=True)
    target_story_title = serializers.CharField(source='target_story.title', read_only=True)
    resolved_by_email = serializers.CharField(source='resolved_by.email', read_only=True, allow_null=True)
    
    class Meta:
        model = StoryDependency
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'resolved_at', 'resolved_by']


class StoryAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for StoryAttachment."""
    story_title = serializers.CharField(source='story.title', read_only=True)
    uploaded_by_email = serializers.CharField(source='uploaded_by.email', read_only=True, allow_null=True)
    file_size_display = serializers.CharField(source='get_file_size_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = StoryAttachment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'uploaded_by']
    
    def get_file_url(self, obj):
        """Get file URL."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification."""
    recipient_email = serializers.CharField(source='recipient.email', read_only=True)
    recipient_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    story_title = serializers.CharField(source='story.title', read_only=True, allow_null=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True, allow_null=True)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'read_at', 'email_sent_at', 'created_by']
    
    def get_recipient_name(self, obj):
        """Get recipient's full name or email."""
        if obj.recipient:
            return obj.recipient.get_full_name() or obj.recipient.email
        return None
    
    def get_created_by_name(self, obj):
        """Get creator's full name or email."""
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activity."""
    
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)
    user_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    content_type_name = serializers.SerializerMethodField()
    content_object_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
    
    def get_user_name(self, obj):
        """Get user's full name or email."""
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return None
    
    def get_content_type_name(self, obj):
        """Get the model name of the content object."""
        if obj.content_type:
            return obj.content_type.model
        return None
    
    def get_content_object_title(self, obj):
        """Get the title/name of the content object."""
        return obj.content_object_title


class WatcherSerializer(serializers.ModelSerializer):
    """Watcher serializer."""

    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    content_type_name = serializers.SerializerMethodField()
    content_object_title = serializers.SerializerMethodField()

    class Meta:
        model = Watcher
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        """Get user's full name or email."""
        if obj.user:
            if obj.user.first_name and obj.user.last_name:
                return f"{obj.user.first_name} {obj.user.last_name}"
            return obj.user.email
        return None

    def get_user_email(self, obj):
        """Get user's email."""
        return obj.user.email if obj.user else None

    def get_content_type_name(self, obj):
        """Get the model name of the content object."""
        return obj.content_type.model if obj.content_type else None

    def get_content_object_title(self, obj):
        """Get the title/name of the content object."""
        if obj.content_object:
            # Try common title/name fields
            if hasattr(obj.content_object, 'title'):
                return obj.content_object.title
            elif hasattr(obj.content_object, 'name'):
                return obj.content_object.name
            return str(obj.content_object)
        return None


class EditHistorySerializer(serializers.ModelSerializer):
    """Serializer for EditHistory."""
    
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)
    user_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    content_type_name = serializers.SerializerMethodField()
    content_object_title = serializers.SerializerMethodField()
    all_diffs = serializers.SerializerMethodField()
    
    class Meta:
        model = EditHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
    
    def get_user_name(self, obj):
        """Get user's full name or email."""
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return None
    
    def get_content_type_name(self, obj):
        """Get the model name of the content object."""
        if obj.content_type:
            return obj.content_type.model
        return None
    
    def get_content_object_title(self, obj):
        """Get the title/name of the content object."""
        return obj.content_object_title
    
    def get_all_diffs(self, obj):
        """Get all diffs for changed fields."""
        return obj.get_all_diffs()


class SavedSearchSerializer(serializers.ModelSerializer):
    """Serializer for SavedSearch."""
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)
    user_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    
    class Meta:
        model = SavedSearch
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_used_at', 'usage_count']
    
    def get_user_name(self, obj):
        """Get user's full name or email."""
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return None