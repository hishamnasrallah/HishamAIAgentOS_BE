---
title: "Phase 17-18: Admin & Configuration UI - Comprehensive Manual Testing Checklist"
description: "**Date:** December 2024"

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
  - admin
  - phase-17
  - testing
  - test
  - phase
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

# Phase 17-18: Admin & Configuration UI - Comprehensive Manual Testing Checklist

**Date:** December 6, 2024  
**Component:** Complete Admin & Configuration UI System  
**Phase:** Phase 17-18  
**Status:** ✅ Complete (100%)  
**Last Updated:** December 6, 2024 - Added bulk operations, import/export, activity log, role management, permissions matrix

---

## 📋 Pre-Testing Setup

- [ ] Backend server is running (`python manage.py runserver` or `daphne`)
- [ ] Frontend server is running (`npm run dev`)
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] You have an admin user account (role: 'admin')
- [ ] You are logged in as an admin user
- [ ] Browser console is open (F12) to check for errors
- [ ] At least one AI platform configured
- [ ] At least one agent loaded

---

## 🏗️ Admin Layout & Navigation

### 1. Admin Layout Component

#### 1.1 Layout Structure
- [ ] Navigate to any `/admin/*` route
- [ ] Admin layout displays correctly
- [ ] Admin sidebar is visible on left
- [ ] Main content area is visible
- [ ] Layout is responsive (sidebar collapses on mobile)

#### 1.2 Admin Sidebar
- [ ] Sidebar shows all admin sections:
  - [ ] Dashboard
  - [ ] Users
  - [ ] Agents
  - [ ] Platforms
  - [ ] System Settings
  - [ ] Analytics
  - [ ] API Keys (if implemented)
  - [ ] Security (if implemented)
  - [ ] Database (if implemented)
- [ ] Active section is highlighted
- [ ] Clicking section navigates to correct page
- [ ] Sidebar is collapsible (if implemented)

#### 1.3 Admin Route Protection
- [ ] Non-admin user cannot access `/admin/*` routes
- [ ] Non-admin user is redirected to home page
- [ ] Admin user can access all admin routes
- [ ] Route protection works correctly

---

## 📊 Admin Dashboard

### 1. Dashboard Overview

#### 1.1 Dashboard Access
- [ ] Navigate to `/admin` - dashboard loads without errors
- [ ] Dashboard shows "Admin Dashboard" title
- [ ] Dashboard shows "System overview and statistics" description
- [ ] No console errors

#### 1.2 Statistics Cards
- [ ] **Total Users** card displays:
  - [ ] Correct count from database
  - [ ] Users icon
  - [ ] Blue color scheme
- [ ] **Active Agents** card displays:
  - [ ] Correct count of active agents
  - [ ] Bot icon
  - [ ] Green color scheme
- [ ] **AI Platforms** card displays:
  - [ ] Correct count of platforms
  - [ ] Server icon
  - [ ] Purple color scheme
- [ ] **System Health** card displays:
  - [ ] Health status (healthy/degraded/unhealthy)
  - [ ] Activity icon
  - [ ] Color changes based on status (green/red)
- [ ] **Total Commands** card displays:
  - [ ] Correct count of active commands
  - [ ] TrendingUp icon
  - [ ] Orange color scheme
- [ ] **Security Status** card displays:
  - [ ] "Secure" status
  - [ ] Shield icon
  - [ ] Green color scheme

#### 1.3 Real-Time Data
- [ ] Statistics update automatically (every 30 seconds)
- [ ] Loading state shows skeleton cards while fetching
- [ ] Data refreshes without page reload
- [ ] No errors during refresh

#### 1.4 Quick Actions
- [ ] **Manage Users** card:
  - [ ] Clickable link
  - [ ] Navigates to `/admin/users`
  - [ ] Hover effect works
- [ ] **Configure Platforms** card:
  - [ ] Clickable link
  - [ ] Navigates to `/admin/platforms`
  - [ ] Hover effect works
- [ ] **System Settings** card:
  - [ ] Clickable link
  - [ ] Navigates to `/admin/settings`
  - [ ] Hover effect works

