"""
Django signals for Project Management app.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Project, ProjectConfiguration, UserStory, Mention, StoryComment, Task, Epic
from .services.automation import execute_automation_rules
from .services.notifications import get_notification_service
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

# Store previous state for status change detection
_story_previous_state = {}
_epic_previous_state = {}


@receiver(post_save, sender=Project)
def create_project_configuration(sender, instance, created, **kwargs):
    """
    Automatically creates a ProjectConfiguration for a new Project.
    """
    if created:
        try:
            config = ProjectConfiguration.objects.create(project=instance)
            config.initialize_defaults()
            logger.info(f"Created default configuration for new project: {instance.name}")
        except Exception as e:
            logger.error(f"Error creating default configuration for project {instance.name}: {e}", exc_info=True)


@receiver(pre_save, sender=UserStory)
def store_story_previous_state(sender, instance, **kwargs):
    """Store previous state of story before save to detect changes."""
    if instance.pk:
        try:
            old_instance = UserStory.objects.get(pk=instance.pk)
            _story_previous_state[instance.pk] = {
                'status': old_instance.status,
                'assigned_to': old_instance.assigned_to_id,
                'priority': old_instance.priority,
            }
        except UserStory.DoesNotExist:
            pass


@receiver(post_save, sender=UserStory)
def handle_story_automation(sender, instance, created, **kwargs):
    """
    Execute automation rules when a story is created or updated.
    Also send notifications for story events.
    """
    try:
        # Get current user for notifications
        current_user = None
        try:
            from apps.monitoring.middleware import _thread_locals
            if hasattr(_thread_locals, 'user'):
                current_user = getattr(_thread_locals, 'user', None)
                if current_user and hasattr(current_user, 'is_authenticated') and not current_user.is_authenticated:
                    current_user = None
        except Exception:
            pass
        
        if not current_user and hasattr(instance, 'created_by') and instance.created_by:
            current_user = instance.created_by
        
        notification_service = get_notification_service(instance.project)
        
        if created:
            # Execute on_story_create rules
            results = execute_automation_rules('on_story_create', instance)
            if results:
                logger.info(f"Executed {len(results)} automation rules on story creation: {instance.id}")
            
            # Send story creation notification
            if current_user:
                try:
                    notification_service.notify_story_created(instance, current_user)
                except Exception as e:
                    logger.error(f"Error sending story creation notification: {e}", exc_info=True)
        else:
            # Check if status changed
            previous_state = _story_previous_state.get(instance.pk, {})
            old_status = previous_state.get('status')
            old_assignee_id = previous_state.get('assigned_to')
            
            if old_status and old_status != instance.status:
                # Execute on_status_change rules
                results = execute_automation_rules(
                    'on_status_change',
                    instance,
                    context={'old_status': old_status, 'new_status': instance.status}
                )
                if results:
                    logger.info(f"Executed {len(results)} automation rules on status change: {instance.id}")
                
                # Send status change notification
                if current_user:
                    try:
                        notification_service.notify_status_change(
                            instance,
                            old_status,
                            instance.status,
                            current_user
                        )
                    except Exception as e:
                        logger.error(f"Error sending status change notification: {e}", exc_info=True)
            
            # Check if assignee changed
            if old_assignee_id != instance.assigned_to_id and instance.assigned_to and current_user:
                try:
                    old_assignee = User.objects.get(id=old_assignee_id) if old_assignee_id else None
                    notification_service.notify_assignment(
                        instance,
                        old_assignee,
                        instance.assigned_to,
                        current_user
                    )
                except Exception as e:
                    logger.error(f"Error sending assignment notification: {e}", exc_info=True)
            
            # Execute on_story_update rules
            results = execute_automation_rules('on_story_update', instance, previous_state)
            if results:
                logger.info(f"Executed {len(results)} automation rules on story update: {instance.id}")
            
            # Send story update notification (if not already sent for status/assignment)
            if current_user and old_status == instance.status and old_assignee_id == instance.assigned_to_id:
                try:
                    notification_service.notify_story_updated(instance, current_user)
                except Exception as e:
                    logger.error(f"Error sending story update notification: {e}", exc_info=True)
        
        # Clean up stored state
        if instance.pk in _story_previous_state:
            del _story_previous_state[instance.pk]
            
    except Exception as e:
        logger.error(f"Error executing automation rules for story {instance.id}: {e}", exc_info=True)


@receiver(post_save, sender=UserStory)
def extract_story_mentions(sender, instance, created, **kwargs):
    """
    Extract @mentions from story description and acceptance_criteria.
    Creates Mention objects for each mentioned user.
    """
    try:
        mentions = instance.extract_mentions()
        if not mentions:
            return
        
        # Get current user from thread-local storage (set by middleware)
        current_user = None
        try:
            from apps.monitoring.middleware import _thread_locals
            if hasattr(_thread_locals, 'user'):
                current_user = getattr(_thread_locals, 'user', None)
                # Ensure user is authenticated
                if current_user and hasattr(current_user, 'is_authenticated') and not current_user.is_authenticated:
                    current_user = None
        except Exception:
            pass
        
        # Fallback: use instance's created_by if available
        if not current_user and hasattr(instance, 'created_by') and instance.created_by:
            current_user = instance.created_by
        
        # Find users by email or username
        for mention_text in mentions:
            # Try to find user by email first, then by username
            user = None
            if '@' in mention_text:
                # It's an email
                try:
                    user = User.objects.get(email=mention_text)
                except User.DoesNotExist:
                    logger.warning(f"Mentioned user not found: {mention_text}")
                    continue
            else:
                # It's a username - try to find by username or email prefix
                try:
                    user = User.objects.get(username=mention_text)
                except User.DoesNotExist:
                    # Try email prefix match
                    try:
                        user = User.objects.filter(email__startswith=mention_text).first()
                    except:
                        pass
                
                if not user:
                    logger.warning(f"Mentioned user not found: {mention_text}")
                    continue
            
            # Create or update mention
            mention, created = Mention.objects.get_or_create(
                story=instance,
                mentioned_user=user,
                mention_text=f"@{mention_text}",
                defaults={
                    'created_by': current_user if current_user and current_user.is_authenticated else None,
                }
            )
            
            if created:
                logger.info(f"Created mention: {mention_text} in story {instance.title}")
                
                # Send notification
                try:
                    notification_service = get_notification_service(instance.project)
                    notification_service.notify_mention(mention, instance)
                except Exception as e:
                    logger.error(f"Error sending mention notification: {e}", exc_info=True)
        
    except Exception as e:
        logger.error(f"Error extracting mentions from story {instance.id}: {e}", exc_info=True)


@receiver(post_save, sender=StoryComment)
def handle_comment_notifications(sender, instance, created, **kwargs):
    """
    Send notifications when a comment is created.
    """
    if not created:
        return
    
    try:
        notification_service = get_notification_service(instance.story.project)
        notification_service.notify_comment(instance, instance.story)
    except Exception as e:
        logger.error(f"Error sending comment notification: {e}", exc_info=True)


@receiver(post_save, sender=StoryComment)
def extract_comment_mentions(sender, instance, created, **kwargs):
    """
    Extract @mentions from comment content.
    Creates Mention objects for each mentioned user.
    """
    if not created:
        return
    
    try:
        mentions = instance.extract_mentions()
        if not mentions:
            return
        
        # Get current user from thread-local storage
        from apps.monitoring.signals import get_current_user
        current_user = get_current_user()
        
        # Find users by email or username
        for mention_text in mentions:
            # Try to find user by email first, then by username
            user = None
            if '@' in mention_text:
                # It's an email
                try:
                    user = User.objects.get(email=mention_text)
                except User.DoesNotExist:
                    logger.warning(f"Mentioned user not found: {mention_text}")
                    continue
            else:
                # It's a username - try to find by username or email prefix
                try:
                    user = User.objects.get(username=mention_text)
                except User.DoesNotExist:
                    # Try email prefix match
                    try:
                        user = User.objects.filter(email__startswith=mention_text).first()
                    except:
                        pass
                
                if not user:
                    logger.warning(f"Mentioned user not found: {mention_text}")
                    continue
            
            # Create mention
            mention = Mention.objects.create(
                comment=instance,
                story=instance.story,
                mentioned_user=user,
                mention_text=f"@{mention_text}",
                created_by=current_user if current_user and current_user.is_authenticated else None,
            )
            
            logger.info(f"Created mention: {mention_text} in comment on story {instance.story.title}")
            
            # Send notification
            try:
                notification_service = get_notification_service(instance.story.project)
                notification_service.notify_mention(mention, instance.story)
            except Exception as e:
                logger.error(f"Error sending mention notification: {e}", exc_info=True)
        
    except Exception as e:
        logger.error(f"Error extracting mentions from comment {instance.id}: {e}", exc_info=True)


@receiver(pre_save, sender=Epic)
def store_epic_previous_state(sender, instance, **kwargs):
    """Store previous state of epic before save to detect owner changes."""
    if instance.pk:
        try:
            old_instance = Epic.objects.get(pk=instance.pk)
            _epic_previous_state[instance.pk] = {
                'owner': old_instance.owner_id,
                'status': old_instance.status,
            }
        except Epic.DoesNotExist:
            pass


@receiver(post_save, sender=Epic)
def handle_epic_owner_assignment(sender, instance, created, **kwargs):
    """
    Send notification when epic owner is assigned or changed.
    """
    try:
        previous_state = _epic_previous_state.get(instance.pk, {})
        old_owner_id = previous_state.get('owner')
        new_owner_id = instance.owner_id if instance.owner else None
        
        # Only send notification if owner changed and new owner exists
        if new_owner_id and new_owner_id != old_owner_id:
            notification_service = get_notification_service(instance.project)
            
            # Get current user (who made the change)
            current_user = None
            try:
                from apps.monitoring.middleware import _thread_locals
                if hasattr(_thread_locals, 'user'):
                    current_user = getattr(_thread_locals, 'user', None)
                    if current_user and hasattr(current_user, 'is_authenticated') and not current_user.is_authenticated:
                        current_user = None
            except Exception:
                pass
            
            if not current_user and hasattr(instance, 'updated_by') and instance.updated_by:
                current_user = instance.updated_by
            elif not current_user and hasattr(instance, 'created_by') and instance.created_by:
                current_user = instance.created_by
            
            # Get old owner if exists
            old_owner = None
            if old_owner_id:
                try:
                    old_owner = User.objects.get(id=old_owner_id)
                except User.DoesNotExist:
                    pass
            
            # Send notification to new owner
            if instance.owner:
                try:
                    notification_service.notify_epic_owner_assignment(
                        epic=instance,
                        old_owner=old_owner,
                        new_owner=instance.owner,
                        assigned_by=current_user or instance.owner
                    )
                    logger.info(f"Sent owner assignment notification for epic {instance.id} to {instance.owner.email}")
                except Exception as e:
                    logger.error(f"Error sending epic owner assignment notification: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Error handling epic owner assignment for epic {instance.id}: {e}", exc_info=True)


@receiver(post_save, sender=Task)
def handle_task_complete_automation(sender, instance, created, **kwargs):
    """
    Execute automation rules when a task is completed.
    """
    if created or instance.status != 'done':
        return
    
    try:
        # Check if task was just completed (status changed to done)
        if hasattr(instance, '_previous_status') and instance._previous_status != 'done':
            story = instance.story
            if story:
                results = execute_automation_rules(
                    'on_task_complete',
                    story,
                    context={'task': instance}
                )
                if results:
                    logger.info(f"Executed {len(results)} automation rules on task completion: {instance.id}")
    except Exception as e:
        logger.error(f"Error executing automation rules for task {instance.id}: {e}", exc_info=True)
