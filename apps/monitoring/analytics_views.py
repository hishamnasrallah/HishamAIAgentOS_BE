"""
Analytics views for usage, cost, and token tracking.
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.integrations.models import PlatformUsage, AIPlatform
from apps.agents.models import AgentExecution


class AnalyticsViewSet(viewsets.ViewSet):
    """Analytics endpoints for usage, cost, and token tracking."""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def usage_summary(self, request):
        """
        Get usage summary (tokens, requests, cost) for different time periods.
        
        Query params:
        - period: 'today', 'week', 'month', 'year', 'all' (default: 'week')
        - platform: platform name filter (optional)
        - user: user ID filter (optional, admin only)
        """
        period = request.query_params.get('period', 'week')
        platform_name = request.query_params.get('platform')
        user_id = request.query_params.get('user')
        
        # Check if user is admin for user filtering
        if user_id and request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can filter by user.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calculate date range
        now = timezone.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:  # all
            start_date = None
        
        # Build queryset
        queryset = PlatformUsage.objects.filter(success=True)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        if platform_name:
            queryset = queryset.filter(platform__platform_name=platform_name)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        elif request.user.role != 'admin':
            # Non-admins only see their own usage
            queryset = queryset.filter(user=request.user)
        
        # Aggregate data
        total_count = queryset.count()
        successful_count = queryset.filter(success=True).count()
        
        summary = queryset.aggregate(
            total_requests=Count('id'),
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('cost'),
            avg_response_time=Avg('response_time'),
        )
        
        # Calculate success rate
        success_rate = (successful_count * 100.0 / total_count) if total_count > 0 else 0
        summary['success_rate'] = success_rate
        
        # Get platform breakdown
        platform_breakdown = queryset.values('platform__display_name', 'platform__platform_name').annotate(
            requests=Count('id'),
            tokens=Sum('tokens_used'),
            cost=Sum('cost')
        ).order_by('-cost')
        
        # Get model breakdown
        model_breakdown = queryset.values('model').annotate(
            requests=Count('id'),
            tokens=Sum('tokens_used'),
            cost=Sum('cost')
        ).order_by('-cost')[:10]  # Top 10 models
        
        return Response({
            'period': period,
            'start_date': start_date.isoformat() if start_date else None,
            'summary': {
                'total_requests': summary['total_requests'] or 0,
                'total_tokens': summary['total_tokens'] or 0,
                'total_cost': float(summary['total_cost'] or Decimal('0')),
                'avg_response_time_seconds': float(summary['avg_response_time'] or 0),
                'success_rate': summary['success_rate'] or 0,
            },
            'platform_breakdown': list(platform_breakdown),
            'model_breakdown': list(model_breakdown),
        })
    
    @action(detail=False, methods=['get'])
    def cost_timeline(self, request):
        """
        Get cost timeline data for charts.
        
        Query params:
        - period: 'week', 'month', 'year' (default: 'month')
        - platform: platform name filter (optional)
        - group_by: 'day', 'week', 'month' (default: 'day')
        """
        period = request.query_params.get('period', 'month')
        platform_name = request.query_params.get('platform')
        group_by = request.query_params.get('group_by', 'day')
        
        # Calculate date range
        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)
        
        # Build queryset
        queryset = PlatformUsage.objects.filter(
            success=True,
            timestamp__gte=start_date
        )
        
        if platform_name:
            queryset = queryset.filter(platform__platform_name=platform_name)
        
        if request.user.role != 'admin':
            queryset = queryset.filter(user=request.user)
        
        # Group by date (database-agnostic using Django's TruncDate)
        from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
        
        if group_by == 'day':
            queryset = queryset.annotate(
                date=TruncDate('timestamp')
            ).values('date').annotate(
                cost=Sum('cost'),
                tokens=Sum('tokens_used'),
                requests=Count('id')
            ).order_by('date')
        elif group_by == 'week':
            queryset = queryset.annotate(
                week=TruncWeek('timestamp')
            ).values('week').annotate(
                cost=Sum('cost'),
                tokens=Sum('tokens_used'),
                requests=Count('id')
            ).order_by('week')
        else:  # month
            queryset = queryset.annotate(
                month=TruncMonth('timestamp')
            ).values('month').annotate(
                cost=Sum('cost'),
                tokens=Sum('tokens_used'),
                requests=Count('id')
            ).order_by('month')
        
        timeline_data = []
        for item in queryset:
            timeline_data.append({
                'date': str(item.get('date') or item.get('week') or item.get('month')),
                'cost': float(item['cost'] or Decimal('0')),
                'tokens': item['tokens'] or 0,
                'requests': item['requests'] or 0,
            })
        
        return Response({
            'period': period,
            'group_by': group_by,
            'data': timeline_data,
        })
    
    @action(detail=False, methods=['get'])
    def token_usage(self, request):
        """
        Get token usage breakdown.
        
        Query params:
        - period: 'week', 'month', 'year' (default: 'month')
        - platform: platform name filter (optional)
        """
        period = request.query_params.get('period', 'month')
        platform_name = request.query_params.get('platform')
        
        # Calculate date range
        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)
        
        # Build queryset
        queryset = PlatformUsage.objects.filter(
            success=True,
            timestamp__gte=start_date
        )
        
        if platform_name:
            queryset = queryset.filter(platform__platform_name=platform_name)
        
        if request.user.role != 'admin':
            queryset = queryset.filter(user=request.user)
        
        # Get token usage by platform
        platform_tokens = queryset.values('platform__display_name', 'platform__platform_name').annotate(
            total_tokens=Sum('tokens_used'),
            requests=Count('id')
        ).order_by('-total_tokens')
        
        # Get token usage by model
        model_tokens = queryset.values('model').annotate(
            total_tokens=Sum('tokens_used'),
            requests=Count('id')
        ).order_by('-total_tokens')[:10]  # Top 10 models
        
        # Get daily token usage (database-agnostic)
        from django.db.models.functions import TruncDate
        daily_tokens = queryset.annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            tokens=Sum('tokens_used')
        ).order_by('date')
        
        return Response({
            'period': period,
            'platform_breakdown': [
                {
                    'platform': item['platform__display_name'],
                    'platform_name': item['platform__platform_name'],
                    'tokens': item['total_tokens'] or 0,
                    'requests': item['requests'] or 0,
                }
                for item in platform_tokens
            ],
            'model_breakdown': [
                {
                    'model': item['model'],
                    'tokens': item['total_tokens'] or 0,
                    'requests': item['requests'] or 0,
                }
                for item in model_tokens
            ],
            'daily_usage': [
                {
                    'date': str(item['date']),
                    'tokens': item['tokens'] or 0,
                }
                for item in daily_tokens
            ],
        })
    
    @action(detail=False, methods=['get'])
    def top_users(self, request):
        """
        Get top users by usage (admin only).
        
        Query params:
        - period: 'week', 'month', 'year' (default: 'month')
        - limit: number of users to return (default: 10)
        """
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can view top users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        period = request.query_params.get('period', 'month')
        limit = int(request.query_params.get('limit', 10))
        
        # Calculate date range
        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)
        
        # Get top users
        top_users = PlatformUsage.objects.filter(
            success=True,
            timestamp__gte=start_date,
            user__isnull=False
        ).values(
            'user__id', 'user__email', 'user__username',
            'user__first_name', 'user__last_name'
        ).annotate(
            total_cost=Sum('cost'),
            total_tokens=Sum('tokens_used'),
            total_requests=Count('id')
        ).order_by('-total_cost')[:limit]
        
        return Response({
            'period': period,
            'users': [
                {
                    'user_id': str(item['user__id']),
                    'email': item['user__email'],
                    'username': item['user__username'],
                    'name': f"{item['user__first_name'] or ''} {item['user__last_name'] or ''}".strip() or item['user__username'],
                    'total_cost': float(item['total_cost'] or Decimal('0')),
                    'total_tokens': item['total_tokens'] or 0,
                    'total_requests': item['total_requests'] or 0,
                }
                for item in top_users
            ],
        })

