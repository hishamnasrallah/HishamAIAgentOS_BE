#!/usr/bin/env python
"""
Script to create a superuser for HishamOS.
This creates an admin user with predefined credentials.
"""
import os
import sys
import django
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    """Create superuser if it doesn't exist."""
    
    email = 'admin@hishamos.com'
    username = 'admin'
    password = 'Amman123'
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        print(f'[!] User with email "{email}" already exists!')
        user = User.objects.get(email=email)
        print(f'    Username: {user.username}')
        print(f'    Role: {user.role}')
        print(f'    Is superuser: {user.is_superuser}')
        
        # Ask if want to update password
        print('\n[OK] User exists. Skipping creation.')
        return
    
    # Check if username exists
    if User.objects.filter(username=username).exists():
        print(f'[ERROR] User with username "{username}" already exists!')
        return
    
    # Create superuser
    try:
        user = User.objects.create_superuser(
            email=email,
            username=username,
            password=password,
            first_name='Admin',
            last_name='User',
            role='admin',
        )
        
        print('[SUCCESS] Superuser created successfully!')
        print(f'   Email: {email}')
        print(f'   Username: {username}')
        print(f'   Password: {password}')
        print(f'   Role: {user.role}')
        print(f'\n[LOGIN] Admin Panel: http://localhost:8000/admin/')
        print(f'[LOGIN] API Login: http://localhost:8000/api/v1/auth/login/')
        
    except Exception as e:
        print(f'[ERROR] Error creating superuser: {e}')
        sys.exit(1)

if __name__ == '__main__':
    print('='*60)
    print('HishamOS - Superuser Creation Script')
    print('='*60)
    create_superuser()
    print('='*60)
