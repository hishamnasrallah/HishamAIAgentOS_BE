"""
Cost tracking service for AI platform usage.

Tracks and persists AI platform usage data to the database,
including tokens, costs, and performance metrics.
"""

from typing import Optional
from decimal import Decimal
import logging

from asgiref.sync import sync_to_async
from apps.integrations.models import AIPlatform, PlatformUsage
from apps.authentication.models import User
from ..adapters.base import CompletionResponse

logger = logging.getLogger(__name__)


class CostTracker:
    """Service for tracking AI platform costs and usage."""
    
    @staticmethod
    async def track_completion(
        response: CompletionResponse,
        platform_name: str,
        user: Optional[User] = None,
        operation_type: str = 'completion'
    ) -> Optional[PlatformUsage]:
        """
        Track a completion request in the database.
        
        Args:
            response: CompletionResponse from adapter
            platform_name: Name of the platform used
            user: User who made the request (optional)
            operation_type: Type of operation (completion, streaming, etc.)
            
        Returns:
            PlatformUsage instance or None if tracking failed
        """
        try:
            # Skip tracking for mock platform (not in database)
            if platform_name == 'mock':
                logger.debug(f"Skipping cost tracking for mock platform")
                return None
            
            # Get platform instance
            platform = await sync_to_async(
                AIPlatform.objects.get
            )(platform_name=platform_name)
            
            # Extract token counts from metadata
            tokens_used = response.tokens_used
            
            # Create usage record
            usage = await sync_to_async(PlatformUsage.objects.create)(
                platform=platform,
                user=user,
                model=response.model,
                tokens_used=tokens_used,
                cost=Decimal(str(response.cost)),
                success=True,
                response_time=response.metadata.get('latency_ms', 0) / 1000,  # Convert to seconds
            )
            
            # Update platform statistics
            await sync_to_async(platform.__class__.objects.filter(id=platform.id).update)(
                total_requests=platform.total_requests + 1,
                total_tokens=platform.total_tokens + tokens_used,
                total_cost=platform.total_cost + Decimal(str(response.cost))
            )
            
            logger.info(
                f"Tracked usage: {platform_name}/{response.model} - "
                f"{tokens_used} tokens, ${response.cost:.6f}"
            )
            
            return usage
            
        except AIPlatform.DoesNotExist:
            logger.error(f"Platform not found: {platform_name}")
            return None
        except Exception as e:
            logger.error(f"Failed to track usage: {str(e)}")
            return None
    
    @staticmethod
    async def track_error(
        platform_name: str,
        model: str,
        error_message: str,
        user: Optional[User] = None,
        operation_type: str = 'completion',
        latency_ms: int = 0
    ) -> Optional[PlatformUsage]:
        """
        Track a failed request in the database.
        
        Args:
            platform_name: Name of the platform
            model: Model that was attempted
            error_message: Error message
            user: User who made the request
            operation_type: Type of operation
            latency_ms: Time taken before failure
            
        Returns:
            PlatformUsage instance or None if tracking failed
        """
        try:
            # Skip tracking for mock platform (not in database)
            if platform_name == 'mock':
                logger.debug(f"Skipping error tracking for mock platform")
                return None
            
            platform = await sync_to_async(
                AIPlatform.objects.get
            )(platform_name=platform_name)
            
            # Create error record
            usage = await sync_to_async(PlatformUsage.objects.create)(
                platform=platform,
                user=user,
                model=model,
                tokens_used=0,
                cost=Decimal('0'),
                success=False,
                error_message=error_message,
                response_time=latency_ms / 1000  # Convert to seconds
            )
            
            # Update platform failed requests counter
            await sync_to_async(platform.__class__.objects.filter(id=platform.id).update)(
                total_requests=platform.total_requests + 1,
                failed_requests=platform.failed_requests + 1
            )
            
            logger.info(f"Tracked error: {platform_name}/{model} - {error_message[:50]}")
            
            return usage
            
        except Exception as e:
            logger.error(f"Failed to track error: {str(e)}")
            return None
    
    @staticmethod
    async def get_user_cost_summary(user: User, platform_name: Optional[str] = None):
        """
        Get cost summary for a user.
        
        Args:
            user: User to get summary for
            platform_name: Optional platform filter
            
        Returns:
            Dictionary with cost summary
        """
        try:
            from django.db.models import Sum, Count, Avg
            
            queryset = PlatformUsage.objects.filter(user=user, success=True)
            
            if platform_name:
                queryset = queryset.filter(platform__platform_name=platform_name)
            
            summary = await sync_to_async(queryset.aggregate)(
                total_cost=Sum('cost'),
                total_tokens=Sum('tokens_used'),
                total_requests=Count('id'),
                avg_response_time=Avg('response_time')
            )
            
            return {
                'total_cost': float(summary['total_cost'] or 0),
                'total_tokens': summary['total_tokens'] or 0,
                'total_requests': summary['total_requests'] or 0,
                'avg_response_time_seconds': float(summary['avg_response_time'] or 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cost summary: {str(e)}")
            return {
                'total_cost': 0,
                'total_tokens': 0,
                'total_requests': 0,
                'avg_latency_ms': 0
            }


# Global tracker instance
tracker = CostTracker()
