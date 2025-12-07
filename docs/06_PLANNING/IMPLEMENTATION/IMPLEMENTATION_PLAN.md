---
title: "Phase 3: AI Platform Integration Layer - Implementation Plan"
description: "Build a unified AI platform integration layer that provides seamless access to multiple AI platforms (OpenAI, Anthropic Claude, Google Gemini) with automatic fallback, cost tracking, rate limiting, an"

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Project Manager
    - CTO / Technical Lead
  secondary:
    - All

applicable_phases:
  primary:
    - Development

tags:
  - core
  - implementation

status: "active"
priority: "medium"
difficulty: "intermediate"
completeness: "100%"
quality_status: "draft"

estimated_read_time: "10 minutes"

version: "1.0"
last_updated: "2025-12-06"
last_reviewed: "2025-12-06"
review_frequency: "quarterly"

author: "Development Team"
maintainer: "Development Team"

related: []
see_also: []
depends_on: []
prerequisite_for: []

aliases: []

changelog:
  - version: "1.0"
    date: "2025-12-06"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---

# Phase 3: AI Platform Integration Layer - Implementation Plan

## Overview

Build a unified AI platform integration layer that provides seamless access to multiple AI platforms (OpenAI, Anthropic Claude, Google Gemini) with automatic fallback, cost tracking, rate limiting, and comprehensive error handling.

---

## Goals

1. Create abstract adapter interface for AI platforms
2. Implement OpenAI adapter with GPT-4, GPT-3.5 support
3. Implement Anthropic Claude adapter
4. Implement Google Gemini adapter  
5. Add intelligent fallback mechanism
6. Implement rate limiting per platform
7. Create cost tracking and monitoring
8. Add retry logic with exponential backoff
9. Implement platform health checks
10. Create comprehensive error handling

---

## Architecture Design

### Base Adapter Interface

```
AIAdapter (Abstract Base Class)
├── initialize()
├── generate_completion()
├── generate_streaming_completion()
├── calculate_cost()
├── check_health()
├── get_available_models()
└── validate_request()

Concrete Implementations:
├── OpenAIAdapter
├── AnthropicAdapter
└── GeminiAdapter

Supporting Services:
├── AdapterRegistry (manages available adapters)
├── FallbackHandler (handles platform failures)
├── CostTracker (tracks usage and costs)
└── RateLimiter (enforces rate limits)
```

---

## File Structure

```
backend/
├── apps/
│   └── integrations/
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── base.py              # Abstract base adapter ✅ NEW
│       │   ├── openai_adapter.py    # OpenAI implementation ✅ NEW
│       │   ├── anthropic_adapter.py # Claude implementation ✅ NEW
│       │   └── gemini_adapter.py    # Gemini implementation ✅ NEW
│       ├── services/
│       │   ├── __init__.py
│       │   ├── adapter_registry.py  # Adapter management ✅ NEW
│       │   ├── fallback_handler.py  # Fallback logic ✅ NEW
│       │   ├── cost_tracker.py      # Cost tracking ✅ NEW
│       │   └── rate_limiter.py      # Rate limiting ✅ NEW
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── pricing.py           # Platform pricing data ✅ NEW
│       │   ├── validators.py        # Request validators ✅ NEW
│       │   └── exceptions.py        # Custom exceptions ✅ NEW
│       └── tests/
│           ├── test_adapters.py     # Adapter tests ✅ NEW
│           ├── test_fallback.py     # Fallback tests ✅ NEW
│           └── test_cost_tracking.py # Cost tests ✅ NEW
```

---

## Proposed Changes

### 1. Abstract Base Adapter

**File**: `backend/apps/integrations/adapters/base.py` [NEW]

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass


@dataclass
class CompletionRequest:
    """Standardized completion request."""
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: Optional[str] = None
    stop_sequences: Optional[List[str]] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None


@dataclass
class CompletionResponse:
    """Standardized completion response."""
    content: str
    model: str
    platform: str
    tokens_used: int
    cost: float
    metadata: Dict[str, Any]
    finish_reason: str


class BaseAIAdapter(ABC):
    """Abstract base class for AI platform adapters."""
    
    def __init__(self, platform_config: 'AIPlatform'):
        self.platform_config = platform_config
        self.platform_name = platform_config.platform_name
        self.api_key = platform_config.api_key
        self.max_retries = 3
        self.retry_delay = 1.0
    
    @abstractmethod
    async def generate_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> CompletionResponse:
        """Generate a completion."""
        pass
    
    @abstractmethod
    async def generate_streaming_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Generate a streaming completion."""
        pass
    
    @abstractmethod
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for token usage."""
        pass
    
    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Check platform health status."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass
    
    @abstractmethod
    def validate_request(self, request: CompletionRequest) -> bool:
        """Validate request parameters."""
        pass
```

---

### 2. OpenAI Adapter

**File**: `backend/apps/integrations/adapters/openai_adapter.py` [NEW]

```python
import openai
from typing import Optional, AsyncIterator, Dict, List, Any
from .base import BaseAIAdapter, CompletionRequest, CompletionResponse
from ..utils.pricing import OpenAIPricing
import asyncio


