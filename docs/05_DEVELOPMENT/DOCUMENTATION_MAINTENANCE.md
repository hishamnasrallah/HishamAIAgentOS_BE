---
title: "Documentation Maintenance Guide"
description: "**Purpose:** Detailed instructions for updating documentation after code changes"

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Technical Writer
    - Developer
  secondary:
    - Project Manager
    - CTO / Technical Lead
    - AI Agent

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

related:
  - 01_CORE/DOCUMENTATION_STANDARDS.md
see_also:
  - DOCUMENTATION_WRITING_GUIDELINES.md
depends_on:
  - 01_CORE/DOCUMENTATION_STANDARDS.md
prerequisite_for: []

aliases: []

changelog:
  - version: "1.0"
    date: "2025-12-06"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---

# Documentation Maintenance Guide
## How to Keep Documentation in Sync with Code Changes

**Purpose:** Detailed instructions for updating documentation after code changes  
**Critical:** Documentation MUST be updated after every development task

---

## 📋 Overview

This guide provides step-by-step instructions for maintaining documentation consistency. **You are responsible for keeping all documentation up-to-date - the user will not check this manually.**

**⚠️ IMPORTANT:** All new and updated documents MUST follow the new Metadata standards. See [Documentation Metadata Requirements](#documentation-metadata-requirements) below.

**📖 Full Writing Guidelines:** See `docs/01_CORE/DOCUMENTATION_WRITING_GUIDELINES.md` for complete instructions on creating new documents with Metadata.

---

## 📋 Documentation Metadata Requirements

**⚠️ CRITICAL:** Every document MUST include complete YAML frontmatter with the following structure:

```yaml
---
title: "[Document Title]"
description: "[2-3 sentence description]"
category: "[Core|Design|Testing|Development|Deployment|Planning|Tracking|Commands|Phases]"
language: "[ar|en]"
original_language: "[ar|en]"

purpose: |
  [1-2 paragraph explanation]

target_audience:
  primary:
    - [Role 1]  # 1-2 roles maximum
    - [Role 2]
  secondary:
    - [Role 3]  # Multiple allowed
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
  # ... 10+ tags recommended

status: "active"
priority: "high"
difficulty: "intermediate"
completeness: "100%"

version: "1.0"
last_updated: "YYYY-MM-DD"
last_reviewed: "YYYY-MM-DD"
author: "[Name]"
maintainer: "[Name]"

changelog:
  - version: "1.0"
    date: "YYYY-MM-DD"
    changes: "[Description]"
    author: "[Name]"
---
```

**For detailed instructions and templates, see:**
- `docs/01_CORE/DOCUMENTATION_WRITING_GUIDELINES.md` - Complete writing guide
- `docs/01_CORE/TEMPLATES/` - Templates and examples
- Existing documentation files for examples

---

## 🔄 Documentation Update Workflow

### After Completing ANY Development Task:

1. **Update Project Tracking Documents** (REQUIRED) ⚠️ **NEW**
2. **Update Task Status** (REQUIRED)
3. **Create Manual Test Checklist** (REQUIRED for phase completion) ⚠️ **NEW**
4. **Update Expected Output Files** (if applicable)
5. **Update Comprehensive Audit** (REQUIRED)
6. **Update Blockers** (if applicable)
7. **Update README** (if major changes)
8. **Re-check Everything** (REQUIRED)

---

## 1. Update Project Tracking Documents ⚠️ **REQUIRED - ALWAYS UPDATE**

**CRITICAL: These documents must be updated to stay on track!**

### A. Update Phase Status Summary

**File:** `docs/07_TRACKING/PHASE_STATUS_SUMMARY.md`

**When to Update:**
- ✅ After completing any feature or task
- ✅ After completing a phase
- ✅ When status changes (Not Implemented → Partially → Done)

**What to Update:**

1. **Feature/Task Status Table**
   ```markdown
   | Feature/Task | Status | Notes |
   |--------------|--------|-------|
   | Command Library | ⚠️ Partially | 30/325 commands (9.2%) |
   ```

2. **Overall Statistics Table**
   ```markdown
   | Category | Done | Partially | Not Implemented | Total | Completion % |
   |----------|------|-----------|------------------|-------|--------------|
   | **Commands** | 30 | 0 | 295 | 325 | 9.2% |
   ```

**Steps:**
1. Open `docs/07_TRACKING/PHASE_STATUS_SUMMARY.md`
2. Find the relevant phase section
3. Update feature/task status (Done/Partially/Not Implemented)
4. Update overall statistics table
5. Update completion percentages

---

### B. Update Project Roadmap

**File:** `docs/07_TRACKING/PROJECT_ROADMAP.md`

**When to Update:**
- ✅ After completing roadmap tasks
- ✅ When milestones are reached
- ✅ When priorities change
- ✅ When timeline needs adjustment

**What to Update:**

1. **Task Completion Status**
   ```markdown
   #### Tasks:
   1. **Load Command Library** 🔴
      - [x] Create script to load commands from prompts library
      - [x] Load at least 50 high-priority commands
      - [ ] Target: 100 commands by end of week 2
   ```

2. **Success Metrics**
   ```markdown
   ### Phase 1 Success Metrics
   - [x] Command library: 30%+ (100/325 commands)
   - [ ] Security: 100% (encryption + 2FA)
   - [ ] Test coverage: 70%+
   ```

3. **Milestones**
   ```markdown
   ### Milestone 1: MVP Ready (End of Week 4)
   - [x] Command library at 30%+ (100 commands)
   - [ ] All security issues resolved
   - [ ] Command endpoints tested
   ```

**Steps:**
1. Open `docs/07_TRACKING/PROJECT_ROADMAP.md`
2. Find the relevant phase/task section
3. Mark completed items with `[x]`
4. Update success metrics
5. Update milestone status if applicable

---

### C. Update Immediate Next Steps

**File:** `docs/07_TRACKING/IMMEDIATE_NEXT_STEPS.md`

**When to Update:**
- ✅ After completing immediate action items
- ✅ When next steps change
- ✅ When priorities shift

**What to Update:**

1. **Step Completion Status**
   ```markdown
   ## 📋 Step 2: Expand Command Library (Week 1-2) 🔴 CRITICAL

   ### Task 2.1: Enhance Command Loading Script
   - [x] Review existing script structure
   - [x] Add more command templates (target: 100 commands)
   - [x] Organize by category
   ```

2. **Success Metrics**
   ```markdown
   ## 📊 Success Metrics (End of Week 1)

   - [x] Command library: 30+ commands loaded (from 5 to 30+)
   - [ ] Command endpoints: All tested and working
   - [ ] SQLite migration: Fixed
   ```

**Steps:**
1. Open `docs/07_TRACKING/IMMEDIATE_NEXT_STEPS.md`
2. Find the relevant step/task
3. Mark completed items with `[x]`
4. Update success metrics
5. Update next steps if priorities changed

---

## 2. Create/Update Manual Test Checklist ⚠️ **REQUIRED - ALWAYS UPDATE**

**File Location:** `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/PHASE_{N}_TESTING.md`

**When to Create/Update:**
- ✅ After completing ANY feature implementation
- ✅ After completing a phase implementation
- ✅ After completing significant phase milestones (50%+, major features)
- ✅ When phase status changes from "Not Implemented" to "Partially" or "Done"
- ✅ **ALWAYS when adding new API endpoints or frontend components**

**File Naming:**
- Single phase: `PHASE_{N}_TESTING.md` (e.g., `PHASE_2_AUTHENTICATION_TESTING.md`)
- Multi-phase: `PHASE_{N}_{N+1}_TESTING.md` (e.g., `PHASE_13_14_CHAT_INTERFACE_TESTING.md`)

**Required Sections:**

1. **Pre-Testing Setup**
   - Backend server requirements
   - Frontend server requirements
   - Database setup
   - Prerequisites checklist

2. **Backend Django Admin Testing** (if applicable)
   - Model admin interfaces
   - CRUD operations
   - Search and filters
   - Data validation

3. **Backend API Testing**
   - All API endpoints
   - Request/response validation
   - Error handling
   - Authentication/authorization

4. **Frontend Testing** (if applicable)
   - UI components
   - User interactions
   - Form validation
   - Navigation
   - Real-time features (if applicable)

5. **Security Testing**
   - Access control
   - Data protection
   - Input validation
   - Self-protection mechanisms

6. **Error Handling**
   - Network errors
   - Server errors
   - Validation errors
   - Edge cases

7. **Integration Testing**
   - End-to-end workflows
   - Backend-frontend integration
   - Real-time features (if applicable)

8. **Final Verification**
   - Complete workflows
   - Sign-off section

**Format Template:**

```markdown
# Phase {N}: [Phase Name] - Manual Testing Checklist

**Date:** [Date]
**Component:** [Component Name]
**Phase:** Phase {N}
**Status:** ✅ Complete / ⚠️ Partially Complete / ❌ Not Implemented

---

## 📋 Pre-Testing Setup

- [ ] Backend server is running
- [ ] Frontend server is running (if applicable)
- [ ] Database migrations applied
- [ ] Prerequisites checklist

---

## [Section Name] Testing

### [Subsection]

#### [Test Item]
- [ ] Test description
- [ ] Expected behavior
- [ ] Actual result

---

## ✅ Final Verification

### Complete Workflows
- [ ] Workflow 1
- [ ] Workflow 2

---

## 📝 Notes & Issues

**Date:** _______________
**Tester:** _______________
**Environment:** _______________

### Issues Found:
1. 
2. 

---

## ✅ Sign-Off

- [ ] All tests passed
- [ ] Complete workflows tested

**Tester Signature:** _______________
**Date:** _______________
```

**Steps:**

1. Check if test checklist already exists for the phase
2. **If exists, UPDATE it with new features/endpoints** ⚠️ **CRITICAL**
3. If doesn't exist, create new file using template above
4. **Add test cases for ALL new features:**
   - New API endpoints
   - New frontend components
   - New user workflows
   - New error scenarios
5. Reference existing checklists for format:
   - `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/PHASE_1_DATABASE_MODELS_TESTING.md`
   - `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/PHASE_2_AUTHENTICATION_TESTING.md`
   - `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/PHASE_17_18_ADMIN_UI_COMPREHENSIVE_TESTING.md`
6. Update `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/README.md` if new checklist created:
   - Mark checklist as complete in the index
   - Update test coverage status table

**Reference Files:**
- Format examples: `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/PHASE_*.md`
- Index: `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/README.md`

**Important Notes:**
- ⚠️ **Test checklists MUST be updated whenever new features are added**
- Test checklists must be comprehensive and cover all features
- Include both positive and negative test cases
- Document all API endpoints (including new ones)
- Include security and error handling tests
- Follow the same format as existing checklists
- **Do not wait for phase completion - update incrementally**

---

## 3. Update Task Status

**File:** `docs/07_TRACKING/tasks.md`

### Steps:

1. Find your task in the file
2. Update the status marker:
   - `[ ]` → `[/]` (when starting)
   - `[/]` → `[x]` (when complete)
   - `[ ]` → `[!]` (if blocked)

3. Add completion details:
   ```markdown
   - [x] 6.4.1: Create execution serializers
     - **Acceptance:** CommandExecutionRequestSerializer, CommandExecutionResponseSerializer
     - **Completed:** December 4, 2024
     - **Files:** backend/apps/commands/serializers.py
     - **Notes:** Added validation for required parameters
   ```

4. If task was blocked, add blocker reference:
   ```markdown
   - [!] 6.5.1: Load 50 commands
     - **Blocked By:** BLOCKER-001
     - **Reason:** Waiting for command generation script
   ```

---

## 4. Create/Update Expected Output Files ⚠️ **REQUIRED - ALWAYS UPDATE**

**Location:** `docs/07_TRACKING/expected_output/`

### When to Create/Update:

- ✅ **New API endpoints added** ⚠️ **ALWAYS UPDATE**
- ✅ **New features implemented** ⚠️ **ALWAYS UPDATE**
- ✅ **New components created** ⚠️ **ALWAYS UPDATE**
- ✅ Phase completion
- ✅ **After ANY development work that adds functionality**

### File Naming:

- `phase_{N}_expected.md` for phase-specific outputs
- `phase_{N}_{N+1}_expected.md` for multi-phase outputs

### Template:

```markdown
# Phase X: [Name] - Expected Output

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## API Endpoints
| Method | Endpoint | Expected Response |
|--------|----------|-------------------|
| GET | /api/v1/... | {...} |

## Test Scenarios

### Scenario 1: [Name]
**Setup:**
- Step 1
- Step 2

**Execution:**
```bash
curl ...
```

**Expected Output:**
```json
{...}
```

**Validation:**
- Check 1
- Check 2

## Final Checklist
- [ ] All endpoints respond correctly
- [ ] Data persists to database
- [ ] Tests pass
```

### Steps:

1. Check if expected output file exists for your phase
2. **If exists, UPDATE it with new endpoints/features** ⚠️ **CRITICAL**
3. If doesn't exist, create it using the template
4. **Add ALL new endpoints to the API Endpoints table**
5. **Add test scenarios for ALL new features**
6. **Add error handling scenarios for new features**
7. Update `docs/07_TRACKING/expected_output/index.md` if new file created

**Important Notes:**
- ⚠️ **CRITICAL:** Expected output files MUST be updated whenever new features are added
- ⚠️ **CRITICAL:** If document exists, you MUST update it with new endpoints/scenarios, not create a new one
- **Do not wait for phase completion - update incrementally**
- Include ALL new API endpoints with expected responses
- Include test scenarios for ALL new features
- Include error handling scenarios for ALL new features
- Include request/response examples for ALL new endpoints

---

## 5. Update Comprehensive Audit

**File:** `docs/07_TRACKING/COMPREHENSIVE_AUDIT.md`

### What to Update:

#### A. Phase Completion Status

If you completed a phase or significant portion:

```markdown
### Phase 6: Command Library System ⚠️ 40% COMPLETE (INFRASTRUCTURE ONLY)

#### Tasks Audit
- **Total Tasks:** 27
- **Completed:** 15 ✅
- **Partial:** 3 ⚠️
- **Missing:** 9 ❌
```

#### B. Implementation Verification Tables

Update the relevant table:

```markdown
| Component | Expected | Actual | Status |
|-----------|----------|--------|--------|
| **CommandExecutor** | Full execution pipeline | ✅ `command_executor.py` (200 lines) | ✅ |
```

#### C. API Endpoints List

If you added new endpoints:

```markdown
| Endpoint | Method | Status | Tested |
|----------|--------|--------|--------|
| `/api/v1/commands/{id}/execute/` | POST | ✅ | ✅ |
```

#### D. Component Counts (Frontend)

If you added frontend components:

```markdown
| Component | Expected | Actual | Status |
|-----------|----------|--------|--------|
| **NewComponent** | Component description | ✅ `NewComponent.tsx` | ✅ |
```

#### E. Overall Statistics

Update the summary tables:

```markdown
| Category | Complete | Partial | Missing | Total | Completion % |
|----------|----------|---------|---------|-------|--------------|
| **API Endpoints** | 50 | 0 | 8 | 58 | 86% |
```

### Steps:

1. Open `docs/07_TRACKING/COMPREHENSIVE_AUDIT.md`
2. Find the relevant phase section
3. Update task counts
4. Update implementation verification tables
5. Update API endpoints list (if applicable)
6. Update component counts (if frontend work)
7. Update overall statistics at the top
8. Update completion percentages

---

## 6. Update Blockers

**File:** `docs/07_TRACKING/BLOCKERS.md`

### When to Update:

#### A. Resolving a Blocker:

1. Find the blocker entry
2. Move it to "✅ RESOLVED Blockers" section
3. Update status:
   ```markdown
   ### BLOCKER-001: Phase 6 - Command Library Incomplete
   **Status:** ✅ RESOLVED
   **Resolved:** December 4, 2024
   **Resolved By:** [Your name/identifier]
   
   **Solution:**
   - Created batch command generation script
   - Loaded 50 commands from prompts library
   - Verified command execution
   ```

4. Update blocker statistics at the bottom:
   ```markdown
   **Total Open:** 4 (down from 5)
   **Total Resolved:** 3 (up from 2)
   ```

#### B. Creating a New Blocker:

1. Add new entry with next BLOCKER-XXX number
2. Fill in all fields:
   ```markdown
   ### BLOCKER-005: [Title]
   **Status:** 🔴 OPEN
   **Priority:** HIGH
   **Phase:** [Phase number]
   **Opened:** [Date]
   **Owner:** [Your name]
   
   **Problem:**
   - Description of problem
   
   **Impact:**
   - Impact description
   
   **Root Cause:**
   - Root cause analysis
   
   **Next Steps:**
   1. Step 1
   2. Step 2
   
   **Related Tasks:** [Task numbers]
   **Related Files:**
   - `path/to/file.py`
   ```

3. Update statistics

---

## 7. Update README

**File:** `README.md`

### When to Update:

- ✅ New API endpoints added
- ✅ New features completed
- ✅ Setup instructions changed
- ✅ New dependencies added
- ✅ Major architectural changes

### What to Update:

#### A. API Endpoints Section

If you added new endpoints:

```markdown
### Commands API
- `POST /api/v1/commands/{id}/execute/` - Execute a command
- `POST /api/v1/commands/{id}/preview/` - Preview command execution
```

#### B. Feature List

If you completed a major feature:

```markdown
### ✅ Phase 6: Command Library System
- ✅ Command execution infrastructure
- ✅ Parameter validation
- ✅ Template rendering
- ✅ Command registry
```

#### C. Setup Instructions

If setup changed:

```markdown
### 3. Run Development Server

```bash
# Start Django server
python manage.py runserver

# Start Celery worker (if needed)
celery -A core worker -l info
```
```

---

## 8. Re-check Everything

### Final Documentation Check:

Before saying "done", verify:

1. **Project Tracking Documents** ⚠️ **NEW - REQUIRED**
   - [ ] `docs/07_TRACKING/STATUS/PHASE_STATUS_SUMMARY.md` - Phase/feature status updated
   - [ ] `docs/07_TRACKING/STATUS/PROJECT_ROADMAP.md` - Roadmap tasks marked complete
   - [ ] `docs/07_TRACKING/STATUS/IMMEDIATE_NEXT_STEPS.md` - Next steps updated
   - [ ] Statistics and completion percentages recalculated

2. **Task Status**
   - [ ] Task marked complete in `docs/07_TRACKING/tasks.md`
   - [ ] Completion date added
   - [ ] Files listed
   - [ ] Notes added

3. **Manual Test Checklist** ⚠️ **REQUIRED - ALWAYS UPDATE**
   - [ ] Test checklist created/updated in `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/`
   - [ ] **ALL new API endpoints added to checklist** ⚠️ **CRITICAL**
   - [ ] **ALL new frontend components added to checklist** ⚠️ **CRITICAL**
   - [ ] **ALL new features have test cases** ⚠️ **CRITICAL**
   - [ ] All required sections included
   - [ ] Format matches existing checklists
   - [ ] README index updated (if new checklist created)

4. **Expected Output Document** ⚠️ **REQUIRED - ALWAYS UPDATE**
   - [ ] Expected output file exists (if applicable)
   - [ ] **ALL new API endpoints added to API Endpoints table** ⚠️ **CRITICAL**
   - [ ] **ALL new features have test scenarios** ⚠️ **CRITICAL**
   - [ ] **ALL new features have error handling scenarios** ⚠️ **CRITICAL**
   - [ ] Expected output file is complete and up-to-date
   - [ ] Index updated (if new file created)

5. **Comprehensive Audit**
   - [ ] Phase section updated
   - [ ] Task counts updated
   - [ ] Implementation tables updated
   - [ ] API endpoints list updated (if applicable)
   - [ ] Component counts updated (if frontend)
   - [ ] Overall statistics updated

6. **Blockers**
   - [ ] Resolved blockers moved to "RESOLVED" section
   - [ ] Statistics updated
   - [ ] New blockers added (if any)

7. **README**
   - [ ] API endpoints updated (if applicable)
   - [ ] Features updated (if major)
   - [ ] Setup instructions updated (if changed)

6. **File Verification**
   - [ ] All created files documented
   - [ ] All modified files documented
   - [ ] No temporary files left behind

---

## 📝 Documentation Update Checklist Template

Use this checklist after every task:

```markdown
## Documentation Update Checklist

### Project Tracking Documents ⚠️ **NEW**
- [ ] `docs/07_TRACKING/PHASE_STATUS_SUMMARY.md` - Status updated
- [ ] `docs/07_TRACKING/PROJECT_ROADMAP.md` - Tasks marked complete
- [ ] `docs/07_TRACKING/IMMEDIATE_NEXT_STEPS.md` - Next steps updated

### Task Status
- [ ] Task marked complete in `docs/07_TRACKING/tasks.md`
- [ ] Completion date added
- [ ] Files listed
- [ ] Notes added

### Manual Test Checklist ⚠️ **NEW - REQUIRED FOR PHASE COMPLETION**
- [ ] Test checklist created/updated in `docs/03_TESTING/manual_test_checklist/`
- [ ] All required sections included (Admin, API, Frontend, Security, etc.)
- [ ] Format matches existing checklists
- [ ] README index updated

### Expected Output
- [ ] Expected output file created/updated
- [ ] Index updated (if new file)

### Comprehensive Audit
- [ ] Phase section updated
- [ ] Task counts updated
- [ ] Implementation tables updated
- [ ] API endpoints updated (if applicable)
- [ ] Component counts updated (if frontend)
- [ ] Overall statistics updated

### Blockers
- [ ] Resolved blockers updated
- [ ] New blockers added (if any)
- [ ] Statistics updated

### README
- [ ] API endpoints updated (if applicable)
- [ ] Features updated (if major)
- [ ] Setup instructions updated (if changed)

### Final Verification
- [ ] All documentation files reviewed
- [ ] No missed updates
- [ ] All file paths verified
```

---

## 🎯 Quick Reference: File Locations

| Document Type | File Path |
|---------------|-----------|
| Phase Status Summary | `docs/07_TRACKING/PHASE_STATUS_SUMMARY.md` ⚠️ **READ FIRST** |
| Project Roadmap | `docs/07_TRACKING/PROJECT_ROADMAP.md` ⚠️ **READ FIRST** |
| Immediate Next Steps | `docs/07_TRACKING/IMMEDIATE_NEXT_STEPS.md` ⚠️ **READ FIRST** |
| Task Tracking | `docs/07_TRACKING/tasks.md` |
| Comprehensive Audit | `docs/07_TRACKING/COMPREHENSIVE_AUDIT.md` |
| Blockers | `docs/07_TRACKING/BLOCKERS.md` |
| Expected Outputs | `docs/07_TRACKING/expected_output/phase_{N}_expected.md` |
| Expected Output Index | `docs/07_TRACKING/expected_output/index.md` |
| Manual Test Checklists | `docs/03_TESTING/manual_test_checklist/PHASE_{N}_TESTING.md` ⚠️ **NEW** |
| Test Checklist Index | `docs/03_TESTING/manual_test_checklist/README.md` ⚠️ **NEW** |
| README | `README.md` |
| Design Documents | `docs/hishamos_complete_design_part{N}.md` |

---

## ⚠️ Common Documentation Mistakes

1. **❌ Forgetting to Update Audit File**
   - Always update `COMPREHENSIVE_AUDIT.md`
   - Update completion percentages
   - Update statistics

2. **❌ Not Creating Expected Output Files**
   - Create expected output for new phases
   - Update existing expected output files

3. **❌ Not Updating Task Status**
   - Always mark tasks complete
   - Add completion details

4. **❌ Not Resolving Blockers**
   - Move resolved blockers to "RESOLVED" section
   - Update statistics

5. **❌ Not Re-checking**
   - Always do final verification
   - Check for missed updates

---

## 🚀 Automation Tips

While documentation must be updated manually, you can:

1. **Keep a Checklist**
   - Use the checklist template above
   - Check off items as you complete them

2. **Document as You Go**
   - Update documentation incrementally
   - Don't wait until the end

3. **Review Before Completion**
   - Always do final review
   - Verify nothing was missed

---

## 📞 Summary

**Remember:**
- Documentation updates are MANDATORY, not optional
- The user will NOT check documentation - you are responsible
- Always do final verification before saying "done"
- Use the checklist to ensure nothing is missed

**Critical Files to Always Update:**
1. `docs/07_TRACKING/STATUS/PHASE_STATUS_SUMMARY.md` - Phase/feature status ⚠️ **REQUIRED**
2. `docs/07_TRACKING/STATUS/PROJECT_ROADMAP.md` - Roadmap progress ⚠️ **REQUIRED**
3. `docs/07_TRACKING/STATUS/IMMEDIATE_NEXT_STEPS.md` - Next steps ⚠️ **REQUIRED**
4. `docs/07_TRACKING/tasks.md` - Task status ⚠️ **REQUIRED**
5. `docs/03_TESTING/MANUAL_TEST_CHECKLISTS/PHASE_{N}_TESTING.md` - Manual test checklist ⚠️ **ALWAYS REQUIRED - MUST UPDATE WITH NEW FEATURES**
6. `docs/07_TRACKING/expected_output/phase_{N}_expected.md` - Expected output document ⚠️ **ALWAYS REQUIRED - MUST UPDATE WITH NEW FEATURES**
7. `docs/07_TRACKING/COMPREHENSIVE_AUDIT.md` - Implementation audit ⚠️ **REQUIRED**
8. `docs/07_TRACKING/BLOCKERS.md` (if blockers resolved)

---

**Last Updated:** December 2024  
**Version:** 1.0

