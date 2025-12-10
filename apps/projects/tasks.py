"""
Celery tasks for project management.
"""

import logging
from datetime import date, timedelta
from collections import defaultdict
from celery import shared_task
from django.utils import timezone
from django.db import transaction
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
    from django.db import transaction
    
    logger.info("Starting check_due_dates_approaching task")
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    three_days_from_now = today + timedelta(days=3)
    
    notifications_sent = 0
    items_checked = 0
    errors = []
    
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
    
    # Check Tasks - Group by project
    tasks = Task.objects.filter(
        due_date__isnull=False,
        due_date__gte=today,
        due_date__lte=three_days_from_now
    ).exclude(
        status__in=['done', 'completed', 'cancelled', 'closed']
    ).select_related('story', 'story__project', 'assigned_to', 'story__project__configuration')
    
    # Filter out tasks without stories or projects
    tasks_with_projects = [t for t in tasks if t.story and t.story.project]
    tasks_by_project = defaultdict(list)
    for task in tasks_with_projects:
        tasks_by_project[task.story.project_id].append(task)
    
    # Process by project
    for project_id, project_tasks in tasks_by_project.items():
        project = project_tasks[0].story.project
        config = getattr(project, 'configuration', None)
        
        # Check notification settings once per project
        notification_enabled = True
        if config:
            notification_settings = config.notification_settings or {}
            due_date_settings = notification_settings.get('on_due_date_approaching', {})
            if isinstance(due_date_settings, dict) and not due_date_settings.get('enabled', True):
                notification_enabled = False
        
        if not notification_enabled:
            continue
        
        # Process all tasks for this project
        for task in project_tasks:
            items_checked += 1
            try:
                with transaction.atomic():
                    days_until_due = (task.due_date - today).days
                    
                    if days_until_due in [0, 1, 3]:
                        notification_service = get_notification_service(project)
                        result = notification_service.notify_due_date_approaching(
                            item=task,
                            days_until_due=days_until_due,
                            due_date=task.due_date
                        )
                        if result:
                            notifications_sent += 1
            except Exception as e:
                error_msg = f"Error processing due date notification for task {task.id}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
    
    # Check Bugs - Group by project
    bugs = Bug.objects.filter(
        due_date__isnull=False,
        due_date__gte=today,
        due_date__lte=three_days_from_now
    ).exclude(
        status__in=['resolved', 'closed', 'cancelled']
    ).select_related('project', 'assigned_to', 'project__configuration')
    
    bugs_by_project = defaultdict(list)
    for bug in bugs:
        bugs_by_project[bug.project_id].append(bug)
    
    # Process by project
    for project_id, project_bugs in bugs_by_project.items():
        project = project_bugs[0].project
        config = getattr(project, 'configuration', None)
        
        # Check notification settings once per project
        notification_enabled = True
        if config:
            notification_settings = config.notification_settings or {}
            due_date_settings = notification_settings.get('on_due_date_approaching', {})
            if isinstance(due_date_settings, dict) and not due_date_settings.get('enabled', True):
                notification_enabled = False
        
        if not notification_enabled:
            continue
        
        # Process all bugs for this project
        for bug in project_bugs:
            items_checked += 1
            try:
                with transaction.atomic():
                    days_until_due = (bug.due_date - today).days
                    
                    if days_until_due in [0, 1, 3]:
                        notification_service = get_notification_service(project)
                        result = notification_service.notify_due_date_approaching(
                            item=bug,
                            days_until_due=days_until_due,
                            due_date=bug.due_date
                        )
                        if result:
                            notifications_sent += 1
            except Exception as e:
                error_msg = f"Error processing due date notification for bug {bug.id}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
    
    # Check Issues
    issues = Issue.objects.filter(
        due_date__isnull=False,
        due_date__gte=today,
        due_date__lte=three_days_from_now
    ).exclude(
        status__in=['resolved', 'closed', 'cancelled']
    ).select_related('project', 'assigned_to', 'project__configuration')
    
    issues_by_project = defaultdict(list)
    for issue in issues:
        issues_by_project[issue.project_id].append(issue)
    
    # Process by project
    for project_id, project_issues in issues_by_project.items():
        project = project_issues[0].project
        config = getattr(project, 'configuration', None)
        
        # Check notification settings once per project
        notification_enabled = True
        if config:
            notification_settings = config.notification_settings or {}
            due_date_settings = notification_settings.get('on_due_date_approaching', {})
            if isinstance(due_date_settings, dict) and not due_date_settings.get('enabled', True):
                notification_enabled = False
        
        if not notification_enabled:
            continue
        
        # Process all issues for this project
        for issue in project_issues:
            items_checked += 1
            try:
                with transaction.atomic():
                    days_until_due = (issue.due_date - today).days
                    
                    if days_until_due in [0, 1, 3]:
                        notification_service = get_notification_service(project)
                        result = notification_service.notify_due_date_approaching(
                            item=issue,
                            days_until_due=days_until_due,
                            due_date=issue.due_date
                        )
                        if result:
                            notifications_sent += 1
            except Exception as e:
                error_msg = f"Error processing due date notification for issue {issue.id}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
    
    logger.info(
        f"Due date check task completed: {items_checked} items checked, "
        f"{notifications_sent} notifications sent, {len(errors)} errors"
    )
    return {
        'items_checked': items_checked,
        'notifications_sent': notifications_sent,
        'errors': errors
    }


