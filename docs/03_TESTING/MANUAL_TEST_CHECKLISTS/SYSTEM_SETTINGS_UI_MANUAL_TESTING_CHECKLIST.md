---
title: "System Settings UI - Manual Testing Checklist"
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
  - checklist
  - testing
  - core
  - test

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

# System Settings UI - Manual Testing Checklist

**Date:** December 2024  
**Component:** System Settings & Feature Flags Management  
**Phase:** Phase 17-18 (Admin & Configuration UI)

---

## 📋 Pre-Testing Setup

- [ ] Backend server is running (`python manage.py runserver`)
- [ ] Frontend server is running (`npm run dev`)
- [ ] Logged in as admin user (`role: 'admin'`)
- [ ] Database migrations applied (`python manage.py migrate core`)
- [ ] Browser console is open (F12) to check for errors

---

## 🔧 System Settings Testing

### 1. System Settings List View

#### 1.1 Display and Loading
- [ ] Navigate to `/admin/settings`
- [ ] System Settings tab is visible and active by default
- [ ] Settings list displays correctly (if any exist)
- [ ] Loading skeleton appears while fetching data
- [ ] Empty state displays "No settings found" when no settings exist

#### 1.2 Search Functionality
- [ ] Type in search box - filters settings in real-time
- [ ] Search is debounced (waits 500ms before searching)
- [ ] Search works for setting key
- [ ] Search works for setting description
- [ ] Clear search - shows all settings again
- [ ] Search term persists in localStorage when navigating away and back

#### 1.3 Category Filter
- [ ] Category filter dropdown is visible
- [ ] All categories are listed: All, General, Security, Performance, Notifications, Integrations
- [ ] Select "General" - only general settings shown
- [ ] Select "Security" - only security settings shown
- [ ] Select "All Categories" - all settings shown
- [ ] Category filter persists in localStorage when navigating away and back

#### 1.4 Setting Display
- [ ] Each setting card shows:
  - [ ] Setting key (bold)
  - [ ] Category badge (colored)
  - [ ] Value type badge
  - [ ] "Public" badge (if is_public is true)
  - [ ] Description (if available)
  - [ ] Formatted value (truncated if long)
- [ ] Setting icons are visible (Settings icon)
- [ ] Edit button is visible and clickable
- [ ] Delete button is visible and clickable

#### 1.5 Actions
- [ ] Click "New Setting" button - opens create form
- [ ] Click "Edit" button on a setting - opens edit form
- [ ] Click "Delete" button on a setting - shows confirmation dialog

---

### 2. Create System Setting

#### 2.1 Form Display
- [ ] Create form opens when clicking "New Setting"
- [ ] Form title shows "Create New System Setting"
- [ ] All fields are visible:
  - [ ] Key input
  - [ ] Category dropdown
  - [ ] Value Type dropdown
  - [ ] Value input (dynamic based on type)
  - [ ] Description textarea
  - [ ] Public checkbox
- [ ] Cancel button is visible
- [ ] Create button is visible

#### 2.2 Key Field
- [ ] Key field is required
- [ ] Key field accepts alphanumeric and dots/underscores
- [ ] Key field shows error if empty on submit
- [ ] Key field is editable (not disabled)

#### 2.3 Category Field
- [ ] Category dropdown shows all options:
  - [ ] General
  - [ ] Security
  - [ ] Performance
  - [ ] Notifications
  - [ ] Integrations
- [ ] Default category is "General"
- [ ] Category can be changed

#### 2.4 Value Type Field
- [ ] Value Type dropdown shows all options:
  - [ ] String
  - [ ] Integer
  - [ ] Float
  - [ ] Boolean
  - [ ] JSON
- [ ] Default value type is "String"
- [ ] Value input changes based on selected type:
  - [ ] String: Text input
  - [ ] Integer: Number input (step=1)
  - [ ] Float: Number input (step=0.01)
  - [ ] Boolean: Select dropdown (True/False)
  - [ ] JSON: Textarea (with placeholder)

