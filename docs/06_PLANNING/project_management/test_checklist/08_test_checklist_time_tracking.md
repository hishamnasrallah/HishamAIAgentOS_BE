# Test Checklist: Time Tracking Features

**Category:** Time Tracking  
**Features:** Time Logs, Global Timer, Time Budgets, Overtime Tracking  
**Estimated Tests:** ~80  
**Priority:** MEDIUM

---

## 1. TIME LOGS

### 1.1 Time Log CRUD

**TC-TIME-001: Create Time Log (API)**
- [ ] **Test Case:** Log time manually
- [ ] **Endpoint:** `POST /api/projects/{project_id}/time-logs/`
- [ ] **Request Body:**
  ```json
  {
    "story": "story-uuid",
    "task": "task-uuid",
    "description": "Implemented login feature",
    "duration_minutes": 120,
    "logged_date": "2024-12-10"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Time log created
  - `user` set to current user
  - Linked to story/task
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-002: List Time Logs (API)**
- [ ] **Test Case:** Get time logs
- [ ] **Endpoint:** `GET /api/projects/{project_id}/time-logs/`
- [ ] **Query Params:** Filter by user, story, task, date range
- [ ] **Expected Result:** 
  - Returns time logs
  - Filters work correctly
  - Ordered by date (most recent first)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-003: Retrieve Time Log (API)**
- [ ] **Test Case:** Get single time log
- [ ] **Endpoint:** `GET /api/projects/{project_id}/time-logs/{time_log_id}/`
- [ ] **Expected Result:** 
  - Returns complete time log data
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-004: Update Time Log (API)**
- [ ] **Test Case:** Edit time log
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/time-logs/{time_log_id}/`
- [ ] **Request Body:** `{"duration_minutes": 180}`
- [ ] **Expected Result:** 
  - Time log updated
  - Only owner can update (or admin)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-005: Delete Time Log (API)**
