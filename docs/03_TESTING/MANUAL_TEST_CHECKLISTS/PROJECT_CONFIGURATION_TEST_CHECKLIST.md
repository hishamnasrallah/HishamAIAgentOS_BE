---
title: "Project Configuration Test Checklist"
description: "Comprehensive manual testing checklist for Project Configuration feature covering all 11 configuration categories, API endpoints, and UI components."

category: "Testing"
subcategory: "Manual Test Checklist"
language: "en"
original_language: "en"

purpose: |
  This checklist provides step-by-step manual testing procedures for Project Configuration feature. It covers backend API endpoints, frontend UI components, permission checks, and all 11 configuration categories.

target_audience:
  primary:
    - QA / Tester
    - Developer
  secondary:
    - Technical Lead
    - Project Manager

applicable_phases:
  primary:
    - Testing
  secondary:
    - Development
    - Production

tags:
  - project-configuration
  - testing
  - checklist
  - manual-testing
  - qa
  - api-testing
  - ui-testing
  - regression

keywords:
  - "project configuration testing"
  - "settings testing"
  - "configuration test"
  - "manual test"

related_features:
  - "Project Management"
  - "Workflow Management"

prerequisites:
  documents:
    - 01_CORE/PROJECT_CONFIGURATION_API.md
    - 01_CORE/USER_GUIDES/PROJECT_CONFIGURATION_GUIDE.md
  knowledge:
    - "REST API testing"
    - "Browser testing"
    - "Project management concepts"
  tools:
    - "Web browser"
    - "Postman/Insomnia (optional)"
    - "Access to HishamOS"

status: "active"
priority: "high"
difficulty: "intermediate"
completeness: "100%"
quality_status: "reviewed"

estimated_read_time: "15 minutes"
estimated_usage_time: "2-3 hours for complete testing"
estimated_update_time: "30 minutes"

version: "1.0"
last_updated: "2024-12-08"
last_reviewed: "2024-12-08"
review_frequency: "as needed"
next_review_date: "2025-01-08"

author: "QA Team"
maintainer: "QA Team"
reviewer: "Technical Lead"

related:
  - 01_CORE/PROJECT_CONFIGURATION_API.md
  - 01_CORE/USER_GUIDES/PROJECT_CONFIGURATION_GUIDE.md
  - 07_TRACKING/PROJECT_CONFIGURATION_IMPLEMENTATION.md
see_also:
  - 03_TESTING/QUICK_START_TESTING_GUIDE.md
depends_on:
  - 01_CORE/PROJECT_CONFIGURATION_API.md
prerequisite_for:
  - []

aliases:
  - "Project Config Test Checklist"
  - "Configuration Testing"

changelog:
  - version: "1.0"
    date: "2024-12-08"
    changes: "Initial test checklist for Project Configuration feature"
    author: "QA Team"
---

# Project Configuration Test Checklist

**Last Updated:** December 8, 2024  
**Estimated Time:** 2-3 hours  
**Status:** Ready for Testing

---

## 📋 Pre-Testing Setup

### Prerequisites

- [ ] Access to HishamOS development/staging environment
- [ ] Test user accounts:
  - [ ] Admin user
  - [ ] Project owner user
  - [ ] Project member user
  - [ ] Non-member user
- [ ] Test project created
- [ ] Browser developer tools ready
- [ ] Postman/Insomnia (optional, for API testing)

### Test Data

- [ ] Create test project: "Test Project Configuration"
- [ ] Note project ID for API testing
- [ ] Ensure project has at least one member (non-owner)

---

## 🔐 Authentication & Permissions Testing

### API Authentication

- [ ] **Test:** GET configuration without authentication
  - **Expected:** 401 Unauthorized
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** GET configuration with invalid token
  - **Expected:** 401 Unauthorized
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** GET configuration with valid token
  - **Expected:** 200 OK with configuration data
  - **Result:** [ ] Pass [ ] Fail

### Permission Checks

- [ ] **Test:** Project owner can view configuration
  - **Expected:** 200 OK
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Project member can view configuration
  - **Expected:** 200 OK
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Non-member cannot view configuration
  - **Expected:** 403 Forbidden or 404 Not Found
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Project owner can update configuration
  - **Expected:** 200 OK
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Project member cannot update configuration
  - **Expected:** 403 Forbidden
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Admin can view and update any configuration
  - **Expected:** 200 OK
  - **Result:** [ ] Pass [ ] Fail

