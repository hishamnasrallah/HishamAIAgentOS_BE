# Feature 01: User Story Management

**Document Type:** Business Requirements Document (BRD)  
**Version:** 1.0.0  
**Created By:** BA Agent  
**Created Date:** December 9, 2024  
**Last Updated:** December 9, 2024  
**Last Updated By:** BA Agent  
**Status:** Active  
**Dependencies:** `01_overview_and_scope.md`, `02_features_master_list/01_complete_features.md`  
**Related Features:** Task Management, Sprint Management, Epic Management, Board Views

---

## 📋 Table of Contents

1. [Feature Overview](#feature-overview)
2. [Business Logic](#business-logic)
3. [Scenarios & Edge Cases](#scenarios--edge-cases)
4. [Backend Effects](#backend-effects)
5. [Frontend Effects](#frontend-effects)
6. [Data Model Updates](#data-model-updates)
7. [API Requirements](#api-requirements)
8. [Permissions](#permissions)
9. [State Logic](#state-logic)
10. [CRUD Operations](#crud-operations)
11. [UX Interactions](#ux-interactions)
12. [Validation Rules](#validation-rules)
13. [Dynamic Logic](#dynamic-logic)
14. [Cross-Table Reflections](#cross-table-reflections)

---

## 1. Feature Overview

### 1.1 Purpose
User Story Management is the core feature for creating, updating, and managing user stories (feature stories) within projects. Stories represent user-facing features with acceptance criteria, story points, and workflow states.

### 1.2 Scope
- Create, read, update, delete user stories
- Story assignment to epics, sprints, assignees
- Story status tracking with custom workflow states
- Story points estimation
- Acceptance criteria management
- Story filtering, searching, and sorting
- Story relationships (dependencies, links)
- Story collaboration (comments, mentions, attachments)

### 1.3 Status
✅ **100% Complete** (Backend ✅, Frontend ✅, API ✅)

---

## 2. Business Logic

### 2.1 Story Creation
- **Rule:** Stories must belong to a project
- **Rule:** Stories can optionally belong to an epic
- **Rule:** Stories can optionally be assigned to a sprint
- **Rule:** Stories can optionally be assigned to a user
- **Rule:** Story status defaults to project's default state (usually 'backlog')
- **Rule:** Story points are optional but validated against project configuration
- **Rule:** Acceptance criteria are required if validation rule is enabled

### 2.2 Story Updates
- **Rule:** Status changes must follow state transition rules
- **Rule:** Status changes may require approval if configured
- **Rule:** Story points must be within min/max limits
- **Rule:** Story points must be from allowed scale if configured
- **Rule:** Moving to 'in_progress' may require assignee and story points (if configured)

### 2.3 Story Deletion
- **Rule:** Deleting a story deletes all associated tasks (CASCADE)
- **Rule:** Deleting a story removes it from dependencies
- **Rule:** Deleting a story removes all comments, attachments, mentions
- **Rule:** Only users with delete permission can delete stories

### 2.4 Story Assignment
- **Rule:** Stories can be assigned to project members
- **Rule:** Assignment triggers notifications
- **Rule:** Assignment can trigger automation rules

### 2.5 Story Status Changes
- **Rule:** Status must be from project's custom states
- **Rule:** Status transitions must be allowed by state transition rules
- **Rule:** Moving to 'done' may require all tasks to be complete (if configured)
- **Rule:** Status changes trigger automation rules
- **Rule:** Status changes may require approval

---

## 3. Scenarios & Edge Cases

### 3.1 Story Creation Scenarios

#### Scenario 1: Create Story with All Fields
- **Input:** Title, description, acceptance criteria, epic, sprint, assignee, story points, tags, labels, component, due date
- **Expected:** Story created with all fields populated
- **Validation:** All fields validated, story points validated against scale

#### Scenario 2: Create Story with Minimal Fields
- **Input:** Title, description, acceptance criteria only
- **Expected:** Story created with defaults (status='backlog', no assignee, no sprint)
- **Validation:** Required fields validated

#### Scenario 3: Create Story with Invalid Story Points
- **Input:** Story points = 25, but max = 21
- **Expected:** Validation error, story not created
- **Error:** "Story points (25) exceed maximum allowed (21)"

#### Scenario 4: Create Story with Invalid Status
- **Input:** Status = 'invalid_status'
- **Expected:** Validation error, story not created
- **Error:** "Invalid status 'invalid_status'. Valid statuses: backlog, todo, in_progress, review, done"

### 3.2 Story Update Scenarios

#### Scenario 1: Update Story Status (Valid Transition)
- **Input:** Status change from 'todo' to 'in_progress'
- **Expected:** Status updated, automation rules executed, notifications sent
- **Validation:** Transition allowed by state_transitions

#### Scenario 2: Update Story Status (Invalid Transition)
- **Input:** Status change from 'done' to 'todo'
- **Expected:** Validation error, status not updated
- **Error:** "Cannot transition from 'done' to 'todo'. Allowed transitions: []"

#### Scenario 3: Update Story with Approval Required
- **Input:** Status change to 'done' with approval workflow enabled
- **Expected:** StatusChangeApproval created, status not updated until approved
- **Flow:** Approval request → Pending approval → Approval → Status update

#### Scenario 4: Update Story Points (Exceeds Sprint Capacity)
- **Input:** Story points = 15, sprint already has 30 points, max = 40
- **Expected:** Warning (if configured), story points updated
- **Warning:** "Sprint capacity exceeded: 45 story points (max: 40)"

### 3.3 Story Deletion Scenarios

#### Scenario 1: Delete Story with Tasks
- **Input:** Delete story with 5 tasks
- **Expected:** Story deleted, all 5 tasks deleted (CASCADE)
- **Impact:** Tasks removed, time logs for tasks remain (orphaned)

#### Scenario 2: Delete Story with Dependencies
- **Input:** Delete story that blocks another story
- **Expected:** Story deleted, dependency relationship removed
- **Impact:** Blocked story's dependency removed

### 3.4 Edge Cases

#### Edge Case 1: Story Assigned to Non-Member
- **Scenario:** Assign story to user who is not a project member
- **Expected:** Validation error or auto-add user as member (based on configuration)
- **Current:** Validation error

#### Edge Case 2: Story Points Changed After Sprint Assignment
- **Scenario:** Story in sprint, story points increased beyond sprint capacity
- **Expected:** Warning if overcommitment not allowed, validation error
- **Current:** Warning only, validation if overcommitment disabled

#### Edge Case 3: Story Moved to Different Sprint
- **Scenario:** Story moved from Sprint 1 to Sprint 2
- **Expected:** Story points removed from Sprint 1, added to Sprint 2
- **Impact:** Sprint capacity calculations updated

---

## 4. Backend Effects

### 4.1 Model Changes
- **UserStory Model:** Core model with all fields
- **Indexes:** `['project', 'status']`, `['sprint', 'status']`
- **Relationships:**
  - ForeignKey to Project (CASCADE)
  - ForeignKey to Epic (SET_NULL)
  - ForeignKey to Sprint (SET_NULL)
  - ForeignKey to User (assigned_to, SET_NULL)
  - ForeignKey to User (created_by, SET_NULL)
  - ForeignKey to User (updated_by, SET_NULL)

### 4.2 Serializer Logic
- **StorySerializer:** Full CRUD with validation
- **Validation:**
  - Status against project configuration
  - Story points against scale and limits
  - State transitions
  - Required fields
  - Acceptance criteria (if configured)

### 4.3 ViewSet Logic
- **UserStoryViewSet:** Full CRUD operations
- **Filtering:** By project, status, sprint, epic, assignee, tags
- **Search:** By title, description
- **Permissions:** Project member checks
- **Custom Actions:**
  - `estimate` - AI story point estimation
  - `generate_stories` - AI story generation

### 4.4 Signal Handlers
- **post_save:** Extract mentions, execute automation, send notifications
- **pre_save:** Validate status, validate story points
- **post_delete:** Clean up dependencies, comments, attachments

### 4.5 Service Integration
- **ValidationService:** Validate story creation/update
- **AutomationService:** Execute automation rules
- **NotificationService:** Send notifications
- **PermissionService:** Check permissions

---

## 5. Frontend Effects

### 5.1 Components
- **StoryFormModal:** Create/edit story form
- **StoryEditModal:** Edit story modal
- **KanbanCard:** Display story in Kanban board
- **ListView:** Display story in list view
- **TableView:** Display story in table view
- **TaskQuickView:** Story details in quick view

### 5.2 Hooks
- **useStories:** Fetch, create, update, delete stories
- **useProjectPermissions:** Check permissions for UI hiding
- **useTagAutocomplete:** Tag autocomplete

### 5.3 Pages
- **BacklogPage:** Story backlog view
- **BoardPage:** Kanban/List/Table board view
- **ProjectDetailPage:** Project overview with stories

### 5.4 State Management
- **React Query:** Story data caching and invalidation
- **State Updates:** Optimistic updates for better UX
- **Error Handling:** Error display and retry logic

---

## 6. Data Model Updates

### 6.1 UserStory Model Fields
```python
- id: UUID (primary key)
- project: ForeignKey to Project (CASCADE)
- epic: ForeignKey to Epic (SET_NULL, optional)
- sprint: ForeignKey to Sprint (SET_NULL, optional)
- title: CharField (max_length=300)
- description: TextField
- acceptance_criteria: TextField
- status: CharField (validated against custom_states)
- priority: CharField
- story_points: IntegerField (nullable)
- story_type: CharField (choices)
- component: CharField (optional)
- due_date: DateField (nullable)
- labels: JSONField (list of {name, color})
- tags: JSONField (list of strings)
- custom_fields: JSONField (dict)
- assigned_to: ForeignKey to User (SET_NULL, optional)
- generated_by_ai: BooleanField
- generation_workflow: ForeignKey to WorkflowExecution (SET_NULL, optional)
- created_by: ForeignKey to User (SET_NULL)
- updated_by: ForeignKey to User (SET_NULL)
- created_at: DateTimeField (auto_now_add)
- updated_at: DateTimeField (auto_now)
```

### 6.2 Indexes
- `['project', 'status']` - For filtering stories by project and status
- `['sprint', 'status']` - For filtering stories by sprint and status

### 6.3 Relationships
- **One-to-Many:** Project → Stories
- **Many-to-One:** Story → Epic, Story → Sprint, Story → Assignee
- **One-to-Many:** Story → Tasks
- **One-to-Many:** Story → Comments
- **One-to-Many:** Story → Attachments
- **One-to-Many:** Story → Dependencies (outgoing)
- **One-to-Many:** Story → Dependencies (incoming)
- **One-to-Many:** Story → Mentions
- **One-to-Many:** Story → Time Logs

---

## 7. API Requirements

### 7.1 Endpoints
- `GET /api/projects/{project_id}/stories/` - List stories
- `POST /api/projects/{project_id}/stories/` - Create story
- `GET /api/projects/{project_id}/stories/{id}/` - Get story
- `PUT /api/projects/{project_id}/stories/{id}/` - Update story
- `PATCH /api/projects/{project_id}/stories/{id}/` - Partial update story
- `DELETE /api/projects/{project_id}/stories/{id}/` - Delete story
- `POST /api/projects/{project_id}/stories/{id}/estimate/` - Estimate story points
- `POST /api/projects/{project_id}/stories/generate/` - Generate stories (AI)

### 7.2 Request/Response Formats
- **Create Request:** JSON with story fields
- **Update Request:** JSON with fields to update
- **Response:** JSON with story data including related objects
- **Error Response:** JSON with error details

### 7.3 Validation
- **Input Validation:** Serializer validation
- **Business Validation:** Service validation
- **Permission Validation:** Permission checks

### 7.4 Error Handling
- **400 Bad Request:** Validation errors
- **403 Forbidden:** Permission denied
- **404 Not Found:** Story not found
- **500 Internal Server Error:** Server errors

---

## 8. Permissions

### 8.1 Permission Checks
- **Create:** `can_create_story()` - Check project member and permission settings
- **Read:** `can_view_story()` - Check project member
- **Update:** `can_edit_story()` - Check project member and permission settings
- **Delete:** `can_delete_story()` - Check project member and permission settings
- **Assign:** `can_assign_story()` - Check project member and permission settings
- **Change Status:** `can_change_status()` - Check project member, permission settings, approval requirements

### 8.2 Role-Based Access
- **Admin:** Full access
- **Owner:** Full access
- **Member:** Create, edit, assign (based on settings)
- **Viewer:** Read-only access

---

## 9. State Logic

### 9.1 Status Validation
- Status must be from project's `custom_states`
- Status validated in model `clean()` method
- Status validated in serializer

### 9.2 State Transitions
- Transitions validated against `state_transitions` configuration
- Final states cannot transition to other states
- Transitions can be restricted per state

### 9.3 Status Change Flow
1. Validate new status is valid
2. Validate transition is allowed
3. Check if approval required
4. If approval required: Create approval request
5. If no approval: Update status
6. Execute automation rules
7. Send notifications
8. Create activity log

---

## 10. CRUD Operations

### 10.1 Create
- **Input:** Story data (title, description, acceptance_criteria, etc.)
- **Process:** Validate → Create → Save → Signals → Notifications
- **Output:** Created story data

### 10.2 Read
- **Input:** Story ID
- **Process:** Fetch story with related objects
- **Output:** Story data with relationships

### 10.3 Update
- **Input:** Story ID + updated fields
- **Process:** Validate → Check permissions → Update → Save → Signals → Notifications
- **Output:** Updated story data

### 10.4 Delete
- **Input:** Story ID
- **Process:** Check permissions → Delete (CASCADE to tasks) → Clean up relationships
- **Output:** Success/error response

---

## 11. UX Interactions

### 11.1 Story Creation
- **Form Modal:** StoryFormModal with all fields
- **Validation:** Real-time validation feedback
- **Autocomplete:** Tag autocomplete, user autocomplete
- **Success:** Story created, modal closed, board refreshed

### 11.2 Story Editing
- **Edit Modal:** StoryEditModal with pre-filled data
- **Status Dropdown:** Filtered by allowed transitions
- **Validation:** Real-time validation feedback
- **Success:** Story updated, modal closed, board refreshed

### 11.3 Story Display
- **Kanban Card:** Title, assignee, story points, tags, due date
- **List View:** Card display with details
- **Table View:** Row display with sortable columns
- **Quick View:** Full story details in side panel

### 11.4 Drag-and-Drop
- **Kanban:** Drag card to change status
- **Validation:** Check WIP limits, check transitions
- **Feedback:** Visual feedback during drag
- **Success:** Status updated, board refreshed

---

## 12. Validation Rules

### 12.1 Required Fields
- Title (always required)
- Description (always required)
- Acceptance Criteria (if `require_acceptance_criteria` enabled)

### 12.2 Story Points Validation
- Must be within min/max limits
- Must be from allowed scale (if configured)
- Must be positive integer

### 12.3 Status Validation
- Must be from project's custom states
- Transition must be allowed
- Final states cannot transition

### 12.4 Assignment Validation
- Assignee must be project member (or auto-added)
- Assignment permission required

---

## 13. Dynamic Logic

### 13.1 Configuration-Based Behavior
- **Status Values:** From `custom_states` configuration
- **State Transitions:** From `state_transitions` configuration
- **Story Point Scale:** From `story_point_scale` configuration
- **Validation Rules:** From `validation_rules` configuration
- **Permission Settings:** From `permission_settings` configuration

### 13.2 Automation Triggers
- **On Create:** Execute automation rules for story creation
- **On Status Change:** Execute automation rules for status changes
- **On Update:** Execute automation rules for field updates
- **On Task Complete:** Execute automation rules for task completion

### 13.3 Conditional Logic
- **Approval Required:** If `require_approval_for_status_change` enabled
- **Task Completion:** If `block_status_change_if_tasks_incomplete` enabled
- **Story Points Required:** If `require_story_points_before_in_progress` enabled

---

## 14. Cross-Table Reflections

### 14.1 Story → Task
- **Impact:** Story deletion deletes all tasks (CASCADE)
- **Impact:** Task completion affects story status validation
- **Impact:** Story status change can trigger task automation

### 14.2 Story → Epic
- **Impact:** Story status affects epic progress calculation
- **Impact:** Epic deletion sets story.epic to NULL (SET_NULL)

### 14.3 Story → Sprint
- **Impact:** Story assignment affects sprint capacity
- **Impact:** Sprint deletion sets story.sprint to NULL (SET_NULL)
- **Impact:** Story points affect sprint total_story_points

### 14.4 Story → Dependencies
- **Impact:** Story deletion removes dependency relationships
- **Impact:** Dependency creation affects board visualization

### 14.5 Story → Comments
- **Impact:** Story deletion deletes all comments (CASCADE)
- **Impact:** Comment creation triggers notifications

### 14.6 Story → Attachments
- **Impact:** Story deletion deletes all attachments (CASCADE)
- **Impact:** Attachment creation triggers notifications

### 14.7 Story → Time Logs
- **Impact:** Story deletion deletes all time logs (CASCADE)
- **Impact:** Time logs affect time reporting

---

**End of Document**

**Related Documents:**
- `feature_02_task_management.md`
- `feature_03_sprint_management.md`
- `feature_04_epic_management.md`
- `feature_05_board_views.md`

