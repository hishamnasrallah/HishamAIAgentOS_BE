"""
Add performance indexes for agent queries.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0001_initial'),
    ]

    operations = [
        # Add index for status filtering with ordering
        migrations.AddIndex(
            model_name='agent',
            index=models.Index(fields=['status', '-total_invocations'], name='agents_status_invocations_idx'),
        ),
        # Add index for preferred_platform filtering
        migrations.AddIndex(
            model_name='agent',
            index=models.Index(fields=['preferred_platform', 'status'], name='agents_platform_status_idx'),
        ),
        # Add index for agent execution lookups by user and status
        migrations.AddIndex(
            model_name='agentexecution',
            index=models.Index(fields=['user', 'status', '-created_at'], name='agent_exec_user_status_created_idx'),
        ),
        # Add index for platform filtering
        migrations.AddIndex(
            model_name='agentexecution',
            index=models.Index(fields=['platform_used', '-created_at'], name='agent_exec_platform_created_idx'),
        ),
    ]

