"""
Utility functions for HishamOS.
"""

import hashlib
import secrets
from typing import Any, Dict
from datetime import datetime
import json


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(48)


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def calculate_cost(tokens: int, model: str) -> float:
    """
    Calculate the cost based on tokens and model.
    
    Args:
        tokens: Number of tokens used
        model: Model name
        
    Returns:
        Cost in USD
    """
    # Pricing per 1K tokens (as of 2024)
    pricing = {
        'gpt-4-turbo': 0.01,
        'gpt-4': 0.03,
        'gpt-3.5-turbo': 0.0015,
        'claude-3-opus': 0.015,
        'claude-3-sonnet': 0.003,
        'claude-3-haiku': 0.00025,
        'gemini-pro': 0.00025,
        'gemini-ultra': 0.01,
    }
    
    cost_per_1k = pricing.get(model, 0.01)  # Default fallback
    return (tokens / 1000) * cost_per_1k


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    # Truncate to max length
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO 8601 string."""
    return dt.isoformat() if dt else None


def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safely load JSON with a default value on error."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result
