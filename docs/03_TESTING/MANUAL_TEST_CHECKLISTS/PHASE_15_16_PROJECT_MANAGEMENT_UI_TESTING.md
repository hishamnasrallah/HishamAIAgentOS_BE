---
title: "Phase 15-16: Project Management UI - Manual Testing Checklist"
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
  - test
  - phase
  - phase-15
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

# Phase 15-16: Project Management UI - Manual Testing Checklist

**Date:** December 2024  
**Component:** Project Management UI (Kanban, Sprint Planning)  
**Phase:** Phase 15-16  
**Status:** ✅ Complete (100%)

---

## 📋 Pre-Testing Setup

- [ ] Backend server is running
- [ ] Frontend server is running (`npm run dev`)
- [ ] User is logged in
- [ ] At least one project exists
- [ ] Browser console is open (F12)

---

## 📋 Frontend Testing

### 1. Kanban Board

#### 1.1 Board Display
- [ ] Navigate to `/projects/{id}/kanban`
- [ ] Kanban board displays
- [ ] Columns show: Backlog, To Do, In Progress, Review, Done
- [ ] Stories appear as cards in columns
- [ ] Cards show: title, assignee, points, priority
- [ ] Board is responsive

#### 1.2 Drag and Drop
- [ ] Drag story card between columns
- [ ] Card moves smoothly
- [ ] Status updates automatically
- [ ] Change persists after refresh
- [ ] Multiple cards can be moved

#### 1.3 Card Actions
- [ ] Click card - opens story details
- [ ] Edit button works
- [ ] Delete button works (with confirmation)
- [ ] Assignee can be changed
- [ ] Priority can be changed

---

### 2. Sprint Planning

#### 2.1 Sprint Planning Page
- [ ] Navigate to `/projects/{id}/sprints`
- [ ] Sprint planning interface displays
- [ ] Active sprint shown
- [ ] Backlog visible
- [ ] Stories can be added to sprint
- [ ] Capacity tracking works

#### 2.2 Auto Plan Sprint
- [ ] "Auto Plan Sprint" button
- [ ] Stories automatically assigned
- [ ] Capacity respected
- [ ] Priorities respected
- [ ] Results can be adjusted

---

### 3. Story Editor

#### 3.1 Rich Text Editor
- [ ] Story editor uses TipTap
- [ ] Rich text formatting works
- [ ] Code blocks work
- [ ] Lists work
- [ ] Links work
- [ ] Save works

#### 3.2 Story Form
- [ ] Create story form works
- [ ] Edit story form works
- [ ] All fields save correctly
- [ ] Validation works
- [ ] File uploads work (if implemented)

---

## 🌐 Backend API Testing

### 4. Project Management APIs

#### 4.1 Stories API
- [ ] All CRUD operations work
- [ ] Filtering works
- [ ] Sorting works
- [ ] Bulk operations work

#### 4.2 Sprints API
- [ ] All CRUD operations work
- [ ] Auto-plan endpoint works
- [ ] Burndown data works

---

## ✅ Final Verification

### 5. Complete Workflows

#### 5.1 Kanban Workflow
- [ ] Create story
- [ ] Add to board
- [ ] Drag through columns
- [ ] Update status
- [ ] Complete story

#### 5.2 Sprint Planning Workflow
- [ ] Create sprint
- [ ] Auto-plan sprint
- [ ] Adjust assignments
- [ ] Start sprint
- [ ] Track progress

---

## 📝 Notes & Issues

**Date:** _______________  
**Tester:** _______________  
**Environment:** _______________

### Issues Found:
1. 
2. 
3. 

---

## ✅ Sign-Off

- [ ] All frontend tests passed
- [ ] Kanban board works
- [ ] Sprint planning works
- [ ] Story editor works
- [ ] Drag and drop works
- [ ] Complete workflows tested

**Tester Signature:** _______________  
**Date:** _______________

