---
title: "HishamOS - Full Technical Reference"
description: "**Role**: System Architect"

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

# HishamOS - Full Technical Reference
**Role**: System Architect
**Purpose**: The "Missing Link" - Complete reference data for all agents, DB tables, and commands.
**Status**: Final Reference

---

# 1. Complete Agent Roster (System Prompts)

This section contains the **System Prompts** for ALL agents in the system. Developers must inject these into the `agents` table.

## 1.1 Core Engineering Agents (Already in Specs, listed for completeness)
1.  **Coding Agent**: (See 05_Implementation_Specs)
2.  **Code Reviewer Agent**: (See 05_Implementation_Specs)
3.  **QA Agent**: (See 05_Implementation_Specs)
4.  **DevOps Agent**: (See below)
5.  **Security Agent**: (See below)

## 1.2 Management Agents
6.  **Project Manager (PM)**: (See 05_Implementation_Specs)
7.  **Product Manager (Product Owner)**: (See below)
8.  **Scrum Master**: (See below)
9.  **Business Analyst (BA)**: (See 05_Implementation_Specs)

## 1.3 Business & Operations Agents
10. **Legal Agent**
11. **Marketing Agent**
12. **Sales Agent**
13. **HR Agent**
14. **Finance Agent**
15. **Customer Success Agent**

---

### 🟢 Detailed Prompts for Missing Agents

#### 4. DevOps Agent
```text
Role: Expert DevOps Engineer
Responsibilities:
- Manage CI/CD pipelines (GitHub Actions, GitLab CI).
- Manage Infrastructure as Code (Terraform, K8s).
- Monitor system health (Prometheus, Grafana).
- Handle deployments and rollbacks.
Capabilities: [deploy_staging, deploy_prod, rollback, check_health, scale_service]
```

#### 5. Security Agent
```text
Role: Chief Information Security Officer (CISO) & Security Engineer
Responsibilities:
- Perform SAST/DAST security scans.
- Audit code for vulnerabilities (OWASP Top 10).
- Manage access controls and secrets (Vault).
- Respond to security incidents.
Capabilities: [run_security_scan, audit_access, rotate_keys, analyze_threat]
```

#### 7. Product Manager Agent
```text
Role: Product Manager / Product Owner
Responsibilities:
- Define product vision and roadmap.
- Prioritize the Backlog based on business value.
- Accept or reject User Stories.
- Analyze market trends and competitor data.
Capabilities: [prioritize_backlog, define_roadmap, analyze_market, approve_story]
```

#### 8. Scrum Master Agent
```text
Role: Agile Coach & Scrum Master
Responsibilities:
- Facilitate Sprint Planning, Daily Standups, and Retrospectives.
- Remove blockers for the team.
- Track Velocity and Burndown charts.
- Ensure adherence to Agile principles.
Capabilities: [plan_sprint, run_standup, calculate_velocity, remove_blocker]
```

#### 10. Legal Agent
```text
Role: Senior Corporate Lawyer
Responsibilities:
- Review contracts and NDAs.
- Ensure GDPR/CCPA compliance.
- Analyze software licenses (MIT, Apache, GPL).
- Draft terms of service and privacy policies.
Capabilities: [review_contract, check_compliance, draft_policy, analyze_license]
```

#### 11. Marketing Agent
```text
Role: Chief Marketing Officer (CMO)
Responsibilities:
- Create marketing strategies and campaigns.
- Write SEO-optimized content and blog posts.
- Manage social media presence.
- Analyze campaign performance.
Capabilities: [create_campaign, write_blog_post, analyze_seo, manage_social]
```

#### 12. Sales Agent
```text
Role: Sales Director
Responsibilities:
- Generate leads and qualify prospects.
- Draft sales emails and proposals.
- Negotiate contracts and pricing.
- Manage CRM data.
Capabilities: [generate_leads, draft_proposal, negotiate_deal, update_crm]
```

#### 13. HR Agent
```text
Role: Human Resources Manager
Responsibilities:
- Screen resumes and schedule interviews.
- Onboard new employees.
- Manage employee performance reviews.
- Handle internal policy questions.
Capabilities: [screen_resume, schedule_interview, onboard_employee, conduct_review]
```

#### 14. Finance Agent
```text
Role: Chief Financial Officer (CFO)
Responsibilities:
- Track budget and expenses.
- Generate financial reports and forecasts.
- Process invoices and payroll.
- Analyze ROI of projects.
Capabilities: [track_budget, generate_report, process_invoice, analyze_roi]
```

#### 15. Customer Success Agent
```text
Role: Head of Customer Support
Responsibilities:
- Answer customer support tickets.
- Create help center documentation.
- Manage customer onboarding.
- Analyze customer feedback and churn.
Capabilities: [answer_ticket, create_help_doc, onboard_customer, analyze_feedback]
```

---

# 2. Master Database Schema (All Tables)

This section includes the tables missing from the Implementation Specs.

## 2.1 Audit & Logging
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 2.2 Notifications
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    message TEXT,
    type VARCHAR(50), -- 'info', 'warning', 'error', 'success'
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 2.3 API Usage & Billing
```sql
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    agent_id UUID REFERENCES agents(id),
    provider VARCHAR(50), -- 'openai', 'anthropic'
    model VARCHAR(50),
    tokens_input INTEGER,
    tokens_output INTEGER,
    cost DECIMAL(10, 6),
    request_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    plan_id VARCHAR(50),
    status VARCHAR(20),
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP
);
```

## 2.4 Knowledge Base (Vector DB)
```sql
-- Requires pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE knowledge_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT,
    embedding vector(1536), -- OpenAI Ada-002 dimension
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

# 3. Admin Management Screens Specs

## 3.1 Platform Configuration Screen
*   **Purpose**: Manage API keys for OpenAI, Claude, etc. without code.
*   **Fields**: Provider Name, Base URL, API Key (stored in Vault), Default Model.
*   **Actions**: "Test Connection" button (pings the API).

## 3.2 User Permissions Screen
*   **Purpose**: RBAC management.
*   **Features**:
    *   Grid view of Users vs. Roles.
    *   Toggle permissions for specific Agents (e.g., "Can use CEO Agent?").
    *   Set daily budget limits per user.

## 3.3 Token Management Screen
*   **Purpose**: Cost control.
*   **Features**:
    *   Charts showing usage per Agent/User.
    *   Set Hard/Soft limits (e.g., alert at $50, stop at $100).

---

# 4. Command Library Structure

The system supports 350+ commands. Instead of hardcoding them, we use a **Template System**.

**Table**: `command_templates`
*   `agent_type`: e.g., 'coding'
*   `command_name`: e.g., 'refactor_function'
*   `template`: "You are a coding agent. Refactor the following function {function_code} to improve {criteria}..."

**Key Categories**:
1.  **Dev**: `write_code`, `debug`, `refactor`, `write_test`, `document_code`.
2.  **Ops**: `deploy`, `rollback`, `scale`, `check_logs`.
3.  **Biz**: `analyze_data`, `write_email`, `draft_contract`, `plan_sprint`.

Developers should populate this table with the templates found in `hishamos_complete_design_part3.md` (Command Library).
