"""
AI Project Management models for HishamOS.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
import re


class Project(models.Model):
    """AI-managed project."""
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, db_index=True, blank=True)  # No longer unique globally, unique per organization. Auto-generated from name if not provided.
    description = models.TextField(blank=True, default='')
    
    # Organization relationship (for SaaS multi-tenancy)
    # Projects belong to an organization
    # Note: nullable=True temporarily - will be made required after data migration
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='projects',
        db_index=True,
        null=True,
        blank=True,
        help_text='Organization this project belongs to'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Team
    owner = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_projects'
    )
    members = models.ManyToManyField(
        'authentication.User',
        related_name='projects',
        blank=True
    )
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_projects',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_projects',
        verbose_name='Updated By'
    )
    
    # Tags
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorizing and filtering projects"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']
        unique_together = [['organization', 'slug']]  # Slug unique per organization
        indexes = [
            models.Index(fields=['organization', 'slug']),
            models.Index(fields=['organization']),
            models.Index(fields=['status']),
            models.Index(fields=['owner']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name


class Sprint(models.Model):
    """Agile sprint."""
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sprints')
    
    name = models.CharField(max_length=200)
    sprint_number = models.IntegerField()
    goal = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Metrics
    total_story_points = models.IntegerField(default=0)
    completed_story_points = models.IntegerField(default=0)
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_sprints',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_sprints',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'sprints'
        verbose_name = 'Sprint'
        verbose_name_plural = 'Sprints'
        unique_together = [['project', 'sprint_number']]
        ordering = ['project', '-sprint_number']
    
    def __str__(self):
        return f'{self.project.name} - Sprint {self.sprint_number}'


class Epic(models.Model):
    """Epic - high-level feature or initiative containing multiple user stories."""
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='epics')
    
    # Work item number (e.g., EPIC-12)
    number = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Unique work item number within project"
    )
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    
    # Tags
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorizing and filtering epics"
    )
    
    # Owner
    owner = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_epics',
        help_text="Epic owner/lead"
    )
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_epics',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_epics',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'epics'
        verbose_name = 'Epic'
        verbose_name_plural = 'Epics'
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['owner']),
            models.Index(fields=['project', 'owner']),
        ]
    
    def __str__(self):
        return self.title


class UserStory(models.Model):
    """User story."""
    
    # Note: STATUS_CHOICES and PRIORITY_CHOICES are now dynamic based on ProjectConfiguration
    # These are kept for backward compatibility and default values only
    DEFAULT_STATUS = 'backlog'
    DEFAULT_PRIORITY = 'medium'
    
    STORY_TYPE_CHOICES = [
        ('feature', 'Feature'),
        ('bug', 'Bug'),
        ('enhancement', 'Enhancement'),
        ('technical_debt', 'Technical Debt'),
        ('documentation', 'Documentation'),
        ('research', 'Research'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stories')
    epic = models.ForeignKey(Epic, on_delete=models.SET_NULL, null=True, blank=True, related_name='stories')
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name='stories')
    
    # Work item number (e.g., STORY-123) - project-specific, auto-incremented
    number = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Unique work item number within project (e.g., STORY-123)"
    )
    
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    acceptance_criteria = models.TextField(blank=True, null=True)
    
    # Status is now dynamic - validated against ProjectConfiguration.custom_states
    status = models.CharField(max_length=50, default=DEFAULT_STATUS, help_text="Workflow state (validated against project configuration)")
    # Priority is now dynamic - can be extended to use ProjectConfiguration if needed
    priority = models.CharField(max_length=20, default=DEFAULT_PRIORITY, help_text="Priority level")
    story_points = models.IntegerField(null=True, blank=True)
    
    story_type = models.CharField(max_length=20, choices=STORY_TYPE_CHOICES, default='feature', help_text="Type of user story")
    component = models.CharField(max_length=100, blank=True, help_text="Component or module this story belongs to")
    due_date = models.DateField(null=True, blank=True, help_text="Due date for this story")
    labels = models.JSONField(default=list, blank=True, help_text="Color-coded labels for visual grouping")
    
    assigned_to = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_stories'
    )
    
    generated_by_ai = models.BooleanField(default=False)
    generation_workflow = models.ForeignKey(
        'workflows.WorkflowExecution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Tags
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorizing and filtering stories"
    )
    
    # Custom fields - values based on project configuration
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom field values based on project configuration"
    )
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_stories',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_stories',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'user_stories'
        verbose_name = 'User Story'
        verbose_name_plural = 'User Stories'
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['sprint', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['project', 'due_date']),
            models.Index(fields=['component']),
            models.Index(fields=['project', 'component']),
            models.Index(fields=['story_type']),
            models.Index(fields=['project', 'story_type']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_valid_statuses(self):
        """Get valid status values from project configuration."""
        try:
            config = self.project.configuration
            if config and config.custom_states:
                return [state.get('id') for state in config.custom_states if state.get('id')]
        except ProjectConfiguration.DoesNotExist:
            pass
        # Fallback to default states if no configuration exists
        return ['backlog', 'todo', 'in_progress', 'review', 'done']
    
    def get_default_status(self):
        """Get default status from project configuration using is_default flag."""
        try:
            config = self.project.configuration
            if config and config.custom_states:
                # Find state with is_default=True
                default_state = next(
                    (state for state in config.custom_states if state.get('is_default', False)),
                    None
                )
                if default_state and default_state.get('id'):
                    return default_state['id']
                # If no default state found, use first state by order
                sorted_states = sorted(
                    [s for s in config.custom_states if s.get('id')],
                    key=lambda x: x.get('order', 999)
                )
                if sorted_states:
                    return sorted_states[0].get('id')
        except ProjectConfiguration.DoesNotExist:
            pass
        
        # Fallback to hardcoded default
        return self.DEFAULT_STATUS
    
    def clean(self):
        """Validate status against project configuration."""
        from django.core.exceptions import ValidationError
        
        if self.status:
            valid_statuses = self.get_valid_statuses()
            if self.status not in valid_statuses:
                raise ValidationError({
                    'status': f"Invalid status '{self.status}'. Valid statuses for this project are: {', '.join(valid_statuses)}"
                })
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)
    
    def extract_mentions(self):
        """Extract @mentions from description and acceptance_criteria.
        
        Handles both HTML format (from rich text editor) and plain text format.
        HTML format: <span class="mention" data-id="email@example.com" data-label="Name">@Name</span>
        Plain text format: @username
        """
        mentions = []
        text = f"{self.description or ''} {self.acceptance_criteria or ''}"
        if not text.strip():
            return mentions
        
        # First, try to extract from HTML mention spans (data-id attribute contains email)
        # Pattern: data-id="email@example.com" or data-id='email@example.com'
        html_pattern = r'data-id=["\']([^"\']+@[^"\']+)["\']'
        html_matches = re.findall(html_pattern, text)
        for match in html_matches:
            # Extract email from data-id
            email = match.strip()
            if '@' in email:
                # It's an email - add it directly (user lookup will handle email matching)
                if email not in mentions:
                    mentions.append(email)
                # Also add username part for fallback matching
                username = email.split('@')[0]
                if username and username not in mentions:
                    mentions.append(username)
        
        # Also extract plain text @mentions (for backward compatibility and plain text content)
        # Pattern to match @username (allows letters, numbers, dots, underscores, hyphens)
        # Matches: @username, @user.name, @user_name, @user-name, @user123
        plain_pattern = r'@([a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?)'
        plain_matches = re.findall(plain_pattern, text)
        for match in plain_matches:
            # Remove any trailing punctuation that might have been captured
            match = match.rstrip('.,;:!?)')
            if match and len(match) > 0 and match not in mentions:
                mentions.append(match)
        
        return list(set(mentions))  # Remove duplicates


# Alias for backward compatibility
Story = UserStory


class Task(models.Model):
    """Task within a user story."""
    
    # Note: STATUS_CHOICES and PRIORITY_CHOICES are now dynamic based on ProjectConfiguration
    # These are kept for backward compatibility and default values only
    DEFAULT_STATUS = 'todo'
    DEFAULT_PRIORITY = 'medium'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(
        UserStory, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        null=True,
        blank=True,
        help_text="Parent story (null for standalone tasks)"
    )
    
    # Parent task for sub-tasks
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
        help_text="Parent task for sub-tasks"
    )
    
    # Work item number (e.g., TASK-45)
    number = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Unique work item number within project"
    )
    
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    # Status is now dynamic - validated against ProjectConfiguration.custom_states
    status = models.CharField(max_length=50, default=DEFAULT_STATUS, help_text="Workflow state (validated against project configuration)")
    # Priority is now dynamic - can be extended to use ProjectConfiguration if needed
    priority = models.CharField(max_length=20, default=DEFAULT_PRIORITY, help_text="Priority level")
    
    assigned_to = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    
    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    actual_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Progress tracking
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Task completion percentage (0-100)"
    )
    
    # Tags
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorizing and filtering tasks"
    )
    
    # Labels (color-coded, different from tags)
    labels = models.JSONField(
        default=list,
        blank=True,
        help_text="Color-coded labels for visual grouping (e.g., [{'name': 'Urgent', 'color': '#red'}])"
    )
    
    # Custom fields - values based on project configuration
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom field values based on project configuration"
    )
    
    # Component/module
    component = models.CharField(
        max_length=100,
        blank=True,
        help_text="Component or module this task belongs to"
    )
    
    # Due date
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Due date for this task"
    )
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_tasks',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        indexes = [
            models.Index(fields=['story', 'status']),
            models.Index(fields=['parent_task', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['component']),
        ]
    
    def __str__(self):
        return self.title

    def get_valid_statuses(self):
        """Get valid status values from project configuration."""
        # If task has a story, use story's project configuration
        if self.story and self.story.project:
            try:
                config = self.story.project.configuration
                if config and config.custom_states:
                    return [state.get('id') for state in config.custom_states if state.get('id')]
            except ProjectConfiguration.DoesNotExist:
                pass
        # Fallback to default states if no configuration exists
        return ['todo', 'in_progress', 'done']
    
    def clean(self):
        """Validate task relationships and status."""
        from django.core.exceptions import ValidationError
        
        # Prevent circular parent references
        if self.parent_task:
            if self.parent_task.id == self.id:
                raise ValidationError("A task cannot be its own parent.")
            
            # Check for circular references
            current = self.parent_task
            visited = {self.id}
            while current:
                if current.id in visited:
                    raise ValidationError("Circular parent reference detected.")
                visited.add(current.id)
                current = getattr(current, 'parent_task', None)
        
        # Validate status against project configuration
        if self.status:
            valid_statuses = self.get_valid_statuses()
            if self.status not in valid_statuses:
                raise ValidationError({
                    'status': f"Invalid status '{self.status}'. Valid statuses for this project are: {', '.join(valid_statuses)}"
                })
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)


class Bug(models.Model):
    """Bug/Defect tracking model."""
    
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('trivial', 'Trivial'),
    ]
    
    PRIORITY_CHOICES = [
        ('p0', 'P0 - Blocker'),
        ('p1', 'P1 - Critical'),
        ('p2', 'P2 - High'),
        ('p3', 'P3 - Medium'),
        ('p4', 'P4 - Low'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('reopened', 'Reopened'),
    ]
    
    RESOLUTION_CHOICES = [
        ('fixed', 'Fixed'),
        ('wont_fix', "Won't Fix"),
        ('duplicate', 'Duplicate'),
        ('invalid', 'Invalid'),
        ('works_as_designed', 'Works as Designed'),
    ]
    
    ENVIRONMENT_CHOICES = [
        ('production', 'Production'),
        ('staging', 'Staging'),
        ('development', 'Development'),
        ('local', 'Local'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bugs')
    
    # Work item number (e.g., BUG-789)
    number = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Unique work item number within project"
    )
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='p3')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    resolution = models.CharField(
        max_length=20,
        choices=RESOLUTION_CHOICES,
        null=True,
        blank=True,
        help_text="Resolution when bug is closed/resolved"
    )
    
    environment = models.CharField(
        max_length=20,
        choices=ENVIRONMENT_CHOICES,
        default='production',
        help_text="Environment where bug was found"
    )
    
    # Reproduction information
    reproduction_steps = models.TextField(
        blank=True,
        help_text="Steps to reproduce the bug"
    )
    expected_behavior = models.TextField(
        blank=True,
        help_text="Expected behavior"
    )
    actual_behavior = models.TextField(
        blank=True,
        help_text="Actual behavior observed"
    )
    
    # Assignment
    reporter = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_bugs',
        help_text="User who reported the bug"
    )
    assigned_to = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bugs',
        help_text="User assigned to fix the bug"
    )
    
    # Relationships
    linked_stories = models.ManyToManyField(
        UserStory,
        related_name='linked_bugs',
        blank=True,
        help_text="User stories related to this bug"
    )
    duplicate_of = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='duplicates',
        help_text="If this is a duplicate, link to the original bug"
    )
    
    # Metadata
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorizing and filtering bugs"
    )
    labels = models.JSONField(
        default=list,
        blank=True,
        help_text="Color-coded labels for visual grouping"
    )
    
    # Custom fields - values based on project configuration
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom field values based on project configuration"
    )
    
    component = models.CharField(
        max_length=100,
        blank=True,
        help_text="Component or module where bug occurs"
    )
    
    # Dates
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Target date for bug resolution"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the bug was resolved"
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the bug was closed"
    )
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_bugs',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_bugs',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'bugs'
        verbose_name = 'Bug'
        verbose_name_plural = 'Bugs'
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['project', 'severity']),
            models.Index(fields=['project', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['reporter', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['project', 'due_date']),
            models.Index(fields=['component']),
            models.Index(fields=['project', 'component']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.project.name} - {self.title}'
    
    def get_valid_statuses(self):
        """Get valid status values - Bug model has fixed STATUS_CHOICES, not custom states."""
        # Bug model always uses fixed STATUS_CHOICES, not custom states from project configuration
        return [choice[0] for choice in self.STATUS_CHOICES]
    
    def clean(self):
        """Validate status against Bug model's STATUS_CHOICES."""
        from django.core.exceptions import ValidationError
        
        if self.status:
            valid_statuses = self.get_valid_statuses()
            if self.status not in valid_statuses:
                raise ValidationError({
                    'status': f"Invalid status '{self.status}'. Valid statuses are: {', '.join(valid_statuses)}"
                })
    
    def save(self, *args, **kwargs):
        """Override save to run validation and set resolved_at/closed_at timestamps."""
        from django.utils import timezone
        
        # Run validation
        self.clean()
        
        # Set resolved_at when status changes to resolved
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status != 'resolved':
            self.resolved_at = None
        
        # Set closed_at when status changes to closed
        if self.status == 'closed' and not self.closed_at:
            self.closed_at = timezone.now()
        elif self.status != 'closed':
            self.closed_at = None
        
        super().save(*args, **kwargs)