#### 1.5 Recent Activity Feed
- [ ] **Recent Users** section:
  - [ ] Shows users created in last 7 days
  - [ ] Displays email, role, and time ago
  - [ ] Shows "No recent users" if none exist
  - [ ] Updates automatically (every 60 seconds)
- [ ] **Recent Agents** section:
  - [ ] Shows agents created in last 7 days
  - [ ] Displays name, status, and time ago
  - [ ] Shows "No recent agents" if none exist
- [ ] **Recent Platforms** section:
  - [ ] Shows platforms configured in last 7 days
  - [ ] Displays platform name, enabled status, and time ago
  - [ ] Shows "No recent platforms" if none exist
- [ ] **Recent Commands** section:
  - [ ] Shows commands added in last 7 days
  - [ ] Displays name, category, and time ago
  - [ ] Shows "No recent commands" if none exist
- [ ] Empty state shows "No recent activity in the last 7 days" when all sections are empty

#### 1.6 API Integration
- [ ] `GET /api/v1/monitoring/admin/stats/` endpoint works
- [ ] `GET /api/v1/monitoring/admin/activity/` endpoint works
- [ ] API returns correct data structure
- [ ] API handles errors gracefully
- [ ] 403 Forbidden for non-admin users

---

## 👥 User Management UI

### 2. User List Page

#### 2.1 Navigation & Access
- [ ] Navigate to `/admin/users` - page loads without errors
- [ ] Admin sidebar shows "Users" link
- [ ] Clicking "Users" navigates to user management page
- [ ] Page title shows "User Management"
- [ ] Page description shows "Manage users, roles, and permissions"

#### 2.2 User List Display
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

#### 2.3 Search Functionality
- [ ] Type in search box - filters users in real-time
- [ ] Search by email - returns matching users
- [ ] Search by username - returns matching users
- [ ] Search by first name - returns matching users
- [ ] Search by last name - returns matching users
- [ ] Clear search - shows all users again
- [ ] Search with no results - shows "No users found"

#### 2.4 Filters
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

#### 2.5 Create New User
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

#### 2.6 Edit User
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

#### 2.7 Activate/Deactivate User
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

#### 2.8 Delete User
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

#### 2.9 Bulk Operations (NEW - Dec 2024)
- [ ] Select multiple users using checkboxes:
  - [ ] Individual checkboxes work for each user
  - [ ] "Select All" checkbox selects/deselects all users
  - [ ] Selected count displays correctly
- [ ] Bulk action bar appears when users are selected:
  - [ ] Shows number of selected users
  - [ ] Shows "Activate" button
  - [ ] Shows "Deactivate" button
  - [ ] Shows "Assign Role" dropdown
  - [ ] Shows "Delete" button
  - [ ] Shows "Clear Selection" button
- [ ] Bulk Activate:
  - [ ] Select multiple inactive users
  - [ ] Click "Activate" button
  - [ ] All selected users become active
  - [ ] Success message appears
  - [ ] Selection clears automatically
- [ ] Bulk Deactivate:
  - [ ] Select multiple active users (not yourself)
  - [ ] Click "Deactivate" button
  - [ ] All selected users become inactive
  - [ ] Success message appears
  - [ ] Selection clears automatically
  - [ ] Try to deactivate yourself - shows error
- [ ] Bulk Delete:
  - [ ] Select multiple users (not yourself)
  - [ ] Click "Delete" button
  - [ ] Confirmation dialog appears
  - [ ] Confirm deletion
  - [ ] All selected users are deleted
  - [ ] Success message appears
  - [ ] Selection clears automatically
  - [ ] Try to delete yourself - shows error
- [ ] Bulk Assign Role:
  - [ ] Select multiple users
  - [ ] Click "Assign Role" dropdown
  - [ ] Select a role (admin, manager, developer, viewer)
  - [ ] All selected users get the new role
  - [ ] Success message appears
  - [ ] Selection clears automatically
  - [ ] Role badges update in the list

