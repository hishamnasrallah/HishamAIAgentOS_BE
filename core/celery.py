"""
Celery configuration for HishamOS.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

app = Celery('hishamos')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'cleanup-old-executions': {
        'task': 'apps.agents.tasks.cleanup_old_executions',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    'update-agent-metrics': {
        'task': 'apps.agents.tasks.update_agent_metrics',
        'schedule': crontab(minute='*/15'),  # Run every 15 minutes
    },
    'cleanup-expired-tokens': {
        'task': 'apps.authentication.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=3, minute=0),  # Run at 3 AM daily
    },
    'auto-close-sprints': {
        'task': 'apps.projects.tasks.auto_close_sprints',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight daily
    },
    'check-due-dates-approaching': {
        'task': 'apps.projects.tasks.check_due_dates_approaching',
        'schedule': crontab(hour=9, minute=0),  # Run at 9 AM daily
    },
    'send-pending-email-notifications': {
        'task': 'apps.projects.tasks.send_pending_email_notifications',
        'schedule': crontab(minute='*/15'),  # Run every 15 minutes
    },
    'execute-scheduled-automation-rules': {
        'task': 'apps.projects.tasks.execute_scheduled_automation_rules',
        'schedule': crontab(hour='*/1', minute=0),  # Run every hour to check for scheduled triggers
    },
    'check-conversations-for-summarization': {
        'task': 'apps.chat.tasks.check_conversations_for_summarization',
        'schedule': crontab(minute='*/30'),  # Run every 30 minutes to check for conversations needing summarization
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery is working."""
    print(f'Request: {self.request!r}')