class Issue(models.Model):
    """General issue tracking model (broader than bugs - includes feature requests, questions, etc.)."""
    
    TYPE_CHOICES = [
        ('bug', 'Bug'),
        ('feature_request', 'Feature Request'),
        ('question', 'Question'),
        ('documentation', 'Documentation'),
        ('performance', 'Performance'),
        ('security', 'Security'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('blocker', 'Blocker'),
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('trivial', 'Trivial'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('reopened', 'Reopened'),
    ]
    
    RESOLUTION_CHOICES = [
        ('fixed', 'Fixed'),
        ('wont_fix', "Won't Fix"),
        ('duplicate', 'Duplicate'),
        ('invalid', 'Invalid'),
        ('works_as_designed', 'Works as Designed'),
        ('answered', 'Answered'),
        ('implemented', 'Implemented'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    
    # Work item number (e.g., ISSUE-456)
    number = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Unique work item number within project"
    )
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    
    issue_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other', help_text="Type of issue")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='minor')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolution = models.CharField(
        max_length=20,
        choices=RESOLUTION_CHOICES,
        null=True,
        blank=True,
        help_text="Resolution when issue is closed/resolved"
    )
    
    environment = models.CharField(
        max_length=100,
        blank=True,
        help_text="Environment where issue occurs (if applicable)"
    )
    
    # Assignment
    reporter = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_issues',
        help_text="User who reported the issue"
    )
    assigned_to = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_issues',
        help_text="User assigned to work on the issue"
    )
    
    # Watchers - users who want to be notified of updates
    watchers = models.ManyToManyField(
        'authentication.User',
        related_name='watched_issues',
        blank=True,
        help_text="Users watching this issue for updates"
    )
    
    # Relationships - link to related work items
    linked_stories = models.ManyToManyField(
        UserStory,
        related_name='linked_issues',
        blank=True,
        help_text="User stories related to this issue"
    )
    linked_tasks = models.ManyToManyField(
        Task,
        related_name='linked_issues',
        blank=True,
        help_text="Tasks related to this issue"
    )
    linked_bugs = models.ManyToManyField(
        'Bug',
        related_name='linked_issues',
        blank=True,
        help_text="Bugs related to this issue"
    )
    duplicate_of = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='duplicates',
        help_text="If this is a duplicate, link to the original issue"
    )
    
    # Metadata
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorizing and filtering issues"
    )
    labels = models.JSONField(
        default=list,
        blank=True,
        help_text="Color-coded labels for visual grouping"
    )
    
    # Custom fields - values based on project configuration
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom field values based on project configuration"
    )
    
    component = models.CharField(
        max_length=100,
        blank=True,
        help_text="Component or module related to this issue"
    )
    
    # Dates
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Target date for issue resolution"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the issue was resolved"
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the issue was closed"
    )
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_issues',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_issues',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'issues'
        verbose_name = 'Issue'
        verbose_name_plural = 'Issues'
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['project', 'issue_type']),
            models.Index(fields=['project', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['reporter', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['project', 'due_date']),
            models.Index(fields=['component']),
            models.Index(fields=['project', 'component']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.project.name} - {self.title}'
    
    def get_valid_statuses(self):
        """Get valid status values - Issue model has fixed STATUS_CHOICES, not custom states."""
        # Issue model always uses fixed STATUS_CHOICES, not custom states from project configuration
        return [choice[0] for choice in self.STATUS_CHOICES]
    
    def clean(self):
        """Validate status against Issue model's STATUS_CHOICES."""
        from django.core.exceptions import ValidationError
        
        if self.status:
            valid_statuses = self.get_valid_statuses()
            if self.status not in valid_statuses:
                raise ValidationError({
                    'status': f"Invalid status '{self.status}'. Valid statuses are: {', '.join(valid_statuses)}"
                })
    
    def save(self, *args, **kwargs):
        """Override save to run validation and set resolved_at/closed_at timestamps."""
        from django.utils import timezone
        
        # Run validation
        self.clean()
        
        # Set resolved_at when status changes to resolved
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status != 'resolved':
            self.resolved_at = None
        
        # Set closed_at when status changes to closed
        if self.status == 'closed' and not self.closed_at:
            self.closed_at = timezone.now()
        elif self.status != 'closed':
            self.closed_at = None
        
        super().save(*args, **kwargs)


class TimeLog(models.Model):
    """Time logging entry for tracking time spent on work items."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Work item relationships - at least one must be set
    story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='time_logs',
        help_text="User story this time log is for"
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='time_logs',
        help_text="Task this time log is for"
    )
    bug = models.ForeignKey(
        Bug,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='time_logs',
        help_text="Bug this time log is for"
    )
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='time_logs',
        help_text="Issue this time log is for"
    )
    
    # User who logged the time
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='time_logs',
        help_text="User who logged this time"
    )
    
    # Time tracking
    start_time = models.DateTimeField(
        help_text="When the work started"
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the work ended (null if still in progress)"
    )
    duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Duration in minutes (calculated if end_time is set, or manually entered)"
    )
    
    # Description
    description = models.TextField(
        blank=True,
        help_text="Description of work performed"
    )
    
    # Billable flag
    is_billable = models.BooleanField(
        default=True,
        help_text="Whether this time is billable"
    )
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_time_logs',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_time_logs',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'time_logs'
        verbose_name = 'Time Log'
        verbose_name_plural = 'Time Logs'
        indexes = [
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['story', 'start_time']),
            models.Index(fields=['task', 'start_time']),
            models.Index(fields=['bug', 'start_time']),
            models.Index(fields=['issue', 'start_time']),
        ]
        ordering = ['-start_time']
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(story__isnull=False) |
                    models.Q(task__isnull=False) |
                    models.Q(bug__isnull=False) |
                    models.Q(issue__isnull=False)
                ),
                name='time_log_must_have_work_item'
            )
        ]
    
    def __str__(self):
        work_item = self.story or self.task or self.bug or self.issue
        work_item_type = 'Story' if self.story else 'Task' if self.task else 'Bug' if self.bug else 'Issue'
        return f'{work_item_type} - {self.user.email} - {self.start_time}'
    
    def save(self, *args, **kwargs):
        """Override save to calculate duration if end_time is set."""
        from django.utils import timezone
        
        # Calculate duration if end_time is set and duration_minutes is not manually set
        if self.end_time and not self.duration_minutes:
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
        elif not self.end_time:
            # If no end_time, duration should be None (timer still running)
            self.duration_minutes = None
        
        super().save(*args, **kwargs)
    
    @property
    def duration_hours(self):
        """Get duration in hours."""
        if self.duration_minutes:
            return round(self.duration_minutes / 60, 2)
        return None
    
    @property
    def is_active(self):
        """Check if timer is still running (no end_time)."""
        return self.end_time is None


class ProjectConfiguration(models.Model):
    """Project-specific configuration settings."""
    
    BOARD_VIEW_CHOICES = [
        ('kanban', 'Kanban'),
        ('list', 'List'),
        ('table', 'Table'),
        ('timeline', 'Timeline'),
        ('calendar', 'Calendar'),
    ]
    
    SWIMLANE_GROUPING_CHOICES = [
        ('none', 'None'),
        ('assignee', 'Assignee'),
        ('epic', 'Epic'),
        ('priority', 'Priority'),
        ('component', 'Component'),
        ('custom_field', 'Custom Field'),
    ]
    
    CARD_COLOR_BY_CHOICES = [
        ('priority', 'Priority'),
        ('epic', 'Epic'),
        ('type', 'Story Type'),
        ('component', 'Component'),
        ('custom', 'Custom'),
    ]
    
    SPRINT_START_DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='configuration'
    )
    
    # Workflow & Board Configuration
    custom_states = models.JSONField(
        default=list,
        blank=True,
        help_text="Custom workflow states for this project"
    )
    state_transitions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Allowed state transitions"
    )
    board_columns = models.JSONField(
        default=list,
        blank=True,
        help_text="Board column configuration (order, visibility, etc.)"
    )
    
    # Work Item Number Prefixes
    story_prefix = models.CharField(
        max_length=20,
        default='STORY-',
        help_text="Prefix for story numbers (e.g., STORY-)"
    )
    task_prefix = models.CharField(
        max_length=20,
        default='TASK-',
        help_text="Prefix for task numbers (e.g., TASK-)"
    )
    bug_prefix = models.CharField(
        max_length=20,
        default='BUG-',
        help_text="Prefix for bug numbers (e.g., BUG-)"
    )
    issue_prefix = models.CharField(
        max_length=20,
        default='ISSUE-',
        help_text="Prefix for issue numbers (e.g., ISSUE-)"
    )
    epic_prefix = models.CharField(
        max_length=20,
        default='EPIC-',
        help_text="Prefix for epic numbers (e.g., EPIC-)"
    )
    
    # Story Point Configuration
    max_story_points_per_story = models.IntegerField(default=21, help_text="Maximum story points allowed per story")
    min_story_points_per_story = models.IntegerField(default=1, help_text="Minimum story points allowed per story")
    story_point_scale = models.JSONField(
        default=list,
        blank=True,
        help_text="Allowed story point values (e.g., Fibonacci: [1,2,3,5,8,13,21])"
    )
    max_story_points_per_sprint = models.IntegerField(default=40, help_text="Maximum total story points allowed per sprint")
    story_points_required = models.BooleanField(default=False, help_text="Require story points before moving to 'In Progress'")
    
    # Sprint Configuration
    default_sprint_duration_days = models.IntegerField(default=14, help_text="Default sprint duration in days")
    sprint_start_day = models.IntegerField(
        choices=SPRINT_START_DAY_CHOICES,
        default=0,
        help_text="Default day of week for sprint start"
    )
    auto_close_sprints = models.BooleanField(default=False, help_text="Automatically close sprints when end date passes")
    allow_overcommitment = models.BooleanField(default=False, help_text="Allow sprints to exceed max story points")
    
    # Board Customization
    default_board_view = models.CharField(
        max_length=20,
        choices=BOARD_VIEW_CHOICES,
        default='kanban',
        help_text="Default board view"
    )
    swimlane_grouping = models.CharField(
        max_length=20,
        choices=SWIMLANE_GROUPING_CHOICES,
        default='none',
        null=True,
        blank=True,
        help_text="Swimlane grouping option"
    )
    swimlane_custom_field = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Custom field name for swimlane grouping"
    )
    card_display_fields = models.JSONField(
        default=list,
        blank=True,
        help_text="Fields to display on cards"
    )
    card_color_by = models.CharField(
        max_length=20,
        choices=CARD_COLOR_BY_CHOICES,
        default='priority',
        null=True,
        blank=True,
        help_text="Card color coding rule"
    )
    
    # Automation, Notifications, Permissions, etc.
    automation_rules = models.JSONField(
        default=list,
        blank=True,
        help_text="Workflow automation rules"
    )
    notification_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Project notification preferences"
    )
    permission_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Project-specific permission overrides"
    )
    custom_roles = models.JSONField(
        default=list,
        blank=True,
        help_text="Custom roles defined for this project (e.g., ['architect', 'devops', 'support'])"
    )
    integration_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Project-specific integration settings"
    )
    custom_fields_schema = models.JSONField(
        default=list,
        blank=True,
        help_text="Schema for custom fields in this project"
    )
    validation_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="Validation rules for stories/tasks"
    )
    analytics_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Analytics and reporting preferences"
    )
    
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_project_configurations',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_configurations'
        verbose_name = 'Project Configuration'
        verbose_name_plural = 'Project Configurations'
    
    def __str__(self):
        return f'Configuration for {self.project.name}'
    
    def get_default_custom_states(self):
        """Return default workflow states."""
        return [
            {
                "id": "backlog",
                "name": "Backlog",
                "order": 0,
                "color": "#gray",
                "is_default": True,
                "is_final": False,
                "wip_limit": None,
                "auto_transitions": []
            },
            {
                "id": "todo",
                "name": "To Do",
                "order": 1,
                "color": "#blue",
                "is_default": False,
                "is_final": False,
                "wip_limit": None,
                "auto_transitions": []
            },
            {
                "id": "in_progress",
                "name": "In Progress",
                "order": 2,
                "color": "#orange",
                "is_default": False,
                "is_final": False,
                "wip_limit": None,
                "auto_transitions": []
            },
            {
                "id": "review",
                "name": "Review",
                "order": 3,
                "color": "#orange",
                "is_default": False,
                "is_final": False,
                "wip_limit": None,
                "auto_transitions": []
            },
            {
                "id": "done",
                "name": "Done",
                "order": 4,
                "color": "#green",
                "is_default": False,
                "is_final": True,
                "wip_limit": None,
                "auto_transitions": []
            }
        ]
    
    def get_default_story_point_scale(self):
        """Return default Fibonacci story point scale."""
        return [1, 2, 3, 5, 8, 13, 21]
    
    def get_default_state_transitions(self):
        """Return default state transitions."""
        return {
            "backlog": ["todo", "in_progress"],
            "todo": ["in_progress", "backlog"],
            "in_progress": ["review", "testing", "todo"],
            "review": ["done", "in_progress"],
            "testing": ["done", "review"],
            "done": []  # Final state
        }
    
    def initialize_defaults(self):
        """Initialize default configuration values."""
        if not self.custom_states:
            self.custom_states = self.get_default_custom_states()
        if not self.story_point_scale:
            self.story_point_scale = self.get_default_story_point_scale()
        if not self.state_transitions:
            self.state_transitions = self.get_default_state_transitions()
        if not self.card_display_fields:
            self.card_display_fields = ["title", "assignee", "story_points", "tags", "due_date"]
        if not self.notification_settings:
            self.notification_settings = {
                "email_enabled": True,
                "in_app_enabled": True,
                "mention_notifications": True,
                "status_change_notifications": True,
                "assignment_notifications": True,
            }
        if not self.permission_settings:
            self.permission_settings = {
                "default_role": "viewer",
                "allow_self_assignment": True,
                "require_approval_for_status_change": False,
            }
        if not self.custom_roles:
            self.custom_roles = []
        self.save()


class Mention(models.Model):
    """User mention in story description or comments."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mention_text = models.CharField(max_length=200, help_text="The actual @mention text (e.g., '@john.doe')")
    mentioned_user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='mentions',
        help_text="User who was mentioned"
    )
    story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        related_name='mentions',
        null=True,
        blank=True,
        help_text="Story where mention occurred"
    )
    comment = models.ForeignKey(
        'StoryComment',
        on_delete=models.CASCADE,
        related_name='mentions',
        null=True,
        blank=True,
        help_text="Comment where mention occurred (if implemented)"
    )
    read = models.BooleanField(default=False, help_text="Whether the mention has been read by the user")
    notified = models.BooleanField(default=False, help_text="Whether notification was sent")
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_mentions',
        verbose_name='Created By'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'mentions'
        verbose_name = 'Mention'
        verbose_name_plural = 'Mentions'
        indexes = [
            models.Index(fields=['mentioned_user', 'read']),
            models.Index(fields=['story']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'@{self.mentioned_user.email} in {self.story.title if self.story else "comment"}'


class StoryComment(models.Model):
    """Comment on a user story with threading support."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(UserStory, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        help_text="Parent comment for threading"
    )
    author = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='story_comments')
    content = models.TextField()
    reactions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Emoji reactions to the comment"
    )
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_story_comments'
    )
    
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_story_comments',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_story_comments',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    def extract_mentions(self):
        """Extract @mentions from comment content.
        
        Handles both HTML format (from rich text editor) and plain text format.
        HTML format: <span class="mention" data-id="email@example.com" data-label="Name">@Name</span>
        Plain text format: @username
        """
        mentions = []
        if not self.content:
            return mentions
        
        # First, try to extract from HTML mention spans (data-id attribute contains email)
        # Pattern: data-id="email@example.com" or data-id='email@example.com'
        html_pattern = r'data-id=["\']([^"\']+@[^"\']+)["\']'
        html_matches = re.findall(html_pattern, self.content)
        for match in html_matches:
            # Extract email from data-id
            email = match.strip()
            if '@' in email:
                # It's an email - add it directly (user lookup will handle email matching)
                if email not in mentions:
                    mentions.append(email)
                # Also add username part for fallback matching
                username = email.split('@')[0]
                if username and username not in mentions:
                    mentions.append(username)
        
        # Also extract plain text @mentions (for backward compatibility and plain text content)
        # Pattern to match @username (allows letters, numbers, dots, underscores, hyphens)
        # Matches: @username, @user.name, @user_name, @user-name, @user123
        plain_pattern = r'@([a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?)'
        plain_matches = re.findall(plain_pattern, self.content)
        for match in plain_matches:
            # Remove any trailing punctuation that might have been captured
            match = match.rstrip('.,;:!?)')
            if match and len(match) > 0 and match not in mentions:
                mentions.append(match)
        
        return list(set(mentions))  # Remove duplicates
    
    class Meta:
        db_table = 'story_comments'
        verbose_name = 'Story Comment'
        verbose_name_plural = 'Story Comments'
        indexes = [
            models.Index(fields=['story', 'created_at']),
            models.Index(fields=['parent']),
        ]
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author.email} on {self.story.title}'


class StoryDependency(models.Model):
    """Dependency relationship between user stories."""
    
    DEPENDENCY_TYPE_CHOICES = [
        ('blocks', 'Blocks'),
        ('blocked_by', 'Blocked By'),
        ('relates_to', 'Relates To'),
        ('duplicates', 'Duplicates'),
        ('depends_on', 'Depends On'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        related_name='outgoing_dependencies',
        help_text="Story that has the dependency"
    )
    target_story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        related_name='incoming_dependencies',
        help_text="Story that is depended upon"
    )
    dependency_type = models.CharField(
        max_length=20,
        choices=DEPENDENCY_TYPE_CHOICES,
        default='blocks',
        help_text="Type of dependency relationship"
    )
    description = models.TextField(blank=True, help_text="Optional description of the dependency")
    resolved = models.BooleanField(default=False, help_text="Whether the dependency has been resolved")
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_dependencies'
    )
    
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_story_dependencies',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_story_dependencies',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'story_dependencies'
        verbose_name = 'Story Dependency'
        verbose_name_plural = 'Story Dependencies'
        indexes = [
            models.Index(fields=['source_story', 'dependency_type']),
            models.Index(fields=['target_story', 'dependency_type']),
            models.Index(fields=['resolved']),
        ]
        unique_together = [['source_story', 'target_story', 'dependency_type']]
    
    def __str__(self):
        return f'{self.source_story.title} {self.get_dependency_type_display()} {self.target_story.title}'


class StoryAttachment(models.Model):
    """File attachment for a user story."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(UserStory, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='story_attachments/%Y/%m/%d/', help_text="Uploaded file")
    file_name = models.CharField(max_length=255, help_text="Original file name")
    file_size = models.BigIntegerField(help_text="File size in bytes")
    file_type = models.CharField(max_length=100, help_text="MIME type of the file")
    description = models.TextField(blank=True, help_text="Optional description of the attachment")
    
    uploaded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_attachments'
    )
    
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_story_attachments',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_story_attachments',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'story_attachments'
        verbose_name = 'Story Attachment'
        verbose_name_plural = 'Story Attachments'
        indexes = [
            models.Index(fields=['story', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.file_name} on {self.story.title}'
    
    def get_file_size_display(self):
        """Return human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class Notification(models.Model):
    """In-app notification for users."""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('mention', 'Mention'),
        ('comment', 'Comment'),
        ('status_change', 'Status Change'),
        ('assignment', 'Assignment'),
        ('story_created', 'Story Created'),
        ('story_updated', 'Story Updated'),
        ('dependency_added', 'Dependency Added'),
        ('dependency_resolved', 'Dependency Resolved'),
        ('attachment_added', 'Attachment Added'),
        ('due_date_approaching', 'Due Date Approaching'),
        ('sprint_start', 'Sprint Start'),
        ('sprint_end', 'Sprint End'),
        ('automation_triggered', 'Automation Triggered'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="User who receives the notification"
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional notification data (e.g., old_status, new_status, etc.)"
    )
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Related objects
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    comment = models.ForeignKey(
        StoryComment,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    mention = models.ForeignKey(
        Mention,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_notifications',
        verbose_name='Created By'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.notification_type} notification for {self.recipient.email}'


class Watcher(models.Model):
    """
    Generic Watcher model to allow users to subscribe to updates for any content object.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='watchers'
    )

    # Generic Foreign Key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watchers'
        verbose_name = 'Watcher'
        verbose_name_plural = 'Watchers'
        unique_together = [['user', 'content_type', 'object_id']]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} watching {self.content_object}'


class Activity(models.Model):
    """
    Comprehensive activity log for tracking all changes and events in the project management system.
    Uses generic foreign keys to track activities on any model.
    """
    
    ACTIVITY_TYPE_CHOICES = [
        # Story activities
        ('story_created', 'Story Created'),
        ('story_updated', 'Story Updated'),
        ('story_deleted', 'Story Deleted'),
        ('story_status_changed', 'Story Status Changed'),
        ('story_priority_changed', 'Story Priority Changed'),
        ('story_assigned', 'Story Assigned'),
        ('story_unassigned', 'Story Unassigned'),
        ('story_moved_to_sprint', 'Story Moved to Sprint'),
        ('story_removed_from_sprint', 'Story Removed from Sprint'),
        ('story_points_changed', 'Story Points Changed'),
        
        # Task activities
        ('task_created', 'Task Created'),
        ('task_updated', 'Task Updated'),
        ('task_deleted', 'Task Deleted'),
        ('task_status_changed', 'Task Status Changed'),
        ('task_priority_changed', 'Task Priority Changed'),
        ('task_assigned', 'Task Assigned'),
        ('task_unassigned', 'Task Unassigned'),
        ('task_progress_updated', 'Task Progress Updated'),
        
        # Bug activities
        ('bug_created', 'Bug Created'),
        ('bug_updated', 'Bug Updated'),
        ('bug_deleted', 'Bug Deleted'),
        ('bug_status_changed', 'Bug Status Changed'),
        ('bug_severity_changed', 'Bug Severity Changed'),
        ('bug_resolved', 'Bug Resolved'),
        ('bug_closed', 'Bug Closed'),
        ('bug_reopened', 'Bug Reopened'),
        
        # Issue activities
        ('issue_created', 'Issue Created'),
        ('issue_updated', 'Issue Updated'),
        ('issue_deleted', 'Issue Deleted'),
        ('issue_status_changed', 'Issue Status Changed'),
        ('issue_resolved', 'Issue Resolved'),
        ('issue_closed', 'Issue Closed'),
        
        # Epic activities
        ('epic_created', 'Epic Created'),
        ('epic_updated', 'Epic Updated'),
        ('epic_deleted', 'Epic Deleted'),
        ('epic_status_changed', 'Epic Status Changed'),
        
        # Sprint activities
        ('sprint_created', 'Sprint Created'),
        ('sprint_updated', 'Sprint Updated'),
        ('sprint_deleted', 'Sprint Deleted'),
        ('sprint_started', 'Sprint Started'),
        ('sprint_completed', 'Sprint Completed'),
        
        # Project activities
        ('project_created', 'Project Created'),
        ('project_updated', 'Project Updated'),
        ('project_deleted', 'Project Deleted'),
        ('project_status_changed', 'Project Status Changed'),
        ('member_added', 'Member Added'),
        ('member_removed', 'Member Removed'),
        
        # Comment activities
        ('comment_added', 'Comment Added'),
        ('comment_updated', 'Comment Updated'),
        ('comment_deleted', 'Comment Deleted'),
        
        # Dependency activities
        ('dependency_added', 'Dependency Added'),
        ('dependency_removed', 'Dependency Removed'),
        ('dependency_resolved', 'Dependency Resolved'),
        
        # Attachment activities
        ('attachment_added', 'Attachment Added'),
        ('attachment_deleted', 'Attachment Deleted'),
        
        # Time log activities
        ('time_logged', 'Time Logged'),
        ('time_log_updated', 'Time Log Updated'),
        ('time_log_deleted', 'Time Log Deleted'),
        
        # Watcher activities
        ('watcher_added', 'Watcher Added'),
        ('watcher_removed', 'Watcher Removed'),
        
        # Other activities
        ('tag_added', 'Tag Added'),
        ('tag_removed', 'Tag Removed'),
        ('label_added', 'Label Added'),
        ('label_removed', 'Label Removed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Activity type
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES, db_index=True)
    
    # User who performed the activity
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities',
        help_text="User who performed this activity"
    )
    
    # Project context (for filtering)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='activities',
        null=True,
        blank=True,
        db_index=True,
        help_text="Project this activity belongs to"
    )
    
    # Generic foreign key to the object this activity relates to
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(db_index=True, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Activity description
    description = models.TextField(
        help_text="Human-readable description of the activity"
    )
    
    # Metadata about the activity (e.g., old_value, new_value, field_name)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data about the activity (e.g., old_status, new_status, changed_fields)"
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'activities'
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['content_type', 'object_id', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        user_str = self.user.email if self.user else 'System'
        return f'{user_str} - {self.get_activity_type_display()}'
    
    @property
    def content_object_title(self):
        """Get the title/name of the content object."""
        if self.content_object:
            if hasattr(self.content_object, 'title'):
                return self.content_object.title
            elif hasattr(self.content_object, 'name'):
                return self.content_object.name
            return str(self.content_object)
        return None


class EditHistory(models.Model):
    """
    Edit history model for tracking field-level changes to objects.
    Stores snapshots of object state before and after edits, with diff calculation.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User who made the change
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edit_histories',
        help_text="User who made this edit"
    )
    
    # Project context (for filtering)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='edit_histories',
        null=True,
        blank=True,
        db_index=True,
        help_text="Project this edit history belongs to"
    )
    
    # Generic foreign key to the object this edit history relates to
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(db_index=True, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Version number (increments for each edit)
    version = models.IntegerField(default=1, db_index=True, help_text="Version number of this edit")
    
    # Snapshot of object state before the edit
    old_values = models.JSONField(
        default=dict,
        blank=True,
        help_text="Field values before the edit"
    )
    
    # Snapshot of object state after the edit
    new_values = models.JSONField(
        default=dict,
        blank=True,
        help_text="Field values after the edit"
    )
    
    # List of fields that were changed
    changed_fields = models.JSONField(
        default=list,
        blank=True,
        help_text="List of field names that were changed"
    )
    
    # Diff representation (for text fields)
    diffs = models.JSONField(
        default=dict,
        blank=True,
        help_text="Computed diffs for text fields (field_name -> diff_data)"
    )
    
    # Edit description/comment
    comment = models.TextField(
        blank=True,
        help_text="Optional comment about this edit"
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'edit_histories'
        verbose_name = 'Edit History'
        verbose_name_plural = 'Edit Histories'
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-version']),
            models.Index(fields=['content_type', 'object_id', '-created_at']),
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']
        unique_together = [['content_type', 'object_id', 'version']]
    
    def __str__(self):
        user_str = self.user.email if self.user else 'System'
        obj_str = self.content_object_title or 'Unknown'
        return f'{user_str} - {obj_str} (v{self.version})'
    
    @property
    def content_object_title(self):
        """Get the title/name of the content object."""
        if self.content_object:
            if hasattr(self.content_object, 'title'):
                return self.content_object.title
            elif hasattr(self.content_object, 'name'):
                return self.content_object.name
            return str(self.content_object)
        return None
    
    def get_field_diff(self, field_name: str) -> dict:
        """
        Get the diff for a specific field.
        
        Returns:
            dict with keys: 'old_value', 'new_value', 'diff' (if text field)
        """
        old_value = self.old_values.get(field_name)
        new_value = self.new_values.get(field_name)
        
        result = {
            'old_value': old_value,
            'new_value': new_value,
        }
        
        # If there's a pre-computed diff, include it
        if field_name in self.diffs:
            result['diff'] = self.diffs[field_name]
        
        return result
    
    def get_all_diffs(self) -> dict:
        """
        Get diffs for all changed fields.
        
        Returns:
            dict mapping field_name -> diff_data
        """
        result = {}
        for field_name in self.changed_fields:
            result[field_name] = self.get_field_diff(field_name)
        return result


class SavedSearch(models.Model):
    """
    Saved search queries for users.
    Allows users to save frequently used search queries with filters.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User who saved this search
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='saved_searches',
        help_text="User who saved this search"
    )
    
    # Search name and description
    name = models.CharField(max_length=200, help_text="Name for this saved search")
    description = models.TextField(blank=True, help_text="Optional description")
    
    # Search query
    query = models.TextField(help_text="Search query string")
    
    # Search filters (stored as JSON)
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Search filters (e.g., project, status, assignee, etc.)"
    )
    
    # Content types to search (e.g., ['userstory', 'task', 'bug'])
    content_types = models.JSONField(
        default=list,
        blank=True,
        help_text="List of content types to search (e.g., ['userstory', 'task'])"
    )
    
    # Project context (optional - if None, searches across all accessible projects)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='saved_searches',
        null=True,
        blank=True,
        help_text="Optional project to limit search to"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True, help_text="When this search was last used")
    
    # Usage count
    usage_count = models.IntegerField(default=0, help_text="Number of times this search has been used")
    
    class Meta:
        db_table = 'saved_searches'
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', '-last_used_at']),
            models.Index(fields=['project', '-created_at']),
        ]
        ordering = ['-last_used_at', '-created_at']
        unique_together = [['user', 'name']]
    
    def __str__(self):
        return f'{self.user.email} - {self.name}'
    
    def mark_used(self):
        """Mark this search as used and increment usage count."""
        from django.utils import timezone
        self.last_used_at = timezone.now()
        self.usage_count += 1
        self.save(update_fields=['last_used_at', 'usage_count'])


class SearchHistory(models.Model):
    """Search history for tracking user search queries."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='search_history',
        help_text="User who performed this search"
    )
    query = models.TextField(help_text="Search query string")
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Search filters applied"
    )
    content_types = models.JSONField(
        default=list,
        blank=True,
        help_text="Content types searched"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='search_history',
        null=True,
        blank=True,
        help_text="Project context (if any)"
    )
    result_count = models.IntegerField(default=0, help_text="Number of results found")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'search_history'
        verbose_name = 'Search History'
        verbose_name_plural = 'Search Histories'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['project', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.email} - {self.query[:50]}...'


class FilterPreset(models.Model):
    """Saved filter presets for quick filtering."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='filter_presets',
        null=True,
        blank=True,
        help_text="Project this preset belongs to (null for global presets)"
    )
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='filter_presets',
        null=True,
        blank=True,
        help_text="User who created this preset (null for shared presets)"
    )
    name = models.CharField(max_length=200, help_text="Preset name")
    description = models.TextField(blank=True, help_text="Preset description")
    filters = models.JSONField(
        default=list,
        blank=True,
        help_text="Filter rules (array of FilterRule objects)"
    )
    is_shared = models.BooleanField(default=False, help_text="Whether this preset is shared with team")
    is_default = models.BooleanField(default=False, help_text="Whether this is a default preset")
    usage_count = models.IntegerField(default=0, help_text="Number of times this preset has been used")
    
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_filter_presets',
        verbose_name='Created By'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'filter_presets'
        verbose_name = 'Filter Preset'
        verbose_name_plural = 'Filter Presets'
        indexes = [
            models.Index(fields=['project', 'is_shared']),
            models.Index(fields=['user', 'is_shared']),
        ]
        ordering = ['is_default', 'name']
    
    def __str__(self):
        return self.name


