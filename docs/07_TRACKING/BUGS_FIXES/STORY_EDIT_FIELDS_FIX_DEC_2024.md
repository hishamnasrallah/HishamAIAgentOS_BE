---
title: "Story Edit Fields Fix - December 2024"
description: "When clicking 'Edit' on a story in the Kanban board, not all related fields (priority, story_points, epic, sprint, assignee) were showing their values in the form modal."

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Developer
  secondary:
    - QA / Tester
    - Project Manager

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

# Story Edit Fields Fix - December 2024

## Problem
When clicking "Edit" on a story in the Kanban board, not all related fields (priority, story_points, epic, sprint, assignee) were showing their values in the form modal.

## Root Cause
1. **Data Flow Issue**: When editing, we fetch fresh data using `useStory`, but during the initial render, `editingStory` might be `undefined` while loading, causing the modal to receive incomplete data.

2. **Field Extraction**: The form population logic needed better handling for different data types (UUID strings vs objects with id property).

3. **Missing Fallback**: The story object from the list wasn't being used as a reliable fallback when the fetched story wasn't available yet.

## Solution

### 1. Enhanced Data Flow (`ProjectDetailPage.tsx`)
- **Added `editingStoryFromList` state**: Stores the complete story object from the list as an immediate fallback
- **Improved `storyForModal` logic**: Uses fetched story if available, otherwise falls back to list story
- **Added debug logging**: Logs what story data is being passed to the modal

```typescript
const [editingStoryFromList, setEditingStoryFromList] = useState<any>(null)

const handleEditStory = (story: any) => {
  setEditingStoryFromList(story) // Store full story object as fallback
  setEditingStoryId(story.id) // Trigger refetch
  setIsStoryModalOpen(true)
}

const storyForModal = editingStoryId 
  ? (editingStory || editingStoryFromList || null)
  : ({ project: id, status: 'backlog' })
```

### 2. Enhanced Field Extraction (`StoryFormModal.tsx`)
- **Better type handling**: Checks if fields are strings, objects with id, or null
- **Explicit null checks**: Handles `null`, `undefined`, and empty values properly
- **Priority validation**: Ensures priority is always a valid choice
- **Enhanced logging**: Logs full story object and field extraction process

```typescript
// Handle epic - can be null, UUID string, or object with id
let epicValue = null
if (story.epic) {
  if (typeof story.epic === 'object' && story.epic.id) {
    epicValue = story.epic.id
  } else if (typeof story.epic === 'string') {
    epicValue = story.epic
  }
}
setEpicId(epicValue ? String(epicValue) : 'none')
```

### 3. Story Points Handling
- **Explicit null/undefined check**: Properly handles `null` and `undefined` values
- **Type conversion**: Safely converts number to string

```typescript
const storyPointsValue = story.story_points !== null && story.story_points !== undefined
  ? story.story_points.toString()
  : ''
setStoryPoints(storyPointsValue)
```

## Files Modified

1. **`frontend/src/pages/projects/ProjectDetailPage.tsx`**
   - Added `editingStoryFromList` state
   - Enhanced `handleEditStory` to store full story object
   - Improved `storyForModal` logic with fallback
   - Added debug logging

2. **`frontend/src/components/stories/StoryFormModal.tsx`**
   - Enhanced field extraction logic for epic, sprint, assigned_to
   - Improved story_points handling
   - Added priority validation
   - Enhanced logging for debugging

## Testing
1. Click "Edit" on a story in the Kanban board
2. Verify all fields populate correctly:
   - Priority dropdown shows correct value
   - Story Points field shows correct number
   - Epic dropdown shows correct selection (or "None")
   - Sprint dropdown shows correct selection (or "None")
   - Assignee dropdown shows correct selection (or "None")
3. Check browser console for debug logs showing:
   - Full story object being loaded
   - Field extraction process
   - Form values being set

## Expected Behavior
- When clicking "Edit", the modal should immediately show all field values from the list story
- When the fresh fetch completes, the modal should update with the latest data
- All fields (priority, story_points, epic, sprint, assignee) should always be populated correctly

## Notes
- The story object from the API list response includes all fields as UUIDs (strings)
- The serializer returns `epic`, `sprint`, and `assigned_to` as UUID strings, not objects
- The `epic_name` and `sprint_name` fields are read-only and provided for display purposes only