#### 2.5 Value Field Validation
- [ ] String: Accepts any text
- [ ] Integer: Only accepts whole numbers
- [ ] Integer: Shows error for non-numeric input
- [ ] Float: Accepts decimal numbers
- [ ] Float: Shows error for invalid numbers
- [ ] Boolean: Only accepts True/False
- [ ] JSON: Validates JSON syntax
- [ ] JSON: Shows error for invalid JSON
- [ ] JSON: Pretty-formats valid JSON in textarea

#### 2.6 Public Checkbox
- [ ] Public checkbox is unchecked by default
- [ ] Public checkbox can be toggled
- [ ] Public checkbox label is clear

#### 2.7 Form Submission
- [ ] Submit with all required fields - creates setting successfully
- [ ] Submit with missing key - shows error
- [ ] Submit with invalid value (wrong type) - shows error
- [ ] Submit with invalid JSON - shows error
- [ ] After successful creation:
  - [ ] Form closes
  - [ ] Settings list refreshes
  - [ ] New setting appears in list
- [ ] Click Cancel - form closes without saving

#### 2.8 Error Handling
- [ ] Submit with duplicate key - shows error message
- [ ] Network error - shows error message in UI
- [ ] Server error (500) - shows error message in UI
- [ ] Validation errors display inline below fields

---

### 3. Edit System Setting

#### 3.1 Form Display
- [ ] Edit form opens when clicking "Edit" on a setting
- [ ] Form title shows "Edit System Setting"
- [ ] All fields are pre-populated with current values:
  - [ ] Key (disabled/read-only)
  - [ ] Category
  - [ ] Value Type
  - [ ] Value (correctly typed)
  - [ ] Description
  - [ ] Public checkbox

#### 3.2 Value Type Change
- [ ] Change value type - value input updates accordingly
- [ ] Change from String to Integer - converts value if possible
- [ ] Change from Integer to Float - converts value
- [ ] Change to Boolean - shows True/False dropdown
- [ ] Change to JSON - shows textarea with formatted JSON

#### 3.3 Form Submission
- [ ] Update value - saves successfully
- [ ] Update category - saves successfully
- [ ] Update description - saves successfully
- [ ] Toggle public checkbox - saves successfully
- [ ] After successful update:
  - [ ] Form closes
  - [ ] Settings list refreshes
  - [ ] Updated setting shows new values

#### 3.4 Error Handling
- [ ] Submit with invalid value - shows error
- [ ] Network error - shows error message
- [ ] Server error - shows error message

---

### 4. Delete System Setting

#### 4.1 Confirmation Dialog
- [ ] Click "Delete" on a setting - shows confirmation dialog
- [ ] Dialog title shows "Delete Setting"
- [ ] Dialog message is clear and informative
- [ ] Cancel button is visible and clickable
- [ ] Delete button is visible and clickable

#### 4.2 Delete Action
- [ ] Click Cancel - dialog closes, setting not deleted
- [ ] Click Delete - setting is deleted
- [ ] After deletion:
  - [ ] Dialog closes
  - [ ] Settings list refreshes
  - [ ] Deleted setting no longer appears

#### 4.3 Error Handling
- [ ] Network error during delete - shows error message
- [ ] Server error during delete - shows error message

---

## 🚩 Feature Flags Testing

### 5. Feature Flags List View

#### 5.1 Display and Loading
- [ ] Click "Feature Flags" tab
- [ ] Feature Flags tab is active
- [ ] Flags list displays correctly (if any exist)
- [ ] Loading skeleton appears while fetching data
- [ ] Empty state displays "No feature flags found" when no flags exist

#### 5.2 Search Functionality
- [ ] Type in search box - filters flags in real-time
- [ ] Search is debounced (waits 500ms before searching)
- [ ] Search works for flag key
- [ ] Search works for flag name
- [ ] Search works for flag description
- [ ] Clear search - shows all flags again
- [ ] Search term persists in localStorage when navigating away and back