class ProjectLabelPreset(models.Model):
    """Project-level label presets for standardization."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='label_presets',
        help_text="Project this label preset belongs to"
    )
    name = models.CharField(max_length=100, help_text="Label name")
    color = models.CharField(
        max_length=7,
        default='#3b82f6',
        help_text="Hex color code (e.g., #3b82f6)"
    )
    description = models.TextField(blank=True, help_text="Optional description of the label")
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is a default label for the project"
    )
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_label_presets',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_label_presets',
        verbose_name='Updated By'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_label_presets'
        verbose_name = 'Project Label Preset'
        verbose_name_plural = 'Project Label Presets'
        indexes = [
            models.Index(fields=['project', 'is_default']),
            models.Index(fields=['project', 'name']),
        ]
        ordering = ['is_default', 'name']
        unique_together = [['project', 'name']]
    
    def __str__(self):
        return f'{self.project.name} - {self.name}'


class Milestone(models.Model):
    """Project milestone for tracking major deliverables and deadlines."""
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Dates
    target_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    
    # Progress tracking
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Progress percentage (0-100)"
    )
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_milestones',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_milestones',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'milestones'
        verbose_name = 'Milestone'
        verbose_name_plural = 'Milestones'
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['project', 'target_date']),
        ]
        ordering = ['project', 'target_date']
    
    def __str__(self):
        return f'{self.project.name} - {self.name}'


class TicketReference(models.Model):
    """External ticket references (GitHub issues, Jira tickets, etc.)."""
    
    SYSTEM_CHOICES = [
        ('github', 'GitHub'),
        ('jira', 'Jira'),
        ('gitlab', 'GitLab'),
        ('linear', 'Linear'),
        ('asana', 'Asana'),
        ('trello', 'Trello'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ticket_references')
    
    # Reference to work item (generic foreign key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    work_item = GenericForeignKey('content_type', 'object_id')
    
    # External ticket details
    system = models.CharField(max_length=20, choices=SYSTEM_CHOICES)
    ticket_id = models.CharField(max_length=200, help_text="External ticket ID (e.g., issue number, ticket key)")
    ticket_url = models.URLField(max_length=500, blank=True, help_text="URL to the external ticket")
    title = models.CharField(max_length=300, blank=True, help_text="Title of the external ticket")
    status = models.CharField(max_length=50, blank=True, help_text="Status in external system")
    
    # Sync metadata
    last_synced_at = models.DateTimeField(null=True, blank=True)
    sync_enabled = models.BooleanField(default=True, help_text="Enable automatic syncing with external system")
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_ticket_references',
        verbose_name='Created By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ticket_references'
        verbose_name = 'Ticket Reference'
        verbose_name_plural = 'Ticket References'
        unique_together = [['content_type', 'object_id', 'system', 'ticket_id']]
        indexes = [
            models.Index(fields=['project', 'system']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f'{self.get_system_display()} #{self.ticket_id}'


class StoryLink(models.Model):
    """Links between stories (blocks, relates to, duplicates, etc.)."""
    
    LINK_TYPE_CHOICES = [
        ('blocks', 'Blocks'),
        ('blocked_by', 'Blocked By'),
        ('relates_to', 'Relates To'),
        ('duplicates', 'Duplicates'),
        ('duplicated_by', 'Duplicated By'),
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('depends_on', 'Depends On'),
        ('required_by', 'Required By'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='story_links')
    
    # Source story
    source_story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        related_name='outgoing_links',
        help_text="Story that has the link"
    )
    
    # Target story
    target_story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        related_name='incoming_links',
        help_text="Story that is linked to"
    )
    
    # Link type
    link_type = models.CharField(max_length=20, choices=LINK_TYPE_CHOICES)
    description = models.TextField(blank=True, help_text="Optional description of the link")
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_story_links',
        verbose_name='Created By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'story_links'
        verbose_name = 'Story Link'
        verbose_name_plural = 'Story Links'
        unique_together = [['source_story', 'target_story', 'link_type']]
        indexes = [
            models.Index(fields=['project', 'link_type']),
            models.Index(fields=['source_story']),
            models.Index(fields=['target_story']),
        ]
    
    def __str__(self):
        return f'{self.source_story.title} {self.get_link_type_display()} {self.target_story.title}'
    
    def clean(self):
        """Validate that source and target are different stories."""
        from django.core.exceptions import ValidationError
        if self.source_story_id and self.target_story_id:
            if self.source_story_id == self.target_story_id:
                raise ValidationError("Source and target stories cannot be the same.")


class StatusChangeApproval(models.Model):
    """Approval request for status changes when approval workflow is enabled."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Generic foreign key to work item (Story, Task, Bug, Issue)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    work_item = GenericForeignKey('content_type', 'object_id')
    
    # Status change details
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    reason = models.TextField(blank=True, help_text="Reason for status change")
    
    # Approval workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    requested_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='requested_approvals',
        help_text="User who requested the status change"
    )
    approver = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approvals_to_review',
        help_text="User who should approve this request"
    )
    approved_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requests',
        help_text="User who approved/rejected the request"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection if rejected")
    
    # Project reference for filtering
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='status_change_approvals',
        help_text="Project this approval belongs to"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'status_change_approvals'
        verbose_name = 'Status Change Approval'
        verbose_name_plural = 'Status Change Approvals'
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['approver', 'status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Approval {self.id} - {self.old_status} → {self.new_status} ({self.status})"
    
    def approve(self, approver, comment: str = ''):
        """Approve this status change request."""
        from django.utils import timezone
        self.status = 'approved'
        self.approved_by = approver
        self.approved_at = timezone.now()
        if comment:
            self.rejection_reason = comment  # Reuse field for approval comment
        self.save(update_fields=['status', 'approved_by', 'approved_at', 'rejection_reason', 'updated_at'])
        
        # Apply the status change to the work item
        self._apply_status_change()
    
    def reject(self, approver, reason: str):
        """Reject this status change request."""
        from django.utils import timezone
        self.status = 'rejected'
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.save(update_fields=['status', 'approved_by', 'approved_at', 'rejection_reason', 'updated_at'])
    
    def cancel(self):
        """Cancel this approval request."""
        self.status = 'cancelled'
        self.save(update_fields=['status', 'updated_at'])
    
    def _apply_status_change(self):
        """Apply the approved status change to the work item."""
        if self.status != 'approved':
            return
        
        work_item = self.work_item
        if not work_item:
            return
        
        # Update the status
        work_item.status = self.new_status
        work_item.save(update_fields=['status', 'updated_at'])
        
        # Create activity log
        from apps.projects.models import Activity, UserStory, Task, Bug, Issue
        Activity.objects.create(
            project=self.project,
            activity_type='status_change_approved',
            description=f"Status changed from {self.old_status} to {self.new_status} (approved)",
            user=self.approved_by,
            story=work_item if isinstance(work_item, UserStory) else None,
            task=work_item if isinstance(work_item, Task) else None,
            bug=work_item if isinstance(work_item, Bug) else None,
            issue=work_item if isinstance(work_item, Issue) else None,
        )


class CardTemplate(models.Model):
    """Template for creating cards/stories with predefined fields."""
    
    SCOPE_CHOICES = [
        ('project', 'Project'),
        ('global', 'Global'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='card_templates',
        null=True,
        blank=True,
        help_text="Project this template belongs to (null for global templates)"
    )
    
    name = models.CharField(max_length=200, help_text="Template name")
    description = models.TextField(blank=True, help_text="Template description")
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='project', help_text="Template scope")
    
    # Template fields - JSON structure with default values
    template_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Template field values (title, description, acceptance_criteria, story_type, priority, etc.)"
    )
    
    # Template metadata
    icon = models.CharField(max_length=50, blank=True, help_text="Icon identifier (e.g., 'bug', 'feature', 'task')")
    color = models.CharField(max_length=7, blank=True, help_text="Template color (hex code)")
    is_default = models.BooleanField(default=False, help_text="Whether this is a default template")
    usage_count = models.IntegerField(default=0, help_text="Number of times this template has been used")
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_card_templates',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_card_templates',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'card_templates'
        verbose_name = 'Card Template'
        verbose_name_plural = 'Card Templates'
        indexes = [
            models.Index(fields=['project', 'scope']),
            models.Index(fields=['scope', 'is_default']),
        ]
        ordering = ['scope', 'is_default', 'name']
    
    def __str__(self):
        scope_label = 'Global' if self.scope == 'global' else self.project.name if self.project else 'Unknown'
        return f'{scope_label} - {self.name}'


