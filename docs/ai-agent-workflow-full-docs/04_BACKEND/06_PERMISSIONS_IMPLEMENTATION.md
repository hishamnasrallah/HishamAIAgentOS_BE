# Backend Permissions Implementation - Security & Access Control

**Document Type:** Permissions Implementation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 04_VIEWS_IMPLEMENTATION.md, ../08_SECURITY/, ../02_BUSINESS/04_BUSINESS_RULES.md  
**File Size:** 497 lines

---

## 📋 Purpose

This document specifies the permission classes and access control implementation for the AI agent workflow enhancement endpoints.

---

## 🔐 Permission Classes

### Permission Class 1: IsProjectMemberOrReadOnly

**Location:** `backend/apps/projects/permissions.py`

**Purpose:** Allow read access to project members, write to owners/admins

**Implementation:**

```python
class IsProjectMemberOrReadOnly(permissions.BasePermission):
    """
    Permission class for project members.
    - Read: Project members, owners, org admins
    - Write: Project owners, org admins, super admins
    """
    
    def has_object_permission(self, request, view, obj):
        # Super admin bypass
        if request.user.is_superuser:
            return True
        
        # Get project from object
        project = self._get_project(obj)
        if not project:
            return False
        
        # Check organization status
        if not self._check_organization_status(project.organization):
            return False
        
        # Read permissions
        if request.method in permissions.SAFE_METHODS:
            return self._is_project_member(project, request.user)
        
        # Write permissions
        return (
            self._is_project_owner(project, request.user) or
            self._is_org_admin(project.organization, request.user)
        )
    
    def _get_project(self, obj):
        """Extract project from object."""
        if hasattr(obj, 'project'):
            return obj.project
        elif isinstance(obj, Project):
            return obj
        return None
    
    def _check_organization_status(self, organization):
        """Check organization is active."""
        if not organization:
            return False
        return organization.status == 'active'
    
    def _is_project_member(self, project, user):
        """Check user is project member."""
        return (
            project.owner == user or
            project.members.filter(user=user).exists()
        )
    
    def _is_project_owner(self, project, user):
        """Check user is project owner."""
        return project.owner == user
    
    def _is_org_admin(self, organization, user):
        """Check user is org admin."""
        if not organization:
            return False
        return organization.members.filter(
            user=user,
            role='admin'
        ).exists()
```

---

### Permission Class 2: CanGenerateProject

**Location:** `backend/apps/projects/permissions.py`

**Purpose:** Check user can generate projects

**Implementation:**

```python
class CanGenerateProject(permissions.BasePermission):
    """
    Permission to generate projects.
    Checks:
    - User is project member
    - Organization subscription valid
    - Concurrent generation limits
    - Storage quotas
    """
    
    def has_permission(self, request, view):
        # Super admin bypass
        if request.user.is_superuser:
            return True
        
        # Must be authenticated
        if not request.user.is_authenticated:
            return False
        
        # Get project from view kwargs
        project_id = view.kwargs.get('project_id')
        if not project_id:
            return False
        
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return False
        
        # Check organization status
        if project.organization.status != 'active':
            return False
        
        # Check user is project member
        if not self._is_project_member(project, request.user):
            return False
        
        # Check concurrent generation limits
        if not self._check_concurrent_limit(project.organization):
            return False
        
        # Check storage quota
        if not self._check_storage_quota(project.organization):
            return False
        
        return True
    
    def _check_concurrent_limit(self, organization):
        """Check concurrent generation limit."""
        active_generations = GeneratedProject.objects.filter(
            project__organization=organization,
            status='generating'
        ).count()
        
        limit = self._get_concurrent_limit(organization)
        return active_generations < limit
    
    def _get_concurrent_limit(self, organization):
        """Get concurrent generation limit for organization."""
        subscription = organization.subscription
        if not subscription:
            return 1  # Default
        
        tier_limits = {
            'free': 1,
            'pro': 5,
            'enterprise': 999999,  # Effectively unlimited
        }
        return tier_limits.get(subscription.tier, 1)
    
    def _check_storage_quota(self, organization):
        """Check storage quota."""
        used_storage = GeneratedProject.objects.filter(
            project__organization=organization,
            status__in=['completed', 'generating']
        ).aggregate(
            total=Sum('total_size')
        )['total'] or 0
        
        quota = self._get_storage_quota(organization)
        return used_storage < quota
    
    def _get_storage_quota(self, organization):
        """Get storage quota for organization."""
        subscription = organization.subscription
        if not subscription:
            return 1024 * 1024 * 1024  # 1GB default
        
        tier_quotas = {
            'free': 1024 * 1024 * 1024,  # 1GB
            'pro': 10 * 1024 * 1024 * 1024,  # 10GB
            'enterprise': 999999 * 1024 * 1024 * 1024,  # Unlimited
        }
        return tier_quotas.get(subscription.tier, 1024 * 1024 * 1024)
```

