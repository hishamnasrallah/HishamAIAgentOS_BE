"""
Performance optimization utilities.
"""
import functools
import time
import logging
from django.core.cache import cache
from django.db import connection, reset_queries
from django.conf import settings

logger = logging.getLogger(__name__)


def cache_result(timeout=300, key_prefix=''):
    """
    Decorator to cache function results.
    
    Usage:
        @cache_result(timeout=600)
        def expensive_function(arg1, arg2):
            return expensive_computation()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def query_count_monitor(func):
    """
    Decorator to monitor database query count.
    
    Usage:
        @query_count_monitor
        def my_view(request):
            # Your view code
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        reset_queries()
        start_queries = len(connection.queries)
        
        result = func(*args, **kwargs)
        
        end_queries = len(connection.queries)
        query_count = end_queries - start_queries
        
        if query_count > 10:  # Warn if more than 10 queries
            logger.warning(
                f"{func.__name__} executed {query_count} database queries. "
                f"Consider optimization."
            )
        
        return result
    return wrapper


def performance_monitor(func):
    """
    Decorator to monitor function performance.
    
    Usage:
        @performance_monitor
        def my_view(request):
            # Your view code
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        elapsed = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        if elapsed > 200:  # Warn if slower than 200ms
            logger.warning(
                f"{func.__name__} took {elapsed:.2f}ms. "
                f"Consider optimization."
            )
        
        return result
    return wrapper


def select_related_optimization(queryset, *related_fields):
    """
    Optimize queryset with select_related to prevent N+1 queries.
    
    Usage:
        queryset = select_related_optimization(
            Agent.objects.all(),
            'created_by',
            'platform'
        )
    """
    return queryset.select_related(*related_fields)


def prefetch_related_optimization(queryset, *prefetch_fields):
    """
    Optimize queryset with prefetch_related for reverse relations.
    
    Usage:
        queryset = prefetch_related_optimization(
            Project.objects.all(),
            'stories',
            'epics'
        )
    """
    return queryset.prefetch_related(*prefetch_fields)


class QueryOptimizer:
    """
    Utility class for database query optimization.
    """
    
    @staticmethod
    def optimize_list_queryset(queryset, model_class):
        """
        Automatically optimize a list queryset based on model relationships.
        """
        # Get model fields
        fields = model_class._meta.get_fields()
        
        # Find ForeignKey and OneToOneField relationships
        select_related_fields = []
        for field in fields:
            if hasattr(field, 'related_model') and field.related_model:
                select_related_fields.append(field.name)
        
        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields[:5])  # Limit to 5
        
        return queryset
    
    @staticmethod
    def get_query_count(queryset):
        """
        Get the number of queries that will be executed for a queryset.
        """
        reset_queries()
        list(queryset)  # Force evaluation
        return len(connection.queries)


def batch_process(items, batch_size=100, processor_func=None):
    """
    Process items in batches to avoid memory issues.
    
    Usage:
        for batch in batch_process(items, batch_size=50):
            process_batch(batch)
    """
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        if processor_func:
            processor_func(batch)
        yield batch

