---
title: "Phase 22: Advanced Workflow Features - Implementation Plan"
description: "Plan for implementing advanced workflow features including parallel execution, loops, conditionals, and sub-workflows"
category: "Core"
language: "en"
status: "active"
priority: "high"
completeness: "100%"
version: "1.0"
last_updated: "2024-12-06"
---

# Phase 22: Advanced Workflow Features - Implementation Plan

**Date:** December 6, 2024  
**Status:** ✅ COMPLETE  
**Priority:** 🟡 HIGH

---

## 🎯 Objectives

Enhance the workflow engine with advanced features to support complex, real-world workflows:

1. **Parallel Execution** - Execute independent steps simultaneously
2. **Conditional Branching** - Enhanced if/else logic with multiple paths
3. **Loop Support** - For loops and while loops for iterative processing
4. **Sub-workflows** - Nested workflow execution for composition

---

## 📋 Current State Analysis

### Existing Infrastructure ✅

- **Workflow Executor:** Sequential step execution working
- **Workflow Parser:** Validates and parses workflow definitions
- **Conditional Evaluator:** Basic condition/skip_if support
- **Parallel Infrastructure:** `workflow_executor_parallel.py` exists but not fully integrated
- **State Manager:** Tracks workflow state and context

### Gaps to Address

1. **Parallel Execution:**
   - Infrastructure exists but not integrated into main executor
   - Need to add `parallel: true` flag support in schema
   - Need dependency analysis for parallel groups

2. **Conditional Branching:**
   - Basic `condition` exists but limited
   - Need multiple branch paths (if/else/elif)
   - Need branch merging logic

3. **Loop Support:**
   - No loop support currently
   - Need for loop (iterate over array)
   - Need while loop (condition-based)
   - Need loop break/continue

4. **Sub-workflows:**
   - No nested workflow support
   - Need sub-workflow step type
   - Need context passing between workflows

---

## 🏗️ Implementation Plan

### Task 1: Enable Parallel Execution (Priority 1)

**Status:** ✅ COMPLETE

#### 1.1 Update Workflow Schema
- [x] Add `parallel: boolean` field to step definition
- [x] Add `parallel_group: string` field for grouping parallel steps
- [x] Update JSON schema validation

#### 1.2 Enhance Workflow Parser
- [x] Parse `parallel` flag from step definitions
- [x] Build dependency graph for parallel analysis
- [x] Identify parallelizable step groups

#### 1.3 Integrate Parallel Executor
- [x] Integrate `workflow_executor_parallel.py` into main executor
- [x] Add parallel execution logic to `WorkflowExecutor.execute()`
- [x] Handle parallel step results and context merging

#### 1.4 Update ParsedStep
- [x] Add `parallel: bool` field to `ParsedStep` dataclass
- [x] Add `parallel_group: Optional[str]` field

**Files to Modify:**
- `backend/apps/workflows/schemas/workflow_schema.json`
- `backend/apps/workflows/services/workflow_parser.py`
- `backend/apps/workflows/services/workflow_executor.py`
- `backend/apps/workflows/services/workflow_executor_parallel.py`

**Estimated Time:** 1-2 days

---

### Task 2: Enhanced Conditional Branching (Priority 2)

**Status:** ✅ COMPLETE

#### 2.1 Update Workflow Schema
- [x] Add `branch_group` field for conditional branches
- [x] Support `if/else/elif` structure via branch groups
- [x] Add `merge` step type for combining branches

#### 2.2 Enhance Conditional Evaluator
- [x] Support complex boolean expressions (already supported)
- [x] Add branch selection logic
- [x] Handle branch merging

#### 2.3 Update Executor
- [x] Evaluate branch conditions
- [x] Execute selected branch path
- [x] Merge branch results

**Files to Modify:**
- `backend/apps/workflows/schemas/workflow_schema.json`
- `backend/apps/workflows/services/conditional_evaluator.py`
- `backend/apps/workflows/services/workflow_executor.py`

**Estimated Time:** 2-3 days

---

### Task 3: Loop Support (Priority 3)

**Status:** ✅ COMPLETE

#### 3.1 Update Workflow Schema
- [x] Add `loop` step type
- [x] Support `for` loop (iterate over array)
- [x] Support `while` loop (condition-based)
- [x] Add `break` and `continue` actions (via step results)

#### 3.2 Create Loop Executor
- [x] Implement loop iteration logic
- [x] Handle loop variables and context
- [x] Support nested loops (via recursive step execution)

#### 3.3 Update Executor
- [x] Detect loop steps
- [x] Execute loop iterations
- [x] Handle break/continue

**Files to Create:**
- `backend/apps/workflows/services/loop_executor.py`

