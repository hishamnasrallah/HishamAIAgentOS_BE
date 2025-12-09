"""
Command library models for HishamOS.
"""

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class CommandCategory(models.Model):
    """Categories for organizing commands."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_command_categories',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_command_categories',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'command_categories'
        verbose_name = 'Command Category'
        verbose_name_plural = 'Command Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class CommandTemplate(models.Model):
    """Template for AI agent commands."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        CommandCategory,
        on_delete=models.CASCADE,
        related_name='commands'
    )
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    
    # Template content
    template = models.TextField(help_text="Template with parameter placeholders using {{param_name}} syntax")
    
    # Parameters definition
    parameters = models.JSONField(
        default=list,
        help_text="List of parameter definitions with name, type, required, description, example"
    )
    
    # Enhanced usability fields
    example_usage = models.JSONField(
        default=dict,
        blank=True,
        help_text="Example input parameters and expected output preview"
    )
    
    # Agent integration
    recommended_agent = models.ForeignKey(
        'agents.Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recommended_commands',
        help_text="Agent that works best with this command"
    )
    
    required_capabilities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of required agent capabilities (e.g., CODE_GENERATION, LEGAL_REVIEW)"
    )
    
    # Performance metrics
    estimated_cost = models.FloatField(default=0.0, help_text="Estimated cost per execution")
    estimated_duration = models.IntegerField(default=0, help_text="Estimated duration in seconds")
    
    # Execution statistics (updated automatically via signals)
    success_rate = models.FloatField(default=100.0, help_text="Percentage of successful executions (0-100)")
    avg_execution_time = models.FloatField(default=0.0, help_text="Average execution time in seconds")
    total_successes = models.IntegerField(default=0, help_text="Total number of successful executions")
    total_failures = models.IntegerField(default=0, help_text="Total number of failed executions")
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    version = models.CharField(max_length=20, default='1.0.0')
    usage_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_command_templates',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_command_templates',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'command_templates'
        verbose_name = 'Command Template'
        verbose_name_plural = 'Command Templates'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', '-usage_count']),
            models.Index(fields=['-success_rate', '-usage_count'], name='cmd_tmpl_success_idx'),
            models.Index(fields=['category', 'is_active', '-success_rate'], name='cmd_cat_act_success_idx'),
        ]
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name
    
    def recalculate_statistics(self):
        """Recalculate execution statistics from executions."""
        executions = self.executions.all()
        total = executions.count()
        
        if total == 0:
            self.success_rate = 100.0
            self.avg_execution_time = 0.0
            self.total_successes = 0
            self.total_failures = 0
        else:
            successful = executions.filter(status='completed').count()
            failed = executions.filter(status='failed').count()
            
            self.total_successes = successful
            self.total_failures = failed
            self.success_rate = (successful / total) * 100.0 if total > 0 else 100.0
            
            # Calculate average execution time from completed executions
            completed_executions = executions.filter(status='completed')
            if completed_executions.exists():
                total_time_ms = sum(e.execution_time_ms for e in completed_executions)
                self.avg_execution_time = (total_time_ms / completed_executions.count()) / 1000.0  # Convert to seconds
            else:
                self.avg_execution_time = 0.0
        
        # Update usage_count
        self.usage_count = total
        
        # Save without triggering signals to avoid recursion
        CommandTemplate.objects.filter(id=self.id).update(
            success_rate=self.success_rate,
            avg_execution_time=self.avg_execution_time,
            total_successes=self.total_successes,
            total_failures=self.total_failures,
            usage_count=self.usage_count
        )


class CommandExecution(models.Model):
    """Track command template executions."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    command = models.ForeignKey(
        CommandTemplate,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='command_executions'
    )
    
    # Execution details
    input_parameters = models.JSONField(default=dict, help_text="Input parameters used")
    rendered_template = models.TextField(blank=True, help_text="Rendered command template")
    output = models.TextField(blank=True, help_text="Command output/result")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Performance metrics
    execution_time_ms = models.IntegerField(default=0, help_text="Execution time in milliseconds")
    tokens_used = models.IntegerField(default=0)
    cost = models.FloatField(default=0.0)
    
    # Agent execution link (if executed via agent)
    agent_execution = models.ForeignKey(
        'agents.AgentExecution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='command_executions'
    )
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_command_executions',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_command_executions',
        verbose_name='Updated By'
    )
    
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'command_executions'
        verbose_name = 'Command Execution'
        verbose_name_plural = 'Command Executions'
        indexes = [
            models.Index(fields=['command', '-started_at']),
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['started_at']),
        ]
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.command.name} - {self.status}"
