---
title: "Phase 21: External Integrations - Expected Output"
description: "Expected outputs, API endpoints, and test scenarios for Phase 21 external integrations"
category: "Tracking"
language: "en"
original_language: "en"
purpose: |
  Document expected outputs, API endpoints, test scenarios, and validation steps for Phase 21 external integrations.
target_audience:
  primary:
    - Developer
    - QA / Tester
  secondary:
    - Project Manager
    - CTO / Technical Lead
applicable_phases:
  primary:
    - Testing
    - Development
  secondary:
    - QA
tags:
  - phase-21
  - expected-output
  - api-endpoints
  - testing
  - external-integrations
  - github
  - slack
  - email
  - webhooks
status: "active"
priority: "high"
difficulty: "intermediate"
completeness: "100%"
version: "1.0"
last_updated: "2024-12-06"
last_reviewed: "2024-12-06"
review_frequency: "monthly"
next_review_date: "2025-01-06"
author: "Development Team"
maintainer: "Development Team"
reviewer: "QA Team"
related: []
see_also:
  - 03_TESTING/MANUAL_TEST_CHECKLISTS/PHASE_17_18_ADMIN_UI_COMPREHENSIVE_TESTING.md
depends_on: []
prerequisite_for: []
changelog:
  - version: "1.0"
    date: "2024-12-06"
    changes: "Initial version - Phase 21 external integrations expected outputs"
    author: "AI Assistant"
---

# Phase 21: External Integrations - Expected Output

**Date:** December 6, 2024  
**Status:** ✅ Complete  
**Phase:** Phase 21

---

## Success Criteria

- [x] GitHub integration works for creating issues and syncing PRs
- [x] Slack notifications work for workflows and commands
- [x] Email notifications work for workflows and commands
- [x] Webhook system delivers events with retry logic
- [x] All API endpoints respond correctly
- [x] Signal handlers trigger notifications automatically
- [x] Command execution signals trigger notifications (Dec 2024)

---

## API Endpoints

### GitHub Integration

| Method | Endpoint | Description | Request Body | Expected Response | Auth Required |
|--------|----------|-------------|--------------|-------------------|--------------|
| GET | `/api/v1/integrations-external/github/` | List GitHub integrations | - | `[{...}]` | Authenticated |
| POST | `/api/v1/integrations-external/github/` | Create GitHub integration | `{"repository_owner": "...", "repository_name": "...", "access_token": "..."}` | `{...}` | Authenticated |
| GET | `/api/v1/integrations-external/github/{id}/` | Get GitHub integration | - | `{...}` | Owner/Admin |
| PUT | `/api/v1/integrations-external/github/{id}/` | Update GitHub integration | `{...}` | `{...}` | Owner/Admin |
| DELETE | `/api/v1/integrations-external/github/{id}/` | Delete GitHub integration | - | `204 No Content` | Owner/Admin |
| POST | `/api/v1/integrations-external/github/{id}/verify/` | Verify connection | - | `{"status": "success"}` | Owner/Admin |
| POST | `/api/v1/integrations-external/github/{id}/sync-prs/` | Sync pull requests | - | `{"synced": 5}` | Owner/Admin |

### Slack Integration

| Method | Endpoint | Description | Request Body | Expected Response | Auth Required |
|--------|----------|-------------|--------------|-------------------|--------------|
| GET | `/api/v1/integrations-external/slack/` | List Slack integrations | - | `[{...}]` | Authenticated |
| POST | `/api/v1/integrations-external/slack/` | Create Slack integration | `{"workspace_name": "...", "channel_id": "...", "bot_token": "..."}` | `{...}` | Authenticated |
| GET | `/api/v1/integrations-external/slack/{id}/` | Get Slack integration | - | `{...}` | Owner/Admin |
| PUT | `/api/v1/integrations-external/slack/{id}/` | Update Slack integration | `{...}` | `{...}` | Owner/Admin |
| DELETE | `/api/v1/integrations-external/slack/{id}/` | Delete Slack integration | - | `204 No Content` | Owner/Admin |
| POST | `/api/v1/integrations-external/slack/{id}/verify/` | Verify connection | - | `{"status": "success"}` | Owner/Admin |
| POST | `/api/v1/integrations-external/slack/{id}/test-message/` | Send test message | `{"text": "Test"}` | `{"status": "ok"}` | Owner/Admin |

### Email Notifications

| Method | Endpoint | Description | Request Body | Expected Response | Auth Required |
|--------|----------|-------------|--------------|-------------------|--------------|
| GET | `/api/v1/integrations-external/email/` | Get email settings | - | `{...}` | Authenticated |
| PUT | `/api/v1/integrations-external/email/` | Update email settings | `{"notify_workflow_completion": true, ...}` | `{...}` | Authenticated |
| POST | `/api/v1/integrations-external/email/test-email/` | Send test email | - | `{"status": "sent"}` | Authenticated |

### Webhook System

| Method | Endpoint | Description | Request Body | Expected Response | Auth Required |
|--------|----------|-------------|--------------|-------------------|--------------|
| GET | `/api/v1/integrations-external/webhooks/` | List webhook endpoints | - | `[{...}]` | Authenticated |
| POST | `/api/v1/integrations-external/webhooks/` | Create webhook endpoint | `{"name": "...", "url": "...", "secret": "..."}` | `{...}` | Authenticated |
| GET | `/api/v1/integrations-external/webhooks/{id}/` | Get webhook endpoint | - | `{...}` | Owner/Admin |
| PUT | `/api/v1/integrations-external/webhooks/{id}/` | Update webhook endpoint | `{...}` | `{...}` | Owner/Admin |
| DELETE | `/api/v1/integrations-external/webhooks/{id}/` | Delete webhook endpoint | - | `204 No Content` | Owner/Admin |
| POST | `/api/v1/integrations-external/webhooks/{id}/test/` | Test webhook | `{"payload": {...}}` | `{"status": "success", "delivery_id": "..."}` | Owner/Admin |
| GET | `/api/v1/integrations-external/webhooks/{id}/deliveries/` | Get delivery history | - | `[{...}]` | Owner/Admin |

