# Feature 02: Task Management

**Document Type:** Business Requirements Document (BRD)  
**Version:** 1.0.0  
**Created By:** BA Agent  
**Created Date:** December 9, 2024  
**Last Updated:** December 9, 2024  
**Last Updated By:** BA Agent  
**Status:** Active  
**Dependencies:** `01_overview_and_scope.md`, `feature_01_user_story_management.md`  
**Related Features:** User Story Management, Sprint Management, Time Logging

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
Task Management allows creating, updating, and managing tasks within projects. Tasks can belong to user stories or be standalone, and support hierarchical relationships (parent-child tasks).

### 1.2 Scope
- Create, read, update, delete tasks
- Task assignment to stories (optional) or standalone
- Task hierarchy (parent-child relationships)
- Task status tracking with custom workflow states
- Task progress tracking (percentage)
- Task filtering, searching, and sorting
- Task relationships (parent-child)
- Task time tracking

### 1.3 Status
✅ **100% Complete** (Backend ✅, Frontend ✅, API ✅)

---

## 2. Business Logic

### 2.1 Task Creation
- **Rule:** Tasks can belong to a story (optional) or be standalone
- **Rule:** Tasks can have a parent task (for sub-tasks)
- **Rule:** Tasks must belong to a project (via story or directly)
- **Rule:** Task status defaults to project's default state (usually 'todo')
- **Rule:** Task priority defaults to 'medium'
- **Rule:** Progress percentage defaults to 0

### 2.2 Task Updates
- **Rule:** Status changes must follow state transition rules
- **Rule:** Status changes may require approval if configured
- **Rule:** Progress percentage must be 0-100
- **Rule:** Parent task cannot be the task itself (circular reference prevention)
- **Rule:** Parent task cannot create circular chain

### 2.3 Task Deletion
- **Rule:** Deleting a task deletes all sub-tasks (CASCADE)
- **Rule:** Deleting a task removes it from story task list
- **Rule:** Deleting a task removes all time logs (CASCADE)
- **Rule:** Only users with delete permission can delete tasks

### 2.4 Task Assignment
- **Rule:** Tasks can be assigned to project members
- **Rule:** Assignment triggers notifications
- **Rule:** Assignment can trigger automation rules

### 2.5 Task Status Changes
- **Rule:** Status must be from project's custom states
- **Rule:** Status transitions must be allowed by state transition rules
- **Rule:** Moving to 'done' may trigger story status update (if configured)
- **Rule:** Status changes trigger automation rules
- **Rule:** Status changes may require approval

### 2.6 Task Hierarchy
- **Rule:** Tasks can have parent tasks (for sub-tasks)
- **Rule:** Circular references prevented (task cannot be its own parent or ancestor)
- **Rule:** Deleting parent task deletes all sub-tasks (CASCADE)
- **Rule:** Sub-tasks inherit project from parent task

---

## 3. Scenarios & Edge Cases

### 3.1 Task Creation Scenarios

#### Scenario 1: Create Task Linked to Story
- **Input:** Title, description, story, assignee, status, priority
- **Expected:** Task created and linked to story
- **Validation:** Story must exist and belong to same project

#### Scenario 2: Create Standalone Task
- **Input:** Title, description, project (via story=null), assignee
- **Expected:** Task created without story link
- **Validation:** Project must be accessible

#### Scenario 3: Create Sub-Task
- **Input:** Title, description, parent_task, assignee
- **Expected:** Task created as sub-task
- **Validation:** Parent task must exist, no circular reference

#### Scenario 4: Create Task with Invalid Parent
- **Input:** parent_task = self
- **Expected:** Validation error, task not created
- **Error:** "A task cannot be its own parent."

#### Scenario 5: Create Task with Circular Parent Chain
- **Input:** parent_task that would create circular chain
- **Expected:** Validation error, task not created
- **Error:** "Circular parent reference detected."

### 3.2 Task Update Scenarios

#### Scenario 1: Update Task Status (Valid Transition)
- **Input:** Status change from 'todo' to 'in_progress'
- **Expected:** Status updated, automation rules executed, notifications sent
- **Validation:** Transition allowed by state_transitions

#### Scenario 2: Update Task Progress
- **Input:** progress_percentage = 75
- **Expected:** Progress updated, story progress may update (if configured)
- **Validation:** Progress must be 0-100

#### Scenario 3: Update Task Parent (Valid)
- **Input:** Change parent_task to different task
- **Expected:** Parent updated, circular reference checked
- **Validation:** No circular reference

#### Scenario 4: Update Task Parent (Circular)
- **Input:** Set parent_task to a sub-task of this task
- **Expected:** Validation error, parent not updated
- **Error:** "Circular parent reference detected."

