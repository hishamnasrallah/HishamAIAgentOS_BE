# Generated manually for adding old_values and new_values fields to AuditLog

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0004_auditconfiguration'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='old_values',
            field=models.JSONField(blank=True, default=dict, help_text='Complete state before the change'),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='new_values',
            field=models.JSONField(blank=True, default=dict, help_text='Complete state after the change'),
        ),
    ]

