---
title: "Phase 21: External Integrations - Manual Testing Checklist"
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
  - phase-21
  - testing
  - test
  - external-integrations
  - core
status: "active"
priority: "medium"
difficulty: "intermediate"
completeness: "100%"
quality_status: "draft"
estimated_read_time: "10 minutes"
version: "1.0"
last_updated: "2024-12-06"
last_reviewed: "2024-12-06"
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
    date: "2024-12-06"
    changes: "Initial version - Phase 21 external integrations testing checklist"
    author: "AI Assistant"
---

# Phase 21: External Integrations - Manual Testing Checklist

**Date:** December 6, 2024  
**Component:** External Integrations System  
**Phase:** Phase 21  
**Status:** ✅ Complete (100%)  
**Last Updated:** December 6, 2024 - All integrations including command execution signals complete

---

## 📋 Pre-Testing Setup

- [ ] Backend server is running (`python manage.py runserver` or `daphne`)
- [ ] Frontend server is running (`npm run dev`)
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] You have an admin user account (role: 'admin')
- [ ] You are logged in as an admin user
- [ ] Browser console is open (F12) to check for errors
- [ ] GitHub account with repository access (for GitHub integration testing)
- [ ] Slack workspace with bot token (for Slack integration testing)
- [ ] Email server configured (for email notification testing)
- [ ] Webhook testing tool (e.g., webhook.site) or local server

---

## 🔌 GitHub Integration Testing

### 1. GitHub Integration CRUD

#### 1.1 Create GitHub Integration
- [ ] Navigate to `/admin/integrations-external/github/` or use API
- [ ] Create new GitHub integration:
  - [ ] Enter repository owner
  - [ ] Enter repository name
  - [ ] Enter access token
  - [ ] Save integration
- [ ] Integration appears in list
- [ ] Integration is active by default

#### 1.2 Verify GitHub Connection
- [ ] Click "Verify" button on integration
- [ ] Connection verification succeeds
- [ ] Error handling: Invalid token shows error message

#### 1.3 Create GitHub Issue
- [ ] Use API endpoint: `POST /api/v1/integrations-external/github/{id}/create-issue/`
- [ ] Provide title and body
- [ ] Issue created in GitHub repository
- [ ] Response includes issue URL

#### 1.4 Sync Pull Requests
- [ ] Use API endpoint: `POST /api/v1/integrations-external/github/{id}/sync-prs/`
- [ ] PRs synced from GitHub
- [ ] Response shows count of synced PRs

#### 1.5 Update/Delete Integration
- [ ] Update integration details
- [ ] Changes saved correctly
- [ ] Delete integration
- [ ] Integration removed from list

---

## 💬 Slack Integration Testing

### 2. Slack Integration CRUD

#### 2.1 Create Slack Integration
- [ ] Navigate to `/admin/integrations-external/slack/` or use API
- [ ] Create new Slack integration:
  - [ ] Enter workspace name
  - [ ] Enter channel ID
  - [ ] Enter channel name
  - [ ] Enter bot token
  - [ ] Configure notification preferences
  - [ ] Save integration
- [ ] Integration appears in list

#### 2.2 Verify Slack Connection
- [ ] Click "Verify" button on integration
- [ ] Connection verification succeeds
- [ ] Error handling: Invalid token shows error message

#### 2.3 Send Test Message
- [ ] Use API endpoint: `POST /api/v1/integrations-external/slack/{id}/test-message/`
- [ ] Provide message text
- [ ] Message appears in Slack channel
- [ ] Response confirms success

#### 2.4 Notification Settings
- [ ] Toggle `notify_workflow_completion`
- [ ] Toggle `notify_command_execution`
- [ ] Toggle `notify_system_alerts`
- [ ] Settings saved correctly

---

## 📧 Email Notifications Testing

### 3. Email Notification Settings

