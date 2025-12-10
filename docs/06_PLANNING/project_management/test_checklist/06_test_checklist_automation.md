# Test Checklist: Automation & Workflow Features

**Category:** Automation  
**Features:** Automation Rules, Notification Delivery, Approval Workflows, Scheduled Tasks  
**Estimated Tests:** ~110  
**Priority:** MEDIUM

---

## 1. AUTOMATION RULE EXECUTION

### 1.1 Status Change Triggers

**TC-AUTO-001: Rule Triggers on Status Change**
- [ ] **Test Case:** Rule executes when story status changes
- [ ] **Steps:**
  1. Create rule: trigger on status change from "todo" to "in_progress", action: assign to user X
  2. Change story status from "todo" to "in_progress"
- [ ] **Expected Result:** 
  - Rule executes automatically
  - Story assigned to user X
  - Action logged
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-AUTO-002: Rule with Multiple Actions**
- [ ] **Test Case:** Rule executes multiple actions
- [ ] **Steps:**
  1. Create rule with multiple actions (assign, add label, notify)
  2. Trigger rule
- [ ] **Expected Result:** 
  - All actions execute
  - Actions executed in order
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-AUTO-003: Rule with Conditions**
- [ ] **Test Case:** Rule executes only if conditions met
- [ ] **Steps:**
  1. Create rule: trigger on status change, condition: priority="high", action: assign to user X
  2. Change status on high priority story
  3. Change status on low priority story
- [ ] **Expected Result:** 
  - Rule executes for high priority story
  - Rule does not execute for low priority story
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.2 Field Update Triggers

**TC-AUTO-004: Rule Triggers on Field Update**
- [ ] **Test Case:** Rule executes when field changes
- [ ] **Steps:**
  1. Create rule: trigger on field update (assigned_to), action: notify user
  2. Assign story to user
- [ ] **Expected Result:** 
  - Rule executes
  - User notified
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.3 On-Create Triggers

**TC-AUTO-005: Rule Triggers on Story Create**
- [ ] **Test Case:** Rule executes when story created
- [ ] **Steps:**
  1. Create rule: trigger on story create, action: add default label
  2. Create new story
- [ ] **Expected Result:** 
  - Rule executes
  - Default label added
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.4 Scheduled Triggers

**TC-AUTO-006: Daily Scheduled Rule**
- [ ] **Test Case:** Rule executes daily at scheduled time
- [ ] **Steps:**
  1. Create rule: trigger daily at 9:00 AM, action: update status of overdue stories
  2. Wait for scheduled time or trigger Celery task manually
- [ ] **Expected Result:** 
  - Rule executes at scheduled time
  - Celery task runs
  - Actions applied
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-AUTO-007: Weekly Scheduled Rule**
- [ ] **Test Case:** Rule executes weekly
- [ ] **Steps:**
  1. Create rule: trigger weekly on Monday at 9:00 AM
  2. Verify schedule
- [ ] **Expected Result:** 
  - Rule executes on specified day and time
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-AUTO-008: Monthly Scheduled Rule**
- [ ] **Test Case:** Rule executes monthly
- [ ] **Steps:**
  1. Create rule: trigger monthly on day 1 at 9:00 AM
  2. Verify schedule
- [ ] **Expected Result:** 
  - Rule executes on specified day of month
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.5 Task Complete Triggers

**TC-AUTO-009: Rule Triggers on Task Complete**
- [ ] **Test Case:** Rule executes when all tasks complete
- [ ] **Steps:**
  1. Create rule: trigger on all tasks complete, action: update story status to "done"
  2. Complete all tasks in story
- [ ] **Expected Result:** 
  - Rule executes
  - Story status updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. AUTOMATION ACTIONS

### 2.1 Assign Action

**TC-AUTO-010: Auto-Assign Action**
- [ ] **Test Case:** Automatically assign story to user
- [ ] **Steps:**
  1. Create rule with assign action
  2. Trigger rule
- [ ] **Expected Result:** 
  - Story assigned to specified user
  - Assignment notification sent
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-AUTO-011: Auto-Assign Based on Component**
- [ ] **Test Case:** Assign based on component
- [ ] **Steps:**
  1. Create rule: if component="frontend", assign to frontend team lead
  2. Set story component to "frontend"
- [ ] **Expected Result:** 
  - Story assigned to correct user
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 2.2 Update Field Action

**TC-AUTO-012: Auto-Update Field**
- [ ] **Test Case:** Automatically update field
- [ ] **Steps:**
  1. Create rule: action update_field priority="high"
  2. Trigger rule
- [ ] **Expected Result:** 
  - Priority field updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 2.3 Update Status Action

**TC-AUTO-013: Auto-Update Status**
- [ ] **Test Case:** Automatically update status
- [ ] **Steps:**
  1. Create rule: action update_status="in_progress"
  2. Trigger rule
- [ ] **Expected Result:** 
  - Status updated
  - Status transition validated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 2.4 Add Label Action

