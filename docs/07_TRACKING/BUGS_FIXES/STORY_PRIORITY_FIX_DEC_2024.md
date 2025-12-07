---
title: "Story Priority Validation Fix - December 2024"
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

# Story Priority Validation Fix - December 2024

**Date:** December 5, 2024  
**Status:** ✅ **FIXED**

---

## 🐛 Issue Found

When updating a user story, the API returned:
```
ValidationError: {'priority': [ErrorDetail(string='"" is not a valid choice.', code='invalid_choice')]}
```

**Root Cause:**
The `priority` field was being sent as an empty string `""` instead of a valid choice. The backend expects one of: `'low'`, `'medium'`, `'high'`, `'critical'`, but received an empty string.

**Possible Causes:**
1. The Select component might have returned an empty string in some edge cases
2. The priority state might have been reset to an empty string
3. Form validation didn't catch the empty value before submission

---

## ✅ Fix Applied

**File:** `frontend/src/components/stories/StoryFormModal.tsx`

**Change:**
```typescript
// Before
priority: priority && priority !== 'none' && priority !== '' ? priority : 'medium',

// After
// Ensure priority is always a valid value
const validPriority = (priority && priority !== 'none' && priority !== '' && ['low', 'medium', 'high', 'critical'].includes(priority)) 
    ? priority 
    : 'medium'

const storyData: any = {
    ...
    priority: validPriority,
    ...
}
```

**Additional Improvements:**
- Added explicit validation to check if priority is in the valid choices array
- Added `.trim()` to text fields to remove whitespace
- Ensured priority always defaults to 'medium' if invalid

---

## 📋 Validation Rules

The backend accepts these priority values:
- `'low'`
- `'medium'` (default)
- `'high'`
- `'critical'`

Any other value (including empty string, 'none', or invalid strings) will default to `'medium'`.

---

**Last Updated:** December 5, 2024  
**Status:** ✅ **FIXED**

