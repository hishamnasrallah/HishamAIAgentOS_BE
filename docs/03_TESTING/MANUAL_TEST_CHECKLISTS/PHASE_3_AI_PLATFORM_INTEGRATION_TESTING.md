---
title: "Phase 3: AI Platform Integration - Manual Testing Checklist"
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
  - phase-3
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

# Phase 3: AI Platform Integration - Manual Testing Checklist

**Date:** December 2024  
**Component:** AI Platform Integration Layer  
**Phase:** Phase 3  
**Status:** ✅ Complete (100%)

---

## 📋 Pre-Testing Setup

- [ ] Backend server is running (`python manage.py runserver` or `daphne`)
- [ ] Frontend server is running (`npm run dev`) - for admin UI
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Valid API keys configured for all platforms (OpenAI, Anthropic, Google)
- [ ] Browser console is open (F12) to check for errors
- [ ] Postman/API client ready for API testing
- [ ] Django admin accessible at `/admin/`

---

## 🔌 Backend Django Admin Testing

### 1. AI Platform Model Admin

#### 1.1 Access Platform Admin
- [ ] Navigate to `/admin/integrations/aiplatform/`
- [ ] Platform list displays all platforms
- [ ] Platform list shows: display_name, platform_name, status, health_status, is_default
- [ ] Search works (display_name, platform_name)
- [ ] Filters work (platform_name, status, health_status, is_default)
- [ ] Each platform shows encrypted API key status (not the key itself)

#### 1.2 Create Platform via Admin
- [ ] Click "Add AI Platform" button
- [ ] Form displays all fields:
  - [ ] Platform Name (dropdown: openai, anthropic, google)
  - [ ] Display Name (required)
  - [ ] API Type (dropdown)
  - [ ] Default Model (required)
  - [ ] API Key (password field, encrypted on save)
  - [ ] API URL (optional)
  - [ ] Organization ID (optional)
  - [ ] Timeout (number, required)
  - [ ] Max Tokens (number, required)
  - [ ] Capabilities checkboxes (Vision, JSON Mode, Image Generation)
  - [ ] Rate Limit Per Minute (number)
  - [ ] Rate Limit Per Day (number)
  - [ ] Status (dropdown: active, inactive, maintenance)
  - [ ] Priority (number)
  - [ ] Is Default checkbox
  - [ ] Enabled checkbox
- [ ] Submit with valid data - platform created
- [ ] API key is encrypted in database (verify in database)
- [ ] API key is never displayed in admin after save

#### 1.3 Edit Platform via Admin
- [ ] Click on existing platform to edit
- [ ] API Key field is empty (for security)
- [ ] Enter new API key - encrypts and saves
- [ ] Leave API key empty - preserves existing encrypted key
- [ ] Update all other fields - saves correctly
- [ ] Change default model - saves correctly
- [ ] Toggle capabilities - saves correctly
- [ ] Update rate limits - saves correctly

#### 1.4 Delete Platform via Admin
- [ ] Select platform and delete
- [ ] Confirmation shows
- [ ] Confirm deletion - platform removed
- [ ] Related usage logs handled correctly

---

### 2. Platform Usage Model Admin

#### 2.1 Access Usage Admin
- [ ] Navigate to `/admin/integrations/platformusage/`
- [ ] Usage list displays all usage records
- [ ] Usage list shows: platform, user, date, requests, tokens, cost
- [ ] Search works (platform, user)
- [ ] Filters work (platform, user, date)
- [ ] Date range filter works (if implemented)

#### 2.2 View Usage Details
- [ ] Click on usage record
- [ ] All fields visible:
  - [ ] Platform (foreign key)
  - [ ] User (foreign key, nullable)
  - [ ] Date (date field)
  - [ ] Requests (integer)
  - [ ] Tokens Used (integer)
  - [ ] Cost (decimal)
  - [ ] Created At (datetime)
- [ ] Usage records are read-only (created automatically)

---

## 🌐 Backend API Testing

### 3. Platform Management Endpoints

