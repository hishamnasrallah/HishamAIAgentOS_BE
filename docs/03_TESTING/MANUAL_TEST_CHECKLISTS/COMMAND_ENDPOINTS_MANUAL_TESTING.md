---
title: "Command API Endpoints - Manual Testing Checklist"
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
  - commands
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

# Command API Endpoints - Manual Testing Checklist

**Date:** December 2024  
**Component:** Command Library API Endpoints  
**Related Phase:** Phase 6 (Command Library)  
**Status:** ✅ Complete

---

## 📋 Pre-Testing Setup

- [ ] Backend server is running (`python manage.py runserver` or `daphne`)
- [ ] Frontend server is running (`npm run dev`)
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Commands are loaded: `python manage.py create_commands`
- [ ] You have a valid authentication token
- [ ] Browser console is open (F12) to check for errors
- [ ] API testing tool ready (Postman, Swagger UI, or curl)
- [ ] At least one command template exists in database

---

## 🔍 Endpoint 1: Popular Commands

### 1.1 GET /api/v1/commands/templates/popular/

#### 1.1.1 Basic Request
- [ ] Make GET request to `/api/v1/commands/templates/popular/`
- [ ] Request includes `Authorization: Bearer <token>` header
- [ ] Response status is `200 OK`
- [ ] Response is a JSON array
- [ ] Array contains up to 10 commands

#### 1.1.2 Response Structure
- [ ] Each command object contains:
  - [ ] `id` (UUID)
  - [ ] `name` (string)
  - [ ] `slug` (string)
  - [ ] `description` (string)
  - [ ] `category_name` (string)
  - [ ] `tags` (array)
  - [ ] `usage_count` (integer)
  - [ ] `success_rate` (float)
  - [ ] `estimated_cost` (decimal)
  - [ ] `is_active` (boolean)

#### 1.1.3 Data Validation
- [ ] Commands are sorted by success_rate (descending)
- [ ] Commands are sorted by usage_count (descending)
- [ ] Only active commands are returned
- [ ] Maximum 10 commands returned
- [ ] Commands have valid data types

#### 1.1.4 Authentication
- [ ] Request without token returns `401 Unauthorized`
- [ ] Request with invalid token returns `401 Unauthorized`
- [ ] Request with valid token returns `200 OK`

#### 1.1.5 Edge Cases
- [ ] No commands exist - returns empty array `[]`
- [ ] All commands inactive - returns empty array `[]`
- [ ] Less than 10 commands - returns all available commands

---

## 🔍 Endpoint 2: Preview Command Template

### 2.1 POST /api/v1/commands/templates/{id}/preview/

#### 2.1.1 Get Command ID
- [ ] List commands: `GET /api/v1/commands/templates/`
- [ ] Select a command with parameters
- [ ] Note the command `id` (UUID)

#### 2.1.2 Basic Preview Request
- [ ] Make POST request to `/api/v1/commands/templates/{id}/preview/`
- [ ] Request includes `Authorization: Bearer <token>` header
- [ ] Request body: `{"parameters": {}}`
- [ ] Response status is `200 OK` or `400 Bad Request`

#### 2.1.3 Valid Parameters
- [ ] Get command parameters schema: `GET /api/v1/commands/templates/{id}/`
- [ ] Identify required parameters
- [ ] Create request with all required parameters:
  ```json
  {
    "parameters": {
      "param1": "value1",
      "param2": "value2"
    }
  }
  ```
- [ ] Response status is `200 OK`
- [ ] Response contains `rendered_template` (string)
- [ ] Response contains `validation_errors` (empty array)
- [ ] Rendered template has parameters substituted

#### 2.1.4 Parameter Validation
- [ ] Missing required parameter:
  - [ ] Request with missing required parameter
  - [ ] Response status is `400 Bad Request`
  - [ ] Response contains `validation_errors` array
  - [ ] Error message describes missing parameter
- [ ] Invalid parameter type:
  - [ ] Request with wrong type (e.g., string instead of integer)
  - [ ] Response status is `400 Bad Request`
  - [ ] Error message describes type mismatch
- [ ] Invalid parameter value (allowed_values):
  - [ ] Request with value not in allowed_values
  - [ ] Response status is `400 Bad Request`
  - [ ] Error message lists allowed values

