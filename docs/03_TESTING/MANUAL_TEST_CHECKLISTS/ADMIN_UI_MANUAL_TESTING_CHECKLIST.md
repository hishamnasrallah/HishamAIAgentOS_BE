---
title: "Admin UI Manual Testing Checklist"
description: "**Date:** December 6, 2024"

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Project Manager
    - CTO / Technical Lead
  secondary:
    - All

applicable_phases:
  primary:
    - Testing
    - QA
  secondary:
    - Development

tags:
  - checklist
  - admin
  - testing
  - test
  - core

status: "active"
priority: "medium"
difficulty: "intermediate"
completeness: "100%"
quality_status: "draft"

estimated_read_time: "10 minutes"

version: "1.0"
last_updated: "2025-12-06"
last_reviewed: "2025-12-06"
review_frequency: "quarterly"

author: "Development Team"
maintainer: "Development Team"

related: []
see_also: []
depends_on: []
prerequisite_for: []

aliases: []

changelog:
  - version: "1.0"
    date: "2025-12-06"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---

# Admin UI Manual Testing Checklist

**Date:** December 6, 2024  
**Version:** 1.0  
**Tester:** _______________  
**Test Date:** _______________

---

## 🔐 Prerequisites

- [ ] Backend server is running (`python manage.py runserver` or `daphne`)
- [ ] Frontend server is running (`npm run dev`)
- [ ] You have an admin user account (role: 'admin')
- [ ] You are logged in as an admin user
- [ ] Browser console is open (F12) to check for errors

---

## 🧑‍💼 User Management UI Testing

### Navigation & Access
- [ ] Navigate to `/admin/users` - page loads without errors
- [ ] Admin sidebar shows "Users" link
- [ ] Clicking "Users" navigates to user management page
- [ ] Page title shows "User Management"
- [ ] Page description shows "Manage users, roles, and permissions"

### User List Display
- [ ] User list displays all users (if any exist)
- [ ] Each user card shows:
  - [ ] User avatar/icon
  - [ ] Full name (first_name + last_name)
  - [ ] Email address
  - [ ] Role badge (admin, manager, developer, viewer) with correct color
  - [ ] Status badge (Active/Inactive) with correct color
  - [ ] 2FA badge (if 2FA is enabled)
- [ ] Empty state shows "No users found" when no users exist
- [ ] Loading skeleton appears while data is fetching

### Search Functionality
- [ ] Type in search box - filters users in real-time
- [ ] Search by email - returns matching users
- [ ] Search by username - returns matching users
- [ ] Search by first name - returns matching users
- [ ] Search by last name - returns matching users
- [ ] Clear search - shows all users again
- [ ] Search with no results - shows "No users found"

### Filters
- [ ] Role filter dropdown works:
  - [ ] "All Roles" shows all users
  - [ ] "Admin" shows only admin users
  - [ ] "Manager" shows only manager users
  - [ ] "Developer" shows only developer users
  - [ ] "Viewer" shows only viewer users
- [ ] Status filter dropdown works:
  - [ ] "All Status" shows all users
  - [ ] "Active" shows only active users
  - [ ] "Inactive" shows only inactive users
- [ ] Combined filters (role + status) work correctly
- [ ] Filters persist when navigating away and back

### Create New User
- [ ] Click "New User" button - form appears
- [ ] Form shows "Create New User" title
- [ ] All required fields are marked with *
- [ ] Fill in form:
  - [ ] Email field accepts valid email format
  - [ ] Username field accepts text
  - [ ] First Name field accepts text
  - [ ] Last Name field accepts text
  - [ ] Password field is password type (hidden)
  - [ ] Confirm Password field is password type (hidden)
  - [ ] Role dropdown shows all 4 options
  - [ ] Preferred Language dropdown works
  - [ ] Timezone dropdown works
- [ ] Validation:
  - [ ] Submit with empty email - shows error
  - [ ] Submit with invalid email - shows error
  - [ ] Submit with empty username - shows error
  - [ ] Submit with empty first name - shows error
  - [ ] Submit with empty last name - shows error
  - [ ] Submit with password < 8 chars - shows error
  - [ ] Submit with mismatched passwords - shows error
- [ ] Submit valid form:
  - [ ] Shows "Saving..." button state
  - [ ] User is created successfully
  - [ ] Form closes automatically
  - [ ] New user appears in list
  - [ ] Success message (if implemented)
- [ ] Cancel button closes form without saving