---

## 🔌 Backend API Testing

### GET Configuration

- [ ] **Test:** GET `/api/v1/projects/configurations/{project_id}/`
  - **Expected:** Returns full configuration object
  - **Verify:**
    - [ ] All 11 categories present
    - [ ] Default values correct
    - [ ] Timestamps present
    - [ ] Project ID matches
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** GET configuration for non-existent project
  - **Expected:** 404 Not Found
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** GET configuration with invalid project ID format
  - **Expected:** 400 Bad Request or 404 Not Found
  - **Result:** [ ] Pass [ ] Fail

### PATCH Configuration

- [ ] **Test:** Update single field (e.g., `max_story_points_per_story`)
  - **Request:** `{"max_story_points_per_story": 34}`
  - **Expected:** Only that field updated, others unchanged
  - **Verify:** Response shows updated value
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Update multiple fields
  - **Request:** Update 3-4 different fields
  - **Expected:** All fields updated correctly
  - **Verify:** Response shows all updated values
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Update `custom_states` array
  - **Request:** Add new state, modify existing, reorder
  - **Expected:** States updated correctly
  - **Verify:** Order preserved, all states present
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Update `story_point_scale` array
  - **Request:** `{"story_point_scale": [1, 2, 3, 5, 8, 13, 21, 34]}`
  - **Expected:** Scale updated
  - **Verify:** Response shows new scale
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Update with invalid data (e.g., negative story points)
  - **Expected:** 400 Bad Request with error message
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Update with missing required fields (if any)
  - **Expected:** 400 Bad Request or successful (PATCH allows partial)
  - **Result:** [ ] Pass [ ] Fail

### POST Reset to Defaults

- [ ] **Test:** Reset configuration to defaults
  - **Precondition:** Configuration has custom values
  - **Expected:** All values reset to defaults
  - **Verify:** 
    - [ ] Default workflow states restored
    - [ ] Default story point scale restored
    - [ ] All other defaults restored
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Reset as project member (non-owner)
  - **Expected:** 403 Forbidden
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Reset as project owner
  - **Expected:** 200 OK, configuration reset
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Reset as admin
  - **Expected:** 200 OK, configuration reset
  - **Result:** [ ] Pass [ ] Fail

---

## 🎨 Frontend UI Testing

### Navigation

- [ ] **Test:** Settings button visible on project detail page
  - **Expected:** Settings button in header
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Click Settings button navigates to settings page
  - **Expected:** URL changes to `/projects/{id}/settings`
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Back arrow returns to project detail
  - **Expected:** Navigates back to project detail page
  - **Result:** [ ] Pass [ ] Fail

### Page Load

- [ ] **Test:** Settings page loads configuration data
  - **Expected:** All fields populated with current values
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Loading state displays while fetching
  - **Expected:** Loading indicator shown
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Error state displays on fetch failure
  - **Expected:** Error message displayed
  - **Result:** [ ] Pass [ ] Fail

### Tab Navigation

- [ ] **Test:** All 10 tabs are visible
  - **Expected:** Workflow, Story Points, Sprint, Board, Automation, Notifications, Permissions, Integrations, Custom Fields, Validation
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Clicking tabs switches content
  - **Expected:** Content changes to selected tab
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Tab icons display correctly
  - **Expected:** Icons visible for each tab
  - **Result:** [ ] Pass [ ] Fail

### Workflow Settings Tab

