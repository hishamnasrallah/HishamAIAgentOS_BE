"""
One-command script to export and prepare fixtures for deployment.
This combines export_initial_data with prepare_fixtures for convenience.
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
    print("  HISHAMOS - EXPORT & PREPARE FIXTURES FOR DEPLOYMENT")
    print("=" * 70)
    print()
    
    # Step 1: Export fixtures without users
    print("Step 1: Exporting fixtures (excluding users)...")
    print()
    
    fixtures_dir = backend_dir / 'initial_data' / 'fixtures'
    deployment_dir = fixtures_dir / 'deployment'
    
    try:
        call_command(
            'export_initial_data',
            output=str(fixtures_dir),
            exclude_users=True,
            verbosity=1
        )
    except Exception as e:
        print(f"❌ Export failed: {e}")
        sys.exit(1)
    
    print()
    print("Step 2: Preparing fixtures for deployment...")
    print()
    
    # Step 2: Prepare fixtures
    try:
        # Import and run preparer
        sys.path.insert(0, str(backend_dir / 'initial_data' / 'scripts'))
        from prepare_fixtures import FixturePreparer
        
        preparer = FixturePreparer(fixtures_dir, deployment_dir)
        stats = preparer.prepare_all()
        
        if stats['files_processed'] == 0:
            print("⚠️  No files were processed.")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Preparation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("=" * 70)
    print("  ✅ COMPLETE!")
    print("=" * 70)
    print()
    print("Deployment-ready fixtures are in:")
    print(f"   {deployment_dir}")
    print()
    print("To load them:")
    print(f"   python manage.py loaddata {deployment_dir}/*.json")
    print()

