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
from apps.core.services.roles import RoleService


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
    if not request.user.is_authenticated or not RoleService.is_admin(request.user):
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Filter by organization for org_admin
    is_super_admin = RoleService.is_super_admin(request.user)
    user_orgs = RoleService.get_user_organizations(request.user)
    org_ids = [org.id for org in user_orgs] if user_orgs else []
    
    # User statistics
    user_qs = User.objects.all()
    if not is_super_admin and org_ids:
        user_qs = user_qs.filter(organization_id__in=org_ids)
    total_users = user_qs.count()
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_users = user_qs.filter(
        last_login__gte=thirty_days_ago
    ).count()
    
    # Agent statistics (org_admin sees all agents, but could be filtered by org if needed)
    agent_qs = Agent.objects.all()
    # Note: Agents don't have organization field yet, so org_admin sees all
    # If you add organization to Agent model, filter here
    total_agents = agent_qs.count()
    active_agents = agent_qs.filter(status='active').count()
    
    # Platform statistics (org_admin sees all platforms)
    platform_qs = AIPlatform.objects.all()
    # Note: Platforms don't have organization field yet, so org_admin sees all
    # If you add organization to AIPlatform model, filter here
    total_platforms = platform_qs.count()
    healthy_platforms = platform_qs.filter(is_enabled=True).count()
    
    # Command statistics (org_admin sees all commands)
    command_qs = CommandTemplate.objects.filter(is_active=True)
    total_commands = command_qs.count()
    
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
    if not request.user.is_authenticated or not RoleService.is_admin(request.user):
        return Response(
            {'error': 'Admin access required'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Filter by organization for org_admin
    is_super_admin = RoleService.is_super_admin(request.user)
    user_orgs = RoleService.get_user_organizations(request.user)
    org_ids = [org.id for org in user_orgs] if user_orgs else []
    
    # Get recent items (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    # Recent users - filter by organization for org_admin
    user_qs = User.objects.filter(date_joined__gte=seven_days_ago)
    if not is_super_admin and org_ids:
        user_qs = user_qs.filter(organization_id__in=org_ids)
    recent_users = user_qs.order_by('-date_joined')[:5]
    
    # Recent agents (all agents for now, can be filtered by org if needed)
    recent_agents = Agent.objects.filter(
        created_at__gte=seven_days_ago
    ).order_by('-created_at')[:5]
    
    # Recent platforms (all platforms for now, can be filtered by org if needed)
    recent_platforms = AIPlatform.objects.filter(
        created_at__gte=seven_days_ago
    ).order_by('-created_at')[:5]
    
    # Recent commands (all commands for now, can be filtered by org if needed)
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

