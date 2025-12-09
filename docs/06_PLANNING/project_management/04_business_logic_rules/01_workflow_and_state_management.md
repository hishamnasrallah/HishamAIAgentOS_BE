# Business Logic Rules - Workflow and State Management

**Document Type:** Business Requirements Document (BRD)  
**Version:** 1.0.0  
**Created By:** BA Agent  
**Created Date:** December 9, 2024  
**Last Updated:** December 9, 2024  
**Last Updated By:** BA Agent  
**Status:** Active  
**Dependencies:** `01_overview_and_scope.md`, `02_features_master_list/`  
**Related Features:** User Story Management, Task Management, Bug Management, Issue Management

---

## 📋 Table of Contents

1. [Workflow State Rules](#workflow-state-rules)
2. [State Transition Rules](#state-transition-rules)
3. [Status Validation Rules](#status-validation-rules)
4. [State Change Approval Rules](#state-change-approval-rules)
5. [Workflow Automation Rules](#workflow-automation-rules)

---

## 1. Workflow State Rules

### 1.1 Custom States Configuration
- **Rule:** Each project can define custom workflow states
- **Rule:** States are stored in `ProjectConfiguration.custom_states` (JSONField)
- **Rule:** Each state must have:
  - `id`: Unique identifier (string)
  - `name`: Display name (string)
  - `order`: Display order (integer)
  - `color`: Color code (string, e.g., "#blue")
  - `is_default`: Default state flag (boolean)
  - `is_final`: Final state flag (boolean)
  - `wip_limit`: Work-in-progress limit (integer, nullable)
  - `auto_transitions`: Auto-transition rules (array)

### 1.2 Default States
- **Rule:** If no custom states defined, use default states:
  - `backlog` (order: 0, is_default: true)
  - `todo` (order: 1)
  - `in_progress` (order: 2)
  - `review` (order: 3)
  - `done` (order: 4, is_final: true)

### 1.3 State Validation
- **Rule:** Work item status must be from project's custom states
- **Rule:** Status validation occurs in model `clean()` method
- **Rule:** Status validation occurs in serializer `validate()` method
- **Rule:** Invalid status raises ValidationError with valid statuses list

### 1.4 Default State Assignment
- **Rule:** New work items default to project's default state
- **Rule:** Default state is identified by `is_default: true` in custom_states
- **Rule:** If no default state, use first state in order

---

## 2. State Transition Rules

### 2.1 Transition Configuration
- **Rule:** State transitions are stored in `ProjectConfiguration.state_transitions` (JSONField)
- **Rule:** Format: `{from_state: [allowed_to_states]}`
- **Rule:** Empty array `[]` means no transitions allowed
- **Rule:** Missing key means all transitions allowed (backward compatibility)

### 2.2 Default Transitions
- **Rule:** If no transitions defined, use default transitions:
  ```json
  {
    "backlog": ["todo", "in_progress"],
    "todo": ["in_progress", "backlog"],
    "in_progress": ["review", "testing", "todo"],
    "review": ["done", "in_progress"],
    "testing": ["done", "review"],
    "done": []
  }
  ```

### 2.3 Transition Validation
- **Rule:** Status change must follow allowed transitions
- **Rule:** Transition validation occurs in serializer `validate_state_transition()`
- **Rule:** Invalid transition raises ValidationError with allowed transitions list
- **Rule:** Final states cannot transition to other states (enforced by empty array)

### 2.4 Special Transition Rules
- **Rule:** Final states (is_final: true) cannot transition to other states
- **Rule:** Final states can only be reached, not left
- **Rule:** Transitions can be restricted per state
- **Rule:** Transitions can be one-way or bidirectional

### 2.5 Transition Execution
- **Rule:** Transition validation must pass before status update
- **Rule:** Transition may require approval (if configured)
- **Rule:** Transition triggers automation rules
- **Rule:** Transition creates activity log entry
- **Rule:** Transition sends notifications

---

## 3. Status Validation Rules

### 3.1 Status Change Validation
- **Rule:** Status must be from project's custom states
- **Rule:** Transition must be allowed by state_transitions
- **Rule:** Final states cannot transition to other states
- **Rule:** Status change may require approval (if `require_approval_for_status_change` enabled)

### 3.2 Pre-Status-Change Validation
- **Rule:** Moving to 'in_progress' may require:
  - Story points (if `require_story_points_before_in_progress` enabled)
  - Assignee (if `require_assignee_before_in_progress` enabled)
  - Acceptance criteria (if `require_acceptance_criteria` enabled)

### 3.3 Post-Status-Change Validation
- **Rule:** Moving to 'done' may require:
  - All tasks completed (if `block_status_change_if_tasks_incomplete` enabled)
  - All dependencies resolved (if configured)

### 3.4 Status Change Warnings
- **Rule:** Sprint capacity warnings (if `warn_if_story_points_exceed_sprint_capacity` enabled)
- **Rule:** Warnings do not block status change, only inform user

---

## 4. State Change Approval Rules

### 4.1 Approval Configuration
- **Rule:** Approval workflow enabled via `permission_settings.require_approval_for_status_change`
- **Rule:** Approval can be required for specific status changes
- **Rule:** Approval can be required for specific states (e.g., moving to 'done')

### 4.2 Approval Request Creation
- **Rule:** When status change requires approval, create `StatusChangeApproval` record
- **Rule:** Approval request includes:
  - Work item reference (generic foreign key)
  - Old status
  - New status
  - Reason (optional)
  - Requested by (user)
  - Approver (user, optional - can be auto-assigned)

### 4.3 Approval Workflow
- **Rule:** Approval status: 'pending', 'approved', 'rejected', 'cancelled'
- **Rule:** Only approver can approve/reject
- **Rule:** Requester can cancel pending approval
- **Rule:** Approved status change is applied automatically
- **Rule:** Rejected status change is not applied

### 4.4 Approval Execution
- **Rule:** When approved, status change is applied
- **Rule:** Approval creates activity log entry
- **Rule:** Approval sends notifications
- **Rule:** Approval triggers automation rules

---

## 5. Workflow Automation Rules

### 5.1 Automation Configuration
- **Rule:** Automation rules stored in `ProjectConfiguration.automation_rules` (JSONField)
- **Rule:** Each rule has:
  - `enabled`: Enable/disable flag (boolean)
  - `trigger`: Trigger configuration (object)
  - `conditions`: Condition evaluation (array, optional)
  - `actions`: Actions to execute (array)

### 5.2 Trigger Types
- **Rule:** `on_create` - Trigger on work item creation
- **Rule:** `on_status_change` - Trigger on status change
  - `from`: Source status (optional)
  - `to`: Target status (optional)
  - `statuses`: List of statuses (optional)
- **Rule:** `on_field_update` - Trigger on field update
  - `field`: Field name
  - `conditions`: Field value conditions
- **Rule:** `on_task_complete` - Trigger on task completion

### 5.3 Condition Evaluation
- **Rule:** Conditions are evaluated before action execution
- **Rule:** Condition types:
  - `equals`: Field equals value
  - `not_equals`: Field not equals value
  - `contains`: Field contains value (for strings/arrays)
  - `greater_than`: Field greater than value (for numbers)
  - `less_than`: Field less than value (for numbers)
  - `in`: Field in list of values
  - `not_in`: Field not in list of values

### 5.4 Action Types
- **Rule:** `assign` - Assign work item to user
  - `assign_to`: User ID, email, or role
- **Rule:** `update_field` - Update field value
  - `field`: Field name
  - `value`: New value
- **Rule:** `update_status` - Update status
  - `status`: New status
- **Rule:** `add_label` - Add label
  - `label`: Label name
  - `color`: Label color (optional)
- **Rule:** `add_tag` - Add tag
  - `tag`: Tag name
- **Rule:** `notify` - Send notification
  - `notification_type`: Notification type
  - `recipients`: List of recipients
  - `message`: Notification message

### 5.5 Automation Execution
- **Rule:** Automation rules executed in order
- **Rule:** Only enabled rules are executed
- **Rule:** Conditions must match for actions to execute
- **Rule:** Actions executed sequentially
- **Rule:** Action failures logged but don't stop other actions
- **Rule:** Automation execution creates activity log entries

### 5.6 Automation Triggers
- **Rule:** Automation triggered by signals:
  - `post_save` signal for work items
  - Status change detection
  - Field change detection
  - Task completion detection

---

**End of Document**

**Next Document:** `02_validation_and_constraints.md` - Validation rules and constraints

