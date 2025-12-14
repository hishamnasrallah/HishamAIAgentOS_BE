# Workflow System Integration - Step Types

**Document Type:** Integration Documentation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** ../04_BACKEND/03_SERVICES_IMPLEMENTATION.md, ../03_ARCHITECTURE/  
**File Size:** 495 lines

---

## 📋 Purpose

This document describes how new step types integrate with the existing workflow system.

---

## 🔗 Integration Points

### Integration 1: Step Type Registry

**New Step Types Registered:**
- `api_call` - Execute API call via AgentAPICaller
- `file_generation` - Generate files via ProjectGenerator
- `repo_creation` - Create repository via RepositoryExporter

**Registry Implementation:**
```python
STEP_EXECUTORS = {
    'agent': AgentStepExecutor,
    'api_call': APICallStepExecutor,  # NEW
    'file_generation': FileGenerationStepExecutor,  # NEW
    'repo_creation': RepoCreationStepExecutor,  # NEW
    ...
}
```

---

### Integration 2: Workflow Executor Enhancement

**Enhanced Executor:**
- Supports new step types
- Executes step executors from registry
- Handles errors appropriately
- Updates workflow state

---

### Integration 3: Step Execution Flow

**Flow:**
```
Workflow Step
    │
    ▼
Workflow Executor
    │
    ▼
Step Type Registry (lookup executor)
    │
    ▼
Step Executor (execute step)
    │
    ├──> api_call → AgentAPICaller
    ├──> file_generation → ProjectGenerator
    └──> repo_creation → RepositoryExporter
    │
    ▼
Result stored in workflow state
```

---

## 🔗 Related Documentation

- **Services:** `../04_BACKEND/03_SERVICES_IMPLEMENTATION.md`
- **Architecture:** `../03_ARCHITECTURE/`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

