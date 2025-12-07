"""
Base agent class for all AI agents in HishamOS.

This module provides the abstract base class that all agents inherit from,
integrating with AI platform adapters and providing common functionality.
"""

from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import logging
import time
from datetime import datetime

from apps.integrations.services import get_registry, tracker
from apps.integrations.adapters.base import CompletionRequest, CompletionResponse


logger = logging.getLogger(__name__)


class AgentCapability(str, Enum):
    """Agent capability types."""
    CODE_GENERATION = 'CODE_GENERATION'
    CODE_REVIEW = 'CODE_REVIEW'
    REQUIREMENTS_ANALYSIS = 'REQUIREMENTS_ANALYSIS'
    USER_STORY_GENERATION = 'USER_STORY_GENERATION'
    PROJECT_MANAGEMENT = 'PROJECT_MANAGEMENT'
    TESTING = 'TESTING'
    DOCUMENTATION = 'DOCUMENTATION'
    DEVOPS = 'DEVOPS'
    CONVERSATION = 'CONVERSATION'
    TASK_EXECUTION = 'TASK_EXECUTION'


@dataclass
class AgentContext:
    """Context for agent execution."""
    user: Any  # User object
    session_id: Optional[str] = None
    conversation_history: List[Dict[str, str]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AgentResult:
    """Result of agent execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    tokens_used: int = 0
    cost: float = 0.0
    execution_time: float = 0.0
    platform_used: str = ''
    model_used: str = ''
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAgent:
    """
    Abstract base class for all AI agents.
    
    Provides common functionality:
    - AI adapter integration
    - Execution lifecycle management
    - Error handling and retries
    - Cost and token tracking
    - Context management
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        system_prompt: str,
        capabilities: List[AgentCapability],
        preferred_platform: str = 'openai',
        fallback_platforms: Optional[List[str]] = None,
        model_name: str = 'gpt-3.5-turbo',
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ):
        """
        Initialize base agent.
        
        Args:
            agent_id: Unique agent identifier
            name: Human-readable agent name
            description: Agent description
            system_prompt: System prompt for the agent
            capabilities: List of agent capabilities
            preferred_platform: Preferred AI platform
            fallback_platforms: Fallback platforms if preferred fails
            model_name: Model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens
        """
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.capabilities = capabilities
        self.preferred_platform = preferred_platform
        self.fallback_platforms = fallback_platforms or ['anthropic', 'google']
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Runtime state
        self._registry = None
    
    async def execute(
        self,
        input_data: Dict[str, Any],
        context: Optional[AgentContext] = None
    ) -> AgentResult:
        """
        Execute the agent with given input.
        
        This is the main entry point for agent execution.
        
        Args:
            input_data: Input data for the agent
            context: Execution context
            
        Returns:
            AgentResult with execution results
        """
        start_time = time.time()
        
        try:
            # Prepare context
            if context is None:
                context = AgentContext(user=None)
            
            # Pre-execution hook
            await self._pre_execute(input_data, context)
            
            # Prepare prompt
            prompt = await self.prepare_prompt(input_data, context)
            
            # Execute with AI
            response = await self._execute_with_ai(prompt, context)
            
            # Process response
            output = await self.process_response(response, input_data, context)
            
            # Post-execution hook
            await self._post_execute(output, context)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Track usage
            if context.user:
                await tracker.track_completion(
                    response,
                    self.preferred_platform,
                    context.user
                )
            
            return AgentResult(
                success=True,
                output=output,
                tokens_used=response.tokens_used,
                cost=response.cost,
                execution_time=execution_time,
                platform_used=response.platform,
                model_used=response.model,
                metadata=response.metadata
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = await self.handle_error(e, input_data, context)
            
            return AgentResult(
                success=False,
                output=None,
                error=error_msg,
                execution_time=execution_time
            )
    
    async def execute_streaming(
        self,
        input_data: Dict[str, Any],
        context: Optional[AgentContext] = None
    ) -> AsyncGenerator[str, None]:
        """
        Execute agent with streaming response.
        
        Args:
            input_data: Input data
            context: Execution context
            
        Yields:
            Response chunks as they arrive
        """
        if context is None:
            context = AgentContext(user=None)
        
        # Prepare prompt
        prompt = await self.prepare_prompt(input_data, context)
        
        # Get adapter
        registry = await self._get_registry()
        adapter = registry.get_adapter(self.preferred_platform)
        
        if not adapter:
            raise ValueError(f"Platform {self.preferred_platform} not available")
        
        # Create request
        request = CompletionRequest(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        
        # Stream response
        async for chunk in adapter.generate_streaming_completion(request, self.model_name):
            yield chunk
    
    async def prepare_prompt(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> str:
        """
        Prepare the prompt for AI execution.
        
        Override this method to customize prompt preparation.
        
        Args:
            input_data: Input data
            context: Execution context
            
        Returns:
            Prepared prompt string
        """
        # Default implementation - override in subclasses
        if isinstance(input_data, dict):
            if 'prompt' in input_data:
                return input_data['prompt']
            elif 'task' in input_data:
                return input_data['task']
            elif 'message' in input_data:
                return input_data['message']
        
        return str(input_data)
    
    async def process_response(
        self,
        response: CompletionResponse,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> Any:
        """
        Process the AI response.
        
        Override this method to customize response processing.
        
        Args:
            response: AI response
            input_data: Original input
            context: Execution context
            
        Returns:
            Processed output
        """
        # Default implementation - return content as-is
        return response.content
    
    async def handle_error(
        self,
        error: Exception,
        input_data: Dict[str, Any],
        context: AgentContext
    ) -> str:
        """
        Handle execution errors.
        
        Args:
            error: The exception that occurred
            input_data: Input data
            context: Execution context
            
        Returns:
            Error message
        """
        error_msg = f"Agent execution failed: {str(error)}"
        logger.error(f"{self.name} - {error_msg}", exc_info=True)
        return error_msg
    
    async def _pre_execute(
        self,
        input_data: Dict[str, Any],
        context: AgentContext
    ):
        """Pre-execution hook. Override to add custom logic."""
        pass
    
    async def _post_execute(
        self,
        output: Any,
        context: AgentContext
    ):
        """Post-execution hook. Override to add custom logic."""
        pass
    
    async def _execute_with_ai(
        self,
        prompt: str,
        context: AgentContext
    ) -> CompletionResponse:
        """
        Execute prompt with AI adapter.
        
        Handles platform selection and fallback.
        
        Args:
            prompt: Prepared prompt
            context: Execution context
            
        Returns:
            CompletionResponse from AI
        """
        # Get adapter registry
        registry = await self._get_registry()
        
        # Try preferred platform first
        platforms_to_try = [self.preferred_platform] + self.fallback_platforms
        
        # Always ensure mock is available as a fallback
        available_adapters = registry.get_all_adapters()
        
        # If no adapters are available, ensure mock is added to registry
        if not available_adapters:
            try:
                # Re-initialize registry to ensure mock adapter is added
                if not registry._initialized:
                    await registry.initialize()
                else:
                    # Force add mock adapter if registry is initialized but empty
                    from apps.integrations.adapters.mock_adapter import MockAdapter
                    mock_adapter = MockAdapter()
                    # Use the public method if available, otherwise access directly
                    if hasattr(registry, '_adapters'):
                        registry._adapters['mock'] = mock_adapter
                    logger.info("Added mock adapter as fallback")
                available_adapters = registry.get_all_adapters()
            except Exception as e:
                logger.warning(f"Failed to add mock adapter: {str(e)}")
        
        # Add mock to platforms_to_try if not already there and no other adapters work
        if 'mock' not in platforms_to_try:
            # If only mock is available, use it first
            if len(available_adapters) == 1 and 'mock' in available_adapters:
                platforms_to_try = ['mock'] + platforms_to_try
            # Otherwise, add it as last resort
            else:
                platforms_to_try.append('mock')
        
        last_error = None
        for platform_name in platforms_to_try:
            adapter = registry.get_adapter(platform_name)
            
            if not adapter:
                logger.warning(f"Platform {platform_name} not available")
                continue
            
            try:
                request = CompletionRequest(
                    prompt=prompt,
                    system_prompt=self.system_prompt,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                
                response = await adapter.generate_completion(request, self.model_name)
                
                # Update which platform was actually used
                self.preferred_platform = platform_name
                
                return response
                
            except Exception as e:
                logger.error(f"Failed with {platform_name}: {str(e)}")
                last_error = e
                continue
        
        # All platforms failed
        raise Exception(f"All platforms failed. Last error: {str(last_error)}")
    
    async def _get_registry(self):
        """Get or initialize adapter registry."""
        if self._registry is None:
            self._registry = await get_registry()
        # Ensure registry is initialized
        if not self._registry._initialized:
            await self._registry.initialize()
        return self._registry
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities
