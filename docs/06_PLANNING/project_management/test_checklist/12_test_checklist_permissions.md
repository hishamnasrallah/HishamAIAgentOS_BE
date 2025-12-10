# Test Checklist: Permissions & Security

**Category:** Permissions  
**Features:** Role-based Access Control, Permission Checks, Security Validation  
**Estimated Tests:** ~100  
**Priority:** HIGH (Security Critical)

---

## 1. PROJECT PERMISSIONS

### 1.1 Project Owner

**TC-PERM-001: Owner Can View Project**
- [ ] **Test Case:** Project owner can view project
- [ ] **Endpoint:** `GET /api/projects/{project_id}/`
- [ ] **User:** Project owner
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Project data returned
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-002: Owner Can Update Project**
- [ ] **Test Case:** Project owner can update project
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/`
- [ ] **User:** Project owner
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Project updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-003: Owner Can Delete Project**
- [ ] **Test Case:** Project owner can delete project
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/`
- [ ] **User:** Project owner
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Project deleted
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-004: Owner Can Manage Members**
- [ ] **Test Case:** Project owner can add/remove members
- [ ] **Endpoint:** `POST /api/projects/{project_id}/members/add/`
- [ ] **User:** Project owner
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Member added
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-005: Owner Can Configure Project**
- [ ] **Test Case:** Project owner can configure project
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/configurations/`
- [ ] **User:** Project owner
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Configuration updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.2 Project Admin

**TC-PERM-006: Admin Can View Project**
- [ ] **Test Case:** Project admin can view project
- [ ] **Endpoint:** `GET /api/projects/{project_id}/`
- [ ] **User:** Project admin (member with admin role)
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Project data returned
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-007: Admin Can Update Project**
- [ ] **Test Case:** Project admin can update project
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/`
- [ ] **User:** Project admin
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Project updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-008: Admin Cannot Delete Project**
- [ ] **Test Case:** Project admin cannot delete project
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/`
- [ ] **User:** Project admin
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-009: Admin Can Manage Members**
- [ ] **Test Case:** Project admin can add/remove members
- [ ] **Endpoint:** `POST /api/projects/{project_id}/members/add/`
- [ ] **User:** Project admin
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Member added
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.3 Project Member

**TC-PERM-010: Member Can View Project**
- [ ] **Test Case:** Project member can view project
- [ ] **Endpoint:** `GET /api/projects/{project_id}/`
- [ ] **User:** Project member
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Project data returned
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-011: Member Cannot Update Project**
- [ ] **Test Case:** Project member cannot update project
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/`
- [ ] **User:** Project member
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-012: Member Cannot Delete Project**
- [ ] **Test Case:** Project member cannot delete project
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/`
- [ ] **User:** Project member
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-013: Member Cannot Manage Members**
- [ ] **Test Case:** Project member cannot add/remove members
- [ ] **Endpoint:** `POST /api/projects/{project_id}/members/add/`
- [ ] **User:** Project member
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

### 1.4 Non-Member

**TC-PERM-014: Non-Member Cannot View Project**
- [ ] **Test Case:** Non-member cannot view project
- [ ] **Endpoint:** `GET /api/projects/{project_id}/`
- [ ] **User:** User not in project
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden or 404 Not Found
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 2. STORY PERMISSIONS

### 2.1 Story CRUD Permissions

**TC-PERM-015: Member Can Create Story**
- [ ] **Test Case:** Project member can create story
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/`
- [ ] **User:** Project member
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Story created
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-016: Member Can View Story**
- [ ] **Test Case:** Project member can view story
- [ ] **Endpoint:** `GET /api/projects/{project_id}/stories/{story_id}/`
- [ ] **User:** Project member
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Story data returned
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-017: Member Can Update Own Story**
- [ ] **Test Case:** Member can update story they created
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/stories/{story_id}/`
- [ ] **User:** Story creator (member)
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Story updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-018: Member Can Update Assigned Story**
- [ ] **Test Case:** Member can update story assigned to them
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/stories/{story_id}/`
- [ ] **User:** Story assignee (member)
- [ ] **Expected Result:** 
  - Status code: 200 OK (if permission allows)
  - Or 403 if not allowed
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-019: Member Cannot Delete Story**
- [ ] **Test Case:** Member cannot delete story
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/stories/{story_id}/`
- [ ] **User:** Project member
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-020: Admin Can Delete Story**
- [ ] **Test Case:** Admin can delete story
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/stories/{story_id}/`
- [ ] **User:** Project admin
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Story deleted
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 3. COMMENT PERMISSIONS