#### 5.3 Status Filter
- [ ] Status filter dropdown is visible
- [ ] All statuses are listed: All Status, Enabled, Disabled
- [ ] Select "Enabled" - only enabled flags shown
- [ ] Select "Disabled" - only disabled flags shown
- [ ] Select "All Status" - all flags shown
- [ ] Status filter persists in localStorage when navigating away and back

#### 5.4 Flag Display
- [ ] Each flag card shows:
  - [ ] Flag name (bold)
  - [ ] Flag key badge
  - [ ] Enabled/Disabled badge (colored)
  - [ ] Description (if available)
  - [ ] Role restrictions (if any)
  - [ ] User count (if any)
- [ ] Flag icons are visible (Flag icon)
- [ ] Toggle button is visible and clickable
- [ ] Edit button is visible and clickable
- [ ] Delete button is visible and clickable

#### 5.5 Quick Toggle
- [ ] Click toggle button on enabled flag - flag becomes disabled
- [ ] Click toggle button on disabled flag - flag becomes enabled
- [ ] Toggle updates immediately (optimistic update)
- [ ] Toggle persists after page refresh
- [ ] Toggle shows loading state while processing

#### 5.6 Actions
- [ ] Click "New Feature Flag" button - opens create form
- [ ] Click "Edit" button on a flag - opens edit form
- [ ] Click "Delete" button on a flag - shows confirmation dialog

---

### 6. Create Feature Flag

#### 6.1 Form Display
- [ ] Create form opens when clicking "New Feature Flag"
- [ ] Form title shows "Create New Feature Flag"
- [ ] All fields are visible:
  - [ ] Key input
  - [ ] Name input
  - [ ] Description textarea
  - [ ] Enabled checkbox
  - [ ] Role checkboxes (admin, manager, developer, viewer)
  - [ ] User IDs input
- [ ] Cancel button is visible
- [ ] Create button is visible

#### 6.2 Key Field
- [ ] Key field is required
- [ ] Key field accepts alphanumeric and dots/underscores
- [ ] Key field shows error if empty on submit
- [ ] Key field is editable (not disabled)

#### 6.3 Name Field
- [ ] Name field is required
- [ ] Name field accepts any text
- [ ] Name field shows error if empty on submit

#### 6.4 Enabled Checkbox
- [ ] Enabled checkbox is unchecked by default
- [ ] Enabled checkbox can be toggled
- [ ] Enabled checkbox label is clear

#### 6.5 Role Selection
- [ ] All roles are listed: admin, manager, developer, viewer
- [ ] Roles can be selected/deselected
- [ ] Selected roles show as badges
- [ ] Empty role selection means "all roles"

#### 6.6 User IDs Field
- [ ] User IDs input accepts comma-separated values
- [ ] User IDs input is optional
- [ ] Help text explains the field
- [ ] Empty user IDs means "all users" (if no role restrictions)

#### 6.7 Form Submission
- [ ] Submit with all required fields - creates flag successfully
- [ ] Submit with missing key - shows error
- [ ] Submit with missing name - shows error
- [ ] After successful creation:
  - [ ] Form closes
  - [ ] Flags list refreshes
  - [ ] New flag appears in list

#### 6.8 Error Handling
- [ ] Submit with duplicate key - shows error message
- [ ] Network error - shows error message in UI
- [ ] Server error - shows error message in UI
- [ ] Validation errors display inline below fields

---

### 7. Edit Feature Flag

#### 7.1 Form Display
- [ ] Edit form opens when clicking "Edit" on a flag
- [ ] Form title shows "Edit Feature Flag"
- [ ] All fields are pre-populated with current values:
  - [ ] Key (disabled/read-only)
  - [ ] Name
  - [ ] Description
  - [ ] Enabled checkbox
  - [ ] Selected roles (checked)
  - [ ] User IDs (comma-separated)

