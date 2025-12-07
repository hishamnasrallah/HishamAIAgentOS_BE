---
title: "Phase 2: Authentication & Authorization - Manual Testing Checklist"
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
  - testing
  - phase-2
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

# Phase 2: Authentication & Authorization - Manual Testing Checklist

**Date:** December 2024  
**Component:** Authentication & Authorization System  
**Phase:** Phase 2  
**Status:** ✅ Complete (100%)

---

## 📋 Pre-Testing Setup

- [ ] Backend server is running (`python manage.py runserver` or `daphne`)
- [ ] Frontend server is running (`npm run dev`)
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Browser console is open (F12) to check for errors
- [ ] Postman/API client ready for API testing
- [ ] Django admin accessible at `/admin/`

---

## 🔐 Backend Django Admin Testing

### 1. User Model Admin Interface

#### 1.1 Access User Admin
- [ ] Navigate to `/admin/authentication/user/`
- [ ] User list displays all users
- [ ] User list shows: email, username, role, is_active, date_joined
- [ ] Search functionality works (by email, username)
- [ ] Filter by role works (admin, manager, developer, viewer)
- [ ] Filter by is_active works
- [ ] Filter by is_staff works
- [ ] Filter by date_joined works

#### 1.2 Create User via Admin
- [ ] Click "Add User" button
- [ ] Form displays all required fields:
  - [ ] Email (required)
  - [ ] Username (required)
  - [ ] Password (required, with show/hide toggle)
  - [ ] First Name
  - [ ] Last Name
  - [ ] Role dropdown (admin, manager, developer, viewer)
  - [ ] Is Active checkbox
  - [ ] Is Staff checkbox
  - [ ] Is Superuser checkbox
  - [ ] Date Joined (auto-set)
  - [ ] Last Login (auto-set)
  - [ ] Two Factor Secret (encrypted field)
  - [ ] Two Factor Enabled checkbox
  - [ ] Notification Preferences (JSON field)
- [ ] Submit with valid data - user created successfully
- [ ] Submit with duplicate email - shows error
- [ ] Submit with duplicate username - shows error
- [ ] Submit with invalid email format - shows error
- [ ] Password is hashed (not stored in plain text)

#### 1.3 Edit User via Admin
- [ ] Click on existing user to edit
- [ ] All fields are editable (except password - has change password link)
- [ ] Change user role - saves successfully
- [ ] Change user status (is_active) - saves successfully
- [ ] Change password via "Change password" link - works
- [ ] Update notification preferences (JSON) - saves correctly
- [ ] Two Factor Secret field is encrypted (not visible in plain text)

#### 1.4 Delete User via Admin
- [ ] Select user(s) and click "Delete selected users"
- [ ] Confirmation page shows
- [ ] Confirm deletion - user removed from database
- [ ] Related data handled correctly (cascade or protect)

#### 1.5 User Actions
- [ ] Bulk actions work (if implemented)
- [ ] Export users functionality works (if implemented)

---

### 2. API Key Model Admin Interface

#### 2.1 Access API Key Admin
- [ ] Navigate to `/admin/authentication/apikey/`
- [ ] API Key list displays all API keys
- [ ] API Key list shows: key (masked), user, name, created_at, expires_at, is_active
- [ ] Search functionality works (by name, user)
- [ ] Filter by user works
- [ ] Filter by is_active works
- [ ] Filter by expires_at works

#### 2.2 Create API Key via Admin
- [ ] Click "Add API Key" button
- [ ] Form displays all fields:
  - [ ] User (required, dropdown)
  - [ ] Name (required)
  - [ ] Key (auto-generated, displayed once)
  - [ ] Expires At (optional, datetime picker)
  - [ ] Is Active checkbox
  - [ ] Rate Limit Per Minute (number)
  - [ ] Rate Limit Per Day (number)
  - [ ] Created At (auto-set)
- [ ] Submit with valid data - API key created
- [ ] Generated key is displayed (and should be copied immediately)
- [ ] Key is hashed in database (not stored in plain text)

#### 2.3 Edit API Key via Admin
- [ ] Click on existing API key to edit
- [ ] Key field is read-only (cannot be changed)
- [ ] Update name - saves successfully
- [ ] Update expiration date - saves successfully
- [ ] Toggle is_active - saves successfully
- [ ] Update rate limits - saves successfully

