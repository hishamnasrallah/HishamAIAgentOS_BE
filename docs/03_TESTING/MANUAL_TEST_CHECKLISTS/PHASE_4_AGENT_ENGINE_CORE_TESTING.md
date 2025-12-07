---
title: "Phase 4: Agent Engine Core - Manual Testing Checklist"
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
  - phase-4
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

# Phase 4: Agent Engine Core - Manual Testing Checklist

**Date:** December 2024  
**Component:** Agent Engine Core System  
**Phase:** Phase 4  
**Status:** ✅ Complete (100%)

---

## 📋 Pre-Testing Setup

- [ ] Backend server is running (`python manage.py runserver` or `daphne`)
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] At least one AI platform configured with valid API key
- [ ] At least one agent loaded in database
- [ ] Browser console is open (F12) to check for errors
- [ ] Postman/API client ready for API testing
- [ ] Django admin accessible at `/admin/`

---

## 🤖 Backend Django Admin Testing

### 1. Agent Model Admin

#### 1.1 Access Agent Admin
- [ ] Navigate to `/admin/agents/agent/`
- [ ] Agent list displays all agents
- [ ] Agent list shows: agent_id, name, status, preferred_platform, model_name
- [ ] Search works (agent_id, name, description)
- [ ] Filters work (status, preferred_platform, capabilities)
- [ ] Each agent shows metrics (if available): invocations, success_rate, avg_response_time

#### 1.2 Create Agent via Admin
- [ ] Click "Add Agent" button
- [ ] Form displays all fields:
  - [ ] Agent ID (required, unique, lowercase, no spaces)
  - [ ] Name (required)
  - [ ] Description (textarea)
  - [ ] Capabilities (many-to-many checkboxes, 15 options)
  - [ ] System Prompt (large textarea, required)
  - [ ] Preferred Platform (dropdown: OpenAI, Anthropic, Google)
  - [ ] Model Name (text input)
  - [ ] Temperature (number, 0-2, step 0.1)
  - [ ] Max Tokens (number, required)
  - [ ] Status (dropdown: active, inactive, maintenance)
  - [ ] Version (string)
  - [ ] Fallback Platforms (many-to-many checkboxes)
- [ ] Submit with valid data - agent created
- [ ] Agent ID is validated (format, uniqueness)
- [ ] System prompt is saved correctly

#### 1.3 Edit Agent via Admin
- [ ] Click on existing agent to edit
- [ ] Agent ID is read-only (cannot change)
- [ ] Update all other fields - saves correctly
- [ ] Update system prompt - saves correctly
- [ ] Change capabilities - saves correctly
- [ ] Change preferred platform - saves correctly
- [ ] Update model configuration - saves correctly

#### 1.4 Delete Agent via Admin
- [ ] Select agent and delete
- [ ] Confirmation shows
- [ ] Check for related executions (warn if exist)
- [ ] Confirm deletion - agent removed
- [ ] Related executions handled correctly

---

### 2. Agent Execution Model Admin

#### 2.1 Access Execution Admin
- [ ] Navigate to `/admin/agents/agentexecution/`
- [ ] Execution list displays all executions
- [ ] Execution list shows: agent, user, status, created_at, cost, tokens
- [ ] Search works (agent, user, status)
- [ ] Filters work (agent, user, status, created_at)
- [ ] Date range filter works

#### 2.2 View Execution Details
- [ ] Click on execution record
- [ ] All fields visible:
  - [ ] Agent (foreign key)
  - [ ] User (foreign key)
  - [ ] Status (dropdown: pending, running, completed, failed, cancelled)
  - [ ] Input (JSON field, formatted)
  - [ ] Output (JSON field, formatted)
  - [ ] Error Message (textarea, if failed)
  - [ ] Cost (decimal)
  - [ ] Tokens Used (integer)
  - [ ] Response Time (decimal, seconds)
  - [ ] Created At (datetime)
  - [ ] Updated At (datetime)
  - [ ] Completed At (datetime, nullable)
- [ ] JSON fields are formatted and readable
- [ ] Execution relationships work (agent, user)

---

## 🌐 Backend API Testing

### 3. Agent Management Endpoints

#### 3.1 List Agents
- [ ] **GET** `/api/v1/agents/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Returns 200 OK with agent list
- [ ] Response includes: id, agent_id, name, description, status, capabilities
- [ ] Pagination works (if implemented)
- [ ] Filtering works (status, capabilities, platform)
- [ ] Search works (name, description)

#### 3.2 Get Agent Details
- [ ] **GET** `/api/v1/agents/{id}/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Returns agent details
- [ ] Includes all agent configuration
- [ ] Includes metrics (if available)
- [ ] Does NOT include system prompt (security)

