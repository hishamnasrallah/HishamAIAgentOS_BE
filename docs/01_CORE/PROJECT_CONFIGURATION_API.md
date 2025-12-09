---
title: "Project Configuration API Documentation"
description: "Comprehensive API documentation for Project Configuration management in HishamOS. Covers all 11 configuration categories, endpoints, and usage examples."

category: "Core"
subcategory: "API"
language: "en"
original_language: "en"

purpose: |
  This document provides complete API reference for Project Configuration endpoints. It covers all 11 configuration categories including workflow states, story points, sprint settings, board customization, automation rules, notifications, permissions, integrations, custom fields, validation rules, and analytics.

target_audience:
  primary:
    - Developer
    - Technical Writer
  secondary:
    - QA / Tester
    - CTO / Technical Lead
    - Business Analyst

applicable_phases:
  primary:
    - Development
    - Testing
  secondary:
    - Production

tags:
  - project-configuration
  - api
  - documentation
  - reference
  - projects
  - configuration
  - workflow
  - story-points
  - sprint
  - board
  - automation
  - notifications
  - permissions
  - integrations

keywords:
  - "project configuration"
  - "project settings"
  - "workflow states"
  - "story points"
  - "sprint configuration"
  - "board customization"

related_features:
  - "Project Management"
  - "Workflow Management"
  - "Sprint Planning"
  - "Board Customization"

prerequisites:
  documents:
    - 01_CORE/USER_GUIDES/WALKTHROUGH.md
  knowledge:
    - "REST API basics"
    - "Django REST Framework"
  tools:
    - "Postman/Insomnia (optional)"

status: "active"
priority: "high"
difficulty: "intermediate"
completeness: "100%"
quality_status: "reviewed"

estimated_read_time: "30 minutes"
estimated_usage_time: "Ongoing reference"
estimated_update_time: "1 hour"

version: "1.0"
last_updated: "2024-12-08"
last_reviewed: "2024-12-08"
review_frequency: "monthly"
next_review_date: "2025-01-08"

author: "Development Team"
maintainer: "Developer"
reviewer: "Technical Lead"

related:
  - 06_PLANNING/PROJECT_MANAGEMENT_ENHANCEMENTS_DISCUSSION.md
  - 01_CORE/USER_GUIDE.md
see_also:
  - 01_CORE/SYSTEM_SETTINGS_API.md
depends_on:
  - 01_CORE/USER_GUIDES/WALKTHROUGH.md
prerequisite_for:
  - 03_TESTING/MANUAL_TEST_CHECKLISTS/PROJECT_CONFIGURATION_TEST_CHECKLIST.md

aliases:
  - "Project Settings API"
  - "Project Config API"
  - "Configuration API"

changelog:
  - version: "1.0"
    date: "2024-12-08"
    changes: "Initial version - Complete API documentation for Project Configuration"
    author: "Development Team"
---

# Project Configuration API Documentation

**Last Updated:** December 8, 2024  
**Base URL:** `/api/v1/projects/configurations/`  
**Authentication:** Required (JWT Token)

---

## 📋 Overview

The Project Configuration API allows project owners and administrators to manage project-specific settings. Each project has a one-to-one relationship with a configuration that controls:

1. **Workflow & Board Configuration** - Custom states, transitions, board columns
2. **Story Point Configuration** - Scale, limits, validation
3. **Sprint Configuration** - Duration, start day, auto-close settings
4. **Board Customization** - View type, swimlanes, card display
5. **Workflow Automation Rules** - Auto-assign, auto-status changes
6. **Notification Configuration** - Event-based notifications
7. **Permission Configuration** - Role-based permission overrides
8. **Integration Configuration** - GitHub, Jira, Slack settings
9. **Custom Fields Schema** - Project-specific custom fields
10. **Validation Rules** - Story/task validation rules
11. **Analytics Configuration** - Reporting preferences

---

## 🔐 Authentication & Permissions

### Required Authentication
- All endpoints require JWT authentication
- Include token in `Authorization: Bearer <token>` header

### Permission Levels

| Action | Permission Required |
|--------|---------------------|
| View Configuration | Project Member or Owner |
| Create Configuration | Project Owner or Admin (auto-created) |
| Update Configuration | Project Owner or Admin |
| Delete Configuration | Project Owner or Admin |
| Reset to Defaults | Project Owner or Admin |

---

## 📡 API Endpoints

### Get Configuration by Project ID

```http
GET /api/v1/projects/configurations/{project_id}/
```

**Description:** Retrieve configuration for a specific project. The `project_id` is used as the lookup key.

