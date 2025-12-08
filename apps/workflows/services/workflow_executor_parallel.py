"""
Parallel Workflow Step Execution Support

This module provides utilities for identifying and executing independent workflow steps in parallel.
"""

import uuid
import asyncio
from typing import Dict, Any, List, Set, Optional, Tuple
from .workflow_parser import ParsedWorkflow, ParsedStep


def find_parallel_steps(parsed_workflow: ParsedWorkflow, completed_steps: Set[str]) -> List[List[str]]:
    """
    Find steps that can be executed in parallel.
    
    Steps can run in parallel if:
    1. They have parallel=True flag
    2. They're in the same parallel_group (or no group specified)
    3. All their dependencies (depends_on) are completed
    4. They're not already completed
    
    Args:
        parsed_workflow: Parsed workflow definition
        completed_steps: Set of completed step IDs
        
    Returns:
        List of step groups, where each group can be executed in parallel
    """
    # Build dependency graph from depends_on, on_success, and on_failure
    dependencies: Dict[str, Set[str]] = {}
    step_map = parsed_workflow.step_map
    
    for step_id, step in step_map.items():
        # Check on_success dependencies (implicit dependency)
        if step.on_success:
            if step.on_success in step_map:
                if step.on_success not in dependencies:
                    dependencies[step.on_success] = set()
                dependencies[step.on_success].add(step_id)
        
        # Check on_failure dependencies (implicit dependency)
        if step.on_failure:
            if step.on_failure in step_map:
                if step.on_failure not in dependencies:
                    dependencies[step.on_failure] = set()
                dependencies[step.on_failure].add(step_id)
    
    # Find steps ready to execute (all dependencies completed)
    ready_steps = []
    branch_groups_seen = {}  # Track which branch groups have already been evaluated
    
    for step_id, step in step_map.items():
        if step_id in completed_steps:
            continue
        
        # Check explicit depends_on
        step_deps = set(step.depends_on) if step.depends_on else set()
        # Add implicit dependencies
        step_deps.update(dependencies.get(step_id, set()))
        
        if step_deps.issubset(completed_steps):
            # Handle branch groups: only add steps from branch groups if they haven't been evaluated yet
            if step.branch_group:
                if step.branch_group not in branch_groups_seen:
                    # First time seeing this branch group - add it
                    ready_steps.append(step_id)
                    branch_groups_seen[step.branch_group] = step_id
                # If branch group already seen, skip (only one branch per group executes)
            else:
                ready_steps.append(step_id)
    
    # Group steps by parallel_group
    parallel_groups_by_group: Dict[Optional[str], List[str]] = {}
    sequential_steps = []
    
    for step_id in ready_steps:
        step = step_map[step_id]
        if step.parallel:
            # Group by parallel_group (None means no group, can run with other ungrouped parallel steps)
            group_key = step.parallel_group if step.parallel_group else "__ungrouped__"
            if group_key not in parallel_groups_by_group:
                parallel_groups_by_group[group_key] = []
            parallel_groups_by_group[group_key].append(step_id)
        else:
            # Sequential step
            sequential_steps.append(step_id)
    
    # Build result: parallel groups first, then sequential steps
    result = []
    
    # Add parallel groups (each group executes in parallel)
    for group_steps in parallel_groups_by_group.values():
        if group_steps:
            result.append(group_steps)
    
    # Add sequential steps (one at a time)
    for step_id in sequential_steps:
        result.append([step_id])
    
    return result if result else []


async def execute_parallel_steps(
    executor,
    execution_id: str,
    step_ids: List[str],
    parsed_workflow: ParsedWorkflow,
    context: Dict[str, Any],
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Execute multiple steps in parallel.
    
    Args:
        executor: WorkflowExecutor instance
        execution_id: Execution UUID
        step_ids: List of step IDs to execute in parallel
        parsed_workflow: Parsed workflow definition
        context: Current workflow context
        user_id: Optional user ID
        
    Returns:
        List of step execution results
    """
    # Create tasks for parallel execution
    tasks = []
    for step_id in step_ids:
        step = parsed_workflow.step_map.get(step_id)
        if step:
            task = executor._execute_step(
                uuid.UUID(execution_id),
                step,
                context,
                user_id
            )
            tasks.append(task)
    
    # Execute all steps in parallel
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        step_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                step_results.append({
                    'success': False,
                    'output': {'error': str(result)},
                    'error': str(result)
                })
            else:
                step_results.append(result)
        
        return step_results
    
    return []

