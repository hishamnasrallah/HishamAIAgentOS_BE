"""
One-command script to load all deployment-ready fixtures.
This script loads fixtures from initial_data/fixtures/deployment/ directory.
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

if __name__ == '__main__':
    print("=" * 70)
    print("  HISHAMOS - LOAD DEPLOYMENT FIXTURES")
    print("=" * 70)
    print()
    
    fixtures_dir = backend_dir / 'initial_data' / 'fixtures' / 'deployment'
    
    if not fixtures_dir.exists():
        print(f"❌ Deployment fixtures directory not found: {fixtures_dir}")
        print()
        print("Please run first:")
        print("   python initial_data/scripts/prepare_and_export.py")
        sys.exit(1)
    
    # Get all JSON fixture files
    fixture_files = list(fixtures_dir.glob("*.json"))
    
    if not fixture_files:
        print(f"❌ No fixture files found in {fixtures_dir}")
        print()
        print("Please run first:")
        print("   python initial_data/scripts/prepare_and_export.py")
        sys.exit(1)
    
    print(f"📦 Found {len(fixture_files)} fixture file(s)")
    print(f"📁 Directory: {fixtures_dir}")
    print()
    print("Loading fixtures in order...")
    print()
    
    # Define loading order
    loading_order = [
        'integrations.json',
        'agents.json',
        'commands.json',
        'projects.json',
        'workflows.json',
        'chat.json',
        'results.json',
        'monitoring.json',
    ]
    
    # Load fixtures in order
    loaded_count = 0
    error_count = 0
    
    for fixture_name in loading_order:
        fixture_path = fixtures_dir / fixture_name
        
        if not fixture_path.exists():
            continue
        
        try:
            print(f"📥 Loading {fixture_name}...", end=' ')
            call_command('loaddata', str(fixture_path), verbosity=0)
            print("✅")
            loaded_count += 1
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
            error_count += 1
    
    # Also load any other fixtures not in the predefined order
    for fixture_file in fixture_files:
        if fixture_file.name not in loading_order:
            try:
                print(f"📥 Loading {fixture_file.name}...", end=' ')
                call_command('loaddata', str(fixture_file), verbosity=0)
                print("✅")
                loaded_count += 1
            except Exception as e:
                print(f"❌ Error: {str(e)[:100]}")
                error_count += 1
    
    print()
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"✅ Loaded: {loaded_count} fixture(s)")
    if error_count > 0:
        print(f"❌ Errors: {error_count} fixture(s)")
    print("=" * 70)
    print()
    
    if error_count == 0:
        print("✅ All fixtures loaded successfully!")
    else:
        print("⚠️  Some fixtures failed to load. Check errors above.")
        sys.exit(1)