#### 2.4 Delete API Key via Admin
- [ ] Select API key(s) and delete
- [ ] Confirmation shows
- [ ] Confirm deletion - API key removed

---

## 🌐 Backend API Testing

### 3. Authentication Endpoints

#### 3.1 User Registration
- [ ] **POST** `/api/v1/auth/register/`
- [ ] Request body:
  ```json
  {
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```
- [ ] Valid request - returns 201 Created with user data and tokens
- [ ] Missing required fields - returns 400 Bad Request
- [ ] Invalid email format - returns 400 with error message
- [ ] Password mismatch - returns 400 with error message
- [ ] Password too short (< 8 chars) - returns 400 with error message
- [ ] Duplicate email - returns 400 with error message
- [ ] Duplicate username - returns 400 with error message
- [ ] Response includes: access token, refresh token, user object

#### 3.2 User Login
- [ ] **POST** `/api/v1/auth/login/`
- [ ] Request body:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- [ ] Valid credentials - returns 200 OK with tokens and user data
- [ ] Invalid email - returns 401 Unauthorized
- [ ] Invalid password - returns 401 Unauthorized
- [ ] Inactive user - returns 401 with appropriate message
- [ ] Response includes: access token, refresh token, user object
- [ ] Access token expires in 15 minutes (or configured time)
- [ ] Refresh token expires in 7 days (or configured time)

#### 3.3 Token Refresh
- [ ] **POST** `/api/v1/auth/token/refresh/`
- [ ] Request body:
  ```json
  {
    "refresh": "refresh_token_here"
  }
  ```
- [ ] Valid refresh token - returns 200 OK with new access token
- [ ] Invalid refresh token - returns 401 Unauthorized
- [ ] Expired refresh token - returns 401 Unauthorized
- [ ] Blacklisted refresh token - returns 401 Unauthorized

#### 3.4 Logout
- [ ] **POST** `/api/v1/auth/logout/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Request body:
  ```json
  {
    "refresh": "refresh_token_here"
  }
  ```
- [ ] Valid request - returns 200 OK
- [ ] Refresh token is blacklisted
- [ ] Access token still valid until expiry (or invalidated if implemented)
- [ ] Subsequent refresh requests fail

#### 3.5 Get User Profile
- [ ] **GET** `/api/v1/auth/profile/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Authenticated user - returns 200 OK with user profile
- [ ] Unauthenticated request - returns 401 Unauthorized
- [ ] Response includes: email, username, first_name, last_name, role, preferences, etc.

#### 3.6 Update User Profile
- [ ] **PUT** `/api/v1/auth/profile/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Request body:
  ```json
  {
    "first_name": "Updated",
    "last_name": "Name",
    "preferred_language": "en",
    "timezone": "UTC"
  }
  ```
- [ ] Valid request - returns 200 OK with updated profile
- [ ] Unauthenticated request - returns 401
- [ ] Invalid data - returns 400 with validation errors

#### 3.7 Change Password
- [ ] **POST** `/api/v1/auth/change-password/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Request body:
  ```json
  {
    "old_password": "oldpass123",
    "new_password": "newpass123",
    "new_password_confirm": "newpass123"
  }
  ```
- [ ] Valid request - returns 200 OK
- [ ] Wrong old password - returns 400 with error
- [ ] Password mismatch - returns 400 with error
- [ ] Password too short - returns 400 with error
- [ ] After change, old password no longer works
- [ ] After change, new password works

