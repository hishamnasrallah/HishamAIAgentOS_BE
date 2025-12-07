---
title: "Permissions Debug - December 2024"
description: "Users can still see all projects despite queryset filtering implementation."

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Project Manager
    - CTO / Technical Lead
  secondary:
    - All

applicable_phases:
  primary:
    - Development

tags:
  - core

status: "active"
priority: "medium"
difficulty: "intermediate"
completeness: "100%"
quality_status: "draft"

estimated_read_time: "10 minutes"

version: "1.0"
last_updated: "2025-12-06"
last_reviewed: "2025-12-06"
review_frequency: "quarterly"

author: "Development Team"
maintainer: "Development Team"

related: []
see_also: []
depends_on: []
prerequisite_for: []

aliases: []

changelog:
  - version: "1.0"
    date: "2025-12-06"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---

# Permissions Debug - December 2024

## Issue
Users can still see all projects despite queryset filtering implementation.

## Current Implementation

### ProjectViewSet.get_queryset()
```python
def get_queryset(self):
    user = self.request.user
    if not user or not user.is_authenticated:
        return Project.objects.none()
    
    # Admins can see all projects
    if user.role == 'admin':
        return Project.objects.all().select_related('owner').prefetch_related('members')
    
    # Regular users can only see projects they own or are members of
    user_projects = Project.objects.filter(
        models.Q(owner=user) | models.Q(members__id=user.id)
    ).distinct()
    
    return user_projects.select_related('owner').prefetch_related('members')
```

## Potential Issues

1. **Server Not Restarted**: Changes require server restart
2. **Caching**: Django queryset caching might be showing old results
3. **Permission Class**: `IsProjectMemberOrReadOnly` allows all authenticated users at view level
4. **ManyToMany Filtering**: The `members__id=user.id` should work, but might need verification

## Verification Steps

1. **Check if queryset is being called**:
   - Add logging to `get_queryset()` method
   - Check Django logs when listing projects

2. **Verify ManyToMany relationship**:
   - Check if projects actually have members assigned
   - Verify the relationship is working correctly

3. **Test the query directly**:
   ```python
   from apps.projects.models import Project
   from apps.authentication.models import User
   
   user = User.objects.get(email='test@example.com')
   projects = Project.objects.filter(
       models.Q(owner=user) | models.Q(members__id=user.id)
   ).distinct()
   print(f"Projects for {user.email}: {projects.count()}")
   ```

4. **Check if default queryset is being used**:
   - Ensure no `queryset = Project.objects.all()` is set at class level
   - Verify `get_queryset()` is always called

## Solution Applied

1. Changed ManyToMany filtering from `members=user` to `members__id=user.id`
2. Added comment to not set queryset at class level
3. Applied same fix to all project-related ViewSets (Sprint, Story, Epic, Task)

## Next Steps

1. Restart Django server
2. Clear browser cache / use incognito
3. Test with different users
4. Check Django logs for queryset execution
5. Verify projects have members assigned correctly