class BoardTemplate(models.Model):
    """Template for board configurations (columns, swimlanes, filters, etc.)."""
    
    SCOPE_CHOICES = [
        ('project', 'Project'),
        ('global', 'Global'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='board_templates',
        null=True,
        blank=True,
        help_text="Project this template belongs to (null for global templates)"
    )
    
    name = models.CharField(max_length=200, help_text="Template name")
    description = models.TextField(blank=True, help_text="Template description")
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='project', help_text="Template scope")
    
    # Board configuration template
    board_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Board configuration (columns, swimlanes, filters, grouping, etc.)"
    )
    
    # Template metadata
    icon = models.CharField(max_length=50, blank=True, help_text="Icon identifier")
    is_default = models.BooleanField(default=False, help_text="Whether this is a default template")
    usage_count = models.IntegerField(default=0, help_text="Number of times this template has been used")
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_board_templates',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_board_templates',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'board_templates'
        verbose_name = 'Board Template'
        verbose_name_plural = 'Board Templates'
        indexes = [
            models.Index(fields=['project', 'scope']),
            models.Index(fields=['scope', 'is_default']),
        ]
        ordering = ['scope', 'is_default', 'name']
    
    def __str__(self):
        scope_label = 'Global' if self.scope == 'global' else self.project.name if self.project else 'Unknown'
        return f'{scope_label} - {self.name}'


