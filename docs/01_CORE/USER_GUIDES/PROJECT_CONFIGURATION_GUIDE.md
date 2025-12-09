---
title: "Project Configuration User Guide"
description: "Complete user guide for configuring project settings in HishamOS. Covers all 11 configuration categories with step-by-step instructions."

category: "Core"
subcategory: "User Guide"
language: "en"
original_language: "en"

purpose: |
  This guide provides step-by-step instructions for configuring project settings in HishamOS. It covers all 11 configuration categories including workflow states, story points, sprint settings, board customization, automation, notifications, permissions, integrations, custom fields, validation rules, and analytics.

target_audience:
  primary:
    - Project Manager
    - Product Owner
    - Scrum Master
  secondary:
    - Developer
    - Business Analyst
    - Team Lead

applicable_phases:
  primary:
    - Planning
    - Development
  secondary:
    - Testing
    - Production

tags:
  - project-configuration
  - user-guide
  - tutorial
  - workflow
  - story-points
  - sprint
  - board
  - automation
  - settings
  - configuration
  - project-management

keywords:
  - "project settings"
  - "project configuration"
  - "workflow setup"
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
    - "Basic project management concepts"
    - "Agile/Scrum methodology"
  tools:
    - "Web browser"
    - "Access to HishamOS"

status: "active"
priority: "high"
difficulty: "beginner"
completeness: "100%"
quality_status: "reviewed"

estimated_read_time: "45 minutes"
estimated_usage_time: "30-60 minutes per project setup"
estimated_update_time: "1.5 hours"

version: "1.0"
last_updated: "2024-12-08"
last_reviewed: "2024-12-08"
review_frequency: "quarterly"
next_review_date: "2025-03-08"

author: "Development Team"
maintainer: "Documentation Team"
reviewer: "Product Manager"

related:
  - 01_CORE/PROJECT_CONFIGURATION_API.md
  - 06_PLANNING/PROJECT_MANAGEMENT_ENHANCEMENTS_DISCUSSION.md
see_also:
  - 01_CORE/USER_GUIDE.md
depends_on:
  - 01_CORE/USER_GUIDES/WALKTHROUGH.md
prerequisite_for:
  - 03_TESTING/MANUAL_TEST_CHECKLISTS/PROJECT_CONFIGURATION_TEST_CHECKLIST.md

aliases:
  - "Project Settings Guide"
  - "Configuration Guide"
  - "Project Setup Guide"

changelog:
  - version: "1.0"
    date: "2024-12-08"
    changes: "Initial version - Complete user guide for Project Configuration"
    author: "Development Team"
---

# Project Configuration User Guide

**Last Updated:** December 8, 2024  
**Audience:** Project Managers, Product Owners, Scrum Masters

---

## 📋 Overview

Project Configuration allows you to customize how your project works in HishamOS. Each project has its own configuration that controls:

- **Workflow States** - Custom board columns and statuses
- **Story Points** - Scale, limits, and validation
- **Sprint Settings** - Duration, start day, and behavior
- **Board Customization** - View type, swimlanes, and card display
- **Automation Rules** - Auto-assignments and status changes
- **Notifications** - When and how to notify team members
- **Permissions** - Who can do what in the project
- **Integrations** - GitHub, Jira, Slack connections
- **Custom Fields** - Project-specific data fields
- **Validation Rules** - Quality checks for stories and tasks

---

## 🚀 Getting Started

### Accessing Project Settings

1. Navigate to your project detail page
2. Click the **"Settings"** button in the top-right corner
3. You'll see 10 tabs for different configuration categories

### Permissions

- **Project Owners** and **Admins** can modify all settings
- **Project Members** can view settings but cannot modify them

---

## 📑 Configuration Tabs

### 1. Workflow Settings

Configure custom workflow states (board columns) for your project.

#### Adding a New State

1. Click **"+ Add State"**
2. Fill in the details:
   - **Name**: Display name (e.g., "In Progress")
   - **Color**: Click the color picker to choose a color
   - **WIP Limit**: Optional limit on items in this state
   - **Default**: Check if this should be the initial state for new stories
   - **Final**: Check if this is a completed/done state
3. Use ↑↓ arrows to reorder states
4. Click **×** to delete a state

#### State Transitions

Define which states can transition to which other states:

1. For each state, select target states from the dropdown
2. Selected transitions appear as badges
3. Click **×** on a badge to remove a transition

