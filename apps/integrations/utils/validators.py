"""Request validators for AI platforms."""

from typing import Dict, Any, List, Optional
from .exceptions import ValidationError


class RequestValidator:
    """Base validator for AI requests."""
    
    @staticmethod
    def validate_temperature(temperature: float) -> None:
        """Validate temperature parameter."""
        if not 0.0 <= temperature <= 2.0:
            raise ValidationError(f"Temperature must be between 0.0 and 2.0, got {temperature}")
    
    @staticmethod
    def validate_max_tokens(max_tokens: int, model_limit: int) -> None:
        """Validate max_tokens against model limit."""
        if max_tokens < 1:
            raise ValidationError(f"max_tokens must be positive, got {max_tokens}")
        if max_tokens > model_limit:
            raise ValidationError(
                f"max_tokens {max_tokens} exceeds model limit of {model_limit}"
            )
    
    @staticmethod
    def validate_top_p(top_p: Optional[float]) -> None:
        """Validate top_p parameter."""
        if top_p is not None and not 0.0 <= top_p <= 1.0:
            raise ValidationError(f"top_p must be between 0.0 and 1.0, got {top_p}")
    
    @staticmethod
    def validate_frequency_penalty(penalty: Optional[float]) -> None:
        """Validate frequency_penalty parameter."""
        if penalty is not None and not -2.0 <= penalty <= 2.0:
            raise ValidationError(
                f"frequency_penalty must be between -2.0 and 2.0, got {penalty}"
            )
    
    @staticmethod
    def validate_presence_penalty(penalty: Optional[float]) -> None:
        """Validate presence_penalty parameter."""
        if penalty is not None and not -2.0 <= penalty <= 2.0:
            raise ValidationError(
                f"presence_penalty must be between -2.0 and 2.0, got {penalty}"
            )


class OpenAIValidator(RequestValidator):
    """Validator for OpenAI requests."""
    
    MODEL_LIMITS = {
        'gpt-4-turbo-preview': 128000,
        'gpt-4-1106-preview': 128000,
        'gpt-4': 8192,
        'gpt-3.5-turbo': 4096,
        'gpt-3.5-turbo-1106': 16385,
    }
    
    @classmethod
    def validate(cls, model: str, params: Dict[str, Any]) -> None:
        """Validate OpenAI request parameters."""
        cls.validate_temperature(params.get('temperature', 0.7))
        
        model_limit = cls.MODEL_LIMITS.get(model, 4096)
        cls.validate_max_tokens(params.get('max_tokens', 1000), model_limit)
        
        cls.validate_top_p(params.get('top_p'))
        cls.validate_frequency_penalty(params.get('frequency_penalty'))
        cls.validate_presence_penalty(params.get('presence_penalty'))


class AnthropicValidator(RequestValidator):
    """Validator for Anthropic requests."""
    
    MODEL_LIMITS = {
        'claude-3-opus-20240229': 200000,
        'claude-3-sonnet-20240229': 200000,
        'claude-3-haiku-20240307': 200000,
        'claude-2.1': 100000,
        'claude-2.0': 100000,
    }
    
    @classmethod
    def validate(cls, model: str, params: Dict[str, Any]) -> None:
        """Validate Anthropic request parameters."""
        cls.validate_temperature(params.get('temperature', 0.7))
        
        model_limit = cls.MODEL_LIMITS.get(model, 100000)
        cls.validate_max_tokens(params.get('max_tokens', 1000), model_limit)
        
        cls.validate_top_p(params.get('top_p'))


class GeminiValidator(RequestValidator):
    """Validator for Gemini requests."""
    
    MODEL_LIMITS = {
        'gemini-pro': 32760,
        'gemini-pro-vision': 16384,
        'gemini-1.5-pro': 1000000,  # 1M context window
    }
    
    @classmethod
    def validate(cls, model: str, params: Dict[str, Any]) -> None:
        """Validate Gemini request parameters."""
        cls.validate_temperature(params.get('temperature', 0.7))
        
        model_limit = cls.MODEL_LIMITS.get(model, 32760)
        cls.validate_max_tokens(params.get('max_tokens', 1000), model_limit)
        
        cls.validate_top_p(params.get('top_p'))
