---
title: "Pre-Completion Verification Checklist"
description: "**Purpose:** Ensure nothing is missed before marking a task as complete"

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Developer
    - QA / Tester
  secondary:
    - Project Manager
    - CTO / Technical Lead

applicable_phases:
  primary:
    - Development

tags:
  - checklist
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

# Pre-Completion Verification Checklist
## Final Check Before Saying "Done"

**Purpose:** Ensure nothing is missed before marking a task as complete  
**Usage:** Complete this checklist BEFORE saying "done" or "complete"

---

## ✅ Code Quality Checklist

### Code Standards
- [ ] Code follows PEP 8 (Python) or ESLint rules (TypeScript)
- [ ] No linting errors
- [ ] Code is properly formatted
- [ ] Maximum line length respected (100 chars for Python)

### Type Safety
- [ ] All functions have type hints (Python) or TypeScript types
- [ ] No `any` types used (TypeScript)
- [ ] Interfaces defined for complex types

### Documentation
- [ ] Docstrings added to all functions/classes (Python)
- [ ] Comments added for complex logic
- [ ] TODO/FIXME comments added where needed
- [ ] No obvious comments (code is self-documenting)

### Error Handling
- [ ] All exceptions handled
- [ ] Specific exception types used
- [ ] Error messages are meaningful
- [ ] Errors are logged appropriately

### Security
- [ ] No hardcoded secrets
- [ ] Environment variables used for configuration
- [ ] User input validated
- [ ] Output sanitized (if applicable)

---

## ✅ Functionality Checklist

### Acceptance Criteria
- [ ] All acceptance criteria from task met
- [ ] Task requirements fully implemented
- [ ] Edge cases handled
- [ ] Error cases handled

### Integration
- [ ] Code integrates with existing systems
- [ ] No breaking changes (unless intentional)
- [ ] Backward compatibility maintained (if required)
- [ ] API contracts followed

### Performance
- [ ] No obvious performance issues
- [ ] Database queries optimized (if applicable)
- [ ] No N+1 queries (Django)
- [ ] Caching used where appropriate

---

## ✅ Testing Checklist

### Test Coverage
- [ ] Unit tests written
- [ ] Integration tests written (if applicable)
- [ ] Test coverage acceptable (80%+)
- [ ] All tests passing

### Test Quality
- [ ] Positive test cases (happy path)
- [ ] Negative test cases (error handling)
- [ ] Edge cases tested
- [ ] Boundary values tested

### Test Execution
- [ ] All tests run successfully
- [ ] No test failures
- [ ] No test warnings (unless acceptable)
- [ ] Tests are deterministic (no flaky tests)

---

## ✅ Documentation Checklist

### Project Tracking Documents ⚠️ **NEW - REQUIRED**
- [ ] `docs/07_TRACKING/PHASE_STATUS_SUMMARY.md` - Phase/feature status updated
- [ ] `docs/07_TRACKING/PROJECT_ROADMAP.md` - Roadmap tasks marked complete
- [ ] `docs/07_TRACKING/IMMEDIATE_NEXT_STEPS.md` - Next steps updated
- [ ] Statistics and completion percentages recalculated

### Task Tracking
- [ ] Task marked complete `[x]` in `docs/07_TRACKING/tasks.md`
- [ ] Completion date added
- [ ] Files created/modified listed
- [ ] Completion notes added
- [ ] Task status updated from `[/]` to `[x]`

### Manual Test Checklist ⚠️ **NEW - REQUIRED FOR PHASE COMPLETION**
- [ ] Test checklist created/updated in `docs/03_TESTING/manual_test_checklist/PHASE_{N}_TESTING.md` (if phase completion)
- [ ] All required sections included:
  - [ ] Pre-Testing Setup
  - [ ] Backend Django Admin Testing (if applicable)
  - [ ] Backend API Testing (all endpoints)
  - [ ] Frontend Testing (if applicable)
  - [ ] Security Testing
  - [ ] Error Handling
  - [ ] Integration Testing
  - [ ] Final Verification
  - [ ] Notes & Issues section
  - [ ] Sign-Off section
- [ ] Format matches existing checklists
- [ ] README index updated (`docs/03_TESTING/manual_test_checklist/README.md`)

### Expected Output
- [ ] Expected output file created (if new phase)
- [ ] Expected output file updated (if existing phase)
- [ ] Expected output file is complete
- [ ] Index updated in `docs/07_TRACKING/expected_output/index.md` (if new file)

### Comprehensive Audit
- [ ] Phase section updated in `docs/07_TRACKING/COMPREHENSIVE_AUDIT.md`
- [ ] Task counts updated
- [ ] Implementation verification tables updated
- [ ] API endpoints list updated (if new endpoints)
- [ ] Component counts updated (if frontend work)
- [ ] Overall statistics updated
- [ ] Completion percentages recalculated

### Blockers
- [ ] Resolved blockers moved to "RESOLVED" section in `docs/07_TRACKING/BLOCKERS.md`
- [ ] Resolution details added
- [ ] Statistics updated
- [ ] New blockers added (if encountered)

### README
- [ ] API endpoints updated (if new endpoints added)
- [ ] Feature list updated (if major feature completed)
- [ ] Setup instructions updated (if changed)
- [ ] Dependencies updated (if new dependencies)

### Design Documents
- [ ] Design compliance verified
- [ ] Any design deviations documented

---

## ✅ File Management Checklist

### Created Files
- [ ] All new files created in correct locations
- [ ] File names follow conventions
- [ ] Files have proper structure
- [ ] All files documented in task completion notes

### Modified Files
- [ ] All modified files listed
- [ ] Changes are documented
- [ ] No unintended changes in other files

