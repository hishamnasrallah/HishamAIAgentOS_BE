"""
Project Management API Serializers

Serializers for AI Project Management endpoints.
"""

from rest_framework import serializers
import re
from apps.projects.models import (
    Project, Sprint, UserStory, Epic, Task, Bug, Issue, TimeLog, ProjectConfiguration, 
    Mention, StoryComment, StoryDependency, StoryAttachment, Notification, Watcher, Activity, EditHistory, SavedSearch,
    StatusChangeApproval, ProjectLabelPreset, Milestone, TicketReference, StoryLink, CardTemplate, BoardTemplate,
    SearchHistory, FilterPreset, TimeBudget, OvertimeRecord, CardCoverImage, CardChecklist, CardVote,
    StoryArchive, StoryVersion, Webhook, StoryClone, GitHubIntegration, JiraIntegration, SlackIntegration,
    ProjectMember, GeneratedProject, ProjectFile, RepositoryExport
)
from apps.core.services.roles import RoleService
# Alias for backward compatibility
Story = UserStory


# Validation helper functions
def validate_label_structure(value):
    """Validate labels structure and content. Returns validated labels list."""
    if value is None:
        return []
    
    if not isinstance(value, list):
        raise serializers.ValidationError("Labels must be a list")
    
    MAX_LABEL_NAME_LENGTH = 100
    LABEL_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_]+$')
    HEX_COLOR_PATTERN = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    
    label_names = []
    validated_labels = []
    
    for label in value:
        if not isinstance(label, dict):
            raise serializers.ValidationError("Each label must be a dictionary")
        
        name = label.get('name')
        if not name or not isinstance(name, str):
            raise serializers.ValidationError("Label name is required and must be a string")
        
        name = name.strip()
        if len(name) == 0:
            raise serializers.ValidationError("Label name cannot be empty")
        
        if len(name) > MAX_LABEL_NAME_LENGTH:
            raise serializers.ValidationError(f"Label name cannot exceed {MAX_LABEL_NAME_LENGTH} characters")
        
        # Validate format (alphanumeric, spaces, hyphens, underscores)
        if not LABEL_NAME_PATTERN.match(name):
            raise serializers.ValidationError(
                "Label name can only contain letters, numbers, spaces, hyphens, and underscores"
            )
        
        # Validate color if provided
        color = label.get('color')
        if color:
            if not isinstance(color, str):
                raise serializers.ValidationError("Label color must be a string")
            if not HEX_COLOR_PATTERN.match(color):
                raise serializers.ValidationError("Label color must be a valid hex color (#RRGGBB or #RGB)")
            # Normalize to uppercase
            color = color.upper()
        
        # Check for duplicates (case-insensitive)
        if name.lower() in [n.lower() for n in label_names]:
            raise serializers.ValidationError(f"Duplicate label name: {name}")
        
        label_names.append(name.lower())
        validated_labels.append({
            'name': name,
            'color': color or '#808080'  # Default color if not provided
        })
    
    return validated_labels


def validate_component_name(value):
    """Validate component name. Returns validated component name."""
    if not value:
        return ''  # Empty string for null/empty values
    
    if not isinstance(value, str):
        raise serializers.ValidationError("Component must be a string")
    
    value = value.strip()
    
    if len(value) == 0:
        return ''  # Empty string
    
    MAX_COMPONENT_LENGTH = 100
    if len(value) > MAX_COMPONENT_LENGTH:
        raise serializers.ValidationError(f"Component name cannot exceed {MAX_COMPONENT_LENGTH} characters")
    
    # Validate format (alphanumeric, spaces, hyphens, underscores)
    COMPONENT_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_]+$')
    if not COMPONENT_NAME_PATTERN.match(value):
        raise serializers.ValidationError(
            "Component name can only contain letters, numbers, spaces, hyphens, and underscores"
        )
    
    return value


def validate_state_transition(project, old_status: str, new_status: str, user=None) -> None:
    """
    Validate that a state transition is allowed according to project configuration.
    Super admins can bypass all state transition validations.
    
    Args:
        project: Project instance
        old_status: Current status
        new_status: Desired new status
        user: Optional user instance to check for super admin status
        
    Raises:
        serializers.ValidationError: If transition is not allowed
    """
    # Super admins can bypass all state transition validations
    if user and RoleService.is_super_admin(user):
        return
    
    if not project or not old_status or not new_status or old_status == new_status:
        return  # No transition or no project
    
    try:
        config = project.configuration
        if not config or not config.state_transitions:
            return  # No configuration or no transitions defined, allow all
        
        transitions = config.state_transitions
        allowed_transitions = transitions.get(old_status, [])
        
        # If transitions are defined for the old status, new status must be in the list
        if allowed_transitions and new_status not in allowed_transitions:
            # Check if new_status is a final state (always allowed)
            if config.custom_states:
                new_state_config = next(
                    (s for s in config.custom_states if s.get('id') == new_status),
                    None
                )
                if new_state_config and new_state_config.get('is_final'):
                    return  # Final states are always allowed
            
            # Check if old_status allows all transitions (empty list means all allowed)
            if allowed_transitions == []:
                return  # Empty list means all transitions allowed
            
            raise serializers.ValidationError(
                f"Cannot transition from '{old_status}' to '{new_status}'. "
                f"Allowed transitions from '{old_status}': {', '.join(allowed_transitions) if allowed_transitions else 'none'}"
            )
    except ProjectConfiguration.DoesNotExist:
        pass  # No configuration, allow transition


class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer."""
    
    # Make slug optional - will auto-generate from name
    # Explicitly define as optional to override model field requirements
    slug = serializers.SlugField(required=False, allow_blank=True, allow_null=True, default='')
    # Make description optional
    description = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'description': {'required': False, 'allow_blank': True},
            'slug': {'required': False, 'allow_blank': True, 'allow_null': True},
        }
    
    def __init__(self, *args, **kwargs):
        """Override __init__ to ensure slug field is not required."""
        super().__init__(*args, **kwargs)
        # Force slug to be optional
        if 'slug' in self.fields:
            self.fields['slug'].required = False
            self.fields['slug'].allow_blank = True
            self.fields['slug'].allow_null = True
    
    def validate_name(self, value):
        """Validate project name: uniqueness per organization, minimum length, and format."""
        if not value or not value.strip():
            raise serializers.ValidationError('Project name is required.')
        
        trimmed = value.strip()
        
        # Minimum length validation (at least 3 characters)
        if len(trimmed) < 3:
            raise serializers.ValidationError('Project name must be at least 3 characters long.')
        
        # Maximum length validation
        if len(trimmed) > 200:
            raise serializers.ValidationError('Project name must be less than 200 characters.')
        
        # Check if name contains at least one alphanumeric character
        import re
        if not re.search(r'[a-zA-Z0-9]', trimmed):
            raise serializers.ValidationError('Project name must contain at least one letter or number.')
        
        # Check if name is only quotes with spaces
        quotes_only = trimmed.replace('"', '').replace("'", '').replace(' ', '')
        if not quotes_only:
            raise serializers.ValidationError('Project name cannot consist only of quotes and spaces.')
        
        # Check for uniqueness within organization
        organization = None
        if self.instance:
            # When updating, get organization from instance
            organization = getattr(self.instance, 'organization', None)
            # If organization is not loaded, try to get it from the project
            if not organization and hasattr(self.instance, 'pk'):
                try:
                    from apps.projects.models import Project
                    project = Project.objects.select_related('organization').get(pk=self.instance.pk)
                    organization = project.organization
                except Project.DoesNotExist:
                    pass
        elif 'organization' in self.initial_data:
            from apps.organizations.models import Organization
            try:
                organization = Organization.objects.get(id=self.initial_data['organization'])
            except (Organization.DoesNotExist, ValueError):
                pass
        
        if organization:
            # Check for duplicate names (case-insensitive) within the same organization
            existing_projects = Project.objects.filter(organization=organization, name__iexact=trimmed)
            # Exclude current project if updating
            if self.instance:
                existing_projects = existing_projects.exclude(id=self.instance.id)
            
            if existing_projects.exists():
                raise serializers.ValidationError(
                    f'A project with the name "{trimmed}" already exists in this organization. Please choose a different name.'
                )
        # If organization is None, skip uniqueness check (might be a data inconsistency issue)
        
        return trimmed
    
    def validate_description(self, value):
        """Validate description: max length 5000, not JSON format."""
        if not value:
            return value
        
        # Check maximum length
        if len(value) > 5000:
            raise serializers.ValidationError('Description must be less than 5000 characters.')
        
        # Check if description is JSON format (starts with { or [ and looks like JSON)
        stripped = value.strip()
        if stripped:
            # Check if it starts with JSON-like characters
            if (stripped.startswith('{') and stripped.endswith('}')) or (stripped.startswith('[') and stripped.endswith(']')):
                # Try to parse as JSON to confirm
                import json
                try:
                    json.loads(stripped)
                    raise serializers.ValidationError('Description cannot be in JSON format. Please provide a plain text description.')
                except (json.JSONDecodeError, ValueError):
                    # Not valid JSON, allow it
                    pass
        
        return value
    
    def validate(self, attrs):
        """Override validate to ensure slug is not required during validation and validate dates."""
        # Remove slug from validation if it's empty/None - will be generated in create()
        if 'slug' in attrs and (not attrs.get('slug') or attrs.get('slug') == ''):
            attrs.pop('slug', None)
        
        # Validate start_date and end_date are required on create
        if not self.instance:  # Creating new project
            start_date = attrs.get('start_date')
            end_date = attrs.get('end_date')
            
            # Check if start_date is missing or empty
            if not start_date or (isinstance(start_date, str) and start_date.strip() == ''):
                raise serializers.ValidationError({
                    'start_date': 'Start date is required when creating a new project.'
                })
            
            # Check if end_date is missing or empty
            if not end_date or (isinstance(end_date, str) and end_date.strip() == ''):
                raise serializers.ValidationError({
                    'end_date': 'End date is required when creating a new project.'
                })
            
            # Update attrs with cleaned values
            attrs['start_date'] = start_date
            attrs['end_date'] = end_date
            
            # Validate end_date is after start_date
            start_date = attrs.get('start_date')
            end_date = attrs.get('end_date')
            if start_date and end_date and end_date < start_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        else:  # Updating existing project
            # If dates are being updated, validate end_date is after start_date
            start_date = attrs.get('start_date', self.instance.start_date)
            end_date = attrs.get('end_date', self.instance.end_date)
            if start_date and end_date and end_date < start_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        
        return attrs
    
    def create(self, validated_data):
        # Get organization from validated_data (set by perform_create in viewset)
        organization = validated_data.get('organization')
        
        # Note: Organization validation (status, subscription, limits) is done in perform_create
        # This is a backup check in case organization is set directly
        # Super admins can bypass these checks (checked in perform_create, but also here for safety)
        if organization:
            # Get user from context (if available) to check super admin status
            user = self.context.get('request').user if self.context.get('request') else None
            is_super_admin = RoleService.is_super_admin(user) if user else False
            
            if not is_super_admin:
                # Check if organization is active
                if not organization.is_active():
                    raise serializers.ValidationError({
                        'organization': f'Cannot create project. Organization "{organization.name}" is {organization.get_status_display()}.'
                    })
                
                # Check if organization subscription is active
                if not organization.is_subscription_active():
                    raise serializers.ValidationError({
                        'organization': f'Cannot create project. Organization subscription has expired.'
                    })
                
                # Check project limit using FeatureService
                if not organization.can_add_project():
                    from apps.organizations.services import FeatureService
                    current_count = organization.get_project_count()
                    max_projects = FeatureService.get_feature_value(organization, 'projects.max_count', default=0)
                    raise serializers.ValidationError({
                        'organization': f'Cannot create project. Organization has reached the maximum number of projects ({max_projects}). Current: {current_count}'
                    })
        
        # Auto-generate slug from name if not provided
        if 'slug' not in validated_data or not validated_data.get('slug'):
            from django.utils.text import slugify
            base_slug = slugify(validated_data['name'])
            slug = base_slug
            # Handle slug uniqueness per organization
            counter = 1
            while Project.objects.filter(slug=slug, organization=organization).exists():
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
        """Validate sprint dates against project dates, check for overlaps, and validate capacity."""
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
        
        # Validate sprint capacity if stories are being added
        if self.instance and 'total_story_points' in data:
            try:
                config = project.configuration
                if config:
                    max_points = config.max_story_points_per_sprint
                    allow_overcommitment = config.allow_overcommitment
                    new_total = data['total_story_points']
                    
                    if new_total > max_points and not allow_overcommitment:
                        raise serializers.ValidationError({
                            'total_story_points': f'Sprint capacity exceeded: {new_total} story points (max: {max_points}). Enable overcommitment in project settings to allow this.'
                        })
            except ProjectConfiguration.DoesNotExist:
                pass  # No configuration, skip validation
        
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
    
    class Meta:
        model = Story
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'generated_by_ai', 'generation_workflow', 'created_by']
        extra_kwargs = {
            'number': {'required': False, 'allow_blank': True},
            'title': {'required': False},
            'description': {'required': False, 'allow_blank': True},
            'acceptance_criteria': {'required': False, 'allow_blank': True},
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
            'custom_fields': {'required': False, 'allow_null': True},
        }
    
    def validate_custom_fields(self, value):
        """Validate custom fields against project configuration schema."""
        if not value or not isinstance(value, dict):
            return value or {}
        
        # Get project from instance or validated_data
        project = None
        if self.instance:
            project = self.instance.project
        elif 'project' in self.initial_data:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=self.initial_data['project'])
            except (Project.DoesNotExist, ValueError):
                pass
        
        if not project:
            return value  # Can't validate without project
        
        try:
            config = project.configuration
            if not config or not config.custom_fields_schema:
                return value  # No schema defined, allow any values
            
            schema = config.custom_fields_schema
            schema_dict = {field.get('id'): field for field in schema if field.get('id')}
            
            # Validate each custom field value
            validated = {}
            for field_id, field_value in value.items():
                if field_id not in schema_dict:
                    continue  # Skip unknown fields
                
                field_schema = schema_dict[field_id]
                field_type = field_schema.get('type')
                
                # Type validation and conversion
                if field_type == 'number':
                    if field_value is not None and field_value != '':
                        try:
                            validated[field_id] = float(field_value)
                        except (ValueError, TypeError):
                            raise serializers.ValidationError({
                                'custom_fields': f"Field '{field_schema.get('name', field_id)}' must be a number"
                            })
                    else:
                        validated[field_id] = None
                elif field_type == 'date':
                    validated[field_id] = field_value  # Date validation handled by frontend
                elif field_type == 'select':
                    options = field_schema.get('options', [])
                    if field_value and field_value not in options:
                        raise serializers.ValidationError({
                            'custom_fields': f"Field '{field_schema.get('name', field_id)}' must be one of: {', '.join(options)}"
                        })
                    validated[field_id] = field_value
                elif field_type == 'multi_select':
                    options = field_schema.get('options', [])
                    if field_value:
                        if not isinstance(field_value, list):
                            field_value = [field_value]
                        invalid = [v for v in field_value if v not in options]
                        if invalid:
                            raise serializers.ValidationError({
                                'custom_fields': f"Field '{field_schema.get('name', field_id)}' contains invalid values: {', '.join(invalid)}"
                            })
                        validated[field_id] = field_value
                    else:
                        validated[field_id] = []
                else:  # text or other
                    validated[field_id] = field_value
                
                # Required field validation
                if field_schema.get('required', False) and (validated[field_id] is None or validated[field_id] == '' or (isinstance(validated[field_id], list) and len(validated[field_id]) == 0)):
                    raise serializers.ValidationError({
                        'custom_fields': f"Field '{field_schema.get('name', field_id)}' is required"
                    })
            
            return validated
        except ProjectConfiguration.DoesNotExist:
            return value  # No configuration, allow any values
    
    def to_representation(self, instance):
        """Override to include nested user data for assigned_to and epic data."""
        representation = super().to_representation(instance)
        
        # Replace assigned_to ID with full user object
        if instance.assigned_to:
            from apps.authentication.serializers import UserSerializer
            representation['assigned_to'] = UserSerializer(instance.assigned_to).data
        else:
            representation['assigned_to'] = None
        
        # Replace epic ID with full epic object (title, id, etc.)
        if instance.epic:
            representation['epic'] = {
                'id': str(instance.epic.id),
                'title': instance.epic.title,
                'status': instance.epic.status,
            }
        else:
            representation['epic'] = None
        
        return representation
    
    def validate_acceptance_criteria(self, value):
        """Convert empty strings to None for acceptance_criteria."""
        if value == '' or (isinstance(value, str) and value.strip() == ''):
            return None
        return value
    
    def validate_description(self, value):
        """Convert empty strings to None for description."""
        if value == '' or (isinstance(value, str) and value.strip() == ''):
            return None
        return value
    
    def validate_status(self, value):
        """Validate status against project configuration and state transitions."""
        if not value:
            return value
        
        # Get user from context to check super admin status
        user = self.context.get('request').user if self.context.get('request') else None
        
        # Super admins can bypass all status validations
        if user and RoleService.is_super_admin(user):
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
                
                # Validate state transition if updating
                if self.instance and self.instance.status:
                    validate_state_transition(project, self.instance.status, value, user=user)
            except ProjectConfiguration.DoesNotExist:
                pass  # No configuration yet, allow default status
        
        return value
    
    def validate_labels(self, value):
        """Validate labels structure and content."""
        return validate_label_structure(value)
    
    def validate_component(self, value):
        """Validate component name."""
        return validate_component_name(value)
    
    def validate_number(self, value):
        """Validate story number uniqueness within project."""
        if not value or value.strip() == '':
            return value  # Empty is OK, will be auto-generated
        
        # Get project from instance (update) or initial_data (create)
        project = None
        if self.instance:
            project = self.instance.project
        elif 'project' in self.initial_data:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=self.initial_data['project'])
            except (Project.DoesNotExist, ValueError):
                pass
        
        if not project:
            return value  # Can't validate without project
        
        # Check for duplicates within the same project
        existing_stories = Story.objects.filter(project=project, number=value.strip())
        
        # Exclude current story if updating
        if self.instance:
            existing_stories = existing_stories.exclude(id=self.instance.id)
        
        if existing_stories.exists():
            raise serializers.ValidationError(
                f"Story number '{value.strip()}' already exists in this project. Please use a different number or leave it empty for auto-generation."
            )
        
        return value.strip()
    
    def validate(self, data):
        """Validate story data including required fields and sprint status."""
        # Validate description and acceptance_criteria are required for new stories
        description = data.get('description')
        acceptance_criteria = data.get('acceptance_criteria')
        
        # Get project to check if this is create or update
        project = None
        if self.instance:
            project = self.instance.project
        elif 'project' in self.initial_data:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=self.initial_data['project'])
            except (Project.DoesNotExist, ValueError):
                pass
        
        # For new stories, description and acceptance_criteria are required
        if not self.instance:
            # Check description
            desc_value = description if description is not None else (self.initial_data.get('description') if hasattr(self, 'initial_data') else None)
            if not desc_value or (isinstance(desc_value, str) and desc_value.strip() in ['', '<p></p>', '<p><br></p>']):
                raise serializers.ValidationError({
                    'description': 'Description is required.'
                })
            
            # Check acceptance_criteria
            ac_value = acceptance_criteria if acceptance_criteria is not None else (self.initial_data.get('acceptance_criteria') if hasattr(self, 'initial_data') else None)
            if not ac_value or (isinstance(ac_value, str) and ac_value.strip() in ['', '<p></p>', '<p><br></p>']):
                raise serializers.ValidationError({
                    'acceptance_criteria': 'Acceptance criteria is required.'
                })
        
        # Validate sprint is not completed
        sprint = data.get('sprint')
        if sprint:
            if hasattr(sprint, 'status') and sprint.status == 'completed':
                raise serializers.ValidationError({
                    'sprint': 'Cannot add story to a completed sprint. Please select an active or planned sprint.'
                })
            elif isinstance(sprint, str):
                # Sprint ID provided, need to fetch sprint
                from apps.projects.models import Sprint
                try:
                    sprint_obj = Sprint.objects.get(id=sprint)
                    if sprint_obj.status == 'completed':
                        raise serializers.ValidationError({
                            'sprint': 'Cannot add story to a completed sprint. Please select an active or planned sprint.'
                        })
                except Sprint.DoesNotExist:
                    pass  # Will be caught by foreign key validation
        
        return data
    
    def update(self, instance, validated_data):
        """Override update to ensure all fields are saved, including null values, and validate."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Track old status for automation
        old_status = instance.status
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
        
        # Check if approval is required for status change
        new_status = validated_data.get('status', instance.status)
        if old_status != new_status and instance.project:
            try:
                config = instance.project.configuration
                if config and config.permission_settings.get('require_approval_for_status_change', False):
                    # Approval required - create approval request instead of changing status
                    from apps.projects.models import StatusChangeApproval
                    from django.contrib.contenttypes.models import ContentType
                    from rest_framework.exceptions import ValidationError
                    
                    # Check if there's already a pending approval for this status change
                    content_type = ContentType.objects.get_for_model(instance)
                    existing_approval = StatusChangeApproval.objects.filter(
                        content_type=content_type,
                        object_id=instance.id,
                        old_status=old_status,
                        new_status=new_status,
                        status='pending'
                    ).first()
                    
                    if existing_approval:
                        raise ValidationError({
                            'status': [f'An approval request for this status change is already pending (ID: {existing_approval.id})']
                        })
                    
                    # Create approval request
                    approver = instance.project.owner
                    approval = StatusChangeApproval.objects.create(
                        content_type=content_type,
                        object_id=instance.id,
                        old_status=old_status,
                        new_status=new_status,
                        reason=validated_data.get('approval_reason', ''),
                        requested_by=request.user if request else None,
                        approver=approver,
                        project=instance.project
                    )
                    
                    # Don't change the status - return the instance with original status
                    # Remove status from validated_data so it doesn't get updated
                    validated_data.pop('status', None)
                    
                    # Return a response indicating approval is required
                    raise ValidationError({
                        'status': [f'Status change requires approval. Approval request created (ID: {approval.id})'],
                        'approval_id': [str(approval.id)]
                    })
            except ProjectConfiguration.DoesNotExist:
                pass  # No configuration, proceed with normal update
        
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
                elif field in array_fields and value is None:
                    # Ensure array fields default to empty list, not None
                    value = []
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
                    elif field in ['tags', 'labels']:
                        # Array fields (JSONField) - ensure it's a list
                        if isinstance(raw_value, list):
                            setattr(instance, field, raw_value)
                        else:
                            setattr(instance, field, [])
                        logger.info(f"[StorySerializer] Set {field} = {getattr(instance, field)} (from raw_data, not in validated_data)")
        
        instance.save()
        logger.info(f"[StorySerializer] Story saved. Story points: {instance.story_points}, Assigned to: {instance.assigned_to}, Epic: {instance.epic}, Sprint: {instance.sprint}")
        
        # Execute automation rules if status changed
        if old_status != instance.status and instance.project:
            from apps.projects.services.automation import AutomationService
            automation_service = AutomationService(instance.project)
            user = self.context.get('request').user if self.context.get('request') else None
            automation_service.execute_rules_for_status_change(
                instance,
                old_status,
                instance.status,
                user
            )
        
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
            
            # Ensure tags and labels are included (JSONField arrays) - default to empty list if not provided
            if 'tags' in raw_data and 'tags' not in validated_data:
                validated_data['tags'] = raw_data['tags'] if isinstance(raw_data['tags'], list) else []
                logger.info(f"[StorySerializer] Added tags = {validated_data['tags']} to validated_data")
            elif 'tags' not in validated_data:
                validated_data['tags'] = []
                
            if 'labels' in raw_data and 'labels' not in validated_data:
                validated_data['labels'] = raw_data['labels'] if isinstance(raw_data['labels'], list) else []
                logger.info(f"[StorySerializer] Added labels = {validated_data['labels']} to validated_data")
            elif 'labels' not in validated_data:
                validated_data['labels'] = []
        
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
            
            # Validate sprint capacity if sprint is provided
            sprint = validated_data.get('sprint')
            story_points = validated_data.get('story_points')
            if sprint and story_points:
                is_valid, error = validation_service.validate_sprint_capacity(
                    sprint,
                    story_points
                )
                if not is_valid:
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError({'sprint': error})
            
            # Set default status from configuration if not provided
            if 'status' not in validated_data or not validated_data.get('status'):
                from apps.projects.models import UserStory
                # Create temporary instance to use get_default_status method
                temp_story = UserStory(project=project)
                default_status = temp_story.get_default_status()
                validated_data['status'] = default_status
                logger.info(f"[StorySerializer] Set default status from configuration: {default_status}")
        
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
            'custom_fields': {'required': False, 'allow_null': True},
        }
    
    def validate_custom_fields(self, value):
        """Validate custom fields against project configuration schema."""
        if not value or not isinstance(value, dict):
            return value or {}
        
        # Get project from instance or validated_data
        project = None
        if self.instance:
            project = self.instance.story.project if self.instance.story else None
        elif 'story' in self.initial_data:
            from apps.projects.models import UserStory
            try:
                story = UserStory.objects.get(id=self.initial_data['story'])
                project = story.project
            except (UserStory.DoesNotExist, ValueError):
                pass
        
        if not project:
            return value  # Can't validate without project
        
        try:
            config = project.configuration
            if not config or not config.custom_fields_schema:
                return value  # No schema defined, allow any values
            
            schema = config.custom_fields_schema
            schema_dict = {field.get('id'): field for field in schema if field.get('id')}
            
            # Validate each custom field value
            validated = {}
            for field_id, field_value in value.items():
                if field_id not in schema_dict:
                    continue  # Skip unknown fields
                
                field_schema = schema_dict[field_id]
                field_type = field_schema.get('type')
                
                # Type validation and conversion
                if field_type == 'number':
                    if field_value is not None and field_value != '':
                        try:
                            validated[field_id] = float(field_value)
                        except (ValueError, TypeError):
                            raise serializers.ValidationError({
                                'custom_fields': f"Field '{field_schema.get('name', field_id)}' must be a number"
                            })
                    else:
                        validated[field_id] = None
                elif field_type == 'date':
                    validated[field_id] = field_value  # Date validation handled by frontend
                elif field_type == 'select':
                    options = field_schema.get('options', [])
                    if field_value and field_value not in options:
                        raise serializers.ValidationError({
                            'custom_fields': f"Field '{field_schema.get('name', field_id)}' must be one of: {', '.join(options)}"
                        })
                    validated[field_id] = field_value
                elif field_type == 'multi_select':
                    options = field_schema.get('options', [])
                    if field_value:
                        if not isinstance(field_value, list):
                            field_value = [field_value]
                        invalid = [v for v in field_value if v not in options]
                        if invalid:
                            raise serializers.ValidationError({
                                'custom_fields': f"Field '{field_schema.get('name', field_id)}' contains invalid values: {', '.join(invalid)}"
                            })
                        validated[field_id] = field_value
                    else:
                        validated[field_id] = []
                else:  # text or other
                    validated[field_id] = field_value
                
                # Required field validation
                if field_schema.get('required', False) and (validated[field_id] is None or validated[field_id] == '' or (isinstance(validated[field_id], list) and len(validated[field_id]) == 0)):
                    raise serializers.ValidationError({
                        'custom_fields': f"Field '{field_schema.get('name', field_id)}' is required"
                    })
            
            return validated
        except ProjectConfiguration.DoesNotExist:
            return value  # No configuration, allow any values
    
    def validate_status(self, value):
        """Validate status against project configuration and state transitions."""
        if not value:
            return value
        
        # Get user from context to check super admin status
        user = self.context.get('request').user if self.context.get('request') else None
        
        # Super admins can bypass all status validations
        if user and RoleService.is_super_admin(user):
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
                
                # Validate state transition if updating
                if self.instance and self.instance.status:
                    validate_state_transition(project, self.instance.status, value, user=user)
            except ProjectConfiguration.DoesNotExist:
                pass  # No configuration yet, allow default status
        
        return value
    
    def validate_labels(self, value):
        """Validate labels structure and content."""
        return validate_label_structure(value)
    
    def validate_component(self, value):
        """Validate component name."""
        return validate_component_name(value)
    
    def update(self, instance, validated_data):
        """Override update to execute automation rules on status changes."""
        # Track old status for automation
        old_status = instance.status
        
        # Get project from task's story
        project = None
        if instance.story:
            project = instance.story.project
        
        # Get request object for approval checks
        request = self.context.get('request')
        
        # Check if approval is required for status change
        new_status = validated_data.get('status', instance.status)
        if old_status != new_status and project and request:
            try:
                config = project.configuration
                if config and config.permission_settings.get('require_approval_for_status_change', False):
                    # Approval required - create approval request
                    from apps.projects.models import StatusChangeApproval
                    from django.contrib.contenttypes.models import ContentType
                    from rest_framework.exceptions import ValidationError
                    
                    content_type = ContentType.objects.get_for_model(instance)
                    existing_approval = StatusChangeApproval.objects.filter(
                        content_type=content_type,
                        object_id=instance.id,
                        old_status=old_status,
                        new_status=new_status,
                        status='pending'
                    ).first()
                    
                    if existing_approval:
                        raise ValidationError({
                            'status': [f'An approval request for this status change is already pending (ID: {existing_approval.id})']
                        })
                    
                    approver = project.owner
                    approval_reason = request.data.get('approval_reason', '')
                    approval = StatusChangeApproval.objects.create(
                        content_type=content_type,
                        object_id=instance.id,
                        old_status=old_status,
                        new_status=new_status,
                        reason=approval_reason,
                        requested_by=request.user,
                        approver=approver,
                        project=project
                    )
                    
                    validated_data.pop('status', None)
                    raise ValidationError({
                        'status': [f'Status change requires approval. Approval request created (ID: {approval.id})'],
                        'approval_id': [str(approval.id)],
                        'approval_required': [True]
                    })
            except ProjectConfiguration.DoesNotExist:
                pass
        
        # Call parent update
        instance = super().update(instance, validated_data)
        
        # Execute automation rules if status changed
        if old_status != instance.status and project:
            from apps.projects.services.automation import AutomationService
            automation_service = AutomationService(project)
            user = self.context.get('request').user if self.context.get('request') else None
            automation_service.execute_rules_for_status_change(
                instance,
                old_status,
                instance.status,
                user
            )
        
        return instance


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
            'custom_fields': {'required': False, 'allow_null': True},
        }
    
    def validate_status(self, value):
        """Validate status against Bug model's STATUS_CHOICES and state transitions."""
        if not value:
            return value
        
        # Get user from context to check super admin status
        user = self.context.get('request').user if self.context.get('request') else None
        
        # Super admins can bypass all status validations
        if user and RoleService.is_super_admin(user):
            return value
        
        # Bug model has fixed STATUS_CHOICES, not custom states
        from apps.projects.models import Bug
        valid_statuses = [choice[0] for choice in Bug.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status '{value}'. Valid statuses are: {', '.join(valid_statuses)}"
            )
        
        # Validate state transition if updating (even with fixed statuses, projects may have transition rules)
        if self.instance and self.instance.status:
            project = self.instance.project
            if project:
                try:
                    validate_state_transition(project, self.instance.status, value, user=user)
                except (ProjectConfiguration.DoesNotExist, AttributeError):
                    pass  # No configuration or no transitions defined, allow all
        
        return value
    
    def validate_labels(self, value):
        """Validate labels structure and content."""
        return validate_label_structure(value)
    
    def validate_component(self, value):
        """Validate component name."""
        return validate_component_name(value)
    
    def create(self, validated_data):
        """Convert null values to empty strings for CharFields and validate."""
        if 'component' in validated_data and validated_data['component'] is None:
            validated_data['component'] = ''
        
        # Validate using project validation rules
        project = validated_data.get('project')
        if project:
            from apps.projects.services.validation import get_validation_service
            validation_service = get_validation_service(project)
            
            # Create instance temporarily for validation
            bug = Bug(**validated_data)
            is_valid, error, warnings = validation_service.validate_bug_before_status_change(
                bug,
                validated_data.get('status', 'new'),
                None
            )
            if not is_valid:
                raise serializers.ValidationError({'status': error})
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Convert null values to empty strings for CharFields and validate."""
        if 'component' in validated_data and validated_data['component'] is None:
            validated_data['component'] = ''
        
        # Track old status for automation
        old_status = instance.status
        
        # Get request object for approval checks
        request = self.context.get('request')
        
        # Validate using project validation rules
        project = instance.project
        new_status = validated_data.get('status', instance.status)
        
        # Check if approval is required for status change
        if old_status != new_status and project and request:
            try:
                config = project.configuration
                if config and config.permission_settings.get('require_approval_for_status_change', False):
                    # Approval required - create approval request
                    from apps.projects.models import StatusChangeApproval
                    from django.contrib.contenttypes.models import ContentType
                    from rest_framework.exceptions import ValidationError
                    
                    content_type = ContentType.objects.get_for_model(instance)
                    existing_approval = StatusChangeApproval.objects.filter(
                        content_type=content_type,
                        object_id=instance.id,
                        old_status=old_status,
                        new_status=new_status,
                        status='pending'
                    ).first()
                    
                    if existing_approval:
                        raise ValidationError({
                            'status': [f'An approval request for this status change is already pending (ID: {existing_approval.id})']
                        })
                    
                    approver = project.owner
                    approval_reason = request.data.get('approval_reason', '')
                    approval = StatusChangeApproval.objects.create(
                        content_type=content_type,
                        object_id=instance.id,
                        old_status=old_status,
                        new_status=new_status,
                        reason=approval_reason,
                        requested_by=request.user,
                        approver=approver,
                        project=project
                    )
                    
                    validated_data.pop('status', None)
                    raise ValidationError({
                        'status': [f'Status change requires approval. Approval request created (ID: {approval.id})'],
                        'approval_id': [str(approval.id)],
                        'approval_required': [True]
                    })
            except ProjectConfiguration.DoesNotExist:
                pass
        
        if project and 'status' in validated_data:
            from apps.projects.services.validation import get_validation_service
            validation_service = get_validation_service(project)
            
            new_status = validated_data.get('status', instance.status)
            
            if new_status != old_status:
                is_valid, error, warnings = validation_service.validate_bug_before_status_change(
                    instance,
                    new_status,
                    old_status
                )
                if not is_valid:
                    raise serializers.ValidationError({'status': error})
        
        # Call parent update
        instance = super().update(instance, validated_data)
        
        # Execute automation rules if status changed
        if old_status != instance.status and project:
            from apps.projects.services.automation import AutomationService
            automation_service = AutomationService(project)
            user = self.context.get('request').user if self.context.get('request') else None
            automation_service.execute_rules_for_status_change(
                instance,
                old_status,
                instance.status,
                user
            )
        
        return instance
    
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
        """Validate status against Issue model's STATUS_CHOICES."""
        if not value:
            return value
        
        # Get user from context to check super admin status
        user = self.context.get('request').user if self.context.get('request') else None
        
        # Super admins can bypass all status validations
        if user and RoleService.is_super_admin(user):
            return value
        
        # Issue model has fixed STATUS_CHOICES, not custom states
        valid_statuses = [choice[0] for choice in Issue.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status '{value}'. Valid statuses are: {', '.join(valid_statuses)}"
            )
        
        return value
    
    def validate_labels(self, value):
        """Validate labels structure and content."""
        return validate_label_structure(value)
    
    def validate_component(self, value):
        """Validate component name."""
        return validate_component_name(value)
    
    def create(self, validated_data):
        """Convert null values to empty strings for CharFields and validate."""
        if 'environment' in validated_data and validated_data['environment'] is None:
            validated_data['environment'] = ''
        if 'component' in validated_data and validated_data['component'] is None:
            validated_data['component'] = ''
        
        # Extract ManyToMany fields that can't be set directly during creation
        watchers = validated_data.pop('watchers', [])
        
        # Validate using project validation rules
        project = validated_data.get('project')
        if project:
            from apps.projects.services.validation import get_validation_service
            validation_service = get_validation_service(project)
            
            # Create instance temporarily for validation (without watchers)
            issue = Issue(**validated_data)
            is_valid, error, warnings = validation_service.validate_issue_before_status_change(
                issue,
                validated_data.get('status', 'open'),
                None
            )
            if not is_valid:
                raise serializers.ValidationError({'status': error})
        
        # Create the issue instance (without watchers)
        issue = super().create(validated_data)
        
        # Set ManyToMany fields after creation
        if watchers:
            issue.watchers.set(watchers)
        
        return issue
    
    def update(self, instance, validated_data):
        """Convert null values to empty strings for CharFields and validate."""
        if 'environment' in validated_data and validated_data['environment'] is None:
            validated_data['environment'] = ''
        if 'component' in validated_data and validated_data['component'] is None:
            validated_data['component'] = ''
        
        # Track old status for automation
        old_status = instance.status
        
        # Get request object for approval checks
        request = self.context.get('request')
        
        # Validate using project validation rules
        project = instance.project
        new_status = validated_data.get('status', instance.status)
        
        # Check if approval is required for status change
        if old_status != new_status and project and request:
            try:
                config = project.configuration
                if config and config.permission_settings.get('require_approval_for_status_change', False):
                    # Approval required - create approval request
                    from apps.projects.models import StatusChangeApproval
                    from django.contrib.contenttypes.models import ContentType
                    from rest_framework.exceptions import ValidationError
                    
                    content_type = ContentType.objects.get_for_model(instance)
                    existing_approval = StatusChangeApproval.objects.filter(
                        content_type=content_type,
                        object_id=instance.id,
                        old_status=old_status,
                        new_status=new_status,
                        status='pending'
                    ).first()
                    
                    if existing_approval:
                        raise ValidationError({
                            'status': [f'An approval request for this status change is already pending (ID: {existing_approval.id})']
                        })
                    
                    approver = project.owner
                    approval_reason = request.data.get('approval_reason', '')
                    approval = StatusChangeApproval.objects.create(
                        content_type=content_type,
                        object_id=instance.id,
                        old_status=old_status,
                        new_status=new_status,
                        reason=approval_reason,
                        requested_by=request.user,
                        approver=approver,
                        project=project
                    )
                    
                    validated_data.pop('status', None)
                    raise ValidationError({
                        'status': [f'Status change requires approval. Approval request created (ID: {approval.id})'],
                        'approval_id': [str(approval.id)],
                        'approval_required': [True]
                    })
            except ProjectConfiguration.DoesNotExist:
                pass
        
        if project and 'status' in validated_data:
            from apps.projects.services.validation import get_validation_service
            validation_service = get_validation_service(project)
            
            if new_status != old_status:
                is_valid, error, warnings = validation_service.validate_issue_before_status_change(
                    instance,
                    new_status,
                    old_status
                )
                if not is_valid:
                    raise serializers.ValidationError({'status': error})
        
        # Extract ManyToMany fields that can't be set directly during update
        watchers = validated_data.pop('watchers', None)
        
        # Call parent update
        instance = super().update(instance, validated_data)
        
        # Set ManyToMany fields after update if provided
        if watchers is not None:
            instance.watchers.set(watchers)
        
        # Execute automation rules if status changed
        if old_status != instance.status and project:
            from apps.projects.services.automation import AutomationService
            automation_service = AutomationService(project)
            user = self.context.get('request').user if self.context.get('request') else None
            automation_service.execute_rules_for_status_change(
                instance,
                old_status,
                instance.status,
                user
            )
        
        return instance
    
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
        
        if len(value) == 0:
            raise serializers.ValidationError("At least one state is required")
        
        state_ids = []
        has_default = False
        
        for state in value:
            if not isinstance(state, dict):
                raise serializers.ValidationError("Each state must be a dictionary")
            
            required_fields = ['id', 'name', 'order']
            for field in required_fields:
                if field not in state:
                    raise serializers.ValidationError(f"State missing required field: {field}")
            
            # Validate id format
            state_id = state['id']
            if not isinstance(state_id, str) or len(state_id.strip()) == 0:
                raise serializers.ValidationError("State id must be a non-empty string")
            
            # Check for duplicates
            if state_id in state_ids:
                raise serializers.ValidationError(f"Duplicate state id: {state_id}")
            state_ids.append(state_id)
            
            # Validate order is integer
            if not isinstance(state.get('order'), int):
                raise serializers.ValidationError(f"State order must be an integer for state: {state_id}")
            
            # Check for is_default flag
            if state.get('is_default', False):
                if has_default:
                    raise serializers.ValidationError("Only one state can have is_default=True")
                has_default = True
        
        # Ensure at least one default state
        if not has_default and len(value) > 0:
            # Auto-set first state as default
            value[0]['is_default'] = True
        
        return value
    
    def validate_story_point_scale(self, value):
        """Validate story point scale."""
        if not isinstance(value, list):
            raise serializers.ValidationError("story_point_scale must be a list")
        
        if len(value) == 0:
            raise serializers.ValidationError("Story point scale must have at least one value")
        
        if not all(isinstance(x, int) and x > 0 for x in value):
            raise serializers.ValidationError("All story point values must be positive integers")
        
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Story point scale must have unique values")
        
        # Don't validate against min/max here - do it in validate() method after all fields are set
        return sorted(value)
    
    def validate_max_story_points_per_story(self, value):
        """Validate max story points per story."""
        if value < 1:
            raise serializers.ValidationError("max_story_points_per_story must be at least 1")
        
        # Don't validate against min_points or scale here - do it in validate() method
        return value
    
    def validate_min_story_points_per_story(self, value):
        """Validate min story points per story."""
        if value < 1:
            raise serializers.ValidationError("min_story_points_per_story must be at least 1")
        
        # Don't validate against max_points or scale here - do it in validate() method
        return value
    
    def validate_state_transitions(self, value):
        """Validate state transitions structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("state_transitions must be a dictionary")
        
        # Validate structure only - state ID validation happens in validate() method
        for from_state, to_states in value.items():
            if not isinstance(to_states, list):
                raise serializers.ValidationError(
                    f"Transition values for '{from_state}' must be a list"
                )
        
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        # Get all relevant data (from data dict or instance)
        custom_states = data.get('custom_states')
        if custom_states is None and self.instance:
            custom_states = self.instance.custom_states
        
        state_transitions = data.get('state_transitions')
        if state_transitions is None and self.instance:
            state_transitions = self.instance.state_transitions
        
        min_points = data.get('min_story_points_per_story')
        if min_points is None and self.instance:
            min_points = self.instance.min_story_points_per_story
        
        max_points = data.get('max_story_points_per_story')
        if max_points is None and self.instance:
            max_points = self.instance.max_story_points_per_story
        
        story_point_scale = data.get('story_point_scale')
        if story_point_scale is None and self.instance:
            story_point_scale = self.instance.story_point_scale
        
        # 1. Ensure at least one state has is_default=True
        if custom_states:
            has_default = any(state.get('is_default', False) for state in custom_states)
            if not has_default and len(custom_states) > 0:
                # Auto-set first state as default
                if isinstance(custom_states, list) and len(custom_states) > 0:
                    custom_states = list(custom_states)  # Make a copy
                    custom_states[0] = {**custom_states[0], 'is_default': True}
                    data['custom_states'] = custom_states
        
        # 2. Validate state_transitions against custom_states
        if state_transitions and custom_states and isinstance(custom_states, list):
            state_ids = [state.get('id') for state in custom_states if state.get('id')]
            
            # Clean up invalid transitions (remove references to non-existent states)
            cleaned_transitions = {}
            for from_state, to_states in state_transitions.items():
                if from_state in state_ids:
                    # Only include valid target states
                    valid_to_states = [s for s in to_states if s in state_ids]
                    cleaned_transitions[from_state] = valid_to_states
                # If from_state doesn't exist, skip it (don't raise error - just clean it up)
            
            # Update data with cleaned transitions
            data['state_transitions'] = cleaned_transitions
        
        # 3. Validate min/max story points relationship
        if min_points is not None and max_points is not None:
            if min_points > max_points:
                raise serializers.ValidationError({
                    'min_story_points_per_story': f"min_story_points_per_story ({min_points}) must be <= max_story_points_per_story ({max_points})",
                    'max_story_points_per_story': f"max_story_points_per_story ({max_points}) must be >= min_story_points_per_story ({min_points})"
                })
        
        # 4. Validate and auto-adjust story_point_scale against min/max
        if story_point_scale and isinstance(story_point_scale, list) and len(story_point_scale) > 0:
            original_scale = list(story_point_scale)  # Make a copy
            adjusted_scale = list(story_point_scale)  # Make a copy
            
            # Filter out values outside min/max range
            if min_points is not None:
                adjusted_scale = [v for v in adjusted_scale if v >= min_points]
            
            if max_points is not None:
                adjusted_scale = [v for v in adjusted_scale if v <= max_points]
            
            # If scale was adjusted, update it
            if len(adjusted_scale) != len(original_scale) or set(adjusted_scale) != set(original_scale):
                if len(adjusted_scale) == 0:
                    # If all values were removed, raise error
                    raise serializers.ValidationError({
                        'story_point_scale': f"Story point scale must have at least one value within the range [{min_points or 1}, {max_points or 21}]. Current scale: {original_scale}"
                    })
                # Auto-adjust the scale - remove invalid values
                data['story_point_scale'] = sorted(adjusted_scale)
                # Update the variable for final validation
                story_point_scale = adjusted_scale
            
            # Final validation - ensure scale is within bounds (should always pass after adjustment)
            final_scale = data.get('story_point_scale', story_point_scale)
            if final_scale and isinstance(final_scale, list) and len(final_scale) > 0:
                if min_points is not None:
                    if min(final_scale) < min_points:
                        raise serializers.ValidationError({
                            'story_point_scale': f"Story point scale minimum ({min(final_scale)}) must be >= min_story_points_per_story ({min_points})"
                        })
                
                if max_points is not None:
                    if max(final_scale) > max_points:
                        raise serializers.ValidationError({
                            'story_point_scale': f"Story point scale maximum ({max(final_scale)}) must be <= max_story_points_per_story ({max_points})"
                        })
        
        return data
    
    def update(self, instance, validated_data):
        """Update configuration and initialize defaults if needed."""
        # Initialize defaults for JSON fields if they're empty
        if 'custom_states' in validated_data and not validated_data['custom_states']:
            validated_data['custom_states'] = instance.get_default_custom_states()
        if 'story_point_scale' in validated_data and not validated_data['story_point_scale']:
            validated_data['story_point_scale'] = instance.get_default_story_point_scale()
        if 'state_transitions' in validated_data and not validated_data['state_transitions']:
            validated_data['state_transitions'] = instance.get_default_state_transitions()
        
        # Ensure at least one state has is_default=True after update
        if 'custom_states' in validated_data and validated_data['custom_states']:
            has_default = any(state.get('is_default', False) for state in validated_data['custom_states'])
            if not has_default:
                validated_data['custom_states'][0]['is_default'] = True
        
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
        extra_kwargs = {
            'file_name': {'required': False},
            'file_size': {'required': False},
            'file_type': {'required': False},
        }
    
    def create(self, validated_data):
        """Extract file metadata from uploaded file."""
        file = validated_data.get('file')
        if file:
            # Extract metadata from file
            validated_data['file_name'] = file.name
            validated_data['file_size'] = file.size
            validated_data['file_type'] = file.content_type or 'application/octet-stream'
        
        # Set uploaded_by to current user
        request = self.context.get('request')
        if request and request.user:
            validated_data['uploaded_by'] = request.user
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        return super().create(validated_data)
    
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


class ProjectLabelPresetSerializer(serializers.ModelSerializer):
    """Serializer for ProjectLabelPreset."""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = ProjectLabelPreset
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_color(self, value):
        """Validate hex color format."""
        HEX_COLOR_PATTERN = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
        if value and not HEX_COLOR_PATTERN.match(value):
            raise serializers.ValidationError("Color must be a valid hex color code (e.g., #3b82f6 or #3bf)")
        return value.upper() if value else value
    
    def validate_name(self, value):
        """Validate label name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Label name cannot be empty")
        MAX_LABEL_NAME_LENGTH = 100
        if len(value.strip()) > MAX_LABEL_NAME_LENGTH:
            raise serializers.ValidationError(f"Label name cannot exceed {MAX_LABEL_NAME_LENGTH} characters")
        LABEL_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_]+$')
        if not LABEL_NAME_PATTERN.match(value.strip()):
            raise serializers.ValidationError(
                "Label name can only contain letters, numbers, spaces, hyphens, and underscores"
            )
        return value.strip()


