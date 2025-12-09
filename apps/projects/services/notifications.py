"""
Notification delivery service for project events.

This service handles creating and delivering notifications based on project events
(mentions, comments, status changes, etc.) and project notification settings.
"""

import logging
from typing import Dict, List, Any, Optional
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.projects.models import (
    ProjectConfiguration,
    UserStory,
    Task,
    Epic,
    Sprint,
    Notification,
    Mention,
    StoryComment
)

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for creating and delivering notifications.
    
    Handles:
    - Mention notifications
    - Comment notifications
    - Status change notifications
    - Assignment notifications
    - Story creation/update notifications
    - Dependency notifications
    - Due date reminders
    - Sprint notifications
    """
    
    def __init__(self, project: Optional[Any] = None):
        """Initialize with optional project for project-specific settings."""
        self.project = project
        self.config = None
        if project:
            try:
                self.config = project.configuration
            except ProjectConfiguration.DoesNotExist:
                logger.warning(f"No configuration found for project {project.id}")
    
    def _should_send_notification(
        self,
        event_type: str,
        recipient: User
    ) -> bool:
        """
        Check if notification should be sent based on project settings and user preferences.
        
        Returns True if:
        1. Project notification settings allow it
        2. User preferences allow it
        3. Notification is enabled for the event type
        """
        # Check project-level settings
        if self.config:
            settings = self.config.notification_settings or {}
            event_setting = settings.get(event_type, {})
            
            if not event_setting.get('enabled', True):
                return False
        
        # Check user preferences (if they have opted out)
        user_prefs = recipient.notification_preferences or {}
        if not user_prefs.get('enabled', True):
            return False
        
        # Check event-specific user preferences
        event_pref = user_prefs.get(event_type, {})
        if event_pref.get('enabled') is False:
            return False
        
        return True
    
    def _get_recipients(
        self,
        event_type: str,
        story: Optional[UserStory] = None,
        comment: Optional[StoryComment] = None,
        mention: Optional[Mention] = None,
        additional_recipients: Optional[List[User]] = None
    ) -> List[User]:
        """
        Get list of recipients for a notification based on event type and project settings.
        
        Recipients can include:
        - assignee: Story assignee
        - watchers: Users watching the story (future feature)
        - mentions: Users mentioned in the story/comment
        - mentioned_user: The user who was mentioned
        - sprint_members: Members of the sprint
        """
        recipients = set()
        
        # Add additional recipients if provided
        if additional_recipients:
            recipients.update(additional_recipients)
        
        # Get project settings for this event
        if self.config:
            settings = self.config.notification_settings or {}
            event_setting = settings.get(event_type, {})
            recipient_types = event_setting.get('recipients', [])
        else:
            # Default recipients if no config
            recipient_types = ['assignee', 'watchers']
        
        if story:
            # Add assignee
            if 'assignee' in recipient_types and story.assigned_to:
                recipients.add(story.assigned_to)
            
            # Add project members (as watchers fallback)
            if 'watchers' in recipient_types:
                # For now, add project members. In future, implement actual watchers
                if story.project and story.project.members.exists():
                    recipients.update(story.project.members.all())
            
            # Add mentioned users
            if 'mentions' in recipient_types:
                mentions = Mention.objects.filter(
                    story=story,
                    is_read=False
                ).select_related('mentioned_user')
                recipients.update([m.mentioned_user for m in mentions])
        
        # Add mentioned user for mention events
        if mention and 'mentioned_user' in recipient_types:
            recipients.add(mention.mentioned_user)
        
        # Add comment author for comment events
        if comment and comment.author:
            # Don't notify the comment author about their own comment
            pass
        
        # Add sprint members for sprint events
        if 'sprint_members' in recipient_types and story and story.sprint:
            # In future, implement sprint members. For now, use project members
            if story.project and story.project.members.exists():
                recipients.update(story.project.members.all())
        
        # Remove None values and return list
        recipients = {r for r in recipients if r is not None}
        return list(recipients)
    
    @transaction.atomic
    def notify_mention(
        self,
        mention: Mention,
        story: UserStory
    ) -> Optional[Notification]:
        """Create notification for a mention."""
        if not self._should_send_notification('on_mention', mention.mentioned_user):
            return None
        
        notification = Notification.objects.create(
            recipient=mention.mentioned_user,
            notification_type='mention',
            title=f"You were mentioned in '{story.title}'",
            message=f"{mention.mentioned_by.get_full_name() or mention.mentioned_by.email} mentioned you in story '{story.title}'",
            project=story.project,
            story=story,
            mention=mention,
            metadata={
                'mentioned_by': str(mention.mentioned_by.id),
                'text_snippet': mention.text_snippet[:200] if mention.text_snippet else ''
            },
            created_by=mention.mentioned_by
        )
        
        logger.info(f"Created mention notification {notification.id} for user {mention.mentioned_user.email}")
        return notification
    
    @transaction.atomic
    def notify_comment(
        self,
        comment: StoryComment,
        story: UserStory
    ) -> List[Notification]:
        """Create notifications for a comment."""
        notifications = []
        
        # Get recipients (excluding comment author)
        recipients = self._get_recipients(
            'on_comment',
            story=story,
            comment=comment
        )
        
        # Remove comment author from recipients
        if comment.author in recipients:
            recipients.remove(comment.author)
        
        for recipient in recipients:
            if not self._should_send_notification('on_comment', recipient):
                continue
            
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type='comment',
                title=f"New comment on '{story.title}'",
                message=f"{comment.author.get_full_name() or comment.author.email} commented on story '{story.title}'",
                project=story.project,
                story=story,
                comment=comment,
                metadata={
                    'comment_id': str(comment.id),
                    'comment_preview': comment.content[:200] if comment.content else ''
                },
                created_by=comment.author
            )
            notifications.append(notification)
        
        logger.info(f"Created {len(notifications)} comment notifications for story {story.id}")
        return notifications
    
    @transaction.atomic
    def notify_status_change(
        self,
        story: UserStory,
        old_status: str,
        new_status: str,
        changed_by: User
    ) -> List[Notification]:
        """Create notifications for status change."""
        notifications = []
        
        recipients = self._get_recipients('on_status_change', story=story)
        
        for recipient in recipients:
            if not self._should_send_notification('on_status_change', recipient):
                continue
            
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type='status_change',
                title=f"Status changed for '{story.title}'",
                message=f"Story '{story.title}' status changed from {old_status} to {new_status}",
                project=story.project,
                story=story,
                metadata={
                    'old_status': old_status,
                    'new_status': new_status,
                    'changed_by': str(changed_by.id)
                },
                created_by=changed_by
            )
            notifications.append(notification)
        
        logger.info(f"Created {len(notifications)} status change notifications for story {story.id}")
        return notifications
    
    @transaction.atomic
    def notify_assignment(
        self,
        story: UserStory,
        old_assignee: Optional[User],
        new_assignee: User,
        assigned_by: User
    ) -> Optional[Notification]:
        """Create notification for assignment."""
        if not self._should_send_notification('on_assignment', new_assignee):
            return None
        
        notification = Notification.objects.create(
            recipient=new_assignee,
            notification_type='assignment',
            title=f"You were assigned to '{story.title}'",
            message=f"{assigned_by.get_full_name() or assigned_by.email} assigned you to story '{story.title}'",
            project=story.project,
            story=story,
            metadata={
                'assigned_by': str(assigned_by.id),
                'old_assignee': str(old_assignee.id) if old_assignee else None
            },
            created_by=assigned_by
        )
        
        logger.info(f"Created assignment notification {notification.id} for user {new_assignee.email}")
        return notification
    
    @transaction.atomic
    def notify_story_created(
        self,
        story: UserStory,
        created_by: User
    ) -> List[Notification]:
        """Create notifications for story creation."""
        notifications = []
        
        recipients = self._get_recipients('on_story_created', story=story)
        
        for recipient in recipients:
            if not self._should_send_notification('on_story_created', recipient):
                continue
            
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type='story_created',
                title=f"New story: '{story.title}'",
                message=f"{created_by.get_full_name() or created_by.email} created story '{story.title}'",
                project=story.project,
                story=story,
                metadata={
                    'created_by': str(created_by.id)
                },
                created_by=created_by
            )
            notifications.append(notification)
        
        logger.info(f"Created {len(notifications)} story creation notifications for story {story.id}")
        return notifications
    
    @transaction.atomic
    def notify_story_updated(
        self,
        story: UserStory,
        updated_by: User,
        changes: Optional[Dict[str, Any]] = None
    ) -> List[Notification]:
        """Create notifications for story update."""
        notifications = []
        
        recipients = self._get_recipients('on_story_updated', story=story)
        
        for recipient in recipients:
            if not self._should_send_notification('on_story_updated', recipient):
                continue
            
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type='story_updated',
                title=f"Story updated: '{story.title}'",
                message=f"{updated_by.get_full_name() or updated_by.email} updated story '{story.title}'",
                project=story.project,
                story=story,
                metadata={
                    'updated_by': str(updated_by.id),
                    'changes': changes or {}
                },
                created_by=updated_by
            )
            notifications.append(notification)
        
        logger.info(f"Created {len(notifications)} story update notifications for story {story.id}")
        return notifications
    
    @transaction.atomic
    def notify_dependency_added(
        self,
        story: UserStory,
        dependency_story: UserStory,
        created_by: User
    ) -> List[Notification]:
        """Create notifications when a dependency is added."""
        notifications = []
        
        # Notify both story owners
        recipients = set()
        if story.assigned_to:
            recipients.add(story.assigned_to)
        if dependency_story.assigned_to:
            recipients.add(dependency_story.assigned_to)
        
        for recipient in recipients:
            if not self._should_send_notification('on_dependency_added', recipient):
                continue
            
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type='dependency_added',
                title=f"Dependency added to '{story.title}'",
                message=f"A dependency was added between '{story.title}' and '{dependency_story.title}'",
                project=story.project,
                story=story,
                metadata={
                    'dependency_story_id': str(dependency_story.id),
                    'dependency_story_title': dependency_story.title
                },
                created_by=created_by
            )
            notifications.append(notification)
        
        logger.info(f"Created {len(notifications)} dependency notifications")
        return notifications
    
    @transaction.atomic
    def notify_automation_triggered(
        self,
        story: UserStory,
        rule_name: str,
        actions_applied: List[Dict[str, Any]]
    ) -> List[Notification]:
        """Create notifications when automation rules are triggered."""
        notifications = []
        
        recipients = self._get_recipients('on_automation_triggered', story=story)
        
        for recipient in recipients:
            if not self._should_send_notification('on_automation_triggered', recipient):
                continue
            
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type='automation_triggered',
                title=f"Automation triggered for '{story.title}'",
                message=f"Automation rule '{rule_name}' was triggered and applied {len(actions_applied)} actions",
                project=story.project,
                story=story,
                metadata={
                    'rule_name': rule_name,
                    'actions_applied': actions_applied
                }
            )
            notifications.append(notification)
        
        logger.info(f"Created {len(notifications)} automation notifications for story {story.id}")
        return notifications


def get_notification_service(project: Optional[Any] = None) -> NotificationService:
    """Convenience function to get a NotificationService instance."""
    return NotificationService(project)

