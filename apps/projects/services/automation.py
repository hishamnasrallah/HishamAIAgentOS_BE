"""
Automation service for executing project-level automation rules.

This service processes automation_rules from ProjectConfiguration and executes
actions based on triggers (e.g., status changes, field updates, etc.).
"""

import logging
from typing import Dict, List, Any, Optional
from django.contrib.auth import get_user_model

from apps.projects.models import (
    Project,
    ProjectConfiguration,
    UserStory,
    Task,
    Bug,
    Issue,
    Sprint
)

User = get_user_model()
logger = logging.getLogger(__name__)


class AutomationService:
    """
    Service for executing automation rules defined in project configuration.
    
    Automation rules can:
    - Auto-assign based on conditions
    - Auto-update fields
    - Send notifications
    - Create related items
    - Update status based on conditions
    """
    
    def __init__(self, project: Optional[Project] = None):
        """Initialize with optional project for project-specific rules."""
        self.project = project
        self.config = None
        if project:
            try:
                self.config = project.configuration
            except ProjectConfiguration.DoesNotExist:
                logger.warning(f"No configuration found for project {project.id}")
    
    def _get_automation_rules(self) -> List[Dict[str, Any]]:
        """Get automation rules from project configuration."""
        if not self.config or not self.config.automation_rules:
            return []
        return self.config.automation_rules or []
    
    def execute_rules_for_status_change(
        self,
        item: Any,  # UserStory, Task, Bug, or Issue
        old_status: str,
        new_status: str,
        user: Optional[User] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute automation rules triggered by status changes.
        
        Args:
            item: The work item (UserStory, Task, Bug, or Issue)
            old_status: Previous status
            new_status: New status
            user: User who made the change (optional)
            
        Returns:
            List of executed actions with results
        """
        if old_status == new_status:
            return []
        
        rules = self._get_automation_rules()
        executed_actions = []
        
        for rule in rules:
            if not rule.get('enabled', True):
                continue
            
            trigger = rule.get('trigger', {})
            trigger_type = trigger.get('type')
            
            # Check if this rule applies to status change
            if trigger_type == 'status_change':
                trigger_statuses = trigger.get('statuses', [])
                trigger_from = trigger.get('from')
                trigger_to = trigger.get('to')
                
                # Check if this status change matches the trigger
                matches = False
                if trigger_from and trigger_to:
                    matches = (old_status == trigger_from and new_status == trigger_to)
                elif trigger_from:
                    matches = (old_status == trigger_from)
                elif trigger_to:
                    matches = (new_status == trigger_to)
                elif trigger_statuses:
                    matches = (old_status in trigger_statuses or new_status in trigger_statuses)
                
                if matches:
                    # Check conditions before executing actions
                    if self._evaluate_conditions(item, rule.get('conditions', [])):
                        actions = rule.get('actions', [])
                        for action in actions:
                            result = self._execute_action(item, action, user)
                            if result:
                                executed_actions.append(result)
        
        return executed_actions
    
    def execute_rules_for_field_update(
        self,
        item: Any,
        field_name: str,
        old_value: Any,
        new_value: Any,
        user: Optional[User] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute automation rules triggered by field updates.
        
        Args:
            item: The work item
            field_name: Name of the field that changed
            old_value: Previous value
            new_value: New value
            user: User who made the change (optional)
            
        Returns:
            List of executed actions with results
        """
        if old_value == new_value:
            return []
        
        rules = self._get_automation_rules()
        executed_actions = []
        
        for rule in rules:
            if not rule.get('enabled', True):
                continue
            
            trigger = rule.get('trigger', {})
            trigger_type = trigger.get('type')
            
            # Check if this rule applies to field update
            if trigger_type == 'field_update':
                trigger_field = trigger.get('field')
                trigger_conditions = trigger.get('conditions', {})
                
                if trigger_field == field_name:
                    # Check conditions
                    matches = True
                    if trigger_conditions:
                        # Check if new_value matches conditions
                        if 'equals' in trigger_conditions:
                            matches = matches and (new_value == trigger_conditions['equals'])
                        if 'not_equals' in trigger_conditions:
                            matches = matches and (new_value != trigger_conditions['not_equals'])
                        if 'contains' in trigger_conditions:
                            if isinstance(new_value, str):
                                matches = matches and (trigger_conditions['contains'] in new_value)
                    
                    if matches:
                        # Check rule-level conditions before executing actions
                        if self._evaluate_conditions(item, rule.get('conditions', [])):
                            actions = rule.get('actions', [])
                            for action in actions:
                                result = self._execute_action(item, action, user)
                                if result:
                                    executed_actions.append(result)
        
        return executed_actions
    
    def _get_items_for_scheduled_rule(
        self,
        conditions: Dict[str, Any],
        project: Project
    ) -> List[Any]:
        """
        Get items matching conditions for scheduled automation rules.
        
        Args:
            conditions: Conditions to filter items
            project: Project to get items from
            
        Returns:
            List of matching items (UserStory, Task, Bug, Issue)
        """
        items = []
        
        # Get content types to check
        content_types = conditions.get('content_types', ['userstory', 'task', 'bug', 'issue'])
        
        # Build filters from conditions
        filters = {}
        if 'status' in conditions:
            filters['status'] = conditions['status']
        if 'status__in' in conditions:
            filters['status__in'] = conditions['status__in']
        if 'assigned_to' in conditions:
            filters['assigned_to_id'] = conditions['assigned_to']
        if 'priority' in conditions:
            filters['priority'] = conditions['priority']
        if 'component' in conditions:
            filters['component'] = conditions['component']
        
        # Get items by content type
        if 'userstory' in content_types:
            stories = UserStory.objects.filter(project=project, **filters)
            items.extend(list(stories))
        
        if 'task' in content_types:
            tasks = Task.objects.filter(
                story__project=project,
                **filters
            ).select_related('story')
            items.extend(list(tasks))
        
        if 'bug' in content_types:
            bugs = Bug.objects.filter(project=project, **filters)
            items.extend(list(bugs))
        
        if 'issue' in content_types:
            issues = Issue.objects.filter(project=project, **filters)
            items.extend(list(issues))
        
        return items
    
    def _evaluate_conditions(
        self,
        item: Any,
        conditions: List[Dict[str, Any]]
    ) -> bool:
        """
        Evaluate conditions for an automation rule.
        
        Args:
            item: The work item
            conditions: List of condition dictionaries
            
        Returns:
            True if all conditions match, False otherwise
        """
        if not conditions or len(conditions) == 0:
            return True  # No conditions means always match
        
        for condition in conditions:
            field_name = condition.get('field')
            operator = condition.get('operator')
            expected_value = condition.get('value')
            
            if not field_name or not operator:
                continue  # Skip invalid conditions
            
            # Get field value from item
            field_value = None
            if hasattr(item, field_name):
                field_value = getattr(item, field_name)
            elif hasattr(item, f'{field_name}_id'):
                field_value = getattr(item, f'{field_name}_id')
            
            # Evaluate condition
            matches = False
            if operator == 'equals':
                matches = (field_value == expected_value)
            elif operator == 'not_equals':
                matches = (field_value != expected_value)
            elif operator == 'contains':
                if isinstance(field_value, str):
                    matches = (expected_value in field_value)
                elif isinstance(field_value, list):
                    matches = (expected_value in field_value)
            elif operator == 'greater_than':
                try:
                    matches = (float(field_value) > float(expected_value))
                except (ValueError, TypeError):
                    matches = False
            elif operator == 'less_than':
                try:
                    matches = (float(field_value) < float(expected_value))
                except (ValueError, TypeError):
                    matches = False
            elif operator == 'in':
                if isinstance(expected_value, list):
                    matches = (field_value in expected_value)
                elif isinstance(expected_value, str):
                    # Treat as comma-separated list
                    values = [v.strip() for v in expected_value.split(',')]
                    matches = (str(field_value) in values)
            elif operator == 'not_in':
                if isinstance(expected_value, list):
                    matches = (field_value not in expected_value)
                elif isinstance(expected_value, str):
                    values = [v.strip() for v in expected_value.split(',')]
                    matches = (str(field_value) not in values)
            
            if not matches:
                return False  # All conditions must match
        
        return True  # All conditions matched
    
    def _execute_action(
        self,
        item: Any,
        action: Dict[str, Any],
        user: Optional[User] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a single automation action.
        
        Args:
            item: The work item
            action: Action configuration
            user: User who triggered the action (optional)
            
        Returns:
            Result dictionary or None if action failed
        """
        action_type = action.get('type')
        
        try:
            if action_type == 'assign':
                return self._action_assign(item, action, user)
            elif action_type == 'update_field':
                return self._action_update_field(item, action, user)
            elif action_type == 'update_status':
                return self._action_update_status(item, action, user)
            elif action_type == 'add_label':
                return self._action_add_label(item, action, user)
            elif action_type == 'add_tag':
                return self._action_add_tag(item, action, user)
            elif action_type == 'notify':
                return self._action_notify(item, action, user)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return None
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {str(e)}", exc_info=True)
            return None
    
    def _action_assign(
        self,
        item: Any,
        action: Dict[str, Any],
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Assign item to a user."""
        assign_to = action.get('assign_to')
        if not assign_to:
            return {'type': 'assign', 'success': False, 'error': 'No assign_to specified'}
        
        # assign_to can be a user ID, email, or role
        if isinstance(assign_to, str):
            # Try to find user by email or ID
            try:
                target_user = User.objects.get(email=assign_to)
            except User.DoesNotExist:
                try:
                    target_user = User.objects.get(id=assign_to)
                except (User.DoesNotExist, ValueError):
                    return {'type': 'assign', 'success': False, 'error': f'User not found: {assign_to}'}
        else:
            target_user = assign_to
        
        item.assigned_to = target_user
        item.save(update_fields=['assigned_to', 'updated_at'])
        
        return {'type': 'assign', 'success': True, 'assigned_to': target_user.id}
    
    def _action_update_field(
        self,
        item: Any,
        action: Dict[str, Any],
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Update a field on the item."""
        field_name = action.get('field')
        field_value = action.get('value')
        
        if not field_name:
            return {'type': 'update_field', 'success': False, 'error': 'No field specified'}
        
        if not hasattr(item, field_name):
            return {'type': 'update_field', 'success': False, 'error': f'Field not found: {field_name}'}
        
        setattr(item, field_name, field_value)
        item.save(update_fields=[field_name, 'updated_at'])
        
        return {'type': 'update_field', 'success': True, 'field': field_name, 'value': field_value}
    
    def _action_update_status(
        self,
        item: Any,
        action: Dict[str, Any],
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Update item status."""
        new_status = action.get('status')
        
        if not new_status:
            return {'type': 'update_status', 'success': False, 'error': 'No status specified'}
        
        item.status = new_status
        item.save(update_fields=['status', 'updated_at'])
        
        return {'type': 'update_status', 'success': True, 'status': new_status}
    
    def _action_add_label(
        self,
        item: Any,
        action: Dict[str, Any],
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Add a label to the item."""
        label_name = action.get('label')
        label_color = action.get('color', '#808080')
        
        if not label_name:
            return {'type': 'add_label', 'success': False, 'error': 'No label specified'}
        
        # Get current labels
        labels = getattr(item, 'labels', []) or []
        if not isinstance(labels, list):
            labels = []
        
        # Check if label already exists
        if not any(l.get('name') == label_name for l in labels):
            labels.append({'name': label_name, 'color': label_color})
            item.labels = labels
            item.save(update_fields=['labels', 'updated_at'])
        
        return {'type': 'add_label', 'success': True, 'label': label_name}
    
    def _action_add_tag(
        self,
        item: Any,
        action: Dict[str, Any],
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Add a tag to the item."""
        tag = action.get('tag')
        
        if not tag:
            return {'type': 'add_tag', 'success': False, 'error': 'No tag specified'}
        
        # Get current tags
        tags = getattr(item, 'tags', []) or []
        if not isinstance(tags, list):
            tags = []
        
        # Add tag if not already present
        if tag not in tags:
            tags.append(tag)
            item.tags = tags
            item.save(update_fields=['tags', 'updated_at'])
        
        return {'type': 'add_tag', 'success': True, 'tag': tag}
    
    def _action_notify(
        self,
        item: Any,
        action: Dict[str, Any],
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """Send a notification using the notification service."""
        try:
            from apps.projects.services.notifications import NotificationService
            
            notification_type = action.get('notification_type', 'status_change')
            recipients = action.get('recipients', [])
            message = action.get('message', '')
            
            # Get project for notification settings
            project = None
            if hasattr(item, 'project'):
                project = item.project
            elif hasattr(item, 'story') and item.story:
                project = item.story.project
            
            notification_service = NotificationService(project)
            
            # Check notification settings from project configuration
            if project and self.config:
                notification_settings = self.config.notification_settings or {}
                
                # Check if email notifications are enabled
                if notification_type == 'email' and not notification_settings.get('email_enabled', True):
                    return {'type': 'notify', 'success': False, 'note': 'Email notifications disabled'}
                
                # Check if in-app notifications are enabled
                if notification_type == 'in_app' and not notification_settings.get('in_app_enabled', True):
                    return {'type': 'notify', 'success': False, 'note': 'In-app notifications disabled'}
            
            # Convert recipient IDs/emails to User objects if needed
            user_recipients = []
            for recipient in recipients:
                if isinstance(recipient, User):
                    user_recipients.append(recipient)
                elif isinstance(recipient, str):
                    # Try to find user by ID or email
                    try:
                        if '@' in recipient:
                            user_obj = User.objects.get(email=recipient)
                        else:
                            user_obj = User.objects.get(id=recipient)
                        user_recipients.append(user_obj)
                    except User.DoesNotExist:
                        logger.warning(f"Recipient not found: {recipient}")
                else:
                    logger.warning(f"Invalid recipient type: {type(recipient)}")
            
            if not user_recipients:
                return {'type': 'notify', 'success': False, 'error': 'No valid recipients'}
            
            # Send notification
            result = notification_service.send_notification(
                item=item,
                notification_type=notification_type,
                recipients=user_recipients,
                message=message,
                user=user
            )
            
            return {'type': 'notify', 'success': True, 'result': result, 'notifications_created': len(result)}
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}", exc_info=True)
            return {'type': 'notify', 'success': False, 'error': str(e)}


def execute_automation_rules(
    trigger_type: str,
    item: Any,  # UserStory, Task, Bug, or Issue
    context: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to execute automation rules for a given trigger.
    
    This function provides a simple interface for signals and other code to
    execute automation rules without needing to instantiate AutomationService.
    
    Args:
        trigger_type: Type of trigger ('on_story_create', 'on_status_change', 
                      'on_story_update', 'on_task_complete', etc.)
        item: The work item (UserStory, Task, Bug, or Issue)
        context: Optional context dictionary with additional information
                 (e.g., {'old_status': 'todo', 'new_status': 'in_progress'})
    
    Returns:
        List of executed actions with results
    """
    context = context or {}
    
    # Get project from item
    project = None
    if hasattr(item, 'project'):
        project = item.project
    elif hasattr(item, 'story') and item.story:
        project = item.story.project
    
    if not project:
        logger.warning(f"Cannot execute automation rules: item has no project")
        return []
    
    service = AutomationService(project)
    executed_actions = []
    
    try:
        if trigger_type == 'on_story_create':
            # Execute rules for story creation
            # This would need a method in AutomationService for creation triggers
            # For now, we'll check for status_change rules that trigger on creation
            rules = service._get_automation_rules()
            for rule in rules:
                if not rule.get('enabled', True):
                    continue
                trigger = rule.get('trigger', {})
                if trigger.get('type') == 'on_create':
                    # Check conditions before executing actions
                    if service._evaluate_conditions(item, rule.get('conditions', [])):
                        actions = rule.get('actions', [])
                        for action in actions:
                            result = service._execute_action(item, action, None)
                            if result:
                                executed_actions.append(result)
        
        elif trigger_type == 'on_status_change':
            # Execute rules for status change
            old_status = context.get('old_status')
            new_status = context.get('new_status')
            if old_status and new_status:
                executed_actions = service.execute_rules_for_status_change(
                    item, old_status, new_status, None
                )
        
        elif trigger_type == 'on_story_update':
            # Execute rules for story update
            # Check for field update triggers
            previous_state = context.get('previous_state', {})
            current_status = getattr(item, 'status', None)
            previous_status = previous_state.get('status')
            
            if previous_status and current_status and previous_status != current_status:
                executed_actions = service.execute_rules_for_status_change(
                    item, previous_status, current_status, None
                )
            
            # Check for assignee changes
            current_assignee = getattr(item, 'assigned_to_id', None)
            previous_assignee = previous_state.get('assigned_to')
            if previous_assignee != current_assignee:
                executed_actions.extend(service.execute_rules_for_field_update(
                    item, 'assigned_to', previous_assignee, current_assignee, None
                ))
        
        elif trigger_type == 'on_task_complete':
            # Execute rules for task completion
            task = context.get('task')
            if task and hasattr(item, 'status'):
                # Check if all tasks are complete and update story status
                rules = service._get_automation_rules()
                for rule in rules:
                    if not rule.get('enabled', True):
                        continue
                    trigger = rule.get('trigger', {})
                    if trigger.get('type') == 'on_task_complete':
                        # Check conditions before executing actions
                        if service._evaluate_conditions(item, rule.get('conditions', [])):
                            actions = rule.get('actions', [])
                            for action in actions:
                                result = service._execute_action(item, action, None)
                                if result:
                                    executed_actions.append(result)
        
        else:
            logger.warning(f"Unknown trigger type: {trigger_type}")
    
    except Exception as e:
        logger.error(f"Error executing automation rules for {trigger_type}: {str(e)}", exc_info=True)
    
    return executed_actions