---

### Permission Class 3: CanExportRepository

**Location:** `backend/apps/projects/permissions.py`

**Purpose:** Check user can export repositories

**Implementation:

```python
class CanExportRepository(permissions.BasePermission):
    """
    Permission to export repositories.
    Checks:
    - User owns generated project or is project owner
    - Generated project is completed
    - Export rate limits
    """
    
    def has_permission(self, request, view):
        # Super admin bypass
        if request.user.is_superuser:
            return True
        
        # Get generated project
        generated_id = view.kwargs.get('generated_id')
        if not generated_id:
            return False
        
        try:
            generated_project = GeneratedProject.objects.get(id=generated_id)
        except GeneratedProject.DoesNotExist:
            return False
        
        # Check generated project is completed
        if generated_project.status != 'completed':
            return False
        
        # Check user owns generated project or is project owner
        if not (
            generated_project.created_by == request.user or
            generated_project.project.owner == request.user
        ):
            return False
        
        # Check export rate limits
        if not self._check_export_rate_limit(request.user, generated_project.project.organization):
            return False
        
        return True
    
    def _check_export_rate_limit(self, user, organization):
        """Check export rate limit."""
        from datetime import datetime, timedelta
        
        # Count exports in last 24 hours
        since = datetime.now() - timedelta(days=1)
        exports_today = RepositoryExport.objects.filter(
            generated_project__project__organization=organization,
            created_by=user,
            created_at__gte=since
        ).count()
        
        limit = self._get_export_limit(organization)
        return exports_today < limit
    
    def _get_export_limit(self, organization):
        """Get export limit for organization."""
        subscription = organization.subscription
        if not subscription:
            return 10  # Default
        
        tier_limits = {
            'free': 10,
            'pro': 100,
            'enterprise': 999999,  # Effectively unlimited
        }
        return tier_limits.get(subscription.tier, 10)
```

---

## 🛡️ Security Checks

### Check 1: File Path Validation

**Location:** `backend/apps/projects/services/project_generator.py`

**Implementation:**

```python
def validate_file_path(path: str) -> bool:
    """
    Validate file path is safe.
    Prevents:
    - Path traversal (../, ..\\)
    - Absolute paths
    - Null bytes
    """
    # No absolute paths
    if path.startswith('/') or (path.startswith('\\') and os.name == 'nt'):
        return False
    
    # No path traversal
    if '..' in path or '..\\' in path or '../' in path:
        return False
    
    # No null bytes
    if '\0' in path:
        return False
    
    # Valid characters only
    import re
    pattern = r'^[a-zA-Z0-9_/\\.-]+$'
    if not re.match(pattern, path):
        return False
    
    # Max length
    if len(path) > 500:
        return False
    
    return True
```

---

### Check 2: File Size Validation

**Location:** `backend/apps/projects/services/project_generator.py`

**Implementation:**

```python
def validate_file_size(file_size: int, organization: Organization) -> bool:
    """Validate file size within limits."""
    # Default limit
    default_limit = 10 * 1024 * 1024  # 10MB
    
    # Get organization-specific limit
    subscription = organization.subscription
    if subscription:
        tier_limits = {
            'free': 10 * 1024 * 1024,  # 10MB
            'pro': 50 * 1024 * 1024,  # 50MB
            'enterprise': 100 * 1024 * 1024,  # 100MB
        }
        limit = tier_limits.get(subscription.tier, default_limit)
    else:
        limit = default_limit
    
    return file_size <= limit
```

---

## 🔄 Permission Integration

### ViewSet Integration

**Usage:**

```python
class GeneratedProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        CanGenerateProject,  # For generation action
        IsProjectMemberOrReadOnly,  # For CRUD
    ]
```

---

## 🔐 Super Admin Bypass

### Implementation Pattern

All permission classes include super admin bypass:

```python
def has_permission(self, request, view):
    # Super admin bypass
    if request.user.is_superuser:
        return True
    
    # ... regular permission checks ...
```

**Rationale:**
- Super admins need full access for system management
- Consistent pattern across all permissions
- Explicit bypass for transparency

---

## 📊 Permission Matrix

| Action | Owner | Member | Org Admin | Super Admin |
|--------|-------|--------|-----------|-------------|
| Generate Project | ✅ | ✅ | ✅ | ✅ |
| View Generated | ✅ | ✅ | ✅ | ✅ |
| Export Repository | ✅ | ❌ | ✅ | ✅ |
| Delete Generated | ✅ | ❌ | ✅ | ✅ |

---

## 🔗 Related Documentation

- **Views:** `04_VIEWS_IMPLEMENTATION.md`
- **Business Rules:** `../02_BUSINESS/04_BUSINESS_RULES.md`
- **Security:** `../08_SECURITY/`

---

**Document Owner:** Backend Development Team & Security Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