@shared_task
def send_pending_email_notifications():
    """
    Send email notifications for pending notifications.
    
    This task processes notifications that have been created but not yet sent via email.
    It respects project notification settings and user preferences.
    """
    from django.utils import timezone
    from apps.projects.models import Notification, ProjectConfiguration
    from apps.projects.services.email_service import EmailService
    
    logger.info("Starting send_pending_email_notifications task")
    
    # Get notifications that need email sending
    # Only get notifications created in the last 24 hours to avoid processing old notifications
    cutoff_time = timezone.now() - timezone.timedelta(hours=24)
    
    notifications = Notification.objects.filter(
        email_sent=False,
        created_at__gte=cutoff_time
    ).select_related('recipient', 'project', 'story', 'task', 'bug', 'issue', 'epic', 'project__configuration')
    
    emails_sent = 0
    emails_failed = 0
    skipped = 0
    
    for notification in notifications:
        try:
            # Check if email notifications are enabled for this project
            if notification.project:
                try:
                    config = notification.project.configuration
                    notification_settings = config.notification_settings or {}
                    
                    # Check if email is enabled globally
                    if not notification_settings.get('email_enabled', True):
                        skipped += 1
                        continue
                    
                    # Check if this notification type has email enabled
                    event_type = f"on_{notification.notification_type}"
                    event_setting = notification_settings.get(event_type, {})
                    if isinstance(event_setting, dict) and not event_setting.get('enabled', True):
                        skipped += 1
                        continue
                except ProjectConfiguration.DoesNotExist:
                    pass  # No config, allow email by default
            
            # Send email
            if EmailService.send_notification_email(notification):
                emails_sent += 1
            else:
                emails_failed += 1
                
        except Exception as e:
            logger.error(f"Error sending email for notification {notification.id}: {str(e)}", exc_info=True)
            emails_failed += 1
    
    logger.info(
        f"Email notification task completed: {emails_sent} sent, {emails_failed} failed, {skipped} skipped"
    )
    return {
        'emails_sent': emails_sent,
        'emails_failed': emails_failed,
        'skipped': skipped
    }


