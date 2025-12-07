"""
Admin-specific API endpoints for system administration.
Provides comprehensive stats and management capabilities.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from apps.authentication.models import User
from apps.agents.models import Agent, AgentExecution
from apps.integrations.models import AIPlatform
from apps.commands.models import CommandTemplate
from apps.workflows.models import WorkflowExecution
from apps.projects.models import Project


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_stats(request):
    """
    Get comprehensive admin statistics for admin dashboard.
    
    Requires admin role (checked via permission class).
    
    Returns:
        - total_users: Total number of users
        - active_users: Number of active users (logged in last 30 days)
        - total_agents: Total number of agents
        - active_agents: Number of active agents
        - total_platforms: Total number of AI platforms
        - healthy_platforms: Number of healthy platforms
        - total_commands: Total command templates
        - system_health: Overall system health status
    """
    
    # Check if user is admin
    if not request.user.is_authenticated or request.user.role != 'admin':
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # User statistics
    total_users = User.objects.count()
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_users = User.objects.filter(
        last_login__gte=thirty_days_ago
    ).count()
    
    # Agent statistics
    total_agents = Agent.objects.count()
    active_agents = Agent.objects.filter(status='active').count()
    
    # Platform statistics
    total_platforms = AIPlatform.objects.count()
    # Consider platform healthy if it's enabled and has been used recently
    healthy_platforms = AIPlatform.objects.filter(
        is_enabled=True
    ).count()
    
    # Command statistics
    total_commands = CommandTemplate.objects.filter(is_active=True).count()
    
    # System health calculation
    # Check various factors to determine overall health
    system_health = 'healthy'
    
    # Check if we have at least one healthy platform
    if healthy_platforms == 0:
        system_health = 'degraded'
    
    # Check if we have active agents
    if active_agents == 0:
        system_health = 'degraded'
    
    # Check for recent errors (if we had error tracking)
    # For now, assume healthy if basic services are available
    
    return Response({
        'total_users': total_users,
        'active_users': active_users,
        'total_agents': total_agents,
        'active_agents': active_agents,
        'total_platforms': total_platforms,
        'healthy_platforms': healthy_platforms,
        'total_commands': total_commands,
        'system_health': system_health,
        'timestamp': timezone.now()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_recent_activity(request):
    """
    Get recent admin activity for dashboard.
    
    Returns:
        - recent_users: Recently created users
        - recent_agents: Recently created agents
        - recent_platforms: Recently configured platforms
        - recent_commands: Recently added commands
    """
    
    # Check if user is admin
    if not request.user.is_authenticated or request.user.role != 'admin':
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get recent items (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    recent_users = User.objects.filter(
        date_joined__gte=seven_days_ago
    ).order_by('-date_joined')[:5]
    
    recent_agents = Agent.objects.filter(
        created_at__gte=seven_days_ago
    ).order_by('-created_at')[:5]
    
    recent_platforms = AIPlatform.objects.filter(
        created_at__gte=seven_days_ago
    ).order_by('-created_at')[:5]
    
    recent_commands = CommandTemplate.objects.filter(
        created_at__gte=seven_days_ago
    ).order_by('-created_at')[:5]
    
    return Response({
        'recent_users': [
            {
                'id': str(u.id),
                'email': u.email,
                'username': u.username,
                'role': u.role,
                'date_joined': u.date_joined
            }
            for u in recent_users
        ],
        'recent_agents': [
            {
                'id': str(a.id),
                'name': a.name,
                'agent_id': a.agent_id,
                'status': a.status,
                'created_at': a.created_at
            }
            for a in recent_agents
        ],
        'recent_platforms': [
            {
                'id': str(p.id),
                'platform_name': p.platform_name,
                'is_enabled': p.is_enabled,
                'created_at': p.created_at
            }
            for p in recent_platforms
        ],
        'recent_commands': [
            {
                'id': str(c.id),
                'name': c.name,
                'slug': c.slug,
                'category': c.category.name if c.category else None,
                'created_at': c.created_at
            }
            for c in recent_commands
        ],
        'timestamp': timezone.now()
    })

