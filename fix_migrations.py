"""
Fix migration history by marking organizations.0001_initial as applied.

Run: python manage.py shell
Then: exec(open('fix_migrations.py').read())
"""

from django.db import connection
from django.utils import timezone
from django.core.management import call_command

# Check if organizations migration exists in history
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT COUNT(*) FROM django_migrations 
        WHERE app = 'organizations' AND name = '0001_initial'
    """)
    exists = cursor.fetchone()[0] > 0
    
    if not exists:
        # Insert the migration record
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES (%s, %s, %s)
        """, ['organizations', '0001_initial', timezone.now()])
        print("✓ Marked organizations.0001_initial as applied")
    else:
        print("✓ organizations.0001_initial is already marked as applied")

print("\nNow you can run: python manage.py migrate")


