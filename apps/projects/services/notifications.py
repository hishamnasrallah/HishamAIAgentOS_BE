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
    Bug,
    Issue,
    Epic,
    Sprint,
    Notification,
    Mention,
    StoryComment
)
from datetime import date

User = get_user_model()
logger = logging.getLogger(__name__)


def _send_websocket_notification(notification: Notification):
    """
    Helper function to send notification via WebSocket.
    This is called after a notification is created to provide real-time updates.
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if channel_layer:
            # Send notification to user's personal notification channel
            user_group = f'user_{notification.recipient.id}_notifications'
            async_to_sync(channel_layer.group_send)(
                user_group,
                {
                    'type': 'notification',
                    'notification': {
                        'id': str(notification.id),
                        'type': notification.notification_type,
                        'title': notification.title,
                        'message': notification.message,
                        'is_read': notification.is_read,
                        'created_at': notification.created_at.isoformat(),
                        'project': str(notification.project.id) if notification.project else None,
                        'story': str(notification.story.id) if notification.story else None,
                    }
                }
            )
    except Exception as e:
        # WebSocket notification is optional, don't fail if it doesn't work
        logger.warning(f"Failed to send WebSocket notification: {e}")


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
        recipient: User,
        notification_type: str = 'in_app'
    ) -> bool:
        """
        Check if notification should be sent based on project settings and user preferences.
        
        Args:
            event_type: Type of event (e.g., 'on_status_change', 'on_assignment')
            recipient: User who should receive the notification
            notification_type: 'email' or 'in_app'
        
        Returns True if:
        1. Project notification settings allow it
        2. User preferences allow it
        3. Notification is enabled for the event type
        """
        # Check project-level settings
        if self.config:
            settings = self.config.notification_settings or {}
            
            # Check global notification settings
            if notification_type == 'email' and not settings.get('email_enabled', True):
                return False
            if notification_type == 'in_app' and not settings.get('in_app_enabled', True):
                return False
            
            # Check event-specific settings
            event_setting = settings.get(event_type, {})
            if isinstance(event_setting, dict):
                # If enabled is explicitly False, don't send
                if event_setting.get('enabled') is False:
                    return False
                # If enabled is not set or is True, allow it (default to True)
            elif isinstance(event_setting, bool):
                if not event_setting:
                    return False
            
            # Check specific notification type settings
            if notification_type == 'email' and not settings.get('mention_notifications', True):
                if event_type in ['on_mention', 'mention']:
                    return False
            if notification_type == 'in_app' and not settings.get('status_change_notifications', True):
                if event_type in ['on_status_change', 'status_change']:
                    return False
            if notification_type == 'in_app' and not settings.get('assignment_notifications', True):
                if event_type in ['on_assignment', 'assignment']:
                    return False
        
        # Check user preferences (if they have opted out)
        user_prefs = getattr(recipient, 'notification_preferences', None) or {}
        if not user_prefs.get('enabled', True):
            return False
        
        # Check event-specific user preferences
        event_pref = user_prefs.get(event_type, {})
        if isinstance(event_pref, dict) and event_pref.get('enabled') is False:
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
            # For mention events, default to mentioned_user
            if event_type == 'on_mention':
                recipient_types = ['mentioned_user']
            else:
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
            
            # Add project members
            if 'project_members' in recipient_types:
                if story.project and story.project.members.exists():
                    recipients.update(story.project.members.all())
            
            # Add sprint members
            if 'sprint_members' in recipient_types and story.sprint:
                # In future, implement sprint members. For now, use project members
                if story.project and story.project.members.exists():
                    recipients.update(story.project.members.all())
            
            # Add epic owner
            if 'epic_owner' in recipient_types and story.epic and story.epic.owner:
                recipients.add(story.epic.owner)
            
            # Add creator
            if 'creator' in recipient_types and story.created_by:
                recipients.add(story.created_by)
            
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
        
        # Remove None values and return list
        recipients = {r for r in recipients if r is not None}
        return list(recipients)
    
    @transaction.atomic
    def notify_mention(
        self,
        mention: Mention,
        story: UserStory
    ) -> Optional[Notification]:
        """
        Create notification for a mention.
        
        For mentions, the mentioned_user should ALWAYS receive a notification if:
        1. The event is enabled in notification settings
        2. User preferences allow it
        
        Note: The mentioned user is ALWAYS notified when mentioned, regardless of recipient configuration.
        This is because being mentioned is a direct action that requires notification.
        """
        # For mentions, ALWAYS send notification unless explicitly disabled
        # This is a direct action that requires notification
        logger.info(f"Processing mention notification for user {mention.mentioned_user.email} in story {story.title}")
        logger.info(f"Project config exists: {self.config is not None}")
        
        # Check if explicitly disabled in project settings
        explicitly_disabled = False
        if self.config:
            settings = self.config.notification_settings or {}
            logger.info(f"Notification settings: {settings}")
            event_setting = settings.get('on_mention', {})
            logger.info(f"on_mention event setting: {event_setting}")
            
            # Check if explicitly disabled
            if isinstance(event_setting, dict):
                if event_setting.get('enabled') is False:
                    explicitly_disabled = True
                    logger.warning("Mention notifications explicitly disabled in project settings")
            elif isinstance(event_setting, bool) and not event_setting:
                explicitly_disabled = True
                logger.warning("Mention notifications explicitly disabled in project settings")
        
        # Check user preferences (if they have opted out)
        user_prefs = getattr(mention.mentioned_user, 'notification_preferences', None) or {}
        if not user_prefs.get('enabled', True):
            logger.warning(f"User {mention.mentioned_user.email} has disabled all notifications")
            return None
        
        # Check event-specific user preferences
        event_pref = user_prefs.get('on_mention', {})
        if isinstance(event_pref, dict) and event_pref.get('enabled') is False:
            logger.warning(f"User {mention.mentioned_user.email} has disabled mention notifications")
            return None
        
        # If explicitly disabled in project settings, don't send
        if explicitly_disabled:
            logger.warning("Mention notifications disabled - not sending")
            return None
        
        logger.info("All checks passed - sending mention notification")
        
        # For mention notifications, ALWAYS notify the mentioned user
        # This is a direct action that requires notification regardless of recipient configuration
        # Get the user who created the mention (created_by)
        mentioned_by = mention.created_by
        if not mentioned_by:
            # Fallback: try to get from story created_by
            mentioned_by = story.created_by
        
        notification = Notification.objects.create(
            recipient=mention.mentioned_user,
            notification_type='mention',
            title=f"You were mentioned in '{story.title}'",
            message=f"{mentioned_by.get_full_name() if mentioned_by else 'Someone'} mentioned you in story '{story.title}'",
            project=story.project,
            story=story,
            mention=mention,
            metadata={
                'mentioned_by': str(mentioned_by.id) if mentioned_by else None,
                'text_snippet': getattr(mention, 'text_snippet', '')[:200] if hasattr(mention, 'text_snippet') else ''
            },
            created_by=mentioned_by
        )
        
        logger.info(f"Created mention notification {notification.id} for user {mention.mentioned_user.email} in story {story.title}")
        
        # Send real-time notification via WebSocket
        _send_websocket_notification(notification)
        
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
    def notify_epic_owner_assignment(
        self,
        epic: Epic,
        old_owner: Optional[User],
        new_owner: User,
        assigned_by: User
    ) -> Optional[Notification]:
        """Create notification for epic owner assignment."""
        if not self._should_send_notification('on_assignment', new_owner):
            return None
        
        notification = Notification.objects.create(
            recipient=new_owner,
            notification_type='assignment',
            title=f"You were assigned as owner of '{epic.title}'",
            message=f"{assigned_by.get_full_name() or assigned_by.email} assigned you as owner of epic '{epic.title}'",
            project=epic.project,
            story=None,  # Epic doesn't have a story
            metadata={
                'assigned_by': str(assigned_by.id),
                'old_owner': str(old_owner.id) if old_owner else None,
                'epic_id': str(epic.id),
                'epic_title': epic.title
            },
            created_by=assigned_by
        )
        
        logger.info(f"Created epic owner assignment notification {notification.id} for user {new_owner.email}")
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
    
    @transaction.atomic
    def send_notification(
        self,
        item: Any,
        notification_type: str,
        recipients: List[User],
        message: str,
        user: Optional[User] = None
    ) -> List[Notification]:
        """
        Generic method to send notifications (used by automation service).
        
        Args:
            item: The work item (UserStory, Task, Bug, Issue)
            notification_type: Type of notification ('email', 'in_app', etc.)
            recipients: List of users to notify
            message: Notification message
            user: User who triggered the notification (optional)
            
        Returns:
            List of created notifications
        """
        notifications = []
        
        if not recipients:
            logger.warning(f"No recipients provided for notification on {item.__class__.__name__} {item.id}")
            return notifications
        
        # Determine event type from item type
        event_type = 'on_automation_triggered'
        if hasattr(item, 'status'):
            event_type = 'on_status_change'
        elif hasattr(item, 'assigned_to'):
            event_type = 'on_assignment'
        
        # Get project from item
        project = None
        if hasattr(item, 'project'):
            project = item.project
        elif hasattr(item, 'story') and item.story:
            project = item.story.project
        
        for recipient in recipients:
            if not recipient:
                continue
                
            # Check if notification should be sent
            if not self._should_send_notification(event_type, recipient, notification_type):
                continue
            
            try:
                # Create notification
                notification = Notification.objects.create(
                    recipient=recipient,
                    notification_type=notification_type,
                    title=message[:100] if message else 'Notification',  # Truncate title
                    message=message or 'You have a new notification',
                    project=project,
                    story=item if isinstance(item, UserStory) else None,
                    created_by=user
                )
                notifications.append(notification)
            except Exception as e:
                logger.error(f"Error creating notification for recipient {recipient.id}: {str(e)}", exc_info=True)
        
        logger.info(f"Created {len(notifications)} notifications via automation for {item.__class__.__name__} {item.id}")
        return notifications
    
    @transaction.atomic
    def notify_due_date_approaching(
        self,
        item: Any,  # UserStory, Task, Bug, or Issue
        days_until_due: int,
        due_date: date
    ) -> Optional[Notification]:
        """
        Create notification for due date approaching.
        
        Args:
            item: Work item (UserStory, Task, Bug, or Issue)
            days_until_due: Number of days until due date
            due_date: The due date
        """
        # Get assignee or project members
        recipients = []
        
        if hasattr(item, 'assigned_to') and item.assigned_to:
            recipients.append(item.assigned_to)
        
        # Also notify project members if configured
        project = None
        if hasattr(item, 'project'):
            project = item.project
        elif hasattr(item, 'story') and item.story:
            project = item.story.project
        
        if not recipients and project:
            # If no assignee, notify project owner
            if project.owner:
                recipients.append(project.owner)
        
        if not recipients:
            logger.debug(f"No recipients for due date notification for {item.__class__.__name__} {item.id}")
            return None
        
        notifications = []
        for recipient in recipients:
            if not self._should_send_notification('on_due_date_approaching', recipient):
                continue
            
            # Determine item type and title
            item_type = item.__class__.__name__.lower()
            if isinstance(item, UserStory):
                item_title = f"Story '{item.title}'"
            elif isinstance(item, Task):
                item_title = f"Task '{item.title}'"
            elif isinstance(item, Bug):
                item_title = f"Bug '{item.title}'"
            elif isinstance(item, Issue):
                item_title = f"Issue '{item.title}'"
            else:
                item_title = f"Item '{getattr(item, 'title', 'Untitled')}'"
            
            # Create message based on days until due
            if days_until_due == 0:
                message = f"{item_title} is due today"
            elif days_until_due == 1:
                message = f"{item_title} is due tomorrow"
            else:
                message = f"{item_title} is due in {days_until_due} days"
            
            notification = Notification.objects.create(
                recipient=recipient,
                notification_type='due_date',
                title=f"Due date approaching: {item_title}",
                message=message,
                project=project,
                story=item if isinstance(item, UserStory) else None,
                metadata={
                    'item_type': item_type,
                    'item_id': str(item.id),
                    'due_date': due_date.isoformat(),
                    'days_until_due': days_until_due
                },
                created_by=None  # System-generated
            )
            notifications.append(notification)
        
        logger.info(f"Created {len(notifications)} due date approaching notifications for {item.__class__.__name__} {item.id}")
        return notifications[0] if notifications else None


def get_notification_service(project: Optional[Any] = None) -> NotificationService:
    """Convenience function to get a NotificationService instance."""
    return NotificationService(project)

