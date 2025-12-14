# API Architecture - AI Agent Workflow Enhancement

**Document Type:** API Architecture  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 01_SYSTEM_ARCHITECTURE.md, 02_COMPONENT_ARCHITECTURE.md, ../04_BACKEND/04_VIEWS_IMPLEMENTATION.md  
**File Size:** 496 lines

---

## 📋 Purpose

This document describes the API architecture for the AI agent workflow enhancement, including endpoint design, request/response formats, authentication, and error handling.

---

## 🔌 API Overview

### API Base URL
```
/api/v1/
```

### API Versioning
- Current version: `v1`
- Version in URL path
- Backward compatibility maintained

---

## 📡 New API Endpoints

### Endpoint Group 1: Project Generation

#### POST /api/v1/projects/{project_id}/generate/

**Purpose:** Generate project files

**Request:**
```json
{
  "workflow_id": "uuid",
  "input_data": {
    "requirements": "...",
    "framework": "django",
    "language": "python"
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "project": "uuid",
  "status": "generating",
  "output_directory": "/path/to/generated",
  "created_at": "2025-12-13T10:00:00Z"
}
```

**Status Codes:**
- `201 Created` - Generation started
- `400 Bad Request` - Invalid input
- `403 Forbidden` - No permission
- `404 Not Found` - Project not found

---

#### GET /api/v1/projects/{project_id}/generated/

**Purpose:** List generated projects

**Query Parameters:**
- `status` - Filter by status
- `page` - Page number
- `page_size` - Items per page

**Response:**
```json
{
  "count": 10,
  "next": "url",
  "previous": "url",
  "results": [
    {
      "id": "uuid",
      "status": "completed",
      "total_files": 50,
      "total_size": 1024000,
      "created_at": "2025-12-13T10:00:00Z"
    }
  ]
}
```

---

#### GET /api/v1/projects/{project_id}/generated/{generated_id}/

**Purpose:** Get generated project details

**Response:**
```json
{
  "id": "uuid",
  "project": {
    "id": "uuid",
    "name": "My Project"
  },
  "status": "completed",
  "output_directory": "/path/to/generated",
  "total_files": 50,
  "total_size": 1024000,
  "files": [
    {
      "id": "uuid",
      "file_path": "src/main.py",
      "file_size": 1024,
      "file_type": "python"
    }
  ],
  "created_at": "2025-12-13T10:00:00Z",
  "completed_at": "2025-12-13T10:05:00Z"
}
```

---

### Endpoint Group 2: File Management

#### GET /api/v1/projects/{project_id}/generated/{generated_id}/files/

**Purpose:** List files in generated project

**Query Parameters:**
- `file_type` - Filter by file type
- `path` - Filter by path prefix
- `page` - Page number
- `page_size` - Items per page

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": "uuid",
      "file_path": "src/main.py",
      "file_name": "main.py",
      "file_type": "python",
      "file_size": 1024,
      "created_at": "2025-12-13T10:00:00Z"
    }
  ]
}
```

---

#### GET /api/v1/projects/{project_id}/generated/{generated_id}/files/{file_id}/

**Purpose:** Get file details and content

**Query Parameters:**
- `content` - Include file content (boolean)

**Response:**
```json
{
  "id": "uuid",
  "file_path": "src/main.py",
  "file_name": "main.py",
  "file_type": "python",
  "file_size": 1024,
  "content_hash": "sha256...",
  "content": "# File content...",
  "content_preview": "# File preview...",
  "created_at": "2025-12-13T10:00:00Z"
}
```

---

#### GET /api/v1/projects/{project_id}/generated/{generated_id}/files/content/

**Purpose:** Download file content

**Query Parameters:**
- `path` - File path (required)

**Response:**
- Content-Type: Based on file type
- Content-Disposition: attachment; filename="..."
- Body: File content

---

### Endpoint Group 3: Repository Export

#### POST /api/v1/projects/{project_id}/generated/{generated_id}/export/

**Purpose:** Export generated project

**Request:**
```json
{
  "export_type": "zip",
  "repository_name": "my-project",
  "config": {
    "private": false
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "generated_project": "uuid",
  "export_type": "zip",
  "status": "exporting",
  "created_at": "2025-12-13T10:00:00Z"
}
```

---

#### POST /api/v1/projects/{project_id}/generated/{generated_id}/export-to-github/

**Purpose:** Export to GitHub

**Request:**
```json
{
  "repository_name": "my-project",
  "organization": "myorg",
  "private": false,
  "github_token": "token" // or use stored token
}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "completed",
  "repository_url": "https://github.com/owner/repo",
  "completed_at": "2025-12-13T10:05:00Z"
}
```

---

#### POST /api/v1/projects/{project_id}/generated/{generated_id}/export-to-gitlab/

**Purpose:** Export to GitLab

**Request:**
```json
{
  "project_name": "my-project",
  "namespace": "mygroup",
  "visibility": "private",
  "gitlab_token": "token"
}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "completed",
  "repository_url": "https://gitlab.com/namespace/project",
  "completed_at": "2025-12-13T10:05:00Z"
}
```

---

#### GET /api/v1/projects/{project_id}/generated/{generated_id}/exports/

**Purpose:** List export jobs

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": "uuid",
      "export_type": "github",
      "status": "completed",
      "repository_url": "https://github.com/...",
      "created_at": "2025-12-13T10:00:00Z"
    }
  ]
}
```

