"""
Django management command to export all database data as fixtures.
"""

import os
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core import serializers
from django.apps import apps
from django.db import models


class Command(BaseCommand):
    help = 'Export all database data to JSON fixtures'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='initial_data/fixtures',
            help='Output directory for fixtures (default: initial_data/fixtures)'
        )
        parser.add_argument(
            '--apps',
            nargs='+',
            help='Export only specific apps (e.g., --apps agents commands)'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='json',
            choices=['json', 'xml'],
            help='Output format (default: json)'
        )
        parser.add_argument(
            '--indent',
            type=int,
            default=2,
            help='JSON indentation level (default: 2)'
        )
        parser.add_argument(
            '--exclude-empty',
            action='store_true',
            default=True,
            help='Skip empty fixtures (default: True)'
        )
        parser.add_argument(
            '--include-audit',
            action='store_true',
            help='Include audit logs'
        )
        parser.add_argument(
            '--include-metrics',
            action='store_true',
            help='Include system metrics'
        )
        parser.add_argument(
            '--include-histories',
            action='store_true',
            help='Include execution histories'
        )
        parser.add_argument(
            '--exclude-users',
            action='store_true',
            help='Exclude user data (useful for templates)'
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output'])
        output_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write("=" * 70)
        self.stdout.write("  HISHAMOS - EXPORT INITIAL DATA")
        self.stdout.write("=" * 70)
        self.stdout.write("")

        # Define models to export by app
        apps_to_export = self._get_apps_to_export(options.get('apps'))

        total_files = 0
        total_records = 0

        for app_label in apps_to_export:
            app_config = apps.get_app_config(app_label)
            models_to_export = self._get_models_to_export(
                app_config,
                options
            )

            if not models_to_export:
                continue

            app_total_records = 0
            fixture_data = []

            for model in models_to_export:
                try:
                    objects = model.objects.all()
                    count = objects.count()

                    if count == 0 and options['exclude_empty']:
                        self.stdout.write(
                            f"  ⏭️  {app_label}.{model.__name__}: No records"
                        )
                        continue

                    # Serialize objects
                    serialized = serializers.serialize(
                        options['format'],
                        objects,
                        indent=options['indent'] if options['format'] == 'json' else None
                    )

                    if options['format'] == 'json':
                        # Parse JSON and add to fixture data
                        parsed = json.loads(serialized)
                        fixture_data.extend(parsed)
                        app_total_records += len(parsed)

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ {app_label}.{model.__name__}: {count} records"
                            )
                        )
                    else:
                        # For XML, append directly
                        fixture_data.append(serialized)
                        app_total_records += count

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ✗ {app_label}.{model.__name__}: Error - {str(e)}"
                        )
                    )
                    continue

            # Save fixture file
            if fixture_data:
                fixture_file = output_dir / f"{app_label}.{options['format']}"

                if options['format'] == 'json':
                    # Pretty print JSON
                    with open(fixture_file, 'w', encoding='utf-8') as f:
                        json.dump(fixture_data, f, indent=options['indent'], ensure_ascii=False)
                else:
                    # XML format
                    with open(fixture_file, 'w', encoding='utf-8') as f:
                        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                        f.write('<django-objects version="1.0">\n')
                        for xml_data in fixture_data:
                            f.write(xml_data)
                        f.write('</django-objects>\n')

                total_files += 1
                total_records += app_total_records

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  💾 Saved: {fixture_file} ({app_total_records} records)"
                    )
                )
                self.stdout.write("")

        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Export Complete!"))
        self.stdout.write(f"   Files created: {total_files}")
        self.stdout.write(f"   Total records: {total_records}")
        self.stdout.write(f"   Output directory: {output_dir.absolute()}")
        self.stdout.write("=" * 70)
        self.stdout.write("")
        self.stdout.write("To import these fixtures, use:")
        self.stdout.write(f"   python manage.py loaddata {output_dir}/*.{options['format']}")

    def _get_apps_to_export(self, specified_apps=None):
        """Get list of apps to export."""
        all_apps = [
            'core',
            'authentication',
            'agents',
            'commands',
            'projects',
            'workflows',
            'integrations',
            'monitoring',
            'chat',
            'results',
        ]

        if specified_apps:
            # Validate specified apps
            valid_apps = []
            for app_label in specified_apps:
                try:
                    apps.get_app_config(app_label)
                    valid_apps.append(app_label)
                except LookupError:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠️  Warning: App '{app_label}' not found, skipping"
                        )
                    )
            return valid_apps

        return all_apps

    def _get_models_to_export(self, app_config, options):
        """Get list of models to export for an app."""
        models_to_export = []

        for model in app_config.get_models():
            model_name = model.__name__

            # Skip proxy models
            if model._meta.proxy:
                continue

            # Skip if excluding users and this is a user-related model
            if options.get('exclude_users'):
                if app_config.label == 'authentication' and model_name == 'User':
                    continue
                if 'User' in model_name:
                    continue

            # Skip audit logs unless included
            if not options.get('include_audit'):
                if 'AuditLog' in model_name or 'audit' in model_name.lower():
                    continue

            # Skip metrics unless included
            if not options.get('include_metrics'):
                if 'Metric' in model_name or 'metric' in model_name.lower():
                    continue
                if 'HealthCheck' in model_name:
                    continue

            # Skip execution histories unless included
            if not options.get('include_histories'):
                if 'Execution' in model_name and 'AgentExecution' not in model_name:
                    continue
                if 'History' in model_name:
                    continue

            models_to_export.append(model)

        return models_to_export

