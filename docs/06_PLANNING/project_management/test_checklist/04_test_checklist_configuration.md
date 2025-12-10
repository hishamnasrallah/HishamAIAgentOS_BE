# Test Checklist: Configuration Features

**Category:** Configuration  
**Features:** Workflow States, Story Points, Sprint Config, Board Customization, Automation Rules, Notification Settings  
**Estimated Tests:** ~100  
**Priority:** HIGH

---

## 1. WORKFLOW & STATE MANAGEMENT

### 1.1 Custom States Configuration

**TC-CFG-001: View Project Configuration (API)**
- [ ] **Test Case:** Get project configuration
- [ ] **Endpoint:** `GET /api/projects/{project_id}/configurations/`
- [ ] **Expected Result:** 
  - Returns project configuration
  - Includes custom_states, state_transitions, board_columns
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-002: Update Custom States (API)**
- [ ] **Test Case:** Update workflow states
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/configurations/`
- [ ] **Request Body:**
  ```json
  {
    "custom_states": [
      {"id": "todo", "name": "To Do", "color": "#gray"},
      {"id": "in_progress", "name": "In Progress", "color": "#blue"},
      {"id": "done", "name": "Done", "color": "#green"}
    ]
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Custom states updated
  - States validated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-003: Workflow States Editor (UI)**
- [ ] **Test Case:** Configure states via UI
- [ ] **Page:** Project settings > Workflow
- [ ] **Steps:**
  1. Navigate to workflow configuration
  2. Add/edit/delete states
  3. Set colors for states
  4. Save
- [ ] **Expected Result:** 
  - States editor loads current states
  - Can add new states
  - Can edit existing states
  - Can delete states (with validation)
  - Colors can be set
  - Changes saved successfully
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-004: State Transitions Configuration**
- [ ] **Test Case:** Configure allowed transitions
- [ ] **Page:** Project settings > Workflow
- [ ] **Steps:**
  1. Configure state transitions
  2. Define which states can transition to which
  3. Save
- [ ] **Expected Result:** 
  - Transitions configured
  - Transition matrix displayed
  - Invalid transitions prevented
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-005: Status Validation on Story Update**
- [ ] **Test Case:** Validate status changes against transitions
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/stories/{story_id}/`
- [ ] **Request Body:** `{"status": "done"}` (from "todo" if transition not allowed)
- [ ] **Expected Result:** 
  - Status code: 400 Bad Request
  - Error message about invalid transition
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. STORY POINTS CONFIGURATION

### 2.1 Story Point Settings

**TC-CFG-006: Configure Story Point Scale**
- [ ] **Test Case:** Set story point scale
- [ ] **Page:** Project settings > Story Points
- [ ] **Steps:**
  1. Navigate to story points configuration
  2. Set scale (e.g., Fibonacci: 1, 2, 3, 5, 8, 13)
  3. Save
- [ ] **Expected Result:** 
  - Scale saved
  - Scale used in story point selection
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-007: Story Point Limits**
- [ ] **Test Case:** Set min/max story points
- [ ] **Page:** Project settings > Story Points
- [ ] **Steps:**
  1. Set min_story_points_per_story (e.g., 1)
  2. Set max_story_points_per_story (e.g., 20)
  3. Save
- [ ] **Expected Result:** 
  - Limits saved
  - Limits enforced when creating/updating stories
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-008: Story Point Validation**
- [ ] **Test Case:** Validate story points against limits
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/`
- [ ] **Request Body:** `{"title": "Test", "story_points": 100}` (if max is 20)
- [ ] **Expected Result:** 
  - Status code: 400 Bad Request
  - Error message about exceeding limit
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-009: Story Points Required Setting**
- [ ] **Test Case:** Require story points on stories
- [ ] **Page:** Project settings > Story Points
- [ ] **Steps:**
  1. Enable `story_points_required`
  2. Try to create story without points
- [ ] **Expected Result:** 
  - Story creation fails if points not provided
  - Error message shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-010: Sprint Story Points Limit**
- [ ] **Test Case:** Set max story points per sprint
- [ ] **Page:** Project settings > Story Points
- [ ] **Steps:**
  1. Set max_story_points_per_sprint (e.g., 40)
  2. Try to add stories exceeding limit
- [ ] **Expected Result:** 
  - Warning shown when limit exceeded
  - Overcommitment allowed if configured
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. SPRINT CONFIGURATION

### 3.1 Sprint Settings

**TC-CFG-011: Default Sprint Duration**
- [ ] **Test Case:** Set default sprint duration
- [ ] **Page:** Project settings > Sprints
- [ ] **Steps:**
  1. Set default_sprint_duration_days (e.g., 14)
  2. Create new sprint without dates
- [ ] **Expected Result:** 
  - Sprint created with default duration
  - End date calculated from start date
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-012: Sprint Start Day**
- [ ] **Test Case:** Set sprint start day
- [ ] **Page:** Project settings > Sprints
- [ ] **Steps:**
  1. Set sprint_start_day (e.g., Monday = 0)
  2. Create sprint
- [ ] **Expected Result:** 
  - Sprint start date adjusted to start day if needed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-013: Auto-Close Sprints**
- [ ] **Test Case:** Enable auto-close sprints
- [ ] **Page:** Project settings > Sprints
- [ ] **Steps:**
  1. Enable auto_close_sprints
  2. Create sprint with past end_date
  3. Run Celery task
- [ ] **Expected Result:** 
  - Sprint automatically closed when end_date passes
  - Celery task runs and closes sprints
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-014: Allow Overcommitment**
- [ ] **Test Case:** Configure sprint overcommitment
- [ ] **Page:** Project settings > Sprints
- [ ] **Steps:**
  1. Enable/disable allow_overcommitment
  2. Try to add stories exceeding sprint capacity
- [ ] **Expected Result:** 
  - If disabled, prevents overcommitment
  - If enabled, allows with warning
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. BOARD CUSTOMIZATION

### 4.1 Board Display Configuration

**TC-CFG-015: Default Board View**
- [ ] **Test Case:** Set default board view
- [ ] **Page:** Project settings > Board
- [ ] **Steps:**
  1. Set default_board_view (kanban, list, table)
  2. Navigate to board
- [ ] **Expected Result:** 
  - Board opens in configured default view
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-016: Swimlane Grouping**
- [ ] **Test Case:** Configure swimlane grouping
- [ ] **Page:** Project settings > Board
- [ ] **Steps:**
  1. Set swimlane_grouping (epic, assignee, priority, component, story_type, null)
  2. View board
- [ ] **Expected Result:** 
  - Board displays with configured grouping
  - Stories grouped correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-017: Card Display Fields**
- [ ] **Test Case:** Configure card display fields
- [ ] **Page:** Project settings > Board
- [ ] **Steps:**
  1. Configure card_display_fields
  2. Select fields to display (title, assignee, points, labels, due_date, etc.)
  3. Save
- [ ] **Expected Result:** 
  - Cards display only selected fields
  - Field order preserved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-018: Card Color Configuration**
- [ ] **Test Case:** Configure card coloring
- [ ] **Page:** Project settings > Board
- [ ] **Steps:**
  1. Set card_color_by (state, epic, type, component, custom)
  2. View board
- [ ] **Expected Result:** 
  - Cards colored according to configuration
  - Colors consistent and meaningful
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-019: Board Columns Configuration**
- [ ] **Test Case:** Configure board columns
- [ ] **Page:** Project settings > Board
- [ ] **Steps:**
  1. Configure board_columns
  2. Set column names, WIP limits, colors
  3. Set column order
  4. Save
- [ ] **Expected Result:** 
  - Columns configured correctly
  - WIP limits applied
  - Column order preserved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. AUTOMATION RULES

### 5.1 Automation Configuration

**TC-CFG-020: View Automation Rules**
- [ ] **Test Case:** Get automation rules
- [ ] **Endpoint:** `GET /api/projects/{project_id}/configurations/`
- [ ] **Expected Result:** 
  - Returns automation_rules array
  - Includes all rule configurations
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-021: Create Automation Rule**
- [ ] **Test Case:** Add new automation rule
- [ ] **Page:** Project settings > Automation
- [ ] **Steps:**
  1. Click "Add Rule"
  2. Configure trigger (status_change, field_update, scheduled, on_create)
  3. Configure conditions
  4. Configure actions (assign, update_field, update_status, add_label, notify)
  5. Save
- [ ] **Expected Result:** 
  - Rule created
  - Rule appears in rules list
  - Rule enabled by default
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-022: Edit Automation Rule**
- [ ] **Test Case:** Modify existing rule
- [ ] **Page:** Project settings > Automation
- [ ] **Steps:**
  1. Click edit on rule
  2. Modify trigger/conditions/actions
  3. Save
- [ ] **Expected Result:** 
  - Rule updated
  - Changes saved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-023: Enable/Disable Automation Rule**
- [ ] **Test Case:** Toggle rule enabled state
- [ ] **Page:** Project settings > Automation
- [ ] **Steps:**
  1. Toggle rule enabled/disabled
  2. Save
- [ ] **Expected Result:** 
  - Rule state updated
  - Disabled rules don't execute
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-024: Delete Automation Rule**
- [ ] **Test Case:** Remove automation rule
- [ ] **Page:** Project settings > Automation
- [ ] **Steps:**
  1. Click delete on rule
  2. Confirm deletion
- [ ] **Expected Result:** 
  - Rule removed
  - Rule no longer executes
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-025: Automation Rule Execution - Status Change**
- [ ] **Test Case:** Rule triggers on status change
- [ ] **Steps:**
  1. Create rule: trigger on status change from "todo" to "in_progress", action: assign to user X
  2. Change story status from "todo" to "in_progress"
- [ ] **Expected Result:** 
  - Rule executes
  - Story assigned to user X
  - Action logged
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-026: Automation Rule Execution - Scheduled**
- [ ] **Test Case:** Rule triggers on schedule
- [ ] **Steps:**
  1. Create rule: trigger daily at 9:00 AM, action: update status
  2. Wait for scheduled time or trigger manually
- [ ] **Expected Result:** 
  - Rule executes at scheduled time
  - Celery task runs
  - Actions applied
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-027: Automation Rules Editor (UI)**
- [ ] **Test Case:** Use automation rules editor
- [ ] **Page:** Project settings > Automation
- [ ] **Expected Result:** 
  - Rules editor loads
  - Can add/edit/delete rules
  - Trigger and action builders work
  - Validation shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 6. NOTIFICATION SETTINGS

### 6.1 Notification Configuration

**TC-CFG-028: View Notification Settings**
- [ ] **Test Case:** Get notification settings
- [ ] **Endpoint:** `GET /api/projects/{project_id}/configurations/`
- [ ] **Expected Result:** 
  - Returns notification_settings
  - Includes email_enabled, in_app_enabled
  - Includes event-specific settings
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-029: Configure Email Notifications**
- [ ] **Test Case:** Enable/disable email notifications
- [ ] **Page:** Project settings > Notifications
- [ ] **Steps:**
  1. Toggle email_enabled
  2. Configure event-specific email settings
  3. Save
- [ ] **Expected Result:** 
  - Settings saved
  - Email notifications sent/not sent according to settings
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-030: Configure In-App Notifications**
- [ ] **Test Case:** Enable/disable in-app notifications
- [ ] **Page:** Project settings > Notifications
- [ ] **Steps:**
  1. Toggle in_app_enabled
  2. Configure event-specific settings
  3. Save
- [ ] **Expected Result:** 
  - Settings saved
  - In-app notifications shown/hidden according to settings
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-031: Event-Specific Notification Settings**
- [ ] **Test Case:** Configure notifications per event type
- [ ] **Page:** Project settings > Notifications
- [ ] **Steps:**
  1. Configure on_status_change notifications
  2. Configure on_assignment notifications
  3. Configure on_mention notifications
  4. Save
- [ ] **Expected Result:** 
  - Each event type can be enabled/disabled independently
  - Settings applied correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 7. PERMISSION SETTINGS

### 7.1 Permission Configuration

**TC-CFG-032: View Permission Settings**
- [ ] **Test Case:** Get permission settings
- [ ] **Endpoint:** `GET /api/projects/{project_id}/configurations/`
- [ ] **Expected Result:** 
  - Returns permission_settings
  - Includes role-based permissions
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-033: Configure Role Permissions**
- [ ] **Test Case:** Set permissions for roles
- [ ] **Page:** Project settings > Permissions
- [ ] **Steps:**
  1. Configure permissions for Owner, Admin, Member, Viewer roles
  2. Set CRUD permissions for each entity
  3. Save
- [ ] **Expected Result:** 
  - Permissions saved
  - Permissions enforced in API and UI
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 8. CUSTOM FIELDS

### 8.1 Custom Fields Schema

**TC-CFG-034: Configure Custom Fields**
- [ ] **Test Case:** Add custom fields to stories
- [ ] **Page:** Project settings > Custom Fields
- [ ] **Steps:**
  1. Add custom field (text, number, date, select, etc.)
  2. Configure field properties
  3. Save
- [ ] **Expected Result:** 
  - Custom field added
  - Field appears in story forms
  - Field displayed on cards/views
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-035: Custom Field Validation**
- [ ] **Test Case:** Validate custom field values
- [ ] **Page:** Story form
- [ ] **Steps:**
  1. Fill custom field with invalid value
  2. Submit form
- [ ] **Expected Result:** 
  - Validation error shown
  - Form does not submit
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 9. INTEGRATION SETTINGS

### 9.1 External Integrations

**TC-CFG-036: GitHub Integration Settings**
- [ ] **Test Case:** Configure GitHub integration
- [ ] **Page:** Project settings > Integrations
- [ ] **Steps:**
  1. Add GitHub repository
  2. Configure webhook
  3. Test connection
- [ ] **Expected Result:** 
  - Integration configured
  - Connection verified
  - Webhook created
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-037: Jira Integration Settings**
- [ ] **Test Case:** Configure Jira integration
- [ ] **Page:** Project settings > Integrations
- [ ] **Steps:**
  1. Add Jira URL and credentials
  2. Test connection
  3. Map fields
- [ ] **Expected Result:** 
  - Integration configured
  - Connection verified
  - Field mapping saved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-038: Slack Integration Settings**
- [ ] **Test Case:** Configure Slack integration
- [ ] **Page:** Project settings > Integrations
- [ ] **Steps:**
  1. Add Slack webhook URL
  2. Configure notification channels
  3. Test webhook
- [ ] **Expected Result:** 
  - Integration configured
  - Webhook tested successfully
  - Notifications sent to Slack
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 10. VALIDATION RULES

### 10.1 Validation Configuration

**TC-CFG-039: Configure Validation Rules**
- [ ] **Test Case:** Set validation rules
- [ ] **Page:** Project settings > Validation
- [ ] **Steps:**
  1. Configure validation rules (required fields, value ranges, etc.)
  2. Save
- [ ] **Expected Result:** 
  - Rules saved
  - Rules enforced on create/update
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CFG-040: Validation Rule Enforcement**
- [ ] **Test Case:** Validation rules applied
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/`
- [ ] **Request Body:** Story missing required field
- [ ] **Expected Result:** 
  - Status code: 400 Bad Request
  - Validation error message
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - Configuration Features  
**Total Test Cases:** ~100  
**Next File:** [05_test_checklist_filtering_search.md](./05_test_checklist_filtering_search.md)

