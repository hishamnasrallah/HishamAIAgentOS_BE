"""
Unfake organizations migration and apply it properly.

Run: python manage.py shell
Then: exec(open('unfake_and_apply_organizations.py').read())
"""

from django.db import connection

# Remove the fake migration record
with connection.cursor() as cursor:
    cursor.execute("""
        DELETE FROM django_migrations 
        WHERE app = 'organizations' AND name = '0001_initial'
    """)
    print("✓ Removed fake organizations.0001_initial migration record")

print("\nNow run: python manage.py migrate organizations")
print("This will actually create the organizations tables.")