#### 2.1.5 Template Rendering
- [ ] Rendered template contains substituted values
- [ ] Template placeholders `{{param_name}}` are replaced
- [ ] Template structure is preserved
- [ ] Special characters are handled correctly
- [ ] Long text parameters are included fully

#### 2.1.6 Edge Cases
- [ ] Command with no parameters - returns template as-is
- [ ] Command with optional parameters only - works with empty parameters
- [ ] Invalid command ID - returns `404 Not Found`
- [ ] Inactive command - can still preview (verify behavior)

---

## 🔍 Endpoint 3: Execute Command Template

### 3.1 POST /api/v1/commands/templates/{id}/execute/

#### 3.1.1 Basic Execute Request
- [ ] Make POST request to `/api/v1/commands/templates/{id}/execute/`
- [ ] Request includes `Authorization: Bearer <token>` header
- [ ] Request body: `{"parameters": {}}`
- [ ] Response status is `200 OK` (or error if execution fails)

#### 3.1.2 Response Structure (Success)
- [ ] Response contains:
  - [ ] `success` (boolean) - `true`
  - [ ] `output` (string) - Command execution output
  - [ ] `execution_time` (float) - Time in seconds
  - [ ] `cost` (decimal) - Cost in USD
  - [ ] `token_usage` (object) - `{"tokens_used": number}`
  - [ ] `agent_used` (string) - Agent ID or name
  - [ ] `error` (null or string)

#### 3.1.3 Response Structure (Error)
- [ ] Response contains:
  - [ ] `success` (boolean) - `false`
  - [ ] `output` (string) - Empty or partial output
  - [ ] `execution_time` (float) - Time before failure
  - [ ] `cost` (decimal) - Cost incurred before failure
  - [ ] `token_usage` (object) - Tokens used before failure
  - [ ] `agent_used` (string) - Agent that attempted execution
  - [ ] `error` (string) - Error message

#### 3.1.4 Parameter Validation
- [ ] Missing required parameters - returns `400 Bad Request`
- [ ] Invalid parameter types - returns `400 Bad Request`
- [ ] Invalid parameter values - returns `400 Bad Request`
- [ ] All valid parameters - request proceeds to execution

#### 3.1.5 Command Execution
- [ ] Command with valid parameters executes
- [ ] Execution completes (may take time for LLM calls)
- [ ] Output is generated
- [ ] Cost is calculated
- [ ] Token usage is tracked
- [ ] Agent is selected and used

#### 3.1.6 Agent Selection
- [ ] Command with `recommended_agent` uses that agent
- [ ] Command without `recommended_agent` uses capability matching
- [ ] Agent override via `agent_id` parameter works (if implemented)
- [ ] Invalid `agent_id` returns `404 Not Found`

#### 3.1.7 Execution Scenarios
- [ ] **Successful Execution:**
  - [ ] AI platform is configured
  - [ ] API keys are valid
  - [ ] Command executes successfully
  - [ ] Output is returned
- [ ] **Platform Not Available:**
  - [ ] No AI platform configured
  - [ ] Response indicates platform error
  - [ ] Error message is descriptive
- [ ] **API Key Invalid:**
  - [ ] API key is invalid or expired
  - [ ] Response indicates authentication error
  - [ ] Error message is descriptive
- [ ] **Execution Timeout:**
  - [ ] Command takes too long
  - [ ] Response indicates timeout
  - [ ] Partial results may be returned

#### 3.1.8 Edge Cases
- [ ] Invalid command ID - returns `404 Not Found`
- [ ] Inactive command - verify behavior (may still execute or return error)
- [ ] Command with no template - verify behavior
- [ ] Command with empty template - verify behavior
- [ ] Very large parameters - verify handling
- [ ] Special characters in parameters - verify handling

---

## 🔧 Integration Testing

### 4.1 Complete Workflow

#### 4.1.1 Browse → Preview → Execute
- [ ] Get popular commands
- [ ] Select a command
- [ ] Preview command with sample parameters
- [ ] Verify preview looks correct
- [ ] Execute command with same parameters
- [ ] Verify execution output matches preview structure

#### 4.1.2 Parameter Validation Flow
- [ ] Preview with invalid parameters - see validation errors
- [ ] Fix parameters based on errors
- [ ] Preview again - validation passes
- [ ] Execute with corrected parameters - execution succeeds

#### 4.1.3 Error Recovery
- [ ] Execute command that fails
- [ ] Review error message
- [ ] Fix issue (parameters, platform config, etc.)
- [ ] Retry execution
- [ ] Execution succeeds

---

## 🔒 Security Testing

### 5.1 Authentication & Authorization

#### 5.1.1 Unauthenticated Access
- [ ] Request without token:
  - [ ] Popular endpoint - returns `401 Unauthorized`
  - [ ] Preview endpoint - returns `401 Unauthorized`
  - [ ] Execute endpoint - returns `401 Unauthorized`

#### 5.1.2 Invalid Token
- [ ] Request with invalid token:
  - [ ] All endpoints return `401 Unauthorized`
  - [ ] Error message indicates authentication failure

#### 5.1.3 Expired Token
- [ ] Request with expired token:
  - [ ] All endpoints return `401 Unauthorized`
  - [ ] Error message indicates token expired

#### 5.1.4 Role-Based Access (if applicable)
- [ ] Non-admin user can access endpoints (verify if admin-only)
- [ ] Admin user has full access
- [ ] Permissions are enforced correctly

---

## 🐛 Error Handling

### 6.1 Error Responses

#### 6.1.1 400 Bad Request
- [ ] Invalid request body format
- [ ] Missing required fields
- [ ] Invalid parameter values
- [ ] Error messages are descriptive

#### 6.1.2 401 Unauthorized
- [ ] Missing authentication token
- [ ] Invalid authentication token
- [ ] Expired authentication token
- [ ] Error messages indicate authentication issue

#### 6.1.3 404 Not Found
- [ ] Invalid command ID
- [ ] Command doesn't exist
- [ ] Invalid agent ID (if agent override used)
- [ ] Error messages indicate resource not found

#### 6.1.4 500 Internal Server Error
- [ ] Database connection issues
- [ ] AI platform errors
- [ ] Unexpected exceptions
- [ ] Error messages are logged (check server logs)

---

## 📊 Performance Testing

### 7.1 Response Times

#### 7.1.1 Popular Commands
- [ ] Response time < 500ms
- [ ] No noticeable delay
- [ ] Works with large number of commands

#### 7.1.2 Preview
- [ ] Response time < 1s
- [ ] Template rendering is fast
- [ ] Works with complex templates

#### 7.1.3 Execute
- [ ] Response time varies (depends on LLM)
- [ ] Timeout is reasonable (if configured)
- [ ] Progress updates (if implemented)

---

## ✅ Test Results Summary

### Endpoint 1: Popular Commands
- **Status:** [ ] Pass / [ ] Fail
- **Issues Found:** 
- **Notes:**

### Endpoint 2: Preview
- **Status:** [ ] Pass / [ ] Fail
- **Issues Found:**
- **Notes:**

### Endpoint 3: Execute
- **Status:** [ ] Pass / [ ] Fail
- **Issues Found:**
- **Notes:**

### Overall
- **Total Tests:** 
- **Passed:** 
- **Failed:** 
- **Success Rate:** %

---

## 🐛 Issues Found

### Issue 1
- **Endpoint:**
- **Description:**
- **Severity:** [ ] Critical / [ ] High / [ ] Medium / [ ] Low
- **Steps to Reproduce:**
- **Expected Behavior:**
- **Actual Behavior:**
- **Status:** [ ] Open / [ ] Fixed / [ ] Won't Fix

---

## 📝 Notes

- **Tested By:**
- **Test Date:**
- **Environment:**
- **Additional Notes:**

---

## 🔗 Related Documentation

- `docs/08_COMMANDS/COMMAND_TESTING_GUIDE.md` - Comprehensive testing guide
- `docs/07_TRACKING/COMMAND_ENDPOINTS_TESTING.md` - Endpoint testing documentation
- `docs/07_TRACKING/COMMAND_ENDPOINTS_TEST_RESULTS.md` - Automated test results

---

**Last Updated:** December 6, 2024  
**Status:** Ready for Testing

