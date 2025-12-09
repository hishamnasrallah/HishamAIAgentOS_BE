"""
Custom permissions for role-based access control.
"""

from rest_framework import permissions
from apps.projects.services.permissions import get_permission_service


class IsAdminUser(permissions.BasePermission):
    """Permission check for admin users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsManager(permissions.BasePermission):
    """Permission check for manager users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'manager']


class IsDeveloper(permissions.BasePermission):
    """Permission check for developer users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'manager', 'developer']


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user or request.user.role == 'admin'


class IsOwner(permissions.BasePermission):
    """Permission check for object owner."""
    
    def has_object_permission(self, request, view, obj):
        # Check if obj has a 'user' or 'owner' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.role == 'admin'
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user or request.user.role == 'admin'
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user or request.user.role == 'admin'
        
        return False


class IsProjectMember(permissions.BasePermission):
    """
    Permission check for project members.
    Allows access if user is the project owner, a project member, or an admin.
    """
    
    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admins have access to everything
        if request.user.role == 'admin':
            return True
        
        return True  # Will check object-level permissions
    
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.role == 'admin':
            return True
        
        # Get the project from the object
        project = None
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Project':
            project = obj
        
        if not project:
            return False
        
        # Check if user is owner
        if project.owner == request.user:
            return True
        
        # Check if user is a member
        if project.members.filter(id=request.user.id).exists():
            return True
        
        return False


class IsProjectOwner(permissions.BasePermission):
    """
    Permission check for project owners only.
    Allows access only if user is the project owner or an admin.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True  # Will check object-level permissions
    
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.role == 'admin':
            return True
        
        # Get the project from the object
        project = None
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Project':
            project = obj
        
        if not project:
            return False
        
        # Only owner can access
        return project.owner == request.user