class MilestoneSerializer(serializers.ModelSerializer):
    """Serializer for Milestone."""
    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'project': {'required': True},
            'name': {'required': True},
        }
    
    def validate_progress_percentage(self, value):
        """Validate progress percentage is between 0 and 100."""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Progress percentage must be between 0 and 100.")
        return value


class TicketReferenceSerializer(serializers.ModelSerializer):
    """Serializer for TicketReference."""
    work_item_type = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = TicketReference
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_synced_at']
        extra_kwargs = {
            'project': {'required': True},
            'system': {'required': True},
            'ticket_id': {'required': True},
        }
    
    def validate_ticket_url(self, value):
        """Validate ticket URL format."""
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Ticket URL must be a valid HTTP/HTTPS URL.")
        return value


class StoryLinkSerializer(serializers.ModelSerializer):
    """Serializer for StoryLink."""
    source_story_title = serializers.CharField(source='source_story.title', read_only=True)
    target_story_title = serializers.CharField(source='target_story.title', read_only=True)
    
    class Meta:
        model = StoryLink
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'project': {'required': True},
            'source_story': {'required': True},
            'target_story': {'required': True},
            'link_type': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate that source and target stories are different."""
        source_story = attrs.get('source_story')
        target_story = attrs.get('target_story')
        
        if source_story and target_story:
            if source_story.id == target_story.id:
                raise serializers.ValidationError({
                    'target_story': "Source and target stories cannot be the same."
                })
            
            # Ensure both stories belong to the same project
            if source_story.project_id != target_story.project_id:
                raise serializers.ValidationError({
                    'target_story': "Source and target stories must belong to the same project."
                })
        
        return attrs


class CardTemplateSerializer(serializers.ModelSerializer):
    """Serializer for CardTemplate."""
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = CardTemplate
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'usage_count']
        extra_kwargs = {
            'name': {'required': True},
        }
    
    def validate_scope(self, value):
        """Validate scope based on project."""
        if value == 'global' and self.initial_data.get('project'):
            raise serializers.ValidationError("Global templates cannot be associated with a project.")
        if value == 'project' and not self.initial_data.get('project'):
            raise serializers.ValidationError("Project templates must be associated with a project.")
        return value
    
    def validate_color(self, value):
        """Validate color is a valid hex code."""
        if value and not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
            raise serializers.ValidationError("Color must be a valid hex color (#RRGGBB or #RGB).")
        return value.upper() if value else value


class TimeBudgetSerializer(serializers.ModelSerializer):
    """Serializer for TimeBudget."""
    spent_hours = serializers.ReadOnlyField()
    remaining_hours = serializers.ReadOnlyField()
    utilization_percentage = serializers.ReadOnlyField()
    is_over_budget = serializers.ReadOnlyField()
    is_warning_threshold_reached = serializers.ReadOnlyField()
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    sprint_name = serializers.CharField(source='sprint.name', read_only=True, allow_null=True)
    story_title = serializers.CharField(source='story.title', read_only=True, allow_null=True)
    task_title = serializers.CharField(source='task.title', read_only=True, allow_null=True)
    epic_title = serializers.CharField(source='epic.title', read_only=True, allow_null=True)
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)
    
    class Meta:
        model = TimeBudget
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'spent_hours', 'remaining_hours', 
                           'utilization_percentage', 'is_over_budget', 'is_warning_threshold_reached']
    
    def validate_budget_hours(self, value):
        """Validate budget hours is positive."""
        if value <= 0:
            raise serializers.ValidationError("Budget hours must be greater than 0.")
        return value
    
    def validate_warning_threshold(self, value):
        """Validate warning threshold is between 0 and 100."""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Warning threshold must be between 0 and 100.")
        return value


class OvertimeRecordSerializer(serializers.ModelSerializer):
    """Serializer for OvertimeRecord."""
    budget_scope = serializers.CharField(source='time_budget.get_scope_display', read_only=True)
    budget_hours = serializers.DecimalField(source='time_budget.budget_hours', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = OvertimeRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'alert_sent', 'alert_sent_at']


class CardCoverImageSerializer(serializers.ModelSerializer):
    """Serializer for CardCoverImage."""
    
    class Meta:
        model = CardCoverImage
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class CardChecklistSerializer(serializers.ModelSerializer):
    """Serializer for CardChecklist."""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = CardChecklist
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_items(self, value):
        """Validate checklist items structure."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Items must be a list.")
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each item must be a dictionary.")
            if 'text' not in item:
                raise serializers.ValidationError("Each item must have a 'text' field.")
        return value