### Temporary Files
- [ ] No temporary files left behind
- [ ] No test files in production code
- [ ] No debug code left in
- [ ] No commented-out code (unless necessary)

### File Organization
- [ ] Files in correct directories
- [ ] Follows project structure conventions
- [ ] No orphaned files

---

## ✅ Migration Checklist (Django)

### Database Migrations
- [ ] Migrations created (if models changed)
- [ ] Migrations applied successfully
- [ ] No migration conflicts
- [ ] Migration files reviewed

### Model Changes
- [ ] Models updated correctly
- [ ] Relationships maintained
- [ ] Indexes added (if needed)
- [ ] Admin updated (if needed)

---

## ✅ API Checklist (Backend)

### Endpoints
- [ ] New endpoints added to `urls.py`
- [ ] Endpoints registered in router (if using DRF)
- [ ] Endpoints documented in Swagger/OpenAPI
- [ ] Endpoints tested

### Serializers
- [ ] Serializers created/updated
- [ ] Validation rules added
- [ ] Error messages meaningful

### Views
- [ ] Views created/updated
- [ ] Permissions set correctly
- [ ] Filtering/searching added (if applicable)
- [ ] Pagination added (if applicable)

---

## ✅ Frontend Checklist

### Components
- [ ] Components created in correct locations
- [ ] Components follow naming conventions
- [ ] Props interfaces defined
- [ ] Components are reusable (if intended)

### State Management
- [ ] State management implemented correctly
- [ ] Zustand stores updated (if applicable)
- [ ] React Query hooks updated (if applicable)

### Styling
- [ ] TailwindCSS classes used
- [ ] Shadcn/UI components used (when available)
- [ ] Responsive design considered
- [ ] Dark mode supported (if applicable)

### Routing
- [ ] Routes added to router
- [ ] Route guards added (if needed)
- [ ] Navigation works correctly

---

## ✅ Final Verification

### Self-Review
- [ ] Code reviewed by yourself
- [ ] Documentation reviewed
- [ ] All checklists completed
- [ ] No obvious issues

### Acceptance Criteria Re-check
- [ ] Re-read task acceptance criteria
- [ ] Verify all criteria met
- [ ] Verify no criteria missed

### Documentation Re-check
- [ ] All documentation files reviewed
- [ ] No missed updates
- [ ] All file paths verified
- [ ] All links work (if applicable)

### Final Statement Ready
- [ ] Completion statement prepared
- [ ] Files listed
- [ ] Documentation updates listed
- [ ] Test results ready

---

## 📋 Completion Statement Template

After completing ALL checklists, use this template:

```markdown
✅ Task Complete

**Task:** [Task number and name]

**Completed:**
- [List of what was completed]
- [Key features implemented]
- [Important changes]

**Files Created:**
- `path/to/new/file1.py`
- `path/to/new/file2.tsx`
- [List all new files]

**Files Modified:**
- `path/to/modified/file1.py`
- `path/to/modified/file2.tsx`
- [List all modified files]

**Documentation Updated:**
- ✅ `docs/07_TRACKING/PHASE_STATUS_SUMMARY.md` - Phase/feature status updated
- ✅ `docs/07_TRACKING/PROJECT_ROADMAP.md` - Roadmap tasks marked complete
- ✅ `docs/07_TRACKING/IMMEDIATE_NEXT_STEPS.md` - Next steps updated
- ✅ `docs/07_TRACKING/tasks.md` - Task marked complete
- ✅ `docs/03_TESTING/manual_test_checklist/PHASE_{N}_TESTING.md` - Manual test checklist created/updated (if phase completion) ⚠️ **NEW**
- ✅ `docs/07_TRACKING/COMPREHENSIVE_AUDIT.md` - Audit updated
- ✅ `docs/07_TRACKING/expected_output/phase_{N}_expected.md` - Expected output updated
- ✅ `docs/07_TRACKING/BLOCKERS.md` - Blockers resolved (if applicable)
- ✅ `README.md` - Updated (if applicable)

**Testing:**
- ✅ Unit tests: [X] tests, all passing
- ✅ Integration tests: [X] tests, all passing
- ✅ Test coverage: [X]%

**Verification:**
- ✅ Acceptance criteria met
- ✅ All documentation updated
- ✅ All tests passing
- ✅ Code quality checks passed
- ✅ No linting errors
- ✅ Final verification completed
```

---

## 🚨 Red Flags - Do NOT Say "Done" If:

- ❌ Project tracking documents not updated (PHASE_STATUS_SUMMARY, ROADMAP, NEXT_STEPS)
- ❌ Task not marked complete in tasks.md
- ❌ **Manual test checklist not created/updated (if phase completion)** ⚠️ **NEW**
- ❌ Comprehensive audit not updated
- ❌ Tests not written or not passing
- ❌ Acceptance criteria not met
- ❌ Documentation not updated
- ❌ Linting errors present
- ❌ Temporary files left behind
- ❌ Blockers not resolved (if you resolved them)
- ❌ Expected output file not created/updated (if applicable)

---

## 🎯 Quick Verification Command

Before saying "done", ask yourself:

1. **Is the code complete?** ✅
2. **Are tests written and passing?** ✅
3. **Is documentation updated?** ✅
4. **Are acceptance criteria met?** ✅
5. **Have I re-checked everything?** ✅

**Only if ALL answers are YES, you can say "done".**

---

## 📝 Notes

- This checklist is comprehensive - use it every time
- Don't skip items - they're all important
- If unsure about an item, check the relevant documentation
- When in doubt, update documentation - it's better to over-document than under-document

---

**Last Updated:** December 2024  
**Version:** 1.0

