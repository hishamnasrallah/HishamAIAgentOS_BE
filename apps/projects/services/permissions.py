"""
Permission enforcement service for project-level permissions.

This service enforces permissions based on ProjectConfiguration.permission_settings,
which allows projects to override default permissions with custom rules.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from django.contrib.auth import get_user_model

from apps.projects.models import (
    Project,
    ProjectConfiguration,
    UserStory,
    Epic,
    Sprint,
    Task
)

User = get_user_model()
logger = logging.getLogger(__name__)


class PermissionEnforcementService:
    """
    Service for enforcing project-level permissions.
    
    Checks permissions based on:
    1. Project configuration permission_settings
    2. User role (admin, manager, developer, viewer)
    3. Project membership (owner, member)
    4. Approval requirements
    """
    
    # Default permission mappings
    DEFAULT_PERMISSIONS = {
        'who_can_create_stories': ['member', 'admin'],
        'who_can_edit_stories': ['member', 'admin'],
        'who_can_delete_stories': ['admin'],
        'who_can_assign_stories': ['member', 'admin'],
        'who_can_change_status': ['member', 'admin'],
        'who_can_manage_sprints': ['admin', 'scrum_master'],
        'who_can_view_analytics': ['member', 'admin'],
        'who_can_create_epics': ['member', 'admin'],
        'who_can_edit_epics': ['member', 'admin'],
        'who_can_delete_epics': ['admin'],
        'who_can_create_issues': ['member', 'admin'],
        'who_can_create_tasks': ['member', 'admin'],
        'who_can_edit_tasks': ['member', 'admin'],
        'who_can_delete_tasks': ['member', 'admin'],
        'who_can_add_comments': ['member', 'admin'],
        'who_can_add_attachments': ['member', 'admin'],
        'who_can_manage_dependencies': ['member', 'admin'],
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
    
    def _get_permission_setting(self, permission_key: str) -> List[str]:
        """Get permission setting from project config or use default."""
        if self.config and self.config.permission_settings:
            settings = self.config.permission_settings
            if permission_key in settings:
                return settings[permission_key]
        
        # Return default
        return self.DEFAULT_PERMISSIONS.get(permission_key, [])
    
    def _get_user_role_in_project(self, user: User) -> str:
        """
        Get user's role in the project.
        
        Returns: 'admin', 'owner', 'member', or 'viewer'
        """
        if not self.project:
            return user.role if hasattr(user, 'role') else 'viewer'
        
        # System admins have admin role
        if user.role == 'admin':
            return 'admin'
        
        # Project owner
        if self.project.owner == user:
            return 'owner'
        
        # Project member
        if self.project.members.filter(id=user.id).exists():
            return 'member'
        
        # Default to viewer
        return 'viewer'
    
    def _check_role_permission(
        self,
        user: User,
        allowed_roles: List[str]
    ) -> bool:
        """
        Check if user's role in project matches allowed roles.
        
        Role mapping:
        - 'admin' -> system admin
        - 'owner' -> project owner
        - 'member' -> project member
        - 'scrum_master' -> project member with special role (future)
        - 'viewer' -> no special access
        """
        user_role = self._get_user_role_in_project(user)
        
        # Admin always has access
        if user_role == 'admin':
            return True
        
        # Check if user role is in allowed roles
        role_mapping = {
            'admin': ['admin'],
            'owner': ['owner', 'admin'],
            'member': ['member', 'owner', 'admin'],
            'scrum_master': ['scrum_master', 'admin'],
            'viewer': ['viewer']
        }
        
        # Check if any of the user's roles match allowed roles
        user_roles = role_mapping.get(user_role, [user_role])
        return any(role in allowed_roles for role in user_roles)
    
    def can_create_story(self, user: User) -> Tuple[bool, Optional[str]]:
        """Check if user can create stories."""
        allowed_roles = self._get_permission_setting('who_can_create_stories')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can create stories"
        return True, None
    
    def can_edit_story(self, user: User, story: Optional[UserStory] = None) -> Tuple[bool, Optional[str]]:
        """Check if user can edit stories."""
        allowed_roles = self._get_permission_setting('who_can_edit_stories')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can edit stories"
        
        # Additional check: story author can always edit their own story
        if story and story.created_by == user:
            return True, None
        
        return True, None
    
    def can_delete_story(self, user: User, story: Optional[UserStory] = None) -> Tuple[bool, Optional[str]]:
        """Check if user can delete stories."""
        allowed_roles = self._get_permission_setting('who_can_delete_stories')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can delete stories"
        return True, None
    
    def can_assign_story(self, user: User) -> Tuple[bool, Optional[str]]:
        """Check if user can assign stories."""
        allowed_roles = self._get_permission_setting('who_can_assign_stories')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can assign stories"
        return True, None
    
    def can_change_status(self, user: User, story: Optional[UserStory] = None) -> Tuple[bool, Optional[str]]:
        """Check if user can change story status."""
        allowed_roles = self._get_permission_setting('who_can_change_status')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can change story status"
        
        # Check if approval is required
        if self._requires_approval('status_change_to_done', story):
            # Check if user has approval (future: implement approval system)
            # For now, just check if user is admin/owner
            user_role = self._get_user_role_in_project(user)
            if user_role not in ['admin', 'owner']:
                return False, "Status change to 'done' requires approval"
        
        return True, None
    
    def can_manage_sprints(self, user: User) -> Tuple[bool, Optional[str]]:
        """Check if user can manage sprints."""
        allowed_roles = self._get_permission_setting('who_can_manage_sprints')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can manage sprints"
        return True, None
    
    def can_view_analytics(self, user: User) -> Tuple[bool, Optional[str]]:
        """Check if user can view analytics."""
        allowed_roles = self._get_permission_setting('who_can_view_analytics')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can view analytics"
        return True, None
    
    def can_create_epic(self, user: User) -> Tuple[bool, Optional[str]]:
        """Check if user can create epics."""
        allowed_roles = self._get_permission_setting('who_can_create_epics')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can create epics"
        return True, None
    
    def can_create_issue(self, user: User) -> Tuple[bool, Optional[str]]:
        """Check if user can create issues."""
        # Use same permissions as creating stories by default
        allowed_roles = self._get_permission_setting('who_can_create_stories')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can create issues"
        return True, None
    
    def can_edit_epic(self, user: User, epic: Optional[Epic] = None) -> Tuple[bool, Optional[str]]:
        """Check if user can edit epics."""
        allowed_roles = self._get_permission_setting('who_can_edit_epics')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can edit epics"
        return True, None
    
    def can_delete_epic(self, user: User) -> Tuple[bool, Optional[str]]:
        """Check if user can delete epics."""
        allowed_roles = self._get_permission_setting('who_can_delete_epics')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can delete epics"
        return True, None
    
    def can_add_comment(self, user: User) -> Tuple[bool, Optional[str]]:
        """Check if user can add comments."""
        allowed_roles = self._get_permission_setting('who_can_add_comments')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can add comments"
        return True, None
    
    def can_add_attachment(self, user: User) -> Tuple[bool, Optional[str]]:
        """Check if user can add attachments."""
        allowed_roles = self._get_permission_setting('who_can_add_attachments')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can add attachments"
        return True, None
    
    def can_manage_dependencies(self, user: User) -> Tuple[bool, Optional[str]]:
        """Check if user can manage dependencies."""
        allowed_roles = self._get_permission_setting('who_can_manage_dependencies')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can manage dependencies"
        return True, None
    
    def _requires_approval(self, action: str, obj: Optional[Any] = None) -> bool:
        """Check if an action requires approval."""
        if not self.config or not self.config.permission_settings:
            return False
        
        approval_required = self.config.permission_settings.get('require_approval_for', [])
        return action in approval_required
    
    def requires_approval_for_status_change(self, story: Optional[UserStory] = None) -> bool:
        """Check if status change requires approval."""
        if story and story.status == 'done':
            return self._requires_approval('status_change_to_done', story)
        return False
    
    def requires_approval_for_deletion(self, obj: Optional[Any] = None) -> bool:
        """Check if deletion requires approval."""
        return self._requires_approval('story_deletion', obj)


def get_permission_service(project: Optional[Project] = None) -> PermissionEnforcementService:
    """Convenience function to get a PermissionEnforcementService instance."""
    return PermissionEnforcementService(project)

