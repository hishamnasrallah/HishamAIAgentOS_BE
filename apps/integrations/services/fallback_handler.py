"""
Fallback handler for AI platform failures.

Provides intelligent fallback mechanism to try alternative platforms
when the primary platform fails or is unavailable.
"""

from typing import List, Optional
import logging

from .adapter_registry import registry
from ..adapters.base import CompletionRequest, CompletionResponse
from ..utils.exceptions import PlatformUnavailableError

logger = logging.getLogger(__name__)


class FallbackHandler:
    """Handles platform fallback on failures."""
    
    def __init__(self, preferred_platforms: Optional[List[str]] = None):
        """
        Initialize fallback handler.
        
        Args:
            preferred_platforms: Ordered list of platform names to try
                               If None, uses all available platforms
        """
        self.preferred_platforms = preferred_platforms or ['openai', 'anthropic', 'gemini']
    
    async def generate_with_fallback(
        self,
        request: CompletionRequest,
        model: Optional[str] = None,
        preferred_platform: Optional[str] = None
    ) -> CompletionResponse:
        """
        Try to generate completion with automatic fallback.
        
        Attempts platforms in preferred order. If a platform fails,
        automatically tries the next one in the list.
        
        Args:
            request: Standardized completion request
            model: Optional model override
            preferred_platform: Start with this platform first
            
        Returns:
            CompletionResponse from whichever platform succeeded
            
        Raises:
            PlatformUnavailableError: If all platforms fail
        """
        # Build platform list
        platforms_to_try = self.preferred_platforms.copy()
        
        # Move preferred platform to front if specified
        if preferred_platform and preferred_platform in platforms_to_try:
            platforms_to_try.remove(preferred_platform)
            platforms_to_try.insert(0, preferred_platform)
        
        last_error = None
        attempts = []
        
        for platform_name in platforms_to_try:
            adapter = registry.get_adapter(platform_name)
            
            if not adapter:
                logger.warning(f"Adapter not found for platform: {platform_name}")
                attempts.append({
                    'platform': platform_name,
                    'status': 'skipped',
                    'reason': 'adapter_not_found'
                })
                continue
            
            try:
                logger.info(f"Attempting completion with {platform_name}")
                
                response = await adapter.generate_completion(request, model)
                
                logger.info(
                    f"Successfully generated completion with {platform_name} "
                    f"({response.tokens_used} tokens, ${response.cost:.6f})"
                )
                
                attempts.append({
                    'platform': platform_name,
                    'status': 'success',
                    'tokens_used': response.tokens_used,
                    'cost': response.cost
                })
                
                # Add fallback info to metadata
                response.metadata['fallback_attempts'] = attempts
                response.metadata['primary_platform'] = platforms_to_try[0]
                
                return response
                
            except Exception as e:
                logger.error(f"Failed with {platform_name}: {str(e)}")
                last_error = e
                attempts.append({
                    'platform': platform_name,
                    'status': 'failed',
                    'error': str(e)
                })
                continue
        
        # All platforms failed
        error_msg = (
            f"All platforms failed after {len(attempts)} attempts. "
            f"Last error: {str(last_error)}"
        )
        logger.error(error_msg)
        raise PlatformUnavailableError(error_msg)
    
    def set_preferred_platforms(self, platforms: List[str]):
        """
        Update the preferred platforms list.
        
        Args:
            platforms: New ordered list of platform names
        """
        self.preferred_platforms = platforms
        logger.info(f"Updated preferred platforms: {platforms}")
