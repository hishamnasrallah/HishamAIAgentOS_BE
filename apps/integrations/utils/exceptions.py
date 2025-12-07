"""Custom exceptions for AI platform integrations."""


class AIAdapterError(Exception):
    """Base exception for AI adapter errors."""
    pass


class PlatformUnavailableError(AIAdapterError):
    """Raised when all platforms are unavailable."""
    pass


class ValidationError(AIAdapterError):
    """Raised when request validation fails."""
    pass


class OpenAIError(AIAdapterError):
    """OpenAI-specific error."""
    pass


class AnthropicError(AIAdapterError):
    """Anthropic-specific error."""
    pass


class GeminiError(AIAdapterError):
    """Gemini-specific error."""
    pass


class RateLimitError(AIAdapterError):
    """Raised when rate limit is exceeded."""
    pass


class CostLimitError(AIAdapterError):
    """Raised when cost limit is exceeded."""
    pass


class TokenLimitError(AIAdapterError):
    """Raised when token limit is exceeded."""
    pass