#### 3.8 Password Reset Request
- [ ] **POST** `/api/v1/auth/password-reset/`
- [ ] Request body:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- [ ] Valid email - returns 200 OK (email sent)
- [ ] Invalid email - returns 200 OK (security: don't reveal if email exists)
- [ ] Email contains reset link with token

#### 3.9 Password Reset Confirm
- [ ] **POST** `/api/v1/auth/password-reset/confirm/`
- [ ] Request body:
  ```json
  {
    "token": "reset_token_from_email",
    "new_password": "newpass123",
    "new_password_confirm": "newpass123"
  }
  ```
- [ ] Valid token - returns 200 OK, password reset
- [ ] Invalid token - returns 400 with error
- [ ] Expired token - returns 400 with error
- [ ] Password mismatch - returns 400 with error

---

### 4. Two-Factor Authentication (2FA) Endpoints

#### 4.1 Setup 2FA
- [ ] **POST** `/api/v1/auth/2fa/setup/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Valid request - returns 200 OK with:
  - [ ] QR code (base64 encoded PNG)
  - [ ] Secret key (for manual entry)
  - [ ] Backup codes (10 codes, format: XXXX-XXXX)
- [ ] QR code can be scanned by authenticator app
- [ ] Secret key can be manually entered
- [ ] Backup codes are unique and stored

#### 4.2 Enable 2FA
- [ ] **POST** `/api/v1/auth/2fa/enable/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Request body:
  ```json
  {
    "token": "123456"
  }
  ```
- [ ] Valid TOTP token - returns 200 OK, 2FA enabled
- [ ] Invalid token - returns 400 with error
- [ ] Expired token - returns 400 with error
- [ ] After enabling, login requires 2FA

#### 4.3 Disable 2FA
- [ ] **POST** `/api/v1/auth/2fa/disable/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Request body:
  ```json
  {
    "password": "user_password"
  }
  ```
- [ ] Valid password - returns 200 OK, 2FA disabled
- [ ] Invalid password - returns 400 with error
- [ ] After disabling, login no longer requires 2FA

#### 4.4 Verify 2FA During Login
- [ ] **POST** `/api/v1/auth/2fa/verify-login/`
- [ ] Request body:
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "two_factor_token": "123456"
  }
  ```
- [ ] Valid credentials + valid TOTP - returns 200 OK with tokens
- [ ] Valid credentials + invalid TOTP - returns 401 with error
- [ ] Valid credentials + backup code - returns 200 OK with tokens
- [ ] Used backup code is invalidated

#### 4.5 Get Backup Codes
- [ ] **GET** `/api/v1/auth/2fa/backup-codes/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Returns remaining backup codes (if any)
- [ ] Used codes are not returned

---

### 5. User Management Endpoints (Admin Only)

#### 5.1 List Users
- [ ] **GET** `/api/v1/auth/users/`
- [ ] Request headers: `Authorization: Bearer <admin_access_token>`
- [ ] Admin user - returns 200 OK with user list
- [ ] Non-admin user - returns 403 Forbidden
- [ ] Unauthenticated - returns 401 Unauthorized
- [ ] Pagination works (if implemented)
- [ ] Filtering works (role, is_active, etc.)
- [ ] Search works (email, username)

#### 5.2 Create User (Admin)
- [ ] **POST** `/api/v1/auth/users/`
- [ ] Request headers: `Authorization: Bearer <admin_access_token>`
- [ ] Request body:
  ```json
  {
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "developer"
  }
  ```
- [ ] Admin user - returns 201 Created
- [ ] Non-admin user - returns 403 Forbidden
- [ ] Valid data - user created successfully
- [ ] Invalid data - returns 400 with validation errors

#### 5.3 Update User (Admin)
- [ ] **PATCH** `/api/v1/auth/users/{id}/`
- [ ] Request headers: `Authorization: Bearer <admin_access_token>`
- [ ] Admin user - can update any user
- [ ] Non-admin user - returns 403 Forbidden
- [ ] Update role - saves successfully
- [ ] Activate/deactivate user - saves successfully

#### 5.4 Delete User (Admin)
- [ ] **DELETE** `/api/v1/auth/users/{id}/`
- [ ] Request headers: `Authorization: Bearer <admin_access_token>`
- [ ] Admin user - can delete user
- [ ] Non-admin user - returns 403 Forbidden
- [ ] User deleted successfully
- [ ] Related data handled correctly

---

### 6. API Key Management Endpoints

#### 6.1 List API Keys
- [ ] **GET** `/api/v1/auth/api-keys/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Returns user's API keys
- [ ] Keys are masked (only last 4 characters shown)
- [ ] Shows: name, created_at, expires_at, is_active

#### 6.2 Create API Key
- [ ] **POST** `/api/v1/auth/api-keys/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Request body:
  ```json
  {
    "name": "My API Key",
    "expires_at": "2025-12-31T23:59:59Z"
  }
  ```
- [ ] Returns 201 Created with full key (display once)
- [ ] Key is hashed in database
- [ ] Key can be used for authentication

#### 6.3 Delete API Key
- [ ] **DELETE** `/api/v1/auth/api-keys/{id}/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] API key deleted successfully
- [ ] Deleted key no longer works for authentication

