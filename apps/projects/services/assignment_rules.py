"""
Assignment rules service for automatic story/task assignment.
"""

from django.db.models import Q
from typing import Dict, List, Any, Optional
from apps.projects.models import UserStory, Task, Bug, Issue, Project
from apps.authentication.models import User


class AssignmentRulesService:
    """Service for managing and applying assignment rules."""
    
    @staticmethod
    def apply_assignment_rules(project_id: str, item_type: str, item_id: str):
        """Apply assignment rules to an item."""
        try:
            if item_type == 'story':
                item = UserStory.objects.get(id=item_id, project_id=project_id)
            elif item_type == 'task':
                item = Task.objects.get(id=item_id, project_id=project_id)
            elif item_type == 'bug':
                item = Bug.objects.get(id=item_id, project_id=project_id)
            elif item_type == 'issue':
                item = Issue.objects.get(id=item_id, project_id=project_id)
            else:
                return None
            
            project = item.project
            
            # Get project configuration for assignment rules
            from apps.projects.models import ProjectConfiguration
            try:
                config = ProjectConfiguration.objects.get(project_id=project_id)
            except ProjectConfiguration.DoesNotExist:
                return None
            
            # Get assignment rules from automation_rules or separate field
            assignment_rules = getattr(config, 'assignment_rules', None) or config.automation_rules.get('assignment_rules', []) if isinstance(config.automation_rules, dict) else []
            
            # Apply rules in order
            for rule in assignment_rules:
                if not rule.get('enabled', True):
                    continue
                
                # Check if rule matches
                if AssignmentRulesService._rule_matches(item, rule):
                    # Apply assignment
                    assignee_id = rule.get('assignee_id')
                    if assignee_id:
                        try:
                            assignee = User.objects.get(id=assignee_id)
                            item.assigned_to = assignee
                            item.save(update_fields=['assigned_to', 'updated_at'])
                            return assignee
                        except User.DoesNotExist:
                            continue
            
            return None
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error applying assignment rules: {str(e)}")
            return None
    
    @staticmethod
    def _rule_matches(item: Any, rule: Dict[str, Any]) -> bool:
        """Check if an assignment rule matches an item."""
        conditions = rule.get('conditions', [])
        
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if not field or not operator:
                continue
            
            # Get field value
            field_value = getattr(item, field, None)
            
            # Apply operator
            if not AssignmentRulesService._condition_matches(field_value, operator, value):
                return False
        
        return True
    
    @staticmethod
    def _condition_matches(field_value: Any, operator: str, expected_value: Any) -> bool:
        """Check if a condition matches."""
        if operator == 'equals':
            return field_value == expected_value
        elif operator == 'not_equals':
            return field_value != expected_value
        elif operator == 'contains':
            if isinstance(field_value, list):
                return expected_value in field_value
            if isinstance(field_value, str):
                return expected_value in field_value
            return False
        elif operator == 'not_contains':
            if isinstance(field_value, list):
                return expected_value not in field_value
            if isinstance(field_value, str):
                return expected_value not in field_value
            return True
        elif operator == 'is_null':
            return field_value is None or field_value == ''
        elif operator == 'is_not_null':
            return field_value is not None and field_value != ''
        elif operator == 'greater_than':
            return field_value > expected_value if field_value is not None else False
        elif operator == 'less_than':
            return field_value < expected_value if field_value is not None else False
        
        return False

