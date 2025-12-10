# Test Checklist: Core Entities

**Category:** Core Entities  
**Features:** Projects, Epics, User Stories, Tasks, Bugs, Issues, Sprints  
**Estimated Tests:** ~200  
**Priority:** HIGH (Test First)

---

## 1. PROJECT MANAGEMENT

### 1.1 Project CRUD Operations

#### Backend API Tests

**TC-PROJ-001: Create Project**
- [ ] **Test Case:** Create a new project via API
- [ ] **Endpoint:** `POST /api/projects/`
- [ ] **Request Body:**
  ```json
  {
    "name": "Test Project",
    "slug": "test-project",
    "description": "Test project description",
    "status": "planning",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Response contains project data with UUID
  - `owner` is automatically set to current user
  - `created_by` is set to current user
  - `created_at` and `updated_at` are set
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-002: Create Project - Missing Required Fields**
- [ ] **Test Case:** Attempt to create project without required fields
- [ ] **Endpoint:** `POST /api/projects/`
- [ ] **Request Body:** `{"name": ""}` or `{}`
- [ ] **Expected Result:** 
  - Status code: 400 Bad Request
  - Error messages for missing required fields (name, slug)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-003: Create Project - Duplicate Slug**
- [ ] **Test Case:** Create project with existing slug
- [ ] **Endpoint:** `POST /api/projects/`
- [ ] **Request Body:** `{"name": "Test", "slug": "existing-slug"}`
- [ ] **Expected Result:** 
  - Status code: 400 Bad Request
  - Error message about duplicate slug
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-004: List Projects**
- [ ] **Test Case:** Get list of projects
- [ ] **Endpoint:** `GET /api/projects/`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns list of projects user has access to (owner or member)
  - Projects include all fields (id, name, slug, description, status, dates, owner, members, tags)
  - Pagination if many projects
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-005: List Projects - Filter by Status**
- [ ] **Test Case:** Filter projects by status
- [ ] **Endpoint:** `GET /api/projects/?status=active`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns only projects with status='active'
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-006: List Projects - Filter by Tags**
- [ ] **Test Case:** Filter projects by tags
- [ ] **Endpoint:** `GET /api/projects/?tags=urgent,important`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns only projects containing those tags
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-007: Retrieve Project**
- [ ] **Test Case:** Get single project details
- [ ] **Endpoint:** `GET /api/projects/{project_id}/`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns complete project data
  - Includes related data (owner, members)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-008: Retrieve Project - Not Found**
- [ ] **Test Case:** Get non-existent project
- [ ] **Endpoint:** `GET /api/projects/{invalid_uuid}/`
- [ ] **Expected Result:** 
  - Status code: 404 Not Found
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-009: Retrieve Project - No Access**
- [ ] **Test Case:** Get project user is not member of
- [ ] **Endpoint:** `GET /api/projects/{other_project_id}/`
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden or 404 Not Found
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-010: Update Project (PUT)**
- [ ] **Test Case:** Full update of project
- [ ] **Endpoint:** `PUT /api/projects/{project_id}/`
- [ ] **Request Body:**
  ```json
  {
    "name": "Updated Project",
    "slug": "updated-project",
    "description": "Updated description",
    "status": "active"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - All fields updated
  - `updated_by` set to current user
  - `updated_at` timestamp updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-011: Update Project (PATCH)**
- [ ] **Test Case:** Partial update of project
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/`
- [ ] **Request Body:** `{"status": "active"}`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Only specified fields updated
  - Other fields unchanged
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-012: Update Project - Permission Check**
- [ ] **Test Case:** Non-owner tries to update project
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/`
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden (if not owner/admin)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-013: Delete Project**
- [ ] **Test Case:** Delete a project
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/`
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Project deleted from database
  - Related entities (stories, tasks, etc.) handled according to CASCADE rules
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-014: Delete Project - Permission Check**
- [ ] **Test Case:** Non-owner tries to delete project
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/`
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

#### Frontend UI Tests

**TC-PROJ-015: Create Project Form**
- [ ] **Test Case:** Create project via UI form
- [ ] **Page:** `/projects/create` or Create Project modal
- [ ] **Steps:**
  1. Navigate to create project page
  2. Fill in all required fields (name, slug)
  3. Optionally fill optional fields (description, dates, tags)
  4. Click "Create" button
- [ ] **Expected Result:** 
  - Form submits successfully
  - Redirects to project detail page
  - Success message displayed
  - Project appears in projects list
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-016: Create Project Form - Validation**
- [ ] **Test Case:** Form validation for required fields
- [ ] **Page:** Create project form
- [ ] **Steps:**
  1. Try to submit form with empty name
  2. Try to submit form with invalid slug (spaces, special chars)
  3. Try to submit form with duplicate slug
- [ ] **Expected Result:** 
  - Validation errors displayed inline
  - Form does not submit
  - Error messages are clear and helpful
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-017: Projects List Page**
- [ ] **Test Case:** Display projects list
- [ ] **Page:** `/projects`
- [ ] **Steps:**
  1. Navigate to projects page
  2. Verify projects are displayed
  3. Check pagination if many projects
- [ ] **Expected Result:** 
  - All accessible projects displayed
  - Projects show key information (name, status, owner, dates)
  - Clicking project navigates to detail page
  - "Create Project" button visible (if user has permission)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-018: Projects List - Filtering**
- [ ] **Test Case:** Filter projects in UI
- [ ] **Page:** `/projects`
- [ ] **Steps:**
  1. Use status filter dropdown
  2. Use tag filter
  3. Use search box
- [ ] **Expected Result:** 
  - Filters apply correctly
  - Results update in real-time or after applying
  - Clear filters button works
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-019: Project Detail Page**
- [ ] **Test Case:** Display project details
- [ ] **Page:** `/projects/{project_id}`
- [ ] **Steps:**
  1. Navigate to project detail page
  2. Verify all project information displayed
  3. Check tabs/sections (Overview, Stories, Tasks, etc.)
- [ ] **Expected Result:** 
  - All project fields displayed correctly
  - Related data accessible (stories, tasks, sprints)
  - Edit button visible (if user has permission)
  - Delete button visible (if user has permission)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-020: Edit Project Form**
- [ ] **Test Case:** Edit project via UI
- [ ] **Page:** `/projects/{project_id}/edit`
- [ ] **Steps:**
  1. Navigate to edit page
  2. Modify fields
  3. Save changes
- [ ] **Expected Result:** 
  - Form pre-filled with current values
  - Changes saved successfully
  - Redirects to detail page
  - Success message displayed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.2 Project Members Management

**TC-PROJ-021: Add Project Member (API)**
- [ ] **Test Case:** Add member to project via API
- [ ] **Endpoint:** `POST /api/projects/{project_id}/members/add/`
- [ ] **Request Body:** `{"user_id": "uuid"}`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - User added to project.members
  - User can now access project
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-022: Remove Project Member (API)**
- [ ] **Test Case:** Remove member from project via API
- [ ] **Endpoint:** `POST /api/projects/{project_id}/members/remove/`
- [ ] **Request Body:** `{"user_id": "uuid"}`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - User removed from project.members
  - User loses access to project
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-023: List Project Members (API)**
- [ ] **Test Case:** Get project members list
- [ ] **Endpoint:** `GET /api/projects/{project_id}/members/`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns list of users (owner + members)
  - Each user includes id, email, name
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-024: Add Project Member (UI)**
- [ ] **Test Case:** Add member via UI
- [ ] **Page:** Project settings or collaborators page
- [ ] **Steps:**
  1. Navigate to members section
  2. Click "Add Member"
  3. Search/select user
  4. Confirm addition
- [ ] **Expected Result:** 
  - User added successfully
  - User appears in members list
  - Success message displayed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-025: Remove Project Member (UI)**
- [ ] **Test Case:** Remove member via UI
- [ ] **Page:** Project settings or collaborators page
- [ ] **Steps:**
  1. Find member in list
  2. Click remove/delete button
  3. Confirm removal
- [ ] **Expected Result:** 
  - User removed successfully
  - User disappears from members list
  - Success message displayed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.3 Project Tags

**TC-PROJ-026: Add Tags to Project (API)**
- [ ] **Test Case:** Add tags via API update
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/`
- [ ] **Request Body:** `{"tags": ["urgent", "important"]}`
- [ ] **Expected Result:** 
  - Tags saved as JSON array
  - Tags can be retrieved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-027: Get Project Tags (API)**
- [ ] **Test Case:** Get all tags used in projects
- [ ] **Endpoint:** `GET /api/projects/tags/`
- [ ] **Expected Result:** 
  - Returns list of unique tags across all accessible projects
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-028: Tag Autocomplete (API)**
- [ ] **Test Case:** Get tag suggestions
- [ ] **Endpoint:** `GET /api/projects/tags/autocomplete/?q=urg`
- [ ] **Expected Result:** 
  - Returns tags matching query
  - Results limited and relevant
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-029: Tag Input Component (UI)**
- [ ] **Test Case:** Use tag input in project form
- [ ] **Page:** Create/Edit project form
- [ ] **Steps:**
  1. Type in tag input field
  2. Verify autocomplete suggestions appear
  3. Select or create new tag
  4. Verify tags display as chips/badges
- [ ] **Expected Result:** 
  - Autocomplete works smoothly
  - Tags can be added and removed
  - Visual feedback for tags
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.4 Project Custom Actions

**TC-PROJ-030: Generate Stories (API)**
- [ ] **Test Case:** Generate stories using AI
- [ ] **Endpoint:** `POST /api/projects/{project_id}/generate-stories/`
- [ ] **Request Body:**
  ```json
  {
    "product_vision": "Build a task management app",
    "context": {},
    "epic_id": "optional-uuid"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 200 or 201
  - Returns array of generated stories
  - Stories created in database
  - Stories linked to project (and epic if provided)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-031: Get Project Velocity (API)**
- [ ] **Test Case:** Get velocity metrics
- [ ] **Endpoint:** `GET /api/projects/{project_id}/velocity/?num_sprints=5`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns velocity data (average story points per sprint, trends)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-032: Export Project (API)**
- [ ] **Test Case:** Export project data
- [ ] **Endpoint:** `GET /api/projects/{project_id}/export/?format=csv`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns CSV/Excel file
  - Contains all project data (stories, tasks, etc.)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PROJ-033: Import Project (API)**
- [ ] **Test Case:** Import project data
- [ ] **Endpoint:** `POST /api/projects/{project_id}/import/`
- [ ] **Request:** Multipart form with CSV file
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Data imported successfully
  - Returns import summary
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. EPIC MANAGEMENT

### 2.1 Epic CRUD Operations

**TC-EPIC-001: Create Epic (API)**
- [ ] **Test Case:** Create new epic
- [ ] **Endpoint:** `POST /api/projects/{project_id}/epics/`
- [ ] **Request Body:**
  ```json
  {
    "title": "User Authentication",
    "description": "Epic for authentication features",
    "status": "planned",
    "start_date": "2024-01-01",
    "target_date": "2024-03-31",
    "owner": "user-uuid",
    "tags": ["auth", "security"]
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Epic created with UUID
  - Linked to project
  - `created_by` set to current user
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-EPIC-002: List Epics (API)**
- [ ] **Test Case:** Get epics for project
- [ ] **Endpoint:** `GET /api/projects/{project_id}/epics/`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns list of epics for project
  - Can filter by status, owner, tags
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-EPIC-003: Retrieve Epic (API)**
- [ ] **Test Case:** Get single epic
- [ ] **Endpoint:** `GET /api/projects/{project_id}/epics/{epic_id}/`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns complete epic data
  - Includes related stories count
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-EPIC-004: Update Epic (API)**
- [ ] **Test Case:** Update epic
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/epics/{epic_id}/`
- [ ] **Request Body:** `{"status": "in_progress"}`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Epic updated
  - `updated_by` and `updated_at` updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-EPIC-005: Delete Epic (API)**
- [ ] **Test Case:** Delete epic
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/epics/{epic_id}/`
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Epic deleted
  - Related stories handled (CASCADE or SET_NULL)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-EPIC-006: Epic Form (UI)**
- [ ] **Test Case:** Create/edit epic via UI
- [ ] **Page:** Epics page or modal
- [ ] **Steps:**
  1. Fill epic form (title, description, status, dates, owner, tags)
  2. Submit form
- [ ] **Expected Result:** 
  - Form validates correctly
  - Epic created/updated
  - Success message displayed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-EPIC-007: Epics List Page (UI)**
- [ ] **Test Case:** Display epics list
- [ ] **Page:** `/projects/{project_id}/epics`
- [ ] **Steps:**
  1. Navigate to epics page
  2. Verify epics displayed
  3. Test filtering by status, owner
- [ ] **Expected Result:** 
  - Epics displayed in list/card view
  - Filtering works
  - Clicking epic opens detail view
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-EPIC-008: Epic Owner Filtering**
- [ ] **Test Case:** Filter epics by owner
- [ ] **Endpoint:** `GET /api/projects/{project_id}/epics/?owner={user_id}`
- [ ] **Expected Result:** 
  - Returns only epics owned by specified user
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. USER STORY MANAGEMENT

### 3.1 Story CRUD Operations

**TC-STORY-001: Create Story (API)**
- [ ] **Test Case:** Create new user story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/`
- [ ] **Request Body:**
  ```json
  {
    "title": "As a user, I want to login",
    "description": "User should be able to login with email and password",
    "acceptance_criteria": "1. User enters email\n2. User enters password\n3. System validates credentials",
    "story_type": "feature",
    "priority": "high",
    "story_points": 5,
    "status": "todo",
    "epic": "epic-uuid",
    "sprint": "sprint-uuid",
    "assigned_to": "user-uuid",
    "due_date": "2024-12-31",
    "component": "authentication",
    "labels": [{"name": "urgent", "color": "#ff0000"}],
    "tags": ["auth", "login"]
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Story created with all fields
  - Linked to project, epic, sprint if provided
  - `created_by` set to current user
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-002: Create Story - Validation**
- [ ] **Test Case:** Validate story points against project configuration
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/`
- [ ] **Request Body:** `{"title": "Test", "story_points": 100}` (if max is 20)
- [ ] **Expected Result:** 
  - Status code: 400 Bad Request
  - Error message about story points exceeding limit
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-003: List Stories (API)**
- [ ] **Test Case:** Get stories for project
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/`
- [ ] **Query Params:** Can filter by status, priority, epic, sprint, assignee, component, labels, tags, story_type, due_date
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns paginated list of stories
  - Filters work correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-004: Retrieve Story (API)**
- [ ] **Test Case:** Get single story
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/{story_id}/`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns complete story data
  - Includes related data (epic, sprint, tasks, comments, etc.)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-005: Update Story Status**
- [ ] **Test Case:** Update story status
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/stories/{story_id}/`
- [ ] **Request Body:** `{"status": "in_progress"}`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Status updated
  - Status change validated against workflow rules
  - Automation rules triggered if configured
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-006: Update Story - Invalid Status Transition**
- [ ] **Test Case:** Try invalid status transition
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/stories/{story_id}/`
- [ ] **Request Body:** `{"status": "done"}` (from "todo", if transition not allowed)
- [ ] **Expected Result:** 
  - Status code: 400 Bad Request
  - Error message about invalid transition
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-007: Delete Story (API)**
- [ ] **Test Case:** Delete story
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/stories/{story_id}/`
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Story deleted
  - Related tasks handled (CASCADE or SET_NULL)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-008: Story Form (UI)**
- [ ] **Test Case:** Create/edit story via UI
- [ ] **Page:** Story form modal or page
- [ ] **Steps:**
  1. Fill all story fields
  2. Use rich text editor for description
  3. Add labels, tags, component
  4. Select epic, sprint, assignee
  5. Submit form
- [ ] **Expected Result:** 
  - Form validates correctly
  - Rich text editor works
  - All fields save correctly
  - Success message displayed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-009: Story View Modal (UI)**
- [ ] **Test Case:** View story details
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Open story from board/list
  2. Verify all information displayed
  3. Check tabs (Details, Tasks, Comments, Attachments, etc.)
- [ ] **Expected Result:** 
  - All story data displayed correctly
  - Rich text rendered properly
  - Related data accessible
  - Edit/Delete buttons visible (if permissions allow)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-010: Story Type Filtering**
- [ ] **Test Case:** Filter stories by type
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?story_type=feature`
- [ ] **Expected Result:** 
  - Returns only stories of specified type
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-011: Story Type Statistics**
- [ ] **Test Case:** Get story type distribution
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/story-types/`
- [ ] **Expected Result:** 
  - Returns count of stories by type
  - Includes percentages
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-012: Story Cloning**
- [ ] **Test Case:** Clone a story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/clone/`
- [ ] **Request Body:** `{"title": "Cloned Story", "sprint": "new-sprint-uuid"}`
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - New story created with copied data
  - Tasks, attachments, etc. optionally copied
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-013: Story Duplicate Detection**
- [ ] **Test Case:** Find duplicate stories
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/{story_id}/duplicates/`
- [ ] **Expected Result:** 
  - Returns list of potentially duplicate stories
  - Similarity score included
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-014: Story Merge**
- [ ] **Test Case:** Merge two stories
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/merge/`
- [ ] **Request Body:** `{"target_story_id": "other-story-uuid", "merge_strategy": "combine"}`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Stories merged according to strategy
  - Source story archived or deleted
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-015: Story Archive**
- [ ] **Test Case:** Archive a story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/archive/`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Story archived
  - Story removed from active views
  - Can be restored later
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-016: Story Versioning**
- [ ] **Test Case:** Create story version
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/create-version/`
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Version snapshot created
  - Can view version history
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STORY-017: AI Story Suggestions**
- [ ] **Test Case:** Get AI suggestions for story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/{story_id}/ai-suggestions/`
- [ ] **Request Body:** `{"suggestion_type": "all"}`
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Returns suggestions for title, criteria, points, tags, related stories
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. TASK MANAGEMENT

### 4.1 Task CRUD Operations

**TC-TASK-001: Create Task (API)**
- [ ] **Test Case:** Create new task
- [ ] **Endpoint:** `POST /api/projects/{project_id}/tasks/`
- [ ] **Request Body:**
  ```json
  {
    "title": "Implement login form",
    "description": "Create login form component",
    "status": "todo",
    "priority": "high",
    "story": "story-uuid",
    "parent_task": null,
    "assigned_to": "user-uuid",
    "due_date": "2024-12-31",
    "estimated_hours": 8,
    "component": "authentication",
    "labels": [{"name": "frontend", "color": "#00ff00"}],
    "tags": ["ui", "form"],
    "progress_percentage": 0
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Task created with all fields
  - Can be standalone (story=null) or linked to story
  - Can have parent_task for subtasks
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TASK-002: Create Standalone Task**
- [ ] **Test Case:** Create task without story (standalone)
- [ ] **Endpoint:** `POST /api/projects/{project_id}/tasks/`
- [ ] **Request Body:** `{"title": "Standalone Task", "story": null}`
- [ ] **Expected Result:** 
  - Task created successfully
  - Task not linked to any story
  - Task appears in project tasks list
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TASK-003: Create Subtask**
- [ ] **Test Case:** Create subtask with parent_task
- [ ] **Endpoint:** `POST /api/projects/{project_id}/tasks/`
- [ ] **Request Body:** `{"title": "Subtask", "parent_task": "parent-task-uuid"}`
- [ ] **Expected Result:** 
  - Subtask created
  - Linked to parent task
  - Circular reference validation prevents parent being subtask of child
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TASK-004: List Tasks (API)**
- [ ] **Test Case:** Get tasks for project
- [ ] **Endpoint:** `GET /api/projects/{project_id}/tasks/`
- [ ] **Query Params:** Filter by status, priority, assignee, story, component, labels, tags, due_date
- [ ] **Expected Result:** 
  - Returns all tasks (standalone + story tasks)
  - Filters work correctly
  - Pagination works
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TASK-005: Retrieve Task (API)**
- [ ] **Test Case:** Get single task
- [ ] **Endpoint:** `GET /api/projects/{project_id}/tasks/{task_id}/`
- [ ] **Expected Result:** 
  - Returns complete task data
  - Includes parent_task and subtasks if applicable
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TASK-006: Update Task Progress**
- [ ] **Test Case:** Update task progress percentage
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/tasks/{task_id}/`
- [ ] **Request Body:** `{"progress_percentage": 50}`
- [ ] **Expected Result:** 
  - Progress updated
  - Validated to be 0-100
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TASK-007: Delete Task (API)**
- [ ] **Test Case:** Delete task
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/tasks/{task_id}/`
- [ ] **Expected Result:** 
  - Task deleted
  - Subtasks handled (CASCADE or SET_NULL)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TASK-008: Task Form (UI)**
- [ ] **Test Case:** Create/edit task via UI
- [ ] **Page:** Task form modal
- [ ] **Steps:**
  1. Fill task form
  2. Select story (optional)
  3. Select parent task (optional)
  4. Set progress
  5. Submit
- [ ] **Expected Result:** 
  - Form validates correctly
  - All fields save
  - Success message displayed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TASK-009: Task Hierarchy View (UI)**
- [ ] **Test Case:** Display tasks in hierarchy
- [ ] **Page:** `/projects/{project_id}/tasks` (hierarchy view)
- [ ] **Steps:**
  1. Toggle to hierarchy view
  2. Verify parent-child relationships displayed
  3. Test expand/collapse
  4. Test "Create Subtask" button
- [ ] **Expected Result:** 
  - Tasks displayed in tree structure
  - Expand/collapse works
  - Subtask creation works from hierarchy
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TASK-010: Task Flat View (UI)**
- [ ] **Test Case:** Display tasks in flat list
- [ ] **Page:** `/projects/{project_id}/tasks` (flat view)
- [ ] **Expected Result:** 
  - All tasks displayed in flat list
  - Filters work
  - Sorting works
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. BUG MANAGEMENT

### 5.1 Bug CRUD Operations

**TC-BUG-001: Create Bug (API)**
- [ ] **Test Case:** Create new bug
- [ ] **Endpoint:** `POST /api/projects/{project_id}/bugs/`
- [ ] **Request Body:**
  ```json
  {
    "title": "Login button not working",
    "description": "Login button does nothing when clicked",
    "status": "new",
    "severity": "high",
    "priority": "p1",
    "assigned_to": "user-uuid",
    "reported_by": "user-uuid",
    "due_date": "2024-12-31",
    "component": "authentication",
    "labels": [{"name": "critical", "color": "#ff0000"}],
    "tags": ["bug", "login"],
    "steps_to_reproduce": "1. Go to login page\n2. Click login button\n3. Nothing happens",
    "expected_behavior": "Should redirect to dashboard",
    "actual_behavior": "No response"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Bug created with all fields
  - `reported_by` set to current user if not specified
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUG-002: List Bugs (API)**
- [ ] **Test Case:** Get bugs for project
- [ ] **Endpoint:** `GET /api/projects/{project_id}/bugs/`
- [ ] **Query Params:** Filter by status, severity, priority, assignee, component, labels, tags
- [ ] **Expected Result:** 
  - Returns all bugs
  - Filters work correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUG-003: Update Bug Status**
- [ ] **Test Case:** Update bug status (e.g., to resolved)
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/bugs/{bug_id}/`
- [ ] **Request Body:** `{"status": "resolved", "resolution": "fixed"}`
- [ ] **Expected Result:** 
  - Status and resolution updated
  - Resolution required when status is resolved/closed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUG-004: Bug Form (UI)**
- [ ] **Test Case:** Create/edit bug via UI
- [ ] **Page:** Bug form modal
- [ ] **Steps:**
  1. Fill bug form
  2. Set severity and priority
  3. Add steps to reproduce
  4. Submit
- [ ] **Expected Result:** 
  - Form validates correctly
  - All fields save
  - Success message displayed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUG-005: Bugs Page (UI)**
- [ ] **Test Case:** Display bugs list
- [ ] **Page:** `/projects/{project_id}/bugs`
- [ ] **Expected Result:** 
  - Bugs displayed in list/card view
  - Filtering by severity, priority works
  - Clicking bug opens detail view
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 6. ISSUE MANAGEMENT

### 6.1 Issue CRUD Operations

**TC-ISSUE-001: Create Issue (API)**
- [ ] **Test Case:** Create new issue
- [ ] **Endpoint:** `POST /api/projects/{project_id}/issues/`
- [ ] **Request Body:**
  ```json
  {
    "title": "Add dark mode support",
    "description": "Users want dark mode theme",
    "type": "feature_request",
    "status": "open",
    "priority": "major",
    "assigned_to": "user-uuid",
    "due_date": "2024-12-31",
    "component": "ui",
    "labels": [{"name": "enhancement", "color": "#0000ff"}],
    "tags": ["ui", "theme"]
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Issue created with all fields
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ISSUE-002: List Issues (API)**
- [ ] **Test Case:** Get issues for project
- [ ] **Endpoint:** `GET /api/projects/{project_id}/issues/`
- [ ] **Query Params:** Filter by type, status, priority, assignee, component
- [ ] **Expected Result:** 
  - Returns all issues
  - Filters work correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ISSUE-003: Issue Form (UI)**
- [ ] **Test Case:** Create/edit issue via UI
- [ ] **Page:** Issue form modal
- [ ] **Expected Result:** 
  - Form validates correctly
  - Issue type dropdown works
  - All fields save
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ISSUE-004: Issues Page (UI)**
- [ ] **Test Case:** Display issues list
- [ ] **Page:** `/projects/{project_id}/issues`
- [ ] **Expected Result:** 
  - Issues displayed
  - Filtering by type works
  - Clicking issue opens detail view
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 7. SPRINT MANAGEMENT

### 7.1 Sprint CRUD Operations

**TC-SPRINT-001: Create Sprint (API)**
- [ ] **Test Case:** Create new sprint
- [ ] **Endpoint:** `POST /api/projects/{project_id}/sprints/`
- [ ] **Request Body:**
  ```json
  {
    "name": "Sprint 1",
    "sprint_number": 1,
    "goal": "Complete authentication features",
    "status": "planned",
    "start_date": "2024-01-01",
    "end_date": "2024-01-14"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Sprint created
  - `sprint_number` auto-incremented if not provided
  - Dates validated (end_date > start_date)
  - Default duration applied from project config if dates not provided
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SPRINT-002: Create Sprint - Auto Numbering**
- [ ] **Test Case:** Sprint number auto-incremented
- [ ] **Endpoint:** `POST /api/projects/{project_id}/sprints/`
- [ ] **Request Body:** `{"name": "Sprint", "start_date": "2024-01-01", "end_date": "2024-01-14"}`
- [ ] **Expected Result:** 
  - Sprint number set to next available number for project
  - No duplicate sprint numbers
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SPRINT-003: List Sprints (API)**
- [ ] **Test Case:** Get sprints for project
- [ ] **Endpoint:** `GET /api/projects/{project_id}/sprints/`
- [ ] **Query Params:** Filter by status
- [ ] **Expected Result:** 
  - Returns all sprints for project
  - Ordered by sprint_number descending
  - Includes metrics (total_story_points, completed_story_points)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SPRINT-004: Retrieve Sprint (API)**
- [ ] **Test Case:** Get single sprint
- [ ] **Endpoint:** `GET /api/projects/{project_id}/sprints/{sprint_id}/`
- [ ] **Expected Result:** 
  - Returns complete sprint data
  - Includes related stories count
  - Includes burndown data if available
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SPRINT-005: Update Sprint Status**
- [ ] **Test Case:** Update sprint status
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/sprints/{sprint_id}/`
- [ ] **Request Body:** `{"status": "active"}`
- [ ] **Expected Result:** 
  - Status updated
  - If activating, other active sprints should be closed (if project config requires)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SPRINT-006: Sprint Auto-Close**
- [ ] **Test Case:** Sprint auto-closes when end_date passes
- [ ] **Endpoint:** Celery task `auto_close_sprints`
- [ ] **Steps:**
  1. Create sprint with end_date in past
  2. Run Celery task
  3. Check sprint status
- [ ] **Expected Result:** 
  - Sprint status changed to 'completed'
  - Only if project has `auto_close_sprints` enabled
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SPRINT-007: Sprint Form (UI)**
- [ ] **Test Case:** Create/edit sprint via UI
- [ ] **Page:** Sprint form modal or page
- [ ] **Steps:**
  1. Fill sprint form
  2. Set dates
  3. Submit
- [ ] **Expected Result:** 
  - Form validates correctly
  - Dates validated
  - Sprint number auto-filled if not provided
  - Success message displayed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SPRINT-008: Sprints Page (UI)**
- [ ] **Test Case:** Display sprints list
- [ ] **Page:** `/projects/{project_id}/sprints`
- [ ] **Expected Result:** 
  - Sprints displayed
  - Shows status, dates, story points
  - Clicking sprint opens detail view
  - "Create Sprint" button visible
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SPRINT-009: Sprint Planning Page (UI)**
- [ ] **Test Case:** Sprint planning interface
- [ ] **Page:** `/projects/{project_id}/sprints/{sprint_id}/planning`
- [ ] **Steps:**
  1. View backlog stories
  2. Drag stories to sprint
  3. Verify story points total
  4. Check overcommitment warning
- [ ] **Expected Result:** 
  - Drag and drop works
  - Story points calculated
  - Overcommitment warning shown if exceeds limit
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SPRINT-010: Sprint Burndown Chart**
- [ ] **Test Case:** View sprint burndown
- [ ] **Endpoint:** `GET /api/projects/{project_id}/sprints/{sprint_id}/burndown/`
- [ ] **Expected Result:** 
  - Returns burndown data (dates, remaining points)
  - Can be used to render chart
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 8. CROSS-ENTITY TESTS

**TC-CROSS-001: Story-Task Relationship**
- [ ] **Test Case:** Create task linked to story
- [ ] **Steps:**
  1. Create story
  2. Create task with story reference
  3. Verify task appears in story's task list
- [ ] **Expected Result:** 
  - Relationship maintained correctly
  - Task count updated on story
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CROSS-002: Epic-Story Relationship**
- [ ] **Test Case:** Link story to epic
- [ ] **Steps:**
  1. Create epic
  2. Create story with epic reference
  3. Verify story appears in epic's story list
- [ ] **Expected Result:** 
  - Relationship maintained correctly
  - Story count updated on epic
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CROSS-003: Sprint-Story Relationship**
- [ ] **Test Case:** Assign story to sprint
- [ ] **Steps:**
  1. Create sprint
  2. Assign story to sprint
  3. Verify story points added to sprint total
- [ ] **Expected Result:** 
  - Story linked to sprint
  - Sprint metrics updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CROSS-004: Cascade Deletes**
- [ ] **Test Case:** Verify cascade behavior on delete
- [ ] **Steps:**
  1. Create project with stories, tasks, sprints
  2. Delete project
  3. Verify all related entities deleted
- [ ] **Expected Result:** 
  - All related entities deleted (CASCADE)
  - Or set to NULL if SET_NULL
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - Core Entities (Projects, Epics, Stories, Tasks, Bugs, Issues, Sprints)  
**Total Test Cases:** ~200  
**Next File:** [02_test_checklist_collaboration.md](./02_test_checklist_collaboration.md)