#### 2.10 User Import/Export (NEW - Dec 2024)
- [ ] Navigate to "Import/Export" tab in Users page
- [ ] Export Users:
  - [ ] Click "Export Users" button
  - [ ] CSV file downloads automatically
  - [ ] File name includes date: `users_export_YYYY-MM-DD.csv`
  - [ ] CSV contains all user fields:
    - [ ] Email
    - [ ] Username
    - [ ] First Name
    - [ ] Last Name
    - [ ] Role
    - [ ] Is Active
    - [ ] 2FA Enabled
    - [ ] Date Joined
    - [ ] Last Login
  - [ ] Export respects current filters (role, status, search)
- [ ] Import Users:
  - [ ] Click "Choose File" button
  - [ ] Select a valid CSV file
  - [ ] File name and size display
  - [ ] Click "Import Users" button
  - [ ] Import processes successfully
  - [ ] Success message shows created/updated counts
  - [ ] New users appear in list
  - [ ] Existing users are updated
  - [ ] Error handling:
    - [ ] Upload non-CSV file - shows error
    - [ ] Upload CSV with invalid format - shows error
    - [ ] Upload CSV with missing required fields - shows error
    - [ ] Upload CSV with invalid role - shows error
    - [ ] Error messages are clear and helpful

#### 2.11 User Activity Log (NEW - Dec 2024)
- [ ] Navigate to "Activity Log" tab in Users page
- [ ] User Selection:
  - [ ] Input field for user ID or email
  - [ ] Enter valid user ID
  - [ ] Activity log loads for that user
- [ ] Activity Display:
  - [ ] Activities list displays:
    - [ ] Action badge (create, update, delete, execute, login, logout)
    - [ ] Resource type badge
    - [ ] Description/details
    - [ ] Changes (if applicable)
    - [ ] IP address
    - [ ] Timestamp (relative time, e.g., "2 hours ago")
  - [ ] Activities are sorted by most recent first
  - [ ] Total count badge shows correct number
- [ ] Search Functionality:
  - [ ] Search by action - filters activities
  - [ ] Search by resource type - filters activities
  - [ ] Search by description - filters activities
  - [ ] Clear search - shows all activities
- [ ] Empty States:
  - [ ] No user selected - shows "Select a user to view their activity log"
  - [ ] User with no activities - shows "No activities found"
  - [ ] Search with no results - shows "No activities match your search"
- [ ] Access Control:
  - [ ] Admin can view any user's activity
  - [ ] Regular users can only view their own activity
  - [ ] Non-admin trying to view another user's activity - shows error

#### 2.12 Role Management Tab (NEW - Dec 2024)
- [ ] Navigate to "Roles" tab in Users page
- [ ] Create New Role:
  - [ ] Enter role name
  - [ ] Enter role description
  - [ ] Click "Create Role" button
  - [ ] New role appears in roles table
- [ ] Edit Role:
  - [ ] Click "Edit" button on a role
  - [ ] Modify name or description
  - [ ] Click "Save" button
  - [ ] Changes are saved
- [ ] Delete Role:
  - [ ] Click "Delete" button on a custom role
  - [ ] Confirmation dialog appears
  - [ ] Confirm deletion
  - [ ] Role is deleted
  - [ ] System roles (admin, manager, developer, viewer) cannot be deleted
- [ ] Role Display:
  - [ ] Roles table shows:
    - [ ] Role name (with "System" badge for predefined roles)
    - [ ] Description
    - [ ] User count
    - [ ] Actions (Edit/Delete buttons)
  - [ ] System roles are protected from deletion

#### 2.13 Permissions Matrix Tab (NEW - Dec 2024)
- [ ] Navigate to "Permissions Matrix" tab in Users page
- [ ] Permissions Grid:
  - [ ] Grid displays roles as rows
  - [ ] Grid displays permissions as columns
  - [ ] Resources grouped: users, agents, workflows, commands, projects, integrations, settings, analytics
  - [ ] Permissions per resource: view, create, edit, delete
- [ ] Permission Editing:
  - [ ] Click checkbox to grant permission
  - [ ] Uncheck to revoke permission
  - [ ] Changes are tracked (pending state)
  - [ ] Click "Save" button for a role
  - [ ] Permissions are saved
  - [ ] Success message appears
