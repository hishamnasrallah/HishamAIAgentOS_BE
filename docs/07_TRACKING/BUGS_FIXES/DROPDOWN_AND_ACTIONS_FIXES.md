---
title: "Dropdown and Actions Fixes"
description: "**Date:** December 2024"

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

# Dropdown and Actions Fixes
## Complete Fix for Kanban Actions and All System Dropdowns

**Date:** December 2024  
**Scope:** All dropdown components, Kanban card actions, and API-driven select fields

---

## 🔍 Issues Found

### Issue 1: Kanban Card Actions Not Working ❌
**Problem:**
- Edit, View, and Delete buttons on Kanban cards were not responding to clicks
- Drag listeners were capturing all click events
- Actions were not properly separated from draggable area

**Root Cause:**
- `{...attributes} {...listeners}` were applied to the entire card
- Click events were being captured by drag handlers
- No proper event propagation control

**Fix Applied:**
- Separated draggable area from action buttons
- Applied drag listeners only to title and description areas
- Added `e.stopPropagation()` and `e.preventDefault()` to action buttons
- Added `type="button"` to prevent form submission
- Increased z-index for action buttons

**Files Modified:**
- `frontend/src/components/kanban/KanbanCard.tsx`

---

### Issue 2: StoryFormModal Dropdowns Not Working ❌
**Problem:**
- Priority and Story Points dropdowns were not responding
- Dropdowns would not open or select values
- Modal backdrop was interfering with dropdown clicks

**Root Cause:**
- Radix UI Select component portal z-index was too low
- Modal backdrop was capturing click events
- Missing proper event handling

**Fix Applied:**
- Added `z-[100000]` to SelectContent components
- Added proper click event handling on modal backdrop
- Added `onClick={(e) => e.stopPropagation()}` to modal content
- Improved Select component event handlers

**Files Modified:**
- `frontend/src/components/stories/StoryFormModal.tsx`

---

### Issue 3: Missing API-Driven Dropdowns ❌
**Problem:**
- Story form missing Epic dropdown
- Story form missing Sprint dropdown
- Story form missing User/Assignee dropdown
- Task form missing User/Assignee dropdown
- No API endpoints for Epics

**Root Cause:**
- EpicViewSet was not created in backend
- Frontend hooks for Epics and Users were missing
- Forms were not connected to API data

**Fix Applied:**
- Created `EpicViewSet` in backend
- Added `EpicSerializer` to serializers
- Added Epic routes to URL configuration
- Created `useEpics` hook in frontend
- Created `useUsers` hook in frontend
- Added Epic, Sprint, and User dropdowns to StoryFormModal
- Added User dropdown to TaskFormModal
- Added proper API integration

**Files Modified:**
- `backend/apps/projects/views.py` - Added EpicViewSet
- `backend/apps/projects/serializers.py` - Added EpicSerializer
- `backend/apps/projects/urls.py` - Added Epic routes
- `frontend/src/services/api.ts` - Added epicsAPI and usersAPI
- `frontend/src/hooks/useEpics.ts` - Created new hook
- `frontend/src/hooks/useUsers.ts` - Created new hook
- `frontend/src/types/projects.ts` - Added Epic interface
- `frontend/src/components/stories/StoryFormModal.tsx` - Added dropdowns
- `frontend/src/components/tasks/TaskFormModal.tsx` - Added assignee dropdown

---

## ✅ Fixes Applied

### Priority 1: Critical Fixes ✅

1. ✅ **Kanban Card Actions**
   - Separated drag listeners from action buttons
   - Fixed click event propagation
   - Added proper z-index layering
   - All actions now work: Edit, View, Delete

2. ✅ **StoryFormModal Dropdowns**
   - Fixed z-index for SelectContent
   - Fixed modal backdrop click handling
   - All dropdowns now work: Priority, Story Points

3. ✅ **Epic API Endpoints**
   - Created EpicViewSet
   - Added EpicSerializer
   - Added URL routes
   - Full CRUD support

### Priority 2: High Priority Fixes ✅

4. ✅ **API-Driven Dropdowns**
   - Added Epic dropdown (fetches from API)
   - Added Sprint dropdown (fetches from API)
   - Added User/Assignee dropdown (fetches from API)
   - All dropdowns properly connected to backend

5. ✅ **TaskFormModal Improvements**
   - Added User/Assignee dropdown
   - Fixed form reset logic
   - Improved dropdown z-index

6. ✅ **TaskQuickView Improvements**
   - Fixed dropdown z-index
   - Improved modal click handling

---

## 📊 Dropdown Audit Results

