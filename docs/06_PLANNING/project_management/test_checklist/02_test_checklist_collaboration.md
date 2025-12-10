# Test Checklist: Collaboration Features

**Category:** Collaboration  
**Features:** Comments, Mentions, Dependencies, Attachments, Watchers, Activity Feed, Edit History  
**Estimated Tests:** ~150  
**Priority:** HIGH

---

## 1. COMMENTS SYSTEM

### 1.1 Comment CRUD Operations

**TC-COMM-001: Create Comment (API)**
- [ ] **Test Case:** Create comment on story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/comments/`
- [ ] **Request Body:**
  ```json
  {
    "story": "story-uuid",
    "content": "This looks good!",
    "parent_comment": null
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Comment created
  - `author` set to current user
  - `created_at` set
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-002: Create Threaded Comment**
- [ ] **Test Case:** Reply to existing comment
- [ ] **Endpoint:** `POST /api/projects/{project_id}/comments/`
- [ ] **Request Body:**
  ```json
  {
    "story": "story-uuid",
    "content": "I agree!",
    "parent_comment": "parent-comment-uuid"
  }
  ```
- [ ] **Expected Result:** 
  - Comment created as reply
  - Thread structure maintained
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-003: List Comments (API)**
- [ ] **Test Case:** Get comments for story
- [ ] **Endpoint:** `GET /api/projects/{project_id}/comments/?story={story_id}`
- [ ] **Expected Result:** 
  - Returns all comments for story
  - Threaded structure preserved
  - Includes author information
  - Ordered by created_at
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-004: Update Comment (API)**
- [ ] **Test Case:** Edit own comment
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/comments/{comment_id}/`
- [ ] **Request Body:** `{"content": "Updated comment"}`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Comment updated
  - `updated_at` set
  - Edit history tracked
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-005: Update Comment - Permission Check**
- [ ] **Test Case:** Try to edit someone else's comment
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/comments/{other_user_comment_id}/`
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-006: Delete Comment (API)**
- [ ] **Test Case:** Delete comment (soft delete)
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/comments/{comment_id}/`
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Comment soft deleted (not removed from DB)
  - Comment marked as deleted
  - Replies preserved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-007: Comment Reactions**
- [ ] **Test Case:** Add reaction to comment
- [ ] **Endpoint:** `POST /api/projects/{project_id}/comments/{comment_id}/react/`
- [ ] **Request Body:** `{"reaction": "👍"}`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Reaction added
  - Reaction count updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-008: Remove Comment Reaction**
- [ ] **Test Case:** Remove own reaction
- [ ] **Endpoint:** `POST /api/projects/{project_id}/comments/{comment_id}/react/`
- [ ] **Request Body:** `{"reaction": "👍"}` (if already reacted)
- [ ] **Expected Result:** 
  - Reaction removed
  - Reaction count decreased
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-009: Comments Section (UI)**
- [ ] **Test Case:** Display comments in UI
- [ ] **Page:** Story view modal or detail page
- [ ] **Steps:**
  1. Open story
  2. Navigate to comments section
  3. Verify comments displayed
  4. Verify threaded structure
- [ ] **Expected Result:** 
  - Comments displayed in chronological order
  - Threaded replies indented
  - Author avatars/names shown
  - Edit/Delete buttons visible for own comments
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-010: Add Comment (UI)**
- [ ] **Test Case:** Add comment via UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Type comment in text area
  2. Click "Post Comment"
  3. Verify comment appears
- [ ] **Expected Result:** 
  - Comment added immediately
  - Text area cleared
  - Comment appears at bottom of list
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-011: Reply to Comment (UI)**
- [ ] **Test Case:** Reply to comment via UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Click "Reply" on a comment
  2. Type reply
  3. Submit
- [ ] **Expected Result:** 
  - Reply created as child comment
  - Threaded structure maintained
  - Reply indented under parent
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-012: Edit Comment (UI)**
- [ ] **Test Case:** Edit comment via UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Click "Edit" on own comment
  2. Modify text
  3. Save
- [ ] **Expected Result:** 
  - Comment updated
  - "Edited" indicator shown
  - Updated timestamp shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMM-013: Comment Reactions UI**
- [ ] **Test Case:** Add reaction via UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Click reaction button on comment
  2. Select emoji
  3. Verify reaction added
- [ ] **Expected Result:** 
  - Reaction button shows emoji picker
  - Selected emoji appears on comment
  - Reaction count updates
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. MENTIONS SYSTEM

### 2.1 Mention Creation

**TC-MENT-001: Create Mention via Comment**
- [ ] **Test Case:** Mention user in comment
- [ ] **Endpoint:** `POST /api/projects/{project_id}/comments/`
- [ ] **Request Body:**
  ```json
  {
    "story": "story-uuid",
    "content": "Hey @user@example.com, can you review this?"
  }
  ```
- [ ] **Expected Result:** 
  - Comment created
  - Mention extracted and created automatically (via signal)
  - Mention linked to user
  - User notified
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-MENT-002: Create Mention via Story Description**
- [ ] **Test Case:** Mention user in story description
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/stories/{story_id}/`
- [ ] **Request Body:**
  ```json
  {
    "description": "Please review @user@example.com"
  }
  ```
- [ ] **Expected Result:** 
  - Story updated
  - Mention extracted and created
  - User notified
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-MENT-003: List Mentions (API)**
- [ ] **Test Case:** Get user's mentions
- [ ] **Endpoint:** `GET /api/projects/{project_id}/mentions/`
- [ ] **Query Params:** `?read=false` (unread only)
- [ ] **Expected Result:** 
  - Returns mentions for current user
  - Includes context (story, comment)
  - Can filter by read status
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-MENT-004: Mark Mention as Read**
- [ ] **Test Case:** Mark mention as read
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/mentions/{mention_id}/`
- [ ] **Request Body:** `{"read": true}`
- [ ] **Expected Result:** 
  - Mention marked as read
  - `read_at` timestamp set
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-MENT-005: Mark All Mentions as Read**
- [ ] **Test Case:** Mark all mentions as read
- [ ] **Endpoint:** `POST /api/projects/{project_id}/mentions/mark-all-read/`
- [ ] **Expected Result:** 
  - All user's mentions marked as read
  - Returns count of marked mentions
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-MENT-006: Mention Input Component (UI)**
- [ ] **Test Case:** Use @mention autocomplete
- [ ] **Page:** Comment form or story form
- [ ] **Steps:**
  1. Type "@" in text field
  2. Verify autocomplete dropdown appears
  3. Select user from dropdown
  4. Verify mention inserted
- [ ] **Expected Result:** 
  - Autocomplete shows project members
  2. Selecting user inserts mention format
  3. Mention highlighted in text
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-MENT-007: Mention Display (UI)**
- [ ] **Test Case:** Display mentions in content
- [ ] **Page:** Story view or comment
- [ ] **Expected Result:** 
  - Mentions highlighted/linked
  - Clicking mention shows user profile or navigates
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-MENT-008: Mentions Notification (UI)**
- [ ] **Test Case:** Show mention notifications
- [ ] **Page:** Notification center or bell icon
- [ ] **Expected Result:** 
  - Unread mentions shown
  - Badge count displayed
  - Clicking opens mention context
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. DEPENDENCIES

### 3.1 Dependency Management

**TC-DEP-001: Create Dependency (API)**
- [ ] **Test Case:** Create dependency between stories
- [ ] **Endpoint:** `POST /api/projects/{project_id}/dependencies/`
- [ ] **Request Body:**
  ```json
  {
    "from_story": "story-1-uuid",
    "to_story": "story-2-uuid",
    "dependency_type": "blocks"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Dependency created
  - Circular dependency check performed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DEP-002: Create Dependency - Circular Check**
- [ ] **Test Case:** Prevent circular dependencies
- [ ] **Endpoint:** `POST /api/projects/{project_id}/dependencies/`
- [ ] **Request Body:**
  ```json
  {
    "from_story": "story-1-uuid",
    "to_story": "story-2-uuid",
    "dependency_type": "blocks"
  }
  ```
- [ ] **Prerequisites:** Story 2 already depends on Story 1
- [ ] **Expected Result:** 
  - Status code: 400 Bad Request
  - Error message about circular dependency
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DEP-003: Check Circular Dependencies (API)**
- [ ] **Test Case:** Check for circular dependencies
- [ ] **Endpoint:** `POST /api/projects/{project_id}/dependencies/check-circular/`
- [ ] **Request Body:**
  ```json
  {
    "from_story": "story-1-uuid",
    "to_story": "story-2-uuid"
  }
  ```
- [ ] **Expected Result:** 
  - Returns whether dependency would create cycle
  - Includes path if cycle exists
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DEP-004: List Dependencies (API)**
- [ ] **Test Case:** Get dependencies for story
- [ ] **Endpoint:** `GET /api/projects/{project_id}/dependencies/?from_story={story_id}`
- [ ] **Expected Result:** 
  - Returns dependencies where story is source
  - Includes dependency type
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DEP-005: List Dependents (API)**
- [ ] **Test Case:** Get stories that depend on this story
- [ ] **Endpoint:** `GET /api/projects/{project_id}/dependencies/?to_story={story_id}`
- [ ] **Expected Result:** 
  - Returns dependencies where story is target
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DEP-006: Delete Dependency (API)**
- [ ] **Test Case:** Remove dependency
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/dependencies/{dependency_id}/`
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Dependency removed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DEP-007: Dependencies Section (UI)**
- [ ] **Test Case:** Display dependencies in UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Navigate to dependencies section
  2. Verify dependencies displayed
  3. Verify dependency types shown (blocks, relates, etc.)
- [ ] **Expected Result:** 
  - Dependencies listed with type badges
  - Clicking dependency navigates to related story
  - "Add Dependency" button visible
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DEP-008: Add Dependency (UI)**
- [ ] **Test Case:** Add dependency via UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Click "Add Dependency"
  2. Search/select target story
  3. Select dependency type
  4. Submit
- [ ] **Expected Result:** 
  - Dependency created
  - Circular dependency warning shown if applicable
  - Dependency appears in list
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DEP-009: Dependency Graph (UI)**
- [ ] **Test Case:** View dependency graph visualization
- [ ] **Page:** Dependency graph component
- [ ] **Steps:**
  1. Open dependency graph
  2. Verify nodes (stories) displayed
  3. Verify edges (dependencies) displayed
  4. Test cycle detection visualization
- [ ] **Expected Result:** 
  - Graph renders correctly
  - Cycles highlighted if present
  - Interactive (zoom, pan, click nodes)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DEP-010: Dependency Impact Analysis**
- [ ] **Test Case:** Analyze impact of dependency changes
- [ ] **Endpoint:** `GET /api/projects/{project_id}/dependencies/{dependency_id}/impact/`
- [ ] **Expected Result:** 
  - Returns affected stories
  - Shows impact chain
  - Estimates effort impact
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. ATTACHMENTS

### 4.1 Attachment Management

**TC-ATT-001: Upload Attachment (API)**
- [ ] **Test Case:** Upload file attachment
- [ ] **Endpoint:** `POST /api/projects/{project_id}/attachments/`
- [ ] **Request:** Multipart form data
  ```
  story: story-uuid
  file: [binary file]
  name: "document.pdf"
  description: "Project requirements"
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - File uploaded to storage
  - Attachment record created
  - File size and type tracked
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ATT-002: Upload Attachment - File Size Validation**
- [ ] **Test Case:** Reject oversized file
- [ ] **Endpoint:** `POST /api/projects/{project_id}/attachments/`
- [ ] **Request:** File > 10MB (or configured limit)
- [ ] **Expected Result:** 
  - Status code: 400 Bad Request
  - Error message about file size limit
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ATT-003: Upload Attachment - File Type Validation**
- [ ] **Test Case:** Reject disallowed file types
- [ ] **Endpoint:** `POST /api/projects/{project_id}/attachments/`
- [ ] **Request:** File with extension .exe or .bat
- [ ] **Expected Result:** 
  - Status code: 400 Bad Request
  - Error message about file type not allowed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ATT-004: List Attachments (API)**
- [ ] **Test Case:** Get attachments for story
- [ ] **Endpoint:** `GET /api/projects/{project_id}/attachments/?story={story_id}`
- [ ] **Expected Result:** 
  - Returns all attachments for story
  - Includes file metadata (size, type, name)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ATT-005: Download Attachment (API)**
- [ ] **Test Case:** Download attachment file
- [ ] **Endpoint:** `GET /api/projects/{project_id}/attachments/{attachment_id}/download/`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - File downloaded
  - Content-Type header correct
  - Content-Disposition header includes filename
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ATT-006: Delete Attachment (API)**
- [ ] **Test Case:** Delete attachment
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/attachments/{attachment_id}/`
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Attachment record deleted
  - File removed from storage
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ATT-007: Attachments Section (UI)**
- [ ] **Test Case:** Display attachments in UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Navigate to attachments section
  2. Verify attachments listed
  3. Verify file icons/types shown
- [ ] **Expected Result:** 
  - Attachments displayed with icons
  - File size shown
  - Upload date shown
  - Download button for each attachment
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ATT-008: Upload Attachment (UI)**
- [ ] **Test Case:** Upload file via UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Click "Upload File" or drag file
  2. Select file
  3. Optionally add name/description
  4. Submit
- [ ] **Expected Result:** 
  - File uploads with progress indicator
  - Attachment appears in list after upload
  - Success message displayed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ATT-009: Image Preview (UI)**
- [ ] **Test Case:** Preview image attachments
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Upload image file
  2. Click on image attachment
- [ ] **Expected Result:** 
  - Image preview opens in modal/lightbox
  - Can zoom/pan if large
  - Download option available
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ATT-010: Download Attachment (UI)**
- [ ] **Test Case:** Download attachment via UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Click download button on attachment
  2. Verify file downloads
- [ ] **Expected Result:** 
  - File downloads to browser
  - Filename preserved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. WATCHERS/SUBSCRIBERS

### 5.1 Watcher Management

**TC-WATCH-001: Add Watcher (API)**
- [ ] **Test Case:** Subscribe to story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/watchers/`
- [ ] **Request Body:**
  ```json
  {
    "story": "story-uuid",
    "user": "user-uuid"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Watcher record created
  - User subscribed to story updates
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WATCH-002: Remove Watcher (API)**
- [ ] **Test Case:** Unsubscribe from story
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/watchers/{watcher_id}/`
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Watcher removed
  - User no longer receives updates
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WATCH-003: List Watchers (API)**
- [ ] **Test Case:** Get watchers for story
- [ ] **Endpoint:** `GET /api/projects/{project_id}/watchers/?story={story_id}`
- [ ] **Expected Result:** 
  - Returns list of users watching story
  - Includes user information
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WATCH-004: Toggle Watch (UI)**
- [ ] **Test Case:** Watch/unwatch story via UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Click "Watch" button
  2. Verify button changes to "Unwatch"
  3. Click again to unwatch
- [ ] **Expected Result:** 
  - Watch state toggles correctly
  - Button text/icon updates
  - User added/removed from watchers
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WATCH-005: Watchers List (UI)**
- [ ] **Test Case:** Display watchers list
- [ ] **Page:** Story view modal
- [ ] **Expected Result:** 
  - Watchers shown as avatars or list
  - Count displayed
  - Clicking watcher shows profile
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 6. ACTIVITY FEED

### 6.1 Activity Tracking

**TC-ACT-001: List Activities (API)**
- [ ] **Test Case:** Get activity feed for story
- [ ] **Endpoint:** `GET /api/projects/{project_id}/activities/?story={story_id}`
- [ ] **Expected Result:** 
  - Returns chronological activity feed
  - Includes all activity types (create, update, comment, status change, etc.)
  - Includes user and timestamp
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ACT-002: Activity Feed (UI)**
- [ ] **Test Case:** Display activity feed
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Navigate to activity tab
  2. Verify activities displayed
- [ ] **Expected Result:** 
  - Activities shown in chronological order
  - Each activity shows user, action, timestamp
  - Icons for different activity types
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 7. EDIT HISTORY

### 7.1 History Tracking

**TC-HIST-001: List Edit History (API)**
- [ ] **Test Case:** Get edit history for story
- [ ] **Endpoint:** `GET /api/projects/{project_id}/edit-history/?story={story_id}`
- [ ] **Expected Result:** 
  - Returns list of edit history records
  - Each record includes changed fields, old values, new values
  - Includes user and timestamp
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-HIST-002: View Edit History (UI)**
- [ ] **Test Case:** Display edit history
- [ ] **Page:** Story view modal or change log component
- [ ] **Steps:**
  1. Navigate to history/changelog section
  2. Verify history displayed
- [ ] **Expected Result:** 
  - History shown in chronological order
  - Changes highlighted (old vs new)
  - User and timestamp for each change
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-HIST-003: Compare Versions (UI)**
- [ ] **Test Case:** Compare two versions
- [ ] **Page:** Change log component
- [ ] **Steps:**
  1. Select two versions
  2. Click "Compare"
- [ ] **Expected Result:** 
  - Side-by-side or diff view shown
  - Changes highlighted
  - Added/removed/modified fields shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - Collaboration Features  
**Total Test Cases:** ~150  
**Next File:** [03_test_checklist_board_features.md](./03_test_checklist_board_features.md)

