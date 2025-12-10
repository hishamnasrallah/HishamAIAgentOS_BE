"""
Django signals for Project Management app.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Project, ProjectConfiguration, UserStory, Mention, StoryComment, Task, Epic, Bug, Issue
from .services.automation import execute_automation_rules
from .services.notifications import get_notification_service
from .services.assignment_rules import AssignmentRulesService
from .services.auto_tagging import AutoTaggingService
from .utils.work_item_numbers import get_next_work_item_number
import logging
import threading

User = get_user_model()
logger = logging.getLogger(__name__)

# Store previous state for status change detection
_story_previous_state = {}
_epic_previous_state = {}

# Thread locks for thread-safe state management
_epic_state_lock = threading.Lock()


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
    """Store previous state of story before save to detect changes and auto-generate number."""
    is_new = instance._state.adding  # True for new instances, False for updates
    logger.info(f"[SIGNAL] Pre-save for UserStory. PK: {instance.pk}, Number: '{instance.number}', Is New: {is_new}")
    
    # Auto-generate number for new stories
    if is_new and (not instance.number or instance.number.strip() == ''):
        try:
            # Ensure project is set before generating number
            if instance.project_id or instance.project:
                project_id = str(instance.project_id) if instance.project_id else str(instance.project.id)
                logger.info(f"[SIGNAL] Generating number for new story in project: {project_id}")
                instance.number = get_next_work_item_number(project_id, 'story')
                logger.info(f"[SIGNAL] ✓ Auto-generated story number: {instance.number}")
            else:
                logger.warning("[SIGNAL] Cannot generate story number - no project set")
        except Exception as e:
            logger.error(f"[SIGNAL] ✗ Error generating story number: {e}", exc_info=True)
    elif is_new:
        logger.info(f"[SIGNAL] New story already has number: {instance.number}")
    
    # Store previous state for existing stories
    if not is_new:
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
            
            # Apply assignment rules
            try:
                assignee = AssignmentRulesService.apply_assignment_rules(
                    str(instance.project.id),
                    'story',
                    str(instance.id)
                )
                if assignee:
                    logger.info(f"Applied assignment rule for story {instance.id}: assigned to {assignee.email}")
            except Exception as e:
                logger.error(f"Error applying assignment rules: {e}", exc_info=True)
            
            # Apply auto-tagging
            try:
                applied_tags = AutoTaggingService.apply_auto_tagging(
                    str(instance.project.id),
                    'story',
                    str(instance.id)
                )
                if applied_tags:
                    logger.info(f"Applied auto-tagging for story {instance.id}: {applied_tags}")
            except Exception as e:
                logger.error(f"Error applying auto-tagging: {e}", exc_info=True)
            
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
    """Store previous state of epic before save to detect owner changes and auto-generate number."""
    is_new = instance._state.adding
    
    # Auto-generate number for new epics
    if is_new and (not instance.number or instance.number.strip() == ''):
        try:
            instance.number = get_next_work_item_number(str(instance.project_id), 'epic')
            logger.info(f"[SIGNAL] Auto-generated epic number: {instance.number}")
        except Exception as e:
            logger.error(f"[SIGNAL] Error generating epic number: {e}", exc_info=True)
    
    # Store previous state for existing epics
    if not is_new:
        try:
            with _epic_state_lock:
                old_instance = Epic.objects.select_for_update().get(pk=instance.pk)
                _epic_previous_state[instance.pk] = {
                    'owner': old_instance.owner_id,
                    'status': old_instance.status,
                }
        except Epic.DoesNotExist:
            pass


@receiver(pre_save, sender=Task)
def generate_task_number(sender, instance, **kwargs):
    """Auto-generate task number if not provided."""
    is_new = instance._state.adding
    if is_new and (not instance.number or instance.number.strip() == ''):
        try:
            project_id = instance.story.project_id if instance.story else None
            if project_id:
                instance.number = get_next_work_item_number(str(project_id), 'task')
                logger.info(f"[SIGNAL] Auto-generated task number: {instance.number}")
        except Exception as e:
            logger.error(f"[SIGNAL] Error generating task number: {e}", exc_info=True)


@receiver(pre_save, sender=Bug)
def generate_bug_number(sender, instance, **kwargs):
    """Auto-generate bug number if not provided."""
    is_new = instance._state.adding
    if is_new and (not instance.number or instance.number.strip() == ''):
        try:
            instance.number = get_next_work_item_number(str(instance.project_id), 'bug')
            logger.info(f"[SIGNAL] Auto-generated bug number: {instance.number}")
        except Exception as e:
            logger.error(f"[SIGNAL] Error generating bug number: {e}", exc_info=True)


@receiver(pre_save, sender=Issue)
def generate_issue_number(sender, instance, **kwargs):
    """Auto-generate issue number if not provided."""
    is_new = instance._state.adding
    if is_new and (not instance.number or instance.number.strip() == ''):
        try:
            instance.number = get_next_work_item_number(str(instance.project_id), 'issue')
            logger.info(f"[SIGNAL] Auto-generated issue number: {instance.number}")
        except Exception as e:
            logger.error(f"[SIGNAL] Error generating issue number: {e}", exc_info=True)


@receiver(post_save, sender=Epic)
def handle_epic_owner_assignment(sender, instance, created, **kwargs):
    """
    Send notification when epic owner is assigned or changed.
    """
    from django.db import transaction
    
    try:
        # Get previous state with lock
        with _epic_state_lock:
            previous_state = _epic_previous_state.get(instance.pk, {})
            old_owner_id = previous_state.get('owner')
            new_owner_id = instance.owner_id if instance.owner else None
            
            # Clean up state
            if instance.pk in _epic_previous_state:
                del _epic_previous_state[instance.pk]
        
        # Only send notification if owner changed and new owner exists
        if new_owner_id and new_owner_id != old_owner_id:
            with transaction.atomic():
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
