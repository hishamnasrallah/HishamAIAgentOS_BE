"""
Management command to migrate users with role='admin' to org_admin.

This command:
1. Finds all users with role='admin'
2. For each user:
   - If user.is_superuser: Keep as superuser (no change needed)
   - Otherwise: Create OrganizationMember with role='org_admin' for their organization
3. Optionally updates user.role to 'viewer' or another role
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.authentication.models import User
from apps.organizations.models import OrganizationMember, Organization


class Command(BaseCommand):
    help = 'Migrate users with role="admin" to org_admin role'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes',
        )
        parser.add_argument(
            '--update-role',
            type=str,
            default='viewer',
            help='Role to set for user.role field after migration (default: viewer)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        update_role = options['update_role']
        
        # Find all users with role='admin'
        admin_users = User.objects.filter(role='admin')
        count = admin_users.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No users with role="admin" found. Migration not needed.'))
            return
        
        self.stdout.write(f'Found {count} user(s) with role="admin"')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        migrated = 0
        skipped = 0
        errors = 0
        
        for user in admin_users:
            try:
                if dry_run:
                    self.stdout.write(f'\n[DRY RUN] Would migrate: {user.email} (ID: {user.id})')
                else:
                    with transaction.atomic():
                        # If user is superuser, they're already super_admin - no change needed
                        if user.is_superuser:
                            self.stdout.write(f'Skipping {user.email} - already superuser (super_admin)')
                            skipped += 1
                            continue
                        
                        # Get user's organization
                        organization = user.organization
                        if not organization:
                            # Try to find organization from OrganizationMember
                            org_member = OrganizationMember.objects.filter(user=user).first()
                            if org_member:
                                organization = org_member.organization
                        
                        if not organization:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'User {user.email} has no organization. Skipping migration. '
                                    'Please assign organization first.'
                                )
                            )
                            skipped += 1
                            continue
                        
                        # Create or update OrganizationMember with org_admin role
                        org_member, created = OrganizationMember.objects.get_or_create(
                            organization=organization,
                            user=user,
                            defaults={'role': 'org_admin'}
                        )
                        
                        if not created:
                            # Update existing membership
                            org_member.role = 'org_admin'
                            org_member.save()
                        
                        # Update user.role to specified role (default: viewer)
                        user.role = update_role
                        user.save(update_fields=['role'])
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Migrated {user.email} to org_admin in organization "{organization.name}"'
                            )
                        )
                        migrated += 1
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error migrating {user.email}: {str(e)}')
                )
                errors += 1
        
        # Summary
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN SUMMARY:'))
            self.stdout.write(f'  Would migrate: {count} user(s)')
        else:
            self.stdout.write(self.style.SUCCESS('MIGRATION SUMMARY:'))
            self.stdout.write(f'  Migrated: {migrated} user(s)')
            self.stdout.write(f'  Skipped: {skipped} user(s)')
            self.stdout.write(f'  Errors: {errors} user(s)')
        
        if not dry_run and migrated > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Successfully migrated {migrated} user(s) from "admin" to "org_admin"'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  Next steps:'
                    '\n  1. Update project permission_settings to replace "admin" with "org_admin"'
                    '\n  2. Run: python manage.py migrate_project_permissions'
                )
            )

