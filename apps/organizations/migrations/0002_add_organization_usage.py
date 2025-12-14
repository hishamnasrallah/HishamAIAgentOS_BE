# Generated manually on 2025-12-12

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationUsage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('usage_type', models.CharField(choices=[('agent_executions', 'Agent Executions'), ('workflow_executions', 'Workflow Executions'), ('chat_messages', 'Chat Messages'), ('command_executions', 'Command Executions')], db_index=True, max_length=50)),
                ('month', models.IntegerField(help_text='Month (1-12)')),
                ('year', models.IntegerField(help_text='Year (e.g., 2025)')),
                ('count', models.IntegerField(default=0, help_text='Usage count for this month')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='usage_records', to='organizations.organization')),
            ],
            options={
                'verbose_name': 'Organization Usage',
                'verbose_name_plural': 'Organization Usage Records',
                'db_table': 'organization_usage',
            },
        ),
        migrations.AddIndex(
            model_name='organizationusage',
            index=models.Index(fields=['organization', 'usage_type', 'month', 'year'], name='organizatio_organiz_usage_idx'),
        ),
        migrations.AddIndex(
            model_name='organizationusage',
            index=models.Index(fields=['organization', 'usage_type'], name='organizatio_organiz_usage_t_idx'),
        ),
        migrations.AddIndex(
            model_name='organizationusage',
            index=models.Index(fields=['month', 'year'], name='organizatio_month_yea_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='organizationusage',
            unique_together={('organization', 'usage_type', 'month', 'year')},
        ),
    ]


