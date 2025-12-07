"""
Execution Engine - coordinates agent execution with state management.

Provides high-level interface for executing agents with full lifecycle management.
"""

from typing import Dict, Any, Optional
import logging

from apps.agents.models import Agent
from apps.agents.engine import BaseAgent, TaskAgent, ConversationalAgent, AgentContext, AgentResult
from .state_manager import state_manager


logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    Coordinates agent execution with state management.
    
    Provides a high-level interface for:
    - Creating agent instances from database models
    - Managing execution lifecycle
    - State persistence
    - Error handling
    """
    
    async def execute_agent(
        self,
        agent: Agent,
        input_data: Dict[str, Any],
        user: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """
        Execute an agent with full lifecycle management.
        
        Args:
            agent: Agent model instance
            input_data: Input data for execution
            user: User initiating execution
            context: Additional context
            
        Returns:
            AgentResult with execution results
        """
        # Create execution record
        execution = await state_manager.create_execution(
            agent=agent,
            input_data=input_data,
            user=user,
            context=context
        )
        
        try:
            # Create agent instance
            agent_instance = self._create_agent_instance(agent)
            
            # Create execution context
            agent_context = AgentContext(
                user=user,
                session_id=str(execution.id),
                conversation_history=context.get('conversation_history', []) if context else [],
                metadata=context or {}
            )
            
            # Mark as started
            await state_manager.start_execution(execution)
            
            # Execute
            result = await agent_instance.execute(input_data, agent_context)
            
            # Update execution record
            if result.success:
                await state_manager.complete_execution(
                    execution=execution,
                    output_data=result.output,
                    tokens_used=result.tokens_used,
                    cost=result.cost,
                    platform_used=result.platform_used,
                    model_used=result.model_used
                )
            else:
                await state_manager.fail_execution(
                    execution=execution,
                    error_message=result.error or "Unknown error"
                )
            
            # Add execution ID to result metadata
            result.metadata['execution_id'] = str(execution.id)
            
            return result
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Execution failed unexpectedly: {str(e)}", exc_info=True)
            
            await state_manager.fail_execution(
                execution=execution,
                error_message=str(e)
            )
            
            return AgentResult(
                success=False,
                output=None,
                error=str(e),
                metadata={'execution_id': str(execution.id)}
            )
    
    async def execute_streaming(
        self,
        agent: Agent,
        input_data: Dict[str, Any],
        user: Any,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Execute agent with streaming response.
        
        Args:
            agent: Agent model instance
            input_data: Input data
            user: User
            context: Additional context
            
        Yields:
            Response chunks
        """
        # Create execution record
        execution = await state_manager.create_execution(
            agent=agent,
            input_data=input_data,
            user=user,
            context=context
        )
        
        try:
            # Create agent instance
            agent_instance = self._create_agent_instance(agent)
            
            # Create context
            agent_context = AgentContext(
                user=user,
                session_id=str(execution.id),
                metadata=context or {}
            )
            
            # Mark as started
            await state_manager.start_execution(execution)
            
            # Stream response
            collected_output = []
            async for chunk in agent_instance.execute_streaming(input_data, agent_context):
                collected_output.append(chunk)
                yield chunk
            
            # Complete execution
            full_output = ''.join(collected_output)
            await state_manager.complete_execution(
                execution=execution,
                output_data=full_output,
                tokens_used=0,  # TODO: estimate tokens
                cost=0.0,  # TODO: calculate cost
                platform_used=agent.preferred_platform,
                model_used=agent.model_name
            )
            
        except Exception as e:
            logger.error(f"Streaming execution failed: {str(e)}", exc_info=True)
            await state_manager.fail_execution(execution, str(e))
            raise
    
    def _create_agent_instance(self, agent: Agent) -> BaseAgent:
        """
        Create agent instance from database model.
        
        Args:
            agent: Agent model instance
            
        Returns:
            BaseAgent subclass instance
        """
        # Determine agent type based on capabilities
        capabilities = agent.capabilities or []
        
        # Choose appropriate agent class
        if 'CONVERSATION' in capabilities:
            agent_class = ConversationalAgent
        elif 'TASK_EXECUTION' in capabilities:
            agent_class = TaskAgent
        else:
            # Default to TaskAgent
            agent_class = TaskAgent
        
        # Create instance
        return agent_class(
            agent_id=agent.agent_id,
            name=agent.name,
            description=agent.description,
            system_prompt=agent.system_prompt,
            capabilities=capabilities,
            preferred_platform=agent.preferred_platform,
            fallback_platforms=agent.fallback_platforms or [],
            model_name=agent.model_name,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens
        )
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution status.
        
        Args:
            execution_id: Execution UUID
            
        Returns:
            Dictionary with execution status
        """
        execution = await state_manager.get_execution(execution_id)
        
        if not execution:
            return None
        
        return {
            'id': str(execution.id),
            'agent':  execution.agent.name,
            'status': execution.status,
            'created_at': execution.created_at.isoformat(),
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'execution_time': execution.execution_time,
            'tokens_used': execution.tokens_used,
            'cost': float(execution.cost),
            'error': execution.error_message if execution.status == 'failed' else None
        }


# Global execution engine instance
execution_engine = ExecutionEngine()
