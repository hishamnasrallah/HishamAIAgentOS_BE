# Test Checklist: Filtering & Search Features

**Category:** Filtering & Search  
**Features:** Advanced Search, Saved Searches, Filter Presets, Quick Filters, Search History, Tag/Mention/Dependency Filters  
**Estimated Tests:** ~130  
**Priority:** MEDIUM

---

## 1. BASIC FILTERING

### 1.1 Status Filtering

**TC-FILT-001: Filter Stories by Status**
- [ ] **Test Case:** Filter stories by status
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?status=todo`
- [ ] **Expected Result:** 
  - Returns only stories with status="todo"
  - Other statuses excluded
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-002: Filter Stories by Multiple Statuses**
- [ ] **Test Case:** Filter by multiple statuses
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?status=todo,in_progress`
- [ ] **Expected Result:** 
  - Returns stories with status="todo" OR status="in_progress"
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-003: Status Filter UI**
- [ ] **Test Case:** Use status filter in UI
- [ ] **Page:** Board or stories list
- [ ] **Steps:**
  1. Select status from filter dropdown
  2. Verify results filtered
- [ ] **Expected Result:** 
  - Filter applies correctly
  - Results update
  - Active filter shown
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.2 Assignee Filtering

**TC-FILT-004: Filter by Assignee**
- [ ] **Test Case:** Filter stories by assignee
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?assigned_to={user_id}`
- [ ] **Expected Result:** 
  - Returns only stories assigned to user
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-005: Filter by Unassigned**
- [ ] **Test Case:** Filter unassigned stories
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?assigned_to=null`
- [ ] **Expected Result:** 
  - Returns only unassigned stories
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-006: Assignee Filter UI**
- [ ] **Test Case:** Use assignee filter in UI
- [ ] **Page:** Board or stories list
- [ ] **Steps:**
  1. Select assignee from filter
  2. Verify results
- [ ] **Expected Result:** 
  - Filter works correctly
  - User list populated from project members
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.3 Epic Filtering

**TC-FILT-007: Filter by Epic**
- [ ] **Test Case:** Filter stories by epic
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?epic={epic_id}`
- [ ] **Expected Result:** 
  - Returns only stories in specified epic
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-008: Filter by No Epic**
- [ ] **Test Case:** Filter stories without epic
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?epic=null`
- [ ] **Expected Result:** 
  - Returns only stories without epic
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.4 Priority Filtering

**TC-FILT-009: Filter by Priority**
- [ ] **Test Case:** Filter stories by priority
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?priority=high`
- [ ] **Expected Result:** 
  - Returns only high priority stories
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.5 Component Filtering

**TC-FILT-010: Filter by Component**
- [ ] **Test Case:** Filter stories by component
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?component=authentication`
- [ ] **Expected Result:** 
  - Returns only stories with specified component
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-011: Component Autocomplete**
- [ ] **Test Case:** Get component suggestions
- [ ] **Endpoint:** `GET /api/projects/{project_id}/components/autocomplete/?q=auth`
- [ ] **Expected Result:** 
  - Returns matching components
  - Results limited and relevant
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. TAG FILTERING

### 2.1 Tag Filters

**TC-FILT-012: Filter by Single Tag**
- [ ] **Test Case:** Filter stories by tag
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?tags=urgent`
- [ ] **Expected Result:** 
  - Returns stories containing tag "urgent"
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-013: Filter by Multiple Tags (AND)**
- [ ] **Test Case:** Filter by multiple tags (all must match)
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?tags=urgent,important`
- [ ] **Expected Result:** 
  - Returns stories containing BOTH tags
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-014: Filter by Multiple Tags (OR)**
- [ ] **Test Case:** Filter by multiple tags (any can match)
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?tags=urgent|important`
- [ ] **Expected Result:** 
  - Returns stories containing EITHER tag
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-015: Tag Filter UI**
- [ ] **Test Case:** Use tag filter in UI
- [ ] **Page:** Board or stories list
- [ ] **Steps:**
  1. Open tag filter
  2. Select tags (multi-select)
  3. Choose AND/OR logic
  4. Apply filter
- [ ] **Expected Result:** 
  - Tag filter works correctly
  - AND/OR logic applied
  - Results update
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. LABEL FILTERING

### 3.1 Label Filters

**TC-FILT-016: Filter by Labels**
- [ ] **Test Case:** Filter stories by labels
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?labels=urgent`
- [ ] **Request:** Filter by label name
- [ ] **Expected Result:** 
  - Returns stories with matching label
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-017: Label Filter UI**
- [ ] **Test Case:** Use label filter in UI
- [ ] **Page:** Board or stories list
- [ ] **Steps:**
  1. Open label filter
  2. Select labels
  3. Apply
