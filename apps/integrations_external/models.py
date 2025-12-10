"""
Models for external integrations.
"""
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class GitHubIntegration(models.Model):
    """GitHub integration configuration for a user or project."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='github_integrations',
        null=True,
        blank=True
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='github_integrations',
        null=True,
        blank=True
    )
    
    # GitHub configuration
    repository_owner = models.CharField(max_length=200)
    repository_name = models.CharField(max_length=200)
    access_token = models.CharField(max_length=500)  # Encrypted in future
    webhook_secret = models.CharField(max_length=500, blank=True)
    
    # Integration settings
    auto_create_issues = models.BooleanField(default=False)
    auto_sync_prs = models.BooleanField(default=False)
    sync_workflows = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_github_integrations',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_github_integrations',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'github_integrations'
        verbose_name = 'GitHub Integration'
        verbose_name_plural = 'GitHub Integrations'
        unique_together = [['repository_owner', 'repository_name', 'user']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['repository_owner', 'repository_name']),
        ]
    
    def __str__(self):
        return f"{self.repository_owner}/{self.repository_name}"


class SlackIntegration(models.Model):
    """Slack integration configuration."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='slack_integrations'
    )
    
    # Slack configuration
    workspace_name = models.CharField(max_length=200)
    channel_id = models.CharField(max_length=200)
    channel_name = models.CharField(max_length=200)
    bot_token = models.CharField(max_length=500)  # Encrypted in future
    
    # Notification settings
    notify_workflow_completion = models.BooleanField(default=True)
    notify_command_execution = models.BooleanField(default=False)
    notify_system_alerts = models.BooleanField(default=True)
    notify_project_updates = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_slack_integrations',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_slack_integrations',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'slack_integrations'
        verbose_name = 'Slack Integration'
        verbose_name_plural = 'Slack Integrations'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['workspace_name', 'channel_id']),
        ]
    
    def __str__(self):
        return f"{self.workspace_name} - {self.channel_name}"


class EmailNotificationSettings(models.Model):
    """Email notification settings for users."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='email_notification_settings'
    )
    
    # Notification preferences
    notify_workflow_completion = models.BooleanField(default=True)
    notify_command_execution = models.BooleanField(default=False)
    notify_system_alerts = models.BooleanField(default=True)
    notify_project_updates = models.BooleanField(default=False)
    notify_daily_summary = models.BooleanField(default=False)
    notify_weekly_summary = models.BooleanField(default=True)
    
    # Email settings
    email_address = models.EmailField()
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_email_notification_settings',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_email_notification_settings',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'email_notification_settings'
        verbose_name = 'Email Notification Settings'
        verbose_name_plural = 'Email Notification Settings'
    
    def __str__(self):
        return f"Email settings for {self.user.email}"


class WebhookEndpoint(models.Model):
    """Generic webhook endpoint configuration."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='webhook_endpoints'
    )
    
    # Webhook configuration
    name = models.CharField(max_length=200)
    url = models.URLField()
    secret = models.CharField(max_length=500, blank=True)  # For signature verification
    
    # Event triggers
    trigger_on_workflow_completion = models.BooleanField(default=False)
    trigger_on_command_execution = models.BooleanField(default=False)
    trigger_on_project_update = models.BooleanField(default=False)
    trigger_on_system_alert = models.BooleanField(default=False)
    
    # Custom events (JSON array)
    custom_events = models.JSONField(default=list, blank=True)
    
    # Settings
    method = models.CharField(max_length=10, default='POST', choices=[
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
    ])
    headers = models.JSONField(default=dict, blank=True)
    retry_count = models.IntegerField(default=3)
    timeout_seconds = models.IntegerField(default=30)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_webhook_endpoints',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_webhook_endpoints',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'webhook_endpoints'
        verbose_name = 'Webhook Endpoint'
        verbose_name_plural = 'Webhook Endpoints'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_active', 'trigger_on_workflow_completion']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.url}"


class WebhookDelivery(models.Model):
    """Record of webhook delivery attempts."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )
    
    # Delivery details
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Response details
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_webhook_deliveries',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_webhook_deliveries',
        verbose_name='Updated By'
    )
    
    # Timing
    attempt_number = models.IntegerField(default=1)
    triggered_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'webhook_deliveries'
        verbose_name = 'Webhook Delivery'
        verbose_name_plural = 'Webhook Deliveries'
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['endpoint', '-triggered_at']),
            models.Index(fields=['status', '-triggered_at']),
        ]
    
    def __str__(self):
        return f"{self.endpoint.name} - {self.event_type} - {self.status}"


class JiraIntegration(models.Model):
    """Jira integration configuration for a user or project."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='jira_integrations',
        null=True,
        blank=True
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='jira_integrations',
        null=True,
        blank=True
    )
    
    # Jira configuration
    jira_url = models.URLField(help_text="Jira instance URL (e.g., https://yourcompany.atlassian.net)")
    username = models.CharField(max_length=200, help_text="Jira username or email")
    api_token = models.CharField(max_length=500, help_text="Jira API token (encrypted in future)")
    project_key = models.CharField(max_length=50, help_text="Jira project key (e.g., PROJ)")
    
    # Integration settings
    auto_create_issues = models.BooleanField(default=False, help_text="Automatically create Jira issues from stories")
    auto_sync_status = models.BooleanField(default=False, help_text="Sync status changes between systems")
    sync_comments = models.BooleanField(default=True, help_text="Sync comments between systems")
    
    # Field mapping
    issue_type = models.CharField(max_length=50, default='Story', help_text="Default Jira issue type")
    priority_mapping = models.JSONField(
        default=dict,
        blank=True,
        help_text="Map story priorities to Jira priorities"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_jira_integrations',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_jira_integrations',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        db_table = 'jira_integrations'
        verbose_name = 'Jira Integration'
        verbose_name_plural = 'Jira Integrations'
        unique_together = [['jira_url', 'project_key', 'user']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['jira_url', 'project_key']),
        ]
    
    def __str__(self):
        return f"{self.jira_url} - {self.project_key}"

