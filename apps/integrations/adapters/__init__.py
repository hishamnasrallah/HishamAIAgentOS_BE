"""Adapters package for AI platform integrations."""

from .base import BaseAIAdapter, CompletionRequest, CompletionResponse

__all__ = [
    'BaseAIAdapter',
    'CompletionRequest',
    'CompletionResponse',
]
