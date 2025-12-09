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
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True, default='')
    
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
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
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
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    acceptance_criteria = models.TextField()
    
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
        """Extract @mentions from description and acceptance_criteria."""
        mentions = []
        text = f"{self.description} {self.acceptance_criteria}"
        pattern = r'@(\w+(?:\.\w+)?)'
        matches = re.findall(pattern, text)
        for match in matches:
            mentions.append(match)
        return mentions


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
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.project.name} - {self.title}'
    
    def get_valid_statuses(self):
        """Get valid status values from project configuration."""
        try:
            config = self.project.configuration
            if config and config.custom_states:
                return [state.get('id') for state in config.custom_states if state.get('id')]
        except ProjectConfiguration.DoesNotExist:
            pass
        # Fallback to default states if no configuration exists
        return ['new', 'assigned', 'in_progress', 'resolved', 'closed', 'reopened']
    
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
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.project.name} - {self.title}'
    
    def get_valid_statuses(self):
        """Get valid status values from project configuration."""
        try:
            config = self.project.configuration
            if config and config.custom_states:
                return [state.get('id') for state in config.custom_states if state.get('id')]
        except ProjectConfiguration.DoesNotExist:
            pass
        # Fallback to default states if no configuration exists
        return ['open', 'in_progress', 'resolved', 'closed', 'reopened']
    
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