- [ ] Reset Functionality:
  - [ ] Make changes to permissions
  - [ ] Click "Reset" button
  - [ ] Permissions revert to original state
- [ ] Admin Role Protection:
  - [ ] Admin role permissions are locked (cannot be changed)
  - [ ] Lock icon/badge indicates protected role
  - [ ] Checkboxes for admin role are disabled

---

## 🔌 Platform Configuration UI

### 3. Platform List Page

#### 3.1 Navigation & Access
- [ ] Navigate to `/admin/platforms` - page loads without errors
- [ ] Admin sidebar shows "Platforms" link
- [ ] Clicking "Platforms" navigates to platform management page
- [ ] Page title shows "Platform Configuration"
- [ ] Page description shows "Manage AI platform integrations and API keys"

#### 3.2 Platform List Display
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

#### 3.3 Search & Filters
- [ ] Search by display name - filters platforms
- [ ] Search by platform name - filters platforms
- [ ] Search by model name - filters platforms
- [ ] Status filter works (All/Active/Inactive/Maintenance)
- [ ] Health filter works (All/Healthy/Unhealthy)
- [ ] Combined filters work correctly

#### 3.4 Create New Platform
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

#### 3.5 Edit Platform
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

#### 3.6 Delete Platform
- [ ] Click "Delete" button on a platform
- [ ] Confirmation dialog appears with warning
- [ ] Click "Cancel" - dialog closes, platform not deleted
- [ ] Click "Delete Platform":
  - [ ] Platform is deleted
  - [ ] Platform disappears from list

#### 3.7 Health Status
- [ ] Healthy platforms show green badge
- [ ] Unhealthy platforms show red badge
- [ ] Health status updates when platform health changes

---

## 🤖 Agent Management UI

### 4. Agent List Page

#### 4.1 Navigation & Access
- [ ] Navigate to `/admin/agents` - page loads without errors
- [ ] Admin sidebar shows "Agents" link
- [ ] Clicking "Agents" navigates to agent management page
- [ ] Page title shows "Agent Management"
- [ ] Page description shows "Manage AI agents, capabilities, and configurations"

#### 4.2 Agent List Display
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

#### 4.3 Search & Filters
- [ ] Search by agent name - filters agents
- [ ] Search by agent ID - filters agents
- [ ] Search by description - filters agents
- [ ] Status filter works (All/Active/Inactive/Maintenance)
- [ ] Platform filter works (All/OpenAI/Anthropic/Google)
- [ ] Combined filters work correctly

#### 4.4 Create New Agent
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

#### 4.5 Edit Agent
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

#### 4.6 Delete Agent
- [ ] Click "Delete" button on an agent
- [ ] Confirmation dialog appears with warning
- [ ] Click "Cancel" - dialog closes, agent not deleted
- [ ] Click "Delete Agent":
  - [ ] Agent is deleted
  - [ ] Agent disappears from list

#### 4.7 Metrics Display
- [ ] Agents with invocations show metrics:
  - [ ] Total invocations count
  - [ ] Success rate percentage (color-coded)
  - [ ] Average response time in seconds
- [ ] Agents without invocations don't show metrics

---

## ⚙️ System Settings UI

### 5. System Settings Page

#### 5.1 Navigation & Access
- [ ] Navigate to `/admin/settings` - page loads without errors
- [ ] Admin sidebar shows "System Settings" link
- [ ] Clicking "System Settings" navigates to settings page
- [ ] Page shows two tabs: "System Settings" and "Feature Flags"

#### 5.2 System Settings Tab
- [ ] System Settings tab is visible and active by default
- [ ] Settings list displays correctly (if any exist)
- [ ] Each setting card shows:
  - [ ] Setting key (bold)
  - [ ] Category badge (colored)
  - [ ] Value type badge
  - [ ] "Public" badge (if is_public is true)
  - [ ] Description (if available)
  - [ ] Formatted value (truncated if long)
- [ ] Search works (key, description)
- [ ] Category filter works (General, Security, Performance, Notifications, Integrations)
- [ ] Click "New Setting" - create form appears
- [ ] Click "Edit" - edit form appears
- [ ] Click "Delete" - confirmation dialog appears

