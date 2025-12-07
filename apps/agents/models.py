"""
Agent management models for HishamOS.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Agent(models.Model):
    """AI Agent definition and configuration."""
    
    CAPABILITY_CHOICES = [
        ('CODE_GENERATION', 'Code Generation'),
        ('CODE_REVIEW', 'Code Review'),
        ('REQUIREMENTS_ANALYSIS', 'Requirements Analysis'),
        ('USER_STORY_GENERATION', 'User Story Generation'),
        ('PROJECT_MANAGEMENT', 'Project Management'),
        ('TESTING', 'Testing'),
        ('DOCUMENTATION', 'Documentation'),
        ('DEVOPS', 'DevOps'),
        ('LEGAL_REVIEW', 'Legal Review'),
        ('HR_MANAGEMENT', 'HR Management'),
        ('FINANCE_ANALYSIS', 'Finance Analysis'),
        ('UX_DESIGN', 'UX Design'),
        ('RESEARCH', 'Research'),
        ('BUG_TRIAGE', 'Bug Triage'),
        ('RELEASE_MANAGEMENT', 'Release Management'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Capabilities - using JSONField for SQLite compatibility
    capabilities = models.JSONField(default=list, blank=True)
    
    # System prompt
    system_prompt = models.TextField()
    
    # Model configuration
    preferred_platform = models.CharField(max_length=50, default='openai')
    fallback_platforms = models.JSONField(default=list, blank=True)
    model_name = models.CharField(max_length=100, default='gpt-4-turbo')
    temperature = models.FloatField(
        default=0.3,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)]
    )
    max_tokens = models.IntegerField(default=4000)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    version = models.CharField(max_length=20, default='1.0.0')
    
    # Metrics
    total_invocations = models.IntegerField(default=0)
    total_tokens_used = models.BigIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    average_response_time = models.FloatField(default=0)  # in seconds
    success_rate = models.FloatField(default=0)  # percentage
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_invoked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'agents'
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'
        indexes = [
            models.Index(fields=['agent_id']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.agent_id})'


class AgentExecution(models.Model):
    """Record of agent execution."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='executions')
    user = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    
    # Input
    input_data = models.JSONField()
    context = models.JSONField(default=dict, blank=True)
    
    # Output
    output_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Execution details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    platform_used = models.CharField(max_length=50)
    model_used = models.CharField(max_length=100)
    
    # Metrics
    tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    execution_time = models.FloatField(default=0)  # in seconds
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'agent_executions'
        verbose_name = 'Agent Execution'
        verbose_name_plural = 'Agent Executions'
        indexes = [
            models.Index(fields=['agent', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.agent.name} - {self.status}'
