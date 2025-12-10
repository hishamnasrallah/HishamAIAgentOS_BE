"""
Auto-tagging service for automatic label/tag assignment based on rules.
"""

from typing import Dict, List, Any
from apps.projects.models import UserStory, Task, Bug, Issue


class AutoTaggingService:
    """Service for automatic tagging of work items."""
    
    @staticmethod
    def apply_auto_tagging(project_id: str, item_type: str, item_id: str):
        """Apply auto-tagging rules to an item."""
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
                return []
            
            # Get project configuration for auto-tagging rules
            from apps.projects.models import ProjectConfiguration
            try:
                config = ProjectConfiguration.objects.get(project_id=project_id)
            except ProjectConfiguration.DoesNotExist:
                return []
            
            # Get auto-tagging rules from automation_rules or separate field
            tagging_rules = getattr(config, 'auto_tagging_rules', None) or config.automation_rules.get('auto_tagging_rules', []) if isinstance(config.automation_rules, dict) else []
            applied_tags = []
            
            # Apply rules in order
            for rule in tagging_rules:
                if not rule.get('enabled', True):
                    continue
                
                # Check if rule matches
                if AutoTaggingService._rule_matches(item, rule):
                    # Apply tags
                    tags = rule.get('tags', [])
                    if tags:
                        current_tags = item.tags if isinstance(item.tags, list) else []
                        new_tags = list(set(current_tags + tags))
                        item.tags = new_tags
                        item.save(update_fields=['tags', 'updated_at'])
                        applied_tags.extend(tags)
            
            return list(set(applied_tags))
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error applying auto-tagging: {str(e)}")
            return []
    
    @staticmethod
    def _rule_matches(item: Any, rule: Dict[str, Any]) -> bool:
        """Check if an auto-tagging rule matches an item."""
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
            if not AutoTaggingService._condition_matches(field_value, operator, value):
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
                return expected_value.lower() in field_value.lower()
            return False
        elif operator == 'not_contains':
            if isinstance(field_value, list):
                return expected_value not in field_value
            if isinstance(field_value, str):
                return expected_value.lower() not in field_value.lower()
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

