# Generated manually for AuditConfiguration model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('monitoring', '0003_alter_auditlog_action'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditConfiguration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True)),
                ('configuration_type', models.CharField(choices=[('default', 'Default'), ('gdpr', 'GDPR Compliance'), ('security', 'Security & Access'), ('compliance', 'General Compliance'), ('financial', 'Financial Transactions'), ('data_access', 'Data Access'), ('user_management', 'User Management'), ('system_changes', 'System Configuration'), ('custom', 'Custom')], default='custom', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('is_default', models.BooleanField(default=False, help_text='Default configuration applied to all actions')),
                ('audit_actions', models.JSONField(default=list, help_text="List of actions to audit: ['create', 'update', 'delete', 'execute', 'login', 'logout', 'read']")),
                ('audit_resource_types', models.JSONField(default=list, help_text="List of resource types to audit: ['agent', 'workflow', 'project', 'user', 'api', etc.]")),
                ('exclude_actions', models.JSONField(blank=True, default=list, help_text='Actions to exclude from auditing (takes precedence over audit_actions)')),
                ('exclude_resource_types', models.JSONField(blank=True, default=list, help_text='Resource types to exclude from auditing (takes precedence over audit_resource_types)')),
                ('exclude_resources', models.JSONField(blank=True, default=list, help_text="Specific resources to exclude: [{'resource_type': 'agent', 'resource_id': 'xxx'}]")),
                ('audit_all_users', models.BooleanField(default=True, help_text='If True, audit all users. If False, only audit users in audit_users list')),
                ('audit_users', models.JSONField(blank=True, default=list, help_text='List of user IDs to audit (only if audit_all_users=False)')),
                ('exclude_users', models.JSONField(blank=True, default=list, help_text='List of user IDs to exclude from auditing')),
                ('audit_all_ips', models.BooleanField(default=True)),
                ('audit_ips', models.JSONField(blank=True, default=list, help_text='List of IP addresses to audit (only if audit_all_ips=False)')),
                ('exclude_ips', models.JSONField(blank=True, default=list, help_text='List of IP addresses to exclude from auditing')),
                ('include_changes', models.BooleanField(default=True, help_text='Include before/after changes in audit logs')),
                ('include_ip_address', models.BooleanField(default=True)),
                ('include_user_agent', models.BooleanField(default=True)),
                ('priority', models.IntegerField(default=0, help_text='Priority order (higher = evaluated first). Default configs have priority 0.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_audit_configurations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Audit Configuration',
                'verbose_name_plural': 'Audit Configurations',
                'db_table': 'audit_configurations',
                'ordering': ['-priority', 'name'],
            },
        ),
        migrations.AddIndex(
            model_name='auditconfiguration',
            index=models.Index(fields=['is_active', 'priority'], name='audit_confi_is_acti_e20cd3_idx'),
        ),
        migrations.AddIndex(
            model_name='auditconfiguration',
            index=models.Index(fields=['configuration_type'], name='audit_confi_configu_079515_idx'),
        ),
    ]