**Parameters:**
- `project_id` (path, required) - UUID of the project

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "project": "project-uuid",
  "custom_states": [
    {
      "id": "state_1",
      "name": "Backlog",
      "order": 0,
      "color": "#gray",
      "is_default": true,
      "is_final": false,
      "wip_limit": null,
      "auto_transitions": []
    }
  ],
  "state_transitions": {
    "state_1": ["state_2", "state_3"]
  },
  "board_columns": [],
  "max_story_points_per_story": 21,
  "min_story_points_per_story": 1,
  "story_point_scale": [1, 2, 3, 5, 8, 13, 21],
  "max_story_points_per_sprint": 40,
  "story_points_required": false,
  "default_sprint_duration_days": 14,
  "sprint_start_day": 0,
  "auto_close_sprints": false,
  "allow_overcommitment": false,
  "default_board_view": "kanban",
  "swimlane_grouping": "none",
  "swimlane_custom_field": null,
  "card_display_fields": [],
  "card_color_by": "priority",
  "automation_rules": [],
  "notification_settings": {},
  "permission_settings": {},
  "integration_settings": {},
  "custom_fields_schema": [],
  "validation_rules": {},
  "analytics_settings": {},
  "created_at": "2024-12-08T10:00:00Z",
  "updated_at": "2024-12-08T10:00:00Z",
  "updated_by": "user-uuid"
}
```

**Error Responses:**
- `404 Not Found` - Configuration not found for project
- `403 Forbidden` - User doesn't have access to project
- `401 Unauthorized` - Authentication required

---

### Update Configuration

```http
PATCH /api/v1/projects/configurations/{project_id}/
Content-Type: application/json
```

**Description:** Partially update project configuration. Only provided fields will be updated.

**Parameters:**
- `project_id` (path, required) - UUID of the project

**Request Body:**
```json
{
  "max_story_points_per_story": 34,
  "story_point_scale": [1, 2, 3, 5, 8, 13, 21, 34],
  "default_sprint_duration_days": 21,
  "auto_close_sprints": true,
  "custom_states": [
    {
      "id": "state_1",
      "name": "Backlog",
      "order": 0,
      "color": "#blue",
      "is_default": true,
      "is_final": false,
      "wip_limit": 10,
      "auto_transitions": ["state_2"]
    }
  ]
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "project": "project-uuid",
  "max_story_points_per_story": 34,
  "story_point_scale": [1, 2, 3, 5, 8, 13, 21, 34],
  "default_sprint_duration_days": 21,
  "auto_close_sprints": true,
  "updated_at": "2024-12-08T10:30:00Z",
  "updated_by": "user-uuid"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid data format
- `403 Forbidden` - User doesn't have permission to update
- `404 Not Found` - Configuration not found

---

### Reset Configuration to Defaults

```http
POST /api/v1/projects/configurations/{project_id}/reset-to-defaults/
```

**Description:** Reset all configuration values to their defaults. This action cannot be undone.

**Parameters:**
- `project_id` (path, required) - UUID of the project

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "project": "project-uuid",
  "message": "Configuration reset to defaults",
  "configuration": {
    // Full configuration object with default values
  }
}
```

**Error Responses:**
- `403 Forbidden` - Only project owners and admins can reset
- `404 Not Found` - Configuration not found

---

## 📊 Configuration Schema

### Workflow States (`custom_states`)

Array of custom workflow states (board columns):

```json
{
  "id": "string (unique identifier)",
  "name": "string (display name)",
  "order": "integer (display order)",
  "color": "string (hex color code)",
  "is_default": "boolean (initial state for new stories)",
  "is_final": "boolean (final/completed state)",
  "wip_limit": "integer | null (work-in-progress limit)",
  "auto_transitions": ["array of state IDs to auto-transition to"]
}
```

**Example:**
```json
[
  {
    "id": "backlog",
    "name": "Backlog",
    "order": 0,
    "color": "#gray",
    "is_default": true,
    "is_final": false,
    "wip_limit": null,
    "auto_transitions": []
  },
  {
    "id": "in_progress",
    "name": "In Progress",
    "order": 2,
    "color": "#blue",
    "is_default": false,
    "is_final": false,
    "wip_limit": 5,
    "auto_transitions": ["review"]
  }
]
```

---

### Story Point Scale (`story_point_scale`)

Array of allowed story point values:

```json
[1, 2, 3, 5, 8, 13, 21]
```

**Common Scales:**
- **Fibonacci:** `[1, 2, 3, 5, 8, 13, 21]`
- **Powers of 2:** `[1, 2, 4, 8, 16]`
- **T-Shirt Sizes:** `[1, 2, 3, 5, 8]` (mapped to XS, S, M, L, XL)

---

### Automation Rules (`automation_rules`)

Array of automation rule objects:

```json
[
  {
    "id": "rule_1",
    "name": "Auto-assign to creator",
    "trigger": "on_story_create",
    "condition": {
      "field": "assigned_to",
      "operator": "is_null"
    },
    "action": {
      "type": "assign",
      "value": "creator"
    },
    "enabled": true
  }
]
```

**Trigger Types:**
- `on_story_create`
- `on_story_update`
- `on_status_change`
- `on_all_tasks_complete`
- `on_due_date_approaching`

---

### Notification Settings (`notification_settings`)

Object mapping event names to notification preferences:

```json
{
  "on_story_created": {
    "enabled": true,
    "recipients": ["assignee", "watchers"],
    "channels": ["email", "in_app"]
  },
  "on_status_change": {
    "enabled": true,
    "recipients": ["assignee"],
    "channels": ["in_app"]
  },
  "digest_frequency": "daily"
}
```

**Event Types:**
- `on_story_created`
- `on_story_updated`
- `on_status_change`
- `on_comment`
- `on_mention`
- `on_due_date_approaching`
- `on_sprint_start`
- `on_sprint_end`

---

### Integration Settings (`integration_settings`)

Object mapping integration names to configuration:

```json
{
  "github": {
    "enabled": true,
    "repository": "org/repo",
    "auto_link_prs": true,
    "webhook_secret": "secret-key"
  },
  "jira": {
    "enabled": true,
    "project_key": "PROJ",
    "server_url": "https://jira.example.com"
  },
  "slack": {
    "enabled": true,
    "channel": "#project-updates",
    "webhook_url": "https://hooks.slack.com/..."
  }
}
```

---

### Custom Fields Schema (`custom_fields_schema`)

Array of custom field definitions:

```json
[
  {
    "id": "field_1",
    "name": "Component",
    "type": "select",
    "required": false,
    "options": ["Frontend", "Backend", "Mobile"],
    "default_value": null
  },
  {
    "id": "field_2",
    "name": "Release Date",
    "type": "date",
    "required": true,
    "default_value": null
  }
]
```

**Field Types:**
- `text` - Single-line text
- `textarea` - Multi-line text
- `number` - Numeric value
- `date` - Date picker
- `select` - Single selection dropdown
- `multi_select` - Multiple selection
- `checkbox` - Boolean checkbox

---

### Validation Rules (`validation_rules`)

Object mapping rule names to boolean values:

```json
{
  "require_acceptance_criteria": true,
  "require_story_points_before_in_progress": true,
  "require_assignee_before_in_progress": true,
  "block_status_change_if_tasks_incomplete": true,
  "warn_if_story_points_exceed_sprint_capacity": true,
  "require_description_min_length": 50
}
```

---

## 🔄 Auto-Creation

When a new project is created, a default configuration is automatically created via Django signals. The default configuration includes:

- Default workflow states: Backlog, To Do, In Progress, Review, Done
- Fibonacci story point scale: [1, 2, 3, 5, 8, 13, 21]
- 14-day sprint duration
- Monday sprint start day
- Kanban board view
- Empty automation rules, notifications, integrations, custom fields

---

## 📝 Usage Examples

### Example 1: Update Story Point Configuration

```bash
curl -X PATCH \
  https://api.hishamos.com/api/v1/projects/configurations/{project_id}/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "max_story_points_per_story": 34,
    "story_point_scale": [1, 2, 3, 5, 8, 13, 21, 34],
    "max_story_points_per_sprint": 50
  }'