- [ ] **Expected Result:** 
  - Label filter works
  - Labels shown with colors
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. DATE FILTERING

### 4.1 Due Date Filters

**TC-FILT-018: Filter by Due Date Range**
- [ ] **Test Case:** Filter stories by due date range
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?due_date__gte=2024-01-01&due_date__lte=2024-12-31`
- [ ] **Expected Result:** 
  - Returns stories with due dates in range
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-019: Filter Overdue Stories**
- [ ] **Test Case:** Filter overdue stories
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?overdue=true`
- [ ] **Expected Result:** 
  - Returns stories with due_date < today and status != done
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-020: Filter Due Today**
- [ ] **Test Case:** Filter stories due today
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?due_today=true`
- [ ] **Expected Result:** 
  - Returns stories with due_date = today
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-021: Filter Due Soon**
- [ ] **Test Case:** Filter stories due soon (next 3 days)
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?due_soon=true`
- [ ] **Expected Result:** 
  - Returns stories due within next 3 days
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-022: Date Range Filter UI**
- [ ] **Test Case:** Use date range filter in UI
- [ ] **Page:** Board or stories list
- [ ] **Steps:**
  1. Open date filter
  2. Select date range or preset (today, this week, this month)
  3. Apply
- [ ] **Expected Result:** 
  - Date picker works
  - Presets work
  - Filter applies correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. MENTION FILTERING

### 5.1 Mention Filters

