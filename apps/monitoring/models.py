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
    changes = models.JSONField(default=dict, blank=True)  # Before/after for updates
    
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
