"""
Add performance indexes for command queries.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commands', '0001_initial'),
    ]

    operations = [
        # Add index for filtering by is_active and ordering by usage
        migrations.AddIndex(
            model_name='commandtemplate',
            index=models.Index(fields=['is_active', '-usage_count'], name='commands_is_active_usage_idx'),
        ),
        # Add index for category filtering with ordering
        migrations.AddIndex(
            model_name='commandtemplate',
            index=models.Index(fields=['category', 'is_active', '-success_rate'], name='commands_cat_active_success_idx'),
        ),
        # Add index for recommended_agent lookups
        migrations.AddIndex(
            model_name='commandtemplate',
            index=models.Index(fields=['recommended_agent'], name='commands_recommended_agent_idx'),
        ),
    ]