---

## 🎨 Frontend Testing

### 7. Login Page

#### 7.1 Login Form
- [ ] Navigate to `/login` or `/auth/login`
- [ ] Form displays: email input, password input, login button
- [ ] "Remember me" checkbox (if implemented)
- [ ] "Forgot password?" link
- [ ] "Don't have an account? Sign up" link

#### 7.2 Login Functionality
- [ ] Enter valid credentials - redirects to dashboard/home
- [ ] Enter invalid email - shows error message
- [ ] Enter invalid password - shows error message
- [ ] Enter inactive user credentials - shows error message
- [ ] Loading state during login
- [ ] Error messages are clear and actionable
- [ ] Success: tokens stored in localStorage/cookies
- [ ] Success: user data stored in state

#### 7.3 2FA Login Flow
- [ ] Login with 2FA-enabled user
- [ ] After password, shows 2FA verification step
- [ ] QR code displayed (if setting up)
- [ ] TOTP input field appears
- [ ] Enter valid TOTP - login completes
- [ ] Enter invalid TOTP - shows error, can retry
- [ ] "Use backup code" option available
- [ ] Enter backup code - login completes
- [ ] Used backup code cannot be reused

---

### 8. Registration Page

#### 8.1 Registration Form
- [ ] Navigate to `/register` or `/auth/register`
- [ ] Form displays all required fields:
  - [ ] Email input
  - [ ] Username input
  - [ ] Password input
  - [ ] Confirm Password input
  - [ ] First Name input
  - [ ] Last Name input
  - [ ] Register button
- [ ] All required fields marked with *

#### 8.2 Registration Functionality
- [ ] Fill all fields correctly - user created, redirects to login
- [ ] Missing required fields - shows validation errors
- [ ] Invalid email format - shows error
- [ ] Password too short - shows error
- [ ] Password mismatch - shows error
- [ ] Duplicate email - shows error
- [ ] Duplicate username - shows error
- [ ] Loading state during registration
- [ ] Success message displayed

---

### 9. Profile Page

#### 9.1 Profile Display
- [ ] Navigate to `/profile` or `/settings/profile`
- [ ] Profile information displayed:
  - [ ] Email (read-only)
  - [ ] Username (read-only or editable)
  - [ ] First Name (editable)
  - [ ] Last Name (editable)
  - [ ] Role (read-only badge)
  - [ ] Avatar/Profile Picture (if implemented)
  - [ ] Preferred Language (dropdown)
  - [ ] Timezone (dropdown)

#### 9.2 Update Profile
- [ ] Change first name - saves successfully
- [ ] Change last name - saves successfully
- [ ] Change preferred language - saves successfully
- [ ] Change timezone - saves successfully
- [ ] Loading state during save
- [ ] Success message after save
- [ ] Error message if save fails

#### 9.3 Change Password
- [ ] "Change Password" section visible
- [ ] Form: old password, new password, confirm password
- [ ] Enter correct old password + new password - password changed
- [ ] Wrong old password - shows error
- [ ] Password mismatch - shows error
- [ ] Password too short - shows error
- [ ] Success message after change
- [ ] After change, can login with new password

---

### 10. 2FA Setup Page

#### 10.1 2FA Setup UI
- [ ] Navigate to `/settings/2fa` or `/profile/2fa`
- [ ] If 2FA not enabled:
  - [ ] "Enable 2FA" button visible
  - [ ] Click button - shows setup flow
  - [ ] QR code displayed
  - [ ] Secret key displayed (for manual entry)
  - [ ] Instructions displayed
  - [ ] TOTP input field for verification
  - [ ] Backup codes displayed (after enabling)
