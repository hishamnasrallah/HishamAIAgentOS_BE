# Test Checklist: Board Features

**Category:** Board Features  
**Features:** Kanban Board, List View, Table View, Swimlanes, WIP Limits, Drag & Drop, Card Display  
**Estimated Tests:** ~120  
**Priority:** HIGH

---

## 1. KANBAN BOARD

### 1.1 Board Display

**TC-BOARD-001: Load Kanban Board (API)**
- [ ] **Test Case:** Get board data for project
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?board=true`
- [ ] **Expected Result:** 
  - Returns stories grouped by status/column
  - Includes column configuration
  - Includes WIP limits
  - Includes swimlane grouping if configured
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BOARD-002: Kanban Board Page (UI)**
- [ ] **Test Case:** Display Kanban board
- [ ] **Page:** `/projects/{project_id}/board`
- [ ] **Steps:**
  1. Navigate to board page
  2. Verify columns displayed
  3. Verify stories in columns
- [ ] **Expected Result:** 
  - Board loads correctly
  - Columns match project configuration
  - Stories displayed as cards in correct columns
  - Loading state shown while fetching
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BOARD-003: Board Columns Configuration**
- [ ] **Test Case:** Verify columns match configuration
- [ ] **Page:** Kanban board
- [ ] **Expected Result:** 
  - Columns match `board_columns` from ProjectConfiguration
  - Column order preserved
  - Column names displayed correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BOARD-004: Card Display Fields**
- [ ] **Test Case:** Cards show configured fields
- [ ] **Page:** Kanban board
- [ ] **Expected Result:** 
  - Cards display fields from `card_display_fields` config
  - Fields include: title, assignee, story points, labels, due date, etc.
  - Custom fields displayed if configured
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BOARD-005: Card Colors**
- [ ] **Test Case:** Cards colored based on configuration
- [ ] **Page:** Kanban board
- [ ] **Expected Result:** 
  - Cards colored according to `card_color_by` config
  - Colors consistent (by epic, type, component, etc.)
  - Color coding legend visible if applicable
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.2 Drag & Drop

**TC-BOARD-006: Drag Story Between Columns**
- [ ] **Test Case:** Move story to different column
- [ ] **Page:** Kanban board
- [ ] **Steps:**
  1. Drag story card from one column to another
  2. Drop in target column
- [ ] **Expected Result:** 
  - Story moves to new column
  - Status updated automatically
  - API call made to update story status
  - Card appears in new column
  - Optimistic update (immediate UI change)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BOARD-007: Drag Story - Status Validation**
- [ ] **Test Case:** Validate status transition on drag
- [ ] **Page:** Kanban board
- [ ] **Steps:**
  1. Drag story to column with invalid status transition
  2. Verify validation
- [ ] **Expected Result:** 
  - Invalid transitions rejected
  - Error message shown
  - Story returns to original column
  - Or approval workflow triggered if configured
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BOARD-008: Drag Story - WIP Limit Check**
- [ ] **Test Case:** Check WIP limit on drag
- [ ] **Page:** Kanban board
- [ ] **Steps:**
  1. Drag story to column at WIP limit
  2. Verify WIP limit enforcement
- [ ] **Expected Result:** 
  - WIP limit warning shown if exceeded
  - Drag prevented or warning shown
  - User can override if allowed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BOARD-009: Reorder Stories Within Column**
- [ ] **Test Case:** Change story order in column
- [ ] **Page:** Kanban board
- [ ] **Steps:**
  1. Drag story within same column
  2. Drop in new position
- [ ] **Expected Result:** 
  - Story order updated
  - Order persisted (if supported)
  - Visual feedback during drag
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BOARD-010: Drag Story - Loading State**
- [ ] **Test Case:** Show loading during drag operation
- [ ] **Page:** Kanban board
- [ ] **Expected Result:** 
  - Loading indicator shown during API call
  - Card shows loading state
  - Error handling if API fails
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.3 Card Interactions

**TC-BOARD-011: Open Story from Card**
- [ ] **Test Case:** Click card to view story
- [ ] **Page:** Kanban board
- [ ] **Steps:**
  1. Click on story card
- [ ] **Expected Result:** 
  - Story view modal opens
  - Story details displayed
  - All tabs accessible
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BOARD-012: Quick Actions on Card**
- [ ] **Test Case:** Access quick actions from card
- [ ] **Page:** Kanban board
- [ ] **Steps:**
  1. Hover over card
  2. Click quick actions menu (if available)
  3. Select action (edit, assign, add label, etc.)
- [ ] **Expected Result:** 
  - Quick actions menu appears
  - Actions work correctly
  - Card updates after action
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BOARD-013: Card Hover Effects**
- [ ] **Test Case:** Visual feedback on hover
- [ ] **Page:** Kanban board
- [ ] **Expected Result:** 
  - Card elevates or highlights on hover
  - Cursor changes to pointer
  - Smooth transitions
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. SWIMLANES

### 2.1 Swimlane Display

**TC-SWIM-001: Swimlanes by Epic**
- [ ] **Test Case:** Group stories by epic in swimlanes
- [ ] **Page:** Kanban board
- [ ] **Configuration:** `swimlane_grouping: "epic"`
- [ ] **Expected Result:** 
  - Stories grouped into swimlanes by epic
  - Each epic has own row
  - Stories without epic in "No Epic" swimlane
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SWIM-002: Swimlanes by Assignee**
- [ ] **Test Case:** Group stories by assignee
- [ ] **Page:** Kanban board
- [ ] **Configuration:** `swimlane_grouping: "assignee"`
- [ ] **Expected Result:** 
  - Stories grouped by assigned user
  - Unassigned stories in "Unassigned" swimlane
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SWIM-003: Swimlanes by Priority**
- [ ] **Test Case:** Group stories by priority
- [ ] **Page:** Kanban board
- [ ] **Configuration:** `swimlane_grouping: "priority"`
- [ ] **Expected Result:** 
  - Stories grouped by priority level
  - Priority labels shown in swimlane headers
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SWIM-004: Swimlanes by Component**
- [ ] **Test Case:** Group stories by component
- [ ] **Page:** Kanban board
- [ ] **Configuration:** `swimlane_grouping: "component"`
- [ ] **Expected Result:** 
  - Stories grouped by component
  - Component names in swimlane headers
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SWIM-005: Swimlanes by Story Type**
- [ ] **Test Case:** Group stories by type
- [ ] **Page:** Kanban board
- [ ] **Configuration:** `swimlane_grouping: "story_type"`
- [ ] **Expected Result:** 
  - Stories grouped by type (feature, bug, etc.)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SWIM-006: Collapsible Swimlanes**
- [ ] **Test Case:** Collapse/expand swimlanes
- [ ] **Page:** Kanban board
- [ ] **Steps:**
  1. Click collapse icon on swimlane header
  2. Verify swimlane collapses
  3. Click again to expand
- [ ] **Expected Result:** 
  - Swimlane collapses/expands smoothly
  - Story count shown when collapsed
  - State persisted (if supported)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SWIM-007: Drag Story Between Swimlanes**
- [ ] **Test Case:** Move story to different swimlane
- [ ] **Page:** Kanban board
- [ ] **Steps:**
  1. Drag story to different swimlane
  2. Drop in target swimlane
- [ ] **Expected Result:** 
  - Story moves to new swimlane
  - Grouping field updated (epic, assignee, etc.)
  - API call made to update story
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SWIM-008: No Swimlanes (Flat View)**
- [ ] **Test Case:** Disable swimlanes
- [ ] **Page:** Kanban board
- [ ] **Configuration:** `swimlane_grouping: null`
- [ ] **Expected Result:** 
  - Board displays without swimlanes
  - All stories in flat columns
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. WIP LIMITS

### 3.1 WIP Limit Display

**TC-WIP-001: WIP Limits in Column Headers**
- [ ] **Test Case:** Display WIP limits
- [ ] **Page:** Kanban board
- [ ] **Expected Result:** 
  - Column headers show WIP limit (e.g., "In Progress (3/5)")
  - Current count and limit displayed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WIP-002: WIP Limit Exceeded Warning**
- [ ] **Test Case:** Show warning when limit exceeded
- [ ] **Page:** Kanban board
- [ ] **Steps:**
  1. Add stories to column until limit exceeded
- [ ] **Expected Result:** 
  - Warning indicator shown (color change, icon)
  - Column header highlights
  - Tooltip shows exceeded count
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WIP-003: WIP Limit Enforcement on Drag**
- [ ] **Test Case:** Prevent drag if limit exceeded
- [ ] **Page:** Kanban board
- [ ] **Steps:**
  1. Column at WIP limit
  2. Try to drag story into it
- [ ] **Expected Result:** 
  - Drag prevented or warning shown
  - User can override if project allows overcommitment
  - Error message if drag prevented
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WIP-004: WIP Limit Configuration**
- [ ] **Test Case:** Configure WIP limits
- [ ] **Page:** Project settings
- [ ] **Steps:**
  1. Navigate to board configuration
  2. Set WIP limits for columns
  3. Save
- [ ] **Expected Result:** 
  - Limits saved
  - Limits applied on board
  - Limits visible in column headers
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. LIST VIEW

### 4.1 List View Display

**TC-LIST-001: List View Page**
- [ ] **Test Case:** Display stories in list view
- [ ] **Page:** `/projects/{project_id}/board` (list view)
- [ ] **Steps:**
  1. Switch to list view
  2. Verify stories displayed
- [ ] **Expected Result:** 
  - Stories displayed as list items
  - Key information visible (title, status, assignee, etc.)
  - Clickable to open story
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-LIST-002: List View Sorting**
- [ ] **Test Case:** Sort stories in list view
- [ ] **Page:** List view
- [ ] **Steps:**
  1. Click column header to sort
  2. Verify sorting applied
- [ ] **Expected Result:** 
  - Stories sorted by selected column
  - Sort direction toggles (asc/desc)
  - Sort indicator shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-LIST-003: List View Filtering**
- [ ] **Test Case:** Filter stories in list view
- [ ] **Page:** List view
- [ ] **Steps:**
  1. Apply filters
  2. Verify filtered results
- [ ] **Expected Result:** 
  - Filters apply correctly
  - Filtered count shown
  - Clear filters button works
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-LIST-004: List View Pagination**
- [ ] **Test Case:** Paginate list view
- [ ] **Page:** List view
- [ ] **Expected Result:** 
  - Pagination controls shown if many stories
  - Page size configurable
  - Navigation works (next, previous, page numbers)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. TABLE VIEW

### 5.1 Table View Display

**TC-TABLE-001: Table View Page**
- [ ] **Test Case:** Display stories in table view
- [ ] **Page:** `/projects/{project_id}/board` (table view)
- [ ] **Steps:**
  1. Switch to table view
  2. Verify stories in table format
- [ ] **Expected Result:** 
  - Stories displayed in table
  - Columns match configuration
  - Rows clickable
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TABLE-002: Table View Column Configuration**
- [ ] **Test Case:** Configure visible columns
- [ ] **Page:** Table view
- [ ] **Steps:**
  1. Open column selector
  2. Toggle columns
- [ ] **Expected Result:** 
  - Columns can be shown/hidden
  - Column order can be changed
  - Preferences saved
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TABLE-003: Table View Sorting**
- [ ] **Test Case:** Sort by column
- [ ] **Page:** Table view
- [ ] **Steps:**
  1. Click column header
- [ ] **Expected Result:** 
  - Table sorted by column
  - Sort indicator shown
  - Multi-column sorting if supported
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TABLE-004: Table View Inline Editing**
- [ ] **Test Case:** Edit fields inline
- [ ] **Page:** Table view
- [ ] **Steps:**
  1. Click on editable cell
  2. Modify value
  3. Save
- [ ] **Expected Result:** 
  - Cell becomes editable
  - Changes saved on blur/enter
  - Validation applied
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-TABLE-005: Table View Row Selection**
- [ ] **Test Case:** Select multiple rows
- [ ] **Page:** Table view
- [ ] **Steps:**
  1. Click checkbox to select rows
  2. Verify bulk actions available
- [ ] **Expected Result:** 
  - Rows can be selected
  - Selection count shown
  - Bulk actions menu appears
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 6. VIEW SWITCHING

### 6.1 View Toggle

**TC-VIEW-001: Switch Between Views**
- [ ] **Test Case:** Toggle between Kanban, List, Table views
- [ ] **Page:** Board page
- [ ] **Steps:**
  1. Click view toggle buttons
  2. Verify view changes
- [ ] **Expected Result:** 
  - View switches smoothly
  - View preference saved
  - Data loads correctly for each view
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-VIEW-002: View Preference Persistence**
- [ ] **Test Case:** Remember selected view
- [ ] **Page:** Board page
- [ ] **Steps:**
  1. Select view
  2. Navigate away
  3. Return to board
- [ ] **Expected Result:** 
  - Previously selected view restored
  - Preference stored in localStorage or user settings
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 7. BOARD FILTERING

### 7.1 Board-Level Filters

**TC-BFILT-001: Filter Board Stories**
- [ ] **Test Case:** Apply filters to board
- [ ] **Page:** Board page
- [ ] **Steps:**
  1. Open filter panel
  2. Apply filters (status, assignee, epic, etc.)
  3. Verify board updates
- [ ] **Expected Result:** 
  - Filters apply to all views
  - Filtered count shown
  - Clear filters works
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BFILT-002: Quick Filters**
- [ ] **Test Case:** Use quick filter buttons
- [ ] **Page:** Board page
- [ ] **Steps:**
  1. Click quick filter (e.g., "My Stories", "Overdue")
  2. Verify filter applied
- [ ] **Expected Result:** 
  - Quick filter applies immediately
  - Filter state shown
  - Can combine with other filters
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-BFILT-003: Saved Filter Presets**
- [ ] **Test Case:** Use saved filter preset
- [ ] **Page:** Board page
- [ ] **Steps:**
  1. Select saved filter preset
  2. Verify preset applied
- [ ] **Expected Result:** 
  - Preset filters applied
  - Preset name shown
  - Can save current filters as preset
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 8. BOARD PERFORMANCE

### 8.1 Large Dataset Handling

**TC-PERF-001: Board with Many Stories**
- [ ] **Test Case:** Load board with 100+ stories
- [ ] **Page:** Board page
- [ ] **Expected Result:** 
  - Board loads within reasonable time
  - Virtual scrolling or pagination if needed
  - No performance degradation
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERF-002: Board with Many Columns**
- [ ] **Test Case:** Load board with many columns
- [ ] **Page:** Board page
- [ ] **Expected Result:** 
  - Horizontal scrolling works
  - Columns remain responsive
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERF-003: Real-time Updates**
- [ ] **Test Case:** Board updates in real-time
- [ ] **Page:** Board page
- [ ] **Steps:**
  1. Open board in two tabs
  2. Make change in one tab
  3. Verify update in other tab
- [ ] **Expected Result:** 
  - Changes reflected automatically
  - WebSocket or polling updates board
  - No page refresh needed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - Board Features  
**Total Test Cases:** ~120  
**Next File:** [04_test_checklist_configuration.md](./04_test_checklist_configuration.md)

