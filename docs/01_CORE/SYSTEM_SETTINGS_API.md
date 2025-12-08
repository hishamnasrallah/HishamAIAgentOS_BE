# System Settings & Feature Flags API Documentation

**Last Updated:** December 2024  
**Base URL:** `/api/v1/core/`  
**Authentication:** Required (JWT or API Key)

---

## 📋 Overview

The System Settings and Feature Flags APIs allow administrators to manage system-wide configuration and feature toggles. These APIs are part of the Core app and provide centralized configuration management.

---

## ⚙️ System Settings API

Base URL: `/api/v1/core/settings/`

### Model Overview

System Settings store key-value pairs with typed values:

- **Value Types:** `string`, `integer`, `float`, `boolean`, `json`
- **Categories:** `general`, `security`, `performance`, `notifications`, `integrations`
- **Access Control:** Public settings visible to all authenticated users, private settings admin-only

### Endpoints

#### List Settings

```http
GET /api/v1/core/settings/
```

**Query Parameters:**
- `category` - Filter by category
- `is_public` - Filter by public status
- `search` - Search in key/description
- `ordering` - Sort order

**Response:**
```json
[
  {
    "id": "uuid",
    "key": "max_file_upload_size",
    "value": "10485760",
    "typed_value": 10485760,
    "value_type": "integer",
    "category": "general",
    "description": "Maximum file upload size in bytes",
    "is_public": true,
    "created_at": "2024-12-01T02:42:21.103Z",
    "updated_at": "2024-12-06T05:54:04.773Z",
    "updated_by": "uuid",
    "updated_by_email": "admin@hishamos.com"
  }
]
```

#### Get Setting

```http
GET /api/v1/core/settings/{id}/
```

#### Create Setting (Admin Only)

```http
POST /api/v1/core/settings/
Content-Type: application/json

{
  "key": "new_setting_key",
  "value": "setting_value",
  "value_type": "string",
  "category": "general",
  "description": "Setting description",
  "is_public": false
}
```

#### Update Setting (Admin Only)

```http
PATCH /api/v1/core/settings/{id}/
Content-Type: application/json

{
  "value": "new_value"
}
```

#### Delete Setting (Admin Only)

```http
DELETE /api/v1/core/settings/{id}/
```

#### Get Settings by Category

```http
GET /api/v1/core/settings/by_category/
```

Returns settings grouped by category.

#### Reset Setting to Default (Admin Only)

```http
POST /api/v1/core/settings/{id}/reset_to_default/
```

---

## 🚩 Feature Flags API

Base URL: `/api/v1/core/feature-flags/`

### Model Overview

Feature Flags enable/disable features with role and user-based access control:

- **Access Control:** Role-based (`enabled_for_roles`) and user-specific (`enabled_for_users`)
- **Empty arrays:** Mean "all roles" or "all users"

### Endpoints

#### List Feature Flags

```http
GET /api/v1/core/feature-flags/
```

**Query Parameters:**
- `is_enabled` - Filter by enabled status
- `search` - Search in key/name/description
- `ordering` - Sort order

**Response:**
```json
[
  {
    "id": "uuid",
    "key": "new_feature_enabled",
    "name": "New Feature",
    "description": "Enable new feature functionality",
    "is_enabled": true,
    "enabled_for_roles": ["admin", "manager"],
    "enabled_for_users": [],
    "created_at": "2024-12-01T02:42:21.103Z",
    "updated_at": "2024-12-06T05:54:04.773Z",
    "updated_by": "uuid",
    "updated_by_email": "admin@hishamos.com"
  }
]
```

#### Get Feature Flag

```http
GET /api/v1/core/feature-flags/{id}/
```

#### Create Feature Flag (Admin Only)

```http
POST /api/v1/core/feature-flags/
Content-Type: application/json

{
  "key": "new_feature_key",
  "name": "New Feature Name",
  "description": "Feature description",
  "is_enabled": false,
  "enabled_for_roles": ["admin"],
  "enabled_for_users": []
}
```

#### Update Feature Flag (Admin Only)

```http
PATCH /api/v1/core/feature-flags/{id}/
Content-Type: application/json

{
  "is_enabled": true
}
```

#### Delete Feature Flag (Admin Only)

```http
DELETE /api/v1/core/feature-flags/{id}/
```

#### Toggle Feature Flag (Admin Only)

```http
POST /api/v1/core/feature-flags/{id}/toggle/
```

Toggles the `is_enabled` status.

#### Get Active Feature Flags

```http
GET /api/v1/core/feature-flags/active/
```

Returns all enabled feature flags.

---

## 🔐 Permissions

### System Settings

- **List/Retrieve:** All authenticated users (public settings only for non-admins)
- **Create/Update/Delete:** Admin only

### Feature Flags

- **List/Retrieve:** All authenticated users
- **Create/Update/Delete/Toggle:** Admin only

---

## 📝 Value Types

### System Settings Value Types

1. **string** - Text value
   ```json
   {"value": "Hello World", "value_type": "string"}
   ```

2. **integer** - Integer number
   ```json
   {"value": "12345", "value_type": "integer"}
   ```
   `typed_value` will be: `12345`

3. **float** - Decimal number
   ```json
   {"value": "123.45", "value_type": "float"}
   ```
   `typed_value` will be: `123.45`

4. **boolean** - true/false
   ```json
   {"value": "true", "value_type": "boolean"}
   ```
   `typed_value` will be: `true`

5. **json** - JSON object/array
   ```json
   {"value": "{\"key\": \"value\"}", "value_type": "json"}
   ```
   `typed_value` will be: `{"key": "value"}`

---

## 🧪 Usage Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/core"
TOKEN = "your_access_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# List system settings
response = requests.get(f"{BASE_URL}/settings/", headers=headers)
settings = response.json()

# Create a setting
data = {
    "key": "max_upload_size",
    "value": "10485760",
    "value_type": "integer",
    "category": "general",
    "description": "Max file upload size",
    "is_public": True
}
response = requests.post(f"{BASE_URL}/settings/", headers=headers, json=data)

# Toggle feature flag
response = requests.post(
    f"{BASE_URL}/feature-flags/{flag_id}/toggle/",
    headers=headers
)
```

### cURL Examples

```bash
# List settings
curl -X GET "http://localhost:8000/api/v1/core/settings/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create setting
curl -X POST "http://localhost:8000/api/v1/core/settings/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "max_upload_size",
    "value": "10485760",
    "value_type": "integer",
    "category": "general",
    "description": "Max file upload size",
    "is_public": true
  }'

# Toggle feature flag
curl -X POST "http://localhost:8000/api/v1/core/feature-flags/{id}/toggle/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔗 Related Documentation

- [Complete API Reference](API_REFERENCE.md)
- [Admin Guide](ADMIN_GUIDE.md)
- [System Settings UI Testing](../03_TESTING/MANUAL_TEST_CHECKLISTS/SYSTEM_SETTINGS_UI_MANUAL_TESTING_CHECKLIST.md)

---

**Last Updated:** December 2024  
**Maintained by:** Development Team