### 3.3 Task Deletion Scenarios

#### Scenario 1: Delete Task with Sub-Tasks
- **Input:** Delete task with 3 sub-tasks
- **Expected:** Task deleted, all 3 sub-tasks deleted (CASCADE)
- **Impact:** Sub-tasks removed, time logs for sub-tasks remain (orphaned)

#### Scenario 2: Delete Task Linked to Story
- **Input:** Delete task that belongs to story
- **Expected:** Task deleted, story task count updated
- **Impact:** Story may update status if all tasks complete (if configured)

---

## 4. Backend Effects

### 4.1 Model Changes
- **Task Model:** Core model with all fields
- **Indexes:** `['story', 'status']`, `['parent_task', 'status']`, `['assigned_to', 'status']`
- **Relationships:**
  - ForeignKey to UserStory (CASCADE, nullable for standalone tasks)
  - ForeignKey to Task (parent_task, CASCADE, self-referential)
  - ForeignKey to User (assigned_to, SET_NULL)
  - ForeignKey to User (created_by, SET_NULL)
  - ForeignKey to User (updated_by, SET_NULL)

### 4.2 Serializer Logic
- **TaskSerializer:** Full CRUD with validation
- **Validation:**
  - Status against project configuration
  - Circular reference prevention
  - Progress percentage range (0-100)
  - Parent task validation

### 4.3 ViewSet Logic
- **TaskViewSet:** Full CRUD operations
- **Filtering:** By project, story, status, assignee, parent_task, tags
- **Search:** By title, description
- **Permissions:** Project member checks
- **Custom Actions:** None currently

### 4.4 Signal Handlers
- **post_save:** Execute automation, send notifications
- **pre_save:** Validate status, validate circular references
- **post_delete:** Clean up relationships

### 4.5 Service Integration
- **ValidationService:** Validate task creation/update
- **AutomationService:** Execute automation rules
- **NotificationService:** Send notifications
- **PermissionService:** Check permissions

---

## 5. Frontend Effects

### 5.1 Components
- **TaskFormModal:** Create/edit task form
- **TasksPage:** Project-level task management page
- **KanbanCard:** Display task in Kanban board (if applicable)
- **TaskQuickView:** Task details in quick view

### 5.2 Hooks
- **useTasks:** Fetch, create, update, delete tasks
- **useProjectPermissions:** Check permissions for UI hiding

### 5.3 Pages
- **TasksPage:** Task list view with filtering
- **BoardPage:** Tasks displayed in board (if configured)

### 5.4 State Management
- **React Query:** Task data caching and invalidation
- **State Updates:** Optimistic updates for better UX

---

## 6. Data Model Updates

### 6.1 Task Model Fields
```python
- id: UUID (primary key)
- story: ForeignKey to UserStory (CASCADE, nullable for standalone tasks)
- parent_task: ForeignKey to Task (CASCADE, nullable, self-referential)
- title: CharField (max_length=300)
- description: TextField (blank=True)
- status: CharField (validated against custom_states)
- priority: CharField
- assigned_to: ForeignKey to User (SET_NULL, optional)
- estimated_hours: DecimalField (nullable)
- actual_hours: DecimalField (nullable)
- progress_percentage: IntegerField (0-100)
- tags: JSONField (list of strings)
- labels: JSONField (list of {name, color})
- custom_fields: JSONField (dict)
- component: CharField (optional)
- due_date: DateField (nullable)
- created_by: ForeignKey to User (SET_NULL)
- updated_by: ForeignKey to User (SET_NULL)
- created_at: DateTimeField (auto_now_add)
- updated_at: DateTimeField (auto_now)
```

### 6.2 Indexes
- `['story', 'status']` - For filtering tasks by story and status
- `['parent_task', 'status']` - For filtering tasks by parent and status
- `['assigned_to', 'status']` - For filtering tasks by assignee and status

### 6.3 Relationships
- **Many-to-One:** Task → Story (CASCADE, nullable)
- **Many-to-One:** Task → ParentTask (CASCADE, self-referential)
- **Many-to-One:** Task → AssignedTo (SET_NULL)
- **One-to-Many:** Task → Subtasks (CASCADE)
- **One-to-Many:** Task → Time Logs (CASCADE)

---

## 7. API Requirements

### 7.1 Endpoints
- `GET /api/projects/{project_id}/tasks/` - List tasks
- `POST /api/projects/{project_id}/tasks/` - Create task
- `GET /api/projects/{project_id}/tasks/{id}/` - Get task
- `PUT /api/projects/{project_id}/tasks/{id}/` - Update task
- `PATCH /api/projects/{project_id}/tasks/{id}/` - Partial update task
- `DELETE /api/projects/{project_id}/tasks/{id}/` - Delete task

