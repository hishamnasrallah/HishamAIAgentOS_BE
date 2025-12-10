"""
Email delivery service for notifications.
Handles sending email notifications for project events.
"""

import logging
from typing import Optional, Dict, Any
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model

from apps.projects.models import Notification

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""
    
    @staticmethod
    def send_notification_email(notification: Notification) -> bool:
        """
        Send email notification.
        
        Args:
            notification: Notification instance to send
        
        Returns:
            True if email sent successfully, False otherwise
        """
        if not notification.recipient or not notification.recipient.email:
            logger.warning(f"Cannot send email: recipient or email missing for notification {notification.id}")
            return False
        
        try:
            # Get email template context
            context = EmailService._get_email_context(notification)
            
            # Render email template
            html_content = EmailService._render_email_template(notification, context)
            text_content = strip_tags(html_content)
            
            # Create email
            subject = EmailService._get_email_subject(notification)
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [notification.recipient.email]
            
            # Send email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email,
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            # Update notification
            notification.email_sent = True
            from django.utils import timezone
            notification.email_sent_at = timezone.now()
            notification.save(update_fields=['email_sent', 'email_sent_at'])
            
            logger.info(f"Email sent successfully for notification {notification.id} to {notification.recipient.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email for notification {notification.id}: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def _get_email_context(notification: Notification) -> Dict[str, Any]:
        """Get context for email template."""
        context = {
            'notification': notification,
            'recipient': notification.recipient,
            'project': notification.project,
            'story': notification.story,
            'task': notification.task,
            'bug': notification.bug,
            'issue': notification.issue,
            'epic': notification.epic,
            'site_name': getattr(settings, 'SITE_NAME', 'HishamOS'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:3000'),
        }
        
        # Add metadata
        if notification.metadata:
            context.update(notification.metadata)
        
        return context
    
    @staticmethod
    def _render_email_template(notification: Notification, context: Dict[str, Any]) -> str:
        """Render email template."""
        # Determine template based on notification type
        template_name = f'projects/emails/{notification.notification_type}.html'
        
        try:
            return render_to_string(template_name, context)
        except Exception:
            # Fallback to default template
            logger.warning(f"Template {template_name} not found, using default template")
            return render_to_string('projects/emails/default.html', context)
    
    @staticmethod
    def _get_email_subject(notification: Notification) -> str:
        """Get email subject based on notification type."""
        subject_prefix = getattr(settings, 'EMAIL_SUBJECT_PREFIX', '[HishamOS]')
        
        # Use notification title if available
        if notification.title:
            return f"{subject_prefix} {notification.title}"
        
        # Generate subject based on type
        type_subjects = {
            'mention': f"{subject_prefix} You were mentioned",
            'comment': f"{subject_prefix} New comment",
            'status_change': f"{subject_prefix} Status changed",
            'assignment': f"{subject_prefix} You were assigned",
            'story_created': f"{subject_prefix} New story created",
            'story_updated': f"{subject_prefix} Story updated",
            'due_date': f"{subject_prefix} Due date approaching",
            'epic_owner_assignment': f"{subject_prefix} You were assigned as epic owner",
        }
        
        return type_subjects.get(notification.notification_type, f"{subject_prefix} Notification")
    
    @staticmethod
    def send_bulk_emails(notifications: list[Notification]) -> Dict[str, int]:
        """
        Send multiple email notifications.
        
        Args:
            notifications: List of Notification instances
        
        Returns:
            Dict with 'sent' and 'failed' counts
        """
        results = {'sent': 0, 'failed': 0}
        
        for notification in notifications:
            if EmailService.send_notification_email(notification):
                results['sent'] += 1
            else:
                results['failed'] += 1
        
        return results

