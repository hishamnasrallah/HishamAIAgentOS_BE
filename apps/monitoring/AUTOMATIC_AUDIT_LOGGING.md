# Automatic Audit Logging System

## Overview

The automatic audit logging system provides comprehensive audit trail coverage without requiring manual code changes for each new model or API endpoint. It uses a combination of middleware and Django signals to automatically capture all operations.

## Architecture

### 1. Middleware-Based API Logging (`AuditLoggingMiddleware`)

**Location**: `apps/monitoring/middleware.py`

**What it does**:
- Intercepts all API requests (POST, PUT, PATCH, DELETE)
- Automatically extracts resource type and ID from URL patterns
- Logs successful operations (2xx status codes)
- Captures request/response data for audit trail
- Stores user context in thread-local storage for signals

**How it works**:
- Processes requests in `process_request()` to store user context
- Processes responses in `process_response()` to log operations
- Extracts resource info from URL patterns (e.g., `/api/v1/users/123/` → resource_type='user', resource_id='123')
- Maps HTTP methods to audit actions (POST→create, PUT/PATCH→update, DELETE→delete)

**Configuration**:
- Added to `MIDDLEWARE` in `settings/base.py`
- Positioned after authentication middleware to have access to user

### 2. Signal-Based Model Logging (`signals.py`)

**Location**: `apps/monitoring/signals.py`

**What it does**:
- Automatically logs all model create/update/delete operations
- Works for any Django model without code changes
- Captures before/after changes for updates
- Captures full object data for deletions

**How it works**:
- Uses `post_save` signal to log create/update operations
- Uses `pre_delete` signal to log delete operations
- Automatically excludes system models (Session, LogEntry, etc.)
- Gets user context from thread-local storage (set by middleware)

**Excluded Models**:
- Session
- LogEntry (Django admin log)
- ContentType
- Permission
- Group
- AuditLog (don't audit audit logs)
- AuditConfiguration (don't audit configurations)
- SystemMetric
- HealthCheck

### 3. Audit Configuration System

**Location**: `apps/monitoring/models.py` (AuditConfiguration model)

**What it does**:
- Filters what gets audited based on active configurations
- Supports fine-grained control (actions, resource types, users, IPs)
- Multiple configurations can be active simultaneously
- Priority-based evaluation (higher priority = evaluated first)

**How it works**:
- `AuditLogger.should_audit()` checks all active configurations
- If any configuration matches, the action is audited
- Exclusions take precedence over inclusions
- If no configurations exist, everything is audited (backward compatibility)

## Benefits

1. **Zero Code Changes Required**: New models and APIs are automatically audited
2. **Comprehensive Coverage**: Captures all operations (API + Django Admin + direct model saves)
3. **Configurable**: Use audit configurations to control what gets logged
4. **Non-Intrusive**: Failures in audit logging don't break the application
5. **User Context**: Automatically captures user who performed the action
6. **Change Tracking**: Captures before/after values for updates

## Usage

### Loading Default Configurations

```bash
python manage.py load_default_audit_configurations
```

This creates 10 pre-configured audit configurations covering common scenarios:
- Default - Audit Everything
- GDPR Compliance
- Security & Access Control
- User Management
- System Configuration Changes
- Financial Transactions
- Data Access Only
- Minimal Audit - Critical Actions Only
- API Operations Only
- External Access Only

### Managing Audit Configurations

**Via Django Admin**:
- Go to `/admin/monitoring/auditconfiguration/`
- Create, edit, activate/deactivate configurations

**Via API**:
- `GET /api/v1/monitoring/audit-configs/` - List configurations
- `POST /api/v1/monitoring/audit-configs/` - Create configuration
- `PATCH /api/v1/monitoring/audit-configs/{id}/` - Update configuration
- `DELETE /api/v1/monitoring/audit-configs/{id}/` - Delete configuration

**Via Frontend**:
- Go to `/admin/audit-configurations`
- Manage configurations through the UI

### Viewing Audit Logs

**Via Django Admin**:
- Go to `/admin/monitoring/auditlog/`
- View, search, and filter audit logs

**Via API**:
- `GET /api/v1/monitoring/audit/` - List audit logs
- `GET /api/v1/monitoring/audit/{id}/` - Get specific audit log

**Via Frontend**:
- Audit logs can be viewed in the admin dashboard (to be implemented)

## How It Works Together

1. **API Request Flow**:
   ```
   Request → Middleware (stores user) → View → Model Save → Signal (logs) → Response → Middleware (logs API call)
   ```

2. **Django Admin Flow**:
   ```
   Admin Save → save_model (stores user) → Model Save → Signal (logs) → Response
   ```

3. **Direct Model Save Flow**:
   ```
   Model Save → Signal (logs, if user in thread-local)
   ```

## Configuration Examples

### Example 1: Audit All User Operations

```python
{
    "name": "User Management",
    "audit_actions": ["create", "update", "delete"],
    "audit_resource_types": ["user"],
    "audit_all_users": True,
    "is_active": True
}
```

### Example 2: GDPR Compliance - Data Access Only

```python
{
    "name": "GDPR Data Access",
    "audit_actions": ["read"],
    "audit_resource_types": ["user", "project"],
    "include_changes": False,
    "is_active": True
}
```

### Example 3: Exclude Specific Actions

```python
{
    "name": "Exclude Reads",
    "audit_actions": ["create", "update", "delete"],
    "exclude_actions": ["read"],
    "is_active": True
}
```

## Performance Considerations

- Audit logging is asynchronous-friendly (can be moved to background tasks)
- Failed audit logs don't break the application
- Signals are lightweight and only fire for write operations
- Middleware only processes write operations (POST, PUT, PATCH, DELETE)

## Future Enhancements

1. **Async Logging**: Move audit logging to background tasks for better performance
2. **Compression**: Compress old audit logs
3. **Retention Policies**: Automatic cleanup based on retention periods
4. **Real-time Alerts**: Alert on specific audit events
5. **Analytics**: Dashboard for audit log analytics

