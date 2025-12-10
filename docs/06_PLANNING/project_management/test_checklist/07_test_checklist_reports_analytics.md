# Test Checklist: Reports & Analytics Features

**Category:** Reports & Analytics  
**Features:** Statistics, Reports, Dashboards, Charts, Burndown, Velocity, Cycle Time, Lead Time  
**Estimated Tests:** ~90  
**Priority:** MEDIUM

---

## 1. STATISTICS API

### 1.1 Story Statistics

**TC-STAT-001: Story Type Distribution**
- [ ] **Test Case:** Get story type statistics
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/story-types/`
- [ ] **Expected Result:** 
  - Returns count of stories by type
  - Includes percentages
  - Cached for performance
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STAT-002: Story Type Trends**
- [ ] **Test Case:** Get story type trends over time
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/story-types/trends/?period=month`
- [ ] **Expected Result:** 
  - Returns trend data by time period
  - Shows growth/decline
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STAT-003: Component Distribution**
- [ ] **Test Case:** Get component statistics
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/components/`
- [ ] **Expected Result:** 
  - Returns count of stories by component
  - Includes percentages
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STAT-004: Component Trends**
- [ ] **Test Case:** Get component trends
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/components/trends/`
- [ ] **Expected Result:** 
  - Returns component trends over time
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STAT-005: Status Distribution**
- [ ] **Test Case:** Get status distribution
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/status/`
- [ ] **Expected Result:** 
  - Returns count of stories by status
  - Shows workflow distribution
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STAT-006: Assignee Distribution**
- [ ] **Test Case:** Get assignee workload
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/assignees/`
- [ ] **Expected Result:** 
  - Returns story count per assignee
  - Shows workload distribution
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. REPORTS API

### 2.1 Time Reports

**TC-REP-001: Time Report**
- [ ] **Test Case:** Get time tracking report
- [ ] **Endpoint:** `GET /api/projects/{project_id}/reports/time/?start_date=2024-01-01&end_date=2024-12-31`
- [ ] **Expected Result:** 
  - Returns time logged by user, story, task
  - Includes totals and breakdowns
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-REP-002: Burndown Chart Data**
- [ ] **Test Case:** Get burndown chart data
- [ ] **Endpoint:** `GET /api/projects/{project_id}/reports/burndown/?sprint_id={sprint_id}`
- [ ] **Expected Result:** 
  - Returns burndown data (dates, remaining points)
  - Includes ideal burndown line
  - Includes actual burndown line
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-REP-003: Velocity Tracking**
- [ ] **Test Case:** Get velocity metrics
- [ ] **Endpoint:** `GET /api/projects/{project_id}/reports/velocity/?num_sprints=5`
- [ ] **Expected Result:** 
  - Returns velocity per sprint
  - Shows average velocity
  - Includes trend
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-REP-004: Estimation History**
- [ ] **Test Case:** Get estimation history
- [ ] **Endpoint:** `GET /api/projects/{project_id}/reports/estimation-history/`
- [ ] **Expected Result:** 
  - Returns estimation changes over time
  - Shows estimation accuracy
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-REP-005: Actual vs Estimated**
- [ ] **Test Case:** Compare actual vs estimated
- [ ] **Endpoint:** `GET /api/projects/{project_id}/reports/actual-vs-estimated/`
- [ ] **Expected Result:** 
  - Returns comparison data
  - Shows variance
  - Identifies estimation patterns
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-REP-006: Epic Progress**
- [ ] **Test Case:** Get epic progress report
- [ ] **Endpoint:** `GET /api/projects/{project_id}/reports/epic-progress/`
- [ ] **Expected Result:** 
  - Returns progress for each epic
  - Shows completion percentage
  - Shows story count
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-REP-007: Sprint Report**
- [ ] **Test Case:** Get sprint report
- [ ] **Endpoint:** `GET /api/projects/{project_id}/reports/sprint/?sprint_id={sprint_id}`
- [ ] **Expected Result:** 
  - Returns sprint summary
  - Includes completed stories, velocity, burndown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. ANALYTICS API

### 3.1 Cycle Time

**TC-ANAL-001: Cycle Time Tracking**
- [ ] **Test Case:** Get cycle time metrics
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/cycle-time/`
- [ ] **Expected Result:** 
  - Returns average cycle time
  - Shows cycle time distribution
  - Includes trends
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ANAL-002: Lead Time Tracking**
- [ ] **Test Case:** Get lead time metrics
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/lead-time/`
- [ ] **Expected Result:** 
  - Returns average lead time
  - Shows lead time distribution
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ANAL-003: Throughput**
- [ ] **Test Case:** Get throughput metrics
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/throughput/`
- [ ] **Expected Result:** 
  - Returns stories completed per time period
  - Shows throughput trends
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ANAL-004: Project Health**
- [ ] **Test Case:** Get project health score
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/health/`
- [ ] **Expected Result:** 
  - Returns health score (0-100)
  - Includes factors (velocity, burndown, blockers, etc.)
  - Shows health trends
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-ANAL-005: Team Performance**
- [ ] **Test Case:** Get team performance metrics
- [ ] **Endpoint:** `GET /api/projects/{project_id}/statistics/team-performance/`
- [ ] **Expected Result:** 
  - Returns performance per team member
  - Shows velocity, completion rate, etc.
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. REPORTS DASHBOARD UI

