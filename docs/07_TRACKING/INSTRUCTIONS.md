---
title: "HishamOS Tracking System - Instructions for AI Agents"
description: "**Version:** 1.0"

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

# HishamOS Tracking System - Instructions for AI Agents

**Version:** 1.0  
**Last Updated:** December 1, 2024  
**Purpose:** Master guide for AI agents working on HishamOS development

---

## 🤖 For AI Agents: How to Use This Tracking System

This tracking system is designed to enable **any AI agent** to pick up **any task** and complete it successfully **without needing full project context**.

---

## 📋 Quick Start Workflow

### When Assigned a Phase (e.g., "Implement Phase 7")

**Step 1: Read the Phase Document**
```
1. Open docs/07_TRACKING/phase_X_detailed.md
2. Read entire document (5-10 min equivalent)
3. Note the "Related Documents" section
```

**Step 2: Study Related Documents**
```
1. Open EVERY file listed in "📚 Related Documents & Source Files"
2. For implementation_plan.md: Read the specific line ranges mentioned
3. For design docs: Read relevant sections
4. Take notes on key requirements
```

**Step 3: Review Current Tasks**
```
1. Open docs/07_TRACKING/tasks.md
2. Find tasks for your phase
3. Check which are complete vs pending
4. Select next pending task
```

**Step 4: Implement**
```
1. Follow the task instructions
2. Reference the phase detailed doc for specs
3. Use source docs for deep technical details
4. Write tests as you go
```

**Step 5: Update Tracking**
```
1. Mark task as complete in tasks.md
2. Update index.md phase status if phase complete
3. Document what you did
4. Commit changes
```

---

## 📂 File Structure Guide

### Core Tracking Files

**index.md** - Project overview and progress matrix
- Shows status of all 30 phases
- Links to all phase documents
- Statistics and metrics
- Consequences and follow-up
- **UPDATE THIS:** When making major technical decisions

### Phase Documents

**phase_X_detailed.md** - Complete phase specifications
- Business requirements
- Technical specs
- Implementation guidance
- **Related Documents section** ← Read these files!
- Deliverables checklist
- Testing requirements

---

## 🎯 Golden Rules for AI Agents

### Rule 1: Always Read Related Documents FIRST
```
❌ DON'T: Jump straight to coding
✅ DO: Read all files in "Related Documents" section first
```

**Why:** Phase docs are summaries. Full details are in source docs.

### Rule 2: Update Tracking After Every Task
```
❌ DON'T: Complete 5 tasks then update tracking
✅ DO: Update tasks.md after EACH task completion
```

**Why:** Others may be working in parallel. Keep everyone synchronized.

### Rule 3: Tasks are Atomic - Don't Combine
```
❌ DON'T: "I'll do tasks 7.1, 7.2, and 7.3 together"
✅ DO: Complete 7.1, update tracking, then start 7.2
```

**Why:** Enables parallel work and clear progress tracking.

### Rule 4: Test Before Marking Complete
```
❌ DON'T: Mark task complete without testing
✅ DO: Run tests, verify acceptance criteria, THEN mark complete
```

**Why:** Quality over speed. Broken code blocks everyone.

### Rule 5: Document As You Go
```
❌ DON'T: "I'll document everything at the end"
✅ DO: Update docs while code is fresh in your mind
```

**Why:** Future agents (and humans) need to understand your work.

---

## 📖 How to Read Implementation Plan Line References

Phase docs reference specific lines in `implementation_plan.md`. Here's how to use them:

**Example from Phase 1:**
```markdown
Lines 301-421: User & Authentication models
```

**How to Use:**
1. Open `docs/06_PLANNING/IMPLEMENTATION/implementation_plan.md`
2. Navigate to line 301
3. Read through line 421
4. That section has the COMPLETE specification for User models

**Pro Tip:** Use your editor's "Go to Line" feature (Ctrl+G in most editors)

---

## 🔄 Standard Development Workflow

### For Backend Development

```
1. Read phase doc
2. Study related documents
3. Check current codebase state
4. Create/modify models (if needed)
5. Create services/business logic
6. Create serializers (DRF)
7. Create views/viewsets
8. Add URL routing
9. Write tests
10. Run tests
11. Update OpenAPI docs
12. Update tracking
13. Commit
```

### For Frontend Development

```
1. Read phase doc
2. Study related documents
3. Check design mockups
4. Create components
5. Add to pages
6. Connect to Redux store
7. Integrate with API
8. Style with Tailwind
9. Write tests
10. Test in browser
11. Update tracking
12. Commit
```

