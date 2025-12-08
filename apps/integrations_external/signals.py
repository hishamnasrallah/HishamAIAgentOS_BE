"""
Signals for external integrations.

Triggers notifications when workflows complete or commands execute.
"""
import logging
from typing import Optional
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from apps.workflows.models import WorkflowExecution
from .services import (
    SlackService,
    EmailService,
    WebhookService
)
from .models import (
    SlackIntegration,
    EmailNotificationSettings,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=WorkflowExecution)
def on_workflow_execution_completed(sender, instance, created, **kwargs):
    """Trigger notifications when workflow execution completes or fails."""
    # Only trigger on status changes to completed/failed
    if instance.status not in ['completed', 'failed']:
        return
    
    if not instance.user:
        return
    
    user = instance.user
    
    # Trigger Slack notifications
    try:
        slack_integrations = SlackIntegration.objects.filter(
            user=user,
            is_active=True,
            notify_workflow_completion=True
        )
        for integration in slack_integrations:
            try:
                service = SlackService(integration)
                service.send_workflow_notification(
                    workflow_name=instance.workflow.name,
                    status=instance.status,
                    execution_id=str(instance.id)
                )
            except Exception as e:
                logger.error(f"Failed to send Slack notification: {e}")
    except Exception as e:
        logger.error(f"Error processing Slack notifications: {e}")
    
    # Trigger email notifications
    try:
        email_settings = EmailNotificationSettings.objects.filter(
            user=user,
            notify_workflow_completion=True
        ).first()
        if email_settings:
            try:
                service = EmailService(email_settings)
                service.send_workflow_notification(
                    workflow_name=instance.workflow.name,
                    status=instance.status,
                    execution_id=str(instance.id),
                    details={
                        'workflow_id': str(instance.workflow.id),
                        'error_message': instance.error_message if instance.status == 'failed' else None,
                    }
                )
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")
    except Exception as e:
        logger.error(f"Error processing email notifications: {e}")
    
    # Trigger webhooks
    try:
        WebhookService.trigger_for_event(
            event_type='workflow.completed',
            payload={
                'workflow_id': str(instance.workflow.id),
                'workflow_name': instance.workflow.name,
                'status': instance.status,
                'execution_id': str(instance.id),
                'user_id': str(user.id),
                'error_message': instance.error_message if instance.status == 'failed' else None,
            },
            user_id=str(user.id)
        )
    except Exception as e:
        logger.error(f"Error triggering webhooks: {e}")


def trigger_command_execution_notifications(
    command_id: str,
    command_name: str,
    status: str,
    user,
    result_summary: Optional[str] = None,
    execution_time: Optional[float] = None,
    cost: Optional[float] = None,
    error: Optional[str] = None
):
    """
    Trigger notifications for command execution.
    
    This function is called directly from the command execution view
    after a command completes (success or failure).
    """
    if not user or not user.is_authenticated:
        return
    
    # Prepare result summary
    if not result_summary:
        if status == 'success':
            result_summary = f"Command executed successfully"
            if execution_time:
                result_summary += f" in {execution_time:.2f}s"
            if cost:
                result_summary += f" (cost: ${cost:.4f})"
        else:
            result_summary = f"Command execution failed"
            if error:
                result_summary += f": {error}"
    
    # Trigger Slack notifications
    try:
        slack_integrations = SlackIntegration.objects.filter(
            user=user,
            is_active=True,
            notify_command_execution=True
        )
        for integration in slack_integrations:
            try:
                service = SlackService(integration)
                service.send_command_notification(
                    command_name=command_name,
                    status=status,
                    result_summary=result_summary
                )
            except Exception as e:
                logger.error(f"Failed to send Slack notification for command {command_id}: {e}")
    except Exception as e:
        logger.error(f"Error processing Slack notifications for command {command_id}: {e}")
    
    # Trigger email notifications
    try:
        email_settings = EmailNotificationSettings.objects.filter(
            user=user,
            notify_command_execution=True
        ).first()
        if email_settings:
            try:
                service = EmailService(email_settings)
                service.send_command_notification(
                    command_name=command_name,
                    status=status,
                    result_summary=result_summary
                )
            except Exception as e:
                logger.error(f"Failed to send email notification for command {command_id}: {e}")
    except Exception as e:
        logger.error(f"Error processing email notifications for command {command_id}: {e}")
    
    # Trigger webhooks
    try:
        WebhookService.trigger_for_event(
            event_type='command.executed',
            payload={
                'command_id': command_id,
                'command_name': command_name,
                'status': status,
                'user_id': str(user.id),
                'result_summary': result_summary,
                'execution_time': execution_time,
                'cost': cost,
                'error': error,
                'timestamp': timezone.now().isoformat(),
            },
            user_id=str(user.id)
        )
    except Exception as e:
        logger.error(f"Error triggering webhooks for command {command_id}: {e}")

