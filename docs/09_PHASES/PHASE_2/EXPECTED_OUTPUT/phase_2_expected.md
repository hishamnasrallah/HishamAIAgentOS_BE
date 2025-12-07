---
title: "Phase 2: Authentication & Authorization - Expected Output"
description: "- [x] JWT authentication working"

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Project Manager
    - CTO / Technical Lead
  secondary:
    - All

applicable_phases:
  primary:
    - Development

tags:
  - phase-2
  - core
  - phase

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

# Phase 2: Authentication & Authorization - Expected Output

## Success Criteria
- [x] JWT authentication working
- [x] User registration/login/logout functional
- [x] Token refresh mechanism
- [x] API key authentication
- [x] RBAC with 4 roles (admin, manager, developer, viewer)
- [x] Permission classes working

---

## API Endpoints Expected

| Method | Endpoint | Expected Response | Status |
|--------|----------|-------------------|--------|
| POST | /api/v1/auth/register/ | `{"user": {...}, "access": "...", "refresh": "..."}` | ✅ |
| POST | /api/v1/auth/login/ | `{"access": "...", "refresh": "..."}` | ✅ |
| POST | /api/v1/auth/logout/ | `{"message": "Successfully logged out"}` | ✅ |
| POST | /api/v1/auth/token/refresh/ | `{"access": "new-token"}` | ✅ |
| GET | /api/v1/auth/me/ | `{"id": "...", "username": "...", "role": "..."}` | ✅ |

---

## Test Scenarios

### Scenario 1: User Registration

**Execution:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "role": "developer"
  }'
```

**Expected Output:**
```json
{
  "user": {
    "id": "uuid-here",
    "username": "testuser",
    "email": "test@example.com",
    "role": "developer",
    "is_active": true
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Validation:**
- User created in database
- Password hashed (not plain text)
- JWT tokens returned
- Tokens are valid

---

### Scenario 2: User Login

**Execution:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

**Expected Output:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "username": "testuser",
    "role": "developer"
  }
}
```

**Validation:**
- Correct credentials accepted
- Invalid credentials rejected with 401
- Tokens can be decoded
- User info included

---

### Scenario 3: Token Refresh

**Execution:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

**Expected Output:**
```json
{
  "access": "new-access-token-here"
}
```

**Validation:**
- New access token generated
- Refresh token still valid
- Old access token expires

---

### Scenario 4: Protected Endpoint Access

**Execution:**
```bash
# Without token (should fail)
curl http://localhost:8000/api/v1/auth/me/

# With token (should succeed)
curl http://localhost:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Expected Output:**

Without token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

With token:
```json
{
  "id": "uuid",
  "username": "testuser",
  "email": "test@example.com",
  "role": "developer"
}
```

**Validation:**
- Unauthenticated requests blocked
- Valid tokens grant access
- User info retrieved correctly

---

### Scenario 5: Role-Based Access Control

**Test Setup:**
Create users with different roles:
- admin_user (role: admin)
- manager_user (role: manager)
- dev_user (role: developer)
- viewer_user (role: viewer)

**Execution:**
```python
# Test permission hierarchy
from apps.authentication.permissions import IsAdmin, IsManagerOrAdmin

# Admin can access everything
admin_request = create_request_with_role('admin')
assert IsAdmin().has_permission(admin_request, None) == True

# Manager can access manager or below
manager_request = create_request_with_role('manager')
assert IsManagerOrAdmin().has_permission(manager_request, None) == True

# Viewer has limited access
viewer_request = create_request_with_role('viewer')
assert IsAdmin().has_permission(viewer_request, None) == False
```

**Expected Behavior:**
- Admins: Full access
- Managers: Manage projects, view reports
- Developers: Edit code, view projects
- Viewers: Read-only access

**Validation:**
- Permission classes enforce hierarchy
- Unauthorized actions return 403
- Role changes reflected immediately

---

### Scenario 6: API Key Authentication

**Execution:**
```bash
# Generate API key for user
curl -X POST http://localhost:8000/api/v1/auth/api-key/generate/ \
  -H "Authorization: Bearer jwt-token"

# Use API key
curl http://localhost:8000/api/v1/some-endpoint/ \
  -H "X-API-Key: generated-api-key-here"
```

**Expected Output:**
```json
{
  "api_key": "sk_test_abc123...",
  "created_at": "2024-12-01T12:00:00Z"
}
```

**Validation:**
- API key generated and stored
- API key authenticates requests
- API key can be revoked

---

## Security Validation

### Password Security
```python
from django.contrib.auth.hashers import check_password

user = User.objects.get(username='testuser')
# Password should be hashed
assert not user.password == 'SecurePass123!'
assert user.password.startswith('pbkdf2_sha256$')
assert check_password('SecurePass123!', user.password) == True
```

### JWT Token Validation
```python
import jwt
from django.conf import settings

token = "access-token-here"
decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
assert 'user_id' in decoded
assert 'exp' in decoded  # Expiration
```

---

## Final Checklist

- [x] User registration creates valid users
- [x] Passwords are hashed (never plain text)
- [x] JWT tokens generated correctly
- [x] Token refresh mechanism works
- [x] Protected endpoints require auth
- [x] RBAC enforces role hierarchy
- [x] API key authentication functional
- [x] 401 returned for unauthenticated
- [x] 403 returned for unauthorized
- [x] Swagger UI shows auth endpoints

---

*Phase 2 Expected Output - Version 1.0*
