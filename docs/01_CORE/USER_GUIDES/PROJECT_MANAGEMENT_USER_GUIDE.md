---
title: "Project Management UI - User Guide"
description: "The HishamOS Project Management UI provides a comprehensive suite of tools for managing agile projects, including:"

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Project Manager
  secondary:
    - Scrum Master
    - Developer
    - QA / Tester
    - Business Analyst

applicable_phases:
  primary:
    - Development

tags:
  - user-guide
  - core
  - guide

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

# Project Management UI - User Guide

## Overview

The HishamOS Project Management UI provides a comprehensive suite of tools for managing agile projects, including:

- **Kanban Board**: Visual workflow management with drag-and-drop
- **Sprint Planning**: Backlog management and sprint capacity tracking
- **Story Editor**: Rich text editor for creating detailed user stories
- **Team Collaboration**: Real-time updates and bulk operations

---

## Getting Started

### Accessing Your Projects

1. Navigate to **Projects** from the sidebar
2. Click on a project to view its Kanban board
3. Or click **New Project** to create one

### Kanban Board

#### Columns

Your board has 5 default columns:
- **Backlog**: Stories that haven't been started
- **To Do**: Ready to work on
- **In Progress**: Currently being worked on
- **Review**: Awaiting review
- **Done**: Completed stories

#### Moving Stories

- **Drag & Drop**: Click and drag any story card to a different column
- **Quick Actions**: Hover over a card and click "View" or "Edit"

#### Filtering Stories

1. Click the **Filters** button
2. Select criteria:
   - **Priority**: Critical, High, Medium, Low
   - **Assignee**: Filter by team member
   - **Story Points**: Filter by size

#### Bulk Operations

1. Select multiple stories (Shift+Click or Ctrl+Click)
2. Click **Bulk Actions**
3. Choose an action:
   - Set Priority
   - Move to Column
   - Delete Selected

---

## Sprint Planning

### Creating a Sprint

1. Navigate to Sprint Planning view
2. Click **Create Sprint**
3. Fill in:
   - Sprint name
   - Duration (start/end dates)
   - Sprint goal
   - Capacity (story points)

### Adding Stories to Sprint

**From Backlog:**
1. Find story in Product Backlog panel
2. Click **Add to Sprint**
3. Story moves to selected sprint

**From Drag & Drop:**
1. Drag story from Backlog
2. Drop into Sprint panel

### Managing Sprint

- **Start Sprint**: Begin the sprint (changes status to Active)
- **Complete Sprint**: Mark sprint as done
- **Capacity Tracker**: Monitor story points vs. capacity

---

## Creating Stories

### Using the Story Editor

1. Click **New Story** button
2. Fill in required fields:
   - **Title**: User story (As a..., I want..., So that...)
   - **Priority**: Set importance level
   - **Story Points**: Estimate effort (Fibonacci: 1, 2, 3, 5, 8, 13, 21)

3. Add details:
   - **Description**: Use rich text formatting
   - **Acceptance Criteria**: Define "done" conditions

4. Click **Save Story**

### Rich Text Formatting

The editor supports:
- **Bold** (Ctrl+B)
- *Italic* (Ctrl+I)
- Bullet lists
- Numbered lists
- Code blocks

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `N` | New story |
| `/` | Focus search |
| `F` | Toggle filters |
| `E` | Edit selected |
| `Esc` | Close/Cancel |
| `↑↓` | Navigate cards |
| `←→` | Navigate columns |
| `Ctrl+A` | Select all |
| `Ctrl+S` | Save |
| `Delete` | Delete selected |

Press `?` anytime to view shortcuts panel.

---

## Customization

### Column Settings

1. Click **Customize Columns**
2. Drag to reorder columns
3. Toggle visibility checkboxes
4. Changes are saved automatically

### Personal Preferences

- **Theme**: Light/Dark mode
- **Column Width**: Adjusts for screen size
- **Filters**: Saved per project

---

## Best Practices

### Writing Good Stories

✅ **DO:**
- Use the format: "As a [user], I want [feature], so that [benefit]"
- Keep stories small and focused
- Include clear acceptance criteria
- Estimate story points collaboratively

❌ **DON'T:**
- Create stories without acceptance criteria
- Make stories too large (>13 points)
- Leave stories unassigned for long periods

### Sprint Planning

✅ **DO:**
- Plan sprints with team involvement
- Set realistic capacity based on team velocity
- Review and refine backlog regularly
- Start sprint with clear goals

❌ **DON'T:**
- Overload sprints beyond capacity
- Change sprint scope mid-sprint
- Skip sprint reviews/retrospectives

---

## Troubleshooting

### Stories Not Saving

- Check internet connection
- Ensure all required fields are filled
- Look for validation errors (highlighted in red)

### Drag & Drop Not Working

- Try refreshing the page
- Check browser compatibility (Chrome, Firefox, Safari supported)
- Disable browser extensions that might interfere

### Performance Issues

- Clear browser cache
- Close unused tabs
- Check for large attachments or descriptions

---

## Support

Need help? Contact:
- **Email**: support@hishamos.com
- **Slack**: #project-management
- **Docs**: https://docs.hishamos.com

---

*Last Updated: December 4, 2024*
