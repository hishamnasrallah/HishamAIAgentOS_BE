"""
Admin interface for external integrations.
"""
from django.contrib import admin
from .models import (
    GitHubIntegration,
    SlackIntegration,
    EmailNotificationSettings,
    WebhookEndpoint,
    WebhookDelivery
)


@admin.register(GitHubIntegration)
class GitHubIntegrationAdmin(admin.ModelAdmin):
    """Admin for GitHub integrations."""
    list_display = ['repository_owner', 'repository_name', 'user', 'is_active', 'last_sync_at', 'created_at']
    list_filter = ['is_active', 'auto_create_issues', 'auto_sync_prs', 'created_at']
    search_fields = ['repository_owner', 'repository_name', 'user__email', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_sync_at']
    fieldsets = (
        ('Repository', {
            'fields': ('user', 'project', 'repository_owner', 'repository_name')
        }),
        ('Authentication', {
            'fields': ('access_token', 'webhook_secret')
        }),
        ('Settings', {
            'fields': ('auto_create_issues', 'auto_sync_prs', 'sync_workflows', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'last_sync_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SlackIntegration)
class SlackIntegrationAdmin(admin.ModelAdmin):
    """Admin for Slack integrations."""
    list_display = ['workspace_name', 'channel_name', 'user', 'is_active', 'last_used_at', 'created_at']
    list_filter = ['is_active', 'notify_workflow_completion', 'notify_command_execution', 'created_at']
    search_fields = ['workspace_name', 'channel_name', 'user__email', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_used_at']
    fieldsets = (
        ('Slack Configuration', {
            'fields': ('user', 'workspace_name', 'channel_id', 'channel_name', 'bot_token')
        }),
        ('Notification Settings', {
            'fields': (
                'notify_workflow_completion',
                'notify_command_execution',
                'notify_system_alerts',
                'notify_project_updates'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'last_used_at')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmailNotificationSettings)
class EmailNotificationSettingsAdmin(admin.ModelAdmin):
    """Admin for email notification settings."""
    list_display = ['user', 'email_address', 'notify_daily_summary', 'notify_weekly_summary', 'updated_at']
    list_filter = [
        'notify_workflow_completion',
        'notify_command_execution',
        'notify_daily_summary',
        'notify_weekly_summary'
    ]
    search_fields = ['user__email', 'user__username', 'email_address']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('User', {
            'fields': ('user', 'email_address')
        }),
        ('Notification Preferences', {
            'fields': (
                'notify_workflow_completion',
                'notify_command_execution',
                'notify_system_alerts',
                'notify_project_updates',
                'notify_daily_summary',
                'notify_weekly_summary'
            )
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    """Admin for webhook endpoints."""
    list_display = ['name', 'url', 'user', 'is_active', 'success_count', 'failure_count', 'last_triggered_at']
    list_filter = [
        'is_active',
        'method',
        'trigger_on_workflow_completion',
        'trigger_on_command_execution',
        'created_at'
    ]
    search_fields = ['name', 'url', 'user__email', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_triggered_at', 'success_count', 'failure_count']
    fieldsets = (
        ('Endpoint Configuration', {
            'fields': ('user', 'name', 'url', 'method', 'secret', 'headers')
        }),
        ('Event Triggers', {
            'fields': (
                'trigger_on_workflow_completion',
                'trigger_on_command_execution',
                'trigger_on_project_update',
                'trigger_on_system_alert',
                'custom_events'
            )
        }),
        ('Settings', {
            'fields': ('retry_count', 'timeout_seconds', 'is_active')
        }),
        ('Statistics', {
            'fields': ('success_count', 'failure_count', 'last_triggered_at')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    """Admin for webhook deliveries."""
    list_display = ['endpoint', 'event_type', 'status', 'response_status', 'attempt_number', 'triggered_at']
    list_filter = ['status', 'event_type', 'triggered_at']
    search_fields = ['endpoint__name', 'endpoint__url', 'event_type', 'error_message']
    readonly_fields = ['id', 'triggered_at', 'completed_at']
    fieldsets = (
        ('Delivery', {
            'fields': ('endpoint', 'event_type', 'status', 'attempt_number')
        }),
        ('Payload', {
            'fields': ('payload',),
            'classes': ('collapse',)
        }),
        ('Response', {
            'fields': ('response_status', 'response_body', 'error_message')
        }),
        ('Timing', {
            'fields': ('triggered_at', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'triggered_at'

