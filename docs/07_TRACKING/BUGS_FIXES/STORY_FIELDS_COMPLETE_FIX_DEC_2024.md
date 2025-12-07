---
title: "Story Fields Complete Fix - December 2024"
description: "**Date:** December 5, 2024"

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

# Story Fields Complete Fix - December 2024

**Date:** December 5, 2024  
**Status:** ✅ **FIXED**

---

## 🐛 Issue Found

Not all fields were being stored in the backend when creating/updating stories:
- `story_points` - not always saved
- `assigned_to` - not always saved
- `epic` - not always saved
- `sprint` - not always saved

**Root Cause:**
1. When creating, fields set to 'none' were not included in the payload
2. When updating, fields were conditionally included, causing some to be omitted
3. The serializer might not have been properly handling all fields

---

## ✅ Fix Applied

### Frontend Changes

**File:** `frontend/src/components/stories/StoryFormModal.tsx`

**Changes:**
1. **Always include all fields** - Even when set to 'none', include them as `null`
2. **Consistent field handling** - Same logic for create and update
3. **Added console logging** - To debug what's being sent

```typescript
// Before - fields conditionally included
if (epicId && epicId !== 'none') {
    storyData.epic = epicId
} else if (isEditing) {
    storyData.epic = null
}

// After - always include
storyData.epic = (epicId && epicId !== 'none') ? epicId : null
storyData.sprint = (sprintId && sprintId !== 'none') ? sprintId : null
storyData.assigned_to = (assignedTo && assignedTo !== 'none') ? assignedTo : null
storyData.story_points = parsedStoryPoints // Always include, even if null
```

### Backend Changes

**File:** `backend/apps/projects/serializers.py`

**Changes:**
1. **Explicitly define optional fields** - Made `story_points`, `status`, `priority` explicitly optional
2. **Enhanced extra_kwargs** - Added `story_points` to `extra_kwargs` with `allow_null=True`
3. **Read-only fields** - Added `generated_by_ai`, `generation_workflow`, `created_by` to read-only fields

```python
# Added explicit field definitions
story_points = serializers.IntegerField(required=False, allow_null=True)
status = serializers.CharField(required=False)
priority = serializers.CharField(required=False)

# Enhanced extra_kwargs
extra_kwargs = {
    'assigned_to': {'required': False, 'allow_null': True},
    'story_points': {'required': False, 'allow_null': True},
}
```

---

## 📋 Fields Now Properly Handled

All these fields are now always included in the payload:

1. ✅ **title** - Always included
2. ✅ **description** - Always included
3. ✅ **acceptance_criteria** - Always included
4. ✅ **priority** - Always included (validated, defaults to 'medium')
5. ✅ **story_points** - Always included (number or null)
6. ✅ **status** - Always included
7. ✅ **epic** - Always included (UUID or null)
8. ✅ **sprint** - Always included (UUID or null)
9. ✅ **assigned_to** - Always included (UUID or null)
10. ✅ **project** - Included when creating (not when updating)

---

## 🔍 Debugging

Added console logging to see what data is being sent:
```typescript
console.log('Story data being sent:', storyData)
```

This will help identify any remaining issues with field transmission.

---

**Last Updated:** December 5, 2024  
**Status:** ✅ **FIXED**

