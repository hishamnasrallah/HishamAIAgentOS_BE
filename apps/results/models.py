"""
Results and output layer models for HishamOS.
"""

from django.db import models
import uuid


class Result(models.Model):
    """Standardized output from agent/workflow executions."""
    
    TYPE_CHOICES = [
        ('agent', 'Agent Result'),
        ('workflow', 'Workflow Result'),
    ]
    
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('markdown', 'Markdown'),
        ('text', 'Plain Text'),
        ('code', 'Code'),
        ('mixed', 'Mixed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Source
    result_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    agent_execution = models.ForeignKey(
        'agents.AgentExecution',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='results'
    )
    workflow_execution = models.ForeignKey(
        'workflows.WorkflowExecution',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='results'
    )
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Content
    title = models.CharField(max_length=300)
    content = models.TextField()
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='text')
    metadata = models.JSONField(default=dict, blank=True)
    
    # Analysis
    critique = models.TextField(blank=True)  # Self-critique from agent
    action_items = models.JSONField(default=list, blank=True)
    
    # Quality metrics
    quality_score = models.FloatField(null=True, blank=True)  # 0-100
    confidence_score = models.FloatField(null=True, blank=True)  # 0-100
    
    # Versioning
    version = models.IntegerField(default=1)
    parent_result = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revisions'
    )
    
    # Tags and categorization
    tags = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'results'
        verbose_name = 'Result'
        verbose_name_plural = 'Results'
        indexes = [
            models.Index(fields=['result_type', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class ResultFeedback(models.Model):
    """User feedback on results."""
    
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True
    )
    
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    
    # Specific feedback
    is_accurate = models.BooleanField(null=True, blank=True)
    is_helpful = models.BooleanField(null=True, blank=True)
    is_complete = models.BooleanField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'result_feedback'
        verbose_name = 'Result Feedback'
        verbose_name_plural = 'Result Feedback'
        unique_together = [['result', 'user']]
    
    def __str__(self):
        return f'{self.result.title} - Rating: {self.rating}'
