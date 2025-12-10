"""
Management command to generate work item numbers for existing items.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.projects.models import UserStory, Task, Bug, Issue, Epic, Project
from apps.projects.utils.work_item_numbers import get_next_work_item_number
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate work item numbers for existing stories, tasks, bugs, issues, and epics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project',
            type=str,
            help='Project ID to generate numbers for (optional, generates for all if not specified)',
        )

    def handle(self, *args, **options):
        project_id = options.get('project')
        
        if project_id:
            projects = Project.objects.filter(id=project_id)
            if not projects.exists():
                self.stdout.write(self.style.ERROR(f'Project {project_id} not found'))
                return
        else:
            projects = Project.objects.all()
        
        total_updated = 0
        
        for project in projects:
            self.stdout.write(f'\nProcessing project: {project.name}')
            project_updated = 0
            
            # Stories
            stories_without_numbers = UserStory.objects.filter(
                project=project,
                number__isnull=True
            ) | UserStory.objects.filter(
                project=project,
                number=''
            )
            
            self.stdout.write(f'  Found {stories_without_numbers.count()} stories without numbers')
            
            for story in stories_without_numbers:
                try:
                    with transaction.atomic():
                        story.number = get_next_work_item_number(str(project.id), 'story')
                        story.save(update_fields=['number'])
                        project_updated += 1
                        self.stdout.write(f'    Generated {story.number} for: {story.title[:50]}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    Error for story {story.id}: {e}'))
            
            # Tasks
            tasks_without_numbers = Task.objects.filter(
                story__project=project,
                number__isnull=True
            ) | Task.objects.filter(
                story__project=project,
                number=''
            )
            
            self.stdout.write(f'  Found {tasks_without_numbers.count()} tasks without numbers')
            
            for task in tasks_without_numbers:
                try:
                    with transaction.atomic():
                        task.number = get_next_work_item_number(str(project.id), 'task')
                        task.save(update_fields=['number'])
                        project_updated += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    Error for task {task.id}: {e}'))
            
            # Bugs
            bugs_without_numbers = Bug.objects.filter(
                project=project,
                number__isnull=True
            ) | Bug.objects.filter(
                project=project,
                number=''
            )
            
            self.stdout.write(f'  Found {bugs_without_numbers.count()} bugs without numbers')
            
            for bug in bugs_without_numbers:
                try:
                    with transaction.atomic():
                        bug.number = get_next_work_item_number(str(project.id), 'bug')
                        bug.save(update_fields=['number'])
                        project_updated += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    Error for bug {bug.id}: {e}'))
            
            # Issues
            issues_without_numbers = Issue.objects.filter(
                project=project,
                number__isnull=True
            ) | Issue.objects.filter(
                project=project,
                number=''
            )
            
            self.stdout.write(f'  Found {issues_without_numbers.count()} issues without numbers')
            
            for issue in issues_without_numbers:
                try:
                    with transaction.atomic():
                        issue.number = get_next_work_item_number(str(project.id), 'issue')
                        issue.save(update_fields=['number'])
                        project_updated += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    Error for issue {issue.id}: {e}'))
            
            # Epics
            epics_without_numbers = Epic.objects.filter(
                project=project,
                number__isnull=True
            ) | Epic.objects.filter(
                project=project,
                number=''
            )
            
            self.stdout.write(f'  Found {epics_without_numbers.count()} epics without numbers')
            
            for epic in epics_without_numbers:
                try:
                    with transaction.atomic():
                        epic.number = get_next_work_item_number(str(project.id), 'epic')
                        epic.save(update_fields=['number'])
                        project_updated += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'    Error for epic {epic.id}: {e}'))
            
            total_updated += project_updated
            self.stdout.write(self.style.SUCCESS(f'  Updated {project_updated} items in {project.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal: Generated numbers for {total_updated} work items'))

