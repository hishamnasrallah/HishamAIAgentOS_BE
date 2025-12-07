"""
Django management command to create or update the default admin user.

This command creates an admin user with the following credentials:
- Email: admin@hishamos.com
- Password: Amman123
- Role: admin
- is_staff: True
- is_superuser: True

Usage:
    python manage.py setup_admin_user
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or update the default admin user (admin@hishamos.com)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@hishamos.com',
            help='Admin user email (default: admin@hishamos.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Amman123',
            help='Admin user password (default: Amman123)'
        )
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin user username (default: admin)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing user password'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        username = options['username']
        force = options['force']

        try:
            with transaction.atomic():
                # Check if user exists
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': username,
                        'role': 'admin',
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True,
                    }
                )

                if created:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Successfully created admin user: {email}'
                        )
                    )
                else:
                    # User exists
                    if force:
                        user.set_password(password)
                        user.username = username
                        user.role = 'admin'
                        user.is_staff = True
                        user.is_superuser = True
                        user.is_active = True
                        user.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✅ Successfully updated admin user: {email}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠️  Admin user already exists: {email}'
                            )
                        )
                        self.stdout.write(
                            self.style.WARNING(
                                '   Use --force to update password and settings'
                            )
                        )
                        return

                # Display user information
                self.stdout.write('')
                self.stdout.write('Admin User Details:')
                self.stdout.write(f'  Email: {user.email}')
                self.stdout.write(f'  Username: {user.username}')
                self.stdout.write(f'  Role: {user.role}')
                self.stdout.write(f'  Staff: {user.is_staff}')
                self.stdout.write(f'  Superuser: {user.is_superuser}')
                self.stdout.write(f'  Active: {user.is_active}')
                self.stdout.write('')
                self.stdout.write(
                    self.style.SUCCESS('✅ Admin user setup complete!')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating admin user: {str(e)}')
            )
            raise