### Edit User
- [ ] Click "Edit" button on a user - form appears
- [ ] Form shows "Edit User" title
- [ ] Form is pre-filled with user data:
  - [ ] Email is pre-filled (and disabled)
  - [ ] Username is pre-filled
  - [ ] First Name is pre-filled
  - [ ] Last Name is pre-filled
  - [ ] Role is pre-filled
  - [ ] Preferred Language is pre-filled
  - [ ] Timezone is pre-filled
- [ ] Password fields are empty (optional for edit)
- [ ] Change user data and submit:
  - [ ] Changes are saved successfully
  - [ ] Form closes automatically
  - [ ] Updated data appears in list
- [ ] Change password:
  - [ ] Enter new password (8+ chars)
  - [ ] Confirm password matches
  - [ ] Submit - password is updated
- [ ] Change role:
  - [ ] Select different role
  - [ ] Submit - role is updated
  - [ ] Role badge updates in list

### Activate/Deactivate User
- [ ] For an active user:
  - [ ] Click deactivate button (UserX icon)
  - [ ] User status changes to "Inactive"
  - [ ] Status badge updates to "Inactive"
- [ ] For an inactive user:
  - [ ] Click activate button (UserCheck icon)
  - [ ] User status changes to "Active"
  - [ ] Status badge updates to "Active"
- [ ] Try to deactivate yourself:
  - [ ] Should show error or prevent action
  - [ ] Your account remains active

### Delete User
- [ ] Click "Delete" button (Trash icon) on a user
- [ ] Confirmation dialog appears:
  - [ ] Shows warning icon
  - [ ] Shows "Delete User" title
  - [ ] Shows warning message
  - [ ] Shows "Cancel" button
  - [ ] Shows "Delete User" button (destructive style)
- [ ] Click "Cancel" - dialog closes, user not deleted
- [ ] Click "Delete User":
  - [ ] Button shows "Deleting..." state
  - [ ] User is deleted
  - [ ] Dialog closes
  - [ ] User disappears from list
- [ ] Try to delete yourself:
  - [ ] Should show error or prevent action
  - [ ] Your account remains

### Error Handling
- [ ] Disconnect internet - shows error message
- [ ] Submit form with server error - shows error message
- [ ] Try to create user with duplicate email - shows error
- [ ] Try to create user with duplicate username - shows error

---

## 🔌 Platform Configuration UI Testing

### Navigation & Access
- [ ] Navigate to `/admin/platforms` - page loads without errors
- [ ] Admin sidebar shows "Platforms" link
- [ ] Clicking "Platforms" navigates to platform management page
- [ ] Page title shows "Platform Configuration"
- [ ] Page description shows "Manage AI platform integrations and API keys"

### Platform List Display
- [ ] Platform list displays all platforms (if any exist)
- [ ] Each platform card shows:
  - [ ] Platform icon/avatar
  - [ ] Display name
  - [ ] Platform name (openai, anthropic, google)
  - [ ] Default model name
  - [ ] "Default" badge (if is_default = true)
  - [ ] "API Key" badge (if has_api_key = true)
  - [ ] Status badge (Active/Inactive/Maintenance)
  - [ ] Health badge (Healthy/Unhealthy)
  - [ ] Request count badge
- [ ] Empty state shows "No platforms found" when no platforms exist
- [ ] Loading skeleton appears while data is fetching

### Search & Filters
- [ ] Search by display name - filters platforms
- [ ] Search by platform name - filters platforms
- [ ] Search by model name - filters platforms
- [ ] Status filter works (All/Active/Inactive/Maintenance)
- [ ] Health filter works (All/Healthy/Unhealthy)
- [ ] Combined filters work correctly

### Create New Platform
- [ ] Click "New Platform" button - form appears
- [ ] Form shows "Create New Platform" title
- [ ] Fill in form:
  - [ ] Platform dropdown (OpenAI/Anthropic/Google)
  - [ ] Display Name (required)
  - [ ] API Type dropdown
  - [ ] Default Model (required)
  - [ ] API Key (password field with show/hide toggle)
  - [ ] API URL (optional)
  - [ ] Organization ID (optional)
  - [ ] Timeout (number, required)
  - [ ] Max Tokens (number, required)
  - [ ] Capabilities checkboxes (Vision, JSON Mode, Image Generation)
  - [ ] Rate Limit Per Minute (number, required)
  - [ ] Rate Limit Per Day (number, required)
  - [ ] Status dropdown
  - [ ] Priority (number)
  - [ ] "Set as Default Platform" checkbox
  - [ ] "Enabled" checkbox
- [ ] Validation:
  - [ ] Submit with empty display name - shows error
  - [ ] Submit with empty default model - shows error
  - [ ] Submit with timeout < 1 - shows error
  - [ ] Submit with max_tokens < 1 - shows error
  - [ ] Submit with rate_limit < 1 - shows error
