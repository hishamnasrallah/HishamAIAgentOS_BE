"""
Helper script to export all database data as fixtures.
This is a convenience wrapper around the Django management command.
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
    print("  HISHAMOS - EXPORT ALL DATABASE DATA")
    print("=" * 70)
    print()
    print("This script will export all data from your database to JSON fixtures.")
    print("Output location: initial_data/fixtures/")
    print()

    # Export all data
    call_command('export_initial_data', verbosity=2)

    print()
    print("Export complete! Check the initial_data/fixtures/ directory.")

