"""
Task Agent - executes specific tasks and returns structured results.
"""

from typing import Dict, Any, Optional
import json
import logging

from .base_agent import BaseAgent, AgentCapability, AgentContext, AgentResult, CompletionResponse


logger = logging.getLogger(__name__)


class TaskAgent(BaseAgent):
    """
    Agent specialized for executing specific tasks.
    
    Task agents are designed to:
    - Execute well-defined tasks
    - Return structured results
    - Support tool calling (future)
    - Provide deterministic outputs
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        system_prompt: str,
        **kwargs
    ):
        """Initialize task agent."""
        # Task agents always have TASK_EXECUTION capability
        capabilities = kwargs.pop('capabilities', [])
        if AgentCapability.TASK_EXECUTION not in capabilities:
            capabilities.append(AgentCapability.TASK_EXECUTION)
        
        # Default to lower temperature for more deterministic results
        temperature = kwargs.pop('temperature', 0.3)
        
        super().__init__(
            agent_id=agent_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            capabilities=capabilities,
            temperature=temperature,
            **kwargs
        )
    
    async def prepare_prompt(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> str:
        """
        Prepare prompt for task execution.
        
        Formats the task clearly and requests structured output.
        """
        task_description = input_data.get('task', input_data.get('prompt', ''))
        
        # Build prompt with clear structure
        prompt_parts = []
        
        # Add task description
        prompt_parts.append(f"Task: {task_description}")
        
        # Add context if provided
        if input_data.get('context'):
            prompt_parts.append(f"\nContext: {input_data['context']}")
        
        # Add requirements
        if input_data.get('requirements'):
            prompt_parts.append("\nRequirements:")
            for req in input_data['requirements']:
                prompt_parts.append(f"- {req}")
        
        # Add output format instructions
        if input_data.get('output_format'):
            prompt_parts.append(f"\nOutput Format: {input_data['output_format']}")
        
        return "\n".join(prompt_parts)
    
    async def process_response(
        self,
        response: CompletionResponse,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> Any:
        """
        Process AI response for task execution.
        
        Attempts to parse structured output if requested.
        """
        content = response.content
        
        # If JSON output was requested, try to parse it
        if input_data.get('output_format') == 'json':
            try:
                # Try to extract JSON from response
                # Sometimes models wrap JSON in code blocks
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                elif '```' in content:
                    json_start = content.find('```') + 3
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                
                return json.loads(content)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, returning as text")
                return content
        
        return content
    
    async def execute_with_tools(
        self,
        input_data: Dict[str, Any],
        tools: list,
        context: Optional[AgentContext] = None
    ) -> AgentResult:
        """
        Execute task with tool calling support.
        
        Future implementation for function calling.
        
        Args:
            input_data: Task input
            tools: Available tools
            context: Execution context
            
        Returns:
            AgentResult with tool call results
        """
        # TODO: Implement tool calling in future phase
        raise NotImplementedError("Tool calling not yet implemented")
