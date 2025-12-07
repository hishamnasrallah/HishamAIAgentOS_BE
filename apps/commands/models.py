"""
Command library models for HishamOS.
"""

from django.db import models
import uuid


class CommandCategory(models.Model):
    """Categories for organizing commands."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=0.0,
        help_text="Estimated cost in USD to execute this command"
    )
    
    avg_execution_time = models.FloatField(
        default=0.0,
        help_text="Average execution time in seconds"
    )
    
    success_rate = models.FloatField(
        default=100.0,
        help_text="Percentage of successful executions (0-100)"
    )
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    version = models.CharField(max_length=20, default='1.0.0')
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    total_successes = models.IntegerField(default=0)
    total_failures = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'command_templates'
        verbose_name = 'Command Template'
        verbose_name_plural = 'Command Templates'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', '-usage_count']),
            models.Index(fields=['-success_rate', '-usage_count']),
            models.Index(fields=['is_active', 'category']),
        ]
    
    def __str__(self):
        return self.name
    
    def update_metrics(self, success: bool, execution_time: float, cost: float):
        """Update command metrics after execution."""
        self.usage_count += 1
        if success:
            self.total_successes += 1
        else:
            self.total_failures += 1
        
        # Update success rate
        total_executions = self.total_successes + self.total_failures
        if total_executions > 0:
            self.success_rate = (self.total_successes / total_executions) * 100
        
        # Update average execution time (exponential moving average)
        if self.avg_execution_time == 0:
            self.avg_execution_time = execution_time
        else:
            alpha = 0.2  # Weight for new value
            self.avg_execution_time = (alpha * execution_time) + ((1 - alpha) * self.avg_execution_time)
        
        # Update estimated cost (exponential moving average)
        if self.estimated_cost == 0:
            self.estimated_cost = cost
        else:
            self.estimated_cost = (alpha * cost) + ((1 - alpha) * float(self.estimated_cost))
        
        self.save()