# ============================================================================
# Nice to Have Features Models
# ============================================================================

class CardCoverImage(models.Model):
    """Cover image for cards (stories, tasks, etc.)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Generic relation to any work item
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    image = models.ImageField(
        upload_to='card_covers/',
        help_text="Cover image for the card"
    )
    thumbnail = models.ImageField(
        upload_to='card_covers/thumbnails/',
        null=True,
        blank=True,
        help_text="Thumbnail version of the cover image"
    )
    
    is_primary = models.BooleanField(default=True, help_text="Primary cover image")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'card_cover_images'
        verbose_name = 'Card Cover Image'
        verbose_name_plural = 'Card Cover Images'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]


class CardChecklist(models.Model):
    """Checklist items for cards."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Generic relation to any work item
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    title = models.CharField(max_length=200, help_text="Checklist title")
    items = models.JSONField(
        default=list,
        help_text="List of checklist items: [{'id': 'uuid', 'text': 'string', 'completed': bool, 'order': int}]"
    )
    
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_checklists'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'card_checklists'
        verbose_name = 'Card Checklist'
        verbose_name_plural = 'Card Checklists'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]


class CardVote(models.Model):
    """Votes on cards (stories, tasks, etc.)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Generic relation to any work item
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='card_votes'
    )
    
    vote_type = models.CharField(
        max_length=20,
        choices=[
            ('upvote', 'Upvote'),
            ('downvote', 'Downvote'),
        ],
        default='upvote'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'card_votes'
        verbose_name = 'Card Vote'
        verbose_name_plural = 'Card Votes'
        unique_together = [['content_type', 'object_id', 'user']]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user']),
        ]


class StoryArchive(models.Model):
    """Archived stories."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.OneToOneField(
        UserStory,
        on_delete=models.CASCADE,
        related_name='archive'
    )
    
    archived_at = models.DateTimeField(auto_now_add=True)
    archived_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='archived_stories'
    )
    reason = models.TextField(blank=True, help_text="Reason for archiving")
    
    class Meta:
        db_table = 'story_archives'
        verbose_name = 'Story Archive'
        verbose_name_plural = 'Story Archives'
        indexes = [
            models.Index(fields=['archived_at']),
        ]