#### 3.1 List Platforms
- [ ] **GET** `/api/v1/integrations/platforms/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Admin user - returns 200 OK with all platforms
- [ ] Non-admin user - returns 200 OK (may filter sensitive data)
- [ ] Response includes: id, display_name, platform_name, status, health_status
- [ ] Response does NOT include API keys
- [ ] Pagination works (if implemented)
- [ ] Filtering works (status, platform_name)

#### 3.2 Get Platform Details
- [ ] **GET** `/api/v1/integrations/platforms/{id}/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Returns platform details
- [ ] Does NOT return API key
- [ ] Returns health status
- [ ] Returns capabilities
- [ ] Returns rate limits

#### 3.3 Create Platform (Admin Only)
- [ ] **POST** `/api/v1/integrations/platforms/`
- [ ] Request headers: `Authorization: Bearer <admin_access_token>`
- [ ] Request body:
  ```json
  {
    "platform_name": "openai",
    "display_name": "OpenAI Production",
    "api_type": "chat",
    "default_model": "gpt-4-turbo-preview",
    "api_key": "sk-...",
    "timeout": 30,
    "max_tokens": 4096,
    "capabilities": ["vision", "json_mode"],
    "rate_limit_per_minute": 60,
    "rate_limit_per_day": 10000,
    "status": "active",
    "priority": 1,
    "is_default": true,
    "enabled": true
  }
  ```
- [ ] Admin user - returns 201 Created
- [ ] Non-admin user - returns 403 Forbidden
- [ ] API key is encrypted in database
- [ ] Platform created successfully

#### 3.4 Update Platform (Admin Only)
- [ ] **PATCH** `/api/v1/integrations/platforms/{id}/`
- [ ] Request headers: `Authorization: Bearer <admin_access_token>`
- [ ] Update display_name - saves successfully
- [ ] Update default_model - saves successfully
- [ ] Update API key - encrypts and saves
- [ ] Leave API key empty - preserves existing key
- [ ] Update rate limits - saves successfully
- [ ] Update capabilities - saves successfully

#### 3.5 Delete Platform (Admin Only)
- [ ] **DELETE** `/api/v1/integrations/platforms/{id}/`
- [ ] Request headers: `Authorization: Bearer <admin_access_token>`
- [ ] Admin user - can delete platform
- [ ] Non-admin user - returns 403 Forbidden
- [ ] Platform deleted successfully

#### 3.6 Platform Health Check
- [ ] **GET** `/api/v1/integrations/platforms/{id}/health/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Returns health status (healthy/unhealthy)
- [ ] Returns response time
- [ ] Returns last checked timestamp
- [ ] Works for all platforms

---

### 4. Platform Usage Endpoints

#### 4.1 List Platform Usage
- [ ] **GET** `/api/v1/integrations/usage/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Returns usage records
- [ ] Filter by platform - works
- [ ] Filter by user - works
- [ ] Filter by date range - works
- [ ] Admin sees all usage
- [ ] Non-admin sees only their usage
- [ ] Pagination works

