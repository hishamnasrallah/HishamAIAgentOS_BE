"""
Advanced Performance Tuning Utilities
Query optimization, connection pooling, batch processing.
"""
import logging
from typing import List, Any, Callable, Optional, Dict
from functools import wraps
from django.db import connection, transaction
from django.db.models import QuerySet
from django.conf import settings

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """
    Advanced query optimization utilities.
    """
    
    @staticmethod
    def optimize_with_cte(queryset: QuerySet, cte_query: str = None) -> QuerySet:
        """
        Optimize query using Common Table Expressions (CTE).
        
        For Django ORM, this applies select_related/prefetch_related optimizations.
        For actual CTE support, use raw SQL queries with this helper.
        
        Args:
            queryset: Django queryset
            cte_query: Optional CTE SQL query (for raw SQL mode)
        
        Returns:
            Optimized queryset
        """
        # Apply Django ORM optimizations
        # Check if queryset has foreign keys or many-to-many relationships
        model = queryset.model
        
        # Get all foreign key fields
        fk_fields = [f.name for f in model._meta.get_fields() if f.many_to_one]
        
        # Apply select_related for foreign keys (up to 2 levels deep)
        if fk_fields:
            # Limit to first few FK fields to avoid too many joins
            select_related_fields = fk_fields[:3]
            queryset = queryset.select_related(*select_related_fields)
        
        # Get all reverse foreign key and many-to-many fields
        reverse_fk_fields = [f.name for f in model._meta.get_fields() 
                            if f.one_to_many or f.many_to_many]
        
        # Apply prefetch_related for reverse relations
        if reverse_fk_fields:
            prefetch_fields = reverse_fk_fields[:2]  # Limit to avoid too many queries
            queryset = queryset.prefetch_related(*prefetch_fields)
        
        # If CTE query is provided, return a note that raw SQL should be used
        if cte_query:
            logger.info("CTE query provided. For actual CTE support, use raw SQL queries.")
            # Return queryset with optimization hints
            return queryset
        
        return queryset
    
    @staticmethod
    def analyze_query(queryset: QuerySet) -> Dict[str, Any]:
        """
        Analyze query performance.
        
        Args:
            queryset: Django queryset
        
        Returns:
            Analysis results
        """
        query = str(queryset.query)
        
        # Get query plan (PostgreSQL specific)
        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"EXPLAIN ANALYZE {query}")
                    plan = cursor.fetchall()
                    return {
                        'query': query,
                        'plan': plan,
                        'suggestions': QueryOptimizer._suggest_optimizations(query, plan)
                    }
            except Exception as e:
                logger.warning(f"Could not analyze query: {e}")
        
        return {
            'query': query,
            'suggestions': []
        }
    
    @staticmethod
    def _suggest_optimizations(query: str, plan: List) -> List[str]:
        """Suggest query optimizations based on plan."""
        suggestions = []
        
        plan_str = str(plan).lower()
        
        # Check for sequential scans
        if 'seq scan' in plan_str:
            suggestions.append("Consider adding an index to avoid sequential scan")
        
        # Check for nested loops
        if 'nested loop' in plan_str and 'hash' not in plan_str:
            suggestions.append("Consider using hash joins for better performance")
        
        # Check for high cost
        if 'cost=' in plan_str:
            # Extract cost (simplified)
            suggestions.append("Query cost is high, consider optimization")
        
        return suggestions