- [ ] **Test Case:** Delete time log
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/time-logs/{time_log_id}/`
- [ ] **Expected Result:** 
  - Time log deleted
  - Only owner can delete (or admin)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.2 Timer Functionality

**TC-TIME-006: Start Timer (API)**
- [ ] **Test Case:** Start time tracking timer
- [ ] **Endpoint:** `POST /api/projects/{project_id}/time-logs/start-timer/`
- [ ] **Request Body:**
  ```json
  {
    "story": "story-uuid",
    "description": "Working on feature"
  }
  ```
- [ ] **Expected Result:** 
  - Timer started
  - `start_time` set
  - `end_time` null
  - Only one active timer per user
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-007: Stop Timer (API)**
- [ ] **Test Case:** Stop time tracking timer
- [ ] **Endpoint:** `POST /api/projects/{project_id}/time-logs/{time_log_id}/stop-timer/`
- [ ] **Expected Result:** 
  - Timer stopped
  - `end_time` set
  - `duration_minutes` calculated
  - Time log saved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-008: Get Active Timer (API)**
- [ ] **Test Case:** Get current active timer
- [ ] **Endpoint:** `GET /api/projects/{project_id}/time-logs/active-timer/`
- [ ] **Expected Result:** 
  - Returns active timer if exists
  - Returns null if no active timer
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-009: Global Timer Widget (UI)**
- [ ] **Test Case:** Display global timer
- [ ] **Page:** Any page (fixed bottom-right widget)
- [ ] **Steps:**
  1. Verify timer widget visible
  2. Click to start timer
  3. Verify timer running
  4. Click to stop
- [ ] **Expected Result:** 
  - Timer widget always visible
  - Start/stop works
  - Timer displays elapsed time
  - Can select story/task
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-010: Timer Persistence**
- [ ] **Test Case:** Timer persists across page navigation
- [ ] **Page:** Any page
- [ ] **Steps:**
  1. Start timer
  2. Navigate to different page
  3. Verify timer still running
- [ ] **Expected Result:** 
  - Timer continues running
  - Elapsed time accurate
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.3 Time Log Forms

**TC-TIME-011: Time Log Form Modal (UI)**
- [ ] **Test Case:** Create time log via form
- [ ] **Page:** Time logs page or modal
- [ ] **Steps:**
  1. Open time log form
  2. Fill in details (story, duration, date, description)
  3. Submit
- [ ] **Expected Result:** 
  - Form validates correctly
  - Time log created
  - Success message displayed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-012: Time Logs Page (UI)**
- [ ] **Test Case:** Display time logs list
- [ ] **Page:** `/projects/{project_id}/time-logs`
- [ ] **Steps:**
  1. Navigate to time logs page
  2. Verify logs displayed
  3. Test filtering
- [ ] **Expected Result:** 
  - Time logs listed
  - Can filter by user, story, date
  - Summary cards show totals
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-013: Time Log Summary Cards**
- [ ] **Test Case:** Display time summary
- [ ] **Page:** Time logs page
- [ ] **Expected Result:** 
  - Cards show: today's time, week's time, month's time
  - Totals calculated correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. TIME BUDGETS

### 2.1 Time Budget Management

**TC-BUDGET-001: Create Time Budget (API)**
- [ ] **Test Case:** Create time budget
- [ ] **Endpoint:** `POST /api/projects/{project_id}/time-budgets/`
- [ ] **Request Body:**
  ```json
  {
    "scope": "project",
    "project": "project-uuid",
    "budget_hours": 100,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Budget created
  - Scope validated (only one scope field set)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUDGET-002: Create Budget for Sprint**
- [ ] **Test Case:** Create budget for sprint
- [ ] **Endpoint:** `POST /api/projects/{project_id}/time-budgets/`
- [ ] **Request Body:**
  ```json
  {
    "scope": "sprint",
    "sprint": "sprint-uuid",
    "budget_hours": 40
  }
  ```
- [ ] **Expected Result:** 
  - Budget created for sprint
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUDGET-003: Create Budget for Story**
- [ ] **Test Case:** Create budget for story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/time-budgets/`
- [ ] **Request Body:**
  ```json
  {
    "scope": "story",
    "story": "story-uuid",
    "budget_hours": 8
  }
  ```
- [ ] **Expected Result:** 
  - Budget created for story
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUDGET-004: List Time Budgets (API)**
- [ ] **Test Case:** Get time budgets
- [ ] **Endpoint:** `GET /api/projects/{project_id}/time-budgets/`
- [ ] **Query Params:** Filter by scope, date range
- [ ] **Expected Result:** 
  - Returns budgets
  - Includes spent hours, remaining hours
  - Includes percentage used
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUDGET-005: Retrieve Time Budget (API)**
- [ ] **Test Case:** Get single budget
- [ ] **Endpoint:** `GET /api/projects/{project_id}/time-budgets/{budget_id}/`
- [ ] **Expected Result:** 
  - Returns complete budget data
  - Includes metrics (spent, remaining, percentage)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUDGET-006: Update Time Budget (API)**
- [ ] **Test Case:** Update budget
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/time-budgets/{budget_id}/`
- [ ] **Request Body:** `{"budget_hours": 120}`
- [ ] **Expected Result:** 
  - Budget updated
  - Metrics recalculated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUDGET-007: Recalculate Budget (API)**
- [ ] **Test Case:** Recalculate budget metrics
- [ ] **Endpoint:** `POST /api/projects/{project_id}/time-budgets/{budget_id}/recalculate/`
- [ ] **Expected Result:** 
  - Spent hours recalculated
  - Metrics updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUDGET-008: Budget Summary (API)**
- [ ] **Test Case:** Get budget summary
- [ ] **Endpoint:** `GET /api/projects/{project_id}/time-budgets/summary/`
- [ ] **Expected Result:** 
  - Returns summary of all budgets
  - Shows total budget, spent, remaining
  - Shows overruns
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUDGET-009: Time Budget UI**
- [ ] **Test Case:** Manage budgets via UI
- [ ] **Page:** Project settings or budgets page
- [ ] **Steps:**
  1. Create budget
  2. View budgets list
  3. Edit budget
  4. View budget details
- [ ] **Expected Result:** 
  - Budget management works
  - Metrics displayed correctly
  - Visual indicators for overruns
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. OVERTIME TRACKING

### 3.1 Overtime Records

**TC-OVERTIME-001: Automatic Overtime Detection**
- [ ] **Test Case:** Overtime record created when budget exceeded
- [ ] **Steps:**
  1. Create budget with 10 hours
  2. Log 11 hours
  3. Verify overtime record created
- [ ] **Expected Result:** 
  - Overtime record created automatically
  - Record shows overrun amount
  - Alert sent if configured
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-OVERTIME-002: List Overtime Records (API)**
- [ ] **Test Case:** Get overtime records
- [ ] **Endpoint:** `GET /api/projects/{project_id}/overtime-records/`
- [ ] **Query Params:** Filter by scope, date range
- [ ] **Expected Result:** 
  - Returns overtime records
  - Includes overrun details
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-OVERTIME-003: Retrieve Overtime Record (API)**
- [ ] **Test Case:** Get single overtime record
- [ ] **Endpoint:** `GET /api/projects/{project_id}/overtime-records/{record_id}/`
- [ ] **Expected Result:** 
  - Returns complete record data
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-OVERTIME-004: Overtime Alerts**
- [ ] **Test Case:** Receive alert on overtime
- [ ] **Steps:**
  1. Configure overtime alerts
  2. Exceed budget
- [ ] **Expected Result:** 
  - Alert notification sent
  - Alert visible in UI
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-OVERTIME-005: Overtime Records UI**
- [ ] **Test Case:** View overtime records
- [ ] **Page:** Budgets or reports page
- [ ] **Expected Result:** 
  - Overtime records displayed
  - Overruns highlighted
  - Can filter and sort
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. TIME TRACKING INTEGRATION

### 4.1 Story/Task Integration

**TC-TIME-INT-001: Time Logs on Story**
- [ ] **Test Case:** View time logs for story
- [ ] **Page:** Story view modal
- [ ] **Steps:**
  1. Open story
  2. Navigate to time logs section
- [ ] **Expected Result:** 
  - Time logs for story displayed
  - Total time shown
  - Can add time log from story
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-INT-002: Time Logs on Task**
- [ ] **Test Case:** View time logs for task
- [ ] **Page:** Task view
- [ ] **Expected Result:** 
  - Time logs for task displayed
  - Total time shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-INT-003: Time Budget on Story**
- [ ] **Test Case:** View time budget for story
- [ ] **Page:** Story view modal
- [ ] **Expected Result:** 
  - Budget displayed if exists
  - Spent vs budget shown
  - Progress indicator
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. TIME REPORTS

### 5.1 Time Reports

**TC-TIME-REP-001: Time Report by User**
- [ ] **Test Case:** Get time report by user
- [ ] **Endpoint:** `GET /api/projects/{project_id}/reports/time/?group_by=user`
- [ ] **Expected Result:** 
  - Returns time logged per user
  - Includes totals
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-REP-002: Time Report by Story**
- [ ] **Test Case:** Get time report by story
- [ ] **Endpoint:** `GET /api/projects/{project_id}/reports/time/?group_by=story`
- [ ] **Expected Result:** 
  - Returns time logged per story
  - Includes totals
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TIME-REP-003: Time Report by Date**
- [ ] **Test Case:** Get time report by date
- [ ] **Endpoint:** `GET /api/projects/{project_id}/reports/time/?group_by=date&start_date=2024-01-01&end_date=2024-12-31`
- [ ] **Expected Result:** 
  - Returns time logged per date
  - Includes daily totals
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - Time Tracking Features  
**Total Test Cases:** ~80  
**Next File:** [09_test_checklist_integrations.md](./09_test_checklist_integrations.md)

