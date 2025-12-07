---
title: "Phase 2: Authentication & Authorization - Complete Documentation"
description: "**Status:** ✅ 100% COMPLETE"

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

# Phase 2: Authentication & Authorization - Complete Documentation

**Status:** ✅ 100% COMPLETE  
**Duration:** Week 5  
**Completion Date:** November 2024

---

## 🎯 Business Requirements

### Objective
Implement secure authentication and authorization system supporting JWT tokens, API keys, role-based access control, and 2FA.

### Success Criteria
- ✅ User registration and login functional
- ✅ JWT token-based authentication working
- ✅ API key authentication for external integrations
- ✅ Role-based permissions enforced
- ✅ Password reset flow operational
- ✅ 2FA ready (implementation optional)

---

## 🔧 Technical Specifications

### Authentication Methods

**1. JWT (JSON Web Tokens)**
- Access tokens: 30 minutes expiry
- Refresh tokens: 30 days expiry
- Automatic refresh mechanism

**2. API Keys** 
- Long-lived tokens for external systems
- Rate limiting per key
- Expiration dates configurable

**3. Role-Based Access Control (RBAC)**
- Admin: Full system access
- Manager: Project and team management
- Developer: Code and task execution
- Viewer: Read-only access

---

## 💻 Implementation Details

### JWT Configuration

**`core/settings/base.py`:**
```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': env('JWT_SECRET_KEY'),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'apps.authentication.authentication.APIKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Authentication Views

**`apps/authentication/views.py`:**
```python
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

class AuthViewSet(viewsets.GenericViewSet):
    """Authentication endpoints."""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """User registration."""
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login."""
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(email=email, password=password)
        if not user:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
```

### API Key Authentication

**`apps/authentication/authentication.py`:**
```python
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import APIKey

class APIKeyAuthentication(BaseAuthentication):
    """Custom API Key authentication."""
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            return None  # Let other auth methods try
        
        try:
            key_obj = APIKey.objects.select_related('user').get(
                key=api_key,
                is_active=True
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')
        
        # Check expiration
        if key_obj.expires_at and key_obj.expires_at < timezone.now():
            raise AuthenticationFailed('API key expired')
        
        # Update last used
        key_obj.last_used_at = timezone.now()
        key_obj.save(update_fields=['last_used_at'])
        
        return (key_obj.user, key_obj)
```

### Custom Permissions

**`apps/authentication/permissions.py`:**
```python
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Only admins can access."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsManagerOrAdmin(BasePermission):
    """Managers and admins can access."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'manager']

class IsOwnerOrAdmin(BasePermission):
    """Object owner or admin can access."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj.user == request.user
```

---

## ✅ Testing & Verification

### API Endpoint Tests (Swagger UI)

**Registration:**
```bash
POST /api/v1/auth/register/
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "SecurePass123!",
  "first_name": "Test",
  "last_name": "User"
}

# Response: 201 Created
{
  "user": {...},
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
✅ PASS
```

**Login:**
```bash
POST /api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

# Response: 200 OK
{
  "user": {...},
  "tokens": {...}
}
✅ PASS
```

**Token Refresh:**
```bash
POST /api/v1/auth/refresh/
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Response: 200 OK
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
✅ PASS
```

**Authenticated Request:**
```bash
GET /api/v1/agents/
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

# Response: 200 OK
✅ PASS
```

**API Key Request:**
```bash
GET /api/v1/agents/
Headers:
  X-API-Key: hak_1234567890abcdef

# Response: 200 OK
✅ PASS
```

### Permission Tests

```python
# Test: Admin can access everything
client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
response = client.get('/api/v1/users/')
assert response.status_code == 200  # ✅

# Test: Viewer cannot create
client.credentials(HTTP_AUTHORIZATION=f'Bearer {viewer_token}')
response = client.post('/api/v1/agents/', data={...})
assert response.status_code == 403  # ✅

# Test: Manager can manage projects
client.credentials(HTTP_AUTHORIZATION=f'Bearer {manager_token}')
response = client.post('/api/v1/projects/', data={...})
assert response.status_code == 201  # ✅
```

---

## 🚀 Deployment

### Security Configuration

**Production settings:**
```python
# Secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECRET_KEY_SECURE = True

# HTTPS redirect
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Security headers
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### Environment Variables

```bash
# JWT secrets
JWT_SECRET_KEY=<random-256-bit-key>
JWT_ALGORITHM=HS256

# Admin credentials
ADMIN_EMAIL=admin@hishamos.com
ADMIN_PASSWORD=<secure-password>
```

---

## 📚 Key Files Created

**Authentication:**
- `apps/authentication/views.py` (350 lines)
- `apps/authentication/serializers.py` (200 lines)
- `apps/authentication/authentication.py` (100 lines)
- `apps/authentication/permissions.py` (80 lines)
- `apps/authentication/urls.py` (30 lines)

**Tests:**
- `apps/authentication/tests/test_auth.py` (250 lines)
- `apps/authentication/tests/test_permissions.py` (150 lines)

---

## 📚 Related Documents & Source Files

### 🎯 Business Requirements
**User Management & Security:**
- `docs/06_PLANNING/01_BA_Artifacts.md` - User management and security requirements
- `docs/hishamos_admin_management_screens.md` - **CRITICAL** User permissions management UI requirements

### 🔧 Technical Specifications
**Authentication Architecture:**
- `docs/06_PLANNING/03_Technical_Architecture.md` - Security architecture and auth patterns
- `docs/06_PLANNING/06_Full_Technical_Reference.md` - Authentication technical reference

**Detailed Design:**
- `docs/hishamos_complete_design_part2.md` - Backend authentication implementation
- `docs/hishamos_complete_design_part3.md` - API security design and JWT implementation

### 💻 Implementation Guidance
**Primary Implementation Plan:**
- `docs/06_PLANNING/IMPLEMENTATION/implementation_plan.md`:
  - **Lines 176-181**: JWT configuration (access/refresh tokens)
  - **Lines 232-235**: Authentication packages (djangorestframework-simplejwt, pyotp)
  - **Lines 301-396**: Custom User model (extends AbstractBaseUser, includes 2FA)
  - **Lines 398-421**: APIKey model for external integrations

**Master Plan:**
- `docs/06_PLANNING/MASTER_DEVELOPMENT_PLAN.md` - Lines 44-61 cover authentication requirements

### 🔐 Security & Compliance
**Security Documentation:**
- `docs/hishamos_critical_gaps_solutions.md` - Security gaps, vulnerabilities, and mitigations
- implementation_plan.md Lines 253-256: HashiCorp Vault for secrets (production)

**RBAC Requirements:**
- hishamos_admin_management_screens.md: Role-based access control UI and logic

### 🧪 Testing Documentation
**API Testing:**
- `docs/API_DOCUMENTATION_FIXES.md` - API documentation and testing guidelines
- `docs/PHASE_3_TESTING_GUIDE.md` - Testing methodologies (applicable to auth endpoints)

### ✅ Verification & Completion
**Completion Documentation:**
- `docs/WALKTHROUGH.md` - Lines 30-42 document Phase 2 authentication completion
- All auth endpoints verified via Swagger UI

---

## ✅ Phase Completion

**Deliverables:**
- ✅ JWT authentication functional
- ✅ API key system implemented
- ✅ RBAC operational with 4 roles
- ✅ All auth endpoints tested via Swagger
- ✅ Permission system working
- ✅ Security best practices applied

**Test Results:** 100% passing  
**Verified By:** Development Team  
**Date:** November 2024

**Next Phase:** [Phase 3: AI Platform Integration](./phase_3_detailed.md)

---

*Document Version: 1.0*
