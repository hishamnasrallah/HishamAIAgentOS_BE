"""
Workflow Executor Service

Executes workflows with state management, conditional logic, error handling, and retry mechanisms.
Integrates with agents, manages execution lifecycle, and handles failures gracefully.
"""

import uuid
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .workflow_parser import workflow_parser, ParsedWorkflow, ParsedStep
from .conditional_evaluator import conditional_evaluator, ConditionalEvaluationError
from .state_manager import workflow_state_manager
from .workflow_executor_parallel import find_parallel_steps, execute_parallel_steps
from .loop_executor import execute_loop, LoopExecutionError
from .sub_workflow_executor import execute_sub_workflow, SubWorkflowExecutionError
from apps.agents.services.execution_engine import execution_engine


class WorkflowExecutionError(Exception):
    """Raised when workflow execution fails."""
    pass


class WorkflowExecutor:
    """
    Execute workflows with full lifecycle management.
    
    Responsibilities:
    - Create WorkflowExecution instances
    - Execute steps in order
    - Handle conditionals (condition, skip_if)
    - Manage state transitions
    - Error handling and retry logic
    - Integration with agent execution engine
    """
    
    def __init__(self):
        self.parser = workflow_parser
        self.evaluator = conditional_evaluator
        self.state_manager = workflow_state_manager
        self.channel_layer = get_channel_layer()
    
    async def execute(
        self,
        workflow_id: str,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_id: Workflow UUID
            input_data: Input data for workflow
            user_id: Optional user ID who triggered execution
            
        Returns:
            Execution result dictionary
            
        Raises:
            WorkflowExecutionError: If execution fails critically
        """
        from apps.workflows.models import Workflow, WorkflowExecution
        
        # Step 1: Get workflow and parse definition (with caching)
        try:
            workflow = await Workflow.objects.aget(id=workflow_id)
        except Workflow.DoesNotExist:
            raise WorkflowExecutionError(f"Workflow '{workflow_id}' not found")
        
        # Check cache for parsed workflow
        cache_key = f'workflow_parsed_{workflow_id}_{workflow.updated_at.timestamp()}'
        parsed_workflow = cache.get(cache_key)
        
        if parsed_workflow is None:
            # Ensure definition has required fields from model
            definition = workflow.definition.copy() if isinstance(workflow.definition, dict) else {}
            if 'name' not in definition:
                definition['name'] = workflow.name
            if 'version' not in definition:
                definition['version'] = workflow.version
            if 'description' not in definition and workflow.description:
                definition['description'] = workflow.description
            
            # Validate definition has steps
            if 'steps' not in definition or not definition['steps']:
                raise WorkflowExecutionError("Workflow definition must have at least one step")
            
            try:
                parsed_workflow = self.parser.parse(definition)
                # Cache parsed workflow for 10 minutes
                cache.set(cache_key, parsed_workflow, settings.CACHE_TIMEOUT_LONG)
            except Exception as e:
                raise WorkflowExecutionError(f"Failed to parse workflow definition: {str(e)}")
        
        # Validate that all agents exist (using async ORM)
        from apps.agents.models import Agent
        # Use async list comprehension for values_list
        agent_names_list = [name async for name in Agent.objects.values_list('name', flat=True)]
        agent_names = set(agent_names_list)
        missing_agents = []
        for step in parsed_workflow.steps:
            if step.agent not in agent_names:
                missing_agents.append(step.agent)
        
        if missing_agents:
            available_preview = ', '.join(list(agent_names)[:5])
            raise WorkflowExecutionError(
                f"Workflow references agents that don't exist: {', '.join(missing_agents)}. "
                f"Available agents: {available_preview}{'...' if len(agent_names) > 5 else ''}"
            )
        
        # Step 2: Create execution instance
        execution = await WorkflowExecution.objects.acreate(
            workflow=workflow,
            user_id=user_id,
            input_data=input_data,
            status='pending',
            state={'steps': {}, 'input': input_data}
        )
        
        # Step 3: Execute workflow
        try:
            result = await self._execute_workflow(
                execution.id,
                parsed_workflow,
                input_data,
                user_id=user_id
            )
            
            # Update workflow execution count
            workflow.execution_count += 1
            await workflow.asave()
            
            return result
            
        except Exception as e:
            await self.state_manager.record_execution_failure(
                str(execution.id),
                str(e)
            )
            raise WorkflowExecutionError(f"Workflow execution failed: {str(e)}")
    
    async def _execute_workflow(
        self,
        execution_id: uuid.UUID,
        parsed_workflow: ParsedWorkflow,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the actual workflow logic.
        
        Args:
            execution_id: Execution UUID
            parsed_workflow: Parsed workflow definition
            input_data: Input data
            
        Returns:
            Workflow execution result
        """
        # Initialize context
        context = {
            'input': input_data,
            'steps': {},
            'workflow': {
                'name': parsed_workflow.name,
                'version': parsed_workflow.version
            }
        }
        
        # Start execution
        await self.state_manager.save_state(
            str(execution_id),
            parsed_workflow.entry_step.id,
            context,
            'running'
        )
        
        # Get total steps for progress calculation
        total_steps = len(parsed_workflow.steps)
        completed_steps: Set[str] = set()
        last_output = None
        last_completed_output = None  # Track last non-skipped output
        
        # Execute workflow using dependency-based approach (supports parallel execution)
        while len(completed_steps) < total_steps:
            # Find steps ready to execute (including parallel groups)
            step_groups = find_parallel_steps(parsed_workflow, completed_steps)
            
            if not step_groups:
                # No more steps ready - check if we're stuck or done
                if len(completed_steps) < total_steps:
                    # Some steps not completed but none are ready - possible deadlock
                    remaining = [s.id for s in parsed_workflow.steps if s.id not in completed_steps]
                    raise WorkflowExecutionError(
                        f"Workflow execution deadlock: steps {remaining} cannot execute. "
                        f"Check dependencies and conditions."
                    )
                break
            
            # Execute each group (parallel groups execute simultaneously, sequential groups one at a time)
            for step_group in step_groups:
                if len(step_group) == 1:
                    # Single step - execute sequentially
                    step_id = step_group[0]
                    step = parsed_workflow.step_map.get(step_id)
                    if not step:
                        continue
                    
                    # Handle branch groups: if this step is part of a branch group, evaluate all branches
                    if step.branch_group:
                        # Find all steps in this branch group that haven't been completed
                        branch_steps = [
                            s for s in parsed_workflow.steps
                            if s.branch_group == step.branch_group and s.id not in completed_steps
                        ]
                        
                        # Evaluate conditions and execute the first matching branch
                        branch_executed = False
                        for branch_step in branch_steps:
                            # Check if branch condition is met (condition is checked in _execute_step)
                            # But we need to check here to decide which branch to execute
                            if branch_step.condition:
                                try:
                                    should_execute = self.evaluator.evaluate(branch_step.condition, context)
                                    if should_execute:
                                        # Execute this branch
                                        await self._emit_step_started(
                                            str(execution_id),
                                            branch_step.id,
                                            branch_step.name,
                                            len(completed_steps) + 1,
                                            total_steps
                                        )
                                        
                                        step_result = await self._execute_step(
                                            execution_id,
                                            branch_step,
                                            context,
                                            user_id=user_id
                                        )
                                        
                                        normalized_result, last_output, last_completed_output = await self._process_step_result(
                                            execution_id,
                                            branch_step,
                                            step_result,
                                            context,
                                            last_output,
                                            last_completed_output,
                                            len(completed_steps) + 1,
                                            total_steps
                                        )
                                        
                                        completed_steps.add(branch_step.id)
                                        branch_executed = True
                                        break
                                except ConditionalEvaluationError:
                                    # Condition evaluation failed, try next branch
                                    continue
                            else:
                                # No condition means this branch always executes (else branch)
                                await self._emit_step_started(
                                    str(execution_id),
                                    branch_step.id,
                                    branch_step.name,
                                    len(completed_steps) + 1,
                                    total_steps
                                )
                                
                                step_result = await self._execute_step(
                                    execution_id,
                                    branch_step,
                                    context,
                                    user_id=user_id
                                )
                                
                                normalized_result, last_output, last_completed_output = await self._process_step_result(
                                    execution_id,
                                    branch_step,
                                    step_result,
                                    context,
                                    last_output,
                                    last_completed_output,
                                    len(completed_steps) + 1,
                                    total_steps
                                )
                                
                                completed_steps.add(branch_step.id)
                                branch_executed = True
                                break
                        
                        # Mark all other branches in the group as skipped
                        for branch_step in branch_steps:
                            if branch_step.id not in completed_steps:
                                completed_steps.add(branch_step.id)
                                # Store skipped status in context
                                if 'steps' not in context:
                                    context['steps'] = {}
                                context['steps'][branch_step.id] = {
                                    'success': True,
                                    'output': {'skipped': True, 'reason': 'branch not selected'},
                                    'skipped': True
                                }
                        
                        # Save state after branch execution
                        if branch_executed:
                            await self.state_manager.save_state(
                                str(execution_id),
                                step.id,
                                context,
                                'running'
                            )
                    else:
                        # Regular step execution
                        # Emit step started event
                        await self._emit_step_started(
                            str(execution_id),
                            step.id,
                            step.name,
                            len(completed_steps) + 1,
                            total_steps
                        )
                        
                        # Execute step
                        step_result = await self._execute_step(
                            execution_id,
                            step,
                            context,
                            user_id=user_id
                        )
                        
                        # Process result
                        normalized_result, last_output, last_completed_output = await self._process_step_result(
                            execution_id,
                            step,
                            step_result,
                            context,
                            last_output,
                            last_completed_output,
                            len(completed_steps) + 1,
                            total_steps
                        )
                        
                        completed_steps.add(step_id)
                        
                        # Save state
                        await self.state_manager.save_state(
                            str(execution_id),
                            step.id,
                            context,
                            'running'
                        )
                else:
                    # Parallel group - execute all steps simultaneously
                    for step_id in step_group:
                        step = parsed_workflow.step_map.get(step_id)
                        if step:
                            await self._emit_step_started(
                                str(execution_id),
                                step.id,
                                step.name,
                                len(completed_steps) + 1,
                                total_steps
                            )
                    
                    # Execute all steps in parallel
                    parallel_results = await execute_parallel_steps(
                        self,
                        str(execution_id),
                        step_group,
                        parsed_workflow,
                        context,
                        user_id
                    )
                    
                    # Process all parallel results
                    for i, step_id in enumerate(step_group):
                        step = parsed_workflow.step_map.get(step_id)
                        if step and i < len(parallel_results):
                            step_result = parallel_results[i]
                            normalized_result, last_output, last_completed_output = await self._process_step_result(
                                execution_id,
                                step,
                                step_result,
                                context,
                                last_output,
                                last_completed_output,
                                len(completed_steps) + 1,
                                total_steps
                            )
                            completed_steps.add(step_id)
                    
                    # Save state after parallel group
                    await self.state_manager.save_state(
                        str(execution_id),
                        step_group[0] if step_group else None,
                        context,
                        'running'
                    )
        
        # Workflow complete
        # Use last completed output if available, otherwise use last output
        final_output = last_completed_output if last_completed_output is not None else last_output
        
        await self.state_manager.record_execution_complete(
            str(execution_id),
            final_output,
            success=True
        )
        
        # Emit execution complete event
        await self._emit_execution_complete(
            str(execution_id),
            True,
            final_output
        )
        
        return {
            'success': True,
            'output': final_output,
            'execution_id': str(execution_id),
            'completed_at': datetime.now().isoformat()
        }
    
    async def _process_step_result(
        self,
        execution_id: uuid.UUID,
        step: ParsedStep,
        step_result: Dict[str, Any],
        context: Dict[str, Any],
        last_output: Any,
        last_completed_output: Any,
        current_step_number: int,
        total_steps: int
    ) -> Tuple[Dict[str, Any], Any, Any]:
        """
        Process a step execution result: normalize output, store in context, emit events.
        
        Returns:
            Tuple of (normalized_result, last_output, last_completed_output)
        """
        # Normalize step output for context storage
        normalized_result = step_result.copy()
        output = step_result.get('output')
        if isinstance(output, str):
            # Wrap string output in a dict with 'content' and 'success' fields
            normalized_result['output'] = {
                'content': output,
                'success': step_result.get('success', True),
                'text': output  # Also include as 'text' for backward compatibility
            }
        elif output is None:
            # Ensure None outputs are handled
            normalized_result['output'] = {
                'success': step_result.get('success', False),
                'content': None
            }
        elif not isinstance(output, dict):
            # If output is not a dict or string, wrap it
            normalized_result['output'] = {
                'value': output,
                'success': step_result.get('success', True)
            }
        
        # Store normalized step output in context
        context['steps'][step.id] = normalized_result
        new_last_output = normalized_result.get('output')
        
        # Track last completed (non-skipped) output for final result
        new_last_completed_output = last_completed_output
        if not normalized_result.get('skipped', False):
            new_last_completed_output = new_last_output
        
        # Emit step completed event
        await self._emit_step_completed(
            str(execution_id),
            step.id,
            step.name,
            step_result.get('success', True),
            step_result.get('output')
        )
        
        # Calculate and emit progress
        progress = int((current_step_number / total_steps) * 100) if total_steps > 0 else 0
        await self._emit_progress(
            str(execution_id),
            progress,
            current_step_number,
            total_steps
        )
        
        return normalized_result, new_last_output, new_last_completed_output
    
    async def _execute_step(
        self,
        execution_id: uuid.UUID,
        step: ParsedStep,
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a single workflow step.
        
        Args:
            execution_id: Execution UUID
            step: Parsed step to execute
            context: Current workflow context
            
        Returns:
            Step execution result
        """
        # Record step start
        await self.state_manager.record_step_start(
            str(execution_id),
            step.id
        )
        
        # Check skip condition
        if step.skip_if:
            try:
                should_skip = self.evaluator.evaluate(step.skip_if, context)
                if should_skip:
                    return {
                        'success': True,
                        'output': {'skipped': True, 'reason': 'skip_if condition met'},
                        'skipped': True
                    }
            except ConditionalEvaluationError as e:
                # If skip condition fails, log but continue
                pass
        
        # Check execution condition (for branch groups, condition determines if branch executes)
        if step.condition:
            try:
                should_execute = self.evaluator.evaluate(step.condition, context)
                if not should_execute:
                    return {
                        'success': True,
                        'output': {'skipped': True, 'reason': 'condition not met'},
                        'skipped': True
                    }
            except ConditionalEvaluationError as e:
                return {
                    'success': False,
                    'output': None,
                    'error': f"Condition evaluation failed: {str(e)}"
                }
        
        # Route to appropriate executor based on step type
        step_type = step.step_type or 'agent'
        
        if step_type == 'merge':
            # Merge step: wait for all branches in the merge_after group to complete
            return await self._execute_merge_step(
                execution_id,
                step,
                context,
                user_id
            )
        elif step_type == 'loop':
            # Loop step: execute loop
            try:
                result = await execute_loop(
                    self,
                    str(execution_id),
                    step,
                    context,
                    user_id
                )
                
                await self.state_manager.record_step_completion(
                    str(execution_id),
                    step.id,
                    result.get('output'),
                    success=result.get('success', True)
                )
                
                return result
            except LoopExecutionError as e:
                await self.state_manager.record_step_completion(
                    str(execution_id),
                    step.id,
                    None,
                    success=False
                )
                return {
                    'success': False,
                    'output': None,
                    'error': str(e)
                }
        elif step_type == 'sub_workflow':
            # Sub-workflow step: execute nested workflow
            try:
                result = await execute_sub_workflow(
                    self,
                    str(execution_id),
                    step,
                    context,
                    user_id
                )
                
                await self.state_manager.record_step_completion(
                    str(execution_id),
                    step.id,
                    result.get('output'),
                    success=result.get('success', True)
                )
                
                return result
            except SubWorkflowExecutionError as e:
                await self.state_manager.record_step_completion(
                    str(execution_id),
                    step.id,
                    None,
                    success=False
                )
                return {
                    'success': False,
                    'output': None,
                    'error': str(e)
                }
        elif step_type == 'api_call':
            # API call step: call HishamOS API
            try:
                result = await self._execute_api_call_step(
                    execution_id,
                    step,
                    context,
                    user_id
                )
                
                await self.state_manager.record_step_completion(
                    str(execution_id),
                    step.id,
                    result.get('output'),
                    success=result.get('success', True)
                )
                
                return result
            except Exception as e:
                await self.state_manager.record_step_completion(
                    str(execution_id),
                    step.id,
                    None,
                    success=False
                )
                return {
                    'success': False,
                    'output': None,
                    'error': str(e)
                }
        elif step_type == 'file_generation':
            # File generation step: generate project files
            try:
                result = await self._execute_file_generation_step(
                    execution_id,
                    step,
                    context,
                    user_id
                )
                
                await self.state_manager.record_step_completion(
                    str(execution_id),
                    step.id,
                    result.get('output'),
                    success=result.get('success', True)
                )
                
                return result
            except Exception as e:
                await self.state_manager.record_step_completion(
                    str(execution_id),
                    step.id,
                    None,
                    success=False
                )
                return {
                    'success': False,
                    'output': None,
                    'error': str(e)
                }
        elif step_type == 'repo_creation':
            # Repository creation step: create Git repository
            try:
                result = await self._execute_repo_creation_step(
                    execution_id,
                    step,
                    context,
                    user_id
                )
                
                await self.state_manager.record_step_completion(
                    str(execution_id),
                    step.id,
                    result.get('output'),
                    success=result.get('success', True)
                )
                
                return result
            except Exception as e:
                await self.state_manager.record_step_completion(
                    str(execution_id),
                    step.id,
                    None,
                    success=False
                )
                return {
                    'success': False,
                    'output': None,
                    'error': str(e)
                }
        else:
            # Default: agent step
            # Prepare step inputs
            step_inputs = self._resolve_step_inputs(step.inputs, context)
            
            # Execute step with retry logic
            for attempt in range(step.max_retries + 1):
                try:
                    # Execute via agent
                    result = await self._execute_with_agent(
                        step.agent,
                        step_inputs,
                        timeout_seconds=step.timeout_seconds,
                        user_id=user_id
                    )
                    
                    # Success
                    await self.state_manager.record_step_completion(
                        str(execution_id),
                        step.id,
                        result,
                        success=True
                    )
                    
                    return {
                        'success': True,
                        'output': result,
                        'attempts': attempt + 1
                    }
                    
                except Exception as e:
                    # Last attempt failed
                    if attempt == step.max_retries:
                        await self.state_manager.record_step_completion(
                            str(execution_id),
                            step.id,
                            None,
                            success=False
                        )
                        
                        return {
                            'success': False,
                            'output': None,
                            'error': str(e),
                            'attempts': attempt + 1
                        }
                    
                    # Retry
                    await asyncio.sleep(min(2 ** attempt, 10))  # Exponential backoff
    
    async def _execute_merge_step(
        self,
        execution_id: uuid.UUID,
        step: ParsedStep,
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a merge step that waits for all branches in a branch group to complete.
        
        Args:
            execution_id: Execution UUID
            step: Merge step definition
            context: Current workflow context
            user_id: Optional user ID
            
        Returns:
            Merge step result
        """
        if not step.merge_after:
            return {
                'success': True,
                'output': {'merged': True, 'message': 'No branch group to merge'},
                'merged': True
            }
        
        # The merge step itself doesn't need to do anything special
        # The branch handling is done in the main execution loop
        # This step just serves as a marker that branches should merge here
        
        return {
            'success': True,
            'output': {
                'merged': True,
                'branch_group': step.merge_after,
                'message': f'Merged branches from group {step.merge_after}'
            },
            'merged': True
        }
    
    def _resolve_step_inputs(
        self,
        inputs: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve step inputs by replacing {{variable}} references.
        
        Args:
            inputs: Input configuration with {{variable}} placeholders
            context: Current context
            
        Returns:
            Resolved inputs
        """
        resolved = {}
        
        for key, value in inputs.items():
            if isinstance(value, str) and '{{' in value:
                # Extract variable path
                import re
                match = re.search(r'\{\{([^}]+)\}\}', value)
                if match:
                    var_path = match.group(1).strip()
                    
                    # Get value from context
                    try:
                        resolved_value = self._get_nested_value(context, var_path)
                        resolved[key] = resolved_value
                    except KeyError:
                        # Variable not found, use original value
                        resolved[key] = value
                else:
                    resolved[key] = value
            else:
                resolved[key] = value
        
        return resolved
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """
        Get nested value using dot notation.
        
        Args:
            data: Data dictionary
            path: Dot-separated path
            
        Returns:
            Value at path
        """
        parts = path.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict):
                value = value[part]
            else:
                raise KeyError(f"Cannot access '{part}' in path {path}")
        
        return value
    
    async def _execute_with_agent(
        self,
        agent_name: str,
        inputs: Dict[str, Any],
        timeout_seconds: int = 300,
        user_id: Optional[str] = None
    ) -> Any:
        """
        Execute step using specified agent.
        
        Args:
            agent_name: Agent name to use
            inputs: Input data for agent
            timeout_seconds: Execution timeout
            user_id: Optional user ID for execution context
            
        Returns:
            Agent execution result
        """
        from apps.agents.models import Agent
        from apps.authentication.models import User
        
        # Get agent by name
        try:
            agent = await Agent.objects.aget(name=agent_name)
        except Agent.DoesNotExist:
            raise WorkflowExecutionError(f"Agent '{agent_name}' not found")
        
        # Get user if provided
        user = None
        if user_id:
            try:
                # Try UUID first, then integer ID
                try:
                    import uuid as uuid_module
                    user_uuid = uuid_module.UUID(user_id)
                    user = await User.objects.aget(id=user_uuid)
                except (ValueError, TypeError):
                    # If not UUID, try as integer
                    try:
                        user = await User.objects.aget(id=int(user_id))
                    except (ValueError, TypeError, User.DoesNotExist):
                        pass
            except User.DoesNotExist:
                pass
        
        # Prepare input_data - use task_description if available, otherwise use inputs
        input_data = inputs.copy()
        if 'task_description' not in input_data and 'prompt' not in input_data:
            # If no task_description or prompt, use the first string value or create a generic one
            task_desc = None
            for key, value in inputs.items():
                if isinstance(value, str) and value:
                    task_desc = value
                    break
            if task_desc:
                input_data['task_description'] = task_desc
            else:
                input_data['task_description'] = f"Execute {agent_name} task"
        
        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                execution_engine.execute_agent(
                    agent=agent,
                    input_data=input_data,
                    user=user,
                    context=inputs
                ),
                timeout=timeout_seconds
            )
            
            # Return the output from AgentResult
            if hasattr(result, 'output'):
                return result.output
            elif hasattr(result, 'result'):
                return result.result
            else:
                return result
            
        except asyncio.TimeoutError:
            raise WorkflowExecutionError(
                f"Step execution timed out after {timeout_seconds} seconds"
            )
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            raise WorkflowExecutionError(
                f"Agent execution failed: {str(e)}\n{error_trace}"
            )
    
    async def pause(self, execution_id: str):
        """Pause workflow execution."""
        await self.state_manager.pause_execution(execution_id)
    
    async def resume(self, execution_id: str):
        """Resume paused or failed workflow execution."""
        from apps.workflows.models import WorkflowExecution, WorkflowStep
        from asgiref.sync import sync_to_async
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get execution
        try:
            execution = await sync_to_async(WorkflowExecution.objects.get)(id=execution_id)
        except WorkflowExecution.DoesNotExist:
            raise ValueError(f"Workflow execution {execution_id} not found")
        
        # Check if execution can be resumed
        if execution.status not in ['paused', 'running', 'failed']:
            raise ValueError(f"Cannot resume execution with status: {execution.status}")
        
        # Resume execution status
        await self.state_manager.resume_execution(execution_id)
        
        # Get current state from database
        state = execution.state or {}
        context = state.get('context', {})
        if not context:
            # Fallback: reconstruct context from input_data
            context = {
                'input': execution.input_data,
                'steps': {},
                'workflow': {
                    'name': execution.workflow.name,
                    'version': execution.workflow.version
                }
            }
        
        # Get completed steps from WorkflowStep records
        completed_steps_query = await sync_to_async(list)(
            WorkflowStep.objects.filter(
                execution=execution,
                status__in=['completed', 'skipped']
            ).values_list('step_name', flat=True)
        )
        completed_steps = set(completed_steps_query)
        
        # Get workflow definition and parse it
        workflow = execution.workflow
        parsed_workflow = await sync_to_async(self.parser.parse)(workflow.definition)
        
        # Find the step to resume from
        current_step_name = execution.current_step
        step_to_resume = None
        
        if current_step_name:
            # Try to find the current step
            for step in parsed_workflow.steps:
                if step.name == current_step_name:
                    if step.name not in completed_steps:
                        step_to_resume = step
                        break
        else:
            # Find first incomplete step
            for step in parsed_workflow.steps:
                if step.name not in completed_steps:
                    step_to_resume = step
                    break
        
        if not step_to_resume:
            # All steps completed, mark as completed
            await self.state_manager.complete_execution(
                execution_id,
                output_data=state.get('output_data', execution.output_data or {})
            )
            return
        
        # Update current step
        execution.current_step = step_to_resume.name
        execution.status = 'running'
        await sync_to_async(execution.save)(update_fields=['current_step', 'status'])
        
        # Continue execution from this step
        try:
            user_id = str(execution.user.id) if execution.user else None
            
            # Continue execution from current step
            await self._continue_workflow_execution(
                execution_id=execution.id,
                parsed_workflow=parsed_workflow,
                context=context,
                completed_steps=completed_steps,
                start_from_step=step_to_resume.name,
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"Failed to resume workflow execution: {str(e)}", exc_info=True)
            await self.state_manager.fail_execution(execution_id, str(e))
            raise
    
    async def _continue_workflow_execution(
        self,
        execution_id: uuid.UUID,
        parsed_workflow: ParsedWorkflow,
        context: Dict[str, Any],
        completed_steps: set,
        start_from_step: str,
        user_id: Optional[str] = None
    ):
        """Continue workflow execution from a specific step."""
        from typing import Set
        
        total_steps = len(parsed_workflow.steps)
        last_output = None
        last_completed_output = None
        
        # Restore last output from context if available
        if 'steps' in context and context['steps']:
            # Get the last completed step's output
            for step_id, step_data in context['steps'].items():
                if step_data.get('success') and not step_data.get('skipped'):
                    last_output = step_data.get('output')
                    last_completed_output = last_output
        
        # Continue execution loop from current step
        while len(completed_steps) < total_steps:
            # Find steps ready to execute (considering dependencies and completed steps)
            step_groups = find_parallel_steps(parsed_workflow, completed_steps)
            
            if not step_groups:
                # Check if we're done or stuck
                if len(completed_steps) < total_steps:
                    remaining = [s.id for s in parsed_workflow.steps if s.id not in completed_steps]
                    raise WorkflowExecutionError(
                        f"Workflow execution cannot continue: steps {remaining} cannot execute. "
                        f"Check dependencies and conditions."
                    )
                break
            
            # Execute each group
            for step_group in step_groups:
                if len(step_group) == 1:
                    step_id = step_group[0]
                    step = parsed_workflow.step_map.get(step_id)
                    if not step or step.name in completed_steps:
                        continue
                    
                    # Skip if we haven't reached the start step yet
                    if step.name != start_from_step and start_from_step not in completed_steps:
                        # Check if this step depends on start_from_step
                        if step.depends_on:
                            # Check if any dependency is the start step
                            depends_on_names = [s.name for s in parsed_workflow.steps if s.id in step.depends_on]
                            if start_from_step not in depends_on_names:
                                continue
                    
                    # Execute step (reuse existing step execution logic)
                    await self._emit_step_started(
                        str(execution_id),
                        step.id,
                        step.name,
                        len(completed_steps) + 1,
                        total_steps
                    )
                    
                    step_result = await self._execute_step(
                        execution_id,
                        step,
                        context,
                        user_id=user_id
                    )
                    
                    normalized_result, last_output, last_completed_output = await self._process_step_result(
                        execution_id,
                        step,
                        step_result,
                        context,
                        last_output,
                        last_completed_output,
                        len(completed_steps) + 1,
                        total_steps
                    )
                    
                    completed_steps.add(step.id)
                    
                    # Save state after step
                    await self.state_manager.save_state(
                        str(execution_id),
                        step.id,
                        context,
                        'running'
                    )
                    
                    # Update start_from_step flag after first step
                    if step.name == start_from_step:
                        start_from_step = None  # Clear flag to allow all subsequent steps
                else:
                    # Parallel group execution
                    await execute_parallel_steps(
                        execution_id,
                        step_group,
                        parsed_workflow,
                        context,
                        user_id,
                        self._execute_step,
                        self._process_step_result,
                        self.state_manager,
                        self._emit_step_started
                    )
                    
                    # Mark all steps in group as completed
                    for step_id in step_group:
                        completed_steps.add(step_id)
        
        # Mark execution as completed
        await self.state_manager.complete_execution(
            str(execution_id),
            output_data=last_completed_output or {}
        )
    
    async def cancel(self, execution_id: str):
        """Cancel workflow execution."""
        await self.state_manager.cancel_execution(execution_id)
    
    # WebSocket emission methods
    async def _emit_step_started(
        self,
        execution_id: str,
        step_id: str,
        step_name: str,
        step_order: int,
        total_steps: int
    ):
        """Emit step started event via WebSocket."""
        if self.channel_layer:
            group_name = f'workflow_execution_{execution_id}'
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'step_started',
                    'step_id': step_id,
                    'step_name': step_name,
                    'step_order': step_order,
                    'total_steps': total_steps,
                    'timestamp': datetime.now().isoformat()
                }
            )
    
    async def _emit_step_completed(
        self,
        execution_id: str,
        step_id: str,
        step_name: str,
        success: bool,
        result: Any
    ):
        """Emit step completed event via WebSocket."""
        if self.channel_layer:
            group_name = f'workflow_execution_{execution_id}'
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'step_completed',
                    'step_id': step_id,
                    'step_name': step_name,
                    'success': success,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
            )
    
    async def _emit_progress(
        self,
        execution_id: str,
        percentage: int,
        current_step: int,
        total_steps: int
    ):
        """Emit progress update via WebSocket."""
        if self.channel_layer:
            group_name = f'workflow_execution_{execution_id}'
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'progress_update',
                    'percentage': percentage,
                    'current_step': current_step,
                    'total_steps': total_steps,
                    'message': f'Step {current_step} of {total_steps}',
                    'timestamp': datetime.now().isoformat()
                }
            )
    
    async def _emit_execution_complete(
        self,
        execution_id: str,
        success: bool,
        output: Any
    ):
        """Emit execution complete event via WebSocket."""
        if self.channel_layer:
            group_name = f'workflow_execution_{execution_id}'
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'execution_complete',
                    'execution_id': execution_id,
                    'success': success,
                    'output': output,
                    'timestamp': datetime.now().isoformat()
                }
            )
    
    async def _execute_api_call_step(
        self,
        execution_id: uuid.UUID,
        step: ParsedStep,
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an API call step.
        
        Args:
            execution_id: Execution UUID
            step: Step definition with API call config
            context: Workflow context
            user_id: User ID for authentication
            
        Returns:
            API call result
        """
        from apps.agents.services.api_caller import AgentAPICaller
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Get user
        if user_id:
            try:
                user = await User.objects.aget(id=user_id)
            except User.DoesNotExist:
                return {
                    'success': False,
                    'output': None,
                    'error': f'User {user_id} not found'
                }
        else:
            return {
                'success': False,
                'output': None,
                'error': 'user_id is required for API calls'
            }
        
        # Resolve step inputs
        step_inputs = self._resolve_step_inputs(step.inputs, context)
        
        # Get API call configuration
        method = step_inputs.get('method', 'GET')
        endpoint = step_inputs.get('endpoint', '')
        data = step_inputs.get('data')
        params = step_inputs.get('params')
        
        if not endpoint:
            return {
                'success': False,
                'output': None,
                'error': 'endpoint is required for API call step'
            }
        
        try:
            # Create API caller and make request
            async with AgentAPICaller(user=user) as api_caller:
                result = await api_caller.call(
                    method=method,
                    endpoint=endpoint,
                    data=data,
                    params=params
                )
                
                return {
                    'success': True,
                    'output': result
                }
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'error': f'API call failed: {str(e)}'
            }
    
    async def _execute_file_generation_step(
        self,
        execution_id: uuid.UUID,
        step: ParsedStep,
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a file generation step.
        
        Args:
            execution_id: Execution UUID
            step: Step definition with file generation config
            context: Workflow context
            user_id: User ID
            
        Returns:
            File generation result
        """
        from apps.projects.models import GeneratedProject
        from apps.projects.services.project_generator import ProjectGenerator, ProjectGenerationError
        import uuid as uuid_lib
        
        # Resolve step inputs
        step_inputs = self._resolve_step_inputs(step.inputs, context)
        
        # Get configuration
        project_id = step_inputs.get('project_id')
        project_structure = step_inputs.get('project_structure', {})
        
        if not project_id:
            return {
                'success': False,
                'output': None,
                'error': 'project_id is required for file generation step'
            }
        
        try:
            # Get or create GeneratedProject
            # Check if there's an existing one in context
            generated_project_id = context.get('generated_project_id')
            
            if generated_project_id:
                try:
                    generated_project = await GeneratedProject.objects.aget(id=generated_project_id)
                except GeneratedProject.DoesNotExist:
                    generated_project = None
            else:
                generated_project = None
            
            if not generated_project:
                # Create new GeneratedProject
                from apps.projects.models import Project
                try:
                    project = await Project.objects.aget(id=project_id)
                except Project.DoesNotExist:
                    return {
                        'success': False,
                        'output': None,
                        'error': f'Project {project_id} not found'
                    }
                
                output_dir = Path(settings.GENERATED_PROJECTS_DIR) / str(uuid_lib.uuid4())
                output_dir.mkdir(parents=True, exist_ok=True)
                
                generated_project = await GeneratedProject.objects.acreate(
                    project=project,
                    output_directory=str(output_dir),
                    status='generating',
                    created_by_id=user_id if user_id else None
                )
            
            # Update context
            context['generated_project_id'] = str(generated_project.id)
            
            # Generate files
            generator = ProjectGenerator(generated_project)
            created_files = generator.generate_project_structure(project_structure)
            
            # Update status
            generated_project.status = 'completed'
            generated_project.completed_at = timezone.now()
            await generated_project.asave()
            
            return {
                'success': True,
                'output': {
                    'generated_project_id': str(generated_project.id),
                    'files_created': len(created_files),
                    'file_paths': list(created_files.keys())
                }
            }
            
        except ProjectGenerationError as e:
            return {
                'success': False,
                'output': None,
                'error': f'File generation failed: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'error': f'Unexpected error: {str(e)}'
            }
    
    async def _execute_repo_creation_step(
        self,
        execution_id: uuid.UUID,
        step: ParsedStep,
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a repository creation step.
        
        Args:
            execution_id: Execution UUID
            step: Step definition with repo creation config
            context: Workflow context
            user_id: User ID
            
        Returns:
            Repository creation result
        """
        from apps.projects.models import GeneratedProject, RepositoryExport
        from apps.projects.services.repository_exporter import RepositoryExporter, RepositoryExportError
        
        # Resolve step inputs
        step_inputs = self._resolve_step_inputs(step.inputs, context)
        
        # Get configuration
        generated_project_id = step_inputs.get('generated_project_id') or context.get('generated_project_id')
        export_type = step_inputs.get('export_type', 'zip')
        
        if not generated_project_id:
            return {
                'success': False,
                'output': None,
                'error': 'generated_project_id is required for repo creation step'
            }
        
        try:
            generated_project = await GeneratedProject.objects.aget(id=generated_project_id)
        except GeneratedProject.DoesNotExist:
            return {
                'success': False,
                'output': None,
                'error': f'Generated project {generated_project_id} not found'
            }
        
        try:
            # Create export record
            export = await RepositoryExport.objects.acreate(
                generated_project=generated_project,
                export_type=export_type,
                status='exporting',
                repository_name=step_inputs.get('repository_name', ''),
                config=step_inputs.get('config', {}),
                created_by_id=user_id if user_id else None
            )
            
            exporter = RepositoryExporter(generated_project)
            
            if export_type == 'zip':
                archive_path = exporter.export_as_zip()
                export.archive_path = str(archive_path)
                export.archive_size = archive_path.stat().st_size
            elif export_type in ('tar', 'tar.gz'):
                gzip = export_type == 'tar.gz'
                archive_path = exporter.export_as_tar(gzip=gzip)
                export.archive_path = str(archive_path)
                export.archive_size = archive_path.stat().st_size
            elif export_type == 'github':
                github_token = step_inputs.get('github_token')
                if not github_token:
                    return {
                        'success': False,
                        'output': None,
                        'error': 'github_token is required for GitHub export'
                    }
                
                repo_info = await exporter.export_to_github(
                    github_token=github_token,
                    repository_name=step_inputs.get('repository_name', ''),
                    organization=step_inputs.get('organization'),
                    private=step_inputs.get('private', False)
                )
                export.repository_url = repo_info.get('repository_url', '')
            elif export_type == 'gitlab':
                gitlab_token = step_inputs.get('gitlab_token')
                if not gitlab_token:
                    return {
                        'success': False,
                        'output': None,
                        'error': 'gitlab_token is required for GitLab export'
                    }
                
                repo_info = await exporter.export_to_gitlab(
                    gitlab_token=gitlab_token,
                    project_name=step_inputs.get('project_name', ''),
                    namespace=step_inputs.get('namespace'),
                    visibility=step_inputs.get('visibility', 'private')
                )
                export.repository_url = repo_info.get('repository_url', '')
            else:
                return {
                    'success': False,
                    'output': None,
                    'error': f'Unsupported export type: {export_type}'
                }
            
            export.status = 'completed'
            export.completed_at = timezone.now()
            await export.asave()
            
            return {
                'success': True,
                'output': {
                    'export_id': str(export.id),
                    'export_type': export_type,
                    'repository_url': export.repository_url,
                    'archive_path': export.archive_path
                }
            }
            
        except RepositoryExportError as e:
            if 'export' in locals():
                export.status = 'failed'
                export.error_message = str(e)
                await export.asave()
            
            return {
                'success': False,
                'output': None,
                'error': f'Repository export failed: {str(e)}'
            }
        except Exception as e:
            if 'export' in locals():
                export.status = 'failed'
                export.error_message = str(e)
                await export.asave()
            
            return {
                'success': False,
                'output': None,
                'error': f'Unexpected error: {str(e)}'
            }
    
    async def _emit_execution_error(
        self,
        execution_id: str,
        message: str,
        error: str,
        step_id: Optional[str] = None
    ):
        """Emit execution error event via WebSocket."""
        if self.channel_layer:
            group_name = f'workflow_execution_{execution_id}'
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'execution_error',
                    'message': message,
                    'error': error,
                    'step_id': step_id,
                    'timestamp': datetime.now().isoformat()
                }
            )


# Global instance
workflow_executor = WorkflowExecutor()