#### 5.3 Create System Setting
- [ ] Form displays all fields:
  - [ ] Key input
  - [ ] Category dropdown
  - [ ] Value Type dropdown (String, Integer, Float, Boolean, JSON)
  - [ ] Value input (dynamic based on type)
  - [ ] Description textarea
  - [ ] Public checkbox
- [ ] Value input changes based on type:
  - [ ] String: Text input
  - [ ] Integer: Number input (step=1)
  - [ ] Float: Number input (step=0.01)
  - [ ] Boolean: Select dropdown (True/False)
  - [ ] JSON: Textarea (with placeholder)
- [ ] Validation works for each type
- [ ] Submit - setting created successfully

#### 5.4 Edit System Setting
- [ ] Form pre-populated with current values
- [ ] Key is read-only
- [ ] Change value type - value input updates
- [ ] Update value - saves successfully
- [ ] Update category - saves successfully

#### 5.5 Feature Flags Tab
- [ ] Click "Feature Flags" tab
- [ ] Feature Flags tab is active
- [ ] Flags list displays correctly
- [ ] Each flag card shows:
  - [ ] Flag name (bold)
  - [ ] Flag key badge
  - [ ] Enabled/Disabled badge
  - [ ] Description (if available)
  - [ ] Role restrictions (if any)
- [ ] Quick toggle button works
- [ ] Search works (key, name, description)
- [ ] Status filter works (All/Enabled/Disabled)

#### 5.6 Create Feature Flag
- [ ] Click "New Feature Flag" - form appears
- [ ] Form displays all fields:
  - [ ] Key input
  - [ ] Name input
  - [ ] Description textarea
  - [ ] Enabled checkbox
  - [ ] Role checkboxes (admin, manager, developer, viewer)
  - [ ] User IDs input
- [ ] Submit - flag created successfully

#### 5.7 Edit Feature Flag
- [ ] Form pre-populated with current values
- [ ] Key is read-only
- [ ] Update enabled status - saves successfully
- [ ] Update role restrictions - saves successfully
- [ ] Update user IDs - saves successfully

---

## 📊 Usage Analytics UI

### 6. Analytics Dashboard

#### 6.1 Navigation & Access
- [ ] Navigate to `/admin/analytics` - page loads without errors
- [ ] Admin sidebar shows "Analytics" link
- [ ] Clicking "Analytics" navigates to analytics page
- [ ] Page title shows "Usage Analytics"

#### 6.2 Analytics Tabs
- [ ] Page shows tabs:
  - [ ] Overview
  - [ ] Cost Tracking
  - [ ] Token Usage
  - [ ] Top Users (admin only)
- [ ] Tabs switch correctly
- [ ] Active tab is highlighted

#### 6.3 Usage Overview Tab
- [ ] Overview tab displays:
  - [ ] Summary cards (Total Cost, Total Tokens, Total Requests, Avg Response Time)
  - [ ] Platform breakdown chart
  - [ ] Model breakdown chart
  - [ ] Cost by platform pie chart
  - [ ] Top models bar chart
  - [ ] Platform details table
- [ ] All charts render correctly
- [ ] Data is accurate
- [ ] Period filter works (Today, Week, Month, Year, All)
- [ ] Platform filter works (if implemented)

#### 6.4 Cost Tracking Tab
- [ ] Cost Tracking tab displays:
  - [ ] Total Cost card
  - [ ] Average Daily Cost card
  - [ ] Data Points card
  - [ ] Cost Over Time area chart
  - [ ] Cost & Requests comparison line chart
- [ ] Charts are interactive
- [ ] Tooltips work on hover
- [ ] Period filter works
- [ ] Charts update when filter changes

#### 6.5 Token Usage Tab
- [ ] Token Usage tab displays:
  - [ ] Total Tokens card
  - [ ] Platforms card
  - [ ] Tokens by Platform bar chart
  - [ ] Token Distribution pie chart
  - [ ] Daily Token Usage line chart
  - [ ] Top Models by Token Usage bar chart
- [ ] All charts render correctly
- [ ] Data is accurate
- [ ] Period filter works

