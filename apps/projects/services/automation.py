"""
Automation rule execution engine for project workflows.

This service evaluates and executes automation rules defined in ProjectConfiguration
when story/task events occur (create, update, status change, etc.).
"""

import logging
from typing import Dict, List, Any, Optional
from django.db import transaction
from django.utils import timezone

from apps.projects.models import (
    ProjectConfiguration,
    UserStory,
    Task,
    Epic,
    Sprint
)

logger = logging.getLogger(__name__)


class AutomationEngine:
    """
    Engine for executing automation rules.
    
    Automation rules are stored in ProjectConfiguration.automation_rules as a list of rule objects.
    Each rule has the structure:
    {
        "id": "unique_id",
        "name": "Rule Name",
        "enabled": true,
        "trigger": "on_story_create" | "on_story_update" | "on_status_change" | "on_task_complete" | etc.,
        "conditions": [
            {"field": "status", "operator": "equals", "value": "todo"},
            {"field": "priority", "operator": "equals", "value": "high"}
        ],
        "actions": [
            {"type": "set_status", "value": "in_progress"},
            {"type": "assign_to", "value": "user_id"},
            {"type": "add_tag", "value": "urgent"},
            {"type": "set_field", "field": "priority", "value": "critical"}
        ]
    }
    """
    
    def __init__(self, project_config: ProjectConfiguration):
        """Initialize with project configuration."""
        self.config = project_config
        self.rules = project_config.automation_rules or []
    
    def execute_on_story_create(self, story: UserStory) -> List[Dict[str, Any]]:
        """Execute automation rules when a story is created."""
        return self._execute_rules(
            trigger='on_story_create',
            story=story,
            previous_data=None
        )
    
    def execute_on_story_update(
        self, 
        story: UserStory, 
        previous_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute automation rules when a story is updated."""
        return self._execute_rules(
            trigger='on_story_update',
            story=story,
            previous_data=previous_data
        )
    
    def execute_on_status_change(
        self, 
        story: UserStory, 
        old_status: str, 
        new_status: str
    ) -> List[Dict[str, Any]]:
        """Execute automation rules when story status changes."""
        previous_data = {'status': old_status} if old_status else None
        return self._execute_rules(
            trigger='on_status_change',
            story=story,
            previous_data=previous_data,
            context={'old_status': old_status, 'new_status': new_status}
        )
    
    def execute_on_task_complete(self, task: Task, story: UserStory) -> List[Dict[str, Any]]:
        """Execute automation rules when a task is completed."""
        return self._execute_rules(
            trigger='on_task_complete',
            story=story,
            previous_data=None,
            context={'task': task}
        )
    
    def _execute_rules(
        self,
        trigger: str,
        story: UserStory,
        previous_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute all rules matching the trigger and conditions.
        
        Returns a list of execution results, each containing:
        {
            "rule_id": "rule_id",
            "rule_name": "Rule Name",
            "executed": true/false,
            "actions_applied": [...],
            "error": "error message" (if any)
        }
        """
        results = []
        context = context or {}
        
        # Filter rules by trigger and enabled status
        matching_rules = [
            rule for rule in self.rules
            if rule.get('enabled', True) and rule.get('trigger') == trigger
        ]
        
        if not matching_rules:
            return results
        
        for rule in matching_rules:
            try:
                # Check if conditions are met
                if not self._evaluate_conditions(rule.get('conditions', []), story, previous_data, context):
                    results.append({
                        'rule_id': rule.get('id'),
                        'rule_name': rule.get('name', 'Unnamed Rule'),
                        'executed': False,
                        'reason': 'Conditions not met',
                        'actions_applied': []
                    })
                    continue
                
                # Execute actions
                actions_applied = self._execute_actions(
                    rule.get('actions', []),
                    story,
                    context
                )
                
                results.append({
                    'rule_id': rule.get('id'),
                    'rule_name': rule.get('name', 'Unnamed Rule'),
                    'executed': True,
                    'actions_applied': actions_applied
                })
                
                logger.info(
                    f"Automation rule '{rule.get('name')}' executed on story {story.id}. "
                    f"Actions applied: {len(actions_applied)}"
                )
                
            except Exception as e:
                logger.error(
                    f"Error executing automation rule '{rule.get('name', 'Unknown')}': {e}",
                    exc_info=True
                )
                results.append({
                    'rule_id': rule.get('id'),
                    'rule_name': rule.get('name', 'Unnamed Rule'),
                    'executed': False,
                    'error': str(e),
                    'actions_applied': []
                })
        
        return results
    
    def _evaluate_conditions(
        self,
        conditions: List[Dict[str, Any]],
        story: UserStory,
        previous_data: Optional[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate if all conditions are met.
        
        Conditions are AND-ed together (all must be true).
        """
        if not conditions:
            return True  # No conditions means always execute
        
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator', 'equals')
            value = condition.get('value')
            
            if not field:
                continue
            
            # Get current field value
            current_value = self._get_field_value(story, field, context)
            
            # Evaluate condition
            if not self._evaluate_condition(current_value, operator, value):
                return False
        
        return True
    
    def _get_field_value(
        self,
        story: UserStory,
        field: str,
        context: Dict[str, Any]
    ) -> Any:
        """Get the value of a field from story or context."""
        # Handle nested fields (e.g., "epic.title")
        if '.' in field:
            parts = field.split('.')
            obj = story
            for part in parts:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                elif isinstance(obj, dict):
                    obj = obj.get(part)
                else:
                    return None
            return obj
        
        # Direct field access
        if hasattr(story, field):
            return getattr(story, field)
        
        # Context values
        if field in context:
            return context[field]
        
        # Special fields
        if field == 'has_tasks':
            return story.tasks.exists()
        
        if field == 'all_tasks_complete':
            tasks = story.tasks.all()
            return tasks.exists() and all(task.status == 'done' for task in tasks)
        
        if field == 'has_unresolved_dependencies':
            from apps.projects.models import StoryDependency
            return StoryDependency.objects.filter(
                source_story=story,
                resolved=False
            ).exists()
        
        return None
    
    def _evaluate_condition(self, current_value: Any, operator: str, expected_value: Any) -> bool:
        """Evaluate a single condition."""
        if operator == 'equals':
            return current_value == expected_value
        elif operator == 'not_equals':
            return current_value != expected_value
        elif operator == 'contains':
            if isinstance(current_value, (list, str)):
                return expected_value in current_value
            return False
        elif operator == 'not_contains':
            if isinstance(current_value, (list, str)):
                return expected_value not in current_value
            return True
        elif operator == 'in':
            if isinstance(expected_value, list):
                return current_value in expected_value
            return False
        elif operator == 'not_in':
            if isinstance(expected_value, list):
                return current_value not in expected_value
            return True
        elif operator == 'greater_than':
            try:
                return float(current_value) > float(expected_value)
            except (ValueError, TypeError):
                return False
        elif operator == 'less_than':
            try:
                return float(current_value) < float(expected_value)
            except (ValueError, TypeError):
                return False
        elif operator == 'is_empty':
            return not current_value or (isinstance(current_value, (list, str)) and len(current_value) == 0)
        elif operator == 'is_not_empty':
            return current_value and (not isinstance(current_value, (list, str)) or len(current_value) > 0)
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    @transaction.atomic
    def _execute_actions(
        self,
        actions: List[Dict[str, Any]],
        story: UserStory,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute a list of actions on a story.
        
        Returns a list of applied actions with their results.
        """
        applied = []
        
        for action in actions:
            action_type = action.get('type')
            if not action_type:
                continue
            
            try:
                result = self._execute_action(action, story, context)
                applied.append({
                    'type': action_type,
                    'success': result.get('success', False),
                    'message': result.get('message', ''),
                    'value': action.get('value')
                })
            except Exception as e:
                logger.error(f"Error executing action {action_type}: {e}", exc_info=True)
                applied.append({
                    'type': action_type,
                    'success': False,
                    'error': str(e),
                    'value': action.get('value')
                })
        
        # Save story if any actions were applied
        if applied:
            story.save()
        
        return applied
    
    def _execute_action(
        self,
        action: Dict[str, Any],
        story: UserStory,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single action."""
        action_type = action.get('type')
        value = action.get('value')
        
        if action_type == 'set_status':
            story.status = value
            return {'success': True, 'message': f'Status set to {value}'}
        
        elif action_type == 'assign_to':
            from apps.authentication.models import User
            try:
                if isinstance(value, str):
                    user = User.objects.get(id=value)
                else:
                    user = User.objects.get(id=value)
                story.assigned_to = user
                return {'success': True, 'message': f'Assigned to {user.email}'}
            except User.DoesNotExist:
                return {'success': False, 'message': f'User {value} not found'}
        
        elif action_type == 'add_tag':
            tags = story.tags or []
            if value not in tags:
                tags.append(value)
                story.tags = tags
                return {'success': True, 'message': f'Tag {value} added'}
            return {'success': True, 'message': f'Tag {value} already exists'}
        
        elif action_type == 'remove_tag':
            tags = story.tags or []
            if value in tags:
                tags.remove(value)
                story.tags = tags
                return {'success': True, 'message': f'Tag {value} removed'}
            return {'success': True, 'message': f'Tag {value} not found'}
        
        elif action_type == 'set_field':
            field = action.get('field')
            if field and hasattr(story, field):
                setattr(story, field, value)
                return {'success': True, 'message': f'Field {field} set to {value}'}
            return {'success': False, 'message': f'Field {field} not found or not settable'}
        
        elif action_type == 'add_to_sprint':
            try:
                sprint = Sprint.objects.get(id=value, project=story.project)
                story.sprint = sprint
                return {'success': True, 'message': f'Added to sprint {sprint.name}'}
            except Sprint.DoesNotExist:
                return {'success': False, 'message': f'Sprint {value} not found'}
        
        elif action_type == 'set_priority':
            if value in ['low', 'medium', 'high', 'critical']:
                story.priority = value
                return {'success': True, 'message': f'Priority set to {value}'}
            return {'success': False, 'message': f'Invalid priority: {value}'}
        
        elif action_type == 'set_story_points':
            try:
                points = int(value)
                story.story_points = points
                return {'success': True, 'message': f'Story points set to {points}'}
            except (ValueError, TypeError):
                return {'success': False, 'message': f'Invalid story points: {value}'}
        
        elif action_type == 'notify_users':
            # Trigger notifications via notification service
            try:
                from .notifications import get_notification_service
                notification_service = get_notification_service(story.project)
                
                # value can be a list of user IDs or 'all'
                if value == 'all' or value is None:
                    # Notify all relevant users (assignee, watchers, etc.)
                    notifications = notification_service.notify_automation_triggered(
                        story,
                        context.get('rule_name', 'Unknown Rule'),
                        [{'type': action_type, 'value': value}]
                    )
                    return {'success': True, 'message': f'{len(notifications)} notifications sent'}
                else:
                    # Notify specific users
                    from apps.authentication.models import User
                    if isinstance(value, list):
                        users = User.objects.filter(id__in=value)
                    else:
                        users = [User.objects.get(id=value)]
                    
                    notifications = []
                    for user in users:
                        notif = notification_service.notify_automation_triggered(
                            story,
                            context.get('rule_name', 'Unknown Rule'),
                            [{'type': action_type, 'value': str(user.id)}]
                        )
                        notifications.extend(notif)
                    
                    return {'success': True, 'message': f'{len(notifications)} notifications sent'}
            except Exception as e:
                logger.error(f"Error sending automation notification: {e}", exc_info=True)
                return {'success': False, 'message': f'Error sending notification: {str(e)}'}
        
        else:
            logger.warning(f"Unknown action type: {action_type}")
            return {'success': False, 'message': f'Unknown action type: {action_type}'}


def execute_automation_rules(
    trigger: str,
    story: UserStory,
    previous_data: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to execute automation rules for a story.
    
    Usage:
        execute_automation_rules('on_story_create', story)
        execute_automation_rules('on_status_change', story, context={'old_status': 'todo', 'new_status': 'in_progress'})
    """
    try:
        config = story.project.configuration
        engine = AutomationEngine(config)
        
        if trigger == 'on_story_create':
            return engine.execute_on_story_create(story)
        elif trigger == 'on_story_update':
            return engine.execute_on_story_update(story, previous_data)
        elif trigger == 'on_status_change':
            old_status = context.get('old_status') if context else None
            new_status = context.get('new_status') if context else None
            return engine.execute_on_status_change(story, old_status, new_status)
        else:
            return engine._execute_rules(trigger, story, previous_data, context or {})
    except ProjectConfiguration.DoesNotExist:
        logger.warning(f"No configuration found for project {story.project.id}")
        return []
    except Exception as e:
        logger.error(f"Error executing automation rules: {e}", exc_info=True)
        return []