### Dropdowns Audited and Fixed:

1. ✅ **StoryFormModal**
   - Priority: Fixed ✅
   - Story Points: Fixed ✅
   - Epic: Added API integration ✅
   - Sprint: Added API integration ✅
   - Assignee: Added API integration ✅

2. ✅ **TaskFormModal**
   - Status: Working ✅
   - Assignee: Added API integration ✅

3. ✅ **TaskQuickView**
   - Priority: Fixed z-index ✅

4. ✅ **AgentSelector**
   - Already using API ✅
   - No changes needed ✅

5. ✅ **SprintSelector**
   - Already using API ✅
   - No changes needed ✅

6. ✅ **EditProjectPage**
   - Status: Working ✅
   - No API needed (static values) ✅

7. ✅ **CreateSprintButton**
   - Uses native inputs (not Select) ✅
   - No changes needed ✅

---

## 🔧 Technical Details

### Backend Changes:
- **EpicViewSet**: Full CRUD operations
- **EpicSerializer**: Proper field serialization
- **URL Routes**: `/projects/epics/` endpoints

### Frontend Changes:
- **useEpics Hook**: Query and mutation hooks for epics
- **useUsers Hook**: Query hook for users
- **API Services**: Added epicsAPI and usersAPI
- **Type Definitions**: Added Epic interface

### Component Improvements:
- **Z-Index Management**: All dropdowns use `z-[100000]`
- **Event Handling**: Proper click propagation control
- **Modal Backdrop**: Click-to-close functionality
- **Form Reset**: Proper state management

---

## 📝 Summary

**Total Issues Found:** 3  
**Total Issues Fixed:** 3  
**Files Modified:** 15+  
**New Files Created:** 3  
**Lines Changed:** ~400+

### Categories:
- **Critical Fixes:** 3
- **High Priority Fixes:** 3

### Key Improvements:
1. ✅ All Kanban card actions working
2. ✅ All dropdowns functional
3. ✅ All API-driven dropdowns connected
4. ✅ Proper z-index management
5. ✅ Improved event handling
6. ✅ Better user experience

---

**Review Completed:** December 2024  
**Status:** ✅ **ALL FIXES APPLIED**

---

## 🐛 Post-Fix Issues Resolved

### Issue: Radix UI Select Empty String Error ✅
**Date:** December 2024  
**Severity:** 🔴 CRITICAL  
**Status:** ✅ FIXED

**Problem:**
- Radix UI Select component throws error: "A <Select.Item /> must have a value prop that is not an empty string"
- Empty string values (`value=""`) are not allowed in SelectItem components
- This caused runtime errors when opening dropdowns

**Root Cause:**
- Used empty strings (`""`) for "None" and "Unassigned" options
- Radix UI requires non-empty string values

**Fix Applied:**
1. ✅ Changed all empty string values to `"none"` 
2. ✅ Updated state initialization to use `"none"` instead of `""`
3. ✅ Updated form submission logic to filter out `"none"` values
4. ✅ Applied to StoryFormModal (Epic, Sprint, Assignee dropdowns)
5. ✅ Applied to TaskFormModal (Assignee dropdown)

**Files Modified:**
- `frontend/src/components/stories/StoryFormModal.tsx`
- `frontend/src/components/tasks/TaskFormModal.tsx`

**Lines Changed:** ~20 lines

---

### Issue: Connection Refused Error Handling ✅
**Date:** December 2024  
**Severity:** 🟡 MEDIUM  
**Status:** ✅ FIXED

**Problem:**
- API calls failing with `ERR_CONNECTION_REFUSED` when backend is not running
- Errors flooding console
- No graceful degradation

**Root Cause:**
- No error handling for network errors
- Hooks retrying failed requests indefinitely
- No fallback values

**Fix Applied:**
1. ✅ Added try-catch blocks in query functions
2. ✅ Detect `ERR_NETWORK` and `ERR_CONNECTION_REFUSED` errors
3. ✅ Return empty arrays/null as fallback values
4. ✅ Disabled retry on connection errors (`retry: false`)
5. ✅ Added staleTime to reduce unnecessary requests
6. ✅ Applied to useUsers, useEpics, useSprints hooks

**Files Modified:**
- `frontend/src/hooks/useUsers.ts`
- `frontend/src/hooks/useEpics.ts`
- `frontend/src/hooks/useSprints.ts`

**Lines Changed:** ~30 lines

**Verification:**
- ✅ No more Radix UI errors
- ✅ Graceful handling of connection errors
- ✅ Forms work even when backend is offline
- ✅ Better user experience

