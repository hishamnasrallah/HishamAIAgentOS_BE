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
from datetime import timedelta

from apps.agents.models import Agent, AgentExecution
from apps.workflows.models import WorkflowExecution
from apps.commands.models import CommandTemplate


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get overall system statistics for dashboard.
    
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
    
    # Agent statistics
    total_agents = Agent.objects.count()
    active_agents = Agent.objects.filter(status='active').count()
    
    # Workflow statistics
    total_workflows = WorkflowExecution.objects.count()
    running_workflows = WorkflowExecution.objects.filter(
        status='running'
    ).count()
    
    # Command statistics
    total_commands = CommandTemplate.objects.count()
    # TODO: Track command executions when execution model is created
    commands_today = 0  # Placeholder until CommandExecution model exists
    
    # System metrics (placeholders - can be calculated from actual metrics later)
    storage_mb = 1250  # TODO: Calculate actual storage usage
    avg_response_time = 45  # TODO: Calculate from request logs
    
    return Response({
        'total_agents': total_agents,
        'active_agents': active_agents,
        'total_workflows': total_workflows,
        'running_workflows': running_workflows,
        'total_commands': total_commands,
        'commands_executed_today': commands_today,
        'storage_used_mb': storage_mb,
        'api_response_time_ms': avg_response_time,
        'timestamp': timezone.now()
    })


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
        'database': 'connected',
        'cache': 'connected',
        'celery': 'running',
        'websocket': 'available'
    }
    
    # TODO: Add actual health checks
    # - Database connectivity
    # - Redis/Cache connectivity
    # - Celery worker status
    # - WebSocket availability
    
    return Response(health_data)
