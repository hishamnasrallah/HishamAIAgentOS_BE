---
title: "HishamOS - Master Development Guide for AI Agents"
description: "دليل شامل ومتكامل للمطورين وAI Agents لتنفيذ ميزات في نظام HishamOS. يتضمن معايير التطوير، أفضل الممارسات، متطلبات التوثيق والاختبار."

category: "Development"
subcategory: "Guide"
language: "en"
original_language: "en"

purpose: |
  توفير دليل شامل ومتكامل للمطورين وAI Agents عند تطوير ميزات جديدة في HishamOS. يضمن اتباع المعايير وأفضل الممارسات في جميع مراحل التطوير.

target_audience:
  primary:
    - Developer
    - AI Agent
  secondary:
    - CTO / Technical Lead
    - Technical Writer
    - Project Manager

applicable_phases:
  primary:
    - Development
  secondary:
    - Planning
    - Testing

tags:
  - development
  - guide
  - master-guide
  - workflow
  - best-practices
  - code-standards
  - documentation
  - testing
  - ai-agent

keywords:
  - "development guide"
  - "دليل التطوير"
  - "workflow"
  - "best practices"

related_features:
  - "All HishamOS Features"

prerequisites:
  documents:
    - 06_PLANNING/TECHNICAL_ARCHITECTURE.md
    - 01_CORE/USER_GUIDES/WALKTHROUGH.md
  knowledge:
    - "Django Framework"
    - "React Framework"
    - "REST API Design"
  tools:
    - "Python 3.11+"
    - "Node.js 18+"
    - "Git"

status: "active"
priority: "critical"
difficulty: "intermediate"
completeness: "100%"
quality_status: "reviewed"

estimated_read_time: "45 minutes"
estimated_usage_time: "Ongoing reference"
estimated_update_time: "2 hours"

version: "1.0"
last_updated: "2024-12-06"
last_reviewed: "2024-12-06"
review_frequency: "monthly"
next_review_date: "2025-01-06"

author: "Development Team"
maintainer: "Technical Lead"
reviewer: "CTO"

related:
  - 05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md
  - 05_DEVELOPMENT/VERIFICATION_CHECKLIST.md
  - 06_PLANNING/TECHNICAL_ARCHITECTURE.md
see_also:
  - 01_CORE/STATUS/PROJECT_STATUS_DEC_2024.md
  - 07_TRACKING/STATUS/IMMEDIATE_NEXT_STEPS.md
depends_on:
  - 06_PLANNING/TECHNICAL_ARCHITECTURE.md
prerequisite_for: []

aliases:
  - "Development Guide"
  - "دليل التطوير"
  - "AI Agent Development Guide"

changelog:
  - version: "1.0"
    date: "2024-12-06"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---

# HishamOS - Master Development Guide for AI Agents
## Complete Instructions for Development Workflow

**Version:** 1.0  
**Last Updated:** December 2024  
**Purpose:** Comprehensive guide for AI agents to follow when developing features in HishamOS

---

## 📋 Table of Contents