**TC-FILT-023: Filter by Mentions**
- [ ] **Test Case:** Filter stories mentioning user
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?mentioned={user_id}`
- [ ] **Expected Result:** 
  - Returns stories where user is mentioned
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-024: Mention Filter UI**
- [ ] **Test Case:** Use mention filter in UI
- [ ] **Page:** Board or stories list
- [ ] **Steps:**
  1. Select "Mentioned" filter
  2. Choose user (or "me")
  3. Apply
- [ ] **Expected Result:** 
  - Filter works correctly
  - Shows stories with mentions
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 6. DEPENDENCY FILTERING

### 6.1 Dependency Filters

**TC-FILT-025: Filter by Dependencies**
- [ ] **Test Case:** Filter stories with dependencies
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?has_dependencies=true`
- [ ] **Expected Result:** 
  - Returns stories that have dependencies
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-FILT-026: Filter Blocked Stories**
- [ ] **Test Case:** Filter blocked stories
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?blocked=true`
- [ ] **Expected Result:** 
  - Returns stories blocked by dependencies
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 7. ADVANCED SEARCH

### 7.1 Search Functionality

**TC-SEARCH-001: Basic Text Search**
- [ ] **Test Case:** Search stories by text
- [ ] **Endpoint:** `GET /api/projects/{project_id}/search/?q=login`
- [ ] **Expected Result:** 
  - Returns stories matching "login" in title, description, etc.
  - Results ranked by relevance
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SEARCH-002: Advanced Search Query**
- [ ] **Test Case:** Use advanced search operators
- [ ] **Endpoint:** `GET /api/projects/{project_id}/search/?q=title:login AND status:todo`
- [ ] **Expected Result:** 
  - Parses query correctly
  - Applies field-specific searches
  - AND/OR/NOT operators work
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SEARCH-003: Search by Content Type**
- [ ] **Test Case:** Search specific content types
- [ ] **Endpoint:** `GET /api/projects/{project_id}/search/?q=login&content_type=story`
- [ ] **Expected Result:** 
  - Returns only stories (not tasks, bugs, etc.)
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SEARCH-004: Advanced Search UI**
- [ ] **Test Case:** Use advanced search component
- [ ] **Page:** Search page or global search
- [ ] **Steps:**
  1. Open advanced search
  2. Enter search query
  3. Select content types
  4. Add filters
  5. Execute search
- [ ] **Expected Result:** 
  - Search interface works
  - Query builder works
  - Results displayed correctly
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SEARCH-005: Global Search**
- [ ] **Test Case:** Search across all projects
- [ ] **Endpoint:** `GET /api/search/?q=login`
- [ ] **Expected Result:** 
  - Returns results from all accessible projects
  - Results grouped by project
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SEARCH-006: Global Search Shortcut**
- [ ] **Test Case:** Open global search with keyboard shortcut
- [ ] **Page:** Any page
- [ ] **Steps:**
  1. Press Ctrl+K (or Cmd+K)
  2. Verify search opens
- [ ] **Expected Result:** 
  - Search modal/panel opens
  - Focus on search input
  - Keyboard shortcut works
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 8. SAVED SEARCHES

### 8.1 Saved Search Management

**TC-SAVED-001: Create Saved Search**
- [ ] **Test Case:** Save current search
- [ ] **Endpoint:** `POST /api/projects/{project_id}/saved-searches/`
- [ ] **Request Body:**
  ```json
  {
    "name": "My Todo Stories",
    "query": "status:todo",
    "filters": {"status": "todo"}
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Saved search created
  - Can be retrieved later
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SAVED-002: List Saved Searches**
- [ ] **Test Case:** Get saved searches
- [ ] **Endpoint:** `GET /api/projects/{project_id}/saved-searches/`
- [ ] **Expected Result:** 
  - Returns user's saved searches for project
  - Includes name, query, filters
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SAVED-003: Execute Saved Search**
- [ ] **Test Case:** Run saved search
- [ ] **Endpoint:** `GET /api/projects/{project_id}/saved-searches/{saved_search_id}/execute/`
- [ ] **Expected Result:** 
  - Executes saved search query
  - Returns results
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SAVED-004: Update Saved Search**
- [ ] **Test Case:** Modify saved search
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/saved-searches/{saved_search_id}/`
- [ ] **Request Body:** `{"name": "Updated Name"}`
- [ ] **Expected Result:** 
  - Saved search updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SAVED-005: Delete Saved Search**
- [ ] **Test Case:** Remove saved search
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/saved-searches/{saved_search_id}/`
- [ ] **Expected Result:** 
  - Saved search deleted
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SAVED-006: Saved Searches UI**
- [ ] **Test Case:** Manage saved searches in UI
- [ ] **Page:** Search page or filter panel
- [ ] **Steps:**
  1. Save current search
  2. View saved searches list
  3. Click to execute saved search
  4. Edit/delete saved search
- [ ] **Expected Result:** 
  - Saved searches accessible
  - Can execute, edit, delete
  - UI intuitive
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 9. FILTER PRESETS

### 9.1 Filter Preset Management

**TC-PRESET-001: Create Filter Preset**
- [ ] **Test Case:** Save filter configuration as preset
- [ ] **Endpoint:** `POST /api/projects/{project_id}/filter-presets/`
- [ ] **Request Body:**
  ```json
  {
    "name": "High Priority Tasks",
    "filters": {
      "priority": "high",
      "status": ["todo", "in_progress"]
    }
  }
  ```
- [ ] **Expected Result:** 
  - Filter preset created
  - Can be applied later
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PRESET-002: List Filter Presets**
- [ ] **Test Case:** Get filter presets
- [ ] **Endpoint:** `GET /api/projects/{project_id}/filter-presets/`
- [ ] **Expected Result:** 
  - Returns filter presets for project
  - Includes user and shared presets
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PRESET-003: Apply Filter Preset**
- [ ] **Test Case:** Apply saved filter preset
- [ ] **Endpoint:** `GET /api/projects/{project_id}/filter-presets/{preset_id}/apply/`
- [ ] **Expected Result:** 
  - Preset filters applied
  - Results returned
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PRESET-004: Filter Preset Manager UI**
- [ ] **Test Case:** Use filter preset manager
- [ ] **Page:** Board or filter panel
- [ ] **Steps:**
  1. Configure filters
  2. Save as preset
  3. Select preset from list
  4. Apply preset
- [ ] **Expected Result:** 
  - Preset manager works
  - Presets can be saved, loaded, deleted
  - Shared presets visible
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 10. QUICK FILTERS

### 10.1 Quick Filter Actions

**TC-QUICK-001: My Stories Filter**
- [ ] **Test Case:** Filter to current user's stories
- [ ] **Endpoint:** `GET /api/projects/{project_id}/quick-filters/my-stories/`
- [ ] **Expected Result:** 
  - Returns stories assigned to current user
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-QUICK-002: Overdue Filter**
- [ ] **Test Case:** Filter overdue items
- [ ] **Endpoint:** `GET /api/projects/{project_id}/quick-filters/overdue/`
- [ ] **Expected Result:** 
  - Returns overdue stories/tasks
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-QUICK-003: Recent Activity Filter**
- [ ] **Test Case:** Filter recently updated items
- [ ] **Endpoint:** `GET /api/projects/{project_id}/quick-filters/recent/`
- [ ] **Expected Result:** 
  - Returns recently updated stories
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-QUICK-004: Quick Filters UI**
- [ ] **Test Case:** Use quick filter buttons
- [ ] **Page:** Board or stories list
- [ ] **Steps:**
  1. Click quick filter button (e.g., "My Stories")
  2. Verify filter applied
- [ ] **Expected Result:** 
  - Quick filters work
  - Active filter highlighted
  - Can combine with other filters
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 11. SEARCH HISTORY

### 11.1 Search History Tracking

**TC-HIST-001: Search History Auto-Save**
- [ ] **Test Case:** Search queries automatically saved
- [ ] **Endpoint:** `GET /api/projects/{project_id}/search/?q=login`
- [ ] **Expected Result:** 
  - Search query saved to history
  - History record created
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-HIST-002: List Search History**
- [ ] **Test Case:** Get search history
- [ ] **Endpoint:** `GET /api/projects/{project_id}/search-history/`
- [ ] **Expected Result:** 
  - Returns recent search queries
  - Ordered by most recent
  - Limited to last N searches
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-HIST-003: Clear Search History**
- [ ] **Test Case:** Delete search history
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/search-history/clear/`
- [ ] **Expected Result:** 
  - Search history cleared
  - All history records deleted
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-HIST-004: Search History UI**
- [ ] **Test Case:** Display search history in UI
- [ ] **Page:** Search page
- [ ] **Steps:**
  1. Open search
  2. Verify recent searches shown
  3. Click to reuse search
- [ ] **Expected Result:** 
  - History displayed
  - Can click to reuse
  - Clear history button works
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 12. COMBINED FILTERS

### 12.1 Multiple Filter Combinations

**TC-COMB-001: Combine Multiple Filters**
- [ ] **Test Case:** Apply multiple filters together
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/?status=todo&assigned_to={user_id}&priority=high`
- [ ] **Expected Result:** 
  - All filters applied (AND logic)
  - Returns stories matching all criteria
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMB-002: Filter AND/OR Logic**
- [ ] **Test Case:** Use AND/OR logic in filters
- [ ] **Page:** Advanced filter panel
- [ ] **Steps:**
  1. Add multiple filter groups
  2. Set AND/OR logic between groups
  3. Apply
- [ ] **Expected Result:** 
  - Complex filter logic works
  - Results match logic
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-COMB-003: Clear All Filters**
- [ ] **Test Case:** Reset all filters
- [ ] **Page:** Board or stories list
- [ ] **Steps:**
  1. Apply multiple filters
  2. Click "Clear All"
- [ ] **Expected Result:** 
  - All filters cleared
  - Results show all items
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - Filtering & Search Features  
**Total Test Cases:** ~130  
**Next File:** [06_test_checklist_automation.md](./06_test_checklist_automation.md)