class IsProjectMemberOrReadOnly(permissions.BasePermission):
    """
    Permission check for project members with read-only for non-members.
    Allows read access to anyone authenticated, but write access only to members/owners.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True  # Will check object-level permissions
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for authenticated users (will be filtered by queryset)
        if request.method in permissions.SAFE_METHODS:
            # Admins have full access
            if request.user.role == 'admin':
                return True
            
            # Get the project from the object
            project = None
            if hasattr(obj, 'project'):
                project = obj.project
            elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Project':
                project = obj
            
            if not project:
                return False
            
            # Check if user is owner or member
            if project.owner == request.user:
                return True
            if project.members.filter(id=request.user.id).exists():
                return True
            
            return False
        
        # Write permissions only for members/owners/admins
        # Admins have full access
        if request.user.role == 'admin':
            return True
        
        # Get the project from the object
        project = None
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Project':
            project = obj
        
        if not project:
            return False
        
        # Check if user is owner
        if project.owner == request.user:
            return True
        
        # Check if user is a member
        if project.members.filter(id=request.user.id).exists():
            return True
        
        return False


class IsProjectPermissionEnforced(permissions.BasePermission):
    """
    Permission class that enforces project-level permission settings.
    
    This class checks permissions based on ProjectConfiguration.permission_settings,
    allowing projects to override default permissions with custom rules.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission for the view action."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admins always have access
        if request.user.role == 'admin':
            return True
        
        return True  # Will check object-level permissions
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission for the specific object and action."""
        # Admins always have access
        if request.user.role == 'admin':
            return True
        
        # Get the project from the object
        project = None
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Project':
            project = obj
        
        if not project:
            # If no project, fall back to default behavior
            return True
        
        # Get permission service
        perm_service = get_permission_service(project)
        
        # Check permissions based on action
        action = getattr(view, 'action', None)
        method = request.method
        
        # Map actions to permission checks
        if method == 'POST' or action == 'create':
            if hasattr(obj, '__class__'):
                if obj.__class__.__name__ == 'UserStory':
                    has_perm, error = perm_service.can_create_story(request.user)
                    if not has_perm:
                        return False
                elif obj.__class__.__name__ == 'Epic':
                    has_perm, error = perm_service.can_create_epic(request.user)
                    if not has_perm:
                        return False
        
        elif method in ['PUT', 'PATCH'] or action in ['update', 'partial_update']:
            if hasattr(obj, '__class__'):
                if obj.__class__.__name__ == 'UserStory':
                    has_perm, error = perm_service.can_edit_story(request.user, obj)
                    if not has_perm:
                        return False
                elif obj.__class__.__name__ == 'Epic':
                    has_perm, error = perm_service.can_edit_epic(request.user, obj)
                    if not has_perm:
                        return False
        
        elif method == 'DELETE' or action == 'destroy':
            if hasattr(obj, '__class__'):
                if obj.__class__.__name__ == 'UserStory':
                    has_perm, error = perm_service.can_delete_story(request.user, obj)
                    if not has_perm:
                        return False
                elif obj.__class__.__name__ == 'Epic':
                    has_perm, error = perm_service.can_delete_epic(request.user)
                    if not has_perm:
                        return False
        
        # Check specific actions
        if action == 'assign':
            has_perm, error = perm_service.can_assign_story(request.user)
            if not has_perm:
                return False
        
        if action == 'change_status' or (method in ['PUT', 'PATCH'] and hasattr(request, 'data') and request.data and 'status' in request.data):
            if hasattr(obj, '__class__') and obj.__class__.__name__ == 'UserStory':
                has_perm, error = perm_service.can_change_status(request.user, obj)
                if not has_perm:
                    return False
        
        return True


class IsProjectPermissionEnforcedOrReadOnly(permissions.BasePermission):
    """
    Permission class that enforces project-level permissions for write operations,
    but allows read access to project members.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission for the view action."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Read permissions are allowed (will be filtered by queryset)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admins always have access
        if request.user.role == 'admin':
            return True
        
        return True  # Will check object-level permissions
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission for the specific object and action."""
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            # Check basic project membership
            project = None
            if hasattr(obj, 'project'):
                project = obj.project
            elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Project':
                project = obj
            
            if project:
                # Admins have full access
                if request.user.role == 'admin':
                    return True
                
                # Check if user is owner or member
                if project.owner == request.user:
                    return True
                if project.members.filter(id=request.user.id).exists():
                    return True
                
                return False
            
            return True
        
        # Write permissions - use permission enforcement
        # Admins always have access
        if request.user.role == 'admin':
            return True
        
        # Get the project from the object
        project = None
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Project':
            project = obj
        
        if not project:
            return False
        
        # Get permission service
        perm_service = get_permission_service(project)
        
        # Check permissions based on action
        action = getattr(view, 'action', None)
        method = request.method
        
        # Map actions to permission checks
        if method == 'POST' or action == 'create':
            if hasattr(obj, '__class__'):
                if obj.__class__.__name__ == 'UserStory':
                    has_perm, error = perm_service.can_create_story(request.user)
                    if not has_perm:
                        return False
                elif obj.__class__.__name__ == 'Epic':
                    has_perm, error = perm_service.can_create_epic(request.user)
                    if not has_perm:
                        return False
        
        elif method in ['PUT', 'PATCH'] or action in ['update', 'partial_update']:
            if hasattr(obj, '__class__'):
                if obj.__class__.__name__ == 'UserStory':
                    has_perm, error = perm_service.can_edit_story(request.user, obj)
                    if not has_perm:
                        return False
                elif obj.__class__.__name__ == 'Epic':
                    has_perm, error = perm_service.can_edit_epic(request.user, obj)
                    if not has_perm:
                        return False
        
        elif method == 'DELETE' or action == 'destroy':
            if hasattr(obj, '__class__'):
                if obj.__class__.__name__ == 'UserStory':
                    has_perm, error = perm_service.can_delete_story(request.user, obj)
                    if not has_perm:
                        return False
                elif obj.__class__.__name__ == 'Epic':
                    has_perm, error = perm_service.can_delete_epic(request.user)
                    if not has_perm:
                        return False
        
        return True