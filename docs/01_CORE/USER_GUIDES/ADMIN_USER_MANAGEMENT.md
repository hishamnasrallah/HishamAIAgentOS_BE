---
title: "Admin User Management Scripts"
description: "This directory contains utility scripts for managing the admin superuser."

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Developer
    - CTO / Technical Lead
  secondary:
    - Project Manager
    - Infrastructure

applicable_phases:
  primary:
    - Development

tags:
  - user-guide
  - admin
  - core

status: "active"
priority: "medium"
difficulty: "intermediate"
completeness: "100%"
quality_status: "draft"

estimated_read_time: "10 minutes"

version: "1.0"
last_updated: "2025-12-06"
last_reviewed: "2025-12-06"
review_frequency: "quarterly"

author: "Development Team"
maintainer: "Development Team"

related: []
see_also: []
depends_on: []
prerequisite_for: []

aliases: []

changelog:
  - version: "1.0"
    date: "2025-12-06"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---

# Admin User Management Scripts

This directory contains utility scripts for managing the admin superuser.

## Scripts

### 1. `create_superuser.py`
Creates a default superuser if it doesn't exist.

**Usage:**
```bash
python create_superuser.py
```

**Default Credentials:**
- Email: `admin@hishamos.com`
- Username: `admin`
- Password: `Amman123`
- Role: `admin` (superuser)

### 2. `reset_admin_password.py`
Resets the admin user password to the default password.

**Usage:**
```bash
python reset_admin_password.py
```

This will reset the password to `Amman123` and display the login URLs.

## Current Admin Credentials

```
Email:        admin@hishamos.com
Username:     admin
Password:     Amman123
Role:         admin
```

## Login URLs

- **Admin Panel:** http://localhost:8000/admin/
- **API Documentation:** http://localhost:8000/api/docs/
- **API Login Endpoint:** http://localhost:8000/api/v1/auth/login/

## Security Note

⚠️ **IMPORTANT:** These default credentials are for development only. 

**Before deploying to production:**
1. Change the admin password using Django admin or:
   ```bash
   python manage.py changepassword admin
   ```
2. Consider using environment variables for admin credentials
3. Enable 2FA for admin accounts
4. Use strong, unique passwords

## API Authentication

### Login via API

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@hishamos.com",
    "password": "Amman123"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "...",
    "email": "admin@hishamos.com",
    "username": "admin",
    "role": "admin",
    ...
  }
}
```

### Use Auth Token

Add to request headers:
```
Authorization: Bearer <access_token>
```

## Manual Superuser Creation

If you prefer to create a superuser manually:

```bash
python manage.py createsuperuser
```

Then follow the prompts to enter email, username, and password.
