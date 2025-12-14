"""
OpenRouter platform adapter implementation.

Provides integration with OpenRouter's API which offers access to multiple AI models
through an OpenAI-compatible interface. Supports models like Mistral 7B Instruct (free).

OpenRouter API Documentation: https://openrouter.ai/docs
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


class OpenRouterAdapter(BaseAIAdapter):
    """OpenRouter platform adapter with OpenAI-compatible API."""
    
    # Model mapping: friendly name -> OpenRouter model ID
    MODELS = {
        'mistral-7b-instruct-free': 'mistralai/mistral-7b-instruct:free',
        'mistral-7b-instruct': 'mistralai/mistral-7b-instruct:free',
    }
    
    def __init__(self, platform_config):
        """Initialize OpenRouter adapter."""
        super().__init__(platform_config)
        
        # OpenRouter uses OpenAI-compatible API with custom base URL
        base_url = platform_config.api_url or "https://openrouter.ai/api/v1"
        
        # Create a custom httpx client without proxies to avoid compatibility issues
        # This works around the issue where OpenAI library tries to pass 'proxies' to httpx.AsyncClient
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        # Initialize OpenAI client with OpenRouter base URL and custom http_client
        # Set max_retries=0 to handle retries ourselves (especially for rate limit errors)
        # This prevents automatic retries that could cause duplicate requests
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=base_url,
            http_client=http_client,
            max_retries=0  # Disable automatic retries - we handle errors explicitly
        )
        
        # Use OpenAI pricing as reference (OpenRouter pricing varies by model)
        self.pricing = OpenAIPricing()
        self.validator = OpenAIValidator()
        self.logger.info(f"OpenRouter adapter initialized with base_url: {base_url}, model: {self.default_model}")
    
    async def generate_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> CompletionResponse:
        """
        Generate completion using OpenRouter.
        
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
        
        # Build messages - use messages array if provided (for conversation history), otherwise use prompt
        if request.messages:
            # Use provided messages array (includes conversation history)
            messages = request.messages.copy()
            # Add system prompt at the beginning if provided
            if request.system_prompt:
                messages.insert(0, {"role": "system", "content": request.system_prompt})
        else:
            # Fallback to single user message (legacy behavior)
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
        
        # OpenRouter-specific headers (optional but recommended)
        extra_headers = {}
        if hasattr(self.platform_config, 'organization_id') and self.platform_config.organization_id:
            # Use organization_id as HTTP-Referer if provided
            extra_headers["HTTP-Referer"] = self.platform_config.organization_id
        if hasattr(self.platform_config, 'display_name'):
            extra_headers["X-Title"] = self.platform_config.display_name
        
        try:
            start_time = time.time()
            
        # NOTE: OpenRouter API doesn't support conversationId parameter (it's stateless)
        # We don't send conversationId in params - it would cause an error
        # Conversation history must be included in the messages array
            
            # Make API call with retry
            # OpenRouter uses OpenAI-compatible API, so we can use the same client
            response = await self._retry_with_backoff(
                self.client.chat.completions.create,
                extra_headers=extra_headers if extra_headers else None,
                **params
            )
            
            # Log if conversationId was provided (for debugging)
            if request.conversation_id:
                self.logger.debug(f"Request included conversation_id: {request.conversation_id} (may not be supported by OpenRouter)")
            
            latency = time.time() - start_time
            
            # Extract response data
            completion = response.choices[0]
            usage = response.usage
            
            # Calculate cost (OpenRouter pricing varies, using OpenAI as reference)
            # For free models like mistral-7b-instruct:free, cost is 0
            cost = 0.0
            if not model_id.endswith(':free'):
                # For paid models, calculate approximate cost
                cost = self.calculate_cost(
                    model_id,
                    usage.prompt_tokens if usage else 0,
                    usage.completion_tokens if usage else 0
                )
            
            self.logger.info(
                f"OpenRouter completion: {usage.total_tokens if usage else 0} tokens, "
                f"${cost:.6f}, {latency:.2f}s, model: {model_id}"
            )
            
            # Extract ALL identifiers and metadata from response
            all_identifiers = self.extract_all_identifiers(completion, None)
            all_metadata = self.extract_all_metadata(completion, None)
            
            metadata = {
                'prompt_tokens': usage.prompt_tokens if usage else 0,
                'completion_tokens': usage.completion_tokens if usage else 0,
                'model_id': model_id,
                'latency_ms': int(latency * 1000),
                'provider': 'openrouter',
                'response_id': response.id if hasattr(response, 'id') else None,
                'created': response.created if hasattr(response, 'created') else None,
                'model': response.model if hasattr(response, 'model') else model_id,
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
                platform='openrouter',
                tokens_used=usage.total_tokens if usage else 0,
                cost=cost,
                finish_reason=completion.finish_reason,
                metadata=metadata
            )
            
        except openai.RateLimitError as e:
            # Extract detailed error information
            error_code = 429
            error_message = None
            
            # First try to extract from e.body (parsed JSON response)
            if hasattr(e, 'body') and isinstance(e.body, dict):
                error_body = e.body
                if 'error' in error_body:
                    error_info = error_body['error']
                    if isinstance(error_info, dict):
                        if 'message' in error_info:
                            error_message = error_info['message']
                        if 'code' in error_info:
                            error_code = error_info['code']
            
            # Fallback: try to extract from response
            if not error_message and hasattr(e, 'response') and e.response:
                try:
                    if hasattr(e.response, 'json'):
                        error_body = e.response.json()
                    elif hasattr(e.response, 'text'):
                        import json
                        error_body = json.loads(e.response.text)
                    else:
                        error_body = {}
                    
                    if 'error' in error_body:
                        error_info = error_body['error']
                        if isinstance(error_info, dict):
                            if 'message' in error_info:
                                error_message = error_info['message']
                            if 'code' in error_info:
                                error_code = error_info['code']
                except Exception:
                    pass
            
            # Final fallback: parse from str(e) which includes JSON
            if not error_message:
                error_str = str(e)
                # Try to extract message from "Error code: 429 - {...}" format
                if "Error code:" in error_str and "- {" in error_str:
                    try:
                        import json
                        json_start = error_str.find("{")
                        if json_start > 0:
                            json_str = error_str[json_start:]
                            error_body = json.loads(json_str)
                            if 'error' in error_body and isinstance(error_body['error'], dict):
                                error_message = error_body['error'].get('message', error_str)
                    except Exception:
                        pass
                
                if not error_message:
                    error_message = error_str
            
            # Clean up error message - remove duplicate "Rate limit exceeded:" prefix
            error_message = error_message.strip()
            error_message_lower = error_message.lower()
            
            # Check if message already starts with "Rate limit exceeded" to avoid duplication
            if error_message_lower.startswith('rate limit exceeded:'):
                # Already has prefix, use as-is but ensure it ends properly
                if not error_message.endswith('.'):
                    error_message = f"{error_message}."
                final_message = f"{error_message} Please wait a moment and try again, or add your own API key for higher limits."
            elif error_message_lower.startswith('rate limit exceeded'):
                # Has prefix without colon, add colon
                if not error_message.endswith('.'):
                    error_message = f"{error_message}."
                final_message = f"{error_message} Please wait a moment and try again, or add your own API key for higher limits."
            else:
                # No prefix, add it
                if not error_message.endswith('.'):
                    error_message = f"{error_message}."
                final_message = f"Rate limit exceeded: {error_message} Please wait a moment and try again, or add your own API key for higher limits."
            
            self.logger.error(
                f"OpenRouter rate limit exceeded: {error_message} (code: {error_code})",
                exc_info=True
            )
            raise OpenAIError(final_message)
        except openai.APIError as e:
            # Extract detailed error information
            error_code = getattr(e, 'code', None) or getattr(e, 'status_code', None) or 'unknown'
            error_message = getattr(e, 'message', None) or str(e)
            
            # Try to extract provider error details
            if hasattr(e, 'response') and e.response:
                try:
                    error_body = e.response.json() if hasattr(e.response, 'json') else {}
                    if 'error' in error_body:
                        error_info = error_body['error']
                        if isinstance(error_info, dict):
                            if 'message' in error_info:
                                error_message = error_info['message']
                            elif 'metadata' in error_info and isinstance(error_info['metadata'], dict):
                                if 'raw' in error_info['metadata']:
                                    error_message = error_info['metadata']['raw']
                except Exception:
                    pass
            
            self.logger.error(
                f"OpenRouter API error: Error code: {error_code} - {error_message}",
                exc_info=True
            )
            raise OpenAIError(f"OpenRouter API error: {error_message} (code: {error_code})")
        except Exception as e:
            self.logger.error(f"OpenRouter completion failed: {str(e)}", exc_info=True)
            raise OpenAIError(f"Completion failed: {str(e)}")
    
    async def generate_streaming_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Generate streaming completion using OpenRouter.
        
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
        
        # Build messages - use messages array if provided (for conversation history), otherwise use prompt
        if request.messages:
            # Use provided messages array (includes conversation history)
            messages = request.messages.copy()
            # Add system prompt at the beginning if provided
            if request.system_prompt:
                messages.insert(0, {"role": "system", "content": request.system_prompt})
        else:
            # Fallback to single user message (legacy behavior)
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
        
        # NOTE: OpenRouter API doesn't support conversationId parameter (it's stateless)
        # We don't send conversationId in params - it would cause an error
        # Conversation history must be included in the messages array
        
        # Add optional params
        if request.top_p is not None:
            params["top_p"] = request.top_p
        
        # OpenRouter-specific headers
        extra_headers = {}
        if hasattr(self.platform_config, 'organization_id') and self.platform_config.organization_id:
            extra_headers["HTTP-Referer"] = self.platform_config.organization_id
        if hasattr(self.platform_config, 'display_name'):
            extra_headers["X-Title"] = self.platform_config.display_name
        
        try:
            # Log request details to track potential duplicates
            request_id = id(params)  # Simple ID based on params hash
            self.logger.info(
                f"Starting OpenRouter streaming request [req_id={request_id}]: "
                f"model={model_id}, messages={len(messages)}, "
                f"max_tokens={params.get('max_tokens')}"
            )
            
            stream = await self.client.chat.completions.create(
                extra_headers=extra_headers if extra_headers else None,
                **params
            )
            
            self.logger.debug(f"OpenRouter streaming request [req_id={request_id}] - stream created successfully")
            
            self.logger.info("Stream object created, starting to read chunks...")
            chunk_count = 0
            empty_chunk_count = 0
            total_chars = 0
            
            async for chunk in stream:
                chunk_count += 1
                
                try:
                    # Check if chunk has choices and delta content
                    if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta and hasattr(delta, 'content') and delta.content:
                            total_chars += len(delta.content)
                            yield delta.content
                        else:
                            empty_chunk_count += 1
                    else:
                        empty_chunk_count += 1
                except Exception as e:
                    self.logger.warning(f"Error processing chunk {chunk_count}: {e}")
                    continue
            
            self.logger.info(f"OpenRouter stream completed: {chunk_count} total chunks ({chunk_count - empty_chunk_count} with content), {total_chars} total chars")
            if chunk_count == 0:
                self.logger.warning("Stream completed but no chunks were received")
            elif chunk_count == empty_chunk_count:
                self.logger.warning(f"Stream received {chunk_count} chunks but all were empty")
                    
        except openai.RateLimitError as e:
            # Extract detailed error information
            # OpenAI library's RateLimitError has error details in different places
            error_code = 429
            error_message = None
            
            # First try to extract from e.body (parsed JSON response)
            if hasattr(e, 'body') and isinstance(e.body, dict):
                error_body = e.body
                if 'error' in error_body:
                    error_info = error_body['error']
                    if isinstance(error_info, dict):
                        if 'message' in error_info:
                            error_message = error_info['message']
                        if 'code' in error_info:
                            error_code = error_info['code']
            
            # Fallback: try to extract from response
            if not error_message and hasattr(e, 'response') and e.response:
                try:
                    if hasattr(e.response, 'json'):
                        error_body = e.response.json()
                    elif hasattr(e.response, 'text'):
                        import json
                        error_body = json.loads(e.response.text)
                    else:
                        error_body = {}
                    
                    if 'error' in error_body:
                        error_info = error_body['error']
                        if isinstance(error_info, dict):
                            if 'message' in error_info:
                                error_message = error_info['message']
                            if 'code' in error_info:
                                error_code = error_info['code']
                except Exception:
                    pass
            
            # Final fallback: use str(e) but try to extract message from it
            if not error_message:
                error_str = str(e)
                # Try to extract message from "Error code: 429 - {...}" format
                if "Error code:" in error_str and "- {" in error_str:
                    try:
                        import json
                        # Extract JSON part
                        json_start = error_str.find("{")
                        if json_start > 0:
                            json_str = error_str[json_start:]
                            error_body = json.loads(json_str)
                            if 'error' in error_body and isinstance(error_body['error'], dict):
                                error_message = error_body['error'].get('message', error_str)
                    except Exception:
                        pass
                
                if not error_message:
                    error_message = error_str
            
            # Clean up error message - remove duplicate "Rate limit exceeded:" prefix
            error_message = error_message.strip()
            error_message_lower = error_message.lower()
            
            # Check if message already starts with "Rate limit exceeded" to avoid duplication
            if error_message_lower.startswith('rate limit exceeded:'):
                # Already has prefix, use as-is but ensure it ends properly
                if not error_message.endswith('.'):
                    error_message = f"{error_message}."
                final_message = f"{error_message} Please wait a moment and try again, or add your own API key for higher limits."
            elif error_message_lower.startswith('rate limit exceeded'):
                # Has prefix without colon, add colon
                if not error_message.endswith('.'):
                    error_message = f"{error_message}."
                final_message = f"{error_message} Please wait a moment and try again, or add your own API key for higher limits."
            else:
                # No prefix, add it
                if not error_message.endswith('.'):
                    error_message = f"{error_message}."
                final_message = f"Rate limit exceeded: {error_message} Please wait a moment and try again, or add your own API key for higher limits."
            
            self.logger.error(
                f"OpenRouter rate limit exceeded during streaming: {error_message} (code: {error_code})",
                exc_info=True
            )
            raise OpenAIError(final_message)
        except openai.APIError as e:
            # Extract detailed error information
            error_code = getattr(e, 'code', None) or getattr(e, 'status_code', None) or 'unknown'
            error_message = getattr(e, 'message', None) or str(e)
            
            # Try to extract provider error details
            if hasattr(e, 'response') and e.response:
                try:
                    error_body = e.response.json() if hasattr(e.response, 'json') else {}
                    if 'error' in error_body:
                        error_info = error_body['error']
                        if isinstance(error_info, dict):
                            if 'message' in error_info:
                                error_message = error_info['message']
                            elif 'metadata' in error_info and isinstance(error_info['metadata'], dict):
                                if 'raw' in error_info['metadata']:
                                    error_message = error_info['metadata']['raw']
                except Exception:
                    pass
            
            self.logger.error(
                f"OpenRouter API error during streaming: Error code: {error_code} - {error_message}",
                exc_info=True
            )
            raise OpenAIError(f"OpenRouter API error: {error_message} (code: {error_code})")
        except Exception as e:
            self.logger.error(f"OpenRouter streaming failed: {str(e)}", exc_info=True)
            raise OpenAIError(f"Streaming failed: {str(e)}")
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost based on OpenRouter pricing.
        
        Note: OpenRouter pricing varies by model. Free models return 0.
        For paid models, we use OpenAI pricing as a reference.
        """
        # Free models have no cost
        if model.endswith(':free') or 'free' in model.lower():
            return 0.0
        
        # For paid models, use OpenAI pricing as reference
        # In production, you might want to implement OpenRouter-specific pricing
        return self.pricing.calculate(model, input_tokens, output_tokens)
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check OpenRouter API health.
        
        Returns:
            Health status dictionary
        """
        try:
            start_time = time.time()
            
            # Simple test request - list models endpoint
            # OpenRouter might not have models.list(), so we'll do a minimal completion test
            test_response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                'status': 'healthy',
                'latency_ms': int(latency),
                'available': True,
                'platform': 'openrouter',
                'model': self.default_model,
            }
        except Exception as e:
            self.logger.error(f"OpenRouter health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'available': False,
                'platform': 'openrouter',
            }
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenRouter models."""
        return list(self.MODELS.keys())
    
    def validate_request(self, request: CompletionRequest, model: str) -> None:
        """
        Validate OpenRouter request parameters.
        
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
        # Use OpenAI validator since OpenRouter uses OpenAI-compatible API
        self.validator.validate(model_id, params)



