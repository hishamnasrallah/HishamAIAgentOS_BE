"""
Django management command to load initial data fixtures.
Simple version - loads all fixtures from initial_data/fixtures.
"""

from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Load all initial data fixtures (simple version)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixtures-dir',
            type=str,
            default='initial_data/fixtures',
            help='Directory containing fixtures (default: initial_data/fixtures)'
        )

    def handle(self, *args, **options):
        fixtures_dir = Path(options['fixtures_dir'])

        self.stdout.write("=" * 70)
        self.stdout.write("  HISHAMOS - LOAD INITIAL DATA (SIMPLE)")
        self.stdout.write("=" * 70)
        self.stdout.write("")

        if not fixtures_dir.exists():
            self.stdout.write(
                self.style.ERROR(f"❌ Fixtures directory not found: {fixtures_dir}")
            )
            self.stdout.write("   Please run 'python manage.py export_initial_data' first")
            return

        # Get all JSON fixture files
        fixture_files = sorted(fixtures_dir.glob("*.json"))

        if not fixture_files:
            self.stdout.write(
                self.style.ERROR(f"❌ No fixture files found in {fixtures_dir}")
            )
            return

        self.stdout.write(f"📦 Found {len(fixture_files)} fixture file(s)")
        self.stdout.write("")
        self.stdout.write("Loading fixtures...")
        self.stdout.write("")

        loaded_count = 0
        error_count = 0

        for fixture_file in fixture_files:
            try:
                self.stdout.write(f"📥 Loading {fixture_file.name}...", ending=' ')
                call_command('loaddata', str(fixture_file), verbosity=0)
                self.stdout.write(self.style.SUCCESS("✅"))
                loaded_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
                error_count += 1

        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 70)
        if error_count == 0:
            self.stdout.write(self.style.SUCCESS(f"[SUCCESS] All fixtures loaded!"))
            self.stdout.write(f"   Files loaded: {loaded_count}")
        else:
            self.stdout.write(self.style.WARNING(f"[WARNING] Some fixtures failed to load"))
            self.stdout.write(f"   ✅ Loaded: {loaded_count}")
            self.stdout.write(f"   ❌ Errors: {error_count}")
        self.stdout.write("=" * 70)
        self.stdout.write("")

