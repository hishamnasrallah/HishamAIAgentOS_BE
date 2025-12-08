"""
Monitoring and metrics models for HishamOS.
"""

from django.db import models
import uuid


class SystemMetric(models.Model):
    """System-wide metrics."""
    
    METRIC_TYPE_CHOICES = [
        ('cpu', 'CPU Usage'),
        ('memory', 'Memory Usage'),
        ('disk', 'Disk Usage'),
        ('api_latency', 'API Latency'),
        ('agent_queue', 'Agent Queue Size'),
        ('error_rate', 'Error Rate'),
        ('cost', 'Cost'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPE_CHOICES)
    value = models.FloatField()
    unit = models.CharField(max_length=20)  # %, MB, ms, USD, etc.
    
    metadata = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'system_metrics'
        verbose_name = 'System Metric'
        verbose_name_plural = 'System Metrics'
        indexes = [
            models.Index(fields=['metric_type', '-timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.metric_type}: {self.value}{self.unit}'


class HealthCheck(models.Model):
    """System health checks."""
    
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('unhealthy', 'Unhealthy'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.CharField(max_length=100)  # database, redis, celery, ai_platform, etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    response_time = models.FloatField(default=0)  # in milliseconds
    message = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'health_checks'
        verbose_name = 'Health Check'
        verbose_name_plural = 'Health Checks'
        indexes = [
            models.Index(fields=['component', '-timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.component}: {self.status}'


class AuditLog(models.Model):
    """Audit trail for important actions."""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('execute', 'Execute'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('read', 'Read'),  # For GDPR data access logging
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=100)  # agent, workflow, project, etc.
    resource_id = models.CharField(max_length=255)
    
    description = models.TextField()
    changes = models.JSONField(default=dict, blank=True)  # Field-by-field changes: {"field": {"before": "old", "after": "new"}}
    old_values = models.JSONField(default=dict, blank=True, help_text="Complete state before the change")
    new_values = models.JSONField(default=dict, blank=True, help_text="Complete state after the change")
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['resource_type', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.action} {self.resource_type} by {self.user}'


class AuditConfiguration(models.Model):
    """
    Configurable audit logging rules.
    Allows fine-grained control over what gets audited.
    """
    
    CONFIGURATION_TYPE_CHOICES = [
        ('default', 'Default'),
        ('gdpr', 'GDPR Compliance'),
        ('security', 'Security & Access'),
        ('compliance', 'General Compliance'),
        ('financial', 'Financial Transactions'),
        ('data_access', 'Data Access'),
        ('user_management', 'User Management'),
        ('system_changes', 'System Configuration'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    configuration_type = models.CharField(max_length=50, choices=CONFIGURATION_TYPE_CHOICES, default='custom')
    
    # Enable/disable this configuration
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Default configuration applied to all actions")
    
    # What to audit - Actions
    audit_actions = models.JSONField(
        default=list,
        help_text="List of actions to audit: ['create', 'update', 'delete', 'execute', 'login', 'logout', 'read']"
    )
    
    # What to audit - Resource Types
    audit_resource_types = models.JSONField(
        default=list,
        help_text="List of resource types to audit: ['agent', 'workflow', 'project', 'user', 'api', etc.]"
    )
    
    # What to exclude - Actions
    exclude_actions = models.JSONField(
        default=list,
        blank=True,
        help_text="Actions to exclude from auditing (takes precedence over audit_actions)"
    )
    
    # What to exclude - Resource Types
    exclude_resource_types = models.JSONField(
        default=list,
        blank=True,
        help_text="Resource types to exclude from auditing (takes precedence over audit_resource_types)"
    )
    
    # What to exclude - Specific Resources
    exclude_resources = models.JSONField(
        default=list,
        blank=True,
        help_text="Specific resources to exclude: [{'resource_type': 'agent', 'resource_id': 'xxx'}]"
    )
    
    # User-based filtering
    audit_all_users = models.BooleanField(
        default=True,
        help_text="If True, audit all users. If False, only audit users in audit_users list"
    )
    audit_users = models.JSONField(
        default=list,
        blank=True,
        help_text="List of user IDs to audit (only if audit_all_users=False)"
    )
    exclude_users = models.JSONField(
        default=list,
        blank=True,
        help_text="List of user IDs to exclude from auditing"
    )
    
    # IP-based filtering
    audit_all_ips = models.BooleanField(default=True)
    audit_ips = models.JSONField(
        default=list,
        blank=True,
        help_text="List of IP addresses to audit (only if audit_all_ips=False)"
    )
    exclude_ips = models.JSONField(
        default=list,
        blank=True,
        help_text="List of IP addresses to exclude from auditing"
    )
    
    # Advanced filters
    include_changes = models.BooleanField(
        default=True,
        help_text="Include before/after changes in audit logs"
    )
    include_ip_address = models.BooleanField(default=True)
    include_user_agent = models.BooleanField(default=True)
    
    # Metadata
    priority = models.IntegerField(
        default=0,
        help_text="Priority order (higher = evaluated first). Default configs have priority 0."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_audit_configurations'
    )
    
    class Meta:
        db_table = 'audit_configurations'
        verbose_name = 'Audit Configuration'
        verbose_name_plural = 'Audit Configurations'
        indexes = [
            models.Index(fields=['is_active', 'priority']),
            models.Index(fields=['configuration_type']),
        ]
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f'{self.name} ({self.configuration_type})'
    
    def should_audit(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user=None,
        ip_address: str = None
    ) -> bool:
        """
        Check if an action should be audited based on this configuration.
        
        Returns:
            True if action should be audited, False otherwise
        """
        # Check if configuration is active
        if not self.is_active:
            return False
        
        # Check actions
        if self.exclude_actions and action in self.exclude_actions:
            return False
        if self.audit_actions and action not in self.audit_actions:
            return False
        
        # Check resource types
        if self.exclude_resource_types and resource_type in self.exclude_resource_types:
            return False
        if self.audit_resource_types and resource_type not in self.audit_resource_types:
            return False
        
        # Check specific resources
        if self.exclude_resources:
            for excluded in self.exclude_resources:
                if (excluded.get('resource_type') == resource_type and 
                    excluded.get('resource_id') == resource_id):
                    return False
        
        # Check users
        if user:
            user_id = str(user.id) if hasattr(user, 'id') else str(user)
            if self.exclude_users and user_id in self.exclude_users:
                return False
            if not self.audit_all_users:
                if not self.audit_users or user_id not in self.audit_users:
                    return False
        
        # Check IP addresses
        if ip_address:
            if self.exclude_ips and ip_address in self.exclude_ips:
                return False
            if not self.audit_all_ips:
                if not self.audit_ips or ip_address not in self.audit_ips:
                    return False
        
        return True