#### 3.1 Configure Email Settings
- [ ] Use API endpoint: `GET /api/v1/integrations-external/email/`
- [ ] Settings retrieved (or created if not exist)
- [ ] Update notification preferences:
  - [ ] `notify_workflow_completion`
  - [ ] `notify_command_execution`
  - [ ] `notify_system_alerts`
  - [ ] `notify_daily_summary`
  - [ ] `notify_weekly_summary`
- [ ] Settings saved correctly

#### 3.2 Send Test Email
- [ ] Use API endpoint: `POST /api/v1/integrations-external/email/test-email/`
- [ ] Test email sent to configured address
- [ ] Email received in inbox
- [ ] Response confirms success

---

## 🔗 Webhook System Testing

### 4. Webhook Endpoint CRUD

#### 4.1 Create Webhook Endpoint
- [ ] Use API endpoint: `POST /api/v1/integrations-external/webhooks/`
- [ ] Provide:
  - [ ] Name
  - [ ] URL (e.g., https://webhook.site/unique-id)
  - [ ] Secret (optional, for HMAC)
  - [ ] Event triggers (workflow, command, etc.)
- [ ] Webhook endpoint created
- [ ] Response includes endpoint ID

#### 4.2 Test Webhook
- [ ] Use API endpoint: `POST /api/v1/integrations-external/webhooks/{id}/test/`
- [ ] Provide test payload
- [ ] Webhook delivered to URL
- [ ] Delivery history shows success
- [ ] Response includes delivery ID

#### 4.3 View Delivery History
- [ ] Use API endpoint: `GET /api/v1/integrations-external/webhooks/{id}/deliveries/`
- [ ] Delivery history returned
- [ ] Shows status, timestamp, response
- [ ] Failed deliveries show error messages

#### 4.4 Webhook Retry Logic
- [ ] Create webhook pointing to server that returns 500 error
- [ ] Trigger webhook
- [ ] First attempt fails
- [ ] Retry attempts made (if configured)
- [ ] Delivery history shows all attempts
- [ ] Exponential backoff timing verified

#### 4.5 HMAC Signature Verification
- [ ] Create webhook with secret
- [ ] Trigger webhook
- [ ] Request includes `X-HishamOS-Signature` header
- [ ] Signature format: `sha256=<hexdigest>`
- [ ] Signature can be verified using secret

---

## 🔔 Automatic Notifications Testing

### 5. Workflow Completion Notifications

#### 5.1 Setup
- [ ] Configure Slack integration with `notify_workflow_completion=True`
- [ ] Configure Email settings with `notify_workflow_completion=True`
- [ ] Configure Webhook with `trigger_on_workflow_completion=True`
- [ ] Execute a workflow that completes successfully

#### 5.2 Expected Results
- [ ] Slack message received in channel
- [ ] Email notification received
- [ ] Webhook delivered to endpoint
- [ ] All notifications include:
  - [ ] Workflow name
  - [ ] Status (completed/failed)
  - [ ] Execution ID
  - [ ] Timestamp

#### 5.3 Failed Workflow
- [ ] Execute workflow that fails
- [ ] Notifications sent with failure status
- [ ] Error message included in notifications

---

### 6. Command Execution Notifications (NEW - Dec 2024)

#### 6.1 Setup
- [ ] Configure Slack integration with `notify_command_execution=True`
- [ ] Configure Email settings with `notify_command_execution=True`
- [ ] Configure Webhook with `trigger_on_command_execution=True`
- [ ] Execute a command via `/api/v1/commands/templates/{id}/execute/`

#### 6.2 Expected Results - Success
- [ ] Slack message received: "✅ Command *name* executed: success"
- [ ] Email notification received with command details
- [ ] Webhook delivered with event type `command.executed`
- [ ] Payload includes:
  - [ ] `command_id`
  - [ ] `command_name`
  - [ ] `status: "success"`
  - [ ] `execution_time`
  - [ ] `cost`
  - [ ] `result_summary`
  - [ ] `timestamp`

#### 6.3 Expected Results - Failure
- [ ] Execute command that fails (invalid parameters, timeout, etc.)
- [ ] Slack message received: "❌ Command *name* executed: failed"
- [ ] Email notification received with error details
- [ ] Webhook delivered with `status: "failed"`
- [ ] Payload includes `error` field with error message

#### 6.4 Notification Preferences
- [ ] Disable `notify_command_execution` in Slack
- [ ] Execute command
- [ ] No Slack notification sent
- [ ] Email and webhook still sent (if enabled)

---

## 🔒 Security Testing

### 7. Access Control

#### 7.1 User Isolation
- [ ] User A creates GitHub integration
- [ ] User B cannot see User A's integration
- [ ] User B cannot update/delete User A's integration
- [ ] Admin can see all integrations

#### 7.2 API Key Protection
- [ ] API keys/tokens not returned in GET responses
- [ ] API keys marked as write-only in serializers
- [ ] Admin interface shows encryption status (if implemented)

#### 7.3 Webhook Secret Protection
- [ ] Webhook secrets not returned in GET responses
- [ ] Secrets marked as write-only in serializers

---

## 🐛 Error Handling Testing

### 8. Error Scenarios

#### 8.1 Invalid GitHub Token
- [ ] Create GitHub integration with invalid token
- [ ] Verify connection fails
- [ ] Error message is clear and helpful

#### 8.2 Invalid Slack Channel
- [ ] Create Slack integration with invalid channel_id
- [ ] Send test message fails
- [ ] Error message indicates channel issue

#### 8.3 Webhook Delivery Failure
- [ ] Create webhook pointing to invalid URL
- [ ] Trigger webhook
- [ ] Delivery fails gracefully
- [ ] Error logged in delivery history
- [ ] Retry attempts made (if configured)

#### 8.4 Network Timeout
- [ ] Create webhook pointing to slow server
- [ ] Trigger webhook
- [ ] Timeout handled correctly
- [ ] Error message indicates timeout

---

## 🔄 Integration Testing

### 9. End-to-End Workflows

#### 9.1 Complete Workflow with Notifications
- [ ] Create workflow
- [ ] Configure all notification types (Slack, Email, Webhook)
- [ ] Execute workflow
- [ ] Workflow completes
- [ ] All notifications received:
  - [ ] Slack message
  - [ ] Email notification
  - [ ] Webhook delivery
- [ ] All notifications contain correct information

#### 9.2 Complete Command Execution with Notifications
- [ ] Select a command template
- [ ] Configure all notification types
- [ ] Execute command with valid parameters
- [ ] Command executes successfully
- [ ] All notifications received:
  - [ ] Slack message
  - [ ] Email notification
  - [ ] Webhook delivery
- [ ] All notifications contain command execution details

---

## ✅ Final Verification

### 10. Complete Workflows

#### 10.1 GitHub Integration Workflow
- [ ] Create GitHub integration
- [ ] Verify connection
- [ ] Create issue from user story
- [ ] Sync pull requests
- [ ] All operations work correctly

#### 10.2 Slack Integration Workflow
- [ ] Create Slack integration
- [ ] Verify connection
- [ ] Send test message
- [ ] Receive workflow notification
- [ ] Receive command notification
- [ ] All operations work correctly

#### 10.3 Email Notifications Workflow
- [ ] Configure email settings
- [ ] Send test email
- [ ] Receive workflow notification
- [ ] Receive command notification
- [ ] All operations work correctly

#### 10.4 Webhook System Workflow
- [ ] Create webhook endpoint
- [ ] Test webhook delivery
- [ ] Receive workflow event
- [ ] Receive command event
- [ ] Verify HMAC signature
- [ ] Check delivery history
- [ ] All operations work correctly

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

- [ ] All GitHub integration tests passed
- [ ] All Slack integration tests passed
- [ ] All Email notification tests passed
- [ ] All Webhook system tests passed
- [ ] Workflow completion notifications working
- [ ] Command execution notifications working (Dec 2024)
- [ ] All error cases handled gracefully
- [ ] Security tests passed
- [ ] Complete workflows tested

**Tester Signature:** _______________  
**Date:** _______________

