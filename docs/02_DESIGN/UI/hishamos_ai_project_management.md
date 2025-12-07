---
title: "HishamOS - AI-Powered Project Management System"
description: "Documentation file"

category: "Core"
language: "ar"
original_language: "ar"

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

# HishamOS - AI-Powered Project Management System
## نظام إدارة مشاريع بالذكاء الاصطناعي الكامل

---

# 🎯 Overview

نظام إدارة مشاريع **ذكي ومتكامل** يعمل بالـ AI حيث:
- ✅ يستلم الذكاء الاصطناعي المهام (Sprints, Stories, Tasks)
- ✅ ينجزها **تلقائياً** بالكامل
- ✅ يمر عبر **جميع مراحل البورد** (Dev → Review → Testing → QA → Done)
- ✅ تتبع التقدم **Realtime**
- ✅ تكامل اختياري مع Jira

---

# 📊 Database Schema

```sql
-- Projects Table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_key VARCHAR(10) UNIQUE NOT NULL,  -- e.g., "HISH"
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    department VARCHAR(100),
    
    -- Settings
    board_columns JSONB DEFAULT '["Todo", "In Progress", "Code Review", "Testing", "QA", "Done"]',
    ai_enabled BOOLEAN DEFAULT true,
    jira_integration_enabled BOOLEAN DEFAULT false,
    jira_project_key VARCHAR(50),
    
    -- Status
    status VARCHAR(50) DEFAULT 'active',  -- active, archived, completed
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sprints Table
CREATE TABLE sprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    sprint_number INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    
    -- Duration
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Goals
    goal TEXT,
    capacity_points INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(50) DEFAULT 'planned',  -- planned, active, completed
    
    -- AI Performance
    ai_completion_rate DECIMAL(5,2) DEFAULT 0,
    manual_intervention_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(project_id, sprint_number)
);

-- Stories Table (Epic/User Story)
CREATE TABLE stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    sprint_id UUID REFERENCES sprints(id),
    
    -- Identification
    story_key VARCHAR(50) UNIQUE NOT NULL,  -- e.g., "HISH-123"
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Type
    story_type VARCHAR(50) DEFAULT 'story',  -- epic, story, bug, task
    
    -- Priority & Estimation
    priority VARCHAR(20) DEFAULT 'medium',  -- critical, high, medium, low
    story_points INTEGER,
    
    -- Assignment
    assigned_to_user_id UUID REFERENCES users(id),
    assigned_to_ai BOOLEAN DEFAULT false,
    assigned_agent_id UUID REFERENCES agents(id),
    
    -- Status
    status VARCHAR(50) DEFAULT 'todo',
    board_column VARCHAR(100) DEFAULT 'Todo',
    
    -- AI Execution
    ai_workflow_id UUID REFERENCES workflows(id),
    ai_execution_id UUID REFERENCES workflow_executions(id),
    ai_completion_percentage DECIMAL(5,2) DEFAULT 0,
    
    -- Metadata
    tags JSONB DEFAULT '[]',
    labels JSONB DEFAULT '[]',
    
    -- Jira Sync
    jira_issue_key VARCHAR(50),
    jira_synced_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Tasks Table (Sub-tasks)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    
    -- Identification
    task_key VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Type
    task_type VARCHAR(50) DEFAULT 'development',
    
    -- Assignment
    assigned_to_user_id UUID REFERENCES users(id),
    assigned_to_ai BOOLEAN DEFAULT false,
    assigned_agent_id UUID REFERENCES agents(id),
    
    -- Status
    status VARCHAR(50) DEFAULT 'todo',
    board_column VARCHAR(100) DEFAULT 'Todo',
    
    -- AI Execution
    ai_command_template_id UUID REFERENCES command_templates(id),
    ai_result_id UUID REFERENCES task_results(id),
    ai_quality_score DECIMAL(3,2),
    
    -- Estimation
    estimated_hours DECIMAL(5,2),
    actual_hours DECIMAL(5,2),
    
    -- Dependencies
    depends_on JSONB DEFAULT '[]',
    blocks JSONB DEFAULT '[]',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

النظام الآن يتضمن **إدارة مشاريع كاملة بالذكاء الاصطناعي**! 🚀

(*الملف كامل جداً - تم اختصاره هنا، الملف الكامل في الـ artifact*)