**Example Workflow:**
```
Backlog → To Do → In Progress → Review → Done
```

---

### 2. Story Points

Configure story point estimation and limits.

#### Story Point Scale

Choose or customize your story point scale:

- **Fibonacci** (Recommended): `1, 2, 3, 5, 8, 13, 21`
- **Powers of 2**: `1, 2, 4, 8, 16`
- **Custom**: Enter comma-separated values

**To customize:**
1. Type values separated by commas (e.g., `1, 2, 3, 5, 8, 13, 21, 34`)
2. Or click a preset button to apply a common scale

#### Limits

- **Min Story Points per Story**: Minimum allowed (default: 1)
- **Max Story Points per Story**: Maximum allowed (default: 21)
- **Max Story Points per Sprint**: Total capacity (default: 40)

#### Validation

- **Require Story Points Before In Progress**: When enabled, stories must have story points assigned before moving to "In Progress"

---

### 3. Sprint Settings

Configure sprint duration and behavior.

#### Sprint Duration

- **Default Sprint Duration**: Number of days (1-30, default: 14)
- **Sprint Start Day**: Day of week when sprints typically start (Monday-Sunday)

#### Sprint Behavior

- **Auto-Close Sprints**: Automatically close sprints when end date passes
- **Allow Overcommitment**: Allow sprints to exceed max story points capacity

**Recommendation:** Enable auto-close for better sprint hygiene.

---

### 4. Board Customization

Customize how your board looks and behaves.

#### Board View

Select the default view:
- **Kanban** (Default): Card-based board
- **List**: Simple list view
- **Table**: Spreadsheet-like view
- **Timeline**: Gantt chart view
- **Calendar**: Calendar view

#### Swimlane Grouping

Group cards by:
- **None**: No grouping
- **Assignee**: Group by assigned team member
- **Epic**: Group by epic
- **Priority**: Group by priority level
- **Component**: Group by component
- **Custom Field**: Group by a custom field (requires field name)

#### Card Display

**Card Color By:**
- Priority (default)
- Epic
- Story Type
- Component
- Custom

**Card Display Fields:**
Select which fields to show on cards:
- Title
- Assignee
- Story Points
- Tags
- Due Date
- Priority
- Epic
- Status

---

### 5. Automation Rules

Create rules to automate workflow actions.

#### Creating a Rule

1. Click **"+ Add Rule"**
2. Enter a rule name
3. Configure:
   - **Trigger**: When the rule should fire (e.g., "On Story Create")
   - **Condition**: When condition is met (e.g., "Assignee is null")
   - **Action**: What to do (e.g., "Assign to creator")
4. Toggle **Enabled** to activate/deactivate the rule

**Example Rules:**
- Auto-assign new stories to creator
- Move to "Done" when all tasks are complete
- Notify assignee when status changes to "In Progress"

---

### 6. Notifications

Configure when and how team members are notified.

#### Notification Events

For each event, you can:
- **Enable/Disable**: Toggle notifications on/off
- **Recipients**: Choose who gets notified (Assignee, Watchers, etc.)
- **Channels**: Choose how to notify (Email, In-App, Slack)

**Available Events:**
- On Story Created
- On Story Updated
- On Status Change
- On Comment
- On Mention
- On Due Date Approaching
- On Sprint Start
- On Sprint End

#### Digest Frequency

Choose how often to send notification digests:
- **Immediate**: Send right away
- **Hourly**: Batch hourly
- **Daily**: Daily summary
- **Weekly**: Weekly summary

---

### 7. Permissions

Override default permissions for this project.

#### Who Can...

- **Create Stories**: Members or Admins Only
- **Edit Stories**: Members or Admins Only
- **Delete Stories**: Members or Admins Only

**Note:** These settings override system-wide permissions for this project only.

---

### 8. Integrations

Connect external tools to your project.

#### GitHub Integration

1. Toggle **Enable GitHub Integration**
2. Enter **Repository** (format: `org/repo`)
3. Enable **Auto-link Pull Requests** to automatically link PRs to stories

#### Jira Integration

1. Toggle **Enable Jira Integration**
2. Enter **Project Key** (e.g., `PROJ`)

#### Slack Integration

1. Toggle **Enable Slack Integration**
2. Enter **Channel** (e.g., `#project-updates`)
3. Configure webhook URL (if needed)

