"""
Prometheus metrics exporters for HishamOS.

Provides metrics collection for Prometheus monitoring.
"""

from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods


# Agent execution metrics
agent_executions_total = Counter(
    'hishamos_agent_executions_total',
    'Total number of agent executions',
    ['agent_id', 'status']
)

agent_execution_duration = Histogram(
    'hishamos_agent_execution_duration_seconds',
    'Agent execution duration in seconds',
    ['agent_id'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

agent_tokens_used = Counter(
    'hishamos_agent_tokens_total',
    'Total tokens used by agents',
    ['agent_id', 'platform']
)

agent_cost = Counter(
    'hishamos_agent_cost_total',
    'Total cost of agent executions',
    ['agent_id', 'platform']
)

# Command execution metrics
command_executions_total = Counter(
    'hishamos_command_executions_total',
    'Total number of command executions',
    ['command_id', 'status']
)

command_execution_duration = Histogram(
    'hishamos_command_execution_duration_seconds',
    'Command execution duration in seconds',
    ['command_id'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

# Workflow execution metrics
workflow_executions_total = Counter(
    'hishamos_workflow_executions_total',
    'Total number of workflow executions',
    ['workflow_id', 'status']
)

workflow_execution_duration = Histogram(
    'hishamos_workflow_execution_duration_seconds',
    'Workflow execution duration in seconds',
    ['workflow_id'],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0)
)

# API metrics
api_requests_total = Counter(
    'hishamos_api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration = Histogram(
    'hishamos_api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# System metrics
active_users = Gauge(
    'hishamos_active_users',
    'Number of active users'
)

system_health = Gauge(
    'hishamos_system_health',
    'System health status (1=healthy, 0=unhealthy)',
    ['component']
)

database_connections = Gauge(
    'hishamos_database_connections',
    'Number of active database connections'
)

cache_hits = Counter(
    'hishamos_cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses = Counter(
    'hishamos_cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# Error metrics
errors_total = Counter(
    'hishamos_errors_total',
    'Total number of errors',
    ['error_type', 'component']
)


@require_http_methods(["GET"])
def metrics_view(request):
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus format.
    """
    metrics_data = generate_latest()
    return HttpResponse(metrics_data, content_type=CONTENT_TYPE_LATEST)


def record_agent_execution(agent_id: str, status: str, duration: float, tokens: int, cost: float, platform: str):
    """Record agent execution metrics."""
    agent_executions_total.labels(agent_id=agent_id, status=status).inc()
    agent_execution_duration.labels(agent_id=agent_id).observe(duration)
    agent_tokens_used.labels(agent_id=agent_id, platform=platform).inc(tokens)
    agent_cost.labels(agent_id=agent_id, platform=platform).inc(cost)


def record_command_execution(command_id: str, status: str, duration: float):
    """Record command execution metrics."""
    command_executions_total.labels(command_id=command_id, status=status).inc()
    command_execution_duration.labels(command_id=command_id).observe(duration)


def record_workflow_execution(workflow_id: str, status: str, duration: float):
    """Record workflow execution metrics."""
    workflow_executions_total.labels(workflow_id=workflow_id, status=status).inc()
    workflow_execution_duration.labels(workflow_id=workflow_id).observe(duration)


def record_api_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record API request metrics."""
    api_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)


def record_error(error_type: str, component: str):
    """Record error metrics."""
    errors_total.labels(error_type=error_type, component=component).inc()


def set_system_health(component: str, healthy: bool):
    """Set system health status."""
    system_health.labels(component=component).set(1 if healthy else 0)


def set_active_users(count: int):
    """Set active users count."""
    active_users.set(count)


def record_cache_hit(cache_type: str):
    """Record cache hit."""
    cache_hits.labels(cache_type=cache_type).inc()


def record_cache_miss(cache_type: str):
    """Record cache miss."""
    cache_misses.labels(cache_type=cache_type).inc()

