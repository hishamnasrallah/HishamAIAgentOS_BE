"""
Dashboard API endpoints for real-time system monitoring.
Provides stats, agent status, and workflow information.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Count, Q
from django.core.cache import cache
from django.conf import settings
from datetime import timedelta
import os
import logging

logger = logging.getLogger(__name__)

from apps.agents.models import Agent, AgentExecution
from apps.workflows.models import WorkflowExecution
from apps.commands.models import CommandTemplate, CommandExecution


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get overall system statistics for dashboard with caching.
    
    Returns:
        - total_agents: Total number of agents
        - active_agents: Number of active agents
        - total_workflows: Total workflow executions
        - running_workflows: Currently running workflows
        - total_commands: Available command templates
        - commands_executed_today: Commands executed today
        - storage_used_mb: Storage usage (placeholder)
        - api_response_time_ms: Average API response time (placeholder)
    """
    # Cache dashboard stats for 1 minute
    cache_key = 'dashboard_stats'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return Response(cached_data)
    
    # Agent statistics
    total_agents = Agent.objects.count()
    active_agents = Agent.objects.filter(status='active').count()
    
    # Workflow statistics
    total_workflows = WorkflowExecution.objects.count()
    running_workflows = WorkflowExecution.objects.filter(
        status='running'
    ).count()
    
    # Command statistics
    total_commands = CommandTemplate.objects.filter(is_active=True).count()
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    commands_today = CommandExecution.objects.filter(started_at__gte=today_start).count()
    
    # System metrics - Calculate actual values
    # Storage usage (database size + media files)
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            if 'postgresql' in settings.DATABASES['default']['ENGINE']:
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
                """)
                db_size_str = cursor.fetchone()[0]
                # Convert to MB (rough estimate, parse string like "1250 MB")
                import re
                db_size_match = re.search(r'([\d.]+)', db_size_str)
                db_size_mb = float(db_size_match.group(1)) if db_size_match else 0
                if 'GB' in db_size_str:
                    db_size_mb *= 1024
            else:
                # SQLite
                import os
                db_path = settings.DATABASES['default']['NAME']
                if os.path.exists(db_path):
                    db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
                else:
                    db_size_mb = 0
        
        # Add media files size
        media_size_mb = 0
        media_root = settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else None
        if media_root and os.path.exists(media_root):
            for dirpath, dirnames, filenames in os.walk(media_root):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    media_size_mb += os.path.getsize(filepath) / (1024 * 1024)
        
        storage_mb = int(db_size_mb + media_size_mb)
    except Exception as e:
        logger.warning(f"Could not calculate storage: {e}")
        storage_mb = 0
    
    # API response time - Calculate from recent requests (last hour)
    try:
        from apps.monitoring.models import SystemMetric
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_metrics = SystemMetric.objects.filter(
            metric_name='api_response_time',
            timestamp__gte=one_hour_ago
        ).order_by('-timestamp')[:100]
        
        if recent_metrics.exists():
            avg_response_time = sum(m.value for m in recent_metrics) / recent_metrics.count()
        else:
            avg_response_time = 0
    except Exception as e:
        logger.warning(f"Could not calculate avg response time: {e}")
        avg_response_time = 0
    
    response_data = {
        'total_agents': total_agents,
        'active_agents': active_agents,
        'total_workflows': total_workflows,
        'running_workflows': running_workflows,
        'total_commands': total_commands,
        'commands_executed_today': commands_today,
        'storage_used_mb': storage_mb,
        'api_response_time_ms': avg_response_time,
        'timestamp': timezone.now()
    }
    
    # Cache for 1 minute
    cache.set(cache_key, response_data, settings.CACHE_TIMEOUT_SHORT)
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_status_list(request):
    """
    Get list of all agents with their current status.
    
    Returns list of agents with:
        - id: Agent UUID
        - name: Agent name
        - type: Agent type
        - status: idle | busy | active
        - current_task: Current task (if busy)
        - last_active: Last activity timestamp
        - capabilities: Agent capabilities
    """
    
    agents = Agent.objects.all().order_by('name')
    
    agent_data = []
    for agent in agents:
        # Get last execution to determine status
        last_execution = agent.executions.order_by('-started_at').first()
        
        # Determine status based on agent availability and execution state
        status_value = 'idle'
        current_task = None
        last_active = None
        
        # Check if agent is available (not inactive or in maintenance)
        is_agent_available = agent.status == 'active'
        
        if last_execution:
            if last_execution.status == 'running':
                # Agent is currently executing
                status_value = 'busy'
                current_task = getattr(last_execution, 'task', None) or last_execution.input_data.get('task_description', 'Running task')
            elif is_agent_available:
                # Agent is available and has completed executions
                status_value = 'active'
            else:
                # Agent is not available (inactive or maintenance)
                status_value = 'idle'
            last_active = last_execution.started_at
        elif is_agent_available:
            # Agent is available but hasn't been used yet
            status_value = 'active'
        
        agent_data.append({
            'id': str(agent.id),
            'name': agent.name,
            'type': agent.agent_id,  # Using agent_id as type identifier
            'status': status_value,
            'current_task': current_task,
            'last_active': last_active,
            'capabilities': agent.capabilities if agent.capabilities else []
        })
    
    return Response(agent_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_workflows(request):
    """
    Get recent workflow executions.
    
    Query params:
        - limit: Number of workflows to return (default: 10, max: 50)
    
    Returns list of workflows with:
        - id: Workflow execution UUID
        - name: Workflow name
        - status: running | completed | failed | pending
        - progress: Progress percentage (0-100)
        - started_at: Start timestamp
        - completed_at: Completion timestamp (if completed)
        - current_step: Current step number
    """
    
    # Get limit from query params (default 10, max 50)
    try:
        limit = min(int(request.GET.get('limit', 10)), 50)
    except ValueError:
        limit = 10
    
    workflows = WorkflowExecution.objects.select_related(
        'workflow'
    ).order_by('-started_at')[:limit]
    
    workflow_data = []
    from apps.workflows.models import WorkflowStep
    
    for wf in workflows:
        # Calculate progress based on status
        if wf.status == 'completed':
            progress = 100
        elif wf.status in ['failed', 'running']:
            # Get total steps from workflow definition
            total_steps = 1
            if wf.workflow.definition and isinstance(wf.workflow.definition, dict):
                steps = wf.workflow.definition.get('steps', [])
                if isinstance(steps, list):
                    total_steps = len(steps)
            
            # Count completed steps from WorkflowStep model
            completed_count = WorkflowStep.objects.filter(
                execution=wf,
                status='completed'
            ).count()
            
            # Calculate progress
            progress = int((completed_count / total_steps) * 100) if total_steps > 0 else 0
        else:
            progress = 0
        
        workflow_data.append({
            'id': str(wf.id),
            'name': wf.workflow.name,
            'status': wf.status,
            'progress': min(progress, 100),  # Cap at 100%
            'started_at': wf.started_at,
            'completed_at': wf.completed_at,
            'current_step': wf.current_step
        })
    
    return Response(workflow_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_health(request):
    """
    Get system health status.
    
    Returns:
        - status: healthy | degraded | error
        - uptime_seconds: System uptime
        - database: Database connection status
        - cache: Cache connection status
        - celery: Celery worker status
    """
    
    health_data = {
        'status': 'healthy',
        'timestamp': timezone.now(),
        'checks': {}
    }
    
    # Database connectivity check
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_data['checks']['database'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
    except Exception as e:
        health_data['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        health_data['status'] = 'degraded'
    
    # Cache/Redis connectivity check
    try:
        cache.set('health_check', 'ok', 10)
        cache_result = cache.get('health_check')
        if cache_result == 'ok':
            health_data['checks']['cache'] = {
                'status': 'healthy',
                'message': 'Cache connection successful'
            }
        else:
            health_data['checks']['cache'] = {
                'status': 'unhealthy',
                'message': 'Cache test failed'
            }
            health_data['status'] = 'degraded'
    except Exception as e:
        health_data['checks']['cache'] = {
            'status': 'unhealthy',
            'message': f'Cache connection failed: {str(e)}'
        }
        health_data['status'] = 'degraded'
    
    # Celery worker status check (if Celery is configured)
    try:
        from celery import current_app
        inspect = current_app.control.inspect()
        active_workers = inspect.active()
        if active_workers:
            health_data['checks']['celery'] = {
                'status': 'healthy',
                'message': f'{len(active_workers)} worker(s) active',
                'workers': list(active_workers.keys())
            }
        else:
            health_data['checks']['celery'] = {
                'status': 'unhealthy',
                'message': 'No Celery workers active'
            }
            health_data['status'] = 'degraded'
    except Exception as e:
        # Celery not configured or not running
        health_data['checks']['celery'] = {
            'status': 'unknown',
            'message': f'Celery check failed: {str(e)}'
        }
    
    # WebSocket availability (basic check - Channels configured)
    try:
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        if channel_layer:
            health_data['checks']['websocket'] = {
                'status': 'healthy',
                'message': 'WebSocket channels configured'
            }
        else:
            health_data['checks']['websocket'] = {
                'status': 'unhealthy',
                'message': 'WebSocket channels not configured'
            }
            health_data['status'] = 'degraded'
    except Exception as e:
        health_data['checks']['websocket'] = {
            'status': 'unknown',
            'message': f'WebSocket check failed: {str(e)}'
        }
    
    # Determine overall status
    unhealthy_checks = [k for k, v in health_data['checks'].items() if v.get('status') == 'unhealthy']
    if unhealthy_checks:
        if 'database' in unhealthy_checks:
            health_data['status'] = 'error'
        else:
            health_data['status'] = 'degraded'
    
    return Response(health_data)