---

## 📝 Maintaining Tracking Files

These files MUST be kept up-to-date. Here's when to update each:

### After Completing EVERY Task:

**1. tasks.md**
```markdown
- [x] Task 7.1.2: Create workflow parser ✅
  Completed: 2024-12-01 14:30
  Files: backend/apps/workflows/services/workflow_parser.py
  Tests: tests/workflows/test_parser.py
```

**2. CHANGELOG.md**
```markdown
## [2024-12-01] Phase 7.1 - Workflow Parser
**Added:**
- WorkflowParser service with YAML/JSON validation
**Files:** backend/apps/workflows/services/workflow_parser.py
```

### When Encountering a Blocker:

**BLOCKERS.md**
```markdown
### BLOCKER-XXX: Brief Description
**Status:** 🔴 OPEN
**Priority:** CRITICAL/HIGH/MEDIUM/LOW
**Problem:** What's blocking progress
**Impact:** How this affects the project
**Next Steps:** What needs to happen
```

### When Making Technical Decisions:

**DECISIONS.md**
```markdown
## ADR-XXX: Decision Title
**Date:** 2024-12-01
**Status:** PROPOSED
**Context:** Why this decision matters
**Decision:** What we decided
**Rationale:** Why this choice
```

### When Phase Status Changes:

**index.md**
- Update phase completion percentage
- Update phase status (Complete/Partial/ Pending)
- Update statistics

### If Dependencies Change:

**DEPENDENCIES.md**
- Update prerequisite relationships
- Update parallel development opportunities
- Note any new blockers

---

## ✅ Task Completion Checklist

Before marking ANY task as complete:

- [ ] Code written and follows project standards
- [ ] Tests written and passing
- [ ] Documentation updated (code comments, docstrings)
- [ ] No linting errors
- [ ] Acceptance criteria met (check tasks.md)
- [ ] tasks.md updated with completion status
- [ ] index.md updated if phase complete
- [ ] Changes committed to git

---

## 🚨 Common Pitfalls to Avoid

### Pitfall 1: Not Reading Source Documents
**Problem:** Implementing based on phase doc summary only  
**Result:** Missing critical requirements  
**Solution:** ALWAYS read files in "Related Documents" section

### Pitfall 2: Working in Isolation
**Problem:** Not updating tracking files  
**Result:** Duplicate work, merge conflicts  
**Solution:** Update tasks.md after every task

### Pitfall 3: Skipping Tests
**Problem:** "Tests can wait until later"  
**Result:** Bugs discovered weeks later, hard to fix  
**Solution:** Write tests WHILE writing code

### Pitfall 4: Vague Task Completion
**Problem:** Marking task "mostly done"  
**Result:** Next agent doesn't know what's left  
**Solution:** Task is either 100% done or not done

### Pitfall 5: Not Following Line References
**Problem:** Guessing at implementation details  
**Result:** Incorrect implementation  
**Solution:** Read the EXACT lines referenced

---

## 🤝 Parallel Development Protocol

Multiple AI agents can work simultaneously if they follow these rules:

### 1. Task Assignment
- Each agent takes ONE task at a time
- Mark task as "In Progress" in tasks.md
- Add your agent ID/name to task

### 2. No Overlapping Work
- Don't work on same file as another agent
- If file needed, wait for other agent to finish
- Coordinate in tasks.md comments

### 3. Frequent Commits
- Commit after each task completion
- Pull latest before starting new task
- Resolve conflicts immediately

### 4. Communication
- Use tasks.md for async communication
- Add notes about blockers
- Document decisions

---

## 📊 How to Update Tracking Files

### Updating tasks.md

**When starting a task:**
```markdown
- [/] Task 7.1.2: Create workflow parser
  Assigned: Agent-123
  Started: 2024-12-01 13:00
```

**When completing a task:**
```markdown
- [x] Task 7.1.2: Create workflow parser
  Assigned: Agent-123
  Completed: 2024-12-01 14:30
  Files: backend/apps/workflows/services/workflow_parser.py
  Tests: tests/workflows/test_parser.py
```

### Updating index.md

**When phase completes:**
```markdown
Update the phase status table:
| Phase | Status | Progress |
|-------|--------|----------|
| 7     | ✅ Complete | 100% |
```

---

## 🎓 Best Practices

### 1. Context Isolation
**Principle:** Each task should be understandable in isolation

