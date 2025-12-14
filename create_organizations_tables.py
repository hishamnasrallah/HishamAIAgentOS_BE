"""
Manually create organizations tables and mark migration as applied.

Run: python manage.py shell
Then: exec(open('create_organizations_tables.py').read())
"""

from django.db import connection
from django.utils import timezone

with connection.cursor() as cursor:
    # Check if organizations table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='organizations'
    """)
    org_table_exists = cursor.fetchone() is not None
    
    if not org_table_exists:
        print("Creating organizations tables...")
        
        # Create organizations table
        cursor.execute("""
            CREATE TABLE organizations (
                id TEXT NOT NULL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                slug VARCHAR(200) NOT NULL UNIQUE,
                description TEXT NOT NULL,
                status VARCHAR(20) NOT NULL,
                subscription_tier VARCHAR(50) NOT NULL,
                max_users INTEGER NOT NULL,
                max_projects INTEGER NOT NULL,
                subscription_start_date DATE NULL,
                subscription_end_date DATE NULL,
                settings TEXT NOT NULL,
                logo VARCHAR(500) NOT NULL,
                primary_color VARCHAR(7) NOT NULL,
                secondary_color VARCHAR(7) NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                created_by_id TEXT NULL,
                owner_id TEXT NULL,
                FOREIGN KEY (created_by_id) REFERENCES users(id),
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        """)
        
        # Create organization_members table
        cursor.execute("""
            CREATE TABLE organization_members (
                id TEXT NOT NULL PRIMARY KEY,
                organization_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role VARCHAR(50) NOT NULL,
                joined_at DATETIME NOT NULL,
                invited_by_id TEXT NULL,
                FOREIGN KEY (organization_id) REFERENCES organizations(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (invited_by_id) REFERENCES users(id),
                UNIQUE(organization_id, user_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX organizatio_slug_5b8b37_idx ON organizations(slug)")
        cursor.execute("CREATE INDEX organizatio_status_195db0_idx ON organizations(status)")
        cursor.execute("CREATE INDEX organizatio_owner_i_0051c7_idx ON organizations(owner_id)")
        cursor.execute("CREATE INDEX organizatio_created_8a4b5e_idx ON organizations(created_at)")
        cursor.execute("CREATE INDEX organizatio_organiz_324912_idx ON organization_members(organization_id, user_id)")
        cursor.execute("CREATE INDEX organizatio_organiz_a66366_idx ON organization_members(organization_id)")
        cursor.execute("CREATE INDEX organizatio_user_id_1a6a95_idx ON organization_members(user_id)")
        
        print("✓ Created organizations tables")
    else:
        print("✓ Organizations tables already exist")
    
    # Mark migration as applied
    cursor.execute("""
        SELECT COUNT(*) FROM django_migrations 
        WHERE app = 'organizations' AND name = '0001_initial'
    """)
    exists = cursor.fetchone()[0] > 0
    
    if not exists:
        from datetime import datetime
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES (?, ?, ?)
        """, ['organizations', '0001_initial', datetime.now()])
        print("✓ Marked organizations.0001_initial as applied")
    else:
        print("✓ Migration already marked as applied")

print("\nNow you can run: python manage.py migrate")