### 4.1 Dashboard Display

**TC-DASH-001: Reports Dashboard Page**
- [ ] **Test Case:** Display reports dashboard
- [ ] **Page:** `/projects/{project_id}/reports`
- [ ] **Steps:**
  1. Navigate to reports page
  2. Verify dashboard loads
- [ ] **Expected Result:** 
  - Dashboard displays
  - Charts render correctly
  - Data loads
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DASH-002: Burndown Chart Visualization**
- [ ] **Test Case:** Display burndown chart
- [ ] **Page:** Reports dashboard
- [ ] **Steps:**
  1. View burndown chart
  2. Verify chart displays correctly
- [ ] **Expected Result:** 
  - Chart renders
  - Shows ideal and actual lines
  - Interactive (hover for details)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DASH-003: Velocity Chart**
- [ ] **Test Case:** Display velocity chart
- [ ] **Page:** Reports dashboard
- [ ] **Expected Result:** 
  - Velocity chart displays
  - Shows velocity per sprint
  - Shows average line
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DASH-004: Story Type Distribution Chart**
- [ ] **Test Case:** Display story type pie/bar chart
- [ ] **Page:** Reports dashboard
- [ ] **Expected Result:** 
  - Chart displays
  - Shows distribution
  - Interactive
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DASH-005: Component Distribution Chart**
- [ ] **Test Case:** Display component distribution
- [ ] **Page:** Reports dashboard
- [ ] **Expected Result:** 
  - Chart displays
  - Shows component breakdown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DASH-006: Cycle Time Chart**
- [ ] **Test Case:** Display cycle time chart
- [ ] **Page:** Reports dashboard
- [ ] **Expected Result:** 
  - Chart displays
  - Shows cycle time distribution
  - Shows trends
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DASH-007: Project Health Indicator**
- [ ] **Test Case:** Display project health
- [ ] **Page:** Reports dashboard
- [ ] **Expected Result:** 
  - Health score displayed
  - Visual indicator (color, gauge)
  - Health factors shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DASH-008: Team Performance Table**
- [ ] **Test Case:** Display team performance
- [ ] **Page:** Reports dashboard
- [ ] **Expected Result:** 
  - Table displays
  - Shows metrics per team member
  - Sortable columns
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DASH-009: Date Range Selection**
- [ ] **Test Case:** Filter reports by date range
- [ ] **Page:** Reports dashboard
- [ ] **Steps:**
  1. Select date range
  2. Verify reports update
- [ ] **Expected Result:** 
  - Date picker works
  - Reports filtered correctly
  - Charts update
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-DASH-010: Export Reports**
- [ ] **Test Case:** Export report data
- [ ] **Page:** Reports dashboard
- [ ] **Steps:**
  1. Click export button
  2. Select format (CSV, PDF)
  3. Download
- [ ] **Expected Result:** 
  - Report exported
  - File downloads
  - Format correct
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. STATISTICS DASHBOARD UI

### 5.1 Statistics Display

**TC-STAT-UI-001: Statistics Dashboard**
- [ ] **Test Case:** Display statistics dashboard
- [ ] **Page:** `/projects/{project_id}/statistics`
- [ ] **Expected Result:** 
  - Dashboard displays
  - Statistics cards show key metrics
  - Charts display
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STAT-UI-002: Statistics Cards**
- [ ] **Test Case:** Display statistics summary cards
- [ ] **Page:** Statistics dashboard
- [ ] **Expected Result:** 
  - Cards show: total stories, completed, in progress, etc.
  - Cards update in real-time
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-STAT-UI-003: Statistics Charts**
- [ ] **Test Case:** Display statistics charts
- [ ] **Page:** Statistics dashboard
- [ ] **Expected Result:** 
  - Charts render correctly
  - Interactive (hover, click)
  - Responsive
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 6. TIME BUDGET REPORTS

### 6.1 Time Budget Analytics

**TC-BUDGET-001: Time Budget Summary**
- [ ] **Test Case:** Get time budget summary
- [ ] **Endpoint:** `GET /api/projects/{project_id}/time-budgets/summary/`
- [ ] **Expected Result:** 
  - Returns budget vs spent
  - Shows remaining budget
  - Shows overruns
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BUDGET-002: Overtime Records**
- [ ] **Test Case:** Get overtime records
- [ ] **Endpoint:** `GET /api/projects/{project_id}/overtime-records/`
- [ ] **Expected Result:** 
  - Returns overtime records
  - Shows budget overruns
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - Reports & Analytics Features  
**Total Test Cases:** ~90  
**Next File:** [08_test_checklist_time_tracking.md](./08_test_checklist_time_tracking.md)