#### 6.6 Top Users Tab (Admin Only)
- [ ] Top Users tab displays:
  - [ ] User list with metrics
  - [ ] Each user shows:
    - [ ] Name and email
    - [ ] Total cost
    - [ ] Total tokens
    - [ ] Total requests
    - [ ] Avg cost per request
- [ ] Users are sorted by cost (highest first)
- [ ] Period filter works
- [ ] Non-admin users cannot access this tab

---

## 🔒 Security Testing

### 7. Access Control

#### 7.1 Admin-Only Access
- [ ] Non-admin users cannot access `/admin/users`
- [ ] Non-admin users cannot access `/admin/platforms`
- [ ] Non-admin users cannot access `/admin/agents`
- [ ] Non-admin users cannot access `/admin/settings`
- [ ] Non-admin users cannot access `/admin/analytics`
- [ ] Non-admin users are redirected to home page
- [ ] Admin users can access all admin pages

#### 7.2 API Key Security
- [ ] API keys are never displayed in the UI
- [ ] Only `has_api_key` boolean is shown
- [ ] API keys are encrypted in the database
- [ ] API keys can only be updated, never retrieved

#### 7.3 Data Validation
- [ ] Email validation works (rejects invalid emails)
- [ ] Password validation works (min 8 characters)
- [ ] Role validation works (only valid roles accepted)
- [ ] Numeric fields reject non-numeric input
- [ ] Required fields cannot be empty

#### 7.4 Self-Protection
- [ ] Users cannot deactivate themselves
- [ ] Users cannot delete themselves
- [ ] Admin cannot lock themselves out

---

## 🎨 UI/UX General Testing

### 8. Responsive Design
- [ ] Test on desktop (1920x1080) - all layouts work
- [ ] Test on tablet (768px width) - layouts adapt
- [ ] Test on mobile (375px width) - layouts adapt
- [ ] Filters stack vertically on mobile
- [ ] Forms are scrollable on mobile
- [ ] Cards stack properly on small screens

### 9. Loading States
- [ ] Loading skeletons appear during data fetch
- [ ] Loading states don't cause layout shift
- [ ] "Saving..." button states work correctly
- [ ] "Deleting..." button states work correctly

### 10. Error Handling
- [ ] Network errors show user-friendly messages
- [ ] Validation errors appear inline below fields
- [ ] Server errors show appropriate messages
- [ ] Error messages are clear and actionable

### 11. Accessibility
- [ ] All buttons have accessible labels
- [ ] Form fields have proper labels
- [ ] Error messages are associated with fields
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Focus indicators are visible
- [ ] Color contrast meets WCAG standards

### 12. Performance
- [ ] Page loads within 2 seconds
- [ ] List filtering is responsive (< 500ms)
- [ ] Form submission is responsive
- [ ] No console errors
- [ ] No console warnings

---

## 🔄 Integration Testing

### 13. Backend Integration

#### 13.1 API Endpoints
- [ ] All user management endpoints work:
  - [ ] `GET /api/v1/auth/users/` - List users
  - [ ] `POST /api/v1/auth/users/` - Create user
  - [ ] `GET /api/v1/auth/users/{id}/` - Get user
  - [ ] `PATCH /api/v1/auth/users/{id}/` - Update user
  - [ ] `DELETE /api/v1/auth/users/{id}/` - Delete user
  - [ ] `POST /api/v1/auth/users/{id}/activate/` - Activate user
  - [ ] `POST /api/v1/auth/users/{id}/deactivate/` - Deactivate user
  - [ ] `POST /api/v1/auth/users/bulk_activate/` - Bulk activate (NEW)
  - [ ] `POST /api/v1/auth/users/bulk_deactivate/` - Bulk deactivate (NEW)
  - [ ] `POST /api/v1/auth/users/bulk_delete/` - Bulk delete (NEW)
  - [ ] `POST /api/v1/auth/users/bulk_assign_role/` - Bulk assign role (NEW)
  - [ ] `GET /api/v1/auth/users/export/` - Export users to CSV (NEW)
  - [ ] `POST /api/v1/auth/users/import_users/` - Import users from CSV (NEW)
  - [ ] `GET /api/v1/auth/users/{id}/activity/` - Get user activity log (NEW)
