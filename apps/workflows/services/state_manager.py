"""
Workflow State Manager Service

Manages workflow execution state persistence and recovery.
Handles state saving to database and Redis for fast access.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from django.core.cache import cache
from django.utils import timezone


class WorkflowStateManager:
    """
    Manage workflow execution state.
    
    Responsibilities:
    - Save execution state to database and Redis
    - Recover state from last successful step
    - Track execution progress
    - Handle state transitions
    """
    
    CACHE_TIMEOUT = 3600  # 1 hour
    CACHE_KEY_PREFIX = 'workflow_execution_'
    
    async def save_state(
        self,
        execution_id: str,
        current_step: str,
        state: Dict[str, Any],
        status: str = 'running'
    ):
        """
        Save workflow execution state.
        
        Args:
            execution_id: Execution UUID
            current_step: Current step ID
            state: Current state dictionary
            status: Execution status
        """
        from apps.workflows.models import WorkflowExecution
        
        # Update database
        execution = await WorkflowExecution.objects.aget(id=execution_id)
        execution.current_step = current_step
        execution.state = state
        execution.status = status
        await execution.asave()
        
        # Cache in Redis for fast access
        cache_key = f"{self.CACHE_KEY_PREFIX}{execution_id}"
        cache_data = {
            'current_step': current_step,
            'state': state,
            'status': status,
            'updated_at': datetime.now().isoformat()
        }
        cache.set(cache_key, json.dumps(cache_data), self.CACHE_TIMEOUT)
    
    async def get_state(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current execution state.
        
        Args:
            execution_id: Execution UUID
            
        Returns:
            State dictionary or None
        """
        # Try cache first
        cache_key = f"{self.CACHE_KEY_PREFIX}{execution_id}"
        cached = cache.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Fall back to database
        from apps.workflows.models import WorkflowExecution
        
        try:
            execution = await WorkflowExecution.objects.aget(id=execution_id)
            # Use completed_at or started_at as the "updated" timestamp
            updated_timestamp = None
            if execution.completed_at:
                updated_timestamp = execution.completed_at.isoformat()
            elif execution.started_at:
                updated_timestamp = execution.started_at.isoformat()
            elif execution.created_at:
                updated_timestamp = execution.created_at.isoformat()
            
            return {
                'current_step': execution.current_step,
                'state': execution.state,
                'status': execution.status,
                'updated_at': updated_timestamp
            }
        except WorkflowExecution.DoesNotExist:
            return None
    
    async def record_step_start(
        self,
        execution_id: str,
        step_id: str
    ):
        """
        Record that a step has started.
        
        Args:
            execution_id: Execution UUID
            step_id: Step ID
        """
        from apps.workflows.models import WorkflowExecution
        
        execution = await WorkflowExecution.objects.aget(id=execution_id)
        
        # Update current step and status
        if execution.status == 'pending':
            execution.status = 'running'
            execution.started_at = timezone.now()
        
        execution.current_step = step_id
        await execution.asave()
    
    async def record_step_completion(
        self,
        execution_id: str,
        step_id: str,
        output: Any,
        success: bool = True
    ):
        """
        Record step completion.
        
        Args:
            execution_id: Execution UUID
            step_id: Step ID
            output: Step output
            success: Whether step succeeded
        """
        execution_state = await self.get_state(execution_id)
        
        if execution_state:
            state = execution_state['state']
            
            # Store step output in state
            if 'steps' not in state:
                state['steps'] = {}
            
            state['steps'][step_id] = {
                'output': output,
                'success': success,
                'completed_at': datetime.now().isoformat()
            }
            
            await self.save_state(
                execution_id,
                execution_state['current_step'],
                state,
                execution_state['status']
            )
    
    async def record_execution_complete(
        self,
        execution_id: str,
        final_output: Any,
        success: bool = True
    ):
        """
        Record workflow execution completion.
        
        Args:
            execution_id: Execution UUID
            final_output: Final workflow output
            success: Whether workflow succeeded
        """
        from apps.workflows.models import WorkflowExecution
        
        execution = await WorkflowExecution.objects.aget(id=execution_id)
        
        execution.status = 'completed' if success else 'failed'
        execution.output_data = final_output
        execution.completed_at = timezone.now()
        
        await execution.asave()
        
        # Clear cache
        cache_key = f"{self.CACHE_KEY_PREFIX}{execution_id}"
        cache.delete(cache_key)
    
    async def record_execution_failure(
        self,
        execution_id: str,
        error_message: str,
        retry_count: int = 0
    ):
        """
        Record workflow execution failure.
        
        Args:
            execution_id: Execution UUID
            error_message: Error description
            retry_count: Number of retries attempted
        """
        from apps.workflows.models import WorkflowExecution
        
        execution = await WorkflowExecution.objects.aget(id=execution_id)
        
        execution.status = 'failed'
        execution.error_message = error_message
        execution.retry_count = retry_count
        execution.completed_at = timezone.now()
        
        await execution.asave()
        
        # Clear cache
        cache_key = f"{self.CACHE_KEY_PREFIX}{execution_id}"
        cache.delete(cache_key)
    
    async def recover(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Recover workflow state from last successful step.
        
        Args:
            execution_id: Execution UUID
            
        Returns:
            Recovery state with last successful step info or None
        """
        state = await self.get_state(execution_id)
        
        if not state:
            return None
        
        # Find last successfully completed step
        steps = state.get('state', {}).get('steps', {})
        last_successful_step = None
        
        for step_id, step_data in steps.items():
            if step_data.get('success'):
                last_successful_step = step_id
        
        return {
            'execution_id': execution_id,
            'last_successful_step': last_successful_step,
            'current_step': state['current_step'],
            'state': state['state'],
            'can_resume': state['status'] in ['running', 'failed']
        }
    
    async def pause_execution(self, execution_id: str):
        """
        Pause a running workflow execution.
        
        Args:
            execution_id: Execution UUID
        """
        from apps.workflows.models import WorkflowExecution
        
        execution = await WorkflowExecution.objects.aget(id=execution_id)
        
        if execution.status == 'running':
            execution.status = 'paused'
            await execution.asave()
            
            # Update cache
            state = await self.get_state(execution_id)
            if state:
                state['status'] = 'paused'
                cache_key = f"{self.CACHE_KEY_PREFIX}{execution_id}"
                cache.set(cache_key, json.dumps(state), self.CACHE_TIMEOUT)
    
    async def resume_execution(self, execution_id: str):
        """
        Resume a paused workflow execution.
        
        Args:
            execution_id: Execution UUID
        """
        from apps.workflows.models import WorkflowExecution
        
        execution = await WorkflowExecution.objects.aget(id=execution_id)
        
        if execution.status == 'paused':
            execution.status = 'running'
            await execution.asave()
            
            # Update cache
            state = await self.get_state(execution_id)
            if state:
                state['status'] = 'running'
                cache_key = f"{self.CACHE_KEY_PREFIX}{execution_id}"
                cache.set(cache_key, json.dumps(state), self.CACHE_TIMEOUT)
    
    async def cancel_execution(self, execution_id: str):
        """
        Cancel a workflow execution.
        
        Args:
            execution_id: Execution UUID
        """
        from apps.workflows.models import WorkflowExecution
        
        execution = await WorkflowExecution.objects.aget(id=execution_id)
        
        if execution.status in ['pending', 'running', 'paused']:
            execution.status = 'cancelled'
            execution.completed_at = timezone.now()
            await execution.asave()
            
            # Clear cache
            cache_key = f"{self.CACHE_KEY_PREFIX}{execution_id}"
            cache.delete(cache_key)


# Global instance
workflow_state_manager = WorkflowStateManager()