1. [Pre-Development Checklist](#pre-development-checklist)
2. [Understanding the Project](#understanding-the-project)
3. [Development Workflow](#development-workflow)
4. [Code Standards & Best Practices](#code-standards--best-practices)
5. [Documentation Requirements](#documentation-requirements)
6. [Testing Requirements](#testing-requirements)
7. [Completion Verification](#completion-verification)
8. [Reference Documents](#reference-documents)

---

## 🎯 Pre-Development Checklist

Before starting any development task, you MUST:

1. ✅ **Check Project Status & Roadmap**
   - Read `docs/07_TRACKING/PHASE_STATUS_SUMMARY.md` to understand current phase status
   - Read `docs/07_TRACKING/PROJECT_ROADMAP.md` to understand priorities and timeline
   - Read `docs/07_TRACKING/IMMEDIATE_NEXT_STEPS.md` for immediate action items
   - Understand where your task fits in the overall roadmap

2. ✅ **Read the Task Assignment**
   - Check `docs/07_TRACKING/tasks.md` for your assigned task
   - Understand the acceptance criteria
   - Note the expected files and outputs

3. ✅ **Check for Blockers**
   - Review `docs/07_TRACKING/BLOCKERS.md` for any related blockers
   - Check if your task is blocked by another issue
   - If blocked, mark task as `[!]` and document the blocker

4. ✅ **Review Related Documentation**
   - Read the relevant design documents (see [Reference Documents](#reference-documents))
   - Understand the architecture and patterns
   - Check existing implementations for consistency

5. ✅ **Update Task Status**
   - Mark task as `[/]` (in progress) in `docs/07_TRACKING/tasks.md`
   - Add your name/identifier to the task
   - Note the start date

---

## 📚 Understanding the Project

### Project Structure

```
hishamAiAgentOS/
├── backend/                    # Django + FastAPI backend
│   ├── apps/                   # Django applications
│   │   ├── authentication/     # User auth, JWT, RBAC
│   │   ├── agents/             # AI agent management
│   │   ├── commands/           # Command library (350+)
│   │   ├── workflows/          # Workflow orchestration
│   │   ├── projects/           # Project & sprint management
│   │   ├── integrations/       # AI platform integrations
│   │   ├── results/            # Standardized output layer
│   │   ├── monitoring/         # System monitoring & logs
│   │   └── chat/              # Chat interface backend
│   ├── core/                   # Django settings
│   │   └── settings/           # Split settings (base, dev, prod, test)
│   └── requirements/           # Python dependencies
├── frontend/                   # React + TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom hooks
│   │   ├── stores/            # State management (Zustand)
│   │   └── services/          # API services
│   └── package.json
├── docs/                       # Documentation
│   ├── how_to_develop/        # This folder - Development guides
│   ├── tracking/              # Task tracking, blockers, audits
│   ├── design/                # Design documents
│   └── [other docs]
└── infrastructure/            # Docker & deployment (future)
```

### Technology Stack

**Backend:**
- Django 5.0.1
- Django REST Framework 3.14.0
- PostgreSQL 16 / SQLite (development)
- Redis 7 (caching, Celery)
- Celery 5.3.6 (background tasks)
- Channels 4.0.0 (WebSockets)

**Frontend:**
- React 18
- TypeScript
- Vite
- TailwindCSS
- Shadcn/UI
- Zustand (state management)
- React Query (@tanstack/react-query)

**AI Platforms:**
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude 3)
- Google (Gemini Pro)

---

## 🔄 Development Workflow

### Step 1: Task Analysis

1. **Read the Task Description**
   - Location: `docs/07_TRACKING/tasks.md`
   - Understand the acceptance criteria
   - Identify required files and components

2. **Check Design Documents**
   - Review relevant design parts (see [Reference Documents](#reference-documents))
   - Understand the expected architecture
   - Check for existing similar implementations

3. **Identify Dependencies**
   - What models/services/components already exist?
   - What needs to be created?
   - Are there any blockers?

### Step 2: Implementation Planning

1. **Create Implementation Plan**
   - Break down the task into sub-steps
   - Identify files to create/modify
   - Plan the code structure

2. **Check Existing Patterns**
   - Review similar implementations in the codebase
   - Follow existing patterns and conventions
   - Maintain consistency

### Step 3: Code Implementation

1. **Follow Code Standards** (see [Code Standards](#code-standards--best-practices))
2. **Write Clean, Documented Code**
3. **Handle Errors Properly**
4. **Add Type Hints** (Python) / TypeScript (Frontend)

### Step 4: Testing

1. **Write Tests** (see [Testing Requirements](#testing-requirements))
2. **Test Locally**
3. **Verify Acceptance Criteria**

### Step 5: Documentation Updates

**CRITICAL: You MUST update documentation after implementation!**

1. **Update Task Status**
   - Mark task as `[x]` (complete) in `docs/07_TRACKING/tasks.md`
   - Add completion date
   - Add completion notes

2. **Update Project Tracking Documents** ⚠️ **NEW - REQUIRED**
   - **Update `docs/07_TRACKING/PHASE_STATUS_SUMMARY.md`**
     - Update phase completion status if you completed a phase
     - Update feature/task status (Done/Partially/Not Implemented)
     - Update overall statistics table
   - **Update `docs/07_TRACKING/PROJECT_ROADMAP.md`**
     - Mark completed tasks in roadmap as done
     - Update timeline if needed
     - Update success metrics if milestones reached
   - **Update `docs/07_TRACKING/IMMEDIATE_NEXT_STEPS.md`**
     - Mark completed steps as done
     - Update next steps if priorities changed
     - Update success metrics

3. **Create/Update Manual Test Checklist** ⚠️ **REQUIRED - ALWAYS UPDATE**
   - **When:** After completing ANY feature implementation or phase milestone
   - **Location:** `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/PHASE_{N}_TESTING.md` or update existing checklist
   - **Format:** Follow existing test checklist format (see `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/README.md`)
   - **Content:** Must include:
     - Backend Django Admin Testing (if applicable)
     - Backend API Testing (all endpoints) - **MUST include new endpoints**
     - Frontend Testing (if applicable) - **MUST include new components**
     - Security Testing
     - Error Handling
     - Integration Testing
     - Complete Workflows
   - **Update:** Add new test cases for new features
   - **Update:** `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/README.md` if new checklist created
   - **Reference:** See existing checklists for format examples
   - **⚠️ CRITICAL:** Test checklist MUST be updated whenever new features are added, not just at phase completion
   - **⚠️ CRITICAL:** If checklist exists, you MUST update it with new test cases for new features/endpoints

4. **Create/Update Expected Output Document** ⚠️ **REQUIRED - ALWAYS UPDATE**
   - **When:** After completing ANY feature implementation or phase milestone
   - **Location:** `docs/07_TRACKING/expected_output/phase_{N}_expected.md` or update existing file
   - **Format:** Follow template in `docs/05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md`
   - **Content:** Must include:
     - Success Criteria
     - API Endpoints (all new endpoints) - **MUST include ALL new endpoints**
     - Test Scenarios (for new features) - **MUST include scenarios for ALL new features**
     - Error Handling Scenarios - **MUST include error cases for new features**
     - Validation Steps
   - **⚠️ CRITICAL:** Expected output document MUST be updated whenever new features/endpoints are added
   - **⚠️ CRITICAL:** If document exists, you MUST update it with new endpoints, scenarios, and error cases
   - **Update:** Add new endpoints and scenarios for new features
   - **⚠️ CRITICAL:** Expected output document MUST be updated whenever new features are added

5. **Update Related Documentation**
   - See `docs/05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md` for detailed instructions
   - Update audit file if needed

5. **Check for Other Updates**
   - Review `docs/07_TRACKING/COMPREHENSIVE_AUDIT.md`
   - Update if your changes affect completion status
   - Update BLOCKERS.md if you resolved a blocker

### Step 6: Verification

**BEFORE saying "done", you MUST:**

1. ✅ Complete the [Verification Checklist](#completion-verification)
2. ✅ Re-check all documentation updates
3. ✅ Verify no files were missed
4. ✅ Confirm acceptance criteria met

---

## 💻 Code Standards & Best Practices

### Python/Django Standards

1. **Code Style**
   - Follow PEP 8
   - Use Black for formatting (if configured)
   - Maximum line length: 100 characters

2. **Django Patterns**
   - Use ModelViewSets for CRUD operations
   - Use Serializers for validation
   - Follow Django REST Framework conventions
   
3. **DRF Serializers - CRITICAL FOR API DOCUMENTATION**
   - ⚠️ **NEVER define serializers inline inside ViewSet methods**
   - ⚠️ **ALWAYS define serializers at module level in `serializers.py`**
   - ⚠️ **This prevents drf-spectacular schema generation errors on Windows**
   
   **❌ WRONG - Causes OSError [Errno 22] on Windows:**
   ```python
   class TaskViewSet(viewsets.ModelViewSet):
       def get_serializer_class(self):
           class TaskSerializer(serializers.ModelSerializer):
               class Meta:
                   model = Task
                   fields = '__all__'
           return TaskSerializer
   ```
   
   **✅ CORRECT - Works on all platforms:**
   ```python
   # In serializers.py
   class TaskSerializer(serializers.ModelSerializer):
       class Meta:
           model = Task
           fields = '__all__'
   
   # In views.py
   class TaskViewSet(viewsets.ModelViewSet):
       serializer_class = TaskSerializer
   ```
   
   **Why this matters:**
   - Inline serializers break drf-spectacular schema generation
   - Windows file path handling causes `OSError [Errno 22] Invalid argument`
   - API documentation (Swagger/ReDoc) will fail to load
   - Always import and use serializers from `serializers.py`

4. **Type Hints**
   ```python
   def process_data(data: dict[str, Any]) -> dict[str, Any]:
       """Process input data and return result."""
       ...
   ```

5. **Docstrings**
   ```python
   def complex_function(param1: str, param2: int) -> bool:
       """
       Brief description of what the function does.
       
       Args:
           param1: Description of param1
           param2: Description of param2
       
       Returns:
           Description of return value
       
       Raises:
           ValueError: When param1 is invalid
       """
   ```

6. **Error Handling**
   - Always handle exceptions
   - Use specific exception types
   - Log errors appropriately
   - Return meaningful error messages

7. **Security**
   - Never hardcode secrets
   - Use environment variables
   - Validate all user input
   - Use parameterized queries (Django ORM does this automatically)
   - Sanitize output

### React/TypeScript Standards

1. **Component Structure**
   ```typescript
   interface ComponentProps {
     // Props interface
   }
   
   export const Component: React.FC<ComponentProps> = ({ prop1, prop2 }) => {
     // Component logic
     return (
       // JSX
     );
   };
   ```

2. **TypeScript**
   - Always use TypeScript types
   - Avoid `any` type
   - Use interfaces for props
   - Use enums for constants

3. **React Best Practices**
   - Use functional components
   - Use hooks for state management
   - Extract reusable logic to custom hooks
   - Use React Query for API calls

4. **Styling**
   - Use TailwindCSS classes
   - Use Shadcn/UI components when available
   - Follow existing component patterns

### File Organization

**Backend:**
```
backend/apps/{app_name}/
├── models.py          # Django models
├── serializers.py     # DRF serializers
├── views.py           # ViewSets and views
├── urls.py            # URL routing
├── admin.py           # Django admin
├── services/          # Business logic
│   └── service_name.py
├── utils/             # Utility functions
│   └── util_name.py
└── tests/             # Tests
    └── test_models.py
```

**Frontend:**
```
frontend/src/
├── components/        # Reusable components
│   ├── ui/           # Shadcn UI components
│   └── feature/      # Feature-specific components
├── pages/            # Page components
├── hooks/            # Custom hooks
├── stores/           # Zustand stores
├── services/         # API services
└── types/            # TypeScript types
```

---

## 📝 Documentation Requirements

**⚠️ NEW:** All documentation MUST follow the new Metadata standards. See `docs/01_CORE/DOCUMENTATION_WRITING_GUIDELINES.md` for complete instructions.

### Required Documentation Updates

After completing any development task, you MUST update:

1. **Task Tracking** (`docs/07_TRACKING/tasks.md`)
   - Mark task as complete `[x]`
   - Add completion date
   - Add completion notes
   - List created/modified files

2. **Manual Test Checklist** ⚠️ **NEW - REQUIRED FOR PHASE COMPLETION**
   - **When:** After completing a phase implementation (or significant phase milestone)
   - **Location:** `docs/03_TESTING/manual_test_checklist/PHASE_{N}_TESTING.md`
   - **Required Sections:**
     - Pre-Testing Setup
     - Backend Django Admin Testing (if applicable)
     - Backend API Testing (all endpoints)
     - Frontend Testing (if applicable)
     - Security Testing
     - Error Handling
     - Integration Testing
     - Final Verification
     - Notes & Issues
     - Sign-Off
   - **Format:** Follow existing test checklist format
   - **Reference:** See `docs/03_TESTING/manual_test_checklist/README.md` for examples
   - **Update:** Mark checklist as complete in README index

3. **Expected Output Files** (if applicable)
   - Location: `docs/07_TRACKING/expected_output/`
   - Create or update phase-specific expected output file
   - Document API endpoints, test scenarios, validation steps

4. **Comprehensive Audit** (`docs/07_TRACKING/COMPREHENSIVE_AUDIT.md`)
   - Update implementation status
   - Update completion percentages
   - Update API endpoints list if new endpoints added
   - Update component counts if frontend work

5. **BLOCKERS.md** (`docs/07_TRACKING/BLOCKERS.md`)
   - If you resolved a blocker, move it to "RESOLVED" section
   - Add resolution details
   - Update blocker statistics

6. **README.md** (if major changes)
   - Update API endpoints list
   - Update feature list
   - Update setup instructions if changed

### Documentation Update Process

**⚠️ NEW:** All documentation MUST follow the new Metadata standards!

**See detailed instructions in:**
- `docs/05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md` - Complete maintenance guide
- `docs/01_CORE/DOCUMENTATION_WRITING_GUIDELINES.md` - **Writing guidelines with Metadata requirements**
- Metadata examples in existing documentation files

#### Metadata Requirements for All Documentation

**All new and updated documents MUST include complete YAML frontmatter:**

```yaml
---
title: "[Document Title]"
description: "[2-3 sentence description]"
category: "[Core|Design|Testing|Development|Deployment|Planning|Tracking|Commands|Phases]"
language: "[ar|en]"
original_language: "[ar|en]"

purpose: |
  [1-2 paragraph explanation of document purpose]

target_audience:
  primary:
    - [Role 1]  # e.g., Developer, QA / Tester, Project Manager
    - [Role 2]  # Maximum 2 primary roles
  secondary:
    - [Role 3]  # Can have multiple secondary roles
    - [Role 4]

applicable_phases:
  primary:
    - [Phase 1]  # e.g., Development, Testing, Planning
    - [Phase 2]
  secondary:
    - [Phase 3]

tags:
  - [tag1]
  - [tag2]
  # ... 10+ comprehensive tags recommended

status: "[active|draft|deprecated]"
priority: "[critical|high|medium|low]"
difficulty: "[beginner|intermediate|advanced]"
completeness: "[percentage]"

version: "[X.Y]"
last_updated: "[YYYY-MM-DD]"
last_reviewed: "[YYYY-MM-DD]"
author: "[Author Name]"
maintainer: "[Maintainer Name]"

related: []
see_also: []
depends_on: []
prerequisite_for: []

changelog:
  - version: "[X.Y]"
    date: "[YYYY-MM-DD]"
    changes: "[Change description]"
    author: "[Author]"
---
```

**Quick Metadata Checklist:**
- [ ] ✅ All mandatory metadata fields filled
- [ ] ✅ `title` - Clear and descriptive
- [ ] ✅ `description` - 2-3 sentences
- [ ] ✅ `target_audience` - Primary (1-2 roles) + Secondary (multiple allowed)
- [ ] ✅ `applicable_phases` - Primary + Secondary phases
- [ ] ✅ `tags` - Comprehensive (10+ recommended)
- [ ] ✅ `category` - Correct category from list
- [ ] ✅ `version` - Updated when modifying existing docs (increment)
- [ ] ✅ `changelog` - Entry added for updates
- [ ] ✅ `last_updated` - Current date
- [ ] ✅ YAML frontmatter properly formatted (between `---` markers)

**Quick Checklist:**
- [ ] Task marked complete in tasks.md
- [ ] **Manual test checklist created/updated (if phase completion)** ⚠️ **NEW**
- [ ] Expected output file created/updated
- [ ] Audit file updated
- [ ] Blockers resolved (if applicable)
- [ ] README updated (if major changes)
- [ ] All file paths verified

---

## 🧪 Testing Requirements

### Backend Testing

1. **Unit Tests**
   - Test models, serializers, services
   - Use pytest
   - Target: 80%+ coverage

2. **Integration Tests**
   - Test API endpoints
   - Test workflows
   - Test agent execution

3. **Test Structure**
   ```python
   # tests/test_models.py
   import pytest
   from django.test import TestCase
   from apps.authentication.models import User
   
   class UserModelTest(TestCase):
       def test_user_creation(self):
           user = User.objects.create_user(
               email="test@example.com",
               username="testuser"
           )
           self.assertEqual(user.email, "test@example.com")
   ```

### Frontend Testing

1. **Component Tests**
   - Test component rendering
   - Test user interactions
   - Use React Testing Library

2. **E2E Tests**
   - Test complete user flows
   - Test API integration
   - Use Playwright or Cypress

### Testing Checklist

- [ ] Unit tests written
- [ ] Integration tests written
- [ ] All tests passing
- [ ] Test coverage acceptable (80%+)
- [ ] Edge cases tested
- [ ] Error cases tested

---

## ✅ Completion Verification

### Pre-Completion Checklist

**BEFORE saying "done" or "complete", verify:**

1. **Code Quality**
   - [ ] Code follows style guidelines
   - [ ] No linting errors
   - [ ] Type hints/TypeScript types added
   - [ ] Docstrings/comments added
   - [ ] Error handling implemented

2. **Functionality**
   - [ ] Acceptance criteria met
   - [ ] All features working
   - [ ] Edge cases handled
   - [ ] Error cases handled

3. **Testing**
   - [ ] Tests written
   - [ ] All tests passing
   - [ ] Coverage acceptable

4. **Documentation**
   - [ ] Task marked complete in tasks.md
   - [ ] **Manual test checklist created/updated (if phase completion)** ⚠️ **NEW**
   - [ ] Expected output file created/updated
   - [ ] Audit file updated
   - [ ] Blockers resolved (if applicable)
   - [ ] README updated (if needed)
   - [ ] **API Documentation verified** - Swagger/ReDoc accessible at `/api/docs/` and `/api/redoc/`

5. **Final Verification**
   - [ ] Re-read task acceptance criteria
   - [ ] Verify all files created/modified
   - [ ] Check for any missed documentation
   - [ ] Verify no broken references

### Verification Process

1. **Self-Review**
   - Review your code
   - Check documentation updates
   - Verify acceptance criteria

2. **Documentation Check**
   - Open `docs/07_TRACKING/tasks.md` - is task marked complete?
   - Open `docs/07_TRACKING/COMPREHENSIVE_AUDIT.md` - is it updated?
   - Open expected output file - does it exist and is it complete?
   - Open BLOCKERS.md - did you resolve any blockers?

3. **File Verification**
   - List all files you created
   - List all files you modified
   - Verify all files are in correct locations
   - Check for any temporary/test files that should be removed

4. **Final Statement**

Only after ALL checks pass, you can say:

```
✅ Task Complete

**Completed:**
- [List of what was completed]

**Files Created:**
- [List of new files]

**Files Modified:**
- [List of modified files]

**Documentation Updated:**
- docs/07_TRACKING/tasks.md
- docs/07_TRACKING/COMPREHENSIVE_AUDIT.md
- docs/03_TESTING/manual_test_checklist/PHASE_{N}_TESTING.md (if phase completion) ⚠️ **NEW**
- [Other updated docs]

**Testing:**
- [Test results]

**Verification:**
- ✅ Acceptance criteria met
- ✅ All documentation updated
- ✅ All tests passing
```

---

## 📖 Reference Documents

### Core Documentation

1. **Project Overview**
   - `README.md` - Project overview, quick start, API endpoints

2. **Design Documents**
   - `docs/hishamos_INDEX.md` - Master index of all design docs
   - `docs/hishamos_complete_design_part1.md` - Foundation & Architecture
   - `docs/hishamos_complete_design_part2.md` - Agents System (16 agents)
   - `docs/hishamos_complete_design_part3.md` - Commands & Workflows
   - `docs/hishamos_complete_design_part4.md` - Database & Integration
   - `docs/hishamos_complete_design_part5.md` - Monitoring & Infrastructure

3. **Critical Gaps Solutions**
   - `docs/hishamos_critical_gaps_solutions.md` - API Contracts, Dispatcher, Caching, State
   - `docs/hishamos_critical_gaps_solutions_part2.md` - Secrets, Alerting, Feedback Loop
   - `docs/hishamos_critical_gaps_solutions_part3.md` - Performance, API Docs, Deployment

4. **SDLC & Workflows**
   - `docs/hishamos_complete_sdlc_roles_workflows.md` - SDLC roles and workflows
   - `docs/hishamos_complete_prompts_library.md` - Complete prompts library
   - `docs/hishamos_ai_project_management.md` - AI project management system

5. **Tracking & Management** ⚠️ **UPDATED - READ THESE FIRST**
   - `docs/07_TRACKING/PHASE_STATUS_SUMMARY.md` - **High-level phase & feature status (READ FIRST)**
   - `docs/07_TRACKING/PROJECT_ROADMAP.md` - **12-week roadmap with priorities (READ FIRST)**
   - `docs/07_TRACKING/IMMEDIATE_NEXT_STEPS.md` - **Immediate action items (READ FIRST)**
   - `docs/07_TRACKING/tasks.md` - All tasks with status
   - `docs/07_TRACKING/BLOCKERS.md` - Current blockers and issues
   - `docs/07_TRACKING/COMPREHENSIVE_AUDIT.md` - Complete implementation audit
   - `docs/07_TRACKING/index.md` - Tracking index

6. **Expected Outputs**
   - `docs/07_TRACKING/expected_output/index.md` - Expected outputs index
   - `docs/07_TRACKING/expected_output/phase_17_18_expected.md` - Example expected output

7. **Development Guides** (This Folder)
   - `docs/05_DEVELOPMENT/MASTER_DEVELOPMENT_GUIDE.md` - This file
   - `docs/05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md` - Doc update instructions
   - `docs/05_DEVELOPMENT/VERIFICATION_CHECKLIST.md` - Pre-completion checklist

### Phase-Specific Documentation

- `docs/PHASE_3_COMPLETION.md` - Phase 3 completion details
- `docs/07_TRACKING/PHASE_17_18_IMPLEMENTATION_PLAN.md` - Phase 17-18 plan
- `docs/PROJECT_MANAGEMENT_USER_GUIDE.md` - User guide

### Code Reference

- `backend/apps/*/models.py` - Database models
- `backend/apps/*/views.py` - API views
- `backend/apps/*/serializers.py` - Serializers
- `frontend/src/components/` - React components
- `frontend/src/pages/` - Page components

---

## 🚨 Common Mistakes to Avoid

1. **❌ Not Updating Documentation**
   - Always update tasks.md, audit file, expected outputs
   - Don't skip documentation updates

2. **❌ Not Following Patterns**
   - Check existing code before creating new
   - Maintain consistency

3. **❌ Not Testing**
   - Write tests for your code
   - Test edge cases and errors

4. **❌ Not Verifying Completion**
   - Always complete verification checklist
   - Don't say "done" without verification

5. **❌ Breaking Existing Functionality**
   - Test that existing features still work
   - Be careful with migrations

6. **❌ Not Handling Errors**
   - Always handle exceptions
   - Return meaningful error messages

7. **❌ Hardcoding Values**
   - Use environment variables
   - Use configuration files

---

## 📞 Getting Help

If you encounter issues:

1. **Check Documentation**
   - Review relevant design docs
   - Check BLOCKERS.md for known issues
   - Review similar implementations

2. **Check Existing Code**
   - Look for similar features
   - Follow existing patterns
   - Check test files for examples

3. **Document the Issue**
   - If it's a blocker, add to BLOCKERS.md
   - Mark task as `[!]` (blocked)
   - Document what you tried

---

## 🎯 Summary

**Remember:**
1. ✅ Read task and understand requirements
2. ✅ Follow code standards and patterns
3. ✅ Write tests
4. ✅ **UPDATE ALL DOCUMENTATION** (critical!)
5. ✅ **CREATE MANUAL TEST CHECKLIST** (when completing a phase) ⚠️ **NEW**
6. ✅ Verify completion before saying "done"
7. ✅ Re-check for missed updates

**The user will NOT check documentation updates - you are responsible for keeping everything in sync!**

---

**Last Updated:** December 2024  
**Maintainer:** Development Team  
**Version:** 1.0

