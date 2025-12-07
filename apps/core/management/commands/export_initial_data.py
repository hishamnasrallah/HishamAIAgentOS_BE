"""
Django management command to export all database data as fixtures.
Simple version - exports everything except users (except admin user).
Automatically cleans user references to point to admin user for deployment-ready fixtures.
"""

import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core import serializers
from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder


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
                # Serialize to Python format first to clean user references
                serialized_data = serializers.serialize('python', all_objects, use_natural_foreign_keys=False, use_natural_primary_keys=False)
                
                # Clean user references: replace all user IDs with admin user ID (if admin exists)
                if admin_user:
                    admin_user_id = str(admin_user.id)
                    for record in serialized_data:
                        fields = record.get('fields', {})
                        # Common user reference field names
                        user_fields = ['owner', 'owner_id', 'created_by', 'created_by_id', 
                                     'assigned_to', 'assigned_to_id', 'user', 'user_id']
                        for field_name in user_fields:
                            if field_name in fields and fields[field_name] is not None:
                                # Replace with admin user ID
                                fields[field_name] = admin_user_id
                        # Handle ManyToMany fields (members, etc.)
                        if 'members' in fields and fields['members']:
                            fields['members'] = [admin_user_id]
                
                # Save as JSON using Django's JSON encoder (handles datetime, etc.)
                with open(fixture_file, 'w', encoding='utf-8') as f:
                    json.dump(serialized_data, f, indent=2, ensure_ascii=False, cls=DjangoJSONEncoder)

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
        if admin_user:
            self.stdout.write(f"   ✅ User references cleaned (pointing to admin: {admin_user.email})")
        self.stdout.write(f"   Output directory: {output_dir.absolute()}")
        self.stdout.write("=" * 70)
        self.stdout.write("")
        self.stdout.write("✅ Fixtures are ready for deployment!")
        self.stdout.write("")
        self.stdout.write("To load these fixtures:")
        self.stdout.write(f"   python manage.py load_initial_data")
        self.stdout.write("   or")
        self.stdout.write(f"   python manage.py loaddata {output_dir}/*.json")
        self.stdout.write("")
