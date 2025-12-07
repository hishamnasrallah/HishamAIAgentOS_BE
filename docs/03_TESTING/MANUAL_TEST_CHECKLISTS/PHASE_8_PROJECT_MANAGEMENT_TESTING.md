---
title: "Phase 8: Project Management Features - Manual Testing Checklist"
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
  - phase-8
  - testing
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

# Phase 8: Project Management Features - Manual Testing Checklist

**Date:** December 2024  
**Component:** Project Management Backend Features  
**Phase:** Phase 8  
**Status:** ✅ Complete (100%)

---

## 📋 Pre-Testing Setup

- [ ] Backend server is running (`python manage.py runserver` or `daphne`)
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] At least one project created
- [ ] Browser console is open (F12) to check for errors
- [ ] Postman/API client ready for API testing
- [ ] Django admin accessible at `/admin/`

---

## 🗂️ Backend Django Admin Testing

### 1. Project Model Admin

#### 1.1 Access Project Admin
- [ ] Navigate to `/admin/projects/project/`
- [ ] Project list displays all projects
- [ ] Project list shows: name, owner, status, created_at
- [ ] Search works (name, description)
- [ ] Filters work (owner, status, created_at)

#### 1.2 Create Project
- [ ] Click "Add Project"
- [ ] Form fields: name, description, owner, status, start_date, end_date
- [ ] Submit - project created
- [ ] Project appears in list

---

### 2. Sprint Model Admin

#### 2.1 Access Sprint Admin
- [ ] Navigate to `/admin/projects/sprint/`
- [ ] Sprint list displays all sprints
- [ ] Sprint list shows: name, project, status, start_date, end_date
- [ ] Search works (name, project)
- [ ] Filters work (project, status, start_date)

---

### 3. Epic, Story, Task Admin

#### 3.1 Epic Admin
- [ ] Navigate to `/admin/projects/epic/`
- [ ] Epic list displays correctly
- [ ] Create, edit, delete work

#### 3.2 User Story Admin
- [ ] Navigate to `/admin/projects/userstory/`
- [ ] Story list displays correctly
- [ ] Create, edit, delete work
- [ ] Rich text fields work

#### 3.3 Task Admin
- [ ] Navigate to `/admin/projects/task/`
- [ ] Task list displays correctly
- [ ] Create, edit, delete work

---

## 🌐 Backend API Testing

### 4. Project Management Endpoints

#### 4.1 Projects API
- [ ] **GET** `/api/v1/projects/projects/` - List projects
- [ ] **POST** `/api/v1/projects/projects/` - Create project
- [ ] **GET** `/api/v1/projects/projects/{id}/` - Get project
- [ ] **PATCH** `/api/v1/projects/projects/{id}/` - Update project
- [ ] **DELETE** `/api/v1/projects/projects/{id}/` - Delete project
- [ ] All endpoints work correctly
- [ ] Permissions enforced (owner/admin)

#### 4.2 Sprints API
- [ ] **GET** `/api/v1/projects/sprints/` - List sprints
- [ ] **POST** `/api/v1/projects/sprints/` - Create sprint
- [ ] **GET** `/api/v1/projects/sprints/{id}/` - Get sprint
- [ ] **PATCH** `/api/v1/projects/sprints/{id}/` - Update sprint
- [ ] **DELETE** `/api/v1/projects/sprints/{id}/` - Delete sprint
- [ ] Filter by project works

#### 4.3 Stories API
- [ ] **GET** `/api/v1/projects/stories/` - List stories
- [ ] **POST** `/api/v1/projects/stories/` - Create story
- [ ] **GET** `/api/v1/projects/stories/{id}/` - Get story
- [ ] **PATCH** `/api/v1/projects/stories/{id}/` - Update story
- [ ] **DELETE** `/api/v1/projects/stories/{id}/` - Delete story
- [ ] Filter by project, sprint, status works

#### 4.4 Tasks API
- [ ] **GET** `/api/v1/projects/tasks/` - List tasks
- [ ] **POST** `/api/v1/projects/tasks/` - Create task
- [ ] **GET** `/api/v1/projects/tasks/{id}/` - Get task
- [ ] **PATCH** `/api/v1/projects/tasks/{id}/` - Update task
- [ ] **DELETE** `/api/v1/projects/tasks/{id}/` - Delete task
- [ ] Filter by story, assignee, status works

---

### 5. AI-Powered Features

#### 5.1 Generate Stories
- [ ] **POST** `/api/v1/projects/projects/{id}/generate-stories/`
- [ ] Request body:
  ```json
  {
    "idea": "Build a user authentication system",
    "epic_id": 1,
    "count": 5
  }
  ```
- [ ] Returns generated user stories
- [ ] Stories are well-formed
- [ ] Stories include acceptance criteria
- [ ] Stories are linked to project/epic

#### 5.2 Auto Plan Sprint
- [ ] **POST** `/api/v1/projects/sprints/{id}/auto-plan/`
- [ ] Request body:
  ```json
  {
    "capacity": 40,
    "priorities": ["high", "medium", "low"]
  }
  ```
- [ ] Automatically assigns stories to sprint
- [ ] Respects capacity
- [ ] Respects priorities
- [ ] Optimizes story distribution

#### 5.3 Estimate Story
- [ ] **POST** `/api/v1/projects/stories/{id}/estimate/`
- [ ] Returns story points estimate
- [ ] Includes confidence score
- [ ] Estimation is reasonable
- [ ] Based on story complexity

---

### 6. Analytics Endpoints

#### 6.1 Burndown Chart
- [ ] **GET** `/api/v1/projects/sprints/{id}/burndown/`
- [ ] Returns burndown data
- [ ] Data includes:
  - [ ] Dates
  - [ ] Planned work
  - [ ] Actual work
  - [ ] Remaining work
- [ ] Data is accurate
- [ ] Chart data is properly formatted

#### 6.2 Velocity Report
- [ ] **GET** `/api/v1/projects/projects/{id}/velocity/`
- [ ] Returns velocity data
- [ ] Includes sprint velocities
- [ ] Includes average velocity
- [ ] Includes trend

#### 6.3 Project Analytics
- [ ] **GET** `/api/v1/projects/projects/{id}/analytics/`
- [ ] Returns project statistics
- [ ] Includes story counts by status
- [ ] Includes task completion rates
- [ ] Includes sprint metrics

---

## 🔒 Security Testing

### 7. Access Control

#### 7.1 Project Access
- [ ] Project owner can access project
- [ ] Project members can access project
- [ ] Non-members cannot access project
- [ ] Admin can access all projects

#### 7.2 Story/Task Access
- [ ] Users can access stories in their projects
- [ ] Users cannot access stories in other projects
- [ ] Permissions enforced correctly

---

## ✅ Final Verification

### 8. Complete Workflows

#### 8.1 Project Creation Workflow
- [ ] Create project
- [ ] Create epic
- [ ] Generate stories from idea
- [ ] Create sprint
- [ ] Auto-plan sprint
- [ ] Estimate stories
- [ ] View analytics

#### 8.2 Story Lifecycle Workflow
- [ ] Create story
- [ ] Assign to sprint
- [ ] Estimate story points
- [ ] Create tasks
- [ ] Update story status
- [ ] Complete story

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
- [ ] AI features work correctly
- [ ] Analytics work correctly
- [ ] Security checks passed
- [ ] Complete workflows tested

**Tester Signature:** _______________  
**Date:** _______________

