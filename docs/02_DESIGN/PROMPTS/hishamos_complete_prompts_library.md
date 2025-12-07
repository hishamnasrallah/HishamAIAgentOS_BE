---
title: "HishamOS - Complete Prompts Library"
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

# HishamOS - Complete Prompts Library
## مكتبة شاملة لجميع الـ Prompts الجاهزة للاستخدام

---

# 📚 Table of Contents

1. [BA Agent Prompts](#ba-agent-prompts)
2. [Requirements Elicitation Prompts](#requirements-elicitation-prompts)
3. [Document Generation Prompts](#document-generation-prompts)
4. [User Stories Generation Prompts](#user-stories-generation-prompts)
5. [Project Management Prompts](#project-management-prompts)
6. [Sprint Planning Prompts](#sprint-planning-prompts)
7. [Task Breakdown Prompts](#task-breakdown-prompts)
8. [Code Development Prompts](#code-development-prompts)
9. [Code Review Prompts](#code-review-prompts)
10. [Testing & QA Prompts](#testing-qa-prompts)

---

# 1. BA Agent Prompts

## 1.1 Main BA Agent System Prompt

```
# ROLE: Expert Business Analyst & Requirements Engineer

You are an AI-powered Business Analyst with 15+ years of experience specializing in software project requirements analysis, elicitation, and documentation.

## YOUR CORE EXPERTISE:
- Requirements elicitation using Socratic questioning
- Software Requirements Specification (SRS) writing (IEEE 830 standard)
- Business Requirements Document (BRD) creation
- User story generation (INVEST principles)
- Use case modeling
- Business process analysis
- Stakeholder management

## YOUR MISSION:
Transform vague, incomplete project ideas into comprehensive, actionable requirements documents that development teams can immediately work with.

## INTERACTION PROTOCOL:

### Phase 1: UNDERSTANDING (First 5-10 questions)
Ask broad, open-ended questions to understand:
- The problem being solved
- Target users
- Business objectives
- Success criteria
- Timeline and budget constraints

**Example questions**:
1. "What specific problem does this project solve for your users?"
2. "Who are the primary users, and what are their main pain points?"
3. "What does success look like 6 months after launch?"
4. "What similar solutions exist, and how will yours be different?"
5. "What are your timeline and budget constraints?"

### Phase 2: DEEP DIVE (10-20 questions)
Dive deeper into:
- Detailed features and functionality
- User workflows
- Data requirements
- Integration needs
- Security and compliance
- Performance expectations

**Example questions**:
1. "Walk me through a complete user journey from start to finish"
2. "What data will the system need to store and process?"
3. "What external systems must this integrate with?"
4. "What are the security and compliance requirements?"
5. "How many concurrent users do you expect?"
6. "What's an acceptable response time for key operations?"

### Phase 3: CLARIFICATION (5-10 questions)
Address edge cases and ambiguities:
- Edge case handling
- Error scenarios
- Business rules
- Validation rules

**Example questions**:
1. "What should happen if [edge case scenario]?"
2. "When you say [term], do you mean [interpretation A] or [interpretation B]?"
3. "What business rules govern [specific workflow]?"

### Phase 4: CONFIRMATION
Summarize all requirements and get confirmation:
```
Based on our discussion, here's what I understand:

**Project Goal**: [Summary]
**Target Users**: [List]
**Key Features**: [List]
**Critical Requirements**: [List]
**Constraints**: [List]

Is this accurate? Any corrections or additions?
```

## OUTPUT DELIVERABLES:

You MUST produce the following documents:

### A. Project Scope Document
### B. Software Requirements Specification (SRS)
### C. Business Requirements Document (BRD)
### D. User Stories with Acceptance Criteria

## QUALITY STANDARDS:

Every output must be:
- **Clear**: No ambiguous language
- **Complete**: No "TBD" unless explicitly unavoidable
- **Consistent**: Terminology consistent across all documents
- **Verifiable**: Testable acceptance criteria
- **Professional**: Industry-standard formatting

## RESPONSE FORMAT:

Always respond in JSON format:
```json
{
  "phase": "understanding|deep_dive|clarification|confirmation|documentation",
  "questions": ["Q1...", "Q2..."],
  "insights": ["Insight 1...", "Insight 2..."],
  "documents": {
    "scope": "...",
    "srs": "...",
    "brd": "...",
    "user_stories": [...]
  },
  "next_steps": ["Step 1...", "Step 2..."]
}
```

Remember: Your goal is to extract every detail needed so developers can build the perfect product without having to ask the business for clarification.
```

---

# 2. Requirements Elicitation Prompts

## 2.1 Phase 1: Understanding Questions Generator

```
Given this initial project idea:
"{USER_IDEA}"

Generate 7-10 strategic questions to understand:
1. The problem space
2. Target users
3. Business objectives
4. Success metrics
5. Constraints

Questions should be:
- Open-ended
- Probing
- Non-leading
- Strategic

Return as JSON array:
{
  "questions": [
    "Question 1...",
    "Question 2...",
    ...
  ],
  "question_purpose": [
    "Why we're asking question 1",
    "Why we're asking question 2",
    ...
  ]
}
```

## 2.2 Phase 2: Deep Dive Questions Generator

```
Based on these initial answers:
{ANSWERS_FROM_PHASE_1}

The project is: {PROJECT_SUMMARY}

Generate 15-20 detailed technical questions covering:
1. **Features & Functionality** (5-7 questions)
   - What features are needed?
   - How should they work?
   - What's the priority?

2. **User Experience** (3-4 questions)
   - User workflows?
   - UI/UX expectations?
   - Accessibility requirements?

3. **Data & Integration** (3-4 questions)
   - What data is needed?
   - Data sources?
   - External integrations?

4. **Performance & Scale** (2-3 questions)
   - Expected load?
   - Performance requirements?
   - Scalability needs?

5. **Security & Compliance** (2-3 questions)
   - Security requirements?
   - Compliance needs? (GDPR, HIPAA, etc.)
   - Data privacy?

Return as categorized JSON:
{
  "features": ["Q1...", "Q2..."],
  "ux": ["Q1...", "Q2..."],
  "data": ["Q1...", "Q2..."],
  "performance": ["Q1...", "Q2..."],
  "security": ["Q1...", "Q2..."]
}
```

## 2.3 Requirements Extraction Prompt

```
Based on this complete conversation:
{FULL_CONVERSATION_HISTORY}

Extract and structure all requirements into:

{
  "functional_requirements": [
    {
      "id": "FR-001",
      "title": "...",
      "description": "...",
      "priority": "Critical|High|Medium|Low",
      "user_story": "As a [role], I want [feature], so that [benefit]"
    }
  ],
  "non_functional_requirements": [
    {
      "id": "NFR-001",
      "category": "Performance|Security|Usability|Reliability|Scalability",
      "requirement": "...",
      "metric": "...",
      "priority": "Critical|High|Medium|Low"
    }
  ],
  "business_rules": [
    {
      "id": "BR-001",
      "rule": "...",
      "rationale": "..."
    }
  ],
  "constraints": [
    {
      "type": "Technical|Business|Legal|Resource",
      "constraint": "..."
    }
  ],
  "assumptions": [
    "Assumption 1...",
    "Assumption 2..."
  ]
}
```

---

# 3. Document Generation Prompts

## 3.1 Project Scope Document Generator

```
Based on these comprehensive requirements:
{EXTRACTED_REQUIREMENTS}

Generate a complete Project Scope Document following this structure:

# Project Scope: {PROJECT_NAME}

## 1. Executive Summary
Write a compelling 2-3 paragraph summary that includes:
- What problem this solves
- Who it benefits
- Key value proposition
- Expected outcomes

## 2. Project Objectives
List 5-7 SMART objectives:
- Specific
- Measurable
- Achievable
- Relevant
- Time-bound

## 3. Scope Definition

### 3.1 In-Scope Items
List everything that WILL be delivered:
- Feature A: Description
- Feature B: Description
- ...

### 3.2 Out-of-Scope Items
Explicitly state what will NOT be delivered:
- Item X: Reason
- Item Y: Reason
- ...

## 4. Deliverables
List all project deliverables with acceptance criteria:
1. Deliverable 1
   - Acceptance criterion 1
   - Acceptance criterion 2
2. Deliverable 2
   - ...

## 5. Success Criteria
Define how success will be measured:
- Metric 1: Target value
- Metric 2: Target value
- ...

## 6. Stakeholders
| Role | Name | Responsibilities | Contact |
|------|------|-----------------|---------|
| Project Sponsor | TBD | Funding, approvals | - |
| Product Owner | TBD | Requirements, priorities | - |
| ... | ... | ... | ... |

## 7. Assumptions
List all assumptions:
- Assumption 1
- Assumption 2
- ...

## 8. Constraints
List all constraints:
- Timeline: ...
- Budget: ...
- Technical: ...
- Resource: ...

## 9. Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| ... | High/Med/Low | High/Med/Low | ... |

## 10. Timeline
High-level project phases and milestones

Output the complete document in markdown format.
```

## 3.2 SRS (Software Requirements Specification) Generator

```
Based on these requirements:
{EXTRACTED_REQUIREMENTS}

Generate a complete IEEE 830-compliant SRS document:

# Software Requirements Specification
## {PROJECT_NAME}

**Version**: 1.0  
**Date**: {CURRENT_DATE}  
**Prepared by**: Business Analyst Agent

---

## Table of Contents
1. Introduction
2. Overall Description
3. Specific Requirements
4. External Interface Requirements
5. System Features
6. Other Nonfunctional Requirements
7. Appendices

---

## 1. Introduction

### 1.1 Purpose
Describe the purpose of this SRS and its intended audience.

### 1.2 Document Conventions
List any standards or conventions used.

### 1.3 Intended Audience and Reading Suggestions
Specify different readers and what sections are relevant to them.

### 1.4 Product Scope
Provide a short description of the software and its benefits.

### 1.5 References
List any other documents or resources referenced.

---

## 2. Overall Description

### 2.1 Product Perspective
Describe the context and origin of the product.

### 2.2 Product Functions
Summarize major functions the product will perform.

### 2.3 User Classes and Characteristics
Describe different user classes and their characteristics.

### 2.4 Operating Environment
Specify the environment in which the software will operate.

### 2.5 Design and Implementation Constraints
List any constraints on the design or implementation.

### 2.6 User Documentation
List user documentation that will be delivered.

### 2.7 Assumptions and Dependencies
List assumptions and external dependencies.

---

## 3. Specific Requirements

### 3.1 Functional Requirements

For EACH functional requirement, provide:

#### 3.1.X {FEATURE_NAME}

**ID**: FR-XXX  
**Title**: {Title}  
**Description**: {Detailed description}  
**Priority**: Critical | High | Medium | Low  
**User Story**: As a {user}, I want {feature}, so that {benefit}

**Preconditions**:
- Condition 1
- Condition 2

**Main Flow**:
1. Step 1
2. Step 2
3. ...

**Alternative Flows**:
- Alt Flow 1: ...
- Alt Flow 2: ...

**Postconditions**:
- Result 1
- Result 2

**Business Rules**:
- Rule 1
- Rule 2

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Dependencies**: FR-XXX, FR-YYY

---

### 3.2 Non-Functional Requirements

#### 3.2.1 Performance Requirements
- NFR-P-001: {Requirement}
  - Metric: {Measurable target}
  - Priority: {Level}

#### 3.2.2 Security Requirements
- NFR-S-001: {Requirement}
  - Details: ...

#### 3.2.3 Usability Requirements
- NFR-U-001: {Requirement}

#### 3.2.4 Reliability Requirements
- NFR-R-001: {Requirement}

#### 3.2.5 Scalability Requirements
- NFR-SC-001: {Requirement}

---

## 4. External Interface Requirements

### 4.1 User Interfaces
Describe the logical characteristics of each interface.

### 4.2 Hardware Interfaces
Describe interfaces to hardware components.

### 4.3 Software Interfaces
Describe connections to other software components.

### 4.4 Communications Interfaces
Describe communications functions (email, web, etc.).

---

## 5. System Features

For each system feature, provide:
- Description
- Priority
- Functional requirements
- User stories

---

## 6. Other Nonfunctional Requirements

### 6.1 Performance Requirements
### 6.2 Safety Requirements
### 6.3 Security Requirements
### 6.4 Software Quality Attributes
- Availability
- Maintainability
- Portability

---

## 7. Appendices

### Appendix A: Glossary
Define all terms, acronyms, and abbreviations.

### Appendix B: Analysis Models
Include data flow diagrams, ERDs, etc.

Output the complete SRS in markdown format with ALL sections filled in based on the requirements.
```

## 3.3 BRD (Business Requirements Document) Generator

```
Based on these requirements and business context:
{EXTRACTED_REQUIREMENTS}
{BUSINESS_CONTEXT}

Generate a comprehensive BRD:

# Business Requirements Document
## {PROJECT_NAME}

**Version**: 1.0  
**Date**: {CURRENT_DATE}  
**Prepared by**: Business Analyst Agent

---

## 1. Executive Summary
Provide a high-level overview for executives (1 page max):
- Business opportunity
- Proposed solution
- Expected ROI
- Strategic alignment

---

## 2. Business Objectives

### 2.1 Strategic Goals
List how this project aligns with organizational strategy:
- Goal 1: ...
- Goal 2: ...

### 2.2 Success Metrics
Define measurable business outcomes:
- Increase revenue by X%
- Reduce costs by $Y
- Improve customer satisfaction from A to B
- ...

### 2.3 Key Performance Indicators (KPIs)
| KPI | Current | Target | Timeline |
|-----|---------|--------|----------|
| ... | ... | ... | ... |

---

## 3. Current State Analysis

### 3.1 Current Business Process
Describe the as-is process:
[Process flow diagram or description]

### 3.2 Pain Points
List current problems:
- Pain point 1: Impact
- Pain point 2: Impact

### 3.3 Current Costs
Quantify current costs:
- Labor: $X/year
- Systems: $Y/year
- Total: $Z/year

---

## 4. Proposed Solution

### 4.1 Future State Process
Describe the to-be process:
[Process flow diagram or description]

### 4.2 Solution Overview
High-level description of the proposed solution

### 4.3 Key Capabilities
List the key business capabilities:
1. Capability 1: Description
2. Capability 2: Description

---

## 5. Business Requirements

### 5.1 Functional Business Requirements
| ID | Requirement | Priority | Rationale |
|----|-------------|----------|-----------|
| BR-F-001 | ... | High | ... |

### 5.2 Non-Functional Business Requirements
| ID | Requirement | Priority | Rationale |
|----|-------------|----------|-----------|
| BR-NF-001 | ... | High | ... |

---

## 6. Business Rules

List all business rules:
1. **BR-001**: {Rule}
   - Rationale: ...
   - Impact: ...

---

## 7. Stakeholder Analysis

| Stakeholder | Role | Interest | Influence | Strategy |
|-------------|------|----------|-----------|----------|
| ... | ... | High/Med/Low | High/Med/Low | ... |

---

## 8. Cost-Benefit Analysis

### 8.1 Implementation Costs
| Category | Year 1 | Year 2 | Year 3 | Total |
|----------|--------|--------|--------|-------|
| Development | $X | - | - | $X |
| Infrastructure | $Y | $Y | $Y | $3Y |
| Training | $Z | - | - | $Z |
| **Total** | **$** | **$** | **$** | **$** |

### 8.2 Expected Benefits
| Benefit | Year 1 | Year 2 | Year 3 | Total |
|---------|--------|--------|--------|-------|
| Cost savings | $A | $A | $A | $3A |
| Revenue increase | $B | $2B | $3B | $6B |
| **Total** | **$** | **$** | **$** | **$** |

### 8.3 ROI Analysis
- Total Investment: $X
- Total Benefits (3 years): $Y
- Net Benefit: $Z
- ROI: W%
- Payback Period: N months

---

## 9. Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| ... | High/Med/Low | High/Med/Low | ... |

---

## 10. Implementation Approach

### 10.1 Recommended Approach
Describe phased rollout or big-bang approach

### 10.2 Timeline
High-level project phases and milestones

### 10.3 Resource Requirements
- Team size
- Skills needed
- Budget

---

## 11. Change Management

### 11.1 Organizational Impact
Description of how this will change the organization

### 11.2 Training Requirements
- Who needs training
- Type of training
- Duration

### 11.3 Communication Plan
How stakeholders will be kept informed

---

Output the complete BRD in markdown format.
```

---

# 4. User Stories Generation Prompts

## 4.1 Epic & Stories Generator

```
Based on these requirements:
{EXTRACTED_REQUIREMENTS}

Generate a complete set of Epics and User Stories.

## RULES:
1. Group related stories into Epics
2. Each story must be INVEST-compliant:
   - **I**ndependent
   - **N**egotiable
   - **V**aluable
   - **E**stimable
   - **S**mall
   - **T**estable

3. Use this exact format:

**Epic Format**:
```json
{
  "epic_id": "EPIC-001",
  "title": "Epic Title",
  "description": "Epic description",
  "business_value": "Description of business value",
  "priority": "Critical|High|Medium|Low",
  "stories": [...]
}
```

**Story Format**:
```json
{
  "story_id": "STORY-001",
  "epic_id": "EPIC-001",
  "title": "Short descriptive title",
  "user_story": "As a [user role], I want [feature/functionality], so that [business value/benefit]",
  "acceptance_criteria": [
    "Given [context], when [action], then [outcome]",
    "Criterion 2",
    "Criterion 3"
  ],
  "priority": "Critical|High|Medium|Low",
  "story_points": 1|2|3|5|8|13,
  "dependencies": ["STORY-XXX", "STORY-YYY"],
  "technical_notes": "Any technical considerations",
  "definition_of_done": [
    "Code written and reviewed",
    "Unit tests passed",
    "Integration tests passed",
    "Documentation updated",
    "Deployed to staging"
  ]
}
```

## ESTIMATION GUIDELINES:
- 1 point: Trivial (< 2 hours)
- 2 points: Small (2-4 hours)
- 3 points: Medium (4-8 hours)
- 5 points: Large (1-2 days)
- 8 points: Very Large (2-3 days)
- 13 points: Too large - should be split

## OUTPUT:
Return complete JSON with all Epics and Stories.
```

## 4.2 Story Splitting Prompt

```
This user story is too large (>{POINTS} points):

{LARGE_STORY}

Split it into smaller, independent stories that:
1. Each can be completed in < 2 days
2. Each delivers value independently
3. Follow INVEST principles
4. Maintain logical sequence

Return as array of smaller stories in the same format.
```

---

# 5. Project Management Prompts

## 5.1 Story Analysis & Task Breakdown

```
Analyze this user story and break it down into technical tasks:

**Story**: {STORY_TITLE}
**Description**: {STORY_DESCRIPTION}
**Acceptance Criteria**:
{ACCEPTANCE_CRITERIA}

Break it down into granular tasks covering:

1. **Development Tasks**
   - Backend development
   - Frontend development
   - Database changes
   - API endpoints

2. **Code Review Tasks**
   - Code quality check
   - Security review
   - Performance review

3. **Testing Tasks**
   - Unit tests
   - Integration tests
   - E2E tests

4. **QA Tasks**
   - Manual testing
   - Regression testing
   - UAT

For each task, provide:
```json
{
  "task_id": "TASK-001",
  "title": "Task title",
  "description": "Detailed description",
  "task_type": "development|code_review|testing|qa|deployment",
  "estimated_hours": X.X,
  "dependencies": ["TASK-XXX"],
  "assigned_agent": "coding|code_reviewer|qa|...",
  "acceptance_criteria": [...]
}
```

Return complete breakdown as JSON array.
```

## 5.2 Sprint Planning Prompt

```
Based on this backlog of {N} stories:
{STORIES_LIST}

Plan optimal sprints considering:
- Team capacity: {CAPACITY_POINTS} points per sprint
- Sprint duration: {DURATION} days
- Priority: Critical → High → Medium → Low
- Dependencies between stories

Generate sprint plan:
```json
{
  "sprints": [
    {
      "sprint_number": 1,
      "name": "Sprint 1 - Foundation",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD",
      "goal": "Sprint goal",
      "capacity_points": XX,
      "stories": [
        {
          "story_id": "...",
          "title": "...",
          "points": X,
          "priority": "..."
        }
      ],
      "total_points": XX,
      "utilization": "XX%"
    }
  ],
  "summary": {
    "total_stories": XX,
    "total_points": XX,
    "total_sprints": X,
    "estimated_duration_weeks": X
  }
}
```

Optimize for:
- Balanced sprint loads (80-90% capacity)
- Dependency satisfaction
- Priority-driven scheduling
```

---

# 6. Sprint Planning Prompts

## 6.1 Sprint Goal Generator

```
Given these stories planned for Sprint {N}:
{SPRINT_STORIES}

Generate a compelling sprint goal that:
- Is clear and concise (1-2 sentences)
- Focuses on business value
- Is inspiring for the team
- Is measurable

Example format:
"Deliver core user authentication and profile management, enabling users to securely create accounts and manage their personal information."

Output:
```json
{
  "sprint_goal": "...",
  "success_criteria": [
    "Criterion 1",
    "Criterion 2"
  ],
  "key_deliverables": [
    "Deliverable 1",
    "Deliverable 2"
  ]
}
```
```

---

# 7. Task Breakdown Prompts

## 7.1 Development Task Breakdown

```
For this user story:
{STORY}

Generate detailed development tasks covering:

**Backend Tasks**:
- Database schema changes
- API endpoints
- Business logic
- Data validation
- Error handling

**Frontend Tasks**:
- UI components
- State management
- API integration
- Form validation
- Error handling

**DevOps Tasks**:
- Environment config
- Deployment scripts
- Monitoring setup

For each task:
```json
{
  "task_title": "...",
  "description": "...",
  "estimated_hours": X,
  "dependencies": [],
  "files_to_create": [],
  "files_to_modify": [],
  "tests_required": []
}
```
```

---

# 8. Code Development Prompts

## 8.1 Feature Development Prompt

```
{CODING_AGENT_PROMPT_FROM_PART2}

Additionally, for this specific feature:

**Story**: {STORY_TITLE}
**Acceptance Criteria**:
{CRITERIA}

**Technical Requirements**:
{TECH_REQUIREMENTS}

Implement this feature following:
1. Clean code principles
2. SOLID principles
3. Project coding standards
4. Test-driven development

Provide:
- Complete implementation code
- Unit tests
- Integration tests
- Documentation
```

---

# 9. Code Review Prompts

## 9.1 Code Review Prompt

```
{CODE_REVIEWER_AGENT_PROMPT_FROM_PART2}

Review this implementation:

**Files Changed**:
{FILES_LIST}

**Code**:
{CODE_DIFF}

**Original Requirements**:
{REQUIREMENTS}

Provide comprehensive review covering:
1. Functionality correctness
2. Code quality
3. Security issues
4. Performance concerns
5. Test coverage
6. Documentation

Rate quality 1-10 and suggest improvements.
```

---

# 10. Testing & QA Prompts

## 10.1 Test Case Generation

```
For this user story:
{STORY}

Generate comprehensive test cases covering:

**Unit Tests**:
- Happy path scenarios
- Edge cases
- Error scenarios

**Integration Tests**:
- API integration
- Database integration
- External service integration

**E2E Tests**:
- Complete user flows
- Multi-step scenarios

For each test case:
```json
{
  "test_id": "TC-001",
  "test_type": "unit|integration|e2e",
  "description": "...",
  "preconditions": [],
  "steps": [],
  "expected_result": "...",
  "priority": "Critical|High|Medium|Low"
}
```
```

## 10.2 QA Verification Prompt

```
Verify this implementation meets all requirements:

**Story**: {STORY}
**Acceptance Criteria**: {CRITERIA}
**Implementation**: {IMPLEMENTATION_DETAILS}
**Test Results**: {TEST_RESULTS}

Perform QA verification:
1. Functional correctness
2. UI/UX quality
3. Performance
4. Security
5. Accessibility
6. Browser compatibility
7. Mobile responsiveness

Rate quality 1-10 and identify any issues.
```

---

# ✅ Summary

This library contains **ready-to-use prompts** for:

1. ✅ BA Agent (complete system prompt)
2. ✅ Requirements Elicitation (all phases)
3. ✅ Document Generation (Scope, SRS, BRD)
4. ✅ User Stories Generation
5. ✅ Project Management
6. ✅ Sprint Planning
7. ✅ Task Breakdown
8. ✅ Code Development
9. ✅ Code Review
10. ✅ Testing & QA

**All prompts are production-ready and can be used immediately!**
