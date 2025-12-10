# Test Checklist: Integrations Features

**Category:** Integrations  
**Features:** GitHub, Jira, Slack, Webhooks  
**Estimated Tests:** ~70  
**Priority:** LOW

---

## 1. GITHUB INTEGRATION

### 1.1 GitHub Setup

**TC-GH-001: Create GitHub Integration**
- [ ] **Test Case:** Configure GitHub integration
- [ ] **Endpoint:** `POST /api/projects/{project_id}/github-integrations/`
- [ ] **Request Body:**
  ```json
  {
    "repository_url": "https://github.com/user/repo",
    "access_token": "token",
    "webhook_secret": "secret"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Integration created
  - Webhook configured in GitHub
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-GH-002: Verify GitHub Connection**
- [ ] **Test Case:** Test GitHub connection
- [ ] **Endpoint:** `POST /api/projects/{project_id}/github-integrations/{integration_id}/verify/`
- [ ] **Expected Result:** 
  - Connection verified
  - Returns repository info
  - Status: connected
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-GH-003: List GitHub Integrations**
- [ ] **Test Case:** Get GitHub integrations
- [ ] **Endpoint:** `GET /api/projects/{project_id}/github-integrations/`
- [ ] **Expected Result:** 
  - Returns integrations for project
  - Includes repository info
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-GH-004: Get GitHub Issues**
- [ ] **Test Case:** Fetch issues from GitHub
- [ ] **Endpoint:** `GET /api/projects/{project_id}/github-integrations/{integration_id}/issues/`
- [ ] **Expected Result:** 
  - Returns GitHub issues
  - Can sync to stories
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-GH-005: Sync GitHub Issue to Story**
- [ ] **Test Case:** Create story from GitHub issue
- [ ] **Endpoint:** `POST /api/projects/{project_id}/github-integrations/{integration_id}/sync-issue/`
- [ ] **Request Body:** `{"issue_number": 123}`
- [ ] **Expected Result:** 
  - Story created from issue
  - Linked to GitHub issue
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-GH-006: GitHub Webhook Handler**
- [ ] **Test Case:** Handle GitHub webhook events
- [ ] **Endpoint:** `POST /api/webhooks/github/`
- [ ] **Request:** GitHub webhook payload
- [ ] **Expected Result:** 
  - Webhook processed
  - Story updated if linked
  - Events logged
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-GH-007: GitHub Integration UI**
- [ ] **Test Case:** Manage GitHub integration via UI
- [ ] **Page:** Project settings > Integrations
- [ ] **Steps:**
  1. Add GitHub integration
  2. Configure repository
  3. Test connection
  4. View synced issues
- [ ] **Expected Result:** 
  - Integration management works
  - Connection test works
  - Issues can be synced
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. JIRA INTEGRATION

### 2.1 Jira Setup

**TC-JIRA-001: Create Jira Integration**
- [ ] **Test Case:** Configure Jira integration
- [ ] **Endpoint:** `POST /api/projects/{project_id}/jira-integrations/`
- [ ] **Request Body:**
  ```json
  {
    "jira_url": "https://company.atlassian.net",
    "username": "user@example.com",
    "api_token": "token",
    "project_key": "PROJ"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Integration created
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-JIRA-002: Verify Jira Connection**
- [ ] **Test Case:** Test Jira connection
- [ ] **Endpoint:** `POST /api/projects/{project_id}/jira-integrations/{integration_id}/verify/`
- [ ] **Expected Result:** 
  - Connection verified
  - Returns project info
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-JIRA-003: Get Jira Issues**
- [ ] **Test Case:** Fetch issues from Jira
- [ ] **Endpoint:** `GET /api/projects/{project_id}/jira-integrations/{integration_id}/issues/`
- [ ] **Expected Result:** 
  - Returns Jira issues
  - Can sync to stories
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-JIRA-004: Sync Jira Issue to Story**
- [ ] **Test Case:** Create story from Jira issue
- [ ] **Endpoint:** `POST /api/projects/{project_id}/jira-integrations/{integration_id}/sync-issue/`
- [ ] **Request Body:** `{"issue_key": "PROJ-123"}`
- [ ] **Expected Result:** 
  - Story created from Jira issue
  - Linked to Jira issue
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-JIRA-005: Jira Integration UI**
- [ ] **Test Case:** Manage Jira integration via UI
- [ ] **Page:** Project settings > Integrations
- [ ] **Steps:**
  1. Add Jira integration
  2. Configure connection
  3. Test connection
  4. Sync issues
- [ ] **Expected Result:** 
  - Integration management works
  - Field mapping works
  - Issues can be synced
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. SLACK INTEGRATION

### 3.1 Slack Setup

**TC-SLACK-001: Create Slack Integration**
- [ ] **Test Case:** Configure Slack integration
- [ ] **Endpoint:** `POST /api/projects/{project_id}/slack-integrations/`
- [ ] **Request Body:**
  ```json
  {
    "webhook_url": "https://hooks.slack.com/services/...",
    "channel": "#project-updates"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Integration created
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SLACK-002: Verify Slack Webhook**
- [ ] **Test Case:** Test Slack webhook
- [ ] **Endpoint:** `POST /api/projects/{project_id}/slack-integrations/{integration_id}/test/`
- [ ] **Expected Result:** 
  - Test message sent to Slack
  - Returns success status
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SLACK-003: Send Slack Notification**
- [ ] **Test Case:** Send notification to Slack
- [ ] **Steps:**
  1. Configure Slack integration
  2. Trigger notification event (e.g., story status change)
- [ ] **Expected Result:** 
  - Notification sent to Slack
  - Message formatted correctly
  - Includes story details
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-SLACK-004: Slack Integration UI**
- [ ] **Test Case:** Manage Slack integration via UI
- [ ] **Page:** Project settings > Integrations
- [ ] **Steps:**
  1. Add Slack integration
  2. Configure webhook
  3. Test webhook
  4. Configure notification events
- [ ] **Expected Result:** 
  - Integration management works
  - Webhook test works
  - Event configuration works
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. WEBHOOKS

### 4.1 Webhook Management

**TC-WH-001: Create Webhook**
- [ ] **Test Case:** Create webhook
- [ ] **Endpoint:** `POST /api/projects/{project_id}/webhooks/`
- [ ] **Request Body:**
  ```json
  {
    "url": "https://example.com/webhook",
    "events": ["story.created", "story.updated"],
    "secret": "webhook-secret"
  }
  ```
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Webhook created
  - Events configured
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WH-002: List Webhooks**
- [ ] **Test Case:** Get webhooks
- [ ] **Endpoint:** `GET /api/projects/{project_id}/webhooks/`
- [ ] **Expected Result:** 
  - Returns webhooks for project
  - Includes events and status
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WH-003: Update Webhook**
- [ ] **Test Case:** Modify webhook
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/webhooks/{webhook_id}/`
- [ ] **Request Body:** `{"events": ["story.created"]}`
- [ ] **Expected Result:** 
  - Webhook updated
  - Events updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WH-004: Delete Webhook**
- [ ] **Test Case:** Remove webhook
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/webhooks/{webhook_id}/`
- [ ] **Expected Result:** 
  - Webhook deleted
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WH-005: Test Webhook**
- [ ] **Test Case:** Send test webhook
- [ ] **Endpoint:** `POST /api/projects/{project_id}/webhooks/{webhook_id}/test/`
- [ ] **Expected Result:** 
  - Test payload sent
  - Returns delivery status
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WH-006: Webhook Delivery**
- [ ] **Test Case:** Webhook sent on event
- [ ] **Steps:**
  1. Create webhook with event "story.created"
  2. Create new story
- [ ] **Expected Result:** 
  - Webhook payload sent to URL
  - Payload includes story data
  - Delivery logged
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WH-007: Webhook Retry**
- [ ] **Test Case:** Webhook retries on failure
- [ ] **Steps:**
  1. Configure webhook with invalid URL
  2. Trigger event
- [ ] **Expected Result:** 
  - Webhook retries (up to N times)
  - Failure logged
  - Status updated to failed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WH-008: Webhook Security**
- [ ] **Test Case:** Webhook signature verification
- [ ] **Steps:**
  1. Create webhook with secret
  2. Send webhook payload
- [ ] **Expected Result:** 
  - Payload includes signature
  - Signature can be verified
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-WH-009: Webhook UI**
- [ ] **Test Case:** Manage webhooks via UI
- [ ] **Page:** Project settings > Webhooks
- [ ] **Steps:**
  1. Create webhook
  2. Configure events
  3. Test webhook
  4. View delivery logs
- [ ] **Expected Result:** 
  - Webhook management works
  - Event selection works
  - Test function works
  - Delivery logs visible
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. INTEGRATION EVENTS

### 5.1 Event Handling

**TC-EVT-001: Story Created Event**
- [ ] **Test Case:** Webhook fires on story creation
- [ ] **Steps:**
  1. Configure webhook for "story.created"
  2. Create story
- [ ] **Expected Result:** 
  - Webhook payload sent
  - Payload includes story data
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-EVT-002: Story Updated Event**
- [ ] **Test Case:** Webhook fires on story update
- [ ] **Steps:**
  1. Configure webhook for "story.updated"
  2. Update story
- [ ] **Expected Result:** 
  - Webhook payload sent
  - Payload includes changes
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-EVT-003: Story Status Change Event**
- [ ] **Test Case:** Webhook fires on status change
- [ ] **Steps:**
  1. Configure webhook for "story.status_changed"
  2. Change story status
- [ ] **Expected Result:** 
  - Webhook payload sent
  - Payload includes old and new status
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - Integrations Features  
**Total Test Cases:** ~70  
**Next File:** [10_test_checklist_ui_features.md](./10_test_checklist_ui_features.md)

