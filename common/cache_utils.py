"""
Cache utility functions for HishamOS.
"""
from django.core.cache import cache
from django.conf import settings


def invalidate_command_cache():
    """Invalidate all command-related cache keys."""
    cache_keys = [
        'command_categories_list',
        'command_templates_list_all',
    ]
    for key in cache_keys:
        cache.delete(key)
    # Delete all command list variations (if using django-redis)
    try:
        from django_redis import get_redis_connection
        redis_client = get_redis_connection("default")
        for key in redis_client.keys('hishamos:command_templates_list_*'):
            cache.delete(key.decode('utf-8').replace('hishamos:', ''))
    except (ImportError, AttributeError):
        # Fallback: just delete known keys
        pass


def invalidate_agent_cache():
    """Invalidate all agent-related cache keys."""
    cache.delete('agents_list')


def invalidate_workflow_cache():
    """Invalidate all workflow-related cache keys."""
    cache.delete('workflows_list_all')
    cache.delete('workflow_templates_list')
    # Delete workflow list variations (if using django-redis)
    try:
        from django_redis import get_redis_connection
        redis_client = get_redis_connection("default")
        for key in redis_client.keys('hishamos:workflows_list_*'):
            cache.delete(key.decode('utf-8').replace('hishamos:', ''))
    except (ImportError, AttributeError):
        # Fallback: just delete known keys
        pass


def invalidate_dashboard_cache():
    """Invalidate dashboard cache."""
    cache.delete('dashboard_stats')


def invalidate_all_cache():
    """Invalidate all application cache."""
    invalidate_command_cache()
    invalidate_agent_cache()
    invalidate_workflow_cache()
    invalidate_dashboard_cache()


def get_or_set_cache(key, callable_func, timeout=None):
    """
    Get value from cache or set it using callable.
    
    Args:
        key: Cache key
        callable_func: Function to call if cache miss
        timeout: Cache timeout in seconds (defaults to CACHE_TIMEOUT_MEDIUM)
    
    Returns:
        Cached or computed value
    """
    if timeout is None:
        timeout = settings.CACHE_TIMEOUT_MEDIUM
    
    value = cache.get(key)
    if value is None:
        value = callable_func()
        cache.set(key, value, timeout)
    return value