---

### 9. Custom Fields

Define project-specific fields for stories.

#### Adding a Custom Field

1. Click **"+ Add Custom Field"**
2. Configure:
   - **Name**: Field name (e.g., "Component")
   - **Type**: Text, Number, Date, Select, Multi-Select, Checkbox
   - **Required**: Whether field is mandatory
   - **Options**: For Select/Multi-Select, enter options
3. Click **Delete** to remove a field

**Field Types:**
- **Text**: Single-line text input
- **Number**: Numeric value
- **Date**: Date picker
- **Select**: Dropdown (single choice)
- **Multi-Select**: Dropdown (multiple choices)
- **Checkbox**: Boolean checkbox

---

### 10. Validation Rules

Set quality checks for stories and tasks.

#### Available Rules

- **Require Acceptance Criteria**: Stories must have acceptance criteria
- **Require Story Points Before In Progress**: Must estimate before starting
- **Require Assignee Before In Progress**: Must assign before starting
- **Block Status Change If Tasks Incomplete**: Can't mark done if tasks incomplete
- **Warn If Story Points Exceed Sprint Capacity**: Alert if overcommitted

Toggle each rule on/off as needed.

---

## 💾 Saving Changes

### Save Button

- Click **"Save Changes"** to save all modifications
- You'll see a confirmation message when saved
- Unsaved changes are indicated by an orange badge

### Reset to Defaults

- Click **"Reset to Defaults"** to restore all settings
- **Warning:** This action cannot be undone
- All custom configurations will be lost

---

## 🎯 Best Practices

### Workflow States

1. **Keep it Simple**: Start with 4-5 states, add more as needed
2. **Clear Names**: Use clear, unambiguous state names
3. **WIP Limits**: Set WIP limits to prevent bottlenecks
4. **Color Coding**: Use consistent colors across projects

### Story Points

1. **Consistent Scale**: Use the same scale across all projects
2. **Team Agreement**: Ensure team agrees on scale meaning
3. **Regular Review**: Review and adjust scale based on team velocity

### Sprint Settings

1. **Standard Duration**: Use consistent sprint length (typically 2 weeks)
2. **Auto-Close**: Enable auto-close to maintain sprint discipline
3. **Capacity Planning**: Set realistic max story points per sprint

### Board Customization

1. **Team Preferences**: Customize based on team's working style
2. **Swimlanes**: Use swimlanes to visualize work distribution
3. **Card Display**: Show only essential information to avoid clutter

### Automation

1. **Start Simple**: Begin with basic rules, add complexity gradually
2. **Test Rules**: Test automation rules in a test project first
3. **Document Rules**: Keep a list of active rules for team reference

### Notifications

1. **Avoid Overload**: Don't enable all notifications for all events
2. **Use Digests**: Use daily/weekly digests for less critical events
3. **Channel Selection**: Choose appropriate channels (email vs in-app)

---

## ❓ Frequently Asked Questions

### Q: Can I have different configurations for different projects?

**A:** Yes! Each project has its own independent configuration.

### Q: What happens if I delete a workflow state that has stories in it?

**A:** You cannot delete a state that has active stories. Move or delete the stories first.

### Q: Can I change the story point scale after stories are estimated?

**A:** Yes, but existing estimates won't automatically update. You'll need to re-estimate stories manually.

### Q: How do I reset just one setting?

**A:** You can manually change it back to the default value, or use "Reset to Defaults" to reset everything.

### Q: Can I copy configuration from one project to another?

**A:** Currently, you need to manually configure each project. This feature may be added in the future.

### Q: What's the difference between "Default" and "Final" states?

**A:** 
- **Default**: New stories start in this state
- **Final**: Stories in this state are considered "done" (counted in velocity, etc.)

---

## 🔗 Related Documentation

- [Project Configuration API Reference](../PROJECT_CONFIGURATION_API.md)
- [Project Management Enhancements Discussion](../../06_PLANNING/PROJECT_MANAGEMENT_ENHANCEMENTS_DISCUSSION.md)
- [User Guide](../USER_GUIDE.md)

---

## 📞 Support

If you need help:
1. Check this guide first
2. Review the [API Documentation](../PROJECT_CONFIGURATION_API.md)
3. Contact your project administrator
4. Reach out to the development team

---

**Last Updated:** December 8, 2024  
**Version:** 1.0