class CardVoteSerializer(serializers.ModelSerializer):
    """Serializer for CardVote."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = CardVote
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class StoryArchiveSerializer(serializers.ModelSerializer):
    """Serializer for StoryArchive."""
    story_title = serializers.CharField(source='story.title', read_only=True)
    archived_by_name = serializers.CharField(source='archived_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = StoryArchive
        fields = '__all__'
        read_only_fields = ['id', 'archived_at']


class StoryVersionSerializer(serializers.ModelSerializer):
    """Serializer for StoryVersion."""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    story_title = serializers.CharField(source='story.title', read_only=True)
    
    class Meta:
        model = StoryVersion
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer for Webhook."""
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Webhook
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_events(self, value):
        """Validate events list."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Events must be a list.")
        valid_events = [choice[0] for choice in Webhook.EVENT_CHOICES]
        for event in value:
            if event not in valid_events:
                raise serializers.ValidationError(f"Invalid event: {event}. Valid events: {', '.join(valid_events)}")
        return value


class StoryCloneSerializer(serializers.ModelSerializer):
    """Serializer for StoryClone."""
    original_story_title = serializers.CharField(source='original_story.title', read_only=True)
    cloned_story_title = serializers.CharField(source='cloned_story.title', read_only=True)
    cloned_by_name = serializers.CharField(source='cloned_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = StoryClone
        fields = '__all__'
        read_only_fields = ['id', 'cloned_at']


class GitHubIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for GitHubIntegration."""
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = GitHubIntegration
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'access_token': {'write_only': True},  # Don't expose token in responses
        }


class JiraIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for JiraIntegration."""
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = JiraIntegration
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_token': {'write_only': True},  # Don't expose token in responses
        }


class SlackIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for SlackIntegration."""
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = SlackIntegration
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'webhook_url': {'write_only': False},  # Webhook URL can be visible
            'bot_token': {'write_only': True},  # Don't expose token in responses
        }


class BoardTemplateSerializer(serializers.ModelSerializer):
    """Serializer for BoardTemplate."""
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = BoardTemplate
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'usage_count']
        extra_kwargs = {
            'name': {'required': True},
        }
    
    def validate_scope(self, value):
        """Validate scope based on project."""
        if value == 'global' and self.initial_data.get('project'):
            raise serializers.ValidationError("Global templates cannot be associated with a project.")
        if value == 'project' and not self.initial_data.get('project'):
            raise serializers.ValidationError("Project templates must be associated with a project.")
        return value


class SearchHistorySerializer(serializers.ModelSerializer):
    """Serializer for SearchHistory."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    
    class Meta:
        model = SearchHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'user': {'required': True},
            'query': {'required': True},
        }


class FilterPresetSerializer(serializers.ModelSerializer):
    """Serializer for FilterPreset."""
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = FilterPreset
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'usage_count']
        extra_kwargs = {
            'name': {'required': True},
        }
    
    def validate(self, data):
        """Validate that either project or user is set, but not both for shared presets."""
        project = data.get('project')
        user = data.get('user')
        is_shared = data.get('is_shared', False)
        
        if is_shared and user:
            raise serializers.ValidationError("Shared presets cannot be associated with a specific user.")
        if not is_shared and not user:
            raise serializers.ValidationError("User-specific presets must have a user.")
        
        return data


class ProjectMemberSerializer(serializers.ModelSerializer):
    """Serializer for ProjectMember model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    added_by_email = serializers.EmailField(source='added_by.email', read_only=True)
    
    class Meta:
        model = ProjectMember
        fields = [
            'id',
            'project',
            'user',
            'user_email',
            'user_username',
            'user_first_name',
            'user_last_name',
            'project_name',
            'roles',
            'added_by',
            'added_by_email',
            'added_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'added_at', 'updated_at']
    
    def validate_roles(self, value):
        """Validate that roles are valid (system roles or custom roles from project) using RoleService."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Roles must be a list.")
        
        if not value:
            raise serializers.ValidationError("At least one role is required.")
        
        # Get project to check custom roles
        project = None
        if self.instance:
            project = self.instance.project
        elif 'project' in self.initial_data:
            try:
                project = Project.objects.get(pk=self.initial_data['project'])
            except (Project.DoesNotExist, ValueError, TypeError):
                pass
        
        # Validate each role using RoleService
        invalid_roles = []
        for role in value:
            if not RoleService.is_valid_role(role, project):
                invalid_roles.append(role)
        
        if invalid_roles:
            valid_roles = RoleService.get_all_available_roles(project)
            raise serializers.ValidationError(
                f"Invalid roles: {', '.join(invalid_roles)}. "
                f"Valid roles are: {', '.join(valid_roles)}"
            )
        
        return value
    
    def validate(self, data):
        """Validate that user and project combination is unique."""
        project = data.get('project') or (self.instance.project if self.instance else None)
        user = data.get('user') or (self.instance.user if self.instance else None)
        
        if project and user:
            # Check for existing ProjectMember with same project and user
            existing = ProjectMember.objects.filter(project=project, user=user).exclude(
                id=self.instance.id if self.instance else None
            )
            if existing.exists():
                raise serializers.ValidationError(
                    "A ProjectMember with this project and user already exists."
                )
        
        return data


class GeneratedProjectSerializer(serializers.ModelSerializer):
    """Serializer for GeneratedProject model."""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    files_count = serializers.SerializerMethodField()
    exports_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneratedProject
        fields = [
            'id',
            'project',
            'project_name',
            'workflow_execution',
            'output_directory',
            'status',
            'error_message',
            'total_files',
            'total_size',
            'files_count',
            'exports_count',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_at',
            'updated_at',
            'completed_at',
            'total_files',
            'total_size',
        ]
    
    def get_created_by_name(self, obj):
        """Get created by user's full name."""
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.email
        return None
    
    def get_files_count(self, obj):
        """Get count of files."""
        if hasattr(obj, '_prefetched_objects_cache') and 'files' in obj._prefetched_objects_cache:
            return len(obj._prefetched_objects_cache['files'])
        return obj.files.count() if obj.id else 0
    
    def get_exports_count(self, obj):
        """Get count of exports."""
        if hasattr(obj, '_prefetched_objects_cache') and 'exports' in obj._prefetched_objects_cache:
            return len(obj._prefetched_objects_cache['exports'])
        return obj.exports.count() if obj.id else 0
    
    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance:
            current_status = self.instance.status
            valid_transitions = {
                'pending': ['generating'],
                'generating': ['completed', 'failed'],
                'completed': ['archived'],
                'failed': [],
                'archived': [],
            }
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Invalid transition from {current_status} to {value}"
                )
        return value


