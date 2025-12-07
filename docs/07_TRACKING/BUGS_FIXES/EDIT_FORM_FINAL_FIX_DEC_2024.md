---
title: "Edit Form Final Fix - December 2024"
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

# Edit Form Final Fix - December 2024

**Date:** December 5, 2024  
**Status:** ✅ **COMPLETED**

---

## 🎯 Issue

The edit form dropdowns (Epic, Sprint, Assignee) were showing "None" or "Unassigned" even though the story had valid values. The console logs showed that:
- Story data was being fetched correctly
- Values were being extracted correctly
- Options arrays were loaded
- The `find()` method was successfully finding matching items
- Form state was being set with the correct UUID strings

But the Select components were still displaying "None" or "Unassigned".

---

## 🔍 Root Cause

The issue was with the **initial state values** and how they were being used in the Select components:

### Problem 1: Initial State Used 'none' String
```typescript
// ❌ WRONG - Initial state was 'none' as a string
const [epicId, setEpicId] = useState<string>('none')
```

### Problem 2: Select Value Logic
```typescript
// ❌ WRONG - This would evaluate to 'none' if epicId was falsy
value={epicId || 'none'}
```

When the form first rendered:
1. Initial state was `'none'` (string)
2. Story data loaded and `setEpicId('ee215fb6-...')` was called
3. But the Select component was using `epicId || 'none'`
4. If `epicId` was ever empty string, null, or undefined, it would default to `'none'`
5. The Select component requires **exact value matching** - if the value doesn't match any SelectItem, it resets

### Problem 3: Form Reset Logic
When the modal closed, the form reset to `'none'`, but when it reopened, if the value wasn't set immediately, the Select would show 'none'.

---

## ✅ Solution

### 1. Changed Initial State to Empty String
```typescript
// ✅ CORRECT - Use empty string for "unset" state
const [epicId, setEpicId] = useState<string>('')
const [sprintId, setSprintId] = useState<string>('')
const [assignedTo, setAssignedTo] = useState<string>('')
```

**Why:** Empty string is falsy, but we can explicitly check for it. More importantly, it allows us to distinguish between "not set" (empty string) and "explicitly set to none" ('none').

### 2. Changed Select Value Logic
```typescript
// ✅ CORRECT - Explicit ternary check
value={epicId ? epicId : 'none'}
```

**Why:** This explicitly checks if `epicId` has a value. If it does, use it. If not (empty string), use 'none'. This ensures the UUID string is always used when it exists.

### 3. Changed Form Reset Logic
```typescript
// ✅ CORRECT - Reset to empty string
setEpicId('')
setSprintId('')
setAssignedTo('')
```

**Why:** Consistent with initial state - empty string means "not set".

### 4. Changed Form Submission Logic
```typescript
// ✅ CORRECT - Check for empty string
epic: epicId ? epicId : null,
sprint: sprintId ? sprintId : null,
assigned_to: assignedTo ? assignedTo : null,
```

**Why:** Empty string is falsy, so `epicId ? epicId : null` correctly sends `null` when empty, and the UUID when set.

### 5. Changed onValueChange Logic
```typescript
// ✅ CORRECT - Convert 'none' to empty string
onValueChange={(value) => {
    setEpicId(value === 'none' ? '' : value)
}}
```

**Why:** When user selects "None", we set it to empty string (consistent with initial state). When they select an option, we set the UUID string.

---

## 📋 Key Changes

### Before:
```typescript
// Initial state
const [epicId, setEpicId] = useState<string>('none')

// Select value
value={epicId || 'none'}

// Form reset
setEpicId('none')

// Form submission
epic: (epicId && epicId !== 'none') ? epicId : null
```

### After:
```typescript
// Initial state
const [epicId, setEpicId] = useState<string>('')

// Select value
value={epicId ? epicId : 'none'}

// Form reset
setEpicId('')

// Form submission
epic: epicId ? epicId : null
```

---

## 🎯 Why This Works

1. **Empty String vs 'none' Distinction:**
   - Empty string (`''`) = "not set yet" or "cleared by user"
   - `'none'` = "explicitly selected 'None' option"
   - UUID string = "has a value"

2. **Explicit Ternary Check:**
   - `epicId ? epicId : 'none'` explicitly checks if epicId has a value
   - If epicId is a UUID string, it uses it
   - If epicId is empty string, it uses 'none'
   - This ensures the Select always receives a valid value that matches a SelectItem

3. **Radix UI Select Requirement:**
   - Radix UI Select requires the `value` prop to **exactly match** one of the SelectItem `value` props
   - If the value doesn't match, the Select resets to the first option or shows placeholder
   - By ensuring we always pass either the UUID (which matches a SelectItem) or 'none' (which matches the "None" SelectItem), the Select displays correctly

---

## 📁 Files Modified

1. **`frontend/src/components/stories/StoryEditModal.tsx`**
   - Changed initial state from `'none'` to `''` (empty string)
   - Changed Select value logic from `epicId || 'none'` to `epicId ? epicId : 'none'`
   - Changed form reset to use empty strings
   - Changed form submission to check for truthy values
   - Changed onValueChange to convert 'none' to empty string
   - Removed all console.log statements

---

## ✅ Result

- ✅ Epic dropdown shows the correct epic when editing
- ✅ Sprint dropdown shows the correct sprint when editing
- ✅ Assignee dropdown shows the correct user when editing
- ✅ All fields populate correctly when the modal opens
- ✅ Form resets correctly when modal closes
- ✅ Form submission sends correct values (UUID or null)

---

**Last Updated:** December 5, 2024  
**Status:** ✅ **COMPLETED**

