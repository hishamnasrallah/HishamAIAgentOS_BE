"""
Celery tasks for project management.
"""

import logging
from datetime import date, timedelta
from celery import shared_task
from django.utils import timezone
from django.db.models import Q

from apps.projects.models import Project, Sprint, ProjectConfiguration, UserStory, Task, Bug, Issue
from apps.projects.services.notifications import get_notification_service

logger = logging.getLogger(__name__)


@shared_task
def auto_close_sprints():
    """
    Automatically close sprints that have passed their end date.
    
    This task checks all active sprints and closes those where:
    1. The sprint end_date has passed
    2. The project has auto_close_sprints enabled in configuration
    """
    logger.info("Starting auto_close_sprints task")
    
    today = date.today()
    closed_count = 0
    skipped_count = 0
    
    # Get all active sprints with end_date in the past
    active_sprints = Sprint.objects.filter(
        status__in=['active', 'in_progress', 'planned'],
        end_date__lt=today
    ).select_related('project')
    
    for sprint in active_sprints:
        try:
            # Check if project has auto_close_sprints enabled
            config = None
            try:
                config = sprint.project.configuration
            except ProjectConfiguration.DoesNotExist:
                pass
            
            # Only close if auto_close_sprints is enabled
            if config and config.auto_close_sprints:
                sprint.status = 'completed'
                sprint.save(update_fields=['status', 'updated_at'])
                closed_count += 1
                logger.info(f"Auto-closed sprint {sprint.id} ({sprint.name}) for project {sprint.project.name}")
            else:
                skipped_count += 1
                logger.debug(f"Skipped sprint {sprint.id} - auto_close_sprints not enabled")
        except Exception as e:
            logger.error(f"Error closing sprint {sprint.id}: {str(e)}", exc_info=True)
    
    logger.info(f"Auto-close sprints task completed: {closed_count} closed, {skipped_count} skipped")
    return {'closed': closed_count, 'skipped': skipped_count}


@shared_task
def check_and_close_sprints_for_project(project_id: str):
    """
    Check and close sprints for a specific project.
    
    Args:
        project_id: UUID of the project
    """
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        logger.error(f"Project {project_id} not found")
        return {'error': 'Project not found'}
    
    today = date.today()
    closed_count = 0
    
    # Get project configuration
    try:
        config = project.configuration
    except ProjectConfiguration.DoesNotExist:
        logger.warning(f"No configuration found for project {project_id}")
        return {'closed': 0, 'skipped': 0, 'reason': 'No configuration'}
    
    # Only proceed if auto_close_sprints is enabled
    if not config.auto_close_sprints:
        logger.debug(f"Auto-close sprints not enabled for project {project_id}")
        return {'closed': 0, 'skipped': 0, 'reason': 'Auto-close disabled'}
    
    # Get active sprints for this project with end_date in the past
    active_sprints = Sprint.objects.filter(
        project=project,
        status__in=['active', 'in_progress', 'planned'],
        end_date__lt=today
    )
    
    for sprint in active_sprints:
        try:
            sprint.status = 'completed'
            sprint.save(update_fields=['status', 'updated_at'])
            closed_count += 1
            logger.info(f"Auto-closed sprint {sprint.id} ({sprint.name}) for project {project.name}")
        except Exception as e:
            logger.error(f"Error closing sprint {sprint.id}: {str(e)}", exc_info=True)
    
    return {'closed': closed_count}