#### 7.2 Form Submission
- [ ] Update name - saves successfully
- [ ] Update description - saves successfully
- [ ] Toggle enabled checkbox - saves successfully
- [ ] Change role selection - saves successfully
- [ ] Update user IDs - saves successfully
- [ ] After successful update:
  - [ ] Form closes
  - [ ] Flags list refreshes
  - [ ] Updated flag shows new values

#### 7.3 Error Handling
- [ ] Submit with invalid data - shows error
- [ ] Network error - shows error message
- [ ] Server error - shows error message

---

### 8. Delete Feature Flag

#### 8.1 Confirmation Dialog
- [ ] Click "Delete" on a flag - shows confirmation dialog
- [ ] Dialog title shows "Delete Feature Flag"
- [ ] Dialog message is clear and informative
- [ ] Cancel button is visible and clickable
- [ ] Delete button is visible and clickable

#### 8.2 Delete Action
- [ ] Click Cancel - dialog closes, flag not deleted
- [ ] Click Delete - flag is deleted
- [ ] After deletion:
  - [ ] Dialog closes
  - [ ] Flags list refreshes
  - [ ] Deleted flag no longer appears

#### 8.3 Error Handling
- [ ] Network error during delete - shows error message
- [ ] Server error during delete - shows error message

---

## 🔐 Security & Permissions Testing

### 9. Access Control

#### 9.1 Admin Access
- [ ] Admin user can access `/admin/settings`
- [ ] Admin user can view all settings (public and private)
- [ ] Admin user can create settings
- [ ] Admin user can edit settings
- [ ] Admin user can delete settings
- [ ] Admin user can view all feature flags
- [ ] Admin user can create feature flags
- [ ] Admin user can edit feature flags
- [ ] Admin user can delete feature flags
- [ ] Admin user can toggle feature flags

#### 9.2 Non-Admin Access
- [ ] Non-admin user cannot access `/admin/settings` (redirected)
- [ ] Non-admin user cannot create settings via API
- [ ] Non-admin user cannot edit settings via API
- [ ] Non-admin user cannot delete settings via API
- [ ] Non-admin user can view public settings via API
- [ ] Non-admin user cannot view private settings via API
- [ ] Non-admin user can view feature flags via API
- [ ] Non-admin user cannot create/edit/delete feature flags via API

#### 9.3 Public Settings
- [ ] Public settings are visible to all authenticated users
- [ ] Private settings are only visible to admins
- [ ] Public checkbox works correctly

---

## 🎨 UI/UX Testing

### 10. General UI/UX

#### 10.1 Layout
- [ ] Page layout is consistent with other admin pages
- [ ] Tabs are clearly visible and functional
- [ ] Sidebar navigation shows "System Settings" link
- [ ] Settings link is highlighted when active

#### 10.2 Responsive Design
- [ ] Page works on desktop (1920x1080)
- [ ] Page works on tablet (768x1024)
- [ ] Page works on mobile (375x667)
- [ ] Forms are responsive
- [ ] Lists are responsive
- [ ] Modals/dialogs are responsive

#### 10.3 Loading States
- [ ] Loading skeletons appear while fetching data
- [ ] Forms show loading state during submission
- [ ] Buttons show loading state during actions
- [ ] Toggle buttons show loading state

#### 10.4 Error States
- [ ] Error messages are visible and clear
- [ ] Error messages are dismissible
- [ ] Form validation errors appear inline
- [ ] Network errors are handled gracefully
- [ ] Server errors are handled gracefully

#### 10.5 Success States
- [ ] Success feedback after create (form closes, list refreshes)
- [ ] Success feedback after update (form closes, list refreshes)
- [ ] Success feedback after delete (dialog closes, list refreshes)
- [ ] Success feedback after toggle (flag updates immediately)

#### 10.6 Accessibility
- [ ] All buttons have proper labels
- [ ] All inputs have proper labels
- [ ] All selects have proper aria-labels
- [ ] Keyboard navigation works
- [ ] Screen reader friendly (if applicable)

---

## 🔄 Integration Testing

### 11. Backend Integration