class OpenAIAdapter(BaseAIAdapter):
    """OpenAI platform adapter."""
    
    MODELS = {
        'gpt-4-turbo': 'gpt-4-1106-preview',
        'gpt-4': 'gpt-4',
        'gpt-3.5-turbo': 'gpt-3.5-turbo',
    }
    
    def __init__(self, platform_config):
        super().__init__(platform_config)
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        self.pricing = OpenAIPricing()
    
    async def generate_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> CompletionResponse:
        """Generate completion using OpenAI."""
        
        model = model or self.platform_config.default_model
        
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                frequency_penalty=request.frequency_penalty,
                presence_penalty=request.presence_penalty,
                stop=request.stop_sequences
            )
            
            completion = response.choices[0]
            usage = response.usage
            
            cost = self.calculate_cost(
                model,
                usage.prompt_tokens,
                usage.completion_tokens
            )
            
            return CompletionResponse(
                content=completion.message.content,
                model=model,
                platform='openai',
                tokens_used=usage.total_tokens,
                cost=cost,
                metadata={
                    'prompt_tokens': usage.prompt_tokens,
                    'completion_tokens': usage.completion_tokens,
                    'finish_reason': completion.finish_reason
                },
                finish_reason=completion.finish_reason
            )
            
        except Exception as e:
            # Log error and re-raise
            raise OpenAIError(f"OpenAI completion failed: {str(e)}")
    
    async def generate_streaming_completion(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Generate streaming completion."""
        
        model = model or self.platform_config.default_model
        
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise OpenAIError(f"OpenAI streaming failed: {str(e)}")
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost based on OpenAI pricing."""
        return self.pricing.calculate(model, input_tokens, output_tokens)
    
    async def check_health(self) -> Dict[str, Any]:
        """Check OpenAI health."""
        try:
            # Simple test request
            await self.client.models.list()
            return {
                'status': 'healthy',
                'latency_ms': 0,  # Measure actual latency
                'available': True
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'available': False
            }
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models."""
        return list(self.MODELS.keys())
    
    def validate_request(self, request: CompletionRequest) -> bool:
        """Validate OpenAI request parameters."""
        if request.max_tokens > 4000:  # Adjust per model
            raise ValidationError("max_tokens exceeds model limit")
        if request.temperature < 0 or request.temperature > 2:
            raise ValidationError("temperature must be between 0 and 2")
        return True
```

---

### 3. Pricing Data

**File**: `backend/apps/integrations/utils/pricing.py` [NEW]

```python
class OpenAIPricing:
    """OpenAI pricing per 1M tokens."""
    
    PRICES = {
        'gpt-4-1106-preview': {'input': 0.01, 'output': 0.03},
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
    }
    
    def calculate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD."""
        prices = self.PRICES.get(model, self.PRICES['gpt-3.5-turbo'])
        input_cost = (input_tokens / 1_000_000) * prices['input']
        output_cost = (output_tokens / 1_000_000) * prices['output']
        return round(input_cost + output_cost, 6)


class AnthropicPricing:
    """Anthropic Claude pricing."""
    
    PRICES = {
        'claude-3-opus': {'input': 0.015, 'output': 0.075},
        'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
        'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
    }
    
    def calculate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        prices = self.PRICES.get(model, self.PRICES['claude-3-sonnet'])
        input_cost = (input_tokens / 1_000_000) * prices['input']
        output_cost = (output_tokens / 1_000_000) * prices['output']
        return round(input_cost + output_cost, 6)


class GeminiPricing:
    """Google Gemini pricing."""
    
    PRICES = {
        'gemini-pro': {'input': 0.00025, 'output': 0.0005},
        'gemini-pro-vision': {'input': 0.00025, 'output': 0.0005},
    }
    
    def calculate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        prices = self.PRICES.get(model, self.PRICES['gemini-pro'])
        input_cost = (input_tokens / 1_000_000) * prices['input']
        output_cost = (output_tokens / 1_000_000) * prices['output']
        return round(input_cost + output_cost, 6)
```

---

### 4. Adapter Registry

**File**: `backend/apps/integrations/services/adapter_registry.py` [NEW]

```python
from typing import Dict, Optional
from apps.integrations.models import AIPlatform
from ..adapters.base import BaseAIAdapter
from ..adapters.openai_adapter import OpenAIAdapter
from ..adapters.anthropic_adapter import AnthropicAdapter
from ..adapters.gemini_adapter import GeminiAdapter


class AdapterRegistry:
    """Registry for managing AI platform adapters."""
    
    ADAPTER_CLASSES = {
        'openai': OpenAIAdapter,
        'anthropic': AnthropicAdapter,
        'gemini': GeminiAdapter,
    }
    
    def __init__(self):
        self._adapters: Dict[str, BaseAIAdapter] = {}
    
    async def initialize(self):
        """Initialize all enabled platform adapters."""
        platforms = await AIPlatform.objects.filter(is_enabled=True).all()
        
        for platform in platforms:
            adapter_class = self.ADAPTER_CLASSES.get(platform.platform_name)
            if adapter_class:
                self._adapters[platform.platform_name] = adapter_class(platform)
    
    def get_adapter(self, platform_name: str) -> Optional[BaseAIAdapter]:
        """Get adapter by platform name."""
        return self._adapters.get(platform_name)
    
    def get_all_adapters(self) -> Dict[str, BaseAIAdapter]:
        """Get all registered adapters."""
        return self._adapters.copy()
    
    async def refresh(self):
        """Refresh adapter registry."""
        self._adapters.clear()
        await self.initialize()


# Global registry instance
registry = AdapterRegistry()
```

---

### 5. Fallback Handler

**File**: `backend/apps/integrations/services/fallback_handler.py` [NEW]

```python
from typing import List, Optional
from .adapter_registry import registry
from ..adapters.base import CompletionRequest, CompletionResponse
import logging

logger = logging.getLogger(__name__)


class FallbackHandler:
    """Handles platform fallback on failures."""
    
    def __init__(self, preferred_platforms: List[str]):
        self.preferred_platforms = preferred_platforms
    
    async def generate_with_fallback(
        self,
        request: CompletionRequest,
        model: Optional[str] = None
    ) -> CompletionResponse:
        """
        Try to generate completion with fallback.
        Attempts platforms in preferred order.
        """
        
        last_error = None
        
        for platform_name in self.preferred_platforms:
            adapter = registry.get_adapter(platform_name)
            
            if not adapter:
                logger.warning(f"Adapter not found for platform: {platform_name}")
                continue
            
            try:
                logger.info(f"Attempting completion with {platform_name}")
                response = await adapter.generate_completion(request, model)
                
                # Log successful platform usage
                logger.info(f"Successfully generated completion with {platform_name}")
                return response
                
            except Exception as e:
                logger.error(f"Failed with {platform_name}: {str(e)}")
                last_error = e
                continue
        
        # All platforms failed
        raise PlatformUnavailableError(
            f"All platforms failed. Last error: {str(last_error)}"
        )
```

---

## User Review Required

> [!IMPORTANT]
> **Design Decisions to Confirm**
> 
> 1. **Async/Await Pattern**: All adapter methods are async for better performance
> 2. **Standardized Interface**: All platforms return the same `CompletionResponse` format
> 3. **Cost Tracking**: Automatic cost calculation on every request
> 4. **Fallback Order**: Configurable per agent or workflow

> [!WARNING]
> **Implementation Considerations**
> 
> 1. **API Keys**: Must be stored securely (already using write_only in serializers)
> 2. **Rate Limits**: Need to implement token bucket or sliding window algorithm
> 3. **Testing**: Will use mock responses for unit tests (no actual API calls)
> 4. **Async Django**: Need to ensure Django async support is properly configured

---

## Verification Plan

### Automated Tests
```bash
# Unit tests for each adapter
python manage.py test apps.integrations.tests.test_adapters

# Fallback mechanism tests
python manage.py test apps.integrations.tests.test_fallback

# Cost tracking accuracy
python manage.py test apps.integrations.tests.test_cost_tracking
```

### Manual Testing
1. Create test agent with OpenAI adapter
2. Execute test completion and verify response
3. Disable OpenAI, verify fallback to Anthropic
4. Check cost tracking in database
5. Verify rate limiting works
6. Test health check endpoints

---

## Next Steps After Approval

1. Create base adapter interface
2. Implement OpenAI adapter (priority 1)
3. Implement Anthropic adapter
4. Implement Gemini adapter
5. Create adapter registry
6. Implement fallback handler
7. Add cost tracking service
8. Add rate limiting
9. Write comprehensive tests
10. Update documentation

---

## Estimated Effort

- Base Infrastructure: 2-3 hours
- OpenAI Adapter: 2 hours
- Anthropic Adapter: 2 hours  
- Gemini Adapter: 2 hours
- Supporting Services: 3-4 hours
- Testing & Documentation: 2-3 hours

**Total: ~13-16 hours of development**

---

## Files to Create

- [ ] `adapters/base.py` - Abstract base adapter
- [ ] `adapters/openai_adapter.py` - OpenAI implementation
- [ ] `adapters/anthropic_adapter.py` - Claude implementation
- [ ] `adapters/gemini_adapter.py` - Gemini implementation
- [ ] `services/adapter_registry.py` - Adapter management
- [ ] `services/fallback_handler.py` - Fallback logic
- [ ] `services/cost_tracker.py` - Cost tracking
- [ ] `services/rate_limiter.py` - Rate limiting
- [ ] `utils/pricing.py` - Pricing data
- [ ] `utils/validators.py` - Request validators
- [ ] `utils/exceptions.py` - Custom exceptions
- [ ] `tests/test_adapters.py` - Tests

**Total: 12 new files**
