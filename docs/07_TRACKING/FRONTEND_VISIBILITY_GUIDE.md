# Frontend Visibility Guide - What You Can See and Where

**Date:** December 8, 2024  
**Status:** Updated after frontend integration fixes

---

## ✅ Features You CAN See in the Frontend

### 1. Tags System
- **Where to see:**
  - ✅ **Kanban Cards**: Tags appear as small badges on each story card (shows up to 3 tags, with "+X" for more)
  - ✅ **Story Edit Modal**: TagInput component with autocomplete when editing a story
  - ✅ **Story View Modal**: Tags displayed as badges below the description
  - ✅ **Story Create Modal**: TagInput component when creating a new story

### 2. Comments System
- **Where to see:**
  - ✅ **Story View Modal**: CommentsSection component at the bottom
  - ✅ **Task Quick View**: CommentsSection component (click the eye icon on a Kanban card)
  - **Features visible:**
    - Threaded comments (reply to comments)
    - Comment reactions (emoji)
    - Add/edit/delete comments
    - Mention users in comments (@username)

### 3. Dependencies
- **Where to see:**
  - ✅ **Story View Modal**: DependenciesSection component
  - ✅ **Task Quick View**: DependenciesSection component
  - **Features visible:**
    - Add dependencies (blocks, blocked_by, relates_to, etc.)
    - View existing dependencies
    - Resolve dependencies
    - Circular dependency warnings

### 4. Attachments
- **Where to see:**
  - ✅ **Story View Modal**: AttachmentsSection component
  - ✅ **Task Quick View**: AttachmentsSection component
  - **Features visible:**
    - Upload files (drag-and-drop)
    - View/download attachments
    - Delete attachments
    - Image preview

### 5. User Mentions
- **Where to see:**
  - ✅ **Comments**: Use @username in comments (MentionInput component)
  - ✅ **Story Description**: Mentions are extracted automatically when you save
  - **Note:** Mentions create notifications (see Notifications below)

### 6. Notifications (In-App)
- **Where to see:**
  - ✅ **Header**: Bell icon in the top-right corner
  - ✅ **Notification Center**: Click the bell icon to see all notifications
  - **Features visible:**
    - Unread count badge
    - List of notifications (mentions, comments, status changes, assignments)
    - Mark as read / Mark all as read
    - Auto-refresh every 30 seconds
  - **Note:** Notifications are now connected to backend API

### 7. Swimlanes
- **Where to see:**
  - ✅ **Kanban Board**: Swimlanes appear within each column when configured
  - **How to enable:**
    1. Go to Project Settings
    2. Navigate to "Board Customization"
    3. Select "Swimlane Grouping" (assignee, epic, priority, component, or custom field)
  - **Features visible:**
    - Collapsible swimlanes (click header to expand/collapse)
    - Task count per swimlane
    - Story points total per swimlane
    - Drag-and-drop between swimlanes

---

## ⚠️ Features That Are Backend-Only (Not Visible in UI Yet)

### 1. Automation Rules
- **Status:** Backend complete, Frontend UI pending
- **What works:** Rules execute automatically in the background
- **What's missing:** UI to create/edit automation rules in Project Settings

### 2. Permission Enforcement
- **Status:** Backend complete, Frontend UI pending
- **What works:** Permissions are enforced (you'll get errors if you don't have permission)
- **What's missing:** UI indicators showing what you can/can't do, permission error messages

### 3. Validation Rules
- **Status:** Backend complete, Frontend UI pending
- **What works:** Validation happens when you create/update stories (you'll see errors)
- **What's missing:** UI to configure validation rules in Project Settings, better error display

---

## 📍 How to Access Features

### View Story Details
1. **From Kanban Board:**
   - Click the **eye icon** on a story card → Opens TaskQuickView (has Comments, Dependencies, Attachments)
   - Click the **edit icon** on a story card → Opens StoryEditModal

2. **From Story View Modal:**
   - Some places may have a "View Story" button
   - Shows: Title, Description, Tags, Comments, Dependencies, Attachments

### Configure Swimlanes
1. Navigate to a Project
2. Click **Settings** (gear icon)
3. Go to **Board Customization** section
4. Select **Swimlane Grouping** dropdown
5. Choose: None, Assignee, Epic, Priority, Component, or Custom Field
6. If Custom Field, enter the field name
7. Save configuration
8. Return to Kanban board - swimlanes should appear

### View Notifications
1. Look for **bell icon** in the top-right corner of the header
2. Click it to open Notification Center
3. Red badge shows unread count
4. Click "Mark all read" to mark all as read
5. Notifications auto-refresh every 30 seconds

---

## 🔍 Troubleshooting

### "I don't see swimlanes"
- **Check:** Project Settings → Board Customization → Swimlane Grouping
- **Solution:** Set it to something other than "None" and save

### "I don't see notifications"
- **Check:** Are you logged in? Notifications are user-specific
- **Check:** Have any events occurred? (mentions, comments, status changes)
- **Solution:** Try mentioning yourself in a comment or changing a story status

### "I don't see Comments/Dependencies/Attachments"
- **Check:** Are you viewing a story? Open Story View Modal or Task Quick View
- **Solution:** Click the eye icon on a Kanban card to open TaskQuickView

### "Tags don't appear on cards"
- **Check:** Does the story have tags? Edit the story and add tags
- **Check:** Are tags in the correct format? (array of strings)
- **Solution:** Tags should appear automatically after adding them

---

## 📝 Summary

**What's Visible:**
- ✅ Tags (cards, modals)
- ✅ Comments (story view, task quick view)
- ✅ Dependencies (story view, task quick view)
- ✅ Attachments (story view, task quick view)
- ✅ Mentions (in comments, creates notifications)
- ✅ Notifications (header bell icon)
- ✅ Swimlanes (kanban board, when configured)

**What's Backend-Only:**
- ⚠️ Automation Rules (execute but no UI to configure)
- ⚠️ Permission Settings (enforced but no UI to configure)
- ⚠️ Validation Rules (enforced but no UI to configure)

---

**Last Updated:** December 8, 2024  
**Status:** All visible features integrated and working