- [ ] Submit valid form:
  - [ ] Shows "Saving..." button state
  - [ ] Platform is created successfully
  - [ ] API key is encrypted (check backend)
  - [ ] Form closes automatically
  - [ ] New platform appears in list
- [ ] Test API key visibility toggle:
  - [ ] Click eye icon - password becomes visible
  - [ ] Click eye-off icon - password becomes hidden

### Edit Platform
- [ ] Click "Edit" button on a platform - form appears
- [ ] Form shows "Edit Platform" title
- [ ] Form is pre-filled with platform data:
  - [ ] Platform name is pre-filled (and disabled)
  - [ ] All fields are pre-filled correctly
- [ ] API Key field is empty (for security)
- [ ] Change platform data and submit:
  - [ ] Changes are saved successfully
  - [ ] Form closes automatically
  - [ ] Updated data appears in list
- [ ] Update API key:
  - [ ] Enter new API key
  - [ ] Submit - API key is encrypted and saved
  - [ ] Old API key is replaced
- [ ] Leave API key empty:
  - [ ] Existing API key is preserved (not cleared)

### Delete Platform
- [ ] Click "Delete" button on a platform
- [ ] Confirmation dialog appears with warning
- [ ] Click "Cancel" - dialog closes, platform not deleted
- [ ] Click "Delete Platform":
  - [ ] Platform is deleted
  - [ ] Platform disappears from list

### Health Status
- [ ] Healthy platforms show green badge
- [ ] Unhealthy platforms show red badge
- [ ] Health status updates when platform health changes

---

## 🤖 Agent Management UI Testing

### Navigation & Access
- [ ] Navigate to `/admin/agents` - page loads without errors
- [ ] Admin sidebar shows "Agents" link
- [ ] Clicking "Agents" navigates to agent management page
- [ ] Page title shows "Agent Management"
- [ ] Page description shows "Manage AI agents, capabilities, and configurations"

### Agent List Display
- [ ] Agent list displays all agents (if any exist)
- [ ] Each agent card shows:
  - [ ] Agent icon/avatar
  - [ ] Agent name
  - [ ] Agent ID badge
  - [ ] Description (truncated if long)
  - [ ] Status badge (Active/Inactive/Maintenance)
  - [ ] Preferred platform badge
  - [ ] Model name badge
  - [ ] Invocation count badge (if > 0)
  - [ ] Success rate badge (if > 0)
  - [ ] Average response time badge (if > 0)
  - [ ] Capabilities badges (first 3, then "+X more")
- [ ] Empty state shows "No agents found" when no agents exist
- [ ] Loading skeleton appears while data is fetching

### Search & Filters
- [ ] Search by agent name - filters agents
- [ ] Search by agent ID - filters agents
- [ ] Search by description - filters agents
- [ ] Status filter works (All/Active/Inactive/Maintenance)
- [ ] Platform filter works (All/OpenAI/Anthropic/Google)
- [ ] Combined filters work correctly

### Create New Agent
- [ ] Click "New Agent" button - form appears
- [ ] Form shows "Create New Agent" title
- [ ] Fill in form:
  - [ ] Agent ID (required, unique, disabled after creation)
  - [ ] Name (required)
  - [ ] Description (required, textarea)
  - [ ] Capabilities (multi-select checkboxes, 15 options)
  - [ ] System Prompt (required, large textarea)
  - [ ] Preferred Platform dropdown
  - [ ] Model Name
  - [ ] Temperature (0-2, number with step 0.1)
  - [ ] Max Tokens (number, required)
  - [ ] Status dropdown
  - [ ] Version
  - [ ] Fallback Platforms (checkboxes, excludes preferred)
- [ ] Validation:
  - [ ] Submit with empty agent_id - shows error
  - [ ] Submit with empty name - shows error
  - [ ] Submit with empty description - shows error
  - [ ] Submit with empty system_prompt - shows error
  - [ ] Submit with temperature < 0 or > 2 - shows error
  - [ ] Submit with max_tokens < 1 - shows error
- [ ] Test capabilities selection:
  - [ ] Check multiple capabilities
  - [ ] Uncheck capabilities
  - [ ] All 15 options are available
- [ ] Test fallback platforms:
  - [ ] Preferred platform is excluded from fallback options
  - [ ] Can select multiple fallback platforms
- [ ] Submit valid form:
  - [ ] Shows "Saving..." button state
  - [ ] Agent is created successfully
  - [ ] Form closes automatically
  - [ ] New agent appears in list