**Files to Modify:**
- `backend/apps/workflows/schemas/workflow_schema.json`
- `backend/apps/workflows/services/workflow_parser.py`
- `backend/apps/workflows/services/workflow_executor.py`

**Estimated Time:** 3-4 days

---

### Task 4: Sub-workflow Support (Priority 4)

**Status:** ✅ COMPLETE

#### 4.1 Update Workflow Schema
- [x] Add `sub_workflow` step type
- [x] Support workflow reference by ID or slug
- [x] Support input/output mapping

#### 4.2 Create Sub-workflow Executor
- [x] Load referenced workflow
- [x] Execute sub-workflow with mapped inputs
- [x] Map sub-workflow outputs back to parent context

#### 4.3 Update Executor
- [x] Detect sub-workflow steps
- [x] Execute sub-workflow
- [x] Handle sub-workflow errors

**Files to Create:**
- `backend/apps/workflows/services/sub_workflow_executor.py`

**Files to Modify:**
- `backend/apps/workflows/schemas/workflow_schema.json`
- `backend/apps/workflows/services/workflow_parser.py`
- `backend/apps/workflows/services/workflow_executor.py`

**Estimated Time:** 2-3 days

---

## 📝 Example Workflow Definitions

### Parallel Execution Example

```yaml
name: Parallel Processing Workflow
version: "1.0.0"
steps:
  - id: step1
    name: "Initialize"
    agent: "coding_agent"
    inputs:
      task: "Initialize data"
  
  - id: step2
    name: "Process A"
    agent: "coding_agent"
    parallel: true
    parallel_group: "processing"
    inputs:
      task: "Process data A"
    depends_on: ["step1"]
  
  - id: step3
    name: "Process B"
    agent: "coding_agent"
    parallel: true
    parallel_group: "processing"
    inputs:
      task: "Process data B"
    depends_on: ["step1"]
  
  - id: step4
    name: "Merge Results"
    agent: "coding_agent"
    inputs:
      task: "Merge results from A and B"
    depends_on: ["step2", "step3"]
```

### Conditional Branching Example

```yaml
name: Conditional Workflow
version: "1.0.0"
steps:
  - id: step1
    name: "Check Condition"
    agent: "coding_agent"
    inputs:
      task: "Evaluate condition"
  
  - id: branch_if
    name: "If Path"
    condition: "{{steps.step1.output.result}} == true"
    agent: "coding_agent"
    inputs:
      task: "Execute if path"
  
  - id: branch_else
    name: "Else Path"
    condition: "{{steps.step1.output.result}} == false"
    agent: "coding_agent"
    inputs:
      task: "Execute else path"
  
  - id: merge
    name: "Merge"
    type: "merge"
    depends_on: ["branch_if", "branch_else"]
```

### Loop Example

```yaml
name: Loop Workflow
version: "1.0.0"
steps:
  - id: step1
    name: "Get Items"
    agent: "coding_agent"
    inputs:
      task: "Get list of items"
  
  - id: loop1
    name: "Process Items"
    type: "loop"
    loop_type: "for"
    loop_over: "{{steps.step1.output.items}}"
    loop_variable: "item"
    steps:
      - id: process_item
        name: "Process Item"
        agent: "coding_agent"
        inputs:
          task: "Process {{loop.item}}"
```

### Sub-workflow Example

```yaml
name: Parent Workflow
version: "1.0.0"
steps:
  - id: step1
    name: "Prepare Data"
    agent: "coding_agent"
    inputs:
      task: "Prepare data"
  
  - id: sub1
    name: "Execute Sub-workflow"
    type: "sub_workflow"
    workflow_id: "child-workflow-id"
    input_mapping:
      data: "{{steps.step1.output.data}}"
    output_mapping:
      result: "sub_result"
  
  - id: step2
    name: "Use Sub Result"
    agent: "coding_agent"
    inputs:
      task: "Use {{sub_result}}"
```

---

## ✅ Success Criteria

- [ ] Parallel execution works for independent steps
- [ ] Conditional branching supports multiple paths
- [ ] Loops can iterate over arrays and conditions
- [ ] Sub-workflows can be nested and executed
- [ ] All features work together in complex workflows
- [ ] Error handling works for all new features
- [ ] Test workflows demonstrate all features

---

## 📊 Progress Tracking

- **Task 1 (Parallel Execution):** 🚧 IN PROGRESS
- **Task 2 (Conditional Branching):** ⏳ PENDING
- **Task 3 (Loop Support):** ⏳ PENDING
- **Task 4 (Sub-workflows):** ⏳ PENDING

**Overall Progress:** 0% → Starting with Task 1

---

**Next Steps:**
1. Start with Task 1: Enable Parallel Execution
2. Update schema and parser
3. Integrate parallel executor
4. Test with example workflow