- [ ] **Test:** Add new workflow state
  - **Steps:** Click "+ Add State", fill form, verify state appears
  - **Expected:** New state added to list
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Edit workflow state name
  - **Steps:** Change name, verify update
  - **Expected:** Name updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Change workflow state color
  - **Steps:** Use color picker, select color
  - **Expected:** Color updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Set WIP limit
  - **Steps:** Enter number in WIP limit field
  - **Expected:** WIP limit saved
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Toggle default state
  - **Steps:** Check/uncheck "Default" switch
  - **Expected:** Only one state can be default
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Toggle final state
  - **Steps:** Check/uncheck "Final" switch
  - **Expected:** State marked as final
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Reorder states (move up)
  - **Steps:** Click ↑ arrow
  - **Expected:** State moves up in order
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Reorder states (move down)
  - **Steps:** Click ↓ arrow
  - **Expected:** State moves down in order
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Delete workflow state
  - **Steps:** Click × button
  - **Expected:** State removed from list
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Add state transition
  - **Steps:** Select target state from dropdown
  - **Expected:** Transition added as badge
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Remove state transition
  - **Steps:** Click × on transition badge
  - **Expected:** Transition removed
  - **Result:** [ ] Pass [ ] Fail

### Story Points Tab

- [ ] **Test:** Update min story points
  - **Steps:** Change value in input field
  - **Expected:** Value updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Update max story points per story
  - **Steps:** Change value in input field
  - **Expected:** Value updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Update max story points per sprint
  - **Steps:** Change value in input field
  - **Expected:** Value updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Apply Fibonacci preset
  - **Steps:** Click "Fibonacci" button
  - **Expected:** Scale set to [1, 2, 3, 5, 8, 13, 21]
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Apply Powers of 2 preset
  - **Steps:** Click "Powers of 2" button
  - **Expected:** Scale set to [1, 2, 4, 8, 16]
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Custom story point scale
  - **Steps:** Type custom values (e.g., "1, 2, 3, 5, 8, 13, 21, 34")
  - **Expected:** Scale updated to custom values
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Toggle story points required
  - **Steps:** Toggle switch
  - **Expected:** Setting saved
  - **Result:** [ ] Pass [ ] Fail

### Sprint Settings Tab

- [ ] **Test:** Update sprint duration
  - **Steps:** Change days input
  - **Expected:** Value updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Change sprint start day
  - **Steps:** Select day from dropdown
  - **Expected:** Day updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Toggle auto-close sprints
  - **Steps:** Toggle switch
  - **Expected:** Setting saved
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Toggle allow overcommitment
  - **Steps:** Toggle switch
  - **Expected:** Setting saved
  - **Result:** [ ] Pass [ ] Fail

### Board Customization Tab

- [ ] **Test:** Change default board view
  - **Steps:** Select view from dropdown
  - **Expected:** View updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Change swimlane grouping
  - **Steps:** Select grouping option
  - **Expected:** Grouping updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Set custom field for swimlane
  - **Steps:** Select "Custom Field", enter field name
  - **Expected:** Custom field name saved
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Change card color by
  - **Steps:** Select option from dropdown
  - **Expected:** Setting updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Toggle card display fields
  - **Steps:** Toggle switches for different fields
  - **Expected:** Selected fields saved
  - **Result:** [ ] Pass [ ] Fail

### Automation Rules Tab

- [ ] **Test:** Add new automation rule
  - **Steps:** Click "+ Add Rule", fill form
  - **Expected:** Rule added to list
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Edit rule name
  - **Steps:** Change name in input
  - **Expected:** Name updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Toggle rule enabled/disabled
  - **Steps:** Toggle switch
  - **Expected:** Rule status updated
  - **Result:** [ ] Pass [ ] Fail

### Notifications Tab

- [ ] **Test:** Toggle notification event
  - **Steps:** Toggle switch for an event
  - **Expected:** Event enabled/disabled
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Change digest frequency
  - **Steps:** Select frequency from dropdown
  - **Expected:** Frequency updated
  - **Result:** [ ] Pass [ ] Fail

### Permissions Tab

- [ ] **Test:** Change who can create stories
  - **Steps:** Select option from dropdown
  - **Expected:** Permission updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Change who can edit stories
  - **Steps:** Select option from dropdown
  - **Expected:** Permission updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Change who can delete stories
  - **Steps:** Select option from dropdown
  - **Expected:** Permission updated
  - **Result:** [ ] Pass [ ] Fail

### Integrations Tab

- [ ] **Test:** Enable GitHub integration
  - **Steps:** Toggle switch, enter repository
  - **Expected:** Integration enabled, repository saved
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Enable Jira integration
  - **Steps:** Toggle switch, enter project key
  - **Expected:** Integration enabled, project key saved
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Enable Slack integration
  - **Steps:** Toggle switch, enter channel
  - **Expected:** Integration enabled, channel saved
  - **Result:** [ ] Pass [ ] Fail

### Custom Fields Tab

- [ ] **Test:** Add custom field
  - **Steps:** Click "+ Add Custom Field", fill form
  - **Expected:** Field added to list
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Change field type
  - **Steps:** Select different type from dropdown
  - **Expected:** Type updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Toggle field required
  - **Steps:** Toggle switch
  - **Expected:** Required status updated
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Delete custom field
  - **Steps:** Click Delete button
  - **Expected:** Field removed
  - **Result:** [ ] Pass [ ] Fail

### Validation Rules Tab

- [ ] **Test:** Toggle validation rule
  - **Steps:** Toggle switch for a rule
  - **Expected:** Rule enabled/disabled
  - **Result:** [ ] Pass [ ] Fail

### Save & Reset

- [ ] **Test:** Save changes button
  - **Steps:** Make changes, click "Save Changes"
  - **Expected:** 
    - [ ] Success toast appears
    - [ ] Changes persisted
    - [ ] Unsaved changes badge disappears
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Unsaved changes indicator
  - **Steps:** Make changes without saving
  - **Expected:** Orange "Unsaved changes" badge appears
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Reset to defaults button
  - **Steps:** Click "Reset to Defaults", confirm
  - **Expected:** 
    - [ ] Confirmation dialog appears
    - [ ] All values reset to defaults
    - [ ] Success toast appears
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Cancel reset confirmation
  - **Steps:** Click "Reset", then cancel
  - **Expected:** No changes made
  - **Result:** [ ] Pass [ ] Fail

---

## 🔄 Auto-Creation Testing

- [ ] **Test:** Create new project
  - **Steps:** Create project via API or UI
  - **Expected:** Configuration automatically created
  - **Verify:** GET configuration returns default values
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Default workflow states created
  - **Expected:** Backlog, To Do, In Progress, Review, Done
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Default story point scale created
  - **Expected:** Fibonacci scale [1, 2, 3, 5, 8, 13, 21]
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Default sprint settings created
  - **Expected:** 14 days, Monday start, auto-close disabled
  - **Result:** [ ] Pass [ ] Fail

---

## 🐛 Error Handling Testing

- [ ] **Test:** Network error during save
  - **Steps:** Disconnect network, try to save
  - **Expected:** Error toast with helpful message
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Invalid data submission
  - **Steps:** Enter invalid values (e.g., negative numbers)
  - **Expected:** Validation error, changes not saved
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Permission denied error
  - **Steps:** Try to save as non-owner
  - **Expected:** 403 error, error toast
  - **Result:** [ ] Pass [ ] Fail

---

## 📱 Responsive Design Testing

- [ ] **Test:** Mobile view (320px width)
  - **Expected:** Tabs stack or use horizontal scroll
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Tablet view (768px width)
  - **Expected:** Layout adapts appropriately
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Desktop view (1920px width)
  - **Expected:** Full layout with all tabs visible
  - **Result:** [ ] Pass [ ] Pass

---

## 🔍 Browser Compatibility

- [ ] **Test:** Chrome (latest)
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Firefox (latest)
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Safari (latest)
  - **Result:** [ ] Pass [ ] Fail

- [ ] **Test:** Edge (latest)
  - **Result:** [ ] Pass [ ] Fail

---

## 📊 Test Summary

### Test Execution

- **Total Test Cases:** ~100
- **Passed:** ___
- **Failed:** ___
- **Skipped:** ___
- **Pass Rate:** ___%

### Critical Issues

- [ ] Issue 1: ________________
- [ ] Issue 2: ________________
- [ ] Issue 3: ________________

### Minor Issues

- [ ] Issue 1: ________________
- [ ] Issue 2: ________________

### Notes

_Add any additional notes or observations here:_

---

## ✅ Sign-Off

**Tester Name:** ________________  
**Date:** ________________  
**Status:** [ ] Pass [ ] Fail [ ] Needs Rework  
**Comments:** ________________

---

**Last Updated:** December 8, 2024  
**Version:** 1.0

