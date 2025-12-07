"""
Base adapter interface for AI platforms.

This module defines the abstract base class that all AI platform adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class CompletionRequest:
    """Standardized completion request across all platforms."""
    
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: Optional[str] = None
    stop_sequences: Optional[List[str]] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    user_id: Optional[str] = None  # For tracking
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'prompt': self.prompt,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'system_prompt': self.system_prompt,
            'stop_sequences': self.stop_sequences,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'user_id': self.user_id,
        }


@dataclass
class CompletionResponse:
    """Standardized completion response from all platforms."""
    
    content: str
    model: str
    platform: str
    tokens_used: int
    cost: float
    finish_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'content': self.content,
            'model': self.model,
            'platform': self.platform,
            'tokens_used': self.tokens_used,
            'cost': self.cost,
            'finish_reason': self.finish_reason,
            'metadata': self.metadata,
        }


class BaseAIAdapter(ABC):
    """
    Abstract base class for AI platform adapters.
    
    All platform-specific adapters (OpenAI, Anthropic, Gemini) must inherit from this class
    and implement all abstract methods.
    """
    
    def __init__(self, platform_config):
        """
        Initialize adapter with platform configuration.
        
        Args:
            platform_config: AIPlatform model instance with configuration
        """
        self.platform_config = platform_config
        self.platform_name = platform_config.platform_name
        # Use get_api_key() to decrypt the API key
        self.api_key = platform_config.get_api_key()
        self.default_model = platform_config.default_model
        self.max_retries = 3
        self.retry_delay = 1.0
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def generate_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> CompletionResponse:
        """
        Generate a completion using the AI platform.
        
        Args:
            request: Standardized completion request
            model: Optional model override (uses default if not specified)
            
        Returns:
            CompletionResponse with standardized format
            
        Raises:
            AIAdapterError: On platform-specific errors
        """
        pass
    
    @abstractmethod
    async def generate_streaming_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Generate a streaming completion.
        
        Args:
            request: Standardized completion request
            model: Optional model override
            
        Yields:
            String chunks as they are generated
            
        Raises:
            AIAdapterError: On platform-specific errors
        """
        pass
    
    @abstractmethod
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for token usage.
        
        Args:
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        pass
    
    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """
        Check platform health status.
        
        Returns:
            Dictionary with health status information:
            {
                'status': 'healthy'|'unhealthy',
                'latency_ms': float,
                'available': bool,
                'error': Optional[str]
            }
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of available models for this platform.
        
        Returns:
            List of model identifiers
        """
        pass
    
    @abstractmethod
    def validate_request(self, request: CompletionRequest, model: str) -> None:
        """
        Validate request parameters for this platform.
        
        Args:
            request: Completion request to validate
            model: Model to validate against
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    async def _retry_with_backoff(self, func, *args, **kwargs):
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Async function to retry
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        import asyncio
        
        last_exception = None
        delay = self.retry_delay
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self.logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}"
                )
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff
        
        raise last_exception
