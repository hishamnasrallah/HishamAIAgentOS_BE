# Test Checklist: Advanced Features

**Category:** Advanced Features  
**Features:** Templates, Cloning, Archiving, Versioning, AI Suggestions, Duplicate Detection, Merge, Export/Import  
**Estimated Tests:** ~90  
**Priority:** LOW

---

## 1. TEMPLATES

### 1.1 Card Templates

**TC-ADV-001: Create Card Template**
- [ ] **Test Case:** Create story template
- [ ] **Endpoint:** `POST /api/projects/{project_id}/card-templates/`
- [ ] **Request Body:**
  ```json
  {
    "name": "Bug Report Template",
    "title": "Bug: {title}",
    "description": "Steps to reproduce:\n1. \n2. \n3.",
    "acceptance_criteria": "Bug is fixed and tested",
    "story_type": "bug",
    "priority": "high"
  }
  ```
- [ ] **Expected Result:** 
  - Template created
  - Can be used to create stories
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-002: List Card Templates**
- [ ] **Test Case:** Get templates
- [ ] **Endpoint:** `GET /api/projects/{project_id}/card-templates/`
- [ ] **Expected Result:** 
  - Returns templates for project
  - Includes global templates
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-003: Use Card Template**
- [ ] **Test Case:** Create story from template
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Click "Use Template"
  2. Select template
  3. Verify fields pre-filled
- [ ] **Expected Result:** 
  - Story form pre-filled
  - Can edit before saving
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-004: Board Templates**
- [ ] **Test Case:** Create board template
- [ ] **Endpoint:** `POST /api/projects/{project_id}/board-templates/`
- [ ] **Request Body:**
  ```json
  {
    "name": "Scrum Board",
    "board_columns": [...],
    "swimlane_grouping": "epic"
  }
  ```
- [ ] **Expected Result:** 
  - Template created
  - Can be applied to project
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. STORY CLONING

### 2.1 Clone Operations

**TC-ADV-005: Clone Story**
- [ ] **Test Case:** Clone a story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/clone/`
- [ ] **Request Body:**
  ```json
  {
    "title": "Cloned Story",
    "sprint": "new-sprint-uuid",
    "copy_tasks": true,
    "copy_attachments": false
  }
  ```
- [ ] **Expected Result:** 
  - New story created
  - Data copied from original
  - Tasks copied if requested
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-006: Clone Story UI**
- [ ] **Test Case:** Clone story via UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Click "Clone" button
  2. Configure clone options
  3. Submit
- [ ] **Expected Result:** 
  - Clone dialog works
  - Options configurable
  - Story cloned successfully
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. DUPLICATE DETECTION

### 3.1 Duplicate Finding

**TC-ADV-007: Find Duplicate Stories**
- [ ] **Test Case:** Detect duplicate stories
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/{story_id}/duplicates/`
- [ ] **Expected Result:** 
  - Returns potentially duplicate stories
  - Includes similarity score
  - Ordered by similarity
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-008: Duplicate Detection UI**
- [ ] **Test Case:** View duplicates in UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Click "Find Duplicates"
  2. View duplicate suggestions
- [ ] **Expected Result:** 
  - Duplicates displayed
  - Similarity scores shown
  - Can navigate to duplicates
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. STORY MERGE

### 4.1 Merge Operations

