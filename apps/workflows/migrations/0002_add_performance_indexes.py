"""
Add performance indexes for workflow queries.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflows', '0001_initial'),
    ]

    operations = [
        # Add index for user filtering with status
        migrations.AddIndex(
            model_name='workflowexecution',
            index=models.Index(fields=['user', 'status', '-created_at'], name='workflows_user_status_created_idx'),
        ),
        # Add index for workflow with status filtering
        migrations.AddIndex(
            model_name='workflowexecution',
            index=models.Index(fields=['workflow', 'status', '-started_at'], name='workflows_wf_status_started_idx'),
        ),
        # Add index for step lookups by execution
        migrations.AddIndex(
            model_name='workflowstep',
            index=models.Index(fields=['execution', 'status'], name='workflow_steps_exec_status_idx'),
        ),
        # Add index for step ordering
        migrations.AddIndex(
            model_name='workflowstep',
            index=models.Index(fields=['execution', 'step_order'], name='workflow_steps_exec_order_idx'),
        ),
    ]