class ProjectFileSerializer(serializers.ModelSerializer):
    """Serializer for ProjectFile model."""
    
    file_size_display = serializers.SerializerMethodField()
    file_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectFile
        fields = [
            'id',
            'generated_project',
            'file_path',
            'file_name',
            'file_type',
            'file_type_display',
            'file_size',
            'file_size_display',
            'content_hash',
            'content_preview',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'content_hash',
            'created_at',
            'updated_at',
        ]
    
    def validate_file_path(self, value):
        """Validate file path."""
        # Prevent path traversal
        if '..' in value or value.startswith('/'):
            raise serializers.ValidationError("Invalid file path")
        return value
    
    def get_file_size_display(self, obj):
        """Format file size."""
        return self._format_file_size(obj.file_size)
    
    def get_file_type_display(self, obj):
        """Format file type."""
        return obj.file_type.upper() if obj.file_type else None
    
    @staticmethod
    def _format_file_size(size_bytes):
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


class RepositoryExportSerializer(serializers.ModelSerializer):
    """Serializer for RepositoryExport model."""
    
    export_type_display = serializers.CharField(
        source='get_export_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    archive_size_display = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = RepositoryExport
        fields = [
            'id',
            'generated_project',
            'export_type',
            'export_type_display',
            'repository_name',
            'repository_url',
            'archive_path',
            'archive_size',
            'archive_size_display',
            'status',
            'status_display',
            'error_message',
            'config',
            'download_url',
            'created_by',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_at',
            'updated_at',
            'completed_at',
            'archive_path',
            'archive_size',
            'repository_url',
            'status',
            'error_message',
        ]
    
    def validate_export_type(self, value):
        """Validate export type."""
        valid_types = ['zip', 'tar', 'tar.gz', 'github', 'gitlab']
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid export type: {value}")
        return value
    
    def validate_repository_name(self, value):
        """Validate repository name."""
        if value:
            # GitHub/GitLab naming rules
            pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$'
            if not re.match(pattern, value) or len(value) > 100:
                raise serializers.ValidationError("Invalid repository name")
        return value
    
    def get_archive_size_display(self, obj):
        """Format archive size."""
        if obj.archive_size:
            return ProjectFileSerializer._format_file_size(obj.archive_size)
        return None
    
    def get_download_url(self, obj):
        """Get download URL if available."""
        if obj.status == 'completed' and obj.archive_path:
            from django.urls import reverse
            try:
                return reverse('export-download', kwargs={'export_id': str(obj.id)})
            except:
                return None
        return None


class ProjectGenerationRequestSerializer(serializers.Serializer):
    """Serializer for project generation requests."""
    
    workflow_id = serializers.UUIDField(required=True)
    input_data = serializers.JSONField(required=True)
    
    def validate_workflow_id(self, value):
        """Validate workflow exists."""
        from apps.workflows.models import Workflow
        try:
            workflow = Workflow.objects.get(id=value)
            if workflow.status != 'active':
                raise serializers.ValidationError("Workflow is not active")
        except Workflow.DoesNotExist:
            raise serializers.ValidationError("Workflow not found")
        return value


class GitHubExportRequestSerializer(serializers.Serializer):
    """Serializer for GitHub export requests."""
    
    repository_name = serializers.CharField(required=True, max_length=100)
    organization = serializers.CharField(required=False, allow_blank=True)
    private = serializers.BooleanField(default=False)
    github_token = serializers.CharField(required=False, write_only=True)
    
    def validate_repository_name(self, value):
        """Validate repository name."""
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$'
        if not re.match(pattern, value) or len(value) > 100:
            raise serializers.ValidationError("Invalid repository name")
        return value


class GitLabExportRequestSerializer(serializers.Serializer):
    """Serializer for GitLab export requests."""
    
    project_name = serializers.CharField(required=True, max_length=255)
    namespace = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(
        choices=['private', 'internal', 'public'],
        default='private'
    )
    gitlab_token = serializers.CharField(required=False, write_only=True)