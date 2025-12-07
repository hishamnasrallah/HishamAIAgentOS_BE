"""
State Manager - manages agent execution state and persistence.

Tracks execution status, progress, and results using AgentExecution model.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from asgiref.sync import sync_to_async
from django.db.models import Sum, Avg
from apps.agents.models import Agent, AgentExecution


logger = logging.getLogger(__name__)


class StateManager:
    """Manages agent execution state."""
    
    async def create_execution(
        self,
        agent: Agent,
        input_data: Dict[str, Any],
        user: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentExecution:
        """
        Create a new agent execution record.
        
        Args:
            agent: Agent instance
            input_data: Input data for execution
            user: User initiating execution
            context: Additional context
            
        Returns:
            AgentExecution instance
        """
        execution = await sync_to_async(AgentExecution.objects.create)(
            agent=agent,
            user=user,
            input_data=input_data,
            context=context or {},
            status='pending',
            platform_used=agent.preferred_platform,
            model_used=agent.model_name
        )
        
        logger.info(f"Created execution {execution.id} for agent {agent.agent_id}")
        return execution
    
    async def start_execution(self, execution: AgentExecution):
        """
        Mark execution as started.
        
        Args:
            execution: AgentExecution instance
        """
        execution.status = 'running'
        execution.started_at = datetime.now()
        await sync_to_async(execution.save)(update_fields=['status', 'started_at'])
        
        logger.info(f"Started execution {execution.id}")
    
    async def complete_execution(
        self,
        execution: AgentExecution,
        output_data: Any,
        tokens_used: int,
        cost: float,
        platform_used: str,
        model_used: str
    ):
        """
        Mark execution as completed successfully.
        
        Args:
            execution: AgentExecution instance
            output_data: Output from agent
            tokens_used: Token count
            cost: Execution cost
            platform_used: Platform that was used
            model_used: Model that was used
        """
        execution.status = 'completed'
        execution.output_data = output_data
        execution.tokens_used = tokens_used
        execution.cost = cost
        execution.platform_used = platform_used
        execution.model_used = model_used
        execution.completed_at = datetime.now()
        
        if execution.started_at:
            execution.execution_time = (
                execution.completed_at - execution.started_at
            ).total_seconds()
        
        await sync_to_async(execution.save)()
        
        # Update agent metrics
        await self._update_agent_metrics(execution.agent, success=True)
        
        logger.info(f"Completed execution {execution.id}")
    
    async def fail_execution(
        self,
        execution: AgentExecution,
        error_message: str
    ):
        """
        Mark execution as failed.
        
        Args:
            execution: AgentExecution instance
            error_message: Error message
        """
        execution.status = 'failed'
        execution.error_message = error_message
        execution.completed_at = datetime.now()
        
        if execution.started_at:
            execution.execution_time = (
                execution.completed_at - execution.started_at
            ).total_seconds()
        
        await sync_to_async(execution.save)()
        
        # Update agent metrics
        await self._update_agent_metrics(execution.agent, success=False)
        
        logger.error(f"Failed execution {execution.id}: {error_message}")
    
    async def cancel_execution(self, execution: AgentExecution):
        """
        Cancel an execution.
        
        Args:
            execution: AgentExecution instance
        """
        execution.status = 'cancelled'
        execution.completed_at = datetime.now()
        
        if execution.started_at:
            execution.execution_time = (
                execution.completed_at - execution.started_at
            ).total_seconds()
        
        await sync_to_async(execution.save)()
        
        logger.info(f"Cancelled execution {execution.id}")
    
    async def get_execution(self, execution_id: str) -> Optional[AgentExecution]:
        """
        Get execution by ID.
        
        Args:
            execution_id: Execution UUID
            
        Returns:
            AgentExecution instance or None
        """
        try:
            return await sync_to_async(
                AgentExecution.objects.select_related('agent', 'user').get
            )(id=execution_id)
        except AgentExecution.DoesNotExist:
            return None
    
    async def get_agent_executions(
        self,
        agent: Agent,
        limit: int = 10
    ) -> list:
        """
        Get recent executions for an agent.
        
        Args:
            agent: Agent instance
            limit: Maximum number of executions
            
        Returns:
            List of AgentExecution instances
        """
        executions = await sync_to_async(list)(
            AgentExecution.objects.filter(agent=agent)
            .select_related('user')
            .order_by('-created_at')[:limit]
        )
        return executions
    
    async def _update_agent_metrics(self, agent: Agent, success: bool):
        """
        Update agent metrics after execution.
        
        Args:
            agent: Agent instance
            success: Whether execution succeeded
        """
        from django.db.models import Avg, F
        
        # Increment invocation count
        agent.total_invocations = F('total_invocations') + 1
        agent.last_invoked_at = datetime.now()
        
        # Update success rate
        if success:
            total_executions = await sync_to_async(
                agent.executions.count
            )()
            successful_executions = await sync_to_async(
                agent.executions.filter(status='completed').count
            )()
            
            if total_executions > 0:
                agent.success_rate = (successful_executions / total_executions) * 100
        
        # Update from executions
        stats = await sync_to_async(agent.executions.filter(status='completed').aggregate)(
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('cost'),
            avg_time=Avg('execution_time')
        )
        
        if stats['total_tokens']:
            agent.total_tokens_used = stats['total_tokens']
        if stats['total_cost']:
            from decimal import Decimal
            agent.total_cost = Decimal(str(stats['total_cost']))
        if stats['avg_time']:
            agent.average_response_time = stats['avg_time']
        
        await sync_to_async(agent.save)()


# Global state manager instance
state_manager = StateManager()