### Edit Agent
- [ ] Click "Edit" button on an agent - form appears
- [ ] Form shows "Edit Agent" title
- [ ] Form is pre-filled with agent data:
  - [ ] Agent ID is pre-filled (and disabled)
  - [ ] All fields are pre-filled correctly
  - [ ] Capabilities checkboxes reflect current selection
  - [ ] Fallback platforms checkboxes reflect current selection
- [ ] Change agent data and submit:
  - [ ] Changes are saved successfully
  - [ ] Form closes automatically
  - [ ] Updated data appears in list
- [ ] Change capabilities:
  - [ ] Add new capabilities
  - [ ] Remove capabilities
  - [ ] Submit - capabilities are updated
- [ ] Change system prompt:
  - [ ] Edit system prompt text
  - [ ] Submit - system prompt is updated

### Delete Agent
- [ ] Click "Delete" button on an agent
- [ ] Confirmation dialog appears with warning
- [ ] Click "Cancel" - dialog closes, agent not deleted
- [ ] Click "Delete Agent":
  - [ ] Agent is deleted
  - [ ] Agent disappears from list

### Metrics Display
- [ ] Agents with invocations show metrics:
  - [ ] Total invocations count
  - [ ] Success rate percentage (color-coded)
  - [ ] Average response time in seconds
- [ ] Agents without invocations don't show metrics

---

## 🎨 UI/UX General Testing

### Responsive Design
- [ ] Test on desktop (1920x1080) - all layouts work
- [ ] Test on tablet (768px width) - layouts adapt
- [ ] Test on mobile (375px width) - layouts adapt
- [ ] Filters stack vertically on mobile
- [ ] Forms are scrollable on mobile
- [ ] Cards stack properly on small screens

### Loading States
- [ ] Loading skeletons appear during data fetch
- [ ] Loading states don't cause layout shift
- [ ] "Saving..." button states work correctly
- [ ] "Deleting..." button states work correctly

### Error Handling
- [ ] Network errors show user-friendly messages
- [ ] Validation errors appear inline below fields
- [ ] Server errors show appropriate messages
- [ ] Error messages are clear and actionable

### Accessibility
- [ ] All buttons have accessible labels
- [ ] Form fields have proper labels
- [ ] Error messages are associated with fields
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Focus indicators are visible
- [ ] Color contrast meets WCAG standards

### Performance
- [ ] Page loads within 2 seconds
- [ ] List filtering is responsive (< 500ms)
- [ ] Form submission is responsive
- [ ] No console errors
- [ ] No console warnings

---

## 🔒 Security Testing

### Access Control
- [ ] Non-admin users cannot access `/admin/users`
- [ ] Non-admin users cannot access `/admin/platforms`
- [ ] Non-admin users cannot access `/admin/agents`
- [ ] Non-admin users are redirected to home page
- [ ] Admin users can access all admin pages

### API Key Security
- [ ] API keys are never displayed in the UI
- [ ] Only `has_api_key` boolean is shown
- [ ] API keys are encrypted in the database
- [ ] API keys can only be updated, never retrieved

### Data Validation
- [ ] Email validation works (rejects invalid emails)
- [ ] Password validation works (min 8 characters)
- [ ] Role validation works (only valid roles accepted)
- [ ] Numeric fields reject non-numeric input
- [ ] Required fields cannot be empty

### Self-Protection
- [ ] Users cannot deactivate themselves
- [ ] Users cannot delete themselves
- [ ] Admin cannot lock themselves out

---

## 📊 Browser Compatibility

- [ ] Chrome (latest) - all features work
- [ ] Firefox (latest) - all features work
- [ ] Edge (latest) - all features work
- [ ] Safari (latest) - all features work (if available)

---

## 🐛 Bug Reporting Template

If you find any issues, please report them using this format:

**Bug #X: [Short Description]**

- **Page:** [e.g., User Management]
- **Steps to Reproduce:**
  1. 
  2. 
  3. 
- **Expected Behavior:**
- **Actual Behavior:**
- **Screenshots:** (if applicable)
- **Browser:** [e.g., Chrome 120]
- **Console Errors:** (if any)

---

## ✅ Test Completion

- [ ] All User Management tests passed
- [ ] All Platform Configuration tests passed
- [ ] All Agent Management tests passed
- [ ] All UI/UX tests passed
- [ ] All Security tests passed
- [ ] All Browser Compatibility tests passed

**Overall Status:** ☐ Pass ☐ Fail  
**Notes:**

---

**Tester Signature:** _______________  
**Date:** _______________