#### 4.2 Get Usage Summary
- [ ] **GET** `/api/v1/integrations/usage/summary/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Query params: `?platform=openai&start_date=2024-01-01&end_date=2024-12-31`
- [ ] Returns aggregated usage:
  - [ ] Total requests
  - [ ] Total tokens
  - [ ] Total cost
  - [ ] Average response time
- [ ] Filtering works correctly
- [ ] Date range filtering works

---

### 5. Adapter Testing (Direct API Calls)

#### 5.1 OpenAI Adapter
- [ ] Create OpenAI platform via API
- [ ] Test OpenAI adapter with valid API key
- [ ] **POST** `/api/v1/agents/execute/` with OpenAI platform
- [ ] Request completes successfully
- [ ] Response includes output
- [ ] Cost is tracked
- [ ] Tokens are tracked
- [ ] Usage record created
- [ ] Test with GPT-3.5 Turbo
- [ ] Test with GPT-4 Turbo
- [ ] Test with GPT-4 Vision (if capability enabled)
- [ ] Test streaming response (if implemented)

#### 5.2 Anthropic Adapter
- [ ] Create Anthropic platform via API
- [ ] Test Anthropic adapter with valid API key
- [ ] **POST** `/api/v1/agents/execute/` with Anthropic platform
- [ ] Request completes successfully
- [ ] Response includes output
- [ ] Cost is tracked
- [ ] Tokens are tracked
- [ ] Usage record created
- [ ] Test with Claude 3 Opus
- [ ] Test with Claude 3 Sonnet
- [ ] Test with Claude 3 Haiku
- [ ] Test streaming response (if implemented)

#### 5.3 Google Gemini Adapter
- [ ] Create Google Gemini platform via API
- [ ] Test Gemini adapter with valid API key
- [ ] **POST** `/api/v1/agents/execute/` with Gemini platform
- [ ] Request completes successfully
- [ ] Response includes output
- [ ] Cost is tracked
- [ ] Tokens are tracked
- [ ] Usage record created
- [ ] Test with Gemini Pro
- [ ] Test with Gemini Flash
- [ ] Test streaming response (if implemented)

---

### 6. Fallback Mechanism Testing

#### 6.1 Automatic Fallback
- [ ] Configure primary platform (OpenAI)
- [ ] Configure fallback platform (Anthropic)
- [ ] Disable primary platform API key (or use invalid key)
- [ ] Execute agent request
- [ ] System automatically falls back to Anthropic
- [ ] Request completes successfully
- [ ] Fallback is logged
- [ ] Usage tracked on fallback platform

#### 6.2 Fallback on Error
- [ ] Primary platform returns error (500, timeout, etc.)
- [ ] System automatically retries with fallback
- [ ] Request completes with fallback platform
- [ ] Error is logged
- [ ] Fallback attempt is tracked

#### 6.3 Fallback on Rate Limit
- [ ] Primary platform hits rate limit
- [ ] System automatically falls back
- [ ] Request completes with fallback platform
- [ ] Rate limit is logged
- [ ] Fallback is tracked

#### 6.4 Multiple Fallbacks
- [ ] Configure multiple fallback platforms
- [ ] Primary fails, first fallback fails
- [ ] System tries second fallback
- [ ] Request completes successfully
- [ ] All attempts are logged

---

### 7. Cost Tracking Testing

#### 7.1 Cost Calculation
- [ ] Execute request with OpenAI
- [ ] Cost is calculated correctly (input + output tokens)
- [ ] Cost matches platform pricing
- [ ] Cost is stored in PlatformUsage record
- [ ] Cost is aggregated correctly

#### 7.2 Cost Tracking Per Platform
- [ ] Execute requests on multiple platforms
- [ ] Each platform tracks its own cost
- [ ] Cost summary shows per-platform breakdown
- [ ] Total cost is accurate

#### 7.3 Cost Tracking Per User
- [ ] Execute requests as different users
- [ ] Each user's cost is tracked separately
- [ ] User cost summary is accurate
- [ ] Admin can see all user costs

---

### 8. Rate Limiting Testing

#### 8.1 Rate Limit Enforcement
- [ ] Configure rate limit (e.g., 60 requests/minute)
- [ ] Make requests up to limit - all succeed
- [ ] Exceed rate limit - returns 429 Too Many Requests
- [ ] Rate limit resets after time window
- [ ] Rate limit is per platform
- [ ] Rate limit is per user (if implemented)

#### 8.2 Rate Limit Headers
- [ ] API responses include rate limit headers:
  - [ ] X-RateLimit-Limit
  - [ ] X-RateLimit-Remaining
  - [ ] X-RateLimit-Reset
- [ ] Headers are accurate
- [ ] Headers update correctly

---

## 🎨 Frontend Testing (Admin UI)

### 9. Platform Configuration UI

#### 9.1 Platform List View
- [ ] Navigate to `/admin/platforms`
- [ ] Platform list displays all platforms
- [ ] Each platform card shows:
  - [ ] Display name
  - [ ] Platform name badge
  - [ ] Status badge (Active/Inactive/Maintenance)
  - [ ] Health status badge (Healthy/Unhealthy)
  - [ ] Default badge (if is_default)
  - [ ] API Key badge (if has key)
  - [ ] Request count
  - [ ] Cost summary
- [ ] Search works
- [ ] Filters work (status, health, platform_name)
- [ ] Loading skeleton appears while fetching

#### 9.2 Create Platform Form
- [ ] Click "New Platform" button
- [ ] Form displays all fields
- [ ] Platform dropdown works (OpenAI/Anthropic/Google)
- [ ] API Key field is password type with show/hide toggle
- [ ] Capabilities checkboxes work
- [ ] Submit with valid data - platform created
- [ ] API key is encrypted (verify in network request)
- [ ] Success message displayed
- [ ] Form closes, list refreshes

#### 9.3 Edit Platform Form
- [ ] Click "Edit" on a platform
- [ ] Form pre-populated with platform data
- [ ] API Key field is empty (for security)
- [ ] Update fields - saves successfully
- [ ] Update API key - encrypts and saves
- [ ] Leave API key empty - preserves existing key

#### 9.4 Platform Health Display
- [ ] Health status updates in real-time (if WebSocket)
- [ ] Healthy platforms show green badge
- [ ] Unhealthy platforms show red badge
- [ ] Health check button works (if implemented)
- [ ] Health status details displayed (response time, last check)

---

## 🔒 Security Testing

### 10. API Key Security

#### 10.1 API Key Encryption
- [ ] API keys are encrypted in database
- [ ] API keys are never returned in API responses
- [ ] API keys are never displayed in frontend
- [ ] Only `has_api_key` boolean is shown
- [ ] API keys can only be updated, never retrieved

#### 10.2 API Key Access Control
- [ ] Only admins can create platforms
- [ ] Only admins can update API keys
- [ ] Non-admins cannot see API keys
- [ ] API keys are validated before saving

---

### 11. Platform Access Control

#### 11.1 Platform Visibility
- [ ] Admin can see all platforms
- [ ] Non-admin can see active platforms (if policy allows)
- [ ] Inactive platforms hidden from non-admins
- [ ] Platform details filtered for non-admins

#### 11.2 Platform Management
- [ ] Only admins can create platforms
- [ ] Only admins can update platforms
- [ ] Only admins can delete platforms
- [ ] Non-admins cannot modify platforms

---

## 🐛 Error Handling

### 12. Error Scenarios

#### 12.1 Invalid API Key
- [ ] Create platform with invalid API key
- [ ] System shows error (or allows but marks unhealthy)
- [ ] Health check fails
- [ ] Requests fail with appropriate error

#### 12.2 Platform Unavailable
- [ ] Platform API is down
- [ ] System handles gracefully
- [ ] Fallback mechanism activates
- [ ] Error is logged
- [ ] User receives appropriate error message

#### 12.3 Network Timeout
- [ ] Platform request times out
- [ ] System handles timeout
- [ ] Fallback activates
- [ ] Timeout is logged
- [ ] User receives timeout error

#### 12.4 Rate Limit Exceeded
- [ ] Platform rate limit exceeded
- [ ] System returns 429 error
- [ ] Fallback activates (if configured)
- [ ] Rate limit error is clear
- [ ] Retry-after header provided (if implemented)

---

## ✅ Final Verification

### 13. Complete Workflows

#### 13.1 Platform Setup Workflow
- [ ] Admin creates OpenAI platform
- [ ] Admin enters API key (encrypted)
- [ ] Platform health check passes
- [ ] Platform is set as default
- [ ] Agent execution uses platform
- [ ] Usage is tracked
- [ ] Cost is calculated correctly

#### 13.2 Fallback Workflow
- [ ] Admin configures primary and fallback platforms
- [ ] Primary platform fails
- [ ] System automatically falls back
- [ ] Request completes successfully
- [ ] Fallback is logged
- [ ] Usage tracked on fallback platform

#### 13.3 Multi-Platform Usage Workflow
- [ ] Admin configures multiple platforms
- [ ] Execute requests on different platforms
- [ ] Each platform tracks usage separately
- [ ] Cost summary shows per-platform breakdown
- [ ] Health status for all platforms is accurate

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
- [ ] All adapter tests passed
- [ ] Fallback mechanism works
- [ ] Cost tracking accurate
- [ ] Rate limiting works
- [ ] Security checks passed
- [ ] Error handling works
- [ ] Complete workflows tested

**Tester Signature:** _______________  
**Date:** _______________

