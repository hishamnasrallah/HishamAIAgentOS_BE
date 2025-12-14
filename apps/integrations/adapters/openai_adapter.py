"""
OpenAI platform adapter implementation.

Provides integration with OpenAI's API including GPT-4, GPT-3.5 models
with support for both standard and streaming completions.
"""

import openai
import httpx
from typing import Optional, AsyncIterator, Dict, List, Any
import time
import asyncio

from .base import BaseAIAdapter, CompletionRequest, CompletionResponse
from ..utils.pricing import OpenAIPricing
from ..utils.validators import OpenAIValidator
from ..utils.exceptions import OpenAIError, ValidationError


class OpenAIAdapter(BaseAIAdapter):
    """OpenAI platform adapter with GPT-4 and GPT-3.5 support."""
    
    # Model mapping: friendly name -> OpenAI model ID
    MODELS = {
        'gpt-4-turbo': 'gpt-4-1106-preview',
        'gpt-4': 'gpt-4',
        'gpt-3.5-turbo': 'gpt-3.5-turbo',
        'gpt-3.5-turbo-16k': 'gpt-3.5-turbo-16385',
    }
    
    def __init__(self, platform_config):
        """Initialize OpenAI adapter."""
        super().__init__(platform_config)
        
        # Create a custom httpx client without proxies to avoid compatibility issues
        # This works around the issue where OpenAI library tries to pass 'proxies' to httpx.AsyncClient
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        # Initialize OpenAI client with custom http_client
        # Set max_retries=0 - we handle retries via _retry_with_backoff for non-streaming
        # For streaming, retries don't make sense, so disable them
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            http_client=http_client,
            max_retries=0  # Disable automatic retries - we handle retries explicitly
        )
        self.pricing = OpenAIPricing()
        self.validator = OpenAIValidator()
        self.logger.info(f"OpenAI adapter initialized with model: {self.default_model}")
    
    async def generate_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> CompletionResponse:
        """
        Generate completion using OpenAI.
        
        Args:
            request: Standardized completion request
            model: Optional model override
            
        Returns:
            CompletionResponse with generated content
            
        Raises:
            OpenAIError: On API errors
            ValidationError: On invalid parameters
        """
        model = model or self.default_model
        model_id = self.MODELS.get(model, model)
        
        # Validate request
        self.validate_request(request, model)
        
        # Build messages
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        #  Build API params
        params = {
            "model": model_id,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        
        # Add optional params
        if request.top_p is not None:
            params["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            params["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            params["presence_penalty"] = request.presence_penalty
        if request.stop_sequences:
            params["stop"] = request.stop_sequences
        
        try:
            start_time = time.time()
            
            # Make API call with retry
            response = await self._retry_with_backoff(
                self.client.chat.completions.create,
                **params
            )
            
            latency = time.time() - start_time
            
            # Extract response data
            completion = response.choices[0]
            usage = response.usage
            
            # Calculate cost
            cost = self.calculate_cost(
                model_id,
                usage.prompt_tokens,
                usage.completion_tokens
            )
            
            self.logger.info(
                f"OpenAI completion: {usage.total_tokens} tokens, "
                f"${cost:.6f}, {latency:.2f}s"
            )
            
            # Extract ALL identifiers and metadata from response
            all_identifiers = self.extract_all_identifiers(response, None)
            all_metadata = self.extract_all_metadata(response, None)
            
            metadata = {
                'prompt_tokens': usage.prompt_tokens,
                'completion_tokens': usage.completion_tokens,
                'model_id': model_id,
                'latency_ms': int(latency * 1000),
                'response_id': response.id if hasattr(response, 'id') else None,
                'created': response.created if hasattr(response, 'created') else None,
                'object': response.object if hasattr(response, 'object') else None,
                'system_fingerprint': getattr(response, 'system_fingerprint', None),
            }
            
            # Store all identifiers in metadata
            if all_identifiers:
                metadata['identifiers'] = all_identifiers
            
            # Merge additional metadata
            if all_metadata:
                metadata.update({k: v for k, v in all_metadata.items() if k not in metadata})
            
            return CompletionResponse(
                content=completion.message.content,
                model=model,
                platform='openai',
                tokens_used=usage.total_tokens,
                cost=cost,
                finish_reason=completion.finish_reason,
                metadata=metadata
            )
            
        except openai.APIError as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise OpenAIError(f"OpenAI API error: {str(e)}")
        except openai.RateLimitError as e:
            self.logger.error(f"OpenAI rate limit exceeded: {str(e)}")
            raise OpenAIError(f"Rate limit exceeded: {str(e)}")
        except Exception as e:
            self.logger.error(f"OpenAI completion failed: {str(e)}")
            raise OpenAIError(f"Completion failed: {str(e)}")
    
    async def generate_streaming_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Generate streaming completion using OpenAI.
        
        Args:
            request: Standardized completion request
            model: Optional model override
            
        Yields:
            String chunks as they are generated
            
        Raises:
            OpenAIError: On API errors
        """
        model = model or self.default_model
        model_id = self.MODELS.get(model, model)
        
        # Validate request
        self.validate_request(request, model)
        
        # Build messages
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        # Build API params
        params = {
            "model": model_id,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": True,
        }
        
        # Add optional params
        if request.top_p is not None:
            params["top_p"] = request.top_p
        
        try:
            stream = await self.client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"OpenAI streaming failed: {str(e)}")
            raise OpenAIError(f"Streaming failed: {str(e)}")
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost based on OpenAI pricing."""
        return self.pricing.calculate(model, input_tokens, output_tokens)
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check OpenAI API health.
        
        Returns:
            Health status dictionary
        """
        try:
            start_time = time.time()
            
            # Simple test request to list models
            await self.client.models.list()
            
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                'status': 'healthy',
                'latency_ms': int(latency),
                'available': True,
                'platform': 'openai',
            }
        except Exception as e:
            self.logger.error(f"OpenAI health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'available': False,
                'platform': 'openai',
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models."""
        return list(self.MODELS.keys())
    
    def validate_request(self, request: CompletionRequest, model: str) -> None:
        """
        Validate OpenAI request parameters.
        
        Args:
            request: Request to validate
            model: Model to validate against
            
        Raises:
            ValidationError: If validation fails
        """
        model_id = self.MODELS.get(model, model)
        params = {
            'temperature': request.temperature,
            'max_tokens': request.max_tokens,
            'top_p': request.top_p,
            'frequency_penalty': request.frequency_penalty,
            'presence_penalty': request.presence_penalty,
        }
        self.validator.validate(model_id, params)
