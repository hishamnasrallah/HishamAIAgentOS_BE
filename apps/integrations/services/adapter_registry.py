"""
Adapter registry for managing AI platform adapters.

Provides centralized access to all platform adapters and handles
initialization and lifecycle management.
"""

from typing import Dict, Optional, List, Type
import logging

from apps.integrations.models import AIPlatform
from ..adapters.base import BaseAIAdapter

logger = logging.getLogger(__name__)


def _get_adapter_class(platform_name: str) -> Optional[Type[BaseAIAdapter]]:
    """
    Lazily import adapter class to avoid loading all adapters at module import time.
    
    This prevents MemoryError on Windows when importing the registry.
    
    Args:
        platform_name: Name of the platform
        
    Returns:
        Adapter class or None if not found
    """
    try:
        if platform_name == 'openai':
            from ..adapters.openai_adapter import OpenAIAdapter
            return OpenAIAdapter
        elif platform_name == 'anthropic':
            from ..adapters.anthropic_adapter import AnthropicAdapter
            return AnthropicAdapter
        elif platform_name == 'google':
            from ..adapters.gemini_adapter import GeminiAdapter
            return GeminiAdapter
        elif platform_name == 'openrouter':
            from ..adapters.openrouter_adapter import OpenRouterAdapter
            return OpenRouterAdapter
        elif platform_name == 'mock':
            from ..adapters.mock_adapter import MockAdapter
            return MockAdapter
        else:
            return None
    except ImportError as e:
        logger.error(f"Failed to import adapter for {platform_name}: {str(e)}")
        return None


class AdapterRegistry:
    """Registry for managing AI platform adapters."""
    
    # Map platform names to adapter class names (for lazy loading)
    # Actual classes are loaded via _get_adapter_class() when needed
    ADAPTER_PLATFORMS = {
        'openai': 'openai',
        'anthropic': 'anthropic',
        'google': 'google',
        'openrouter': 'openrouter',
        'mock': 'mock',
    }
    
    def __init__(self):
        """Initialize empty registry."""
        self._adapters: Dict[str, BaseAIAdapter] = {}
        self._initialized = False
    
    async def initialize(self):
        """
        Initialize all enabled platform adapters from database.
        
        Loads AIPlatform configurations and creates corresponding adapters.
        """
        if self._initialized:
            logger.warning("Registry already initialized")
            return
        
        try:
            # Use sync query with sync_to_async for Django ORM
            from asgiref.sync import sync_to_async
            
            platforms = await sync_to_async(list)(
                AIPlatform.objects.filter(is_enabled=True, status='active')
            )
            
            for platform in platforms:
                # Lazily load adapter class to avoid MemoryError
                adapter_class = _get_adapter_class(platform.platform_name)
                
                if adapter_class:
                    try:
                        adapter = adapter_class(platform)
                        self._adapters[platform.platform_name] = adapter
                        logger.info(f"Initialized adapter for {platform.platform_name}")
                    except Exception as e:
                        logger.error(
                            f"Failed to initialize {platform.platform_name} adapter: {str(e)}"
                        )
                else:
                    logger.warning(
                        f"No adapter class found for platform: {platform.platform_name}"
                    )
            
            # Always add mock adapter for testing (if no other adapters available)
            from django.conf import settings
            if len(self._adapters) == 0 or getattr(settings, 'ENABLE_MOCK_ADAPTER', True):
                try:
                    # Only add if not already present
                    if 'mock' not in self._adapters:
                        MockAdapterClass = _get_adapter_class('mock')
                        if MockAdapterClass:
                            mock_adapter = MockAdapterClass()
                            self._adapters['mock'] = mock_adapter
                            logger.info("Added mock adapter for testing")
                except Exception as e:
                    logger.warning(f"Failed to add mock adapter: {str(e)}")
            
            self._initialized = True
            logger.info(f"Registry initialized with {len(self._adapters)} adapters")
            
        except Exception as e:
            logger.error(f"Failed to initialize registry: {str(e)}")
            raise
    
    def get_adapter(self, platform_name: str) -> Optional[BaseAIAdapter]:
        """
        Get adapter by platform name.
        
        Args:
            platform_name: Name of the platform (openai, anthropic, gemini)
            
        Returns:
            Adapter instance or None if not found
        """
        adapter = self._adapters.get(platform_name)
        
        # If adapter not found and it's mock, try to add it on-demand
        if not adapter and platform_name == 'mock':
            try:
                MockAdapterClass = _get_adapter_class('mock')
                if MockAdapterClass:
                    mock_adapter = MockAdapterClass()
                    self._adapters['mock'] = mock_adapter
                    logger.info("Added mock adapter on-demand")
                    return mock_adapter
            except Exception as e:
                logger.warning(f"Failed to add mock adapter on-demand: {str(e)}")
        
        return adapter
    
    def get_all_adapters(self) -> Dict[str, BaseAIAdapter]:
        """
        Get all registered adapters.
        
        Returns:
            Dictionary mapping platform names to adapters
        """
        return self._adapters.copy()
    
    def get_adapter_names(self) -> List[str]:
        """
        Get names of all registered adapters.
        
        Returns:
            List of platform names
        """
        return list(self._adapters.keys())
    
    async def refresh(self):
        """
        Refresh adapter registry.
        
        Clears existing adapters and reinitializes from database.
        """
        logger.info("Refreshing adapter registry")
        self._adapters.clear()
        self._initialized = False
        await self.initialize()
    
    async def check_all_health(self) -> Dict[str, Dict]:
        """
        Check health of all registered adapters.
        
        Returns:
            Dictionary mapping platform names to health status
        """
        health_results = {}
        
        for platform_name, adapter in self._adapters.items():
            try:
                health = await adapter.check_health()
                health_results[platform_name] = health
            except Exception as e:
                logger.error(f"Health check failed for {platform_name}: {str(e)}")
                health_results[platform_name] = {
                    'status': 'error',
                    'error': str(e),
                    'available': False
                }
        
        return health_results


# Global registry instance
registry = AdapterRegistry()


async def get_registry() -> AdapterRegistry:
    """
    Get the global adapter registry.
    
    Initializes the registry if not already initialized.
    
    Returns:
        Initialized adapter registry
    """
    if not registry._initialized:
        await registry.initialize()
    return registry