#### 11.1 API Endpoints
- [ ] GET `/api/v1/core/settings/` - returns settings list
- [ ] GET `/api/v1/core/settings/{id}/` - returns single setting
- [ ] POST `/api/v1/core/settings/` - creates setting
- [ ] PATCH `/api/v1/core/settings/{id}/` - updates setting
- [ ] DELETE `/api/v1/core/settings/{id}/` - deletes setting
- [ ] GET `/api/v1/core/settings/by_category/` - returns grouped settings
- [ ] GET `/api/v1/core/feature-flags/` - returns flags list
- [ ] GET `/api/v1/core/feature-flags/{id}/` - returns single flag
- [ ] POST `/api/v1/core/feature-flags/` - creates flag
- [ ] PATCH `/api/v1/core/feature-flags/{id}/` - updates flag
- [ ] DELETE `/api/v1/core/feature-flags/{id}/` - deletes flag
- [ ] POST `/api/v1/core/feature-flags/{id}/toggle/` - toggles flag

#### 11.2 Data Persistence
- [ ] Created settings persist in database
- [ ] Updated settings persist in database
- [ ] Deleted settings are removed from database
- [ ] Created flags persist in database
- [ ] Updated flags persist in database
- [ ] Deleted flags are removed from database
- [ ] Toggled flags persist in database

#### 11.3 Data Validation
- [ ] Backend validates setting key uniqueness
- [ ] Backend validates setting value type
- [ ] Backend validates flag key uniqueness
- [ ] Backend validates role names
- [ ] Backend validates user IDs format

---

## 🐛 Edge Cases & Error Scenarios

### 12. Edge Cases

#### 12.1 Empty States
- [ ] Empty settings list displays correctly
- [ ] Empty flags list displays correctly
- [ ] Empty search results display correctly
- [ ] Empty filter results display correctly

#### 12.2 Long Values
- [ ] Long setting keys are truncated or wrapped
- [ ] Long setting values are truncated in list
- [ ] Long descriptions are truncated in list
- [ ] Long flag names are truncated or wrapped
- [ ] Long flag descriptions are truncated in list

#### 12.3 Special Characters
- [ ] Setting keys with special characters work
- [ ] Setting values with special characters work
- [ ] JSON values with special characters work
- [ ] Flag keys with special characters work
- [ ] Flag names with special characters work

#### 12.4 Concurrent Operations
- [ ] Create setting while another user creates - both succeed
- [ ] Edit setting while another user edits - last write wins
- [ ] Delete setting while another user views - handled gracefully
- [ ] Toggle flag while another user toggles - handled gracefully

#### 12.5 Network Issues
- [ ] Slow network - loading states appear
- [ ] Network timeout - error message appears
- [ ] Network disconnection - error message appears
- [ ] Network reconnection - data refreshes

---

## ✅ Final Verification

### 13. Complete Workflow

#### 13.1 System Settings Workflow
- [ ] Create a new setting with each value type
- [ ] Edit each setting and verify changes persist
- [ ] Delete a setting and verify it's removed
- [ ] Search for settings and verify results
- [ ] Filter by category and verify results
- [ ] Toggle public visibility and verify behavior

#### 13.2 Feature Flags Workflow
- [ ] Create a new feature flag
- [ ] Toggle flag enabled/disabled
- [ ] Set role restrictions
- [ ] Set user-specific restrictions
- [ ] Edit flag and verify changes persist
- [ ] Delete flag and verify it's removed
- [ ] Search for flags and verify results
- [ ] Filter by status and verify results

#### 13.3 Cross-Tab Testing
- [ ] Create setting in System Settings tab
- [ ] Switch to Feature Flags tab
- [ ] Switch back to System Settings tab
- [ ] Verify created setting is still visible
- [ ] Verify filters persist across tab switches

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

- [ ] All critical tests passed
- [ ] All major features working
- [ ] No blocking issues found
- [ ] Ready for production

**Tester Signature:** _______________  
**Date:** _______________