**TC-ADV-009: Merge Stories**
- [ ] **Test Case:** Merge two stories
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/merge/`
- [ ] **Request Body:**
  ```json
  {
    "target_story_id": "other-story-uuid",
    "merge_strategy": "combine",
    "copy_tasks": true,
    "copy_comments": true
  }
  ```
- [ ] **Expected Result:** 
  - Stories merged
  - Data combined according to strategy
  - Source story archived
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-010: Merge Story UI**
- [ ] **Test Case:** Merge stories via UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Click "Merge" button
  2. Select target story
  3. Configure merge options
  4. Submit
- [ ] **Expected Result:** 
  - Merge dialog works
  - Options configurable
  - Merge successful
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. STORY ARCHIVING

### 5.1 Archive Operations

**TC-ADV-011: Archive Story**
- [ ] **Test Case:** Archive a story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/archive/`
- [ ] **Expected Result:** 
  - Story archived
  - Removed from active views
  - Archive record created
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-012: List Archived Stories**
- [ ] **Test Case:** Get archived stories
- [ ] **Endpoint:** `GET /api/projects/{project_id}/story-archives/`
- [ ] **Expected Result:** 
  - Returns archived stories
  - Includes archive date and reason
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-013: Restore Archived Story**
- [ ] **Test Case:** Restore archived story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/story-archives/{archive_id}/restore/`
- [ ] **Expected Result:** 
  - Story restored
  - Appears in active views
  - Archive record updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-014: Archive Story UI**
- [ ] **Test Case:** Archive story via UI
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Click "Archive" button
  2. Confirm archive
- [ ] **Expected Result:** 
  - Story archived
  - Success message shown
  - Story removed from board
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 6. STORY VERSIONING

### 6.1 Version Management

**TC-ADV-015: Create Story Version**
- [ ] **Test Case:** Create version snapshot
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/create-version/`
- [ ] **Request Body:**
  ```json
  {
    "version_name": "v1.0",
    "notes": "Initial version"
  }
  ```
- [ ] **Expected Result:** 
  - Version created
  - Snapshot of current state saved
  - Version record created
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-016: List Story Versions**
- [ ] **Test Case:** Get version history
- [ ] **Endpoint:** `GET /api/projects/{project_id}/story-versions/?story={story_id}`
- [ ] **Expected Result:** 
  - Returns versions for story
  - Ordered by creation date
  - Includes version name and notes
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-017: View Story Version**
- [ ] **Test Case:** View specific version
- [ ] **Endpoint:** `GET /api/projects/{project_id}/story-versions/{version_id}/`
- [ ] **Expected Result:** 
  - Returns version data
  - Includes all story fields at that time
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-018: Compare Versions**
- [ ] **Test Case:** Compare two versions
- [ ] **Page:** Story version history
- [ ] **Steps:**
  1. Select two versions
  2. Click "Compare"
- [ ] **Expected Result:** 
  - Diff view shown
  - Changes highlighted
  - Added/removed/modified fields shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-019: Version History UI**
- [ ] **Test Case:** View version history
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Navigate to version history
  2. View versions
  3. Compare versions
- [ ] **Expected Result:** 
  - Version history displayed
  - Can view and compare versions
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 7. AI SUGGESTIONS

### 7.1 AI Features

**TC-ADV-020: AI Story Suggestions**
- [ ] **Test Case:** Get AI suggestions for story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/ai-suggestions/`
- [ ] **Request Body:**
  ```json
  {
    "suggestion_type": "all"
  }
  ```
- [ ] **Expected Result:** 
  - Returns suggestions for:
    - Title improvements
    - Acceptance criteria
    - Story points
    - Related stories
    - Tags
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-021: AI Title Suggestions**
- [ ] **Test Case:** Get title suggestions
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/ai-suggestions/`
- [ ] **Request Body:** `{"suggestion_type": "title"}`
- [ ] **Expected Result:** 
  - Returns improved title suggestions
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-022: AI Acceptance Criteria Suggestions**
- [ ] **Test Case:** Get criteria suggestions
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/ai-suggestions/`
- [ ] **Request Body:** `{"suggestion_type": "criteria"}`
- [ ] **Expected Result:** 
  - Returns acceptance criteria suggestions
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-023: AI Story Points Suggestions**
- [ ] **Test Case:** Get story points estimate
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/ai-suggestions/`
- [ ] **Request Body:** `{"suggestion_type": "points"}`
- [ ] **Expected Result:** 
  - Returns story points estimate
  - Based on description and complexity
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-024: AI Suggestions UI**
- [ ] **Test Case:** Use AI suggestions in UI
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Click "Get AI Suggestions"
  2. View suggestions
  3. Apply suggestions
