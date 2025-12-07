---
title: "Story Modal Refresh Fix - December 2024"
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

# Story Modal Refresh Fix - December 2024

**Date:** December 5, 2024  
**Status:** ✅ **FIXED**

---

## 🐛 Issue Found

After saving a story, when reopening the modal or clicking "view", the old data was shown instead of the updated data. The user had to refresh the page to see the changes.

**Root Cause:**
1. The modal was using stale story data from the `stories` array
2. When editing, the story object was passed directly from the cached array
3. After update, the query was invalidated, but the modal was still using the old story object
4. The "view" button (TaskQuickView) was also using stale task data

---

## ✅ Fix Applied

### 1. ProjectDetailPage - Fetch Latest Story Data

**File:** `frontend/src/pages/projects/ProjectDetailPage.tsx`

**Changes:**
- Changed from storing the story object to storing the story ID
- Added `useStory` hook to fetch the latest story data when editing
- The modal now always gets fresh data when opened

```typescript
// Before
const [editingStory, setEditingStory] = useState<any>(null)
const handleEditStory = (story: any) => {
    setEditingStory(story) // Stale data
    setIsStoryModalOpen(true)
}

// After
const [editingStoryId, setEditingStoryId] = useState<string | null>(null)
const { data: editingStory } = useStory(editingStoryId || '') // Fresh data
const handleEditStory = (story: any) => {
    setEditingStoryId(story.id) // Trigger refetch
    setIsStoryModalOpen(true)
}
```

### 2. TaskQuickView - Fetch Latest Story Data

**File:** `frontend/src/components/kanban/TaskQuickView.tsx`

**Changes:**
- Added `useStory` hook to fetch latest story data when modal opens
- Form fields update when fresh data arrives
- Uses latest data if available, falls back to task prop

```typescript
// Added
const { data: latestStory } = useStory(task.id)
const storyData = latestStory || task

// Update form when story data changes
useEffect(() => {
    if (storyData && isOpen) {
        setEditedTitle(storyData.title);
        setEditedDescription(storyData.description || '');
        setEditedPriority(storyData.priority || 'medium');
    }
}, [storyData, isOpen]);
```

### 3. StoryFormModal - Improved Form Population

**File:** `frontend/src/components/stories/StoryFormModal.tsx`

**Changes:**
- Enhanced form population to handle UUID strings or objects
- Added better logging to debug form population
- Form now properly handles all field types

---

## 📋 How It Works Now

1. **User clicks Edit/View:**
   - Story ID is stored in state
   - `useStory` hook automatically fetches latest data
   - Modal opens with fresh data

2. **User saves story:**
   - Story is updated in backend
   - `useUpdateStory` invalidates queries:
     - `['stories', projectId]` - Refreshes list
     - `['story', storyId]` - Refreshes single story
   - Modal closes

3. **User reopens modal:**
   - `useStory` hook refetches (because query was invalidated)
   - Modal shows latest data immediately

---

## ✅ Benefits

- ✅ Modal always shows latest data
- ✅ No need to refresh page
- ✅ View button shows updated data
- ✅ Edit button shows updated data
- ✅ Automatic data refresh after save

---

**Last Updated:** December 5, 2024  
**Status:** ✅ **FIXED**

