"""
AI Project Management models for HishamOS.
"""

from django.db import models
import uuid


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
    description = models.TextField()
    
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
    
    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stories')
    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stories'
    )
    epic = models.ForeignKey(
        Epic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stories'
    )
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    acceptance_criteria = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    story_points = models.IntegerField(null=True, blank=True)
    
    # AI generation metadata
    generated_by_ai = models.BooleanField(default=False)
    generation_workflow = models.ForeignKey(
        'workflows.WorkflowExecution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    assigned_to = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_stories'
    )
    
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


class Task(models.Model):
    """Task within a user story."""
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(UserStory, on_delete=models.CASCADE, related_name='tasks')
    
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    
    assigned_to = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
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
    
    def __str__(self):
        return self.title


# Backward compatibility alias
Story = UserStory