- [ ] **Expected Result:** 
  - Suggestions displayed
  - Can apply individually
  - Can apply all
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 8. EXPORT/IMPORT

### 8.1 Export

**TC-ADV-025: Export Project to CSV**
- [ ] **Test Case:** Export project data
- [ ] **Endpoint:** `GET /api/projects/{project_id}/export/?format=csv`
- [ ] **Expected Result:** 
  - CSV file downloaded
  - Contains all project data (stories, tasks, etc.)
  - Format correct
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-026: Export Project to Excel**
- [ ] **Test Case:** Export to Excel format
- [ ] **Endpoint:** `GET /api/projects/{project_id}/export/?format=xlsx`
- [ ] **Expected Result:** 
  - Excel file downloaded
  - Multiple sheets if needed
  - Format correct
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-027: Export UI**
- [ ] **Test Case:** Export via UI
- [ ] **Page:** Project settings or project page
- [ ] **Steps:**
  1. Click "Export" button
  2. Select format
  3. Download
- [ ] **Expected Result:** 
  - Export dialog works
  - Format selection works
  - File downloads
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 8.2 Import

**TC-ADV-028: Import Project from CSV**
- [ ] **Test Case:** Import project data
- [ ] **Endpoint:** `POST /api/projects/{project_id}/import/`
- [ ] **Request:** Multipart form with CSV file
- [ ] **Expected Result:** 
  - Data imported
  - Returns import summary
  - Errors reported if any
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-029: Import Validation**
- [ ] **Test Case:** Validate import data
- [ ] **Endpoint:** `POST /api/projects/{project_id}/import/validate/`
- [ ] **Request:** CSV file
- [ ] **Expected Result:** 
  - Validation results returned
  - Errors and warnings listed
  - Preview of data to import
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-030: Import UI**
- [ ] **Test Case:** Import via UI
- [ ] **Page:** Project settings
- [ ] **Steps:**
  1. Click "Import" button
  2. Select CSV file
  3. Review validation
  4. Confirm import
- [ ] **Expected Result:** 
  - Import dialog works
  - File upload works
  - Validation shown
  - Import successful
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 9. CARD ENHANCEMENTS

### 9.1 Card Features

**TC-ADV-031: Card Cover Images**
- [ ] **Test Case:** Add cover image to card
- [ ] **Endpoint:** `POST /api/projects/{project_id}/card-cover-images/`
- [ ] **Request:** Multipart form with image
- [ ] **Expected Result:** 
  - Cover image uploaded
  - Image displayed on card
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-032: Card Checklists**
- [ ] **Test Case:** Add checklist to card
- [ ] **Endpoint:** `POST /api/projects/{project_id}/card-checklists/`
- [ ] **Request Body:**
  ```json
  {
    "story": "story-uuid",
    "items": [
      {"text": "Task 1", "completed": false},
      {"text": "Task 2", "completed": false}
    ]
  }
  ```
- [ ] **Expected Result:** 
  - Checklist created
  - Items can be checked/unchecked
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-033: Card Voting**
- [ ] **Test Case:** Vote on card
- [ ] **Endpoint:** `POST /api/projects/{project_id}/card-votes/`
- [ ] **Request Body:**
  ```json
  {
    "story": "story-uuid",
    "vote": "up"
  }
  ```
- [ ] **Expected Result:** 
  - Vote recorded
  - Vote count updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ADV-034: Card Vote Summary**
- [ ] **Test Case:** Get vote summary
- [ ] **Endpoint:** `GET /api/projects/{project_id}/card-votes/summary/?story={story_id}`
- [ ] **Expected Result:** 
  - Returns vote counts
  - Shows up/down votes
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - Advanced Features  
**Total Test Cases:** ~90  
**Next File:** [12_test_checklist_permissions.md](./12_test_checklist_permissions.md)

