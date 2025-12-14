"""
Execution Engine - coordinates agent execution with state management.

Provides high-level interface for executing agents with full lifecycle management.
"""

from typing import Dict, Any, Optional
import logging

from asgiref.sync import sync_to_async
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
            
        Raises:
            PermissionError: If organization/subscription checks fail
        """
        # Check organization status, subscription, and usage limits (same as ViewSet)
        from apps.core.services.roles import RoleService
        from apps.organizations.services import OrganizationStatusService, SubscriptionService
        
        organization = await sync_to_async(RoleService.get_user_organization)(user)
        
        # Super admins can bypass checks (but we still track usage if they have an org)
        if not await sync_to_async(RoleService.is_super_admin)(user) and organization:
            # Check organization status
            await sync_to_async(OrganizationStatusService.require_active_organization)(organization, user=user)
            
            # Check subscription active
            await sync_to_async(OrganizationStatusService.require_subscription_active)(organization, user=user)
            
            # Check tier-based usage limit
            await sync_to_async(SubscriptionService.check_usage_limit)(organization, 'agent_executions', user=user)
        
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
            
            # Create context - need to handle conversation_history from context dict
            metadata = context or {}
            conversation_history = metadata.get('conversation_history', [])
            
            agent_context = AgentContext(
                user=user,
                session_id=str(execution.id),
                conversation_history=conversation_history,
                metadata=metadata
            )
            
            # Mark as started
            await state_manager.start_execution(execution)
            
            # Stream response
            logger.info(f"[ExecutionEngine] Starting streaming execution, conversation_history={len(conversation_history)} messages")
            collected_output = []
            chunk_count = 0
            async for chunk in agent_instance.execute_streaming(input_data, agent_context):
                chunk_count += 1
                if chunk_count == 1:
                    logger.info(f"[ExecutionEngine] First chunk received, length: {len(chunk)}")
                collected_output.append(chunk)
                yield chunk
            
            logger.info(f"[ExecutionEngine] Streaming completed: {chunk_count} chunks, {len(''.join(collected_output))} total chars")
            
            # Complete execution
            full_output = ''.join(collected_output)
            
            # Extract conversation ID from response if available
            # This allows storing provider-specific conversation IDs for future requests
            try:
                if context and hasattr(context, 'metadata') and context.metadata:
                    platform_config = context.metadata.get('platform_config')
                    if platform_config:
                        # Get adapter to extract conversation ID
                        adapter = await agent_instance._get_registry()
                        adapter_instance = adapter.get_adapter(agent.preferred_platform)
                        if adapter_instance:
                            # Extract conversation ID from response metadata
                            # Note: For streaming, we may need to get this from response headers or final chunk
                            # This is provider-specific and may need adapter implementation
                            pass
            except Exception as e:
                logger.debug(f"[ExecutionEngine] Could not extract conversation ID: {e}")
            
            # Estimate tokens and cost for streaming response
            from apps.agents.utils.token_estimator import estimate_tokens, estimate_cost
            
            # Estimate output tokens
            output_tokens = estimate_tokens(full_output, agent.model_name)
            
            # Estimate input tokens (from input_data)
            input_text = str(input_data.get('prompt', ''))
            input_tokens = estimate_tokens(input_text, agent.model_name)
            
            # Calculate total tokens and cost
            total_tokens = input_tokens + output_tokens
            estimated_cost = estimate_cost(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=agent.model_name,
                platform=agent.preferred_platform
            )
            
            await state_manager.complete_execution(
                execution=execution,
                output_data=full_output,
                tokens_used=total_tokens,
                cost=estimated_cost,
                platform_used=agent.preferred_platform,
                model_used=agent.model_name
            )
            
            # Increment usage count after successful execution (only if organization exists)
            if organization:
                try:
                    await sync_to_async(SubscriptionService.increment_usage)(organization, 'agent_executions')
                except Exception as e:
                    logger.warning(f"Failed to increment usage count: {e}")
            
        except PermissionError:
            # Don't fail execution on permission errors - just raise them
            await state_manager.fail_execution(execution, "Organization/subscription/permission check failed")
            raise
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
