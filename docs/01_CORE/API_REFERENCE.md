# HishamOS API Reference

**Last Updated:** December 2024  
**Base URL:** `http://localhost:8000/api/v1`  
**Authentication:** JWT Bearer Token or API Key

---

## 📋 Table of Contents

1. [Commands API](#commands-api)
2. [System Settings API](#system-settings-api)
3. [Feature Flags API](#feature-flags-api)
4. [Authentication](#authentication)

---

## 🔐 Authentication

All API endpoints require authentication unless otherwise specified.

### JWT Authentication

Include the access token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### API Key Authentication

Include the API key in the X-API-Key header:

```http
X-API-Key: <your_api_key>
```

---

## 📦 Commands API

Base URL: `/api/v1/commands/`

### Command Categories

#### List Categories

```http
GET /api/v1/commands/categories/
```

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Requirements Engineering",
    "slug": "requirements-engineering",
    "description": "Transform ideas into detailed requirements...",
    "icon": "📋",
    "order": 1,
    "command_count": 19,
    "active_command_count": 19,
    "created_at": "2024-12-01T02:42:21.103Z",
    "updated_at": "2024-12-06T05:54:04.773Z"
  }
]
```

#### Get Category

```http
GET /api/v1/commands/categories/{id}/
```

#### Create Category (Admin Only)

```http
POST /api/v1/commands/categories/
Content-Type: application/json

{
  "name": "New Category",
  "slug": "new-category",
  "description": "Category description",
  "icon": "🎯",
  "order": 13
}
```

#### Update Category (Admin Only)

```http
PATCH /api/v1/commands/categories/{id}/
Content-Type: application/json

{
  "description": "Updated description"
}
```

#### Delete Category (Admin Only)

```http
DELETE /api/v1/commands/categories/{id}/
```

---

### Command Templates

#### List Commands

```http
GET /api/v1/commands/templates/
```

**Query Parameters:**
- `category` - Filter by category ID
- `is_active` - Filter by active status (true/false)
- `search` - Search in name, description, tags
- `ordering` - Order by: `created_at`, `usage_count`, `name`, `success_rate`, `estimated_cost`

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Generate User Stories",
    "slug": "generate-user-stories",
    "description": "Generate user stories from requirements...",
    "category_name": "Requirements Engineering",
    "tags": ["requirements", "user-stories"],
    "usage_count": 45,
    "success_rate": 95.5,
    "estimated_cost": 0.05,
    "is_active": true
  }
]
```

#### Get Command

```http
GET /api/v1/commands/templates/{id}/
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Generate User Stories",
  "slug": "generate-user-stories",
  "description": "Generate user stories from requirements...",
  "category": "uuid",
  "category_name": "Requirements Engineering",
  "template": "Generate user stories for: {{project_name}}...",
  "parameters": [
    {
      "name": "project_name",
      "type": "string",
      "required": true,
      "description": "Name of the project",
      "example": "E-commerce Platform"
    }
  ],
  "recommended_agent": "uuid",
  "recommended_agent_name": "Business Analyst Agent",
  "required_capabilities": ["REQUIREMENTS_ANALYSIS"],
  "estimated_cost": 0.05,
  "estimated_duration": 30,
  "tags": ["requirements", "user-stories"],
  "version": "1.0.0",
  "usage_count": 45,
  "is_active": true,
  "created_at": "2024-12-01T02:42:21.103Z",
  "updated_at": "2024-12-06T05:54:04.773Z"
}
```

#### Create Command (Admin Only)

```http
POST /api/v1/commands/templates/
Content-Type: application/json

{
  "category": "uuid",
  "name": "New Command",
  "slug": "new-command",
  "description": "Command description",
  "template": "Template with {{parameter}} placeholders",
  "parameters": [
    {
      "name": "parameter",
      "type": "string",
      "required": true,
      "description": "Parameter description",
      "example": "Example value"
    }
  ],
  "tags": ["tag1", "tag2"],
  "is_active": true
}
```

#### Update Command (Admin Only)

```http
PATCH /api/v1/commands/templates/{id}/
Content-Type: application/json

{
  "description": "Updated description",
  "is_active": false
}
```

#### Delete Command (Admin Only)

```http
DELETE /api/v1/commands/templates/{id}/
```

---

### Command Execution

#### Preview Command (No Execution)

```http
POST /api/v1/commands/templates/{id}/preview/
Content-Type: application/json

{
  "parameters": {
    "project_name": "E-commerce Platform",
    "features": "User authentication, Product catalog"
  }
}
```

**Response:**
```json
{
  "rendered_template": "Generate user stories for: E-commerce Platform...",
  "validation_errors": []
}
```

#### Execute Command

```http
POST /api/v1/commands/templates/{id}/execute/
Content-Type: application/json

{
  "parameters": {
    "project_name": "E-commerce Platform",
    "features": "User authentication, Product catalog"
  },
  "agent_id": "optional-agent-id"
}
```

**Response (Success):**
```json
{
  "success": true,
  "output": "Generated user stories:\n1. As a user...",
  "execution_time": 2.5,
  "cost": 0.05,
  "token_usage": {
    "tokens_used": 1250
  },
  "agent_used": "business-analyst",
  "error": null
}
```

**Response (Error):**
```json
{
  "success": false,
  "output": "",
  "execution_time": 0,
  "cost": 0,
  "token_usage": {},
  "agent_used": "",
  "error": "Error message here"
}
```

**Note:** Execution timeout is 4 minutes (240 seconds).

---

### Popular Commands

```http
GET /api/v1/commands/templates/popular/
```

Returns top 10 commands by success rate and usage count.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Generate User Stories",
    "slug": "generate-user-stories",
    "description": "...",
    "category_name": "Requirements Engineering",
    "tags": ["requirements"],
    "usage_count": 150,
    "success_rate": 98.5,
    "estimated_cost": 0.05,
    "is_active": true
  }
]
```

---

## ⚙️ System Settings API

Base URL: `/api/v1/core/settings/`

### List Settings

```http
GET /api/v1/core/settings/
```

**Query Parameters:**
- `category` - Filter by category: `general`, `security`, `performance`, `notifications`, `integrations`
- `is_public` - Filter by public status (true/false)
- `search` - Search in key, description
- `ordering` - Order by: `category`, `key`, `updated_at`

**Permissions:**
- All authenticated users can view public settings
- Admins can view all settings

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

### Get Setting

```http
GET /api/v1/core/settings/{id}/
```

### Create Setting (Admin Only)

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

**Value Types:**
- `string` - Text value
- `integer` - Integer number
- `float` - Decimal number
- `boolean` - true/false
- `json` - JSON object/array

**Categories:**
- `general` - General settings
- `security` - Security settings
- `performance` - Performance settings
- `notifications` - Notification settings
- `integrations` - Integration settings

### Update Setting (Admin Only)

```http
PATCH /api/v1/core/settings/{id}/
Content-Type: application/json

