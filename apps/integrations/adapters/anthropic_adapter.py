"""
Anthropic Claude platform adapter implementation.

Provides integration with Anthropic's Claude API including Claude 3 models
(Opus, Sonnet, Haiku) with support for both standard and streaming completions.
"""

import anthropic
from typing import Optional, AsyncIterator, Dict, List, Any
import time

from .base import BaseAIAdapter, CompletionRequest, CompletionResponse
from ..utils.pricing import AnthropicPricing
from ..utils.validators import AnthropicValidator
from ..utils.exceptions import AnthropicError, ValidationError


class AnthropicAdapter(BaseAIAdapter):
    """Anthropic Claude platform adapter."""
    
    # Model mapping
    MODELS = {
        'claude-3-opus': 'claude-3-opus-20240229',
        'claude-3-sonnet': 'claude-3-sonnet-20240229',
        'claude-3-haiku': 'claude-3-haiku-20240307',
        'claude-2.1': 'claude-2.1',
        'claude-2': 'claude-2.0',
    }
    
    def __init__(self, platform_config):
        """Initialize Anthropic adapter."""
        super().__init__(platform_config)
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        self.pricing = AnthropicPricing()
        self.validator = AnthropicValidator()
        self.logger.info(f"Anthropic adapter initialized with model: {self.default_model}")
    
    async def generate_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> CompletionResponse:
        """Generate completion using Anthropic Claude."""
        model = model or self.default_model
        model_id = self.MODELS.get(model, model)
        
        # Validate request
        self.validate_request(request, model)
        
        # Build API params
        params = {
            "model": model_id,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        
        # Add system prompt if provided
        if request.system_prompt:
            params["system"] = request.system_prompt
        
        # Add optional params
        if request.top_p is not None:
            params["top_p"] = request.top_p
        if request.stop_sequences:
            params["stop_sequences"] = request.stop_sequences
        
        try:
            start_time = time.time()
            
            # Make API call with retry
            response = await self._retry_with_backoff(
                self.client.messages.create,
                **params
            )
            
            latency = time.time() - start_time
            
            # Extract response data
            content = response.content[0].text
            usage = response.usage
            
            # Calculate cost
            cost = self.calculate_cost(
                model_id,
                usage.input_tokens,
                usage.output_tokens
            )
            
            self.logger.info(
                f"Anthropic completion: {usage.input_tokens + usage.output_tokens} tokens, "
                f"${cost:.6f}, {latency:.2f}s"
            )
            
            # Extract ALL identifiers and metadata from response
            all_identifiers = self.extract_all_identifiers(response, None)
            all_metadata = self.extract_all_metadata(response, None)
            
            metadata = {
                'input_tokens': usage.input_tokens,
                'output_tokens': usage.output_tokens,
                'model_id': model_id,
                'latency_ms': int(latency * 1000),
                'stop_reason': response.stop_reason,
                'stop_sequence': getattr(response, 'stop_sequence', None),
                'response_id': response.id if hasattr(response, 'id') else None,
                'type': getattr(response, 'type', None),
                'role': getattr(response, 'role', None),
                'content_block_type': getattr(response.content[0], 'type', None) if response.content else None,
            }
            
            # Store all identifiers in metadata
            if all_identifiers:
                metadata['identifiers'] = all_identifiers
            
            # Merge additional metadata
            if all_metadata:
                metadata.update({k: v for k, v in all_metadata.items() if k not in metadata})
            
            return CompletionResponse(
                content=content,
                model=model,
                platform='anthropic',
                tokens_used=usage.input_tokens + usage.output_tokens,
                cost=cost,
                finish_reason=response.stop_reason,
                metadata=metadata
            )
            
        except anthropic.APIError as e:
            self.logger.error(f"Anthropic API error: {str(e)}")
            raise AnthropicError(f"Anthropic API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Anthropic completion failed: {str(e)}")
            raise AnthropicError(f"Completion failed: {str(e)}")
    
    async def generate_streaming_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Generate streaming completion using Anthropic."""
        model = model or self.default_model
        model_id = self.MODELS.get(model, model)
        
        # Validate request
        self.validate_request(request, model)
        
        # Build API params
        params = {
            "model": model_id,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        
        if request.system_prompt:
            params["system"] = request.system_prompt
        
        try:
            async with self.client.messages.stream(**params) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            self.logger.error(f"Anthropic streaming failed: {str(e)}")
            raise AnthropicError(f"Streaming failed: {str(e)}")
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost based on Anthropic pricing."""
        return self.pricing.calculate(model, input_tokens, output_tokens)
    
    async def check_health(self) -> Dict[str, Any]:
        """Check Anthropic API health."""
        try:
            start_time = time.time()
            
            # Simple test request
            await self.client.messages.create(
                model=self.MODELS['claude-3-haiku'],  # Use cheapest model
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            
            latency = (time.time() - start_time) * 1000
            
            return {
                'status': 'healthy',
                'latency_ms': int(latency),
                'available': True,
                'platform': 'anthropic',
            }
        except Exception as e:
            self.logger.error(f"Anthropic health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'available': False,
                'platform': 'anthropic',
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available Anthropic models."""
        return list(self.MODELS.keys())
    
    def validate_request(self, request: CompletionRequest, model: str) -> None:
        """Validate Anthropic request parameters."""
        model_id = self.MODELS.get(model, model)
        params = {
            'temperature': request.temperature,
            'max_tokens': request.max_tokens,
            'top_p': request.top_p,
        }
        self.validator.validate(model_id, params)