#### 3.3 Create Agent (Admin Only)
- [ ] **POST** `/api/v1/agents/`
- [ ] Request headers: `Authorization: Bearer <admin_access_token>`
- [ ] Request body:
  ```json
  {
    "agent_id": "test_agent",
    "name": "Test Agent",
    "description": "Test agent description",
    "capabilities": ["code_generation", "code_review"],
    "system_prompt": "You are a helpful assistant...",
    "preferred_platform": "openai",
    "model_name": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "max_tokens": 2000,
    "status": "active",
    "version": "1.0.0",
    "fallback_platforms": ["anthropic"]
  }
  ```
- [ ] Admin user - returns 201 Created
- [ ] Non-admin user - returns 403 Forbidden
- [ ] Agent created successfully
- [ ] Agent ID validated (format, uniqueness)

#### 3.4 Update Agent (Admin Only)
- [ ] **PATCH** `/api/v1/agents/{id}/`
- [ ] Request headers: `Authorization: Bearer <admin_access_token>`
- [ ] Update name - saves successfully
- [ ] Update system prompt - saves successfully
- [ ] Update capabilities - saves successfully
- [ ] Update model configuration - saves successfully
- [ ] Agent ID cannot be changed

#### 3.5 Delete Agent (Admin Only)
- [ ] **DELETE** `/api/v1/agents/{id}/`
- [ ] Request headers: `Authorization: Bearer <admin_access_token>`
- [ ] Admin user - can delete agent
- [ ] Non-admin user - returns 403 Forbidden
- [ ] Agent deleted successfully

---

### 4. Agent Execution Endpoints

#### 4.1 Execute Agent
- [ ] **POST** `/api/v1/agents/{id}/execute/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Request body:
  ```json
  {
    "input": {
      "task": "Write a Python function to calculate factorial",
      "context": "For a math library"
    },
    "stream": false
  }
  ```
- [ ] Returns 200 OK with execution ID
- [ ] Execution record created in database
- [ ] Status is "pending" initially
- [ ] Response includes execution ID

#### 4.2 Execute Agent (Streaming)
- [ ] **POST** `/api/v1/agents/{id}/execute/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Request body:
  ```json
  {
    "input": {
      "task": "Explain quantum computing"
    },
    "stream": true
  }
  ```
- [ ] Returns streaming response (Server-Sent Events or WebSocket)
- [ ] Stream chunks received correctly
- [ ] Final execution record created
- [ ] Status is "completed" after stream ends

#### 4.3 Get Execution Status
- [ ] **GET** `/api/v1/agents/executions/{execution_id}/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Returns execution details
- [ ] Status updates correctly (pending → running → completed)
- [ ] Includes input and output (when completed)
- [ ] Includes cost and tokens (when completed)
- [ ] Includes error message (if failed)

#### 4.4 List Executions
- [ ] **GET** `/api/v1/agents/executions/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Returns execution list
- [ ] Filter by agent - works
- [ ] Filter by user - works
- [ ] Filter by status - works
- [ ] Filter by date range - works
- [ ] Admin sees all executions
- [ ] Non-admin sees only their executions
- [ ] Pagination works

#### 4.5 Cancel Execution
- [ ] **POST** `/api/v1/agents/executions/{execution_id}/cancel/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Cancel pending execution - status changes to "cancelled"
- [ ] Cancel running execution - status changes to "cancelled" (if supported)
- [ ] Cannot cancel completed execution
- [ ] User can only cancel their own executions
- [ ] Admin can cancel any execution

---

### 5. Agent Dispatcher Testing

#### 5.1 Automatic Agent Selection
- [ ] **POST** `/api/v1/agents/dispatch/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Request body:
  ```json
  {
    "task": "Review this code for security issues",
    "required_capabilities": ["code_review", "security_analysis"]
  }
  ```
- [ ] System selects appropriate agent based on capabilities
- [ ] Selected agent has required capabilities
- [ ] Response includes selected agent ID
- [ ] Response includes confidence score (if implemented)

#### 5.2 Agent Scoring
- [ ] Request with multiple matching agents
- [ ] System scores agents based on:
  - [ ] Capability match
  - [ ] Success rate
  - [ ] Response time
  - [ ] Availability
- [ ] Highest scoring agent is selected
- [ ] Scoring algorithm is transparent (if logged)

#### 5.3 Fallback Agent Selection
- [ ] Primary agent unavailable
- [ ] System selects fallback agent
- [ ] Fallback agent has required capabilities
- [ ] Request completes successfully

---

### 6. Execution Engine Testing

#### 6.1 Task Agent Execution
- [ ] Execute agent with task-specific input
- [ ] Agent receives proper context
- [ ] Agent executes task
- [ ] Output is structured (if TaskAgent)
- [ ] Execution status updates correctly
- [ ] Metrics updated (success_rate, avg_response_time)

#### 6.2 Conversational Agent Execution
- [ ] Execute agent with conversation history
- [ ] Agent maintains context across turns
- [ ] History is passed correctly
- [ ] Agent responds appropriately
- [ ] Conversation state is preserved

#### 6.3 Context Management
- [ ] Agent receives full context
- [ ] Context includes user information
- [ ] Context includes previous interactions (if applicable)
- [ ] Context is properly formatted
- [ ] Large contexts are handled correctly

---

### 7. State Management Testing

#### 7.1 Execution State Tracking
- [ ] Execution state updates correctly:
  - [ ] pending → running
  - [ ] running → completed
  - [ ] running → failed (on error)
- [ ] State transitions are logged
- [ ] State is persisted in database
- [ ] State can be queried via API

#### 7.2 Execution Recovery
- [ ] Execution fails mid-process
- [ ] State is saved
- [ ] Execution can be resumed (if implemented)
- [ ] Error is logged
- [ ] User is notified

---

### 8. Metrics Tracking Testing

#### 8.1 Execution Metrics
- [ ] Execute agent multiple times
- [ ] Metrics are tracked:
  - [ ] Total invocations
  - [ ] Success count
  - [ ] Failure count
  - [ ] Success rate
  - [ ] Average response time
  - [ ] Total cost
  - [ ] Total tokens
- [ ] Metrics update after each execution
- [ ] Metrics are accurate

#### 8.2 Agent Metrics API
- [ ] **GET** `/api/v1/agents/{id}/metrics/`
- [ ] Request headers: `Authorization: Bearer <access_token>`
- [ ] Returns agent metrics
- [ ] Includes all tracked metrics
- [ ] Metrics are up-to-date
- [ ] Historical metrics available (if implemented)

---

## 🔒 Security Testing

### 9. Access Control

#### 9.1 Agent Access
- [ ] Admin can create/update/delete agents
- [ ] Non-admin can view agents (if policy allows)
- [ ] Non-admin cannot modify agents
- [ ] Agent system prompts are protected (not exposed)

#### 9.2 Execution Access
- [ ] Users can execute agents
- [ ] Users can view their own executions
- [ ] Users cannot view other users' executions
- [ ] Admin can view all executions
- [ ] Execution input/output is protected

---

## 🐛 Error Handling

### 10. Error Scenarios

#### 10.1 Agent Not Found
- [ ] Execute non-existent agent
- [ ] Returns 404 Not Found
- [ ] Error message is clear

#### 10.2 Agent Inactive
- [ ] Execute inactive agent
- [ ] Returns 400 Bad Request or 403 Forbidden
- [ ] Error message indicates agent is inactive

#### 10.3 Platform Unavailable
- [ ] Agent's platform is unavailable
- [ ] System handles gracefully
- [ ] Fallback platform used (if configured)
- [ ] Error is logged
- [ ] User receives appropriate error

#### 10.4 Execution Timeout
- [ ] Execution takes too long
- [ ] System times out
- [ ] Execution status set to "failed"
- [ ] Error message indicates timeout
- [ ] Timeout is logged

#### 10.5 Invalid Input
- [ ] Execute with invalid input
- [ ] Returns 400 Bad Request
- [ ] Validation errors are clear
- [ ] Execution is not created

---

## ✅ Final Verification

### 11. Complete Workflows

#### 11.1 Agent Execution Workflow
- [ ] User selects agent
- [ ] User provides input
- [ ] System dispatches to agent
- [ ] Agent executes task
- [ ] Output is returned
- [ ] Execution is tracked
- [ ] Metrics are updated
- [ ] Cost is calculated

#### 11.2 Multi-Agent Workflow
- [ ] Execute multiple agents in sequence
- [ ] Each execution is tracked separately
- [ ] Context is passed between agents (if applicable)
- [ ] All executions complete successfully
- [ ] All metrics updated correctly

#### 11.3 Error Recovery Workflow
- [ ] Agent execution fails
- [ ] Error is logged
- [ ] User is notified
- [ ] System recovers gracefully
- [ ] Retry works (if implemented)

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
- [ ] Agent execution works correctly
- [ ] Dispatcher works correctly
- [ ] State management works
- [ ] Metrics tracking accurate
- [ ] Security checks passed
- [ ] Error handling works
- [ ] Complete workflows tested

**Tester Signature:** _______________  
**Date:** _______________

