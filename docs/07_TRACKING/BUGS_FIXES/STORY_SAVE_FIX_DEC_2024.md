---
title: "Story Save 400 Error Fix - December 2024"
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

# Story Save 400 Error Fix - December 2024

**Date:** December 5, 2024  
**Status:** ✅ **FIXED**

---

## 🐛 Issue Found

When saving/updating a user story, the API returned:
```
Failed to load resource: the server responded with a status of 400 (Bad Request)
```

**Root Cause:**
When updating a story, if `epic`, `sprint`, or `assigned_to` fields were set to `'none'` (to clear them), the frontend was not including them in the update payload. However, if the story already had values for these fields, they needed to be explicitly set to `null` to clear them, not just omitted.

**Example:**
- Story has `epic: <some-uuid>`
- User sets epic dropdown to "none" (to clear it)
- Frontend doesn't include `epic` in update payload
- Backend keeps the old value (doesn't clear it)
- Or backend validation fails because the field is required to be explicitly null

---

## ✅ Fix Applied

**File:** `frontend/src/components/stories/StoryFormModal.tsx`

**Change:**
```typescript
// Before
if (epicId && epicId !== 'none') storyData.epic = epicId
if (sprintId && sprintId !== 'none') storyData.sprint = sprintId
if (assignedTo && assignedTo !== 'none') storyData.assigned_to = assignedTo

// After
// Handle epic - set to null if 'none', otherwise set to UUID
storyData.epic = epicId && epicId !== 'none' ? epicId : null
// Handle sprint - set to null if 'none', otherwise set to UUID
storyData.sprint = sprintId && sprintId !== 'none' ? sprintId : null
// Handle assigned_to - set to null if 'none', otherwise set to UUID
storyData.assigned_to = assignedTo && assignedTo !== 'none' ? assignedTo : null
```

**Reason:**
- Now explicitly sets fields to `null` when clearing them
- Ensures backend receives the correct value (UUID or null)
- Prevents validation errors when updating stories

---

## 📋 Additional Notes

- This fix ensures that clearing relationships (epic, sprint, assigned_to) works correctly
- The backend serializer accepts `null` for these fields (they're nullable ForeignKeys)
- Both create and update operations now handle 'none' values correctly

---

**Last Updated:** December 5, 2024  
**Status:** ✅ **FIXED**