class StoryVersion(models.Model):
    """Version history for stories."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    
    version_number = models.IntegerField(help_text="Version number")
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    acceptance_criteria = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50)
    priority = models.CharField(max_length=20)
    story_points = models.IntegerField(null=True, blank=True)
    
    # Store full story data as JSON for complete history
    story_data = models.JSONField(
        default=dict,
        help_text="Complete story data at this version"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_story_versions'
    )
    
    class Meta:
        db_table = 'story_versions'
        verbose_name = 'Story Version'
        verbose_name_plural = 'Story Versions'
        unique_together = [['story', 'version_number']]
        indexes = [
            models.Index(fields=['story', '-version_number']),
        ]
        ordering = ['story', '-version_number']


class Webhook(models.Model):
    """Webhook configuration for external integrations."""
    
    EVENT_CHOICES = [
        ('story.created', 'Story Created'),
        ('story.updated', 'Story Updated'),
        ('story.deleted', 'Story Deleted'),
        ('sprint.created', 'Sprint Created'),
        ('sprint.completed', 'Sprint Completed'),
        ('task.completed', 'Task Completed'),
        ('comment.added', 'Comment Added'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='webhooks',
        null=True,
        blank=True
    )
    
    name = models.CharField(max_length=200, help_text="Webhook name")
    url = models.URLField(help_text="Webhook URL")
    events = models.JSONField(
        default=list,
        help_text="List of events to trigger webhook"
    )
    secret = models.CharField(
        max_length=200,
        blank=True,
        help_text="Secret for webhook signature"
    )
    
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_webhooks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'webhooks'
        verbose_name = 'Webhook'
        verbose_name_plural = 'Webhooks'
        indexes = [
            models.Index(fields=['project', 'is_active']),
        ]


class StoryClone(models.Model):
    """Record of cloned stories."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_story = models.ForeignKey(
        UserStory,
        on_delete=models.CASCADE,
        related_name='clones',
        help_text="Original story that was cloned"
    )
    cloned_story = models.OneToOneField(
        UserStory,
        on_delete=models.CASCADE,
        related_name='clone_source',
        help_text="The cloned story"
    )
    
    cloned_at = models.DateTimeField(auto_now_add=True)
    cloned_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cloned_stories'
    )
    
    class Meta:
        db_table = 'story_clones'
        verbose_name = 'Story Clone'
        verbose_name_plural = 'Story Clones'
        indexes = [
            models.Index(fields=['original_story']),
        ]
    
    def __str__(self):
        return f"Clone: {self.original_story.title} -> {self.cloned_story.title}"


class GitHubIntegration(models.Model):
    """GitHub integration configuration for a project."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_github_integrations')
    
    repository_owner = models.CharField(max_length=255, help_text="GitHub repository owner")
    repository_name = models.CharField(max_length=255, help_text="GitHub repository name")
    access_token = models.CharField(max_length=500, help_text="GitHub access token (encrypted)")
    
    is_active = models.BooleanField(default=True, help_text="Is this integration active?")
    sync_issues = models.BooleanField(default=True, help_text="Sync GitHub issues")
    sync_commits = models.BooleanField(default=False, help_text="Sync GitHub commits")
    sync_pull_requests = models.BooleanField(default=False, help_text="Sync pull requests")
    
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_project_github_integrations')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'project_github_integrations'
        verbose_name = 'GitHub Integration'
        verbose_name_plural = 'GitHub Integrations'
        unique_together = [['project', 'repository_owner', 'repository_name']]
        indexes = [
            models.Index(fields=['project', 'is_active']),
        ]
    
    def __str__(self):
        return f"GitHub: {self.repository_owner}/{self.repository_name}"


class JiraIntegration(models.Model):
    """Jira integration configuration for a project."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_jira_integrations')
    
    base_url = models.URLField(help_text="Jira base URL (e.g., https://yourcompany.atlassian.net)")
    project_key = models.CharField(max_length=50, help_text="Jira project key")
    email = models.EmailField(help_text="Jira email")
    api_token = models.CharField(max_length=500, help_text="Jira API token (encrypted)")
    
    is_active = models.BooleanField(default=True, help_text="Is this integration active?")
    sync_issues = models.BooleanField(default=True, help_text="Sync Jira issues")
    auto_create = models.BooleanField(default=False, help_text="Auto-create Jira issues for stories")
    
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_project_jira_integrations')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'project_jira_integrations'
        verbose_name = 'Jira Integration'
        verbose_name_plural = 'Jira Integrations'
        unique_together = [['project', 'base_url', 'project_key']]
        indexes = [
            models.Index(fields=['project', 'is_active']),
        ]
    
    def __str__(self):
        return f"Jira: {self.project_key} at {self.base_url}"