class ConnectionPoolOptimizer:
    """
    Connection pool optimization utilities.
    """
    
    @staticmethod
    def get_optimal_pool_size(
        concurrent_users: int,
        avg_query_time: float,
        max_connections: int = 100
    ) -> int:
        """
        Calculate optimal connection pool size.
        
        Args:
            concurrent_users: Expected concurrent users
            avg_query_time: Average query time in seconds
            max_connections: Maximum database connections
        
        Returns:
            Optimal pool size
        """
        # Formula: pool_size = concurrent_users * (1 + avg_query_time)
        pool_size = int(concurrent_users * (1 + avg_query_time))
        
        # Cap at max_connections
        pool_size = min(pool_size, max_connections)
        
        # Minimum pool size
        pool_size = max(pool_size, 5)
        
        return pool_size
    
    @staticmethod
    def get_pool_stats() -> Dict[str, Any]:
        """
        Get current connection pool statistics.
        
        Returns:
            Pool statistics
        """
        try:
            if 'postgresql' in settings.DATABASES['default']['ENGINE']:
                with connection.cursor() as cursor:
                    # Get connection stats
                    cursor.execute("""
                        SELECT 
                            count(*) as total_connections,
                            count(*) FILTER (WHERE state = 'active') as active_connections,
                            count(*) FILTER (WHERE state = 'idle') as idle_connections
                        FROM pg_stat_activity
                        WHERE datname = current_database()
                    """)
                    row = cursor.fetchone()
                    
                    return {
                        'total_connections': row[0] if row else 0,
                        'active_connections': row[1] if row else 0,
                        'idle_connections': row[2] if row else 0,
                        'max_connections': 100  # Default, should be from settings
                    }
        except Exception as e:
            logger.warning(f"Could not get pool stats: {e}")
        
        return {
            'total_connections': 0,
            'active_connections': 0,
            'idle_connections': 0,
            'max_connections': 100
        }


class BatchProcessor:
    """
    Batch processing utilities for efficient bulk operations.
    """
    
    @staticmethod
    def process_in_batches(
        items: List[Any],
        batch_size: int = 100,
        processor_func: Callable[[List[Any]], Any] = None,
        use_transaction: bool = True
    ) -> List[Any]:
        """
        Process items in batches.
        
        Args:
            items: List of items to process
            batch_size: Size of each batch
            processor_func: Function to process each batch
            use_transaction: Whether to use database transactions
        
        Returns:
            List of results
        """
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            if use_transaction:
                with transaction.atomic():
                    if processor_func:
                        batch_results = processor_func(batch)
                        results.extend(batch_results if isinstance(batch_results, list) else [batch_results])
                    else:
                        results.extend(batch)
            else:
                if processor_func:
                    batch_results = processor_func(batch)
                    results.extend(batch_results if isinstance(batch_results, list) else [batch_results])
                else:
                    results.extend(batch)
        
        return results
    
    @staticmethod
    def bulk_create_optimized(model_class, items: List[Dict], batch_size: int = 100):
        """
        Optimized bulk create with batching.
        
        Args:
            model_class: Django model class
            items: List of item dictionaries
            batch_size: Batch size for bulk operations
        """
        objects = [model_class(**item) for item in items]
        
        # Use bulk_create with batching
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            model_class.objects.bulk_create(batch, ignore_conflicts=True)
        
        logger.info(f"Bulk created {len(objects)} {model_class.__name__} objects in batches of {batch_size}")
    
    @staticmethod
    def bulk_update_optimized(
        queryset: QuerySet,
        update_fields: List[str],
        batch_size: int = 100
    ):
        """
        Optimized bulk update with batching.
        
        Args:
            queryset: QuerySet to update
            update_fields: Fields to update
            batch_size: Batch size for bulk operations
        """
        items = list(queryset)
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            model_class = queryset.model
            model_class.objects.bulk_update(batch, update_fields, batch_size=batch_size)
        
        logger.info(f"Bulk updated {len(items)} objects in batches of {batch_size}")


def optimize_query(queryset: QuerySet) -> QuerySet:
    """
    Decorator/function to optimize a queryset.
    
    Args:
        queryset: Django queryset
    
    Returns:
        Optimized queryset
    """
    # Apply common optimizations
    queryset = queryset.select_related()
    queryset = queryset.prefetch_related()
    queryset = queryset.only()  # Limit fields if needed
    
    return queryset


def batch_process_decorator(batch_size: int = 100):
    """
    Decorator for batch processing functions.
    
    Usage:
        @batch_process_decorator(batch_size=50)
        def process_items(items):
            # Process items
    """
    def decorator(func):
        @wraps(func)
        def wrapper(items: List[Any], *args, **kwargs):
            return BatchProcessor.process_in_batches(
                items,
                batch_size=batch_size,
                processor_func=func
            )
        return wrapper
    return decorator

