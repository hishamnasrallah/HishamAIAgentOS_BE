"""
Management command to update project permission_settings to replace 'admin' with 'org_admin'.

This command:
1. Finds all ProjectConfiguration with permission_settings
2. Replaces 'admin' with 'org_admin' in all permission lists
3. Saves updated settings
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.projects.models import ProjectConfiguration


class Command(BaseCommand):
    help = 'Update project permission_settings to replace "admin" with "org_admin"'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find all configurations with permission_settings
        configs = ProjectConfiguration.objects.filter(
            permission_settings__isnull=False
        ).exclude(permission_settings={})
        
        count = configs.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No project configurations with permission_settings found.'))
            return
        
        self.stdout.write(f'Found {count} project configuration(s) with permission_settings')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        updated = 0
        skipped = 0
        errors = 0
        
        for config in configs:
            try:
                settings = config.permission_settings
                if not isinstance(settings, dict):
                    skipped += 1
                    continue
                
                has_changes = False
                updated_settings = {}
                
                for key, value in settings.items():
                    if isinstance(value, list):
                        # Replace 'admin' with 'org_admin' in role lists
                        new_value = [r if r != 'admin' else 'org_admin' for r in value]
                        if new_value != value:
                            has_changes = True
                            updated_settings[key] = new_value
                        else:
                            updated_settings[key] = value
                    else:
                        updated_settings[key] = value
                
                if has_changes:
                    if dry_run:
                        self.stdout.write(
                            f'\n[DRY RUN] Would update project: {config.project.name if config.project else "Unknown"} '
                            f'(ID: {config.project.id if config.project else "N/A"})'
                        )
                        for key, old_value in settings.items():
                            if isinstance(old_value, list) and 'admin' in old_value:
                                new_value = [r if r != 'admin' else 'org_admin' for r in old_value]
                                self.stdout.write(f'  {key}: {old_value} -> {new_value}')
                    else:
                        with transaction.atomic():
                            config.permission_settings = updated_settings
                            config.save(update_fields=['permission_settings'])
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Updated permission_settings for project: '
                                f'{config.project.name if config.project else "Unknown"}'
                            )
                        )
                        updated += 1
                else:
                    skipped += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error updating project {config.project.name if config.project else "Unknown"}: {str(e)}'
                    )
                )
                errors += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN SUMMARY:'))
            self.stdout.write(f'  Would update: {updated} project(s)')
        else:
            self.stdout.write(self.style.SUCCESS('MIGRATION SUMMARY:'))
            self.stdout.write(f'  Updated: {updated} project(s)')
            self.stdout.write(f'  Skipped: {skipped} project(s)')
            self.stdout.write(f'  Errors: {errors} project(s)')
        
        if not dry_run and updated > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Successfully updated {updated} project permission_settings'
                )
            )

