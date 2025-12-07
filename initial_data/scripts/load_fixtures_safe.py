"""
Safe fixture loading script that skips authentication.json if users exist.
This prevents conflicts when loading fixtures after setup_admin_user.
"""

import sys
import os
import django
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from django.core.management import call_command
from apps.authentication.models import User

if __name__ == '__main__':
    print("=" * 70)
    print("  HISHAMOS - SAFE FIXTURE LOADING")
    print("=" * 70)
    print()
    
    fixtures_dir = backend_dir / 'initial_data' / 'fixtures'
    
    if not fixtures_dir.exists():
        print(f"❌ Fixtures directory not found: {fixtures_dir}")
        sys.exit(1)
    
    # Check if users exist
    user_count = User.objects.count()
    has_users = user_count > 0
    
    if has_users:
        print(f"⚠️  Found {user_count} existing user(s) in database")
        print("   Will skip authentication.json to avoid conflicts")
        print()
    
    # Define fixture loading order
    fixtures_to_load = [
        'integrations.json',
        'agents.json',
        'commands.json',
        'projects.json',
        'workflows.json',
        'chat.json',
        'results.json',
        'monitoring.json',
    ]
    
    # Skip authentication.json if users exist
    if not has_users:
        fixtures_to_load.insert(0, 'authentication.json')
        print("📦 Loading all fixtures including users...")
    else:
        print("📦 Loading fixtures (skipping authentication.json)...")
    
    print()
    
    loaded_count = 0
    skipped_count = 0
    error_count = 0
    
    for fixture_file in fixtures_to_load:
        fixture_path = fixtures_dir / fixture_file
        
        if not fixture_path.exists():
            print(f"⏭️  {fixture_file}: Not found (skipping)")
            skipped_count += 1
            continue
        
        try:
            print(f"📥 Loading {fixture_file}...", end=' ')
            call_command('loaddata', str(fixture_path), verbosity=0)
            print("✅")
            loaded_count += 1
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            error_count += 1
    
    print()
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"✅ Loaded: {loaded_count} fixtures")
    print(f"⏭️  Skipped: {skipped_count} fixtures")
    if error_count > 0:
        print(f"❌ Errors: {error_count} fixtures")
    print()
    
    if has_users:
        print("💡 Tip: If you need to load additional users, edit")
        print("   authentication.json to use different usernames/emails")
        print("   or load it manually after checking for conflicts.")
    
    print()
    print("✅ Fixture loading complete!")

