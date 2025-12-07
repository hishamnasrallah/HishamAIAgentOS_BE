"""
Django management command to load initial data fixtures.
Simple version - loads all fixtures from initial_data/fixtures.
"""

import json
import tempfile
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

        # Get admin user ID from authentication.json (for replacing user references)
        admin_user_id_in_fixtures = None
        auth_file = fixtures_dir / 'authentication.json'
        if auth_file.exists():
            try:
                with open(auth_file, 'r', encoding='utf-8') as f:
                    auth_data = json.load(f)
                    if auth_data and len(auth_data) > 0:
                        admin_user_id_in_fixtures = auth_data[0].get('pk')
            except:
                pass

        # Get current admin user ID from database (if exists)
        admin_user = None
        try:
            User = apps.get_model('authentication', 'User')
            admin_user = User.objects.filter(email='admin@hishamos.com').first()
        except:
            pass

        for fixture_file in fixture_files:
            # Always load authentication.json (even if admin exists, it will be skipped by Django if duplicate)
            # But we need it to get the user ID for replacing references in other fixtures

            try:
                self.stdout.write(f"📥 Loading {fixture_file.name}...", ending=' ')
                
                # For authentication.json: load it (Django will skip if duplicate)
                if fixture_file.name == 'authentication.json':
                    try:
                        call_command('loaddata', str(fixture_file), verbosity=1)
                        self.stdout.write(self.style.SUCCESS("✅"))
                        loaded_count += 1
                    except Exception as e:
                        # If UNIQUE constraint, user already exists - that's OK
                        if 'UNIQUE constraint' in str(e):
                            self.stdout.write(self.style.WARNING("⏭️  Skipped (user already exists)"))
                            skipped_count += 1
                        else:
                            raise
                    # After loading authentication.json, refresh admin_user from database
                    try:
                        User = apps.get_model('authentication', 'User')
                        admin_user = User.objects.filter(email='admin@hishamos.com').first()
                    except:
                        pass
                    continue
                
                # For other fixtures: replace user IDs if needed
                if admin_user and admin_user_id_in_fixtures and str(admin_user.id) != str(admin_user_id_in_fixtures):
                    # Read fixture, replace user IDs, save to temp file
                    with open(fixture_file, 'r', encoding='utf-8') as f:
                        fixture_data = json.load(f)
                    
                    # Replace user references
                    admin_user_id_str = str(admin_user.id)
                    fixture_user_id_str = str(admin_user_id_in_fixtures)
                    
                    user_fields = ['owner', 'owner_id', 'created_by', 'created_by_id', 
                                 'assigned_to', 'assigned_to_id', 'user', 'user_id']
                    
                    for record in fixture_data:
                        fields = record.get('fields', {})
                        for field_name in user_fields:
                            if field_name in fields:
                                # Handle both string and UUID formats
                                field_value = str(fields[field_name]) if fields[field_name] is not None else None
                                if field_value == fixture_user_id_str:
                                    fields[field_name] = admin_user_id_str
                        # Handle ManyToMany
                        if 'members' in fields and fields['members']:
                            fields['members'] = [
                                admin_user_id_str if str(member_id) == fixture_user_id_str else member_id
                                for member_id in fields['members']
                            ]
                    
                    # Save to temp file and load from there
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_file:
                        json.dump(fixture_data, tmp_file, indent=2, ensure_ascii=False)
                        tmp_path = tmp_file.name
                    
                    try:
                        call_command('loaddata', tmp_path, verbosity=1)
                    finally:
                        Path(tmp_path).unlink(missing_ok=True)
                else:
                    # Load directly
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