### 7.2 Request/Response Formats
- **Create Request:** JSON with task fields
- **Update Request:** JSON with fields to update
- **Response:** JSON with task data including related objects
- **Error Response:** JSON with error details

### 7.3 Validation
- **Input Validation:** Serializer validation
- **Business Validation:** Service validation
- **Permission Validation:** Permission checks

---

## 8. Permissions

### 8.1 Permission Checks
- **Create:** `can_create_task()` - Check project member and permission settings
- **Read:** `can_view_task()` - Check project member
- **Update:** `can_edit_task()` - Check project member and permission settings
- **Delete:** `can_delete_task()` - Check project member and permission settings
- **Assign:** `can_assign_task()` - Check project member and permission settings
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
9. Update story status if all tasks complete (if configured)

---

## 10. CRUD Operations

### 10.1 Create
- **Input:** Task data (title, description, story, parent_task, etc.)
- **Process:** Validate → Create → Save → Signals → Notifications
- **Output:** Created task data

### 10.2 Read
- **Input:** Task ID
- **Process:** Fetch task with related objects
- **Output:** Task data with relationships

### 10.3 Update
- **Input:** Task ID + updated fields
- **Process:** Validate → Check permissions → Update → Save → Signals → Notifications
- **Output:** Updated task data

### 10.4 Delete
- **Input:** Task ID
- **Process:** Check permissions → Delete (CASCADE to sub-tasks) → Clean up relationships
- **Output:** Success/error response

---

## 11. UX Interactions

### 11.1 Task Creation
- **Form Modal:** TaskFormModal with all fields
- **Validation:** Real-time validation feedback
- **Autocomplete:** User autocomplete for assignee
- **Success:** Task created, modal closed, list refreshed

### 11.2 Task Editing
- **Edit Modal:** TaskFormModal with pre-filled data
- **Status Dropdown:** Filtered by allowed transitions
- **Parent Task Dropdown:** Filtered to prevent circular references
- **Validation:** Real-time validation feedback
- **Success:** Task updated, modal closed, list refreshed

### 11.3 Task Display
- **List View:** Task list with filtering and sorting
- **Card View:** Task card in Kanban board (if applicable)
- **Quick View:** Task details in side panel

### 11.4 Task Hierarchy
- **Parent-Child Display:** Hierarchical view of tasks
- **Indentation:** Visual indentation for sub-tasks
- **Expand/Collapse:** Collapsible task hierarchy

---

## 12. Validation Rules

### 12.1 Required Fields
- Title (always required)
- Description (optional but recommended)

### 12.2 Status Validation
- Must be from project's custom states
- Transition must be allowed
- Final states cannot transition

### 12.3 Hierarchy Validation
- Parent task cannot be self
- No circular parent chains
- Parent task must exist

### 12.4 Progress Validation
- Progress percentage must be 0-100
- Integer value

---

## 13. Dynamic Logic

### 13.1 Configuration-Based Behavior
- **Status Values:** From `custom_states` configuration
- **State Transitions:** From `state_transitions` configuration
- **Validation Rules:** From `validation_rules` configuration
- **Permission Settings:** From `permission_settings` configuration

### 13.2 Automation Triggers
- **On Create:** Execute automation rules for task creation
- **On Status Change:** Execute automation rules for status changes
- **On Update:** Execute automation rules for field updates
- **On Complete:** May trigger story status update (if configured)

### 13.3 Conditional Logic
- **Approval Required:** If `require_approval_for_status_change` enabled
- **Story Status Update:** If `block_status_change_if_tasks_incomplete` enabled on story
- **Task Completion:** If all tasks complete, story may auto-update status

---

## 14. Cross-Table Reflections

### 14.1 Task → Story
- **Impact:** Task completion affects story status validation
- **Impact:** Story deletion deletes all tasks (CASCADE)
- **Impact:** Task status change can trigger story automation

### 14.2 Task → Parent Task
- **Impact:** Parent task deletion deletes all sub-tasks (CASCADE)
- **Impact:** Parent task status may affect sub-task workflow

### 14.3 Task → Time Logs
- **Impact:** Task deletion deletes all time logs (CASCADE)
- **Impact:** Time logs affect task actual_hours calculation

### 14.4 Task → Project
- **Impact:** Task belongs to project (via story or directly)
- **Impact:** Task uses project configuration for status/validation

---

**End of Document**

**Related Documents:**
- `feature_01_user_story_management.md`
- `feature_03_sprint_management.md`
- `feature_08_collaboration_features.md`