@shared_task
def execute_scheduled_automation_rules():
    """
    Execute automation rules with scheduled triggers.
    
    This task runs periodically (e.g., daily) and executes automation rules
    that have scheduled triggers (e.g., daily, weekly, monthly).
    
    Scheduled triggers can be configured in automation_rules with:
    - trigger.type: 'scheduled'
    - trigger.schedule: 'daily', 'weekly', 'monthly', or cron expression
    - trigger.time: Time of day (HH:MM format) for daily/weekly schedules
    - trigger.day_of_week: Day of week (0-6, Monday=0) for weekly schedules
    - trigger.day_of_month: Day of month (1-31) for monthly schedules
    """
    from apps.projects.services.automation import AutomationService
    from datetime import datetime, time
    import pytz
    
    logger.info("Starting execute_scheduled_automation_rules task")
    
    now = timezone.now()
    current_date = now.date()
    current_time = now.time()
    current_weekday = current_date.weekday()  # 0=Monday, 6=Sunday
    current_day = current_date.day
    
    executed_count = 0
    skipped_count = 0
    errors = []
    
    # Get all projects with automation rules
    from apps.projects.models import ProjectConfiguration
    configs = ProjectConfiguration.objects.filter(
        automation_rules__isnull=False
    ).exclude(automation_rules=[]).select_related('project')
    
    for config in configs:
        if not config.automation_rules:
            continue
        
        automation_service = AutomationService(project=config.project)
        
        for rule in config.automation_rules:
            if not rule.get('enabled', True):
                continue
            
            trigger = rule.get('trigger', {})
            trigger_type = trigger.get('type')
            
            # Only process scheduled triggers
            if trigger_type != 'scheduled':
                continue
            
            schedule = trigger.get('schedule', 'daily')
            trigger_time_str = trigger.get('time', '00:00')
            
            # Parse time
            try:
                hour, minute = map(int, trigger_time_str.split(':'))
                trigger_time = time(hour, minute)
            except (ValueError, AttributeError):
                logger.warning(f"Invalid time format in scheduled trigger: {trigger_time_str}")
                continue
            
            # Check if this schedule should run now
            should_run = False
            
            if schedule == 'daily':
                # Run if current time matches trigger time (within 1 hour window)
                time_diff = abs((datetime.combine(current_date, current_time) - 
                               datetime.combine(current_date, trigger_time)).total_seconds())
                should_run = time_diff < 3600  # 1 hour window
            
            elif schedule == 'weekly':
                day_of_week = trigger.get('day_of_week', 0)  # Default Monday
                if current_weekday == day_of_week:
                    time_diff = abs((datetime.combine(current_date, current_time) - 
                                   datetime.combine(current_date, trigger_time)).total_seconds())
                    should_run = time_diff < 3600  # 1 hour window
            
            elif schedule == 'monthly':
                day_of_month = trigger.get('day_of_month', 1)  # Default 1st
                if current_day == day_of_month:
                    time_diff = abs((datetime.combine(current_date, current_time) - 
                                   datetime.combine(current_date, trigger_time)).total_seconds())
                    should_run = time_diff < 3600  # 1 hour window
            
            elif schedule.startswith('cron:'):
                # Basic cron support (simplified)
                # Format: cron:minute hour day month day_of_week
                # For now, skip complex cron parsing
                logger.debug(f"Cron schedule not fully supported: {schedule}")
                continue
            
            if should_run:
                try:
                    # Execute actions for all matching items
                    actions = rule.get('actions', [])
                    conditions = rule.get('conditions', {})
                    
                    # Get items matching conditions
                    items = automation_service._get_items_for_scheduled_rule(
                        conditions=conditions,
                        project=config.project
                    )
                    
                    for item in items:
                        for action in actions:
                            result = automation_service._execute_action(item, action, user=None)
                            if result:
                                executed_count += 1
                                logger.info(
                                    f"Executed scheduled automation rule '{rule.get('name', 'Unnamed')}' "
                                    f"on {item.__class__.__name__} {item.id}"
                                )
                except Exception as e:
                    error_msg = f"Error executing scheduled rule '{rule.get('name', 'Unnamed')}': {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)
            else:
                skipped_count += 1
    
    logger.info(
        f"Scheduled automation rules task completed: {executed_count} actions executed, "
        f"{skipped_count} skipped, {len(errors)} errors"
    )
    return {
        'executed': executed_count,
        'skipped': skipped_count,
        'errors': errors
    }

