---
title: "HishamOS - Documentation Index"
description: "**Last Updated:** December 6, 2024"

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
    - Development

tags:
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

# HishamOS - Documentation Index

**Last Updated:** December 6, 2024

---

## Core Documentation

### Tracking, Logging & Audit
- **[Tracking, Logging, and Audit Documentation](07_TRACKING/TRACKING_LOGGING_AUDIT.md)**
  - System architecture for logging
  - Audit trail implementation
  - Monitoring and tracking
  - Known issues (including WebSocket connection issues)
  - Best practices and troubleshooting

### Testing Documentation
- **[User Acceptance Testing (UAT)](../03_TESTING/UAT_USER_ACCEPTANCE_TESTING.md)**
  - UAT process and procedures
  - Test scenarios for all features
  - Defect reporting templates
  - Sign-off criteria

- **[User Journey Guide](../03_TESTING/USER_JOURNEY_GUIDE.md)**
  - Step-by-step user journeys
  - Agent, Chat, Workflow, Command journeys
  - Project management journeys
  - Dashboard journeys
  - Best practices and troubleshooting

---

## Known Issues Documentation

### WebSocket Connection Issues
**Location:** [TRACKING_LOGGING_AUDIT.md](./TRACKING_LOGGING_AUDIT.md#websocket-connection-issues)  
**Issue ID:** WS-001  
**Status:** Under Investigation  
**Severity:** Medium

**Summary:**
WebSocket connections for workflow execution updates are being established successfully on the backend, but connections are closing immediately after the initial message is sent. The frontend reports "WebSocket is closed before the connection is established."

**Affected Components:**
- `backend/apps/workflows/consumers.py`
- `frontend/src/hooks/useWorkflowWebSocket.ts`
- `backend/apps/workflows/routing.py`

**Next Steps:**
1. Add detailed logging for connection lifecycle
2. Monitor connection close codes
3. Test with different execution states
4. Check for race conditions
5. Verify frontend WebSocket event handlers

---

## Quick Links

### For Developers
- [Master Development Guide](../05_DEVELOPMENT/MASTER_DEVELOPMENT_GUIDE.md)
- [Technical Architecture](../06_PLANNING/TECHNICAL_ARCHITECTURE.md)
- [Implementation Plan](../06_PLANNING/PROJECT_PLANS/PROJECT_PLAN.md)

### For Testers
- [UAT Documentation](../03_TESTING/UAT_USER_ACCEPTANCE_TESTING.md)
- [Manual Testing Checklists](../03_TESTING/manual_test_checklist/)
- [User Journey Guide](../03_TESTING/USER_JOURNEY_GUIDE.md)

### For Users
- [User Journey Guide](../03_TESTING/USER_JOURNEY_GUIDE.md)
- [Project Management Guide](../PROJECT_MANAGEMENT_USER_GUIDE.md)
- [Walkthrough](../WALKTHROUGH.md)

### For Administrators
- [Admin User Management](../ADMIN_USER_MANAGEMENT.md)
- [Deployment Guide](../04_DEPLOYMENT/PRODUCTION_DEPLOYMENT_GUIDE.md)
- [System Settings](../03_TESTING/SYSTEM_SETTINGS_UI_IMPLEMENTATION.md)

---

**Last Updated:** December 6, 2024

