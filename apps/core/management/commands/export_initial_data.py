"""
Django management command to export all database data as fixtures.
Simple version - exports everything except users (except admin user).
"""

from pathlib import Path
from django.core.management.base import BaseCommand
from django.core import serializers
from django.apps import apps


class Command(BaseCommand):
    help = 'Export all database data to JSON fixtures (simple version)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='initial_data/fixtures',
            help='Output directory for fixtures (default: initial_data/fixtures)'
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output'])
        output_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write("=" * 70)
        self.stdout.write("  HISHAMOS - EXPORT INITIAL DATA (SIMPLE)")
        self.stdout.write("=" * 70)
        self.stdout.write("")

        # Get admin user ID (email: admin@hishamos.com)
        admin_user = None
        try:
            User = apps.get_model('authentication', 'User')
            admin_user = User.objects.filter(email='admin@hishamos.com').first()
        except:
            pass

        total_files = 0
        total_records = 0

        # Export all apps
        for app_config in apps.get_app_configs():
            app_label = app_config.label
            
            # Skip Django built-in apps
            if app_label in ['admin', 'auth', 'contenttypes', 'sessions', 'messages', 'staticfiles']:
                continue

            app_total_records = 0
            all_objects = []

            # Export all models in this app
            for model in app_config.get_models():
                # Skip proxy models
                if model._meta.proxy:
                    continue

                # For User model: export only admin user
                if app_label == 'authentication' and model.__name__ == 'User':
                    if admin_user:
                        try:
                            all_objects.append(admin_user)
                            app_total_records += 1
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f"  ⚠️  Error exporting admin user: {e}")
                            )
                    continue

                # Export all records for this model
                try:
                    records = model.objects.all()
                    if records.exists():
                        all_objects.extend(list(records))
                        app_total_records += records.count()
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠️  Error exporting {model.__name__}: {e}")
                    )
                    continue

            # Save fixture file if we have data
            if all_objects:
                fixture_file = output_dir / f"{app_label}.json"
                # Use Django's JSON serializer directly to handle datetime objects
                with open(fixture_file, 'w', encoding='utf-8') as f:
                    serializers.serialize('json', all_objects, indent=2, stream=f, use_natural_foreign_keys=False, use_natural_primary_keys=False)

                total_files += 1
                total_records += app_total_records

                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ {app_label}.json ({app_total_records} records)")
                )
            else:
                self.stdout.write(f"  ⏭️  {app_label}: No records")

        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Export Complete!"))
        self.stdout.write(f"   Files created: {total_files}")
        self.stdout.write(f"   Total records: {total_records}")
        self.stdout.write(f"   Output directory: {output_dir.absolute()}")
        self.stdout.write("=" * 70)
        self.stdout.write("")
        self.stdout.write("To load these fixtures:")
        self.stdout.write(f"   python manage.py loaddata {output_dir}/*.json")
        self.stdout.write("")