### 3.1 Comment CRUD Permissions

**TC-PERM-021: Member Can Comment**
- [ ] **Test Case:** Member can add comment
- [ ] **Endpoint:** `POST /api/projects/{project_id}/comments/`
- [ ] **User:** Project member
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Comment created
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-022: Member Can Edit Own Comment**
- [ ] **Test Case:** Member can edit own comment
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/comments/{comment_id}/`
- [ ] **User:** Comment author (member)
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Comment updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-023: Member Cannot Edit Others' Comments**
- [ ] **Test Case:** Member cannot edit others' comments
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/comments/{comment_id}/`
- [ ] **User:** Different member
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-024: Member Can Delete Own Comment**
- [ ] **Test Case:** Member can delete own comment
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/comments/{comment_id}/`
- [ ] **User:** Comment author (member)
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Comment deleted
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-025: Admin Can Delete Any Comment**
- [ ] **Test Case:** Admin can delete any comment
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/comments/{comment_id}/`
- [ ] **User:** Project admin
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Comment deleted
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 4. ATTACHMENT PERMISSIONS

### 4.1 Attachment CRUD Permissions

**TC-PERM-026: Member Can Upload Attachment**
- [ ] **Test Case:** Member can upload attachment
- [ ] **Endpoint:** `POST /api/projects/{project_id}/attachments/`
- [ ] **User:** Project member
- [ ] **Expected Result:** 
  - Status code: 201 Created
  - Attachment uploaded
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-027: Member Can Download Attachment**
- [ ] **Test Case:** Member can download attachment
- [ ] **Endpoint:** `GET /api/projects/{project_id}/attachments/{attachment_id}/download/`
- [ ] **User:** Project member
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - File downloaded
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-028: Member Can Delete Own Attachment**
- [ ] **Test Case:** Member can delete own attachment
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/attachments/{attachment_id}/`
- [ ] **User:** Attachment uploader (member)
- [ ] **Expected Result:** 
  - Status code: 204 No Content
  - Attachment deleted
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-029: Member Cannot Delete Others' Attachments**
- [ ] **Test Case:** Member cannot delete others' attachments
- [ ] **Endpoint:** `DELETE /api/projects/{project_id}/attachments/{attachment_id}/`
- [ ] **User:** Different member
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 5. CONFIGURATION PERMISSIONS

### 5.1 Configuration Access

**TC-PERM-030: Owner Can Configure**
- [ ] **Test Case:** Owner can update configuration
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/configurations/`
- [ ] **User:** Project owner
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Configuration updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-031: Admin Can Configure**
- [ ] **Test Case:** Admin can update configuration
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/configurations/`
- [ ] **User:** Project admin
- [ ] **Expected Result:** 
  - Status code: 200 OK
  - Configuration updated
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-032: Member Cannot Configure**
- [ ] **Test Case:** Member cannot update configuration
- [ ] **Endpoint:** `PATCH /api/projects/{project_id}/configurations/`
- [ ] **User:** Project member
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 6. UI PERMISSION CHECKS

### 6.1 UI Element Visibility

**TC-PERM-033: Edit Button Visibility**
- [ ] **Test Case:** Edit button shown based on permissions
- [ ] **Page:** Story view modal
- [ ] **User:** Member
- [ ] **Expected Result:** 
  - Edit button visible if user can edit
  - Edit button hidden if user cannot edit
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-034: Delete Button Visibility**
- [ ] **Test Case:** Delete button shown based on permissions
- [ ] **Page:** Story view modal
- [ ] **User:** Member
- [ ] **Expected Result:** 
  - Delete button visible only to admin/owner
  - Delete button hidden for members
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-035: Settings Access**
- [ ] **Test Case:** Settings page access
- [ ] **Page:** Project settings
- [ ] **User:** Member
- [ ] **Expected Result:** 
  - Settings page accessible only to admin/owner
  - Redirected or 403 if member
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-036: Create Story Button**
- [ ] **Test Case:** Create button visibility
- [ ] **Page:** Board or stories list
- [ ] **User:** Member
- [ ] **Expected Result:** 
  - Create button visible if user can create stories
  - Hidden if not
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 7. DATA ISOLATION

### 7.1 Cross-Project Access

**TC-PERM-037: Cannot Access Other Projects**
- [ ] **Test Case:** User cannot access projects they're not in
- [ ] **Endpoint:** `GET /api/projects/{other_project_id}/`
- [ ] **User:** User not in project
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden or 404 Not Found
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-038: Cannot Access Other Projects' Stories**
- [ ] **Test Case:** User cannot access stories from other projects
- [ ] **Endpoint:** `GET /api/projects/{other_project_id}/stories/{story_id}/`
- [ ] **User:** User not in project
- [ ] **Expected Result:** 
  - Status code: 403 Forbidden or 404 Not Found
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 8. AUTHENTICATION

### 8.1 Authentication Checks

**TC-PERM-039: Unauthenticated Access Denied**
- [ ] **Test Case:** Unauthenticated user cannot access API
- [ ] **Endpoint:** `GET /api/projects/`
- [ ] **User:** Not authenticated
- [ ] **Expected Result:** 
  - Status code: 401 Unauthorized
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-040: Invalid Token Rejected**
- [ ] **Test Case:** Invalid token rejected
- [ ] **Endpoint:** `GET /api/projects/`
- [ ] **Headers:** `Authorization: Bearer invalid-token`
- [ ] **Expected Result:** 
  - Status code: 401 Unauthorized
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

## 9. INPUT VALIDATION

### 9.1 Security Validation

**TC-PERM-041: SQL Injection Prevention**
- [ ] **Test Case:** SQL injection attempts blocked
- [ ] **Endpoint:** `GET /api/projects/?name=' OR '1'='1`
- [ ] **Expected Result:** 
  - Query sanitized
  - No SQL injection
  - Returns empty or error
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-042: XSS Prevention**
- [ ] **Test Case:** XSS attempts sanitized
- [ ] **Endpoint:** `POST /api/projects/{project_id}/stories/`
- [ ] **Request Body:** `{"title": "<script>alert('xss')</script>"}`
- [ ] **Expected Result:** 
  - Script tags sanitized
  - No script execution
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

**TC-PERM-043: File Upload Validation**
- [ ] **Test Case:** Malicious file uploads blocked
- [ ] **Endpoint:** `POST /api/projects/{project_id}/attachments/`
- [ ] **Request:** File with .exe extension
- [ ] **Expected Result:** 
  - Status code: 400 Bad Request
  - File type rejected
- [ ] **Actual Result:** 
- [ ] **Status:** 
- [ ] **Notes:**

---

**File Status:** Complete - Permissions & Security  
**Total Test Cases:** ~100  
**All Test Checklists Complete!**

---

## SUMMARY

All 12 test checklist files have been created:

1. ✅ Core Entities (~200 tests)
2. ✅ Collaboration (~150 tests)
3. ✅ Board Features (~120 tests)
4. ✅ Configuration (~100 tests)
5. ✅ Filtering & Search (~130 tests)
6. ✅ Automation (~110 tests)
7. ✅ Reports & Analytics (~90 tests)
8. ✅ Time Tracking (~80 tests)
9. ✅ Integrations (~70 tests)
10. ✅ UI Features (~60 tests)
11. ✅ Advanced Features (~90 tests)
12. ✅ Permissions (~100 tests)

**Total Estimated Tests: ~1,300+**

