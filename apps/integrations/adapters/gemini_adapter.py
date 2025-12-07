"""
Google Gemini platform adapter implementation.

Provides integration with Google's Gemini API including Gemini Pro models
with support for both standard and streaming completions.
"""

import google.generativeai as genai
from typing import Optional, AsyncIterator, Dict, List, Any
import time
import asyncio

from .base import BaseAIAdapter, CompletionRequest, CompletionResponse
from ..utils.pricing import GeminiPricing
from ..utils.validators import GeminiValidator
from ..utils.exceptions import GeminiError, ValidationError


class GeminiAdapter(BaseAIAdapter):
    """Google Gemini platform adapter."""
    
    # Model mapping
    MODELS = {
        'gemini-pro': 'gemini-pro',
        'gemini-pro-vision': 'gemini-pro-vision',
        'gemini-1.5-pro': 'gemini-1.5-pro',
    }
    
    def __init__(self, platform_config):
        """Initialize Gemini adapter."""
        super().__init__(platform_config)
        genai.configure(api_key=self.api_key)
        self.pricing = GeminiPricing()
        self.validator = GeminiValidator()
        self.logger.info(f"Gemini adapter initialized with model: {self.default_model}")
    
    async def generate_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> CompletionResponse:
        """Generate completion using Google Gemini."""
        model = model or self.default_model
        model_id = self.MODELS.get(model, model)
        
        # Validate request
        self.validate_request(request, model)
        
        # Build prompt
        full_prompt = request.prompt
        if request.system_prompt:
            full_prompt = f"{request.system_prompt}\n\n{request.prompt}"
        
        # Configure generation
        generation_config = genai.GenerationConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
        )
        
        if request.top_p is not None:
            generation_config.top_p = request.top_p
        if request.stop_sequences:
            generation_config.stop_sequences = request.stop_sequences
        
        try:
            start_time = time.time()
            
            # Create model and generate
            gemini_model = genai.GenerativeModel(model_id)
            
            # Run in thread pool since Gemini SDK is synchronous
            response = await asyncio.to_thread(
                gemini_model.generate_content,
                full_prompt,
                generation_config=generation_config
            )
            
            latency = time.time() - start_time
            
            # Extract content
            content = response.text
            
            # Estimate token count (Gemini doesn't always provide exact counts)
            # Using rough estimate: 1 token ≈ 4 characters
            estimated_input_tokens = len(full_prompt) // 4
            estimated_output_tokens = len(content) // 4
            total_tokens = estimated_input_tokens + estimated_output_tokens
            
            # Calculate cost
            cost = self.calculate_cost(
                model_id,
                estimated_input_tokens,
                estimated_output_tokens
            )
            
            self.logger.info(
                f"Gemini completion: ~{total_tokens} tokens, "
                f"${cost:.6f}, {latency:.2f}s"
            )
            
            return CompletionResponse(
                content=content,
                model=model,
                platform='gemini',
                tokens_used=total_tokens,
                cost=cost,
                finish_reason='stop',
                metadata={
                    'input_tokens_estimated': estimated_input_tokens,
                    'output_tokens_estimated': estimated_output_tokens,
                    'model_id': model_id,
                    'latency_ms': int(latency * 1000),
                }
            )
            
        except Exception as e:
            self.logger.error(f"Gemini completion failed: {str(e)}")
            raise GeminiError(f"Completion failed: {str(e)}")
    
    async def generate_streaming_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Generate streaming completion using Gemini."""
        model = model or self.default_model
        model_id = self.MODELS.get(model, model)
        
        # Validate request
        self.validate_request(request, model)
        
        # Build prompt
        full_prompt = request.prompt
        if request.system_prompt:
            full_prompt = f"{request.system_prompt}\n\n{request.prompt}"
        
        # Configure generation
        generation_config = genai.GenerationConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
        )
        
        try:
            gemini_model = genai.GenerativeModel(model_id)
            
            # Run in thread pool
            response = await asyncio.to_thread(
                gemini_model.generate_content,
                full_prompt,
                generation_config=generation_config,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            self.logger.error(f"Gemini streaming failed: {str(e)}")
            raise GeminiError(f"Streaming failed: {str(e)}")
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost based on Gemini pricing."""
        return self.pricing.calculate(model, input_tokens, output_tokens)
    
    async def check_health(self) -> Dict[str, Any]:
        """Check Gemini API health."""
        try:
            start_time = time.time()
            
            # Simple test request
            gemini_model = genai.GenerativeModel(self.MODELS['gemini-pro'])
            await asyncio.to_thread(
                gemini_model.generate_content,
                "Hi"
            )
            
            latency = (time.time() - start_time) * 1000
            
            return {
                'status': 'healthy',
                'latency_ms': int(latency),
                'available': True,
                'platform': 'gemini',
            }
        except Exception as e:
            self.logger.error(f"Gemini health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'available': False,
                'platform': 'gemini',
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available Gemini models."""
        return list(self.MODELS.keys())
    
    def validate_request(self, request: CompletionRequest, model: str) -> None:
        """Validate Gemini request parameters."""
        model_id = self.MODELS.get(model, model)
        params = {
            'temperature': request.temperature,
            'max_tokens': request.max_tokens,
            'top_p': request.top_p,
        }
        self.validator.validate(model_id, params)