---

## Test Scenarios

### Scenario 1: Workflow Completion Triggers Notifications

**Setup:**
- Configure Slack integration with `notify_workflow_completion=True`
- Configure Email settings with `notify_workflow_completion=True`
- Configure Webhook endpoint with `trigger_on_workflow_completion=True`
- Execute a workflow that completes

**Expected Output:**
- Slack message sent to configured channel
- Email notification sent to user
- Webhook delivered to configured endpoint
- All notifications include workflow name, status, execution ID

**Validation:**
- Check Slack channel for message
- Check email inbox for notification
- Check webhook delivery history for successful delivery
- Verify payload contains correct workflow information

---

### Scenario 2: Command Execution Triggers Notifications (NEW - Dec 2024)

**Setup:**
- Configure Slack integration with `notify_command_execution=True`
- Configure Email settings with `notify_command_execution=True`
- Configure Webhook endpoint with `trigger_on_command_execution=True`
- Execute a command via `/api/v1/commands/templates/{id}/execute/`

**Expected Output:**
- Slack message sent: "✅ Command *command_name* executed: success"
- Email notification sent with command name and status
- Webhook delivered with event type `command.executed`
- All notifications include command ID, name, status, execution time, cost

**Validation:**
- Check Slack channel for message
- Check email inbox for notification
- Check webhook delivery history for successful delivery
- Verify payload contains:
  ```json
  {
    "event": "command.executed",
    "command_id": "uuid",
    "command_name": "Command Name",
    "status": "success",
    "user_id": "uuid",
    "result_summary": "...",
    "execution_time": 2.5,
    "cost": 0.001,
    "error": null,
    "timestamp": "2024-12-06T10:30:00Z"
  }
  ```

---

### Scenario 3: Command Execution Failure Triggers Notifications

**Setup:**
- Configure notifications as in Scenario 2
- Execute a command that fails (invalid parameters, timeout, etc.)

**Expected Output:**
- Slack message sent: "❌ Command *command_name* executed: failed"
- Email notification sent with error details
- Webhook delivered with `status: "failed"` and error message

**Validation:**
- Error information included in all notifications
- Webhook payload includes error field

---

### Scenario 4: Webhook Retry Logic

**Setup:**
- Create webhook endpoint with retry_count=3
- Configure endpoint to point to a server that returns 500 error initially, then 200

**Expected Output:**
- First delivery attempt fails (500 error)
- Second delivery attempt succeeds (200 OK)
- Delivery history shows 2 attempts
- Endpoint statistics updated (success_count incremented)

**Validation:**
- Check delivery history for retry attempts
- Verify exponential backoff timing
- Verify final delivery status is "success"

---

### Scenario 5: Webhook HMAC Signature

**Setup:**
- Create webhook endpoint with secret="test-secret"
- Trigger webhook delivery

**Expected Output:**
- Webhook request includes `X-HishamOS-Signature` header
- Signature format: `sha256=<hexdigest>`
- Signature can be verified using the secret

**Validation:**
- Verify signature header exists
- Verify signature matches expected HMAC-SHA256 value
- Verify signature verification works on receiving end

---

## Error Handling Scenarios

### Error 1: Invalid GitHub Token

**Setup:**
- Create GitHub integration with invalid access_token
- Call verify endpoint

**Expected Output:**
```json
{
  "error": "GitHub API error: Bad credentials"
}
```

**Validation:**
- Error message is clear
- Integration marked as inactive or error logged

---

### Error 2: Slack Channel Not Found

**Setup:**
- Create Slack integration with invalid channel_id
- Send test message

**Expected Output:**
```json
{
  "error": "Slack API error: channel_not_found"
}
```

**Validation:**
- Error message indicates channel issue
- Integration can be updated with correct channel

---

### Error 3: Webhook Delivery Timeout

**Setup:**
- Create webhook endpoint pointing to slow/unresponsive server
- Trigger webhook

**Expected Output:**
- Delivery status: "failed"
- Error message: "Request timeout after Xs"
- Retry attempts made (if configured)
- Final status reflects timeout

**Validation:**
- Timeout handled gracefully
- Retry logic respects timeout
- Delivery history shows timeout errors

---

## Final Checklist

- [x] All GitHub endpoints work correctly
- [x] All Slack endpoints work correctly
- [x] All Email endpoints work correctly
- [x] All Webhook endpoints work correctly
- [x] Workflow completion signals trigger notifications
- [x] Command execution signals trigger notifications (Dec 2024)
- [x] All error cases handled gracefully
- [x] Retry logic works for webhooks
- [x] HMAC signatures generated correctly
- [x] All admin interfaces functional

---

**Status:** ✅ All expected outputs verified  
**Date:** December 6, 2024  
**Last Updated:** December 6, 2024 - Added command execution signal scenarios

---

## Implementation Notes

### Backend Implementation
- All integration models created in `backend/apps/integrations_external/models.py`
- All services implemented with proper error handling
- Signal handlers in `signals.py` for workflow and command execution
- Command execution notifications integrated into `backend/apps/commands/views.py`

### Security Considerations
- API keys and tokens stored (encryption recommended for production)
- Webhook secrets used for HMAC signature generation
- Access control: users can only manage their own integrations
- Admin can view all integrations

### Notification Preferences
- Users can enable/disable notifications per type (workflow, command, system alerts)
- Default: workflow notifications ON, command notifications OFF
- Settings can be updated via API or admin interface