**TC-AUTO-014: Auto-Add Label**
- [ ] **Test Case:** Automatically add label
- [ ] **Steps:**
  1. Create rule: action add_label name="automated"
  2. Trigger rule
- [ ] **Expected Result:** 
  - Label added to story
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 2.5 Notify Action

**TC-AUTO-015: Auto-Notify**
- [ ] **Test Case:** Automatically send notification
- [ ] **Steps:**
  1. Create rule: action notify recipients=[user_id]
  2. Trigger rule
- [ ] **Expected Result:** 
  - Notification created
  - User receives notification
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. NOTIFICATION DELIVERY

### 3.1 In-App Notifications

**TC-NOTIF-001: Create Notification**
- [ ] **Test Case:** Create in-app notification
- [ ] **Endpoint:** `POST /api/projects/{project_id}/notifications/`
- [ ] **Request Body:**
  ```json
  {
    "story": "story-uuid",
    "notification_type": "status_change",
    "message": "Story status changed",
    "recipients": ["user-uuid"]
  }
  ```
- [ ] **Expected Result:** 
  - Notification created
  - Notification visible to recipients
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-NOTIF-002: List Notifications**
- [ ] **Test Case:** Get user's notifications
- [ ] **Endpoint:** `GET /api/projects/{project_id}/notifications/`
- [ ] **Expected Result:** 
  - Returns user's notifications
  - Can filter by read/unread
  - Ordered by most recent
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-NOTIF-003: Mark Notification as Read**
- [ ] **Test Case:** Mark notification as read
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/notifications/{notification_id}/`
- [ ] **Request Body:** `{"read": true}`
- [ ] **Expected Result:** 
  - Notification marked as read
  - Unread count updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-NOTIF-004: Mark All as Read**
- [ ] **Test Case:** Mark all notifications as read
- [ ] **Endpoint:** `POST /api/projects/{project_id}/notifications/mark-all-read/`
- [ ] **Expected Result:** 
  - All notifications marked as read
  - Unread count reset
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-NOTIF-005: Notification Bell/Icon**
- [ ] **Test Case:** Display notification indicator
- [ ] **Page:** Any page (header)
- [ ] **Expected Result:** 
  - Notification bell icon visible
  - Badge shows unread count
  - Clicking opens notification panel
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-NOTIF-006: Notification Panel**
- [ ] **Test Case:** View notifications in panel
- [ ] **Page:** Notification panel
- [ ] **Steps:**
  1. Click notification bell
  2. View notifications
  3. Click notification to view story
- [ ] **Expected Result:** 
  - Notifications listed
  - Can mark as read
  - Can navigate to related story
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 3.2 Email Notifications

**TC-NOTIF-007: Send Email Notification**
- [ ] **Test Case:** Email notification sent
- [ ] **Steps:**
  1. Configure email notifications enabled
  2. Trigger notification event
- [ ] **Expected Result:** 
  - Email sent to recipient
  - Email contains story details
  - Email template rendered correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-NOTIF-008: Email Notification Preferences**
- [ ] **Test Case:** User can disable email notifications
- [ ] **Page:** User settings
- [ ] **Steps:**
  1. Disable email notifications
  2. Trigger notification
- [ ] **Expected Result:** 
  - Email not sent
  - In-app notification still sent (if enabled)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-NOTIF-009: Email Notification Queue**
- [ ] **Test Case:** Email notifications queued and sent by Celery
- [ ] **Steps:**
  1. Create multiple notifications
  2. Run Celery task `send_pending_email_notifications`
- [ ] **Expected Result:** 
  - Emails queued
  - Celery task processes queue
  - Emails sent
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. APPROVAL WORKFLOWS

### 4.1 Status Change Approvals

**TC-APPROV-001: Request Status Change Approval**
- [ ] **Test Case:** Request approval for status change
- [ ] **Endpoint:** `POST /api/projects/{project_id}/status-change-approvals/`
- [ ] **Request Body:**
  ```json
  {
    "story": "story-uuid",
    "requested_status": "done",
    "approvers": ["user-uuid"]
  }
  ```
- [ ] **Expected Result:** 
  - Approval request created
  - Approvers notified
  - Story status not changed yet
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-APPROV-002: Approve Status Change**
- [ ] **Test Case:** Approve status change request
- [ ] **Endpoint:** `POST /api/projects/{project_id}/status-change-approvals/{approval_id}/approve/`
- [ ] **Expected Result:** 
  - Approval granted
  - Story status updated
  - Requester notified
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-APPROV-003: Reject Status Change**
- [ ] **Test Case:** Reject status change request
- [ ] **Endpoint:** `POST /api/projects/{project_id}/status-change-approvals/{approval_id}/reject/`
- [ ] **Request Body:** `{"reason": "Not ready"}`
- [ ] **Expected Result:** 
  - Approval rejected
  - Story status unchanged
  - Requester notified with reason
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-APPROV-004: List Pending Approvals**
- [ ] **Test Case:** Get pending approvals
- [ ] **Endpoint:** `GET /api/projects/{project_id}/status-change-approvals/?status=pending`
- [ ] **Expected Result:** 
  - Returns pending approvals for user
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-APPROV-005: Approval Request Modal (UI)**
- [ ] **Test Case:** Request approval via UI
- [ ] **Page:** Story view or board
- [ ] **Steps:**
  1. Try to change status requiring approval
  2. Approval request modal opens
  3. Select approvers
  4. Submit request
- [ ] **Expected Result:** 
  - Modal works correctly
  - Approvers can be selected
  - Request submitted
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-APPROV-006: Pending Approvals List (UI)**
- [ ] **Test Case:** View pending approvals
- [ ] **Page:** Approvals page or dashboard
- [ ] **Steps:**
  1. Navigate to approvals
  2. View pending approvals
  3. Approve/reject from list
- [ ] **Expected Result:** 
  - Pending approvals displayed
  - Can approve/reject
  - Status updates after action
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. ASSIGNMENT RULES

### 5.1 Auto-Assignment

**TC-ASSIGN-001: Assignment Rule Based on Component**
- [ ] **Test Case:** Auto-assign based on component
- [ ] **Steps:**
  1. Configure assignment rule: component="frontend" -> assign to frontend lead
  2. Create story with component="frontend"
- [ ] **Expected Result:** 
  - Story automatically assigned
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ASSIGN-002: Assignment Rule Based on Epic**
- [ ] **Test Case:** Auto-assign based on epic owner
- [ ] **Steps:**
  1. Configure rule: assign to epic owner
  2. Add story to epic
- [ ] **Expected Result:** 
  - Story assigned to epic owner
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 6. AUTO-TAGGING

### 6.1 Automatic Tagging

**TC-TAG-001: Auto-Tag Based on Component**
- [ ] **Test Case:** Automatically add tag based on component
- [ ] **Steps:**
  1. Configure auto-tagging: component="frontend" -> tag "frontend"
  2. Set story component to "frontend"
- [ ] **Expected Result:** 
  - Tag "frontend" added automatically
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TAG-002: Auto-Tag Based on Priority**
- [ ] **Test Case:** Automatically add tag based on priority
- [ ] **Steps:**
  1. Configure auto-tagging: priority="high" -> tag "urgent"
  2. Set story priority to "high"
- [ ] **Expected Result:** 
  - Tag "urgent" added automatically
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 7. SPRINT AUTOMATION

### 7.1 Sprint Auto-Close

**TC-SPRINT-AUTO-001: Auto-Close Sprint**
- [ ] **Test Case:** Sprint automatically closes when end_date passes
- [ ] **Steps:**
  1. Enable auto_close_sprints in project config
  2. Create sprint with past end_date
  3. Run Celery task `auto_close_sprints`
- [ ] **Expected Result:** 
  - Sprint status changed to "completed"
  - Task logged
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SPRINT-AUTO-002: Auto-Create Sprint**
- [ ] **Test Case:** Automatically create next sprint
- [ ] **Endpoint:** `POST /api/projects/{project_id}/sprints/auto-create/`
- [ ] **Expected Result:** 
  - New sprint created
  - Sprint number auto-incremented
  - Dates calculated from previous sprint
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SPRINT-AUTO-003: Sprint Health Check**
- [ ] **Test Case:** Check sprint health
- [ ] **Endpoint:** `GET /api/projects/{project_id}/sprints/{sprint_id}/health/`
- [ ] **Expected Result:** 
  - Returns sprint health metrics
  - Shows burndown status
  - Identifies risks
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 8. CELERY TASKS

### 8.1 Scheduled Tasks

**TC-CELERY-001: Due Date Check Task**
- [ ] **Test Case:** Celery task checks due dates
- [ ] **Task:** `check_due_dates_approaching`
- [ ] **Steps:**
  1. Create stories with due dates (today, tomorrow, 3 days)
  2. Run Celery task
- [ ] **Expected Result:** 
  - Task runs successfully
  - Notifications sent for approaching due dates
  - Task logs results
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CELERY-002: Scheduled Automation Rules Task**
- [ ] **Test Case:** Celery task executes scheduled rules
- [ ] **Task:** `execute_scheduled_automation_rules`
- [ ] **Steps:**
  1. Create scheduled automation rule
  2. Run Celery task at scheduled time
- [ ] **Expected Result:** 
  - Task runs
  - Scheduled rules executed
  - Actions applied
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-CELERY-003: Email Notification Task**
- [ ] **Test Case:** Celery task sends pending emails
- [ ] **Task:** `send_pending_email_notifications`
- [ ] **Steps:**
  1. Create notifications with email_sent=False
  2. Run Celery task
- [ ] **Expected Result:** 
  - Emails sent
  - email_sent flag updated
  - Task logs results
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - Automation & Workflow Features  
**Total Test Cases:** ~110  
**Next File:** [07_test_checklist_reports_analytics.md](./07_test_checklist_reports_analytics.md)