---

#### GET /api/v1/projects/{project_id}/generated/{generated_id}/exports/{export_id}/

**Purpose:** Get export job status

**Response:**
```json
{
  "id": "uuid",
  "export_type": "zip",
  "status": "completed",
  "archive_path": "/path/to/archive.zip",
  "archive_size": 2048000,
  "download_url": "/api/v1/exports/{export_id}/download/",
  "created_at": "2025-12-13T10:00:00Z",
  "completed_at": "2025-12-13T10:05:00Z"
}
```

---

#### GET /api/v1/exports/{export_id}/download/

**Purpose:** Download export archive

**Response:**
- Content-Type: application/zip or application/tar+gzip
- Content-Disposition: attachment; filename="project.zip"
- Body: Archive file

---

### Endpoint Group 4: Agent API Integration

#### GET /api/v1/agents/api-endpoints/

**Purpose:** Discover available API endpoints for agents

**Response:**
```json
{
  "endpoints": [
    {
      "path": "/api/v1/projects/{project_id}/stories/",
      "method": "POST",
      "description": "Create a user story",
      "parameters": [
        {
          "name": "title",
          "type": "string",
          "required": true
        }
      ]
    }
  ]
}
```

---

## 🔐 Authentication & Authorization

### Authentication
- **Method:** JWT (JSON Web Tokens)
- **Header:** `Authorization: Bearer <token>`
- **Token Source:** Login endpoint
- **Token Expiry:** Configurable (default 24 hours)

### Authorization
- **Method:** Permission classes
- **Scopes:** Project-level permissions
- **Super Admin:** Bypasses all checks

---

## ⚠️ Error Handling

### Error Response Format

```json
{
  "error": "Error code",
  "message": "Human-readable error message",
  "details": {
    "field": "Specific error for field"
  },
  "timestamp": "2025-12-13T10:00:00Z"
}
```

### Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

---

## 📊 Rate Limiting

### Limits

- **Default:** 100 requests/minute per user
- **Export Endpoints:** 10 requests/minute
- **File Download:** 50 requests/minute

### Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## 🔄 Pagination

### Format

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 25, max: 100)

**Response:**
```json
{
  "count": 100,
  "next": "http://api/v1/endpoint/?page=3",
  "previous": "http://api/v1/endpoint/?page=1",
  "results": [...]
}
```

---

## 🔗 Related Documentation

- **Views Implementation:** `../04_BACKEND/04_VIEWS_IMPLEMENTATION.md`
- **System Architecture:** `01_SYSTEM_ARCHITECTURE.md`
- **Component Architecture:** `02_COMPONENT_ARCHITECTURE.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

