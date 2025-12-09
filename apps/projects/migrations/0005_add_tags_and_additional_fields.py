# Generated manually on 2024-12-08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_projectconfiguration'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        # Add tags to Project
        migrations.AddField(
            model_name='project',
            name='tags',
            field=models.JSONField(blank=True, default=list, help_text='Tags for categorizing and filtering projects'),
        ),
        
        # Add tags and owner to Epic
        migrations.AddField(
            model_name='epic',
            name='tags',
            field=models.JSONField(blank=True, default=list, help_text='Tags for categorizing and filtering epics'),
        ),
        migrations.AddField(
            model_name='epic',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                help_text='Epic owner/lead',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='owned_epics',
                to='authentication.user'
            ),
        ),
        
        # Add tags, story_type, component, due_date, labels to UserStory
        migrations.AddField(
            model_name='userstory',
            name='tags',
            field=models.JSONField(blank=True, default=list, help_text='Tags for categorizing and filtering stories'),
        ),
        migrations.AddField(
            model_name='userstory',
            name='story_type',
            field=models.CharField(
                choices=[
                    ('feature', 'Feature'),
                    ('bug', 'Bug'),
                    ('enhancement', 'Enhancement'),
                    ('technical_debt', 'Technical Debt'),
                    ('documentation', 'Documentation'),
                    ('research', 'Research'),
                ],
                default='feature',
                help_text='Type of user story',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='userstory',
            name='component',
            field=models.CharField(
                blank=True,
                help_text="Component or module this story belongs to (e.g., 'Frontend', 'API', 'Database')",
                max_length=100
            ),
        ),
        migrations.AddField(
            model_name='userstory',
            name='due_date',
            field=models.DateField(blank=True, help_text='Due date for this story', null=True),
        ),
        migrations.AddField(
            model_name='userstory',
            name='labels',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Color-coded labels for visual grouping (e.g., [{'name': 'Urgent', 'color': '#red'}])"
            ),
        ),
        
        # Add tags and due_date to Task
        migrations.AddField(
            model_name='task',
            name='tags',
            field=models.JSONField(blank=True, default=list, help_text='Tags for categorizing and filtering tasks'),
        ),
        migrations.AddField(
            model_name='task',
            name='due_date',
            field=models.DateField(blank=True, help_text='Due date for this task', null=True),
        ),
    ]

