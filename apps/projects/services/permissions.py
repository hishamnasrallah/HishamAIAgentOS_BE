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
    Task,
    ProjectMember
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
    # Supports all system roles: admin, owner, product_owner, scrum_master, tech_lead, developer, qa, designer, analyst, manager, member, viewer
    # Plus any custom roles defined per project
    DEFAULT_PERMISSIONS = {
        'who_can_create_stories': ['developer', 'product_owner', 'scrum_master', 'manager', 'member', 'admin', 'owner'],
        'who_can_edit_stories': ['developer', 'product_owner', 'scrum_master', 'manager', 'member', 'admin', 'owner'],
        'who_can_delete_stories': ['admin', 'owner', 'product_owner'],
        'who_can_assign_stories': ['product_owner', 'scrum_master', 'tech_lead', 'manager', 'admin', 'owner'],
        'who_can_change_status': ['developer', 'product_owner', 'scrum_master', 'tech_lead', 'manager', 'member', 'admin', 'owner'],
        'who_can_manage_sprints': ['admin', 'owner', 'scrum_master', 'product_owner'],
        'who_can_view_analytics': ['product_owner', 'scrum_master', 'manager', 'tech_lead', 'member', 'admin', 'owner'],
        'who_can_create_epics': ['product_owner', 'scrum_master', 'manager', 'admin', 'owner'],
        'who_can_edit_epics': ['product_owner', 'scrum_master', 'manager', 'admin', 'owner'],
        'who_can_delete_epics': ['admin', 'owner', 'product_owner'],
        'who_can_create_issues': ['developer', 'qa', 'product_owner', 'scrum_master', 'manager', 'member', 'admin', 'owner'],
        'who_can_create_tasks': ['developer', 'product_owner', 'scrum_master', 'tech_lead', 'manager', 'member', 'admin', 'owner'],
        'who_can_edit_tasks': ['developer', 'product_owner', 'scrum_master', 'tech_lead', 'manager', 'member', 'admin', 'owner'],
        'who_can_delete_tasks': ['developer', 'tech_lead', 'scrum_master', 'manager', 'admin', 'owner'],
        'who_can_add_comments': ['developer', 'qa', 'designer', 'analyst', 'product_owner', 'scrum_master', 'tech_lead', 'manager', 'member', 'admin', 'owner'],
        'who_can_add_attachments': ['developer', 'qa', 'designer', 'analyst', 'product_owner', 'scrum_master', 'tech_lead', 'manager', 'member', 'admin', 'owner'],
        'who_can_manage_dependencies': ['developer', 'product_owner', 'scrum_master', 'tech_lead', 'manager', 'admin', 'owner'],
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
                allowed_roles = settings[permission_key]
                # Validate that all roles exist (system roles or custom roles)
                if isinstance(allowed_roles, list):
                    valid_roles = []
                    system_roles = ProjectMember.SYSTEM_ROLES
                    custom_roles = self.config.custom_roles if self.config.custom_roles else []
                    all_valid_roles = system_roles + custom_roles
                    
                    for role in allowed_roles:
                        if role in all_valid_roles:
                            valid_roles.append(role)
                        else:
                            logger.warning(f"Invalid role '{role}' in permission setting '{permission_key}' for project {self.project.id if self.project else 'None'}")
                    
                    return valid_roles if valid_roles else self.DEFAULT_PERMISSIONS.get(permission_key, [])
        
        # Return default
        return self.DEFAULT_PERMISSIONS.get(permission_key, [])
    
    def _get_user_roles_in_project(self, user: User) -> List[str]:
        """
        Get user's roles in the project.
        
        Returns: List of role strings (e.g., ['developer', 'scrum_master'])
        """
        if not self.project:
            return [user.role] if hasattr(user, 'role') else ['viewer']
        
        roles = []
        
        # System admins always have admin role
        if user.role == 'admin' or user.is_superuser:
            roles.append('admin')
        
        # Project owner always has owner role
        if self.project.owner == user:
            roles.append('owner')
        
        # Get project-specific roles from ProjectMember
        try:
            project_member = ProjectMember.objects.get(project=self.project, user=user)
            # Add all roles from ProjectMember (can include custom roles)
            for role in project_member.roles:
                if role not in roles:
                    roles.append(role)
        except ProjectMember.DoesNotExist:
            # Fallback: check if user is in members ManyToMany (backward compatibility)
            if self.project.members.filter(id=user.id).exists():
                roles.append('member')
            else:
                # Default to viewer if not a member
                roles.append('viewer')
        
        # If no roles found, default to viewer
        if not roles:
            roles.append('viewer')
        
        return roles
    
    def _check_role_permission(
        self,
        user: User,
        allowed_roles: List[str]
    ) -> bool:
        """
        Check if user's roles in project match allowed roles.
        
        Supports:
        - System roles: admin, owner, product_owner, scrum_master, tech_lead, developer, qa, designer, analyst, manager, member, viewer
        - Custom roles: defined per project in ProjectConfiguration.custom_roles
        - Role hierarchy: admin > owner > other roles > viewer
        
        Returns True if user has any of the allowed roles.
        """
        user_roles = self._get_user_roles_in_project(user)
        
        # Admin always has access
        if 'admin' in user_roles:
            return True
        
        # Owner has access if 'owner' is in allowed roles or if allowed roles include 'member'
        if 'owner' in user_roles:
            if 'owner' in allowed_roles or 'member' in allowed_roles:
                return True
        
        # Check if any of the user's roles match allowed roles
        if any(role in allowed_roles for role in user_roles):
            return True
        
        # Role hierarchy: members can do what viewers can do
        if 'member' in user_roles and 'viewer' in allowed_roles:
            return True
        
        # Check role hierarchy (higher roles inherit lower role permissions)
        role_hierarchy = {
            'admin': ['admin', 'owner', 'product_owner', 'scrum_master', 'tech_lead', 'manager', 'developer', 'qa', 'designer', 'analyst', 'member', 'viewer'],
            'owner': ['owner', 'product_owner', 'scrum_master', 'tech_lead', 'manager', 'developer', 'qa', 'designer', 'analyst', 'member', 'viewer'],
            'product_owner': ['product_owner', 'scrum_master', 'manager', 'member', 'viewer'],
            'scrum_master': ['scrum_master', 'member', 'viewer'],
            'tech_lead': ['tech_lead', 'developer', 'member', 'viewer'],
            'manager': ['manager', 'member', 'viewer'],
            'developer': ['developer', 'member', 'viewer'],
            'qa': ['qa', 'member', 'viewer'],
            'designer': ['designer', 'member', 'viewer'],
            'analyst': ['analyst', 'member', 'viewer'],
            'member': ['member', 'viewer'],
            'viewer': ['viewer']
        }
        
        # Check if any of the user's roles have hierarchy that includes allowed roles
        for user_role in user_roles:
            if user_role in role_hierarchy:
                if any(allowed_role in role_hierarchy[user_role] for allowed_role in allowed_roles):
                    return True
        
        return False
    
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
            # For now, just check if user is admin/owner/scrum_master/product_owner
            user_roles = self._get_user_roles_in_project(user)
            if not any(role in ['admin', 'owner', 'scrum_master', 'product_owner'] for role in user_roles):
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
    
    def can_create_task(self, user: User) -> Tuple[bool, Optional[str]]:
        """Check if user can create tasks."""
        allowed_roles = self._get_permission_setting('who_can_create_tasks')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can create tasks"
        return True, None
    
    def can_edit_task(self, user: User, task: Optional[Task] = None) -> Tuple[bool, Optional[str]]:
        """Check if user can edit tasks."""
        allowed_roles = self._get_permission_setting('who_can_edit_tasks')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can edit tasks"
        return True, None
    
    def can_delete_task(self, user: User, task: Optional[Task] = None) -> Tuple[bool, Optional[str]]:
        """Check if user can delete tasks."""
        allowed_roles = self._get_permission_setting('who_can_delete_tasks')
        has_permission = self._check_role_permission(user, allowed_roles)
        
        if not has_permission:
            return False, f"Only {', '.join(allowed_roles)} can delete tasks"
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

