"""
Django management command to load initial data fixtures.
Simple version - loads all fixtures from initial_data/fixtures.
"""

from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps


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

        # Define loading order to respect foreign key dependencies
        # Order: authentication → integrations → agents → commands → projects → workflows → chat → others
        loading_order = [
            'authentication.json',
            'integrations.json',
            'agents.json',
            'commands.json',
            'projects.json',
            'workflows.json',
            'chat.json',
        ]
        
        # Get all JSON fixture files
        all_fixture_files = list(fixtures_dir.glob("*.json"))
        
        # Sort by loading order, then alphabetically for any remaining files
        fixture_files = []
        for ordered_file in loading_order:
            matching = [f for f in all_fixture_files if f.name == ordered_file]
            if matching:
                fixture_files.extend(matching)
        
        # Add any remaining files not in the order list
        remaining = [f for f in all_fixture_files if f.name not in loading_order]
        fixture_files.extend(sorted(remaining))

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
        skipped_count = 0

        # Check if admin user exists (to skip authentication.json if needed)
        admin_exists = False
        try:
            User = apps.get_model('authentication', 'User')
            admin_exists = User.objects.filter(email='admin@hishamos.com').exists()
        except:
            pass

        for fixture_file in fixture_files:
            # Skip authentication.json if admin user already exists
            if fixture_file.name == 'authentication.json' and admin_exists:
                self.stdout.write(f"⏭️  {fixture_file.name}: Skipped (admin user already exists)", ending='')
                self.stdout.write("")
                skipped_count += 1
                continue

            try:
                self.stdout.write(f"📥 Loading {fixture_file.name}...", ending=' ')
                call_command('loaddata', str(fixture_file), verbosity=1)
                self.stdout.write(self.style.SUCCESS("✅"))
                loaded_count += 1
            except Exception as e:
                error_msg = str(e)
                # If it's a UNIQUE constraint error for users, skip it
                if 'authentication.json' in str(fixture_file) and 'UNIQUE constraint' in error_msg:
                    self.stdout.write(self.style.WARNING("⏭️  Skipped (user already exists)"))
                    skipped_count += 1
                elif 'foreign key' in error_msg.lower() or 'invalid foreign key' in error_msg.lower():
                    # Foreign key constraint - extract more details
                    self.stdout.write(self.style.ERROR(f"❌ Foreign key error"))
                    # Try to extract table and key info from error
                    if 'table' in error_msg.lower():
                        # Extract table name if possible
                        import re
                        table_match = re.search(r"table '(\w+)'", error_msg)
                        if table_match:
                            self.stdout.write(f"   Table: {table_match.group(1)}")
                    self.stdout.write(f"   Full error: {error_msg[:200]}")
                    error_count += 1
                else:
                    # Truncate long error messages
                    short_error = error_msg[:200] + "..." if len(error_msg) > 200 else error_msg
                    self.stdout.write(self.style.ERROR(f"❌ {short_error}"))
                    error_count += 1

        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 70)
        if error_count == 0:
            self.stdout.write(self.style.SUCCESS(f"[SUCCESS] All fixtures loaded!"))
            self.stdout.write(f"   ✅ Loaded: {loaded_count}")
            if skipped_count > 0:
                self.stdout.write(f"   ⏭️  Skipped: {skipped_count}")
        else:
            self.stdout.write(self.style.WARNING(f"[WARNING] Some fixtures failed to load"))
            self.stdout.write(f"   ✅ Loaded: {loaded_count}")
            if skipped_count > 0:
                self.stdout.write(f"   ⏭️  Skipped: {skipped_count}")
            self.stdout.write(f"   ❌ Errors: {error_count}")
        self.stdout.write("=" * 70)
        self.stdout.write("")

