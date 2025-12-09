# Generated manually for StatusChangeApproval model
# Date: December 9, 2024

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0015_bug_custom_fields_issue_custom_fields_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusChangeApproval',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('object_id', models.UUIDField()),
                ('old_status', models.CharField(max_length=50)),
                ('new_status', models.CharField(max_length=50)),
                ('reason', models.TextField(blank=True, help_text='Reason for status change')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], db_index=True, default='pending', max_length=20)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('rejection_reason', models.TextField(blank=True, help_text='Reason for rejection if rejected')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approver', models.ForeignKey(blank=True, help_text='User who should approve this request', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approvals_to_review', to=settings.AUTH_USER_MODEL)),
                ('approved_by', models.ForeignKey(blank=True, help_text='User who approved/rejected the request', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_requests', to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('project', models.ForeignKey(help_text='Project this approval belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='status_change_approvals', to='projects.project')),
                ('requested_by', models.ForeignKey(help_text='User who requested the status change', on_delete=django.db.models.deletion.CASCADE, related_name='requested_approvals', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Status Change Approval',
                'verbose_name_plural': 'Status Change Approvals',
                'db_table': 'status_change_approvals',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='statuschangeapproval',
            index=models.Index(fields=['project', 'status'], name='status_chan_project_status_idx'),
        ),
        migrations.AddIndex(
            model_name='statuschangeapproval',
            index=models.Index(fields=['content_type', 'object_id'], name='status_chan_content_object_idx'),
        ),
        migrations.AddIndex(
            model_name='statuschangeapproval',
            index=models.Index(fields=['requested_by', 'status'], name='status_chan_requested_status_idx'),
        ),
        migrations.AddIndex(
            model_name='statuschangeapproval',
            index=models.Index(fields=['approver', 'status'], name='status_chan_approver_status_idx'),
        ),
    ]