@shared_task
def check_due_dates_approaching():
    """
    Check for work items with due dates approaching and send notifications.
    
    This task checks all work items (stories, tasks, bugs, issues) and sends
    notifications for items that are:
    - Due today
    - Due tomorrow
    - Due within the next 3 days (configurable)
    
    Notifications are only sent if:
    1. The item has a due_date set
    2. The item is not already completed/done
    3. The project has due date notifications enabled
    """
    logger.info("Starting check_due_dates_approaching task")
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    three_days_from_now = today + timedelta(days=3)
    
    notifications_sent = 0
    items_checked = 0
    
    # Check UserStories
    stories = UserStory.objects.filter(
        due_date__isnull=False,
        due_date__gte=today,
        due_date__lte=three_days_from_now
    ).exclude(
        status__in=['done', 'completed', 'cancelled', 'closed']
    ).select_related('project', 'assigned_to', 'project__configuration')
    
    for story in stories:
        items_checked += 1
        try:
            # Check if project has due date notifications enabled
            config = None
            try:
                config = story.project.configuration
            except ProjectConfiguration.DoesNotExist:
                pass
            
            # Check notification settings
            if config:
                notification_settings = config.notification_settings or {}
                due_date_settings = notification_settings.get('on_due_date_approaching', {})
                if isinstance(due_date_settings, dict) and not due_date_settings.get('enabled', True):
                    continue  # Due date notifications disabled for this project
            
            # Calculate days until due
            days_until_due = (story.due_date - today).days
            
            # Only notify for today, tomorrow, or 3 days before
            if days_until_due in [0, 1, 3]:
                notification_service = get_notification_service(story.project)
                notification_service.notify_due_date_approaching(
                    item=story,
                    days_until_due=days_until_due,
                    due_date=story.due_date
                )
                notifications_sent += 1
        except Exception as e:
            logger.error(f"Error processing due date notification for story {story.id}: {str(e)}", exc_info=True)
    
    # Check Tasks
    tasks = Task.objects.filter(
        due_date__isnull=False,
        due_date__gte=today,
        due_date__lte=three_days_from_now
    ).exclude(
        status__in=['done', 'completed', 'cancelled', 'closed']
    ).select_related('story', 'story__project', 'assigned_to', 'story__project__configuration')
    
    for task in tasks:
        items_checked += 1
        try:
            # Get project from story
            if not task.story or not task.story.project:
                continue
            
            # Check if project has due date notifications enabled
            config = None
            try:
                config = task.story.project.configuration
            except ProjectConfiguration.DoesNotExist:
                pass
            
            # Check notification settings
            if config:
                notification_settings = config.notification_settings or {}
                due_date_settings = notification_settings.get('on_due_date_approaching', {})
                if isinstance(due_date_settings, dict) and not due_date_settings.get('enabled', True):
                    continue  # Due date notifications disabled for this project
            
            # Calculate days until due
            days_until_due = (task.due_date - today).days
            
            # Only notify for today, tomorrow, or 3 days before
            if days_until_due in [0, 1, 3]:
                notification_service = get_notification_service(task.story.project)
                notification_service.notify_due_date_approaching(
                    item=task,
                    days_until_due=days_until_due,
                    due_date=task.due_date
                )
                notifications_sent += 1
        except Exception as e:
            logger.error(f"Error processing due date notification for task {task.id}: {str(e)}", exc_info=True)
    
    # Check Bugs
    bugs = Bug.objects.filter(
        due_date__isnull=False,
        due_date__gte=today,
        due_date__lte=three_days_from_now
    ).exclude(
        status__in=['resolved', 'closed', 'cancelled']
    ).select_related('project', 'assigned_to', 'project__configuration')
    
    for bug in bugs:
        items_checked += 1
        try:
            # Check if project has due date notifications enabled
            config = None
            try:
                config = bug.project.configuration
            except ProjectConfiguration.DoesNotExist:
                pass
            
            # Check notification settings
            if config:
                notification_settings = config.notification_settings or {}
                due_date_settings = notification_settings.get('on_due_date_approaching', {})
                if isinstance(due_date_settings, dict) and not due_date_settings.get('enabled', True):
                    continue  # Due date notifications disabled for this project
            
            # Calculate days until due
            days_until_due = (bug.due_date - today).days
            
            # Only notify for today, tomorrow, or 3 days before
            if days_until_due in [0, 1, 3]:
                notification_service = get_notification_service(bug.project)
                notification_service.notify_due_date_approaching(
                    item=bug,
                    days_until_due=days_until_due,
                    due_date=bug.due_date
                )
                notifications_sent += 1
        except Exception as e:
            logger.error(f"Error processing due date notification for bug {bug.id}: {str(e)}", exc_info=True)
    
    # Check Issues
    issues = Issue.objects.filter(
        due_date__isnull=False,
        due_date__gte=today,
        due_date__lte=three_days_from_now
    ).exclude(
        status__in=['resolved', 'closed', 'cancelled']
    ).select_related('project', 'assigned_to', 'project__configuration')
    
    for issue in issues:
        items_checked += 1
        try:
            # Check if project has due date notifications enabled
            config = None
            try:
                config = issue.project.configuration
            except ProjectConfiguration.DoesNotExist:
                pass
            
            # Check notification settings
            if config:
                notification_settings = config.notification_settings or {}
                due_date_settings = notification_settings.get('on_due_date_approaching', {})
                if isinstance(due_date_settings, dict) and not due_date_settings.get('enabled', True):
                    continue  # Due date notifications disabled for this project
            
            # Calculate days until due
            days_until_due = (issue.due_date - today).days
            
            # Only notify for today, tomorrow, or 3 days before
            if days_until_due in [0, 1, 3]:
                notification_service = get_notification_service(issue.project)
                notification_service.notify_due_date_approaching(
                    item=issue,
                    days_until_due=days_until_due,
                    due_date=issue.due_date
                )
                notifications_sent += 1
        except Exception as e:
            logger.error(f"Error processing due date notification for issue {issue.id}: {str(e)}", exc_info=True)
    
    logger.info(f"Due date check task completed: {items_checked} items checked, {notifications_sent} notifications sent")
    return {'items_checked': items_checked, 'notifications_sent': notifications_sent}

