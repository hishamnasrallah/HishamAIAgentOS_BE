"""
Script to fix migration history by marking organizations.0001_initial as applied.

Run this with: python manage.py shell
Then copy and paste the code below into the shell.
"""

from django.db import connection
from django.utils import timezone

with connection.cursor() as cursor:
    # Check if organizations.0001_initial is already recorded
    cursor.execute("""
        SELECT COUNT(*) FROM django_migrations 
        WHERE app = 'organizations' AND name = '0001_initial'
    """)
    exists = cursor.fetchone()[0] > 0
    
    if not exists:
        # Insert the migration record
        # For SQLite, use ? placeholder
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES (?, ?, ?)
        """, ['organizations', '0001_initial', timezone.now()])
        print("✓ Marked organizations.0001_initial as applied")
    else:
        print("✓ organizations.0001_initial is already marked as applied")