- [ ] All platform management endpoints work
- [ ] All agent management endpoints work
- [ ] All system settings endpoints work
- [ ] All analytics endpoints work
- [ ] Data persists correctly
- [ ] Data validation works on backend
- [ ] All new bulk operation endpoints require admin role
- [ ] All new import/export endpoints require admin role
- [ ] Activity log endpoint respects access control (admin or own user)

#### 13.2 Real-time Updates
- [ ] Analytics data updates (if WebSocket implemented)
- [ ] Platform health updates (if WebSocket implemented)
- [ ] Agent metrics update (if WebSocket implemented)

---

## 🐛 Edge Cases & Error Scenarios

### 14. Edge Cases

#### 14.1 Empty States
- [ ] Empty user list displays correctly
- [ ] Empty platform list displays correctly
- [ ] Empty agent list displays correctly
- [ ] Empty settings list displays correctly
- [ ] Empty search results display correctly

#### 14.2 Long Values
- [ ] Long names are truncated or wrapped
- [ ] Long descriptions are truncated in list
- [ ] Long system prompts are scrollable in form

#### 14.3 Special Characters
- [ ] Special characters in names work
- [ ] Special characters in descriptions work
- [ ] Special characters in system prompts work

#### 14.4 Concurrent Operations
- [ ] Create user while another user creates - both succeed
- [ ] Edit user while another user edits - last write wins
- [ ] Delete user while another user views - handled gracefully

#### 14.5 Network Issues
- [ ] Slow network - loading states appear
- [ ] Network timeout - error message appears
- [ ] Network disconnection - error message appears
- [ ] Network reconnection - data refreshes

---

## ✅ Final Verification

### 15. Complete Workflows

#### 15.1 User Management Workflow
- [ ] Create new user
- [ ] Edit user role
- [ ] Activate/deactivate user
- [ ] Delete user
- [ ] Search and filter users
- [ ] **Bulk operations (activate, deactivate, delete, assign role)** (NEW)
- [ ] **Import users from CSV** (NEW)
- [ ] **Export users to CSV** (NEW)
- [ ] **View user activity log** (NEW)
- [ ] **Create and manage custom roles** (NEW)
- [ ] **Edit permissions via matrix** (NEW)
- [ ] All operations work correctly

#### 15.2 Platform Management Workflow
- [ ] Create new platform
- [ ] Configure API key (encrypted)
- [ ] Test platform health
- [ ] Edit platform settings
- [ ] Delete platform
- [ ] All operations work correctly

#### 15.3 Agent Management Workflow
- [ ] Create new agent
- [ ] Configure capabilities
- [ ] Set system prompt
- [ ] Configure model settings
- [ ] View agent metrics
- [ ] Edit agent
- [ ] Delete agent
- [ ] All operations work correctly

#### 15.4 System Settings Workflow
- [ ] Create system setting
- [ ] Edit system setting
- [ ] Delete system setting
- [ ] Create feature flag
- [ ] Toggle feature flag
- [ ] Edit feature flag
- [ ] All operations work correctly

#### 15.5 Analytics Workflow
- [ ] View usage overview
- [ ] View cost tracking
- [ ] View token usage
- [ ] View top users (admin)
- [ ] Filter by period
- [ ] Filter by platform
- [ ] All charts render correctly
- [ ] Data is accurate

---

## 📝 Notes & Issues

**Date:** _______________  
**Tester:** _______________  
**Environment:** _______________

### Issues Found:
1. 
2. 
3. 

### Suggestions:
1. 
2. 
3. 

---

## ✅ Sign-Off

- [ ] All User Management tests passed
- [ ] All Platform Configuration tests passed
- [ ] All Agent Management tests passed
- [ ] All System Settings tests passed
- [ ] All Usage Analytics tests passed
- [ ] All UI/UX tests passed
- [ ] All Security tests passed
- [ ] All Browser Compatibility tests passed
- [ ] All Integration tests passed
- [ ] Complete workflows tested

**Overall Status:** ☐ Pass ☐ Fail  
**Tester Signature:** _______________  
**Date:** _______________