{
  "value": "new_value",
  "typed_value": 12345  // Optional: will auto-convert based on value_type
}
```

### Delete Setting (Admin Only)

```http
DELETE /api/v1/core/settings/{id}/
```

### Get Settings by Category

```http
GET /api/v1/core/settings/by_category/
```

**Response:**
```json
{
  "general": [
    {
      "id": "uuid",
      "key": "max_file_upload_size",
      "value": "10485760",
      ...
    }
  ],
  "security": [
    ...
  ]
}
```

### Reset Setting to Default (Admin Only)

```http
POST /api/v1/core/settings/{id}/reset_to_default/
```

**Response:**
```json
{
  "message": "Reset functionality to be implemented",
  "current_value": "current_value"
}
```

---

## 🚩 Feature Flags API

Base URL: `/api/v1/core/feature-flags/`

### List Feature Flags

```http
GET /api/v1/core/feature-flags/
```

**Query Parameters:**
- `is_enabled` - Filter by enabled status (true/false)
- `search` - Search in key, name, description
- `ordering` - Order by: `key`, `is_enabled`, `updated_at`

**Permissions:**
- All authenticated users can view feature flags

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

### Get Feature Flag

```http
GET /api/v1/core/feature-flags/{id}/
```

### Create Feature Flag (Admin Only)

```http
POST /api/v1/core/feature-flags/
Content-Type: application/json

{
  "key": "new_feature_key",
  "name": "New Feature Name",
  "description": "Feature description",
  "is_enabled": false,
  "enabled_for_roles": ["admin"],  // Empty array = all roles
  "enabled_for_users": []  // Empty array = all users
}
```

**Access Control:**
- `enabled_for_roles` - List of roles that have access (empty = all roles)
- `enabled_for_users` - List of user IDs that have access (empty = all users)

### Update Feature Flag (Admin Only)

```http
PATCH /api/v1/core/feature-flags/{id}/
Content-Type: application/json

{
  "is_enabled": true,
  "enabled_for_roles": ["admin", "manager"]
}
```

### Delete Feature Flag (Admin Only)

```http
DELETE /api/v1/core/feature-flags/{id}/
```

### Toggle Feature Flag (Admin Only)

```http
POST /api/v1/core/feature-flags/{id}/toggle/
```

Toggles the `is_enabled` status of the feature flag.

**Response:**
```json
{
  "id": "uuid",
  "key": "new_feature_enabled",
  "name": "New Feature",
  "is_enabled": false,  // Toggled from true to false
  ...
}
```

### Get Active Feature Flags

```http
GET /api/v1/core/feature-flags/active/
```

Returns all feature flags where `is_enabled` is `true`.

**Response:**
```json
[
  {
    "id": "uuid",
    "key": "new_feature_enabled",
    "name": "New Feature",
    "is_enabled": true,
    ...
  }
]
```

---

## 📝 Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden (Admin only) |
| 404 | Not Found |
| 408 | Request Timeout (Command execution timeout) |
| 500 | Internal Server Error |

---

## 🔗 Related Documentation

- [Command Library Documentation](../08_COMMANDS/COMMAND_LIBRARY_DOCUMENTATION.md)
- [Command Testing Guide](../08_COMMANDS/COMMAND_TESTING_GUIDE.md)
- [Admin Guide](ADMIN_GUIDE.md)
- [User Guide](USER_GUIDE.md)

---

## 📚 Interactive API Documentation

For interactive API documentation, visit:
- **Swagger UI:** `http://localhost:8000/api/docs/`
- **ReDoc:** `http://localhost:8000/api/redoc/`
- **OpenAPI Schema:** `http://localhost:8000/api/schema/`

---

## 🧪 Testing Examples

### Using cURL

```bash
# List commands
curl -X GET "http://localhost:8000/api/v1/commands/templates/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Execute command
curl -X POST "http://localhost:8000/api/v1/commands/templates/{id}/execute/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "project_name": "My Project"
    }
  }'

# List system settings
curl -X GET "http://localhost:8000/api/v1/core/settings/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Toggle feature flag
curl -X POST "http://localhost:8000/api/v1/core/feature-flags/{id}/toggle/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_access_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# List commands
response = requests.get(f"{BASE_URL}/commands/templates/", headers=headers)
commands = response.json()

# Execute command
data = {
    "parameters": {
        "project_name": "My Project"
    }
}
response = requests.post(
    f"{BASE_URL}/commands/templates/{command_id}/execute/",
    headers=headers,
    json=data
)
result = response.json()
```

---

**Last Updated:** December 2024  
**Maintained by:** Development Team