- [ ] If 2FA enabled:
  - [ ] "Disable 2FA" button visible
  - [ ] Status shows "Enabled"
  - [ ] Backup codes section (if any remaining)

#### 10.2 Enable 2FA Flow
- [ ] Click "Enable 2FA"
- [ ] QR code scans correctly in authenticator app
- [ ] Enter TOTP code - 2FA enabled
- [ ] Invalid TOTP code - shows error, can retry
- [ ] Backup codes displayed and can be copied/downloaded
- [ ] After enabling, login requires 2FA

#### 10.3 Disable 2FA Flow
- [ ] Click "Disable 2FA"
- [ ] Password confirmation required
- [ ] Enter correct password - 2FA disabled
- [ ] Wrong password - shows error
- [ ] After disabling, login no longer requires 2FA

---

### 11. Password Reset Flow

#### 11.1 Request Password Reset
- [ ] Navigate to `/forgot-password` or `/auth/reset-password`
- [ ] Form: email input, submit button
- [ ] Enter valid email - shows success message (email sent)
- [ ] Enter invalid email - shows success message (security)
- [ ] Check email for reset link

#### 11.2 Reset Password Page
- [ ] Click reset link from email
- [ ] Navigate to `/reset-password?token=...`
- [ ] Form: new password, confirm password
- [ ] Enter valid passwords - password reset, redirects to login
- [ ] Password mismatch - shows error
- [ ] Password too short - shows error
- [ ] Invalid/expired token - shows error
- [ ] After reset, can login with new password

---

## 🔒 Security Testing

### 12. Access Control

#### 12.1 Role-Based Access
- [ ] Admin can access all endpoints
- [ ] Manager can access manager-level endpoints
- [ ] Developer can access developer-level endpoints
- [ ] Viewer has read-only access
- [ ] Unauthorized access returns 403 Forbidden

#### 12.2 Token Security
- [ ] Access tokens expire after configured time
- [ ] Refresh tokens expire after configured time
- [ ] Expired tokens return 401 Unauthorized
- [ ] Invalid tokens return 401 Unauthorized
- [ ] Tokens cannot be reused after logout

#### 12.3 Password Security
- [ ] Passwords are hashed (never stored in plain text)
- [ ] Password reset tokens expire
- [ ] Password reset tokens are single-use
- [ ] Old passwords cannot be reused (if policy implemented)

#### 12.4 API Key Security
- [ ] API keys are hashed in database
- [ ] API keys shown only once on creation
- [ ] API keys can be revoked
- [ ] Revoked keys return 401 Unauthorized

---

## 🐛 Error Handling

### 13. Error Scenarios

#### 13.1 Network Errors
- [ ] Network timeout - shows user-friendly error
- [ ] Network disconnection - shows error, allows retry
- [ ] Server error (500) - shows error message

#### 13.2 Validation Errors
- [ ] Form validation errors appear inline
- [ ] API validation errors are clear
- [ ] Error messages are actionable

#### 13.3 Edge Cases
- [ ] Login with very long email - handled correctly
- [ ] Login with special characters - handled correctly
- [ ] Registration with existing email - shows error
- [ ] Password reset with invalid token - shows error

---

## ✅ Final Verification

### 14. Complete Workflows

#### 14.1 New User Registration Flow
- [ ] User registers via frontend
- [ ] User receives confirmation (if implemented)
- [ ] User can login immediately
- [ ] User can access profile
- [ ] User can enable 2FA
- [ ] User can change password

#### 14.2 Admin User Management Flow
- [ ] Admin logs in
- [ ] Admin accesses user list
- [ ] Admin creates new user
- [ ] Admin edits user role
- [ ] Admin deactivates user
- [ ] Admin deletes user

#### 14.3 2FA Complete Flow
- [ ] User enables 2FA
- [ ] User scans QR code
- [ ] User verifies with TOTP
- [ ] User logs out
- [ ] User logs in with password
- [ ] User enters TOTP code
- [ ] User successfully logs in

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

- [ ] All Django Admin tests passed
- [ ] All API endpoint tests passed
- [ ] All Frontend tests passed
- [ ] All Security tests passed
- [ ] All Error handling tests passed
- [ ] Complete workflows tested

**Tester Signature:** _______________  
**Date:** _______________

