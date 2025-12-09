# Permission Matrix - Role-Based Access Control

**Document Type:** Business Requirements Document (BRD)  
**Version:** 1.0.0  
**Created By:** BA Agent  
**Created Date:** December 9, 2024  
**Last Updated:** December 9, 2024  
**Last Updated By:** BA Agent  
**Status:** Active  
**Dependencies:** `01_overview_and_scope.md`, `02_features_master_list/`  
**Related Features:** All project management features

---

## 📋 Table of Contents

1. [Role Definitions](#role-definitions)
2. [Permission Categories](#permission-categories)
3. [Project-Level Permissions](#project-level-permissions)
4. [Work Item Permissions](#work-item-permissions)
5. [API Permissions](#api-permissions)
6. [Frontend Permissions](#frontend-permissions)
7. [Permission Enforcement](#permission-enforcement)

---

## 1. Role Definitions

### 1.1 System Roles
- **Admin:** System administrator with full access to all projects
- **User:** Regular authenticated user

### 1.2 Project Roles
- **Owner:** Project owner (project.owner)
- **Member:** Project member (project.members)
- **Viewer:** User with read-only access (default for non-members)

### 1.3 Role Hierarchy
```
Admin > Owner > Member > Viewer
```

---

## 2. Permission Categories

### 2.1 CRUD Permissions
- **Create:** Create new entities
- **Read:** View entities
- **Update:** Edit existing entities
- **Delete:** Delete entities

### 2.2 Action Permissions
- **Assign:** Assign work items to users
- **Change Status:** Change work item status
- **Manage Sprints:** Create/edit/delete sprints
- **Manage Configuration:** Edit project configuration
- **View Analytics:** Access analytics and reports

---

## 3. Project-Level Permissions

### 3.1 Project CRUD

| Action | Admin | Owner | Member | Viewer |
|--------|-------|-------|--------|--------|
| Create Project | ✅ | ✅ | ✅ | ❌ |
| View Project | ✅ | ✅ | ✅ | ✅ (if accessible) |
| Edit Project | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Delete Project | ✅ | ✅ | ❌ | ❌ |
| Add Members | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Remove Members | ✅ | ✅ | ⚠️ (if allowed) | ❌ |

### 3.2 Project Configuration

| Action | Admin | Owner | Member | Viewer |
|--------|-------|-------|--------|--------|
| View Configuration | ✅ | ✅ | ✅ | ✅ |
| Edit Configuration | ✅ | ✅ | ❌ | ❌ |

---

## 4. Work Item Permissions

### 4.1 User Story Permissions

| Action | Admin | Owner | Member | Viewer |
|--------|-------|-------|--------|--------|
| Create Story | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| View Story | ✅ | ✅ | ✅ | ✅ |
| Edit Story | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Delete Story | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Assign Story | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Change Status | ✅ | ✅ | ⚠️ (if allowed) | ❌ |

**⚠️ = Based on project permission settings**

### 4.2 Task Permissions

| Action | Admin | Owner | Member | Viewer |
|--------|-------|-------|--------|--------|
| Create Task | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| View Task | ✅ | ✅ | ✅ | ✅ |
| Edit Task | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Delete Task | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Assign Task | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Change Status | ✅ | ✅ | ⚠️ (if allowed) | ❌ |

### 4.3 Bug Permissions

| Action | Admin | Owner | Member | Viewer |
|--------|-------|-------|--------|--------|
| Create Bug | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| View Bug | ✅ | ✅ | ✅ | ✅ |
| Edit Bug | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Delete Bug | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Assign Bug | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Change Status | ✅ | ✅ | ⚠️ (if allowed) | ❌ |

### 4.4 Issue Permissions

| Action | Admin | Owner | Member | Viewer |
|--------|-------|-------|--------|--------|
| Create Issue | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| View Issue | ✅ | ✅ | ✅ | ✅ |
| Edit Issue | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Delete Issue | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Assign Issue | ✅ | ✅ | ⚠️ (if allowed) | ❌ |
| Change Status | ✅ | ✅ | ⚠️ (if allowed) | ❌ |

---

## 5. API Permissions

### 5.1 Permission Enforcement
- **Backend:** Permission checks in ViewSets
- **Permission Classes:** `IsProjectMember`, `IsProjectMemberOrReadOnly`, `IsProjectOwner`
- **Service Layer:** `PermissionEnforcementService` for project-level permissions

### 5.2 API Endpoint Permissions

| Endpoint | Admin | Owner | Member | Viewer |
|----------|-------|-------|--------|--------|
| GET /projects/ | ✅ | ✅ | ✅ | ✅ (own projects) |
| POST /projects/ | ✅ | ✅ | ✅ | ❌ |
| GET /projects/{id}/ | ✅ | ✅ | ✅ | ✅ (if accessible) |
| PUT /projects/{id}/ | ✅ | ✅ | ⚠️ | ❌ |
| DELETE /projects/{id}/ | ✅ | ✅ | ❌ | ❌ |
| GET /projects/{id}/stories/ | ✅ | ✅ | ✅ | ✅ |
| POST /projects/{id}/stories/ | ✅ | ✅ | ⚠️ | ❌ |
| PUT /projects/{id}/stories/{id}/ | ✅ | ✅ | ⚠️ | ❌ |
| DELETE /projects/{id}/stories/{id}/ | ✅ | ✅ | ⚠️ | ❌ |

---

## 6. Frontend Permissions

### 6.1 UI Hiding
- **Hook:** `useProjectPermissions` for permission checks
- **Components:** Hide buttons/actions based on permissions
- **Pages:** Hide create/edit/delete buttons based on permissions

### 6.2 Permission-Based UI

| UI Element | Admin | Owner | Member | Viewer |
|------------|-------|-------|--------|--------|
| Create Button | ✅ | ✅ | ⚠️ | ❌ |
| Edit Button | ✅ | ✅ | ⚠️ | ❌ |
| Delete Button | ✅ | ✅ | ⚠️ | ❌ |
| Assign Button | ✅ | ✅ | ⚠️ | ❌ |
| Status Change | ✅ | ✅ | ⚠️ | ❌ |
| Settings Button | ✅ | ✅ | ❌ | ❌ |

---

## 7. Permission Enforcement

### 7.1 Backend Enforcement
- **ViewSet Level:** Permission classes check access
- **Service Level:** `PermissionEnforcementService` checks project-level permissions
- **Serializer Level:** Permission checks in validation

### 7.2 Frontend Enforcement
- **Hook Level:** `useProjectPermissions` hook checks permissions
- **Component Level:** Conditional rendering based on permissions
- **Page Level:** Hide/show sections based on permissions

### 7.3 Permission Settings
- **Project Configuration:** `permission_settings` JSONField
- **Default Permissions:** Defined in `PermissionEnforcementService.DEFAULT_PERMISSIONS`
- **Override:** Project-specific permission overrides

### 7.4 Permission Keys
- `who_can_create_stories`: ['member', 'admin']
- `who_can_edit_stories`: ['member', 'admin']
- `who_can_delete_stories`: ['admin']
- `who_can_assign_stories`: ['member', 'admin']
- `who_can_change_status`: ['member', 'admin']
- `who_can_manage_sprints`: ['admin', 'scrum_master']
- `who_can_view_analytics`: ['member', 'admin']
- `who_can_create_epics`: ['member', 'admin']
- `who_can_edit_epics`: ['member', 'admin']
- `who_can_delete_epics`: ['admin']
- `who_can_create_issues`: ['member', 'admin']
- `who_can_create_tasks`: ['member', 'admin']
- `who_can_edit_tasks`: ['member', 'admin']
- `who_can_delete_tasks`: ['member', 'admin']
- `who_can_add_comments`: ['member', 'admin']
- `who_can_add_attachments`: ['member', 'admin']
- `who_can_manage_dependencies`: ['member', 'admin']

---

**End of Document**

**Related Documents:**
- `04_business_logic_rules/` - Business logic rules
- `05_data_model_relations/` - Data model documentation
- `06_api_requirements/` - API documentation

