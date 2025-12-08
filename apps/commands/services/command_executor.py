"""
Command Executor - Executes command templates with agents.

Integrates parameter validation, template rendering, and agent execution.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging
import time
from decimal import Decimal

from asgiref.sync import sync_to_async

from apps.commands.models import CommandTemplate
from apps.agents.models import Agent
from apps.authentication.models import User
from apps.agents.services import execution_engine, dispatcher
from apps.commands.services.parameter_validator import ParameterValidator, ValidationResult
from apps.commands.services.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


@dataclass
class CommandExecutionResult:
    """Result of command execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    
    # Execution metadata
    command_id: str = None
    agent_id: str = None
    execution_time: float = 0.0
    cost: float = 0.0
    tokens_used: int = 0
    execution_id: Optional[str] = None  # CommandExecution record ID
    
    # Validation info
    validation_result: Optional[ValidationResult] = None


class CommandExecutor:
    """Execute command templates with AI agents."""
    
    def __init__(self):
        self.validator = ParameterValidator()
        self.renderer = TemplateRenderer()
    
    async def execute(
        self,
        command: CommandTemplate,
        parameters: Dict[str, Any],
        agent: Optional[Agent] = None,
        user: Optional[User] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> CommandExecutionResult:
        """
        Execute command template with parameters.
        
        Flow:
        1. Validate parameters
        2. Merge with defaults
        3. Render template
        4. Select agent if not specified
        5. Execute with agent
        6. Update command metrics
        7. Return result
        
        Args:
            command: CommandTemplate to execute
            parameters: User-provided parameters
            agent: Optional agent to use (auto-selected if not provided)
            user: User executing the command
            context: Optional execution context
            
        Returns:
            CommandExecutionResult
        """
        start_time = time.time()
        
        try:
            # Step 1: Validate parameters
            validation_result = self.validator.validate(
                command.parameters,
                parameters
            )
            
            if not validation_result.is_valid:
                return CommandExecutionResult(
                    success=False,
                    output=None,
                    error=f"Parameter validation failed: {'; '.join(validation_result.errors)}",
                    validation_result=validation_result,
                    command_id=str(command.id)
                )
            
            # Step 2: Merge with defaults
            complete_parameters = self.validator.merge_with_defaults(
                command.parameters,
                parameters
            )
            
            # Step 3: Render template
            rendered_prompt = self.renderer.render(command.template, complete_parameters)
            
            # Step 4: Select agent if not specified
            if agent is None:
                agent = await self._select_agent(command)
            
            if agent is None:
                return CommandExecutionResult(
                    success=False,
                    output=None,
                    error="No suitable agent available for this command",
                    command_id=str(command.id)
                )
            
            # Step 5: Execute with agent
            execution_result = await execution_engine.execute_agent(
                agent=agent,
                input_data={"prompt": rendered_prompt, **complete_parameters},
                user=user,
                context=context or {}
            )
            
            # Step 6: Create execution record and update command metrics
            execution_time = time.time() - start_time
            execution_time_ms = int(execution_time * 1000)
            
            # Create CommandExecution record
            from apps.commands.models import CommandExecution
            from django.utils import timezone
            
            command_execution = await sync_to_async(CommandExecution.objects.create)(
                command=command,
                user=user,
                input_parameters=complete_parameters,
                rendered_template=rendered_prompt,
                output=execution_result.output if execution_result.success else '',
                status='completed' if execution_result.success else 'failed',
                error_message=execution_result.error or '',
                execution_time_ms=execution_time_ms,
                tokens_used=execution_result.tokens_used or 0,
                cost=execution_result.cost or 0.0,
                agent_execution=execution_result.agent_execution if hasattr(execution_result, 'agent_execution') else None,
                completed_at=timezone.now()
            )
            
            # Update command metrics
            await sync_to_async(command.update_metrics)(
                success=execution_result.success,
                execution_time=execution_time,
                cost=execution_result.cost or 0.0
            )
            
            # Step 7: Return result
            return CommandExecutionResult(
                success=execution_result.success,
                output=execution_result.output,
                error=execution_result.error,
                command_id=str(command.id),
                agent_id=str(agent.agent_id),
                execution_time=execution_time,
                cost=execution_result.cost,
                tokens_used=execution_result.tokens_used,
                validation_result=validation_result,
                execution_id=str(command_execution.id)
            )
            
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}", exc_info=True)
            
            # Update failure metrics and create execution record
            execution_time = time.time() - start_time
            execution_time_ms = int(execution_time * 1000)
            
            try:
                # Create CommandExecution record for failure
                from apps.commands.models import CommandExecution
                from django.utils import timezone
                
                command_execution = await sync_to_async(CommandExecution.objects.create)(
                    command=command,
                    user=user,
                    input_parameters=parameters if 'parameters' in locals() else {},
                    rendered_template='',
                    output='',
                    status='failed',
                    error_message=str(e),
                    execution_time_ms=execution_time_ms,
                    tokens_used=0,
                    cost=0.0,
                    completed_at=timezone.now()
                )
                
                # Update command metrics
                await sync_to_async(command.update_metrics)(
                    success=False,
                    execution_time=execution_time,
                    cost=0.0
                )
            except Exception as metric_error:
                logger.error(f"Failed to create execution record or update metrics: {str(metric_error)}")
            
            return CommandExecutionResult(
                success=False,
                output=None,
                error=f"Execution error: {str(e)}",
                command_id=str(command.id),
                execution_time=execution_time
            )
    
    async def _select_agent(self, command: CommandTemplate) -> Optional[Agent]:
        """
        Select best agent for command.
        
        Priority:
        1. Recommended agent (if set)
        2. Agent with required capabilities
        3. Dispatcher-selected agent
        """
        # Try recommended agent first
        if command.recommended_agent:
            try:
                agent = await Agent.objects.aget(
                    agent_id=command.recommended_agent.agent_id,
                    status='active'
                )
                return agent
            except Agent.DoesNotExist:
                logger.warning(
                    f"Recommended agent {command.recommended_agent.agent_id} "
                    "not found or not active"
                )
        
        # Try to find agent with required capabilities
        if command.required_capabilities:
            try:
                agent = await dispatcher.select_agent(
                    required_capabilities=command.required_capabilities
                )
                if agent:
                    return agent
            except Exception as e:
                logger.warning(f"Dispatcher failed to select agent: {str(e)}")
        
        # Fallback: try to get any active agent
        try:
            agent = await Agent.objects.filter(status='active').afirst()
            return agent
        except Exception:
            return None
    
    def validate_parameters(
        self,
        command: CommandTemplate,
        parameters: Dict[str, Any]
    ) -> ValidationResult:
        """Validate parameters without executing."""
        return self.validator.validate(command.parameters, parameters)
    
    def preview_template(
        self,
        command: CommandTemplate,
        parameters: Dict[str, Any]
    ) -> str:
        """
        Preview rendered template without executing.
        
        Useful for debugging and user preview.
        """
        complete_parameters = self.validator.merge_with_defaults(
            command.parameters,
            parameters
        )
        return self.renderer.render(command.template, complete_parameters)


# Global executor instance
command_executor = CommandExecutor()
