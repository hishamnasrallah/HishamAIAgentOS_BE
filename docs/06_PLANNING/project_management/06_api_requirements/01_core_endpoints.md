# API Requirements - Core Endpoints

**Document Type:** Business Requirements Document (BRD)  
**Version:** 1.0.0  
**Created By:** BA Agent  
**Created Date:** December 9, 2024  
**Last Updated:** December 9, 2024  
**Last Updated By:** BA Agent  
**Status:** Active  
**Dependencies:** `01_overview_and_scope.md`, `05_data_model_relations/`  
**Related Features:** All project management features

---

## 📋 Table of Contents

1. [Project Endpoints](#project-endpoints)
2. [Epic Endpoints](#epic-endpoints)
3. [Sprint Endpoints](#sprint-endpoints)
4. [API Standards](#api-standards)

---

## 1. Project Endpoints

### 1.1 List Projects
- **Endpoint:** `GET /api/projects/`
- **Authentication:** Required
- **Permissions:** Returns projects where user is owner or member (admins see all)
- **Query Parameters:**
  - `tags`: Comma-separated tags for filtering
  - `status`: Filter by project status
  - `search`: Search in name/description
- **Response:** List of projects with pagination
- **Response Format:**
  ```json
  {
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "uuid",
        "name": "string",
        "slug": "string",
        "description": "string",
        "status": "string",
        "owner": {"id": "uuid", "email": "string"},
        "members": [{"id": "uuid", "email": "string"}],
        "tags": ["tag1", "tag2"],
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

### 1.2 Create Project
- **Endpoint:** `POST /api/projects/`
- **Authentication:** Required
- **Permissions:** Any authenticated user
- **Request Body:**
  ```json
  {
    "name": "string (required)",
    "slug": "string (optional, auto-generated)",
    "description": "string (optional)",
    "status": "string (optional, default: 'planning')",
    "start_date": "date (optional)",
    "end_date": "date (optional)",
    "tags": ["tag1", "tag2"] (optional)
  }
  ```
- **Validation:**
  - Name required, max 200 characters
  - Slug auto-generated if not provided
  - Status must be from STATUS_CHOICES
  - End date must be after start date
- **Response:** Created project object (201 Created)
- **Side Effects:**
  - ProjectConfiguration created automatically
  - Owner set to current user
  - Activity log entry created

### 1.3 Get Project
- **Endpoint:** `GET /api/projects/{id}/`
- **Authentication:** Required
- **Permissions:** Project member or admin
- **Response:** Project object with related data
- **Response Format:** Same as list item, with additional fields

### 1.4 Update Project
- **Endpoint:** `PUT /api/projects/{id}/` or `PATCH /api/projects/{id}/`
- **Authentication:** Required
- **Permissions:** Project owner or admin
- **Request Body:** Same as create (all fields optional for PATCH)
- **Validation:** Same as create
- **Response:** Updated project object (200 OK)
- **Side Effects:**
  - updated_by set to current user
  - Activity log entry created

### 1.5 Delete Project
- **Endpoint:** `DELETE /api/projects/{id}/`
- **Authentication:** Required
- **Permissions:** Project owner or admin
- **Response:** 204 No Content
- **Side Effects:**
  - All related entities deleted (CASCADE)
  - Activity log entry created

### 1.6 Project Members
- **Endpoint:** `GET /api/projects/{id}/members/`
- **Authentication:** Required
- **Permissions:** Project member or admin
- **Response:** List of project members (owner + members)
- **Response Format:**
  ```json
  [
    {
      "id": "uuid",
      "email": "string",
      "first_name": "string",
      "last_name": "string"
    }
  ]
  ```

### 1.7 Add Member
- **Endpoint:** `POST /api/projects/{id}/members/add/`
- **Authentication:** Required
- **Permissions:** Project owner or admin
- **Request Body:**
  ```json
  {
    "user_id": "uuid (required)"
  }
  ```
- **Validation:**
  - User must exist
  - User cannot be owner (owner is already a member)
  - User cannot already be a member
- **Response:** Success message (200 OK)
- **Side Effects:**
  - User added to project.members
  - Notification sent to added user

### 1.8 Remove Member
- **Endpoint:** `POST /api/projects/{id}/members/remove/`
- **Authentication:** Required
- **Permissions:** Project owner or admin
- **Request Body:**
  ```json
  {
    "user_id": "uuid (required)"
  }
  ```
- **Validation:**
  - User must be a member
  - Cannot remove owner
- **Response:** Success message (200 OK)
- **Side Effects:**
  - User removed from project.members
  - Activity log entry created

### 1.9 Generate Stories (AI)
- **Endpoint:** `POST /api/projects/{id}/generate-stories/`
- **Authentication:** Required
- **Permissions:** Project member or admin
- **Request Body:**
  ```json
  {
    "product_vision": "string (required)",
    "context": {} (optional),
    "epic_id": "uuid (optional)"
  }
  ```
- **Response:** List of generated stories (201 Created)
- **Side Effects:**
  - Stories created with generated_by_ai=True
  - Activity log entries created

### 1.10 Project Velocity
- **Endpoint:** `GET /api/projects/{id}/velocity/`
- **Authentication:** Required
- **Permissions:** Project member or admin
- **Query Parameters:**
  - `num_sprints`: Number of sprints to analyze (default: 5)
- **Response:** Velocity metrics
- **Response Format:**
  ```json
  {
    "average_velocity": 25.5,
    "sprint_velocities": [
      {"sprint_number": 1, "velocity": 20},
      {"sprint_number": 2, "velocity": 25}
    ],
    "trend": "increasing"
  }
  ```

### 1.11 Project Tags
- **Endpoint:** `GET /api/projects/tags/`
- **Authentication:** Required
- **Response:** List of all unique tags from accessible projects
- **Response Format:**
  ```json
  {
    "tags": ["tag1", "tag2", "tag3"]
  }
  ```

### 1.12 Tag Autocomplete
- **Endpoint:** `GET /api/projects/tags/autocomplete/?q=tag`
- **Authentication:** Required
- **Query Parameters:**
  - `q`: Search query (required)
- **Response:** List of matching tags
- **Response Format:**
  ```json
  {
    "tags": ["tag1", "tag2"]
  }
  ```

---

## 2. Epic Endpoints

### 2.1 List Epics
- **Endpoint:** `GET /api/projects/{project_id}/epics/`
- **Authentication:** Required
- **Permissions:** Project member or admin
- **Query Parameters:**
  - `status`: Filter by status
  - `owner`: Filter by owner ID
  - `tags`: Comma-separated tags
  - `search`: Search in title/description
- **Response:** List of epics with pagination

### 2.2 Create Epic
- **Endpoint:** `POST /api/projects/{project_id}/epics/`
- **Authentication:** Required
- **Permissions:** Project member or admin (based on permission settings)
- **Request Body:**
  ```json
  {
    "title": "string (required)",
    "description": "string (required)",
    "status": "string (optional, default: 'planned')",
    "start_date": "date (optional)",
    "target_date": "date (optional)",
    "owner": "uuid (optional)",
    "tags": ["tag1", "tag2"] (optional)
  }
  ```
- **Validation:**
  - Title required, max 300 characters
  - Description required
  - Status must be from STATUS_CHOICES
  - Target date must be after start date
- **Response:** Created epic object (201 Created)

### 2.3 Get Epic
- **Endpoint:** `GET /api/projects/{project_id}/epics/{id}/`
- **Authentication:** Required
- **Permissions:** Project member or admin
- **Response:** Epic object with related stories

### 2.4 Update Epic
- **Endpoint:** `PUT /api/projects/{project_id}/epics/{id}/` or `PATCH /api/projects/{project_id}/epics/{id}/`
- **Authentication:** Required
- **Permissions:** Project member or admin (based on permission settings)
- **Request Body:** Same as create (all fields optional for PATCH)
- **Response:** Updated epic object (200 OK)

### 2.5 Delete Epic
- **Endpoint:** `DELETE /api/projects/{project_id}/epics/{id}/`
- **Authentication:** Required
- **Permissions:** Project admin or owner (based on permission settings)
- **Response:** 204 No Content
- **Side Effects:**
  - Story.epic set to NULL for all related stories (SET_NULL)

---

## 3. Sprint Endpoints

### 3.1 List Sprints
- **Endpoint:** `GET /api/projects/{project_id}/sprints/`
- **Authentication:** Required
- **Permissions:** Project member or admin
- **Query Parameters:**
  - `status`: Filter by status
  - `search`: Search in name/goal
- **Response:** List of sprints with pagination

### 3.2 Create Sprint
- **Endpoint:** `POST /api/projects/{project_id}/sprints/`
- **Authentication:** Required
- **Permissions:** Project member or admin (based on permission settings)
- **Request Body:**
  ```json
  {
    "name": "string (required)",
    "sprint_number": "integer (optional, auto-incremented)",
    "goal": "string (optional)",
    "start_date": "date (required)",
    "end_date": "date (required)"
  }
  ```
- **Validation:**
  - Name required, max 200 characters
  - Sprint number auto-incremented if not provided
  - Start date and end date required
  - End date must be after start date
  - Dates must be within project dates (if project has dates)
  - No overlapping sprints
- **Response:** Created sprint object (201 Created)
- **Side Effects:**
  - Sprint number auto-incremented from project configuration
  - Default duration applied from configuration
  - Default start day applied from configuration

### 3.3 Get Sprint
- **Endpoint:** `GET /api/projects/{project_id}/sprints/{id}/`
- **Authentication:** Required
- **Permissions:** Project member or admin
- **Response:** Sprint object with related stories

### 3.4 Update Sprint
- **Endpoint:** `PUT /api/projects/{project_id}/sprints/{id}/` or `PATCH /api/projects/{project_id}/sprints/{id}/`
- **Authentication:** Required
- **Permissions:** Project member or admin (based on permission settings)
- **Request Body:** Same as create (all fields optional for PATCH)
- **Validation:**
  - Same as create
  - Capacity validation if total_story_points updated
- **Response:** Updated sprint object (200 OK)

### 3.5 Delete Sprint
- **Endpoint:** `DELETE /api/projects/{project_id}/sprints/{id}/`
- **Authentication:** Required
- **Permissions:** Project admin or owner (based on permission settings)
- **Response:** 204 No Content
- **Side Effects:**
  - Story.sprint set to NULL for all related stories (SET_NULL)

---

## 4. API Standards

### 4.1 Authentication
- **Method:** JWT Bearer Token
- **Header:** `Authorization: Bearer <token>`
- **Required:** All endpoints except authentication endpoints

### 4.2 Response Formats
- **Success (200 OK):** Resource data
- **Created (201 Created):** Created resource data
- **No Content (204 No Content):** Empty response
- **Error (400 Bad Request):** Validation errors
- **Error (401 Unauthorized):** Authentication required
- **Error (403 Forbidden):** Permission denied
- **Error (404 Not Found):** Resource not found
- **Error (500 Internal Server Error):** Server error

### 4.3 Error Response Format
```json
{
  "error": "Error message",
  "details": {
    "field_name": ["Error message 1", "Error message 2"]
  }
}
```

### 4.4 Pagination
- **Default:** 20 items per page
- **Query Parameters:** `page`, `page_size`
- **Response Format:**
  ```json
  {
    "count": 100,
    "next": "http://api/projects/?page=2",
    "previous": null,
    "results": [...]
  }
  ```

### 4.5 Filtering
- **Query Parameters:** Field-based filtering
- **Examples:** `?status=active`, `?tags=tag1,tag2`, `?search=query`
- **Multiple Values:** Comma-separated for tags, multiple query params for other fields

### 4.6 Sorting
- **Query Parameter:** `ordering=field_name` or `ordering=-field_name` (descending)
- **Multiple Fields:** `ordering=field1,-field2`

### 4.7 Performance Requirements
- **Response Time:** < 500ms (p95)
- **Pagination:** Required for list endpoints
- **Database Queries:** Optimized with select_related and prefetch_related
- **Caching:** Where appropriate (future enhancement)

---

**End of Document**

**Next Document:** `02_work_item_endpoints.md` - User Story, Task, Bug, Issue endpoints

