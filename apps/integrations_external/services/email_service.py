"""
Email notification service.
"""
import logging
from typing import Dict, Optional, List
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from ..models import EmailNotificationSettings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self, settings_obj: EmailNotificationSettings):
        """Initialize with email notification settings."""
        self.settings = settings_obj
        self.email_address = settings_obj.email_address
    
    def send_email(
        self,
        subject: str,
        message: str,
        html_message: Optional[str] = None,
        recipient_list: Optional[List[str]] = None
    ) -> bool:
        """Send an email."""
        recipients = recipient_list or [self.email_address]
        
        try:
            if html_message:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=recipients,
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
            else:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipients,
                    fail_silently=False,
                )
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_workflow_notification(
        self,
        workflow_name: str,
        status: str,
        execution_id: str,
        details: Optional[Dict] = None
    ) -> bool:
        """Send a workflow completion notification."""
        if not self.settings.notify_workflow_completion:
            return False
        
        subject = f"Workflow {workflow_name} - {status.title()}"
        message = f"Workflow '{workflow_name}' has {status}.\n\nExecution ID: {execution_id}"
        
        if details:
            message += f"\n\nDetails:\n{details}"
        
        return self.send_email(subject, message)
    
    def send_command_notification(
        self,
        command_name: str,
        status: str,
        result_summary: Optional[str] = None
    ) -> bool:
        """Send a command execution notification."""
        if not self.settings.notify_command_execution:
            return False
        
        subject = f"Command {command_name} - {status.title()}"
        message = f"Command '{command_name}' execution {status}."
        
        if result_summary:
            message += f"\n\nResult: {result_summary}"
        
        return self.send_email(subject, message)
    
    def send_system_alert(self, alert_type: str, message: str) -> bool:
        """Send a system alert."""
        if not self.settings.notify_system_alerts:
            return False
        
        subject = f"System Alert: {alert_type}"
        return self.send_email(subject, message)
    
    def send_daily_summary(self, summary_data: Dict) -> bool:
        """Send a daily summary email."""
        if not self.settings.notify_daily_summary:
            return False
        
        subject = "HishamOS Daily Summary"
        message = f"Daily Summary for {timezone.now().strftime('%Y-%m-%d')}\n\n"
        message += f"Workflows executed: {summary_data.get('workflows', 0)}\n"
        message += f"Commands executed: {summary_data.get('commands', 0)}\n"
        message += f"Agents invoked: {summary_data.get('agents', 0)}\n"
        
        return self.send_email(subject, message)
    
    def send_weekly_summary(self, summary_data: Dict) -> bool:
        """Send a weekly summary email."""
        if not self.settings.notify_weekly_summary:
            return False
        
        subject = "HishamOS Weekly Summary"
        message = f"Weekly Summary\n\n"
        message += f"Total workflows: {summary_data.get('workflows', 0)}\n"
        message += f"Total commands: {summary_data.get('commands', 0)}\n"
        message += f"Total agents: {summary_data.get('agents', 0)}\n"
        message += f"Success rate: {summary_data.get('success_rate', 0)}%\n"
        
        return self.send_email(subject, message)

