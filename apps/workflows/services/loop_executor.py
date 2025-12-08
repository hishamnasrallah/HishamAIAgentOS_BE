"""
Loop Executor Service

Handles loop execution (for and while loops) in workflows.
"""

import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from .workflow_parser import ParsedStep
from .conditional_evaluator import conditional_evaluator, ConditionalEvaluationError

if TYPE_CHECKING:
    from .workflow_executor import WorkflowExecutor

logger = logging.getLogger(__name__)


class LoopExecutionError(Exception):
    """Raised when loop execution fails."""
    pass


async def execute_loop(
    executor: "WorkflowExecutor",
    execution_id: str,
    step: ParsedStep,
    context: Dict[str, Any],
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a loop step.
    
    Args:
        executor: WorkflowExecutor instance
        execution_id: Current workflow execution ID
        step: Loop step definition
        context: Current workflow context
        user_id: Optional user ID
        
    Returns:
        Dictionary with loop execution results
        
    Raises:
        LoopExecutionError: If loop execution fails
    """
    if not step.loop:
        raise LoopExecutionError(f"Step {step.id} is not a loop step")
    
    loop_config = step.loop
    loop_type = loop_config.get('type')
    max_iterations = loop_config.get('max_iterations', 100)
    loop_steps = loop_config.get('steps', [])
    
    if not loop_steps:
        raise LoopExecutionError(f"Loop step {step.id} has no steps to execute")
    
    results = []
    iteration = 0
    
    if loop_type == 'for':
        # For loop: iterate over an array
        over_path = loop_config.get('over')
        if not over_path:
            raise LoopExecutionError(f"For loop {step.id} must specify 'over' field")
        
        # Resolve the array to iterate over
        try:
            # Remove {{ }} if present
            if over_path.startswith('{{') and over_path.endswith('}}'):
                over_path = over_path[2:-2].strip()
            
            array_value = _get_nested_value(context, over_path)
            
            if not isinstance(array_value, (list, tuple)):
                raise LoopExecutionError(
                    f"For loop {step.id}: 'over' path must resolve to an array, got {type(array_value).__name__}"
                )
            
            loop_variable = loop_config.get('variable', 'item')
            
            # Execute loop for each item
            for item in array_value:
                if iteration >= max_iterations:
                    logger.warning(f"Loop {step.id} reached max_iterations ({max_iterations})")
                    break
                
                # Add loop variable to context
                loop_context = context.copy()
                loop_context['loop'] = {
                    'item': item,
                    'index': iteration,
                    'variable': loop_variable
                }
                # Also add directly for easier access
                loop_context[loop_variable] = item
                
                # Execute loop steps
                iteration_result = await _execute_loop_iteration(
                    executor,
                    execution_id,
                    step.id,
                    loop_steps,
                    loop_context,
                    iteration,
                    user_id
                )
                
                results.append(iteration_result)
                iteration += 1
                
                # Check for break condition
                if iteration_result.get('break', False):
                    break
        
        except KeyError as e:
            raise LoopExecutionError(f"For loop {step.id}: Could not resolve 'over' path: {str(e)}")
    
    elif loop_type == 'while':
        # While loop: loop while condition is true
        condition = loop_config.get('condition')
        if not condition:
            raise LoopExecutionError(f"While loop {step.id} must specify 'condition' field")
        
        # Execute loop while condition is true
        while iteration < max_iterations:
            try:
                # Evaluate condition
                should_continue = conditional_evaluator.evaluate(condition, context)
                
                if not should_continue:
                    break
                
                # Add loop context
                loop_context = context.copy()
                loop_context['loop'] = {
                    'index': iteration,
                    'iteration': iteration
                }
                
                # Execute loop steps
                iteration_result = await _execute_loop_iteration(
                    executor,
                    execution_id,
                    step.id,
                    loop_steps,
                    loop_context,
                    iteration,
                    user_id
                )
                
                results.append(iteration_result)
                iteration += 1
                
                # Check for break condition
                if iteration_result.get('break', False):
                    break
                
                # Update context with iteration result for next condition check
                context.update(loop_context)
                
            except ConditionalEvaluationError as e:
                raise LoopExecutionError(f"While loop {step.id}: Condition evaluation failed: {str(e)}")
    
    else:
        raise LoopExecutionError(f"Unknown loop type: {loop_type}")
    
    if iteration >= max_iterations:
        logger.warning(f"Loop {step.id} completed after {max_iterations} iterations (max reached)")
    
    return {
        'success': True,
        'output': {
            'iterations': iteration,
            'results': results,
            'total_results': len(results)
        },
        'loop_completed': True
    }


async def _execute_loop_iteration(
    executor: "WorkflowExecutor",
    execution_id: str,
    loop_step_id: str,
    loop_steps: List[Dict],
    context: Dict[str, Any],
    iteration: int,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute one iteration of a loop.
    
    Args:
        executor: WorkflowExecutor instance
        execution_id: Current workflow execution ID
        loop_step_id: ID of the loop step
        loop_steps: List of step definitions to execute in each iteration
        context: Loop iteration context
        iteration: Current iteration number
        user_id: Optional user ID
        
    Returns:
        Dictionary with iteration results
    """
    iteration_results = []
    last_output = None
    
    # Parse loop steps (simplified - in production, you'd want to reuse the parser)
    # For now, we'll execute them directly using the executor's step execution logic
    
    for step_def in loop_steps:
        step_id = step_def.get('id', f'{loop_step_id}_iter_{iteration}_{len(iteration_results)}')
        
        # Create a simplified ParsedStep for the loop step
        from .workflow_parser import ParsedStep
        
        loop_parsed_step = ParsedStep(
            id=step_id,
            name=step_def.get('name'),
            agent=step_def.get('agent', ''),
            inputs=step_def.get('inputs', {}),
            condition=step_def.get('condition'),
            on_success=step_def.get('on_success'),
            on_failure=step_def.get('on_failure'),
            max_retries=step_def.get('max_retries', 3),
            timeout_seconds=step_def.get('timeout_seconds', 300),
            skip_if=step_def.get('skip_if'),
            parallel=step_def.get('parallel', False),
            parallel_group=step_def.get('parallel_group'),
            depends_on=step_def.get('depends_on', []) if step_def.get('depends_on') else [],
            step_type=step_def.get('step_type', 'agent'),
            branch_group=step_def.get('branch_group'),
            merge_after=step_def.get('merge_after'),
            loop=step_def.get('loop'),
            sub_workflow=step_def.get('sub_workflow')
        )
        
        # Execute the step
        try:
            step_result = await executor._execute_step(
                execution_id,
                loop_parsed_step,
                context,
                user_id=user_id
            )
            
            iteration_results.append({
                'step_id': step_id,
                'result': step_result
            })
            
            # Update context with step result
            if 'steps' not in context:
                context['steps'] = {}
            context['steps'][step_id] = step_result
            
            last_output = step_result.get('output')
            
            # Check for break/continue
            if step_result.get('break', False):
                return {
                    'success': True,
                    'output': last_output,
                    'results': iteration_results,
                    'break': True
                }
            
            if step_result.get('continue', False):
                # Continue to next iteration
                return {
                    'success': True,
                    'output': last_output,
                    'results': iteration_results,
                    'continue': True
                }
            
        except Exception as e:
            logger.error(f"Error executing loop step {step_id} in iteration {iteration}: {e}")
            return {
                'success': False,
                'output': None,
                'error': str(e),
                'results': iteration_results
            }
    
    return {
        'success': True,
        'output': last_output,
        'results': iteration_results
    }


def _get_nested_value(context: Dict[str, Any], path: str) -> Any:
    """
    Get nested value from context using dot notation.
    
    Args:
        context: Context dictionary
        path: Dot-separated path (e.g., "steps.triage.output.severity")
        
    Returns:
        Value at the path
        
    Raises:
        KeyError: If path doesn't exist
    """
    parts = path.split('.')
    value = context
    
    for part in parts:
        if value is None:
            raise KeyError(f"Value is None at '{part}' in path {path}")
        
        if isinstance(value, dict):
            if part not in value:
                raise KeyError(f"Key '{part}' not found in path {path}")
            value = value[part]
        elif isinstance(value, (list, tuple)):
            try:
                index = int(part)
                if 0 <= index < len(value):
                    value = value[index]
                else:
                    raise KeyError(f"Index {index} out of range for list in path {path}")
            except ValueError:
                raise KeyError(f"Cannot access '{part}' in list/tuple value in path {path}")
        else:
            raise KeyError(f"Cannot access '{part}' in non-dict value (type: {type(value).__name__}) in path {path}")
    
    return value

