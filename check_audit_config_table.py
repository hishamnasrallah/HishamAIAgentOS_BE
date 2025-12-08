"""
Quick script to check if audit_configurations table exists.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_configurations';")
result = cursor.fetchone()

if result:
    print("✓ Table 'audit_configurations' exists!")
    cursor.execute("SELECT COUNT(*) FROM audit_configurations;")
    count = cursor.fetchone()[0]
    print(f"  - Contains {count} records")
else:
    print("✗ Table 'audit_configurations' does NOT exist!")
    print("  - Migration needs to be applied")

