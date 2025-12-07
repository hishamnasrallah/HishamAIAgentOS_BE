#!/usr/bin/env python
"""
Script to verify superuser credentials and reset password if needed.
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

def reset_admin_password():
    """Reset admin password to Amman123."""
    
    email = 'admin@hishamos.com'
    username = 'admin'
    new_password = 'Amman123'
    
    # Get user
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print(f'[ERROR] User with email "{email}" not found!')
        
        # Create new superuser
        print('[INFO] Creating new superuser...')
        user = User.objects.create_superuser(
            email=email,
            username=username,
            password=new_password,
            first_name='Admin',
            last_name='User',
            role='admin',
        )
        print('[SUCCESS] Superuser created!')
        print_user_info(user, new_password)
        return
    
    # Reset password
    user.set_password(new_password)
    user.save()
    
    print('[SUCCESS] Password reset successfully!')
    print_user_info(user, new_password)

def print_user_info(user, password):
    """Print user information."""
    print('\n' + '='*60)
    print('SUPERUSER CREDENTIALS')
    print('='*60)
    print(f'Email:        {user.email}')
    print(f'Username:     {user.username}')
    print(f'Password:     {password}')
    print(f'Role:         {user.role}')
    print(f'Is superuser: {user.is_superuser}')
    print(f'Is staff:     {user.is_staff}')
    print(f'Is active:    {user.is_active}')
    print('='*60)
    print('\nLOGIN URLS:')
    print('  Admin Panel: http://localhost:8000/admin/')
    print('  API Docs:    http://localhost:8000/api/docs/')
    print('  API Login:   http://localhost:8000/api/v1/auth/login/')
    print('='*60)

if __name__ == '__main__':
    reset_admin_password()
