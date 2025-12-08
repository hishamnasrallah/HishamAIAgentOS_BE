"""
Integration between monitoring and alerting systems.
"""
import logging
from typing import Dict, Any
from apps.core.alerting import get_alert_manager

logger = logging.getLogger(__name__)


def check_system_health_and_alert():
    """
    Check system health metrics and trigger alerts if needed.
    Should be called periodically (e.g., via Celery beat).
    """
    from apps.monitoring.models import SystemMetric, HealthCheck
    
    alert_manager = get_alert_manager()
    
    # Get latest metrics
    try:
        latest_metric = SystemMetric.objects.order_by('-timestamp').first()
        if not latest_metric:
            return
        
        # Build context for alert evaluation
        context = {
            'timestamp': latest_metric.timestamp,
            'cpu_usage': latest_metric.cpu_usage,
            'memory_usage': latest_metric.memory_usage,
            'disk_usage': latest_metric.disk_usage,
            'error_rate': latest_metric.error_rate or 0,
            'avg_response_time': latest_metric.avg_response_time or 0,
        }
        
        # Calculate memory free percentage
        if latest_metric.memory_usage:
            memory_free = 100 - latest_metric.memory_usage
            context['memory_free'] = memory_free
        
        # Check database connection
        from django.db import connection
        try:
            connection.ensure_connection()
            context['db_connection_errors'] = 0
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            context['db_connection_errors'] = 1
        
        # Evaluate alert rules
        alert_manager.evaluate_rules(context)
        
    except Exception as e:
        logger.error(f"Error in health check and alert: {e}")


def alert_on_workflow_failure(workflow_execution):
    """Alert when a workflow execution fails."""
    alert_manager = get_alert_manager()
    
    context = {
        'timestamp': workflow_execution.updated_at,
        'workflow_id': str(workflow_execution.workflow.id),
        'workflow_name': workflow_execution.workflow.name,
        'execution_id': str(workflow_execution.id),
        'status': workflow_execution.status,
        'error': str(workflow_execution.error) if workflow_execution.error else None,
    }
    
    # Create temporary rule for workflow failure
    from apps.core.alerting import AlertRule
    rule = AlertRule(
        name='workflow_execution_failed',
        condition=lambda ctx: ctx.get('status') == 'failed',
        severity='error',
        channels=['email', 'slack'],
        message_template='Workflow "{workflow_name}" execution failed: {error}'
    )
    
    alert_manager.register_rule(rule)
    alert_manager.evaluate_rules(context)