class SlackIntegration(models.Model):
    """Slack integration configuration for a project."""
    
    NOTIFICATION_EVENTS = [
        ('story_created', 'Story Created'),
        ('story_updated', 'Story Updated'),
        ('story_completed', 'Story Completed'),
        ('story_assigned', 'Story Assigned'),
        ('comment_added', 'Comment Added'),
        ('sprint_started', 'Sprint Started'),
        ('sprint_completed', 'Sprint Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_slack_integrations')
    
    webhook_url = models.URLField(blank=True, null=True, help_text="Slack webhook URL")
    bot_token = models.CharField(max_length=500, blank=True, null=True, help_text="Slack bot token (encrypted)")
    channel = models.CharField(max_length=255, blank=True, help_text="Default Slack channel")
    
    is_active = models.BooleanField(default=True, help_text="Is this integration active?")
    notification_events = models.JSONField(default=list, help_text="Events to send notifications for")
    
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_project_slack_integrations')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'project_slack_integrations'
        verbose_name = 'Slack Integration'
        verbose_name_plural = 'Slack Integrations'
        indexes = [
            models.Index(fields=['project', 'is_active']),
        ]
    
    def __str__(self):
        return f"Slack: {self.project.name} ({self.channel or 'webhook'})"


class TimeBudget(models.Model):
    """Time budget for tracking allocated time against various project entities."""
    
    SCOPE_CHOICES = [
        ('project', 'Project'),
        ('sprint', 'Sprint'),
        ('story', 'Story'),
        ('task', 'Task'),
        ('epic', 'Epic'),
        ('user', 'User'),
    ]
    
    PERIOD_CHOICES = [
        ('one_time', 'One Time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='time_budgets', null=True, blank=True)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name='time_budgets', null=True, blank=True)
    story = models.ForeignKey(UserStory, on_delete=models.CASCADE, related_name='time_budgets', null=True, blank=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='time_budgets', null=True, blank=True)
    epic = models.ForeignKey(Epic, on_delete=models.CASCADE, related_name='time_budgets', null=True, blank=True)
    user = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='time_budgets', null=True, blank=True)
    
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, help_text="What this budget applies to")
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='one_time', help_text="Budget period")
    
    budget_hours = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], help_text="Total budgeted hours")
    warning_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=80.0, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Warning threshold percentage")
    
    period_start = models.DateField(null=True, blank=True, help_text="Start date of budget period")
    period_end = models.DateField(null=True, blank=True, help_text="End date of budget period")
    
    is_active = models.BooleanField(default=True, help_text="Is this budget active?")
    auto_alert = models.BooleanField(default=True, help_text="Automatically create overtime records when exceeded")
    
    # Calculated fields (updated by TimeBudgetService)
    spent_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total hours spent (calculated)")
    remaining_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Remaining hours (calculated)")
    utilization_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Utilization percentage (calculated)")
    is_over_budget = models.BooleanField(default=False, help_text="Is over budget? (calculated)")
    is_warning_threshold_reached = models.BooleanField(default=False, help_text="Has warning threshold been reached? (calculated)")
    
    created_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_time_budgets')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'time_budgets'
        verbose_name = 'Time Budget'
        verbose_name_plural = 'Time Budgets'
        indexes = [
            models.Index(fields=['project', 'scope']),
            models.Index(fields=['sprint', 'scope']),
            models.Index(fields=['story', 'scope']),
            models.Index(fields=['task', 'scope']),
            models.Index(fields=['epic', 'scope']),
            models.Index(fields=['user', 'scope']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        scope_obj = self.get_scope_object()
        scope_name = str(scope_obj) if scope_obj else self.get_scope_display()
        return f"Time Budget: {scope_name} ({self.budget_hours}h)"
    
    def get_scope_object(self):
        """Get the object this budget applies to."""
        if self.scope == 'project' and self.project:
            return self.project
        elif self.scope == 'sprint' and self.sprint:
            return self.sprint
        elif self.scope == 'story' and self.story:
            return self.story
        elif self.scope == 'task' and self.task:
            return self.task
        elif self.scope == 'epic' and self.epic:
            return self.epic
        elif self.scope == 'user' and self.user:
            return self.user
        return None


class OvertimeRecord(models.Model):
    """Record of when a time budget was exceeded."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time_budget = models.ForeignKey(TimeBudget, on_delete=models.CASCADE, related_name='overtime_records')
    
    overtime_hours = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], help_text="Hours over budget")
    overtime_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage over budget")
    
    period_start = models.DateField(help_text="Start of period when overtime occurred")
    period_end = models.DateField(help_text="End of period when overtime occurred")
    
    alert_sent = models.BooleanField(default=False, help_text="Has alert been sent?")
    alert_sent_at = models.DateTimeField(null=True, blank=True, help_text="When was alert sent?")
    
    resolved = models.BooleanField(default=False, help_text="Has this overtime been resolved?")
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="When was this resolved?")
    resolved_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_overtime_records')
    resolution_notes = models.TextField(blank=True, help_text="Notes on how overtime was resolved")
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'overtime_records'
        verbose_name = 'Overtime Record'
        verbose_name_plural = 'Overtime Records'
        indexes = [
            models.Index(fields=['time_budget', 'resolved']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['alert_sent']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Overtime: {self.time_budget} (+{self.overtime_hours}h)"


class ProjectMember(models.Model):
    """
    Project-specific member with roles.
    Supports multiple roles per user per project and custom roles.
    
    Note: System roles are defined in apps.core.services.roles.RoleService
    This model uses RoleService for role validation and management.
    """
    
    @classmethod
    def get_system_roles(cls):
        """Get system roles from RoleService."""
        from apps.core.services.roles import RoleService
        return RoleService.get_all_system_roles()
    
    # For backward compatibility, expose SYSTEM_ROLES as a property
    @property
    def SYSTEM_ROLES(self):
        """Backward compatibility property."""
        return self.get_system_roles()
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_members',
        db_index=True
    )
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='project_memberships',
        db_index=True
    )
    roles = models.JSONField(
        default=list,
        help_text="List of roles for this user in this project. Can include system roles and custom roles."
    )
    
    # Metadata
    added_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_project_members',
        verbose_name='Added By'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_members'
        verbose_name = 'Project Member'
        verbose_name_plural = 'Project Members'
        unique_together = [['project', 'user']]
        indexes = [
            models.Index(fields=['project', 'user']),
            models.Index(fields=['project']),
        ]
    
    def __str__(self):
        roles_str = ', '.join(self.roles) if self.roles else 'No roles'
        return f'{self.user.email} in {self.project.name} ({roles_str})'
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles
    
    def has_any_role(self, roles: list) -> bool:
        """Check if user has any of the specified roles."""
        return any(role in self.roles for role in roles)


class GeneratedProject(models.Model):
    """Tracks a generated project's metadata and status."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='generated_projects'
    )
    workflow_execution = models.ForeignKey(
        'workflows.WorkflowExecution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_projects'
    )
    
    # File system path
    output_directory = models.CharField(max_length=500)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Statistics
    total_files = models.IntegerField(default=0)
    total_size = models.BigIntegerField(default=0)  # in bytes
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_generated_projects'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'generated_projects'
        verbose_name = 'Generated Project'
        verbose_name_plural = 'Generated Projects'
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['created_by', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.status}"


class ProjectFile(models.Model):
    """Tracks individual files in a generated project."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generated_project = models.ForeignKey(
        GeneratedProject,
        on_delete=models.CASCADE,
        related_name='files'
    )
    
    # File metadata
    file_path = models.CharField(max_length=500, db_index=True)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)  # e.g., 'python', 'javascript', 'markdown'
    file_size = models.BigIntegerField(default=0)  # in bytes
    content_hash = models.CharField(max_length=64)  # SHA-256 hash
    
    # File content (optional, for small files)
    content_preview = models.TextField(blank=True, help_text="First 1000 chars")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_files'
        verbose_name = 'Project File'
        verbose_name_plural = 'Project Files'
        indexes = [
            models.Index(fields=['generated_project', 'file_path']),
            models.Index(fields=['file_type']),
            models.Index(fields=['content_hash']),
        ]
        unique_together = [['generated_project', 'file_path']]
        ordering = ['file_path']
    
    def __str__(self):
        return f"{self.file_path} ({self.generated_project.project.name})"


class RepositoryExport(models.Model):
    """Tracks repository export jobs."""
    
    EXPORT_TYPE_CHOICES = [
        ('zip', 'ZIP Archive'),
        ('tar', 'TAR Archive'),
        ('tar.gz', 'TAR GZIP Archive'),
        ('github', 'GitHub Repository'),
        ('gitlab', 'GitLab Repository'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('exporting', 'Exporting'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generated_project = models.ForeignKey(
        GeneratedProject,
        on_delete=models.CASCADE,
        related_name='exports'
    )
    
    # Export configuration
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPE_CHOICES)
    repository_name = models.CharField(max_length=255, blank=True)
    repository_url = models.URLField(blank=True)
    
    # Export result
    archive_path = models.CharField(max_length=500, blank=True)
    archive_size = models.BigIntegerField(null=True, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Configuration (for GitHub/GitLab)
    config = models.JSONField(default=dict, blank=True)
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'repository_exports'
        verbose_name = 'Repository Export'
        verbose_name_plural = 'Repository Exports'
        indexes = [
            models.Index(fields=['generated_project', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['export_type']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.generated_project.project.name} - {self.export_type} - {self.status}"

