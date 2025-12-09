"""
Validation rule enforcement service for project-level validation rules.

This service enforces validation rules defined in ProjectConfiguration.validation_rules,
ensuring stories and tasks meet project-specific requirements before certain actions.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from django.contrib.auth import get_user_model

from apps.projects.models import (
    Project,
    ProjectConfiguration,
    UserStory,
    Task,
    Bug,
    Issue
)

User = get_user_model()
logger = logging.getLogger(__name__)


class ValidationRuleEnforcementService:
    """
    Service for enforcing project-level validation rules.
    
    Validates:
    - Required fields before status changes
    - Story points requirements
    - Assignee requirements
    - Acceptance criteria requirements
    - Description length requirements
    - Task completion requirements
    - Sprint capacity limits
    """
    
    # Default validation rules
    DEFAULT_RULES = {
        'require_acceptance_criteria': False,
        'require_story_points_before_in_progress': False,
        'require_assignee_before_in_progress': False,
        'require_description_min_length': 0,
        'block_status_change_if_tasks_incomplete': False,
        'warn_if_story_points_exceed_sprint_capacity': True
    }
    
    def __init__(self, project: Optional[Project] = None):
        """Initialize with optional project for project-specific settings."""
        self.project = project
        self.config = None
        if project:
            try:
                self.config = project.configuration
            except ProjectConfiguration.DoesNotExist:
                logger.warning(f"No configuration found for project {project.id}")
    
    def _get_validation_rule(self, rule_key: str) -> Any:
        """Get validation rule from project config or use default."""
        if self.config and self.config.validation_rules:
            rules = self.config.validation_rules
            if rule_key in rules:
                return rules[rule_key]
        
        # Return default
        return self.DEFAULT_RULES.get(rule_key, None)
    
    def validate_story_before_status_change(
        self,
        story: UserStory,
        new_status: str,
        old_status: Optional[str] = None
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validate story before status change.
        
        Returns: (is_valid, error_message, warnings)
        """
        errors = []
        warnings = []
        
        # Check if moving to 'in_progress'
        if new_status == 'in_progress' and old_status != 'in_progress':
            # Check story points requirement
            if self._get_validation_rule('require_story_points_before_in_progress'):
                if not story.story_points or story.story_points <= 0:
                    errors.append("Story points are required before moving to 'In Progress'")
            
            # Check assignee requirement
            if self._get_validation_rule('require_assignee_before_in_progress'):
                if not story.assigned_to:
                    errors.append("An assignee is required before moving to 'In Progress'")
            
            # Check acceptance criteria requirement
            if self._get_validation_rule('require_acceptance_criteria'):
                if not story.acceptance_criteria or len(story.acceptance_criteria.strip()) == 0:
                    errors.append("Acceptance criteria are required before moving to 'In Progress'")
        
        # Check description length
        min_length = self._get_validation_rule('require_description_min_length')
        if min_length and min_length > 0:
            if not story.description or len(story.description.strip()) < min_length:
                errors.append(f"Description must be at least {min_length} characters long")
        
        # Check task completion requirement
        if self._get_validation_rule('block_status_change_if_tasks_incomplete'):
            if new_status in ['done', 'completed']:
                incomplete_tasks = story.tasks.exclude(status='done')
                if incomplete_tasks.exists():
                    errors.append("All tasks must be completed before marking story as done")
        
        # Check sprint capacity (warning only)
        if self._get_validation_rule('warn_if_story_points_exceed_sprint_capacity'):
            if story.sprint and story.story_points:
                max_points = self.config.max_story_points_per_sprint if self.config else 40
                sprint_stories = UserStory.objects.filter(sprint=story.sprint).exclude(id=story.id)
                total_points = sum(s.story_points or 0 for s in sprint_stories) + story.story_points
                
                if total_points > max_points:
                    warnings.append(
                        f"Sprint capacity exceeded: {total_points} story points "
                        f"(max: {max_points})"
                    )
        
        if errors:
            return False, '; '.join(errors), warnings
        
        return True, None, warnings
    
    def validate_story_creation(self, story_data: Dict[str, Any]) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validate story data before creation.
        
        Returns: (is_valid, error_message, warnings)
        """
        errors = []
        warnings = []
        
        # Check description length
        min_length = self._get_validation_rule('require_description_min_length')
        if min_length and min_length > 0:
            description = story_data.get('description', '')
            if not description or len(description.strip()) < min_length:
                errors.append(f"Description must be at least {min_length} characters long")
        
        # Check story points against scale
        if self.config and story_data.get('story_points') is not None:
            points = story_data['story_points']
            scale = self.config.story_point_scale or []
            if scale and points not in scale:
                errors.append(
                    f"Story points ({points}) must be one of the allowed values: {scale}"
                )
            
            # Check min story points
            min_points = self.config.min_story_points_per_story
            if min_points is not None and points < min_points:
                errors.append(
                    f"Story points ({points}) must be at least {min_points}"
                )
            
            # Check max story points
            max_points = self.config.max_story_points_per_story
            if max_points is not None and points > max_points:
                errors.append(
                    f"Story points ({points}) exceed maximum allowed ({max_points})"
                )
        
        if errors:
            return False, '; '.join(errors), warnings
        
        return True, None, warnings
    
    def validate_story_update(
        self,
        story: UserStory,
        updated_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validate story data before update.
        
        Returns: (is_valid, error_message, warnings)
        """
        errors = []
        warnings = []
        
        # Check if status is being changed
        if 'status' in updated_data:
            new_status = updated_data['status']
            old_status = story.status
            is_valid, error, warns = self.validate_story_before_status_change(
                story,
                new_status,
                old_status
            )
            if not is_valid:
                errors.append(error)
            warnings.extend(warns)
        
        # Check story points
        if 'story_points' in updated_data and self.config:
            points = updated_data['story_points']
            # Skip validation if points is None (optional field)
            if points is not None:
                scale = self.config.story_point_scale or []
                if scale and points not in scale:
                    errors.append(
                        f"Story points ({points}) must be one of the allowed values: {scale}"
                    )
                
                # Check min story points
                min_points = self.config.min_story_points_per_story
                if min_points is not None and points < min_points:
                    errors.append(
                        f"Story points ({points}) must be at least {min_points}"
                    )
                
                # Check max story points
                max_points = self.config.max_story_points_per_story
                if max_points is not None and points > max_points:
                    errors.append(
                        f"Story points ({points}) exceed maximum allowed ({max_points})"
                    )
        
        # Check description length if being updated
        if 'description' in updated_data:
            min_length = self._get_validation_rule('require_description_min_length')
            if min_length and min_length > 0:
                description = updated_data['description']
                if not description or len(description.strip()) < min_length:
                    errors.append(f"Description must be at least {min_length} characters long")
        
        if errors:
            return False, '; '.join(errors), warnings
        
        return True, None, warnings
    
    def validate_sprint_capacity(
        self,
        sprint,
        story_points: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if adding story points to sprint would exceed capacity.
        
        Returns: (is_valid, error_message)
        """
        if not self.config:
            return True, None
        
        max_points = self.config.max_story_points_per_sprint
        allow_overcommitment = self.config.allow_overcommitment
        
        # Get current sprint points
        sprint_stories = UserStory.objects.filter(sprint=sprint)
        current_points = sum(s.story_points or 0 for s in sprint_stories)
        total_points = current_points + story_points
        
        if total_points > max_points:
            if allow_overcommitment:
                return True, f"Warning: Sprint capacity exceeded ({total_points}/{max_points})"
            else:
                return False, f"Sprint capacity exceeded: {total_points} story points (max: {max_points})"
        
        return True, None
    
    def validate_bug_before_status_change(
        self,
        bug: Bug,
        new_status: str,
        old_status: Optional[str] = None
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validate bug before status change.
        
        Returns: (is_valid, error_message, warnings)
        """
        errors = []
        warnings = []
        
        # Check if moving to 'in_progress'
        if new_status == 'in_progress' and old_status != 'in_progress':
            # Check assignee requirement
            if self._get_validation_rule('require_assignee_before_in_progress'):
                if not bug.assigned_to:
                    errors.append("An assignee is required before moving to 'In Progress'")
        
        # Check description length
        min_length = self._get_validation_rule('require_description_min_length')
        if min_length and min_length > 0:
            if not bug.description or len(bug.description.strip()) < min_length:
                errors.append(f"Description must be at least {min_length} characters long")
        
        if errors:
            return False, '; '.join(errors), warnings
        
        return True, None, warnings
    
    def validate_issue_before_status_change(
        self,
        issue: Issue,
        new_status: str,
        old_status: Optional[str] = None
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validate issue before status change.
        
        Returns: (is_valid, error_message, warnings)
        """
        errors = []
        warnings = []
        
        # Check if moving to 'in_progress'
        if new_status == 'in_progress' and old_status != 'in_progress':
            # Check assignee requirement
            if self._get_validation_rule('require_assignee_before_in_progress'):
                if not issue.assigned_to:
                    errors.append("An assignee is required before moving to 'In Progress'")
        
        # Check description length
        min_length = self._get_validation_rule('require_description_min_length')
        if min_length and min_length > 0:
            if not issue.description or len(issue.description.strip()) < min_length:
                errors.append(f"Description must be at least {min_length} characters long")
        
        if errors:
            return False, '; '.join(errors), warnings
        
        return True, None, warnings
    
    def validate_task_before_status_change(
        self,
        task: Task,
        new_status: str,
        old_status: Optional[str] = None
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validate task before status change.
        
        Returns: (is_valid, error_message, warnings)
        """
        errors = []
        warnings = []
        
        # Check if moving to 'in_progress'
        if new_status == 'in_progress' and old_status != 'in_progress':
            # Check assignee requirement
            if self._get_validation_rule('require_assignee_before_in_progress'):
                if not task.assigned_to:
                    errors.append("An assignee is required before moving to 'In Progress'")
        
        # Check description length
        min_length = self._get_validation_rule('require_description_min_length')
        if min_length and min_length > 0:
            if not task.description or len(task.description.strip()) < min_length:
                errors.append(f"Description must be at least {min_length} characters long")
        
        if errors:
            return False, '; '.join(errors), warnings
        
        return True, None, warnings


def get_validation_service(project: Optional[Project] = None) -> ValidationRuleEnforcementService:
    """Convenience function to get a ValidationRuleEnforcementService instance."""
    return ValidationRuleEnforcementService(project)

