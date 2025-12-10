"""
Utility for generating unique work item numbers.

Handles auto-incrementing numbers for Stories, Tasks, Bugs, Issues, and Epics
based on project-specific prefixes.
"""

from django.db import transaction
from django.db.models import Max
from apps.projects.models import UserStory, Task, Bug, Issue, Epic, ProjectConfiguration
import logging

logger = logging.getLogger(__name__)


def get_next_work_item_number(project_id: str, item_type: str, prefix: str = None) -> str:
    """
    Generate the next work item number for a project.
    
    Args:
        project_id: UUID of the project
        item_type: Type of work item ('story', 'task', 'bug', 'issue', 'epic')
        prefix: Optional custom prefix (will use project config if not provided)
    
    Returns:
        str: Formatted work item number (e.g., "STORY-123")
    """
    # Get prefix from project configuration if not provided
    if not prefix:
        try:
            config = ProjectConfiguration.objects.get(project_id=project_id)
            prefix_map = {
                'story': getattr(config, 'story_prefix', None) or 'STORY-',
                'task': getattr(config, 'task_prefix', None) or 'TASK-',
                'bug': getattr(config, 'bug_prefix', None) or 'BUG-',
                'issue': getattr(config, 'issue_prefix', None) or 'ISSUE-',
                'epic': getattr(config, 'epic_prefix', None) or 'EPIC-',
            }
            prefix = prefix_map.get(item_type, f'{item_type.upper()}-')
            logger.info(f"Using prefix '{prefix}' for {item_type} in project {project_id}")
        except ProjectConfiguration.DoesNotExist:
            prefix = f'{item_type.upper()}-'
            logger.warning(f"No configuration found for project {project_id}, using default prefix: {prefix}")
    
    # Use database transaction for atomicity
    with transaction.atomic():
        # Get the model class
        model_map = {
            'story': UserStory,
            'task': Task,
            'bug': Bug,
            'issue': Issue,
            'epic': Epic,
        }
        model = model_map.get(item_type)
        
        if not model:
            raise ValueError(f"Invalid item type: {item_type}")
        
        # Find the highest number for this project and type
        # Parse existing numbers to find the max numeric value
        if item_type == 'task':
            existing_numbers = model.objects.filter(
                story__project_id=project_id,
                number__startswith=prefix
            ).values_list('number', flat=True)
        else:
            existing_numbers = model.objects.filter(
                project_id=project_id,
                number__startswith=prefix
            ).values_list('number', flat=True)
        
        max_number = 0
        for num_str in existing_numbers:
            try:
                # Extract numeric part after prefix
                numeric_part = num_str.replace(prefix, '').split('-')[0]
                number = int(numeric_part)
                if number > max_number:
                    max_number = number
            except (ValueError, IndexError):
                continue
        
        # Generate next number
        next_number = max_number + 1
        result = f"{prefix}{next_number}"
        logger.info(f"Generated work item number: {result} (type: {item_type}, project: {project_id})")
        return result


def validate_work_item_number(project_id: str, item_type: str, number: str, current_id: str = None) -> tuple[bool, str]:
    """
    Validate that a work item number is unique within the project.
    
    Args:
        project_id: UUID of the project
        item_type: Type of work item
        number: The number to validate
        current_id: ID of current item (for updates, to exclude self)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not number:
        return True, ""  # Empty is OK (will be auto-generated)
    
    # Get the model class
    model_map = {
        'story': UserStory,
        'task': Task,
        'bug': Bug,
        'issue': Issue,
        'epic': Epic,
    }
    model = model_map.get(item_type)
    
    if not model:
        return False, f"Invalid item type: {item_type}"
    
    # Check for duplicates in the same project
    filter_kwargs = {'number': number}
    if item_type == 'task':
        filter_kwargs['story__project_id'] = project_id
    else:
        filter_kwargs['project_id'] = project_id
    
    existing = model.objects.filter(**filter_kwargs)
    
    # Exclude current item if updating
    if current_id:
        existing = existing.exclude(id=current_id)
    
    if existing.exists():
        return False, f"Work item number '{number}' already exists in this project"
    
    return True, ""


def format_work_item_number(number: int, prefix: str) -> str:
    """
    Format a work item number with prefix.
    
    Args:
        number: Numeric part
        prefix: Prefix string
    
    Returns:
        str: Formatted number (e.g., "STORY-123")
    """
    return f"{prefix}{number}"

