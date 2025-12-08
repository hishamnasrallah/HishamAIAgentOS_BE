# Dynamic Audit System Documentation

## Overview

The audit system is **100% dynamic** and requires **NO code changes** when:
- Adding new models
- Adding new applications
- Creating new audit configurations
- Modifying audit rules

## How It Works

### 1. Automatic Model Detection

The system automatically detects and audits **ALL models** in your Django project:

- **Signals**: Django signals (`post_save`, `pre_save`, `pre_delete`) automatically catch ALL model operations
- **No Hardcoding**: No model names are hardcoded in the code
- **Dynamic Detection**: Uses Django's `ContentType` to get model names dynamically
- **Exclusions Only**: Only system models (Session, LogEntry, etc.) are excluded

### 2. Dynamic Resource Type Detection

The middleware automatically extracts resource types from URLs:

- **Pattern Matching**: Detects resource types from URL patterns (e.g., `/api/v1/users/123/` → `user`)
- **No Hardcoding**: No hardcoded resource type lists
- **Works for Any Model**: Automatically works for new models you add

### 3. Dynamic Audit Configurations

Audit configurations are stored in the database and evaluated dynamically:

- **Database-Driven**: All rules are in `AuditConfiguration` model
- **No Code Changes**: Add/modify configurations via Django admin or API
- **Flexible Filtering**: Filter by action, resource type, user, IP, etc.
- **Priority-Based**: Multiple configurations can be active simultaneously

### 4. Automatic Change Tracking

The system automatically tracks changes for ALL models:

- **Pre-Save Signal**: Captures old values before save
- **Post-Save Signal**: Compares old vs new values
- **Field-Level Changes**: Tracks which fields changed and their before/after values
- **Complete State**: Stores full `old_values` and `new_values` for each change

## Adding New Models

### Step 1: Create Your Model

```python
# apps/myapp/models.py
from django.db import models

class MyNewModel(models.Model):
    name = models.CharField(max_length=100)
    # ... other fields
```

### Step 2: That's It!

The audit system will automatically:
- ✅ Detect the new model
- ✅ Log all create/update/delete operations
- ✅ Track field-level changes
- ✅ Store old and new values
- ✅ Work with audit configurations

**No code changes needed!**

## Adding New Applications

### Step 1: Add to INSTALLED_APPS

```python
# core/settings/base.py
INSTALLED_APPS = [
    # ... existing apps
    'apps.mynewapp',
]
```

### Step 2: That's It!

The audit system will automatically:
- ✅ Detect all models in the new app
- ✅ Start auditing them
- ✅ Work with existing configurations

**No code changes needed!**

## Creating Audit Configurations

### Via Django Admin

1. Go to `/admin/monitoring/auditconfiguration/`
2. Click "Add Audit Configuration"
3. Configure your rules:
   - **Actions**: Which actions to audit (create, update, delete)
   - **Resource Types**: Which models to audit (e.g., "user", "project")
   - **Users**: Which users to audit
   - **IP Addresses**: Which IPs to audit
   - **Exclusions**: What to exclude
4. Save

### Via API

```python
POST /api/v1/monitoring/audit-configurations/
{
    "name": "Audit All User Changes",
    "configuration_type": "include",
    "is_active": true,
    "audit_actions": ["create", "update", "delete"],
    "audit_resource_types": ["user"],
    "audit_all_users": true,
    "audit_all_ips": true
}
```

### Dynamic Configuration Examples

**Example 1: Audit only admin actions**
```json
{
    "name": "Admin Actions Only",
    "audit_actions": ["create", "update", "delete"],
    "audit_all_users": false,
    "audit_users": ["admin-user-id"],
    "audit_all_resource_types": true
}
```

**Example 2: Exclude specific models**
```json
{
    "name": "Exclude System Models",
    "exclude_resource_types": ["session", "logentry"],
    "audit_all_actions": true,
    "audit_all_users": true
}
```

**Example 3: Audit only from specific IPs**
```json
{
    "name": "Office IPs Only",
    "audit_all_ips": false,
    "audit_ips": ["192.168.1.0/24", "10.0.0.0/8"],
    "audit_all_actions": true
}
```

## How Configurations Are Evaluated

1. **Priority Order**: Configurations are evaluated by priority (higher first)
2. **Include Logic**: If any configuration says "include", the action is audited
3. **Exclude Logic**: Exclusions take precedence over includes
4. **Default Behavior**: If no configurations exist, everything is audited

## System Architecture

```
┌─────────────────┐
│   Django App    │
│  (Your Models)  │
└────────┬────────┘
         │
         │ Model.save()
         │
         ▼
┌─────────────────┐
│  Django Signals  │
│ (post_save, etc)│
└────────┬────────┘
         │
         │ Detect model dynamically
         │
         ▼
┌─────────────────┐
│  Audit Logger    │
│  (audit.py)      │
└────────┬────────┘
         │
         │ Check configurations dynamically
         │
         ▼
┌─────────────────┐
│  AuditConfig     │
│  (Database)      │
└────────┬────────┘
         │
         │ Evaluate rules
         │
         ▼
┌─────────────────┐
│   Audit Log      │
│   (Database)     │
└─────────────────┘
```

## Key Features

### ✅ 100% Dynamic
- No hardcoded model names
- No hardcoded resource types
- No code changes needed for new models

### ✅ Automatic
- Automatically detects all models
- Automatically tracks changes
- Automatically applies configurations

### ✅ Flexible
- Database-driven configurations
- Multiple active configurations
- Priority-based evaluation

### ✅ Comprehensive
- Tracks all model operations
- Field-level change tracking
- Complete before/after state

## Testing

To verify the system is working:

1. **Create a new model** in any app
2. **Create/update/delete** an instance
3. **Check audit logs** at `/admin/monitoring/auditlog/`
4. **Verify** the log entry was created automatically

## Troubleshooting

### No audit logs being created?

1. Check if audit configurations exist and are active
2. Check if the model is in `EXCLUDED_MODELS` (shouldn't be unless it's a system model)
3. Check Django signals are connected (should be automatic)
4. Check middleware is in `MIDDLEWARE` list

### Configurations not working?

1. Check configuration `is_active` is `True`
2. Check configuration priority (higher = evaluated first)
3. Check if exclusions are preventing logging
4. Verify configuration rules match your test case

## Summary

The audit system is **completely dynamic**:
- ✅ Works with any model automatically
- ✅ Works with any application automatically
- ✅ Configurations are database-driven
- ✅ No code changes needed for new models/apps/configurations

Just create your models and configurations - the system handles the rest!