**Good Task:**
```
Task 7.1.2: Create workflow parser
- Read workflow YAML/JSON
- Validate schema
- Return ParsedWorkflow object
- Handle errors gracefully
Acceptance: Can parse valid workflow, rejects invalid
```

**Bad Task:**
```
Task 7.1.2: Do the parser thing
```

### 2. Incremental Progress
**Principle:** Small, frequent completions > Large, infrequent ones

**Do:** Complete 5 small tasks in a day  
**Don't:** Complete 1 massive task in a week

### 3. Documentation First
**Principle:** When in doubt, over-document

**Do:** Explain WHY you made a decision  
**Don't:** Just write code with no comments

### 4. Test Coverage
**Principle:** If it's not tested, it's broken

**Do:** Write tests for happy path + edge cases  
**Don't:** Only write tests for happy path

---

## 🔍 Finding Information

### "Where do I find..."

**...business requirements?**
→ Phase detailed doc "Business Requirements" section  
→ Related docs: `01_BA_Artifacts.md`, `02_User_Stories.md`

**...technical specifications?**
→ Phase detailed doc "Technical Specifications" section  
→ Related docs: `03_Technical_Architecture.md`, design docs

**...implementation details?**
→ `implementation_plan.md` (use line numbers from phase doc)

**...existing code examples?**
→ Completion docs from previous phases  
→ `WALKTHROUGH.md` for code samples

**...test examples?**
→ `PHASE_3_TESTING_GUIDE.md`  
→ Existing test files in `tests/` directories

---

## 🆘 When You're Stuck

### Step 1: Check Related Documents
Most answers are in the source docs referenced in phase detailed files.

### Step 2: Review Previous Phases
Similar functionality might exist in earlier phases. Check completion docs.

### Step 3: Consult Master Plan
`implementation_plan.md` has 1226 lines of detailed guidance.

### Step 4: Ask for Help
Add a note in tasks.md:
```markdown
- [ ] Task 7.1.2: Create workflow parser
  Status: BLOCKED
  Issue: Unclear how to handle circular dependencies
  Need: Clarification on workflow graph validation
```

---

## 📝 Example: Complete Task Execution

**Scenario:** You're assigned "Implement Phase 7, Task 7.1.1"

**Step-by-Step:**

```bash
1. Open docs/07_TRACKING/phase_7_detailed.md
   → Read entire document
   
2. Note Related Documents section lists:
   - docs/hishamos_complete_sdlc_roles_workflows.md
   - docs/06_PLANNING/IMPLEMENTATION/implementation_plan.md Lines 648-756
   
3. Open and read those documents
   → Understand workflow requirements
   → See exact model specifications
   
4. Open docs/07_TRACKING/tasks.md
   → Find "Task 7.1.1: Create Workflow models"
   → Read acceptance criteria
   
5. Check existing code:
   → backend/apps/workflows/models.py already exists (Phase 1)
   → Just need to add business logic methods
   
6. Implement:
   → Add save_state() method to WorkflowExecution
   → Add validation to Workflow model
   → Write docstrings
   
7. Test:
   → Write test_workflow_validation()
   → Run: pytest tests/workflows/
   → All pass ✅
   
8. Update tracking:
   docs/07_TRACKING/tasks.md:
   - [x] Task 7.1.1: Create Workflow models ✅
     Completed: 2024-12-01 15:00
     Files: backend/apps/workflows/models.py
     
9. Commit:
   git add .
   git commit -m "Phase 7, Task 7.1.1: Add workflow model methods"
   
10. Move to next task:
   → Task 7.1.2: Create workflow parser
```

---

## 🎯 Success Metrics

You're doing it right when:

- ✅ You can complete any task without asking questions
- ✅ Your code passes all tests first try
- ✅ Other agents can pick up where you left off
- ✅ tracking/ folder always shows current state
- ✅ No duplicate work across agents
- ✅ All tasks have clear completion status

---

## 🚀 Ready to Start?

1. Read this entire document ✅
2. Open `docs/07_TRACKING/index.md` to see project status
3. Open `docs/07_TRACKING/tasks.md` to see available tasks
4. Pick a task from your assigned phase
5. Follow the workflow above
6. Update tracking as you go
7. Ship quality code!

---

**Remember:** This system exists to make YOUR job easier. Use it, update it, and help improve it!

---

*Last Updated: December 1, 2024*  
*For questions or improvements, update this file and commit.*
