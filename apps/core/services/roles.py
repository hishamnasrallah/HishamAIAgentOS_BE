"""
Unified Role Management Service

This service provides a centralized, dynamic role system that:
1. Defines all system roles in one place
2. Supports role hierarchy
3. Works with both User.role (system-level) and ProjectMember.roles (project-level)
4. Provides consistent role checking across the entire application
5. Supports SaaS multi-tenancy with organizations
6. Handles super admin (system owner) vs organization admin

Role Hierarchy:
- super_admin (system owner) - Highest level, access to all organizations
- org_admin (organization admin) - Organization-level admin
- Other roles (project-level and system-level)
"""

from typing import List, Dict, Optional, Set
from django.contrib.auth import get_user_model
from apps.projects.models import Project, ProjectMember, ProjectConfiguration

User = get_user_model()


class RoleService:
    """
    Centralized role management service.
    
    This is the single source of truth for all roles in the system.
    All role-related operations should go through this service.
    """
    
    # System roles - always available across the entire system
    # These are the base roles that every user can have
    SYSTEM_ROLES = {
        'super_admin': {
            'label': 'Super Administrator',
            'description': 'System owner with access to all organizations and everything',
            'level': 1000,  # Highest level - system owner
            'is_system': True,
            'is_super_admin': True,
        },
        'org_admin': {
            'label': 'Organization Administrator',
            'description': 'Organization administrator with full access to their organization',
            'level': 100,  # Organization-level admin
            'is_system': True,
            'is_org_admin': True,
        },
        'owner': {
            'label': 'Project Owner',
            'description': 'Project owner with full project access',
            'level': 90,
            'is_system': True,
        },
        'product_owner': {
            'label': 'Product Owner',
            'description': 'Product owner responsible for product vision and requirements',
            'level': 80,
            'is_system': True,
        },
        'scrum_master': {
            'label': 'Scrum Master',
            'description': 'Scrum master facilitating agile processes and ceremonies',
            'level': 75,
            'is_system': True,
        },
        'tech_lead': {
            'label': 'Technical Lead',
            'description': 'Technical lead overseeing development and architecture',
            'level': 70,
            'is_system': True,
        },
        'manager': {
            'label': 'Project Manager',
            'description': 'Project manager coordinating project activities',
            'level': 65,
            'is_system': True,
        },
        'developer': {
            'label': 'Developer',
            'description': 'Software developer writing and maintaining code',
            'level': 60,
            'is_system': True,
        },
        'qa': {
            'label': 'QA Engineer',
            'description': 'Quality assurance engineer testing and validating',
            'level': 55,
            'is_system': True,
        },
        'designer': {
            'label': 'Designer',
            'description': 'UI/UX designer creating user interfaces',
            'level': 50,
            'is_system': True,
        },
        'analyst': {
            'label': 'Business Analyst',
            'description': 'Business analyst analyzing requirements and processes',
            'level': 45,
            'is_system': True,
        },
        'member': {
            'label': 'Member',
            'description': 'General project member with standard access',
            'level': 40,
            'is_system': True,
        },
        'viewer': {
            'label': 'Viewer',
            'description': 'Read-only access to view project information',
            'level': 10,
            'is_system': True,
        },
    }
    
    # Role hierarchy - defines which roles inherit permissions from which roles
    # Higher level roles automatically have permissions of lower level roles
    ROLE_HIERARCHY = {
        'super_admin': ['super_admin', 'org_admin', 'owner', 'product_owner', 'scrum_master', 
                        'tech_lead', 'manager', 'developer', 'qa', 'designer', 'analyst', 'member', 'viewer'],
        'org_admin': ['org_admin', 'owner', 'product_owner', 'scrum_master', 'tech_lead', 
                      'manager', 'developer', 'qa', 'designer', 'analyst', 'member', 'viewer'],
        'owner': ['owner', 'product_owner', 'scrum_master', 'tech_lead', 'manager', 
                  'developer', 'qa', 'designer', 'analyst', 'member', 'viewer'],
        'product_owner': ['product_owner', 'scrum_master', 'manager', 'member', 'viewer'],
        'scrum_master': ['scrum_master', 'member', 'viewer'],
        'tech_lead': ['tech_lead', 'developer', 'member', 'viewer'],
        'manager': ['manager', 'member', 'viewer'],
        'developer': ['developer', 'member', 'viewer'],
        'qa': ['qa', 'member', 'viewer'],
        'designer': ['designer', 'member', 'viewer'],
        'analyst': ['analyst', 'member', 'viewer'],
        'member': ['member', 'viewer'],
        'viewer': ['viewer'],
    }
    
    @classmethod
    def get_all_system_roles(cls) -> List[str]:
        """Get list of all system role keys."""
        return list(cls.SYSTEM_ROLES.keys())
    
    @classmethod
    def get_role_info(cls, role: str) -> Optional[Dict]:
        """Get information about a specific role."""
        return cls.SYSTEM_ROLES.get(role)
    
    @classmethod
    def is_valid_role(cls, role: str, project: Optional[Project] = None) -> bool:
        """
        Check if a role is valid.
        
        Args:
            role: Role to check
            project: Optional project to check for custom roles
        
        Returns:
            True if role is valid (system role or project custom role)
        """
        # Check if it's a system role
        if role in cls.SYSTEM_ROLES:
            return True
        
        # Check if it's a custom role in the project
        if project:
            try:
                config = project.configuration
                custom_roles = config.custom_roles if config.custom_roles else []
                if role in custom_roles:
                    return True
            except ProjectConfiguration.DoesNotExist:
                pass
        
        return False
    
    @classmethod
    def get_user_roles(cls, user: User, project: Optional[Project] = None, organization=None) -> List[str]:
        """
        Get all roles for a user (super-admin + organization-level + system-level + project-level).
        
        This is the unified method to get user roles anywhere in the system.
        
        Role priority (highest to lowest):
        1. Super admin (system owner) - if user.is_superuser
        2. Organization admin - if user is org admin in the organization
        3. System-level role (from User.role field)
        4. Project-specific roles (from ProjectMember)
        5. Project owner role
        
        Args:
            user: User object
            project: Optional project to get project-specific roles
            organization: Optional organization to get organization-level roles
        
        Returns:
            List of role strings
        """
        roles = []
        
        # 1. Super admin check (highest priority)
        # Super admins are system owners with access to everything
        if user.is_superuser:
            if 'super_admin' not in roles:
                roles.append('super_admin')
            # Super admin also has org_admin for backward compatibility
            if 'org_admin' not in roles:
                roles.append('org_admin')
        
        # 2. Organization-level roles
        if organization:
            try:
                from apps.organizations.models import OrganizationMember
                org_member = OrganizationMember.objects.get(organization=organization, user=user)
                if org_member.role == 'org_admin' and 'org_admin' not in roles:
                    roles.append('org_admin')
                # Organization owner is also org_admin
                if organization.owner == user and 'org_admin' not in roles:
                    roles.append('org_admin')
            except Exception:
                pass
        
        # 3. System-level role (from User.role field)
        # Note: Legacy 'admin' role is automatically mapped to 'org_admin' for backward compatibility
        if hasattr(user, 'role') and user.role:
            # Map old 'admin' to 'org_admin' for backward compatibility (migration support)
            if user.role == 'admin':
                if 'org_admin' not in roles:
                    roles.append('org_admin')
            elif user.role not in roles:
                roles.append(user.role)
        
        # 4. Project-specific roles (from ProjectMember)
        if project:
            try:
                project_member = ProjectMember.objects.get(project=project, user=user)
                for role in project_member.roles:
                    if role not in roles:
                        roles.append(role)
            except ProjectMember.DoesNotExist:
                pass
            
            # Project owner always has owner role
            if project.owner == user and 'owner' not in roles:
                roles.append('owner')
        
        # If no roles found, default to viewer
        if not roles:
            roles.append('viewer')
        
        return roles
    
    @classmethod
    def has_role(cls, user: User, role: str, project: Optional[Project] = None, organization=None) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            user: User object
            role: Role to check
            project: Optional project for project-specific role check
            organization: Optional organization for org-level role check
        
        Returns:
            True if user has the role
        """
        user_roles = cls.get_user_roles(user, project, organization)
        return role in user_roles
    
    @classmethod
    def has_any_role(cls, user: User, roles: List[str], project: Optional[Project] = None, organization=None) -> bool:
        """
        Check if user has any of the specified roles.
        
        Args:
            user: User object
            roles: List of roles to check
            project: Optional project for project-specific role check
            organization: Optional organization for org-level role check
        
        Returns:
            True if user has any of the roles
        """
        user_roles = cls.get_user_roles(user, project, organization)
        return any(role in user_roles for role in roles)
    
    @classmethod
    def has_role_with_hierarchy(cls, user: User, required_role: str, project: Optional[Project] = None, organization=None) -> bool:
        """
        Check if user has a role, considering role hierarchy.
        
        For example, if required_role is 'member', users with 'developer' or 'org_admin' 
        will also have access because of the hierarchy.
        
        Args:
            user: User object
            required_role: Required role
            project: Optional project for project-specific role check
            organization: Optional organization for org-level role check
        
        Returns:
            True if user has the role or a higher role in hierarchy
        """
        user_roles = cls.get_user_roles(user, project, organization)
        
        # Super admin always has access
        if 'super_admin' in user_roles:
            return True
        
        # Org admin has access to most things (except super admin only)
        if 'org_admin' in user_roles and required_role != 'super_admin':
            return True
        
        # Check if user has the exact role
        if required_role in user_roles:
            return True
        
        # Check role hierarchy
        for user_role in user_roles:
            if user_role in cls.ROLE_HIERARCHY:
                if required_role in cls.ROLE_HIERARCHY[user_role]:
                    return True
        
        return False
    
    @classmethod
    def is_super_admin(cls, user: User) -> bool:
        """Check if user is a super admin (system owner)."""
        return user.is_superuser
    
    @classmethod
    def is_org_admin(cls, user: User, organization=None) -> bool:
        """Check if user is an organization admin."""
        # Super admins are also org admins (they can manage any org)
        if user.is_superuser:
            return True
        
        # Check if user is org owner
        if organization and organization.owner == user:
            return True
        
        # Check OrganizationMember
        if organization:
            try:
                from apps.organizations.models import OrganizationMember
                org_member = OrganizationMember.objects.get(organization=organization, user=user)
                return org_member.role == 'org_admin'
            except Exception:
                pass
        
        # If no specific organization is provided, check if user is org_admin in any organization
        # This is for cases where a general 'admin' check is performed without organization context
        try:
            from apps.organizations.models import OrganizationMember
            if OrganizationMember.objects.filter(user=user, role='org_admin').exists():
                return True
        except Exception:
            pass
        
        # Check User.role for org_admin (works without organization parameter)
        if hasattr(user, 'role') and user.role == 'org_admin':
            return True
        
        # Backward compatibility: check User.role (legacy 'admin' maps to org_admin)
        if hasattr(user, 'role') and user.role == 'admin':
            return True
        
        return False
    
    @classmethod
    def is_admin(cls, user: User) -> bool:
        """Check if user is an admin (backward compatibility - checks org_admin or super_admin)."""
        return cls.is_super_admin(user) or cls.is_org_admin(user)
    
    @classmethod
    def is_admin_or_owner(cls, user: User, project: Optional[Project] = None, organization=None) -> bool:
        """Check if user is super admin, org admin, or project owner."""
        if cls.is_super_admin(user):
            return True
        if organization and cls.is_org_admin(user, organization):
            return True
        if project and project.owner == user:
            return True
        return False
    
    @classmethod
    def get_user_organization(cls, user: User) -> Optional:
        """Get user's primary organization."""
        if hasattr(user, 'organization'):
            return user.organization
        # Try to get from OrganizationMember
        try:
            from apps.organizations.models import OrganizationMember
            org_member = OrganizationMember.objects.filter(user=user).first()
            if org_member:
                return org_member.organization
        except Exception:
            pass
        return None
    
    @classmethod
    def get_user_organizations(cls, user: User) -> List:
        """Get all organizations user belongs to."""
        try:
            from apps.organizations.models import OrganizationMember
            return [om.organization for om in OrganizationMember.objects.filter(user=user).select_related('organization')]
        except Exception:
            return []
    
    @classmethod
    def get_custom_roles(cls, project: Project) -> List[str]:
        """Get custom roles defined for a project."""
        try:
            config = project.configuration
            return config.custom_roles if config.custom_roles else []
        except ProjectConfiguration.DoesNotExist:
            return []
    
    @classmethod
    def get_all_available_roles(cls, project: Optional[Project] = None, organization=None) -> List[str]:
        """
        Get all available roles (system + org + custom).
        
        Args:
            project: Optional project to include custom roles
            organization: Optional organization to include org-level roles
        
        Returns:
            List of all available role keys
        """
        roles = list(cls.SYSTEM_ROLES.keys())
        
        # Add organization-level roles
        if organization:
            from apps.organizations.models import OrganizationMember
            for org_role in OrganizationMember.ORG_ROLES:
                if org_role not in roles:
                    roles.append(org_role)
        
        # Add project custom roles
        if project:
            custom_roles = cls.get_custom_roles(project)
            for custom_role in custom_roles:
                if custom_role not in roles:
                    roles.append(custom_role)
        
        return roles
    
    @classmethod
    def get_roles_with_info(cls, project: Optional[Project] = None, organization=None) -> List[Dict]:
        """
        Get all roles with their information.
        
        Args:
            project: Optional project to include custom roles
            organization: Optional organization to include org-level roles
        
        Returns:
            List of role dictionaries with label, description, etc.
        """
        roles = []
        
        # Add system roles
        for role_key, role_info in cls.SYSTEM_ROLES.items():
            roles.append({
                'value': role_key,
                'label': role_info['label'],
                'description': role_info['description'],
                'level': role_info['level'],
                'is_system': True,
                'is_super_admin': role_info.get('is_super_admin', False),
                'is_org_admin': role_info.get('is_org_admin', False),
            })
        
        # Add organization-level roles
        if organization:
            from apps.organizations.models import OrganizationMember
            org_roles_info = {
                'org_admin': {
                    'label': 'Organization Administrator',
                    'description': 'Organization administrator with full access to their organization',
                    'level': 100,
                },
                'org_member': {
                    'label': 'Organization Member',
                    'description': 'Regular organization member',
                    'level': 40,
                },
            }
            for org_role in OrganizationMember.ORG_ROLES:
                if org_role not in [r['value'] for r in roles]:
                    info = org_roles_info.get(org_role, {
                        'label': org_role.replace('_', ' ').title(),
                        'description': f'Organization role: {org_role}',
                        'level': 50,
                    })
                    roles.append({
                        'value': org_role,
                        'label': info['label'],
                        'description': info['description'],
                        'level': info['level'],
                        'is_system': False,
                        'is_org_role': True,
                    })
        
        # Add custom roles
        if project:
            custom_roles = cls.get_custom_roles(project)
            for custom_role in custom_roles:
                if custom_role not in [r['value'] for r in roles]:
                    roles.append({
                        'value': custom_role,
                        'label': custom_role.replace('_', ' ').title(),
                        'description': f'Custom role: {custom_role}',
                        'level': 30,  # Default level for custom roles
                        'is_system': False,
                        'is_custom': True,
                    })
        
        return sorted(roles, key=lambda x: x['level'], reverse=True)

