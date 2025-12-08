"""
Token estimation utilities for AI responses.
"""
import re
from typing import Dict, Any


def estimate_tokens(text: str, model: str = 'gpt-4') -> int:
    """
    Estimate token count for text.
    
    Uses a simple heuristic: ~4 characters per token for English text.
    More accurate for GPT models, approximate for others.
    
    Args:
        text: Text to estimate tokens for
        model: Model name (for model-specific estimation)
    
    Returns:
        Estimated token count
    """
    if not text:
        return 0
    
    # Basic estimation: ~4 characters per token for English
    # This is a rough estimate, actual tokenization varies by model
    char_count = len(text)
    estimated_tokens = char_count // 4
    
    # Adjust for code (more tokens per character)
    if _is_code(text):
        estimated_tokens = int(estimated_tokens * 1.2)
    
    # Minimum token count
    return max(estimated_tokens, len(text.split()))


def _is_code(text: str) -> bool:
    """Check if text appears to be code."""
    code_indicators = [
        r'def\s+\w+\s*\(',  # Python function
        r'function\s+\w+\s*\(',  # JavaScript function
        r'class\s+\w+',  # Class definition
        r'import\s+',  # Import statement
        r'const\s+\w+\s*=',  # Const declaration
        r'let\s+\w+\s*=',  # Let declaration
        r'var\s+\w+\s*=',  # Var declaration
        r'<\w+',  # HTML/XML tags
        r'SELECT\s+.*\s+FROM',  # SQL
    ]
    
    for pattern in code_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str,
    platform: str = 'openai'
) -> float:
    """
    Estimate cost based on token usage and model.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name
        platform: Platform name (openai, anthropic, google)
    
    Returns:
        Estimated cost in USD
    """
    # Import pricing utilities
    try:
        from apps.integrations.utils.pricing import (
            OpenAIPricing, AnthropicPricing, GeminiPricing
        )
        
        if platform == 'openai':
            pricing = OpenAIPricing()
        elif platform == 'anthropic':
            pricing = AnthropicPricing()
        elif platform == 'google':
            pricing = GeminiPricing()
        else:
            # Default to OpenAI pricing
            pricing = OpenAIPricing()
        
        return pricing.calculate(model, input_tokens, output_tokens)
    except Exception:
        # Fallback: rough estimate $0.00001 per token
        return (input_tokens + output_tokens) * 0.00001