```

### Example 2: Add Custom Workflow State

```bash
curl -X PATCH \
  https://api.hishamos.com/api/v1/projects/configurations/{project_id}/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_states": [
      {
        "id": "backlog",
        "name": "Backlog",
        "order": 0,
        "color": "#gray",
        "is_default": true,
        "is_final": false,
        "wip_limit": null,
        "auto_transitions": []
      },
      {
        "id": "qa",
        "name": "QA Testing",
        "order": 3,
        "color": "#purple",
        "is_default": false,
        "is_final": false,
        "wip_limit": 3,
        "auto_transitions": ["done"]
      }
    ]
  }'
```

### Example 3: Configure Sprint Settings

```bash
curl -X PATCH \
  https://api.hishamos.com/api/v1/projects/configurations/{project_id}/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "default_sprint_duration_days": 21,
    "sprint_start_day": 1,
    "auto_close_sprints": true,
    "allow_overcommitment": false
  }'
```

### Example 4: Reset to Defaults

```bash
curl -X POST \
  https://api.hishamos.com/api/v1/projects/configurations/{project_id}/reset-to-defaults/ \
  -H "Authorization: Bearer {token}"
```

---

## ⚠️ Important Notes

1. **One-to-One Relationship:** Each project has exactly one configuration. It's auto-created when the project is created.

2. **Permission Checks:** All update operations verify that the user is either the project owner or an admin.

3. **Validation:** The API validates:
   - Story point scale must contain positive integers
   - Workflow states must have unique IDs
   - State transitions must reference valid state IDs
   - Sprint duration must be between 1-30 days

4. **Default Values:** If a field is not provided, it retains its current value (PATCH behavior).

5. **Reset Action:** Resetting to defaults cannot be undone. All custom configurations will be lost.

---

## 🔗 Related Documentation

- [Project Management Enhancements Discussion](../06_PLANNING/PROJECT_MANAGEMENT_ENHANCEMENTS_DISCUSSION.md)
- [User Guide](./USER_GUIDE.md)
- [System Settings API](./SYSTEM_SETTINGS_API.md)

---

## 📞 Support

For issues or questions:
- Check the [User Guide](./USER_GUIDE.md)
- Review [Project Management Enhancements](../06_PLANNING/PROJECT_MANAGEMENT_ENHANCEMENTS_DISCUSSION.md)
- Contact the development team

---

**Last Updated:** December 8, 2024  
**Version:** 1.0

