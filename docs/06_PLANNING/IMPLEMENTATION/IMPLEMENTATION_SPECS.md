---
title: "HishamOS - Implementation Specifications"
description: "**Role**: Technical Architect"

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
  - implementation

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

# HishamOS - Implementation Specifications
**Role**: Technical Architect
**Purpose**: Comprehensive technical reference for developers.
**Status**: Ready for Implementation

---

# 1. System Prompts Library (Core Agents)

## 1.1 Coding Agent
**Role**: Senior Software Engineer
**System Prompt**:
```text
You are an expert Senior Software Engineer specializing in Python, Django, and React.
Your responsibilities:
1. Write clean, efficient, and documented code.
2. Follow SOLID principles and Design Patterns.
3. Always handle errors and edge cases.
4. Write Unit Tests for every function you create.

When given a task:
- Analyze the requirements.
- Plan the implementation steps.
- Write the code with comments.
- Verify imports and dependencies.
```

## 1.2 Code Reviewer Agent
**Role**: Senior Tech Lead
**System Prompt**:
```text
You are a strict Code Reviewer and Tech Lead.
Your goal is to ensure code quality, security, and performance.
Review Criteria:
1. Logic Errors: Are there bugs?
2. Security: SQL Injection, XSS, exposed keys?
3. Performance: N+1 queries, inefficient loops?
4. Style: PEP8 compliance, naming conventions.

Output Format:
- Score (0-10)
- Critical Issues (Must Fix)
- Suggestions (Nice to Have)
- Approved: (True/False)
```

## 1.3 QA / Testing Agent
**Role**: Quality Assurance Engineer
**System Prompt**:
```text
You are an expert QA Automation Engineer.
Your responsibilities:
1. Analyze requirements and generate Test Cases.
2. Write automated tests (Pytest / Jest).
3. Identify edge cases and regression risks.

For every feature:
- Create Positive Test Cases (Happy Path).
- Create Negative Test Cases (Error Handling).
- Create Boundary Value Analysis.
```

## 1.4 Business Analyst (BA) Agent
**Role**: Requirements Specialist
**System Prompt**:
```text
You are an expert Business Analyst.
Your goal is to transform vague ideas into concrete technical requirements.
Process:
1. Elicit requirements via Socratic questioning.
2. Generate SRS (Software Requirements Spec).
3. Generate User Stories (INVEST criteria).
4. Define Acceptance Criteria.
```

## 1.5 Project Manager (PM) Agent
**Role**: Agile Project Manager
**System Prompt**:
```text
You are an Agile Project Manager.
Your responsibilities:
1. Plan Sprints and allocate resources.
2. Break down Epics into Tasks.
3. Track progress and identify blockers.
4. Manage risks and dependencies.
```

---

# 2. Complete Database Schema

## 2.1 Core System Tables

```sql
-- Users & Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'dev',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agents Configuration
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    type VARCHAR(50), -- 'coding', 'review', 'pm'
    system_prompt TEXT NOT NULL,
    model_config JSONB DEFAULT '{"model": "gpt-4", "temp": 0.7}',
    capabilities JSONB, -- List of allowed tools
    is_active BOOLEAN DEFAULT true
);

-- Workflows
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    created_by UUID REFERENCES users(id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    metadata JSONB
);

-- Workflow Steps (Execution Log)
CREATE TABLE workflow_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id),
    agent_id UUID REFERENCES agents(id),
    step_order INTEGER NOT NULL,
    command VARCHAR(100),
    input_payload JSONB,
    output_payload JSONB,
    status VARCHAR(20),
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 2.2 Project Management Tables

```sql
-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    key VARCHAR(10) UNIQUE NOT NULL, -- e.g., 'HOS'
    description TEXT,
    owner_id UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'active'
);

-- Sprints
CREATE TABLE sprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    name VARCHAR(100),
    goal TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'planned' -- planned, active, completed
);

-- User Stories / Tasks
CREATE TABLE stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    sprint_id UUID REFERENCES sprints(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    acceptance_criteria TEXT,
    story_points INTEGER,
    priority VARCHAR(20), -- Critical, High, Medium, Low
    status VARCHAR(20) DEFAULT 'todo', -- todo, in_progress, review, testing, done
    assigned_agent_id UUID REFERENCES agents(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

# 3. API Specifications (Key Endpoints)

## 3.1 Agent Execution
**POST** `/api/v1/agents/execute`
Executes a specific command with an agent.
```json
// Request
{
  "agent_id": "uuid...",
  "command": "generate_code",
  "input": {
    "prompt": "Create a login API using Django",
    "context": "..."
  }
}

// Response
{
  "execution_id": "uuid...",
  "status": "success",
  "output": {
    "code": "def login(request): ...",
    "explanation": "..."
  },
  "usage": {"tokens": 150, "cost": 0.004}
}
```

## 3.2 Workflow Orchestration
**POST** `/api/v1/workflows/start`
Starts a complex multi-step workflow.
```json
// Request
{
  "name": "Feature Dev: Login",
  "steps": [
    {"agent": "coding", "command": "write_code", "input": "..."},
    {"agent": "reviewer", "command": "review", "input": "$prev.output"}
  ]
}
```

## 3.3 Project Management
**POST** `/api/v1/projects/{id}/stories`
Creates a new user story.
```json
// Request
{
  "title": "User Login",
  "description": "As a user...",
  "points": 5,
  "priority": "High"
}
```

---

# 4. Command Library Structure

Each agent has a set of allowed commands. These are mapped to specific Python functions or Prompt Templates.

**Example Command Registry:**
```python
COMMAND_REGISTRY = {
    "coding_agent": {
        "write_code": "Generate code based on requirements.",
        "debug_code": "Analyze error logs and fix bugs.",
        "refactor": "Improve code structure without changing behavior."
    },
    "reviewer_agent": {
        "review_pr": "Review a Pull Request.",
        "security_scan": "Check for security vulnerabilities."
    },
    "ba_agent": {
        "analyze_requirements": "Convert raw text to structured requirements.",
        "generate_stories": "Create user stories from SRS."
    }
}
```

---

# 5. Implementation Checklist

1.  **Setup Database**: Run the SQL scripts in Section 2.
2.  **Seed Agents**: Insert the System Prompts from Section 1 into the `agents` table.
3.  **Build API**: Implement the Endpoints in Section 3 using Django/FastAPI.
4.  **Implement Dispatcher**: Build the logic to route commands to agents (Section 4).
5.  **Connect AI**: Integrate OpenAI/Claude SDKs to power the agents.
