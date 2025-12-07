"""
Workflow Executor Service

Executes workflows with state management, conditional logic, error handling, and retry mechanisms.
Integrates with agents, manages execution lifecycle, and handles failures gracefully.
"""

import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .workflow_parser import workflow_parser, ParsedWorkflow, ParsedStep
from .conditional_evaluator import conditional_evaluator, ConditionalEvaluationError
from .state_manager import workflow_state_manager
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
        
        # Step 1: Get workflow and parse definition
        try:
            workflow = await Workflow.objects.aget(id=workflow_id)
        except Workflow.DoesNotExist:
            raise WorkflowExecutionError(f"Workflow '{workflow_id}' not found")
        
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
        current_step_number = 0
        
        # Execute steps starting from entry point
        current_step = parsed_workflow.entry_step
        last_output = None
        last_completed_output = None  # Track last non-skipped output
        
        while current_step:
            current_step_number += 1
            
            # Emit step started event
            await self._emit_step_started(
                str(execution_id),
                current_step.id,
                current_step.name,
                current_step_number,
                total_steps
            )
            
            # Execute current step
            step_result = await self._execute_step(
                execution_id,
                current_step,
                context,
                user_id=user_id
            )
            
            # Normalize step output for context storage
            # If output is a string, wrap it in a structured format for condition evaluation
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
            context['steps'][current_step.id] = normalized_result
            last_output = normalized_result.get('output')
            
            # Track last completed (non-skipped) output for final result
            if not normalized_result.get('skipped', False):
                last_completed_output = last_output
            
            # Emit step completed event
            await self._emit_step_completed(
                str(execution_id),
                current_step.id,
                current_step.name,
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
            
            # Save state after each step
            await self.state_manager.save_state(
                str(execution_id),
                current_step.id,
                context,
                'running'
            )
            
            # Determine next step
            if step_result['success']:
                next_step_id = current_step.on_success
            else:
                next_step_id = current_step.on_failure
            
            # Get next step or finish
            if next_step_id:
                current_step = parsed_workflow.step_map.get(next_step_id)
            else:
                break
        
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
        
        # Check execution condition
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
        """Resume paused workflow execution."""
        await self.state_manager.resume_execution(execution_id)
        
        # TODO: Implement actual resume logic (re-trigger execution from current step)
    
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
