"""
Serializers for external integrations.
"""
from rest_framework import serializers
from .models import (
    GitHubIntegration,
    SlackIntegration,
    JiraIntegration,
    EmailNotificationSettings,
    WebhookEndpoint,
    WebhookDelivery
)


class GitHubIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for GitHub integration."""
    
    class Meta:
        model = GitHubIntegration
        fields = [
            'id',
            'user',
            'project',
            'repository_owner',
            'repository_name',
            'access_token',
            'webhook_secret',
            'auto_create_issues',
            'auto_sync_prs',
            'sync_workflows',
            'is_active',
            'last_sync_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_sync_at']
        extra_kwargs = {
            'access_token': {'write_only': True},
            'webhook_secret': {'write_only': True},
        }


class SlackIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Slack integration."""
    
    class Meta:
        model = SlackIntegration
        fields = [
            'id',
            'user',
            'workspace_name',
            'channel_id',
            'channel_name',
            'bot_token',
            'notify_workflow_completion',
            'notify_command_execution',
            'notify_system_alerts',
            'notify_project_updates',
            'is_active',
            'last_used_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_used_at']
        extra_kwargs = {
            'bot_token': {'write_only': True},
        }


class JiraIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for Jira integration."""
    
    class Meta:
        model = JiraIntegration
        fields = [
            'id',
            'user',
            'project',
            'jira_url',
            'username',
            'api_token',
            'project_key',
            'auto_create_issues',
            'auto_sync_status',
            'sync_comments',
            'issue_type',
            'priority_mapping',
            'is_active',
            'last_sync_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_sync_at']
        extra_kwargs = {
            'api_token': {'write_only': True},
        }


class EmailNotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for email notification settings."""
    
    class Meta:
        model = EmailNotificationSettings
        fields = [
            'id',
            'user',
            'email_address',
            'notify_workflow_completion',
            'notify_command_execution',
            'notify_system_alerts',
            'notify_project_updates',
            'notify_daily_summary',
            'notify_weekly_summary',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WebhookEndpointSerializer(serializers.ModelSerializer):
    """Serializer for webhook endpoint."""
    
    class Meta:
        model = WebhookEndpoint
        fields = [
            'id',
            'user',
            'name',
            'url',
            'secret',
            'trigger_on_workflow_completion',
            'trigger_on_command_execution',
            'trigger_on_project_update',
            'trigger_on_system_alert',
            'custom_events',
            'method',
            'headers',
            'retry_count',
            'timeout_seconds',
            'is_active',
            'last_triggered_at',
            'success_count',
            'failure_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'last_triggered_at',
            'success_count',
            'failure_count',
        ]
        extra_kwargs = {
            'secret': {'write_only': True},
        }


class WebhookDeliverySerializer(serializers.ModelSerializer):
    """Serializer for webhook delivery."""
    
    endpoint_name = serializers.CharField(source='endpoint.name', read_only=True)
    endpoint_url = serializers.URLField(source='endpoint.url', read_only=True)
    
    class Meta:
        model = WebhookDelivery
        fields = [
            'id',
            'endpoint',
            'endpoint_name',
            'endpoint_url',
            'event_type',
            'payload',
            'status',
            'response_status',
            'response_body',
            'error_message',
            'attempt_number',
            'triggered_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'endpoint_name',
            'endpoint_url',
            'triggered_at',
            'completed_at',
        ]

