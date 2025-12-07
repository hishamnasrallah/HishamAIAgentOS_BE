"""
Workflows engine models for HishamOS.
"""

from django.db import models
import uuid


class Workflow(models.Model):
    """Workflow definition."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    
    # Workflow definition (YAML or JSON)
    definition = models.JSONField()
    
    # Metadata
    version = models.CharField(max_length=20, default='1.0.0')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_template = models.BooleanField(default=False)
    
    # Usage tracking
    execution_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_workflows'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workflows'
        verbose_name = 'Workflow'
        verbose_name_plural = 'Workflows'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.name


class WorkflowExecution(models.Model):
    """Workflow execution instance."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Execution state
    current_step = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Input/Output
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(null=True, blank=True)
    state = models.JSONField(default=dict)  # Current workflow state
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'workflow_executions'
        verbose_name = 'Workflow Execution'
        verbose_name_plural = 'Workflow Executions'
        indexes = [
            models.Index(fields=['workflow', '-created_at']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.workflow.name} - {self.status}'


class WorkflowStep(models.Model):
    """Individual step in a workflow execution."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    execution = models.ForeignKey(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    agent_execution = models.ForeignKey(
        'agents.AgentExecution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    step_name = models.CharField(max_length=200)
    step_order = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Input/Output
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'workflow_steps'
        verbose_name = 'Workflow Step'
        verbose_name_plural = 'Workflow Steps'
        ordering = ['execution', 'step_order']
    
    def __str__(self):
        return f'{self.step_name} - {self.status}'
