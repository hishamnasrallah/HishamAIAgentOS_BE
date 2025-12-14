# Business Rules - AI Agent Workflow Full SDLC

**Document Type:** Business Rules Specification  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 01_BUSINESS_REQUIREMENTS.md, 02_BUSINESS_LOGIC.md, ../04_BACKEND/06_PERMISSIONS_IMPLEMENTATION.md  
**File Size:** 488 lines

---

## 📋 Purpose

This document defines all business rules, validation rules, and constraints that govern the AI agent workflow enhancement system.

---

## 🔐 Access Control Rules

### BR-1: Project Generation Permission

**Rule:** Only authorized users can generate projects  
**Enforcement:** Backend permission check  
**Scope:** Global

**Details:**
- User must be authenticated
- User must be project member or owner
- Organization must be active
- Organization subscription must be valid

**Exceptions:**
- Super admins bypass all checks

**Error Message:** "You don't have permission to generate projects for this project."

---

### BR-2: File Generation Permission

**Rule:** Only authorized users can generate files  
**Enforcement:** Backend permission check  
**Scope:** Project-level

**Details:**
- User must have project generation permission
- User must have write access to project
- Project must exist and be accessible

**Exceptions:**
- Super admins bypass all checks

**Error Message:** "You don't have permission to generate files for this project."

---

### BR-3: Repository Export Permission

**Rule:** Only authorized users can export repositories  
**Enforcement:** Backend permission check  
**Scope:** Generated project-level

**Details:**
- User must own generated project or be project owner
- Generated project must be in completed status
- Export limits must not be exceeded

**Exceptions:**
- Super admins bypass all checks

**Error Message:** "You don't have permission to export this project."

---

## 📊 Resource Limit Rules

### BR-4: Concurrent Generation Limit

**Rule:** Organizations have limits on concurrent project generations  
**Enforcement:** Backend validation  
**Scope:** Organization-level

**Details:**
- Free tier: 1 concurrent generation
- Pro tier: 5 concurrent generations
- Enterprise tier: Unlimited

**Calculation:**
```
Active Generations = Count of GeneratedProjects with status='generating' 
                    for organization
Can Start Generation = Active Generations < Limit
```

**Exceptions:**
- Super admins bypass limits

**Error Message:** "Concurrent generation limit reached. Please wait for current generation to complete."

---

### BR-5: File Size Limit

**Rule:** Individual files cannot exceed size limits  
**Enforcement:** Backend validation  
**Scope:** File-level

**Details:**
- Default limit: 10MB per file
- Configurable per organization (up to 100MB)
- Total project size limit: 1GB

**Calculation:**
```
File Size Check = file_size <= file_size_limit
Project Size Check = total_project_size <= project_size_limit
```

**Exceptions:**
- Super admins can configure higher limits

**Error Message:** "File size exceeds limit. Maximum size: {limit}MB"

---

### BR-6: Storage Quota Limit

**Rule:** Organizations have storage quotas for generated projects  
**Enforcement:** Backend validation  
**Scope:** Organization-level

**Details:**
- Free tier: 1GB quota
- Pro tier: 10GB quota
- Enterprise tier: Unlimited

**Calculation:**
```
Storage Used = Sum of total_size for all GeneratedProjects 
               in organization with status != 'archived'
Can Generate = Storage Used + Estimated Size < Quota
```

**Exceptions:**
- Super admins bypass quotas

**Error Message:** "Storage quota exceeded. Current usage: {used}/{quota}GB"

---

### BR-7: Export Rate Limit

**Rule:** Export frequency is limited to prevent abuse  
**Enforcement:** Rate limiting  
**Scope:** User-level, per organization

**Details:**
- Free tier: 10 exports per day
- Pro tier: 100 exports per day
- Enterprise tier: Unlimited

**Calculation:**
```
Exports Today = Count of RepositoryExports 
                created in last 24 hours by user in organization
Can Export = Exports Today < Daily Limit
```

**Exceptions:**
- Super admins bypass limits

**Error Message:** "Export rate limit reached. Limit: {limit} exports per day"

---

## ✅ Validation Rules

### BR-8: File Path Validation

**Rule:** File paths must be valid and secure  
**Enforcement:** Backend validation  
**Scope:** File-level

**Details:**
- Paths must be relative (no absolute paths)
- No path traversal sequences (../, ..\\)
- No null bytes
- Valid characters only
- Maximum path length: 500 characters

**Validation Regex:**
```
^[a-zA-Z0-9_/\\.-]+$
No: ../, ..\\, \0, ..
```

**Error Message:** "Invalid file path. Path must be relative and contain only valid characters."

---

### BR-9: Repository Name Validation

**Rule:** Repository names must be valid  
**Enforcement:** Backend validation  
**Scope:** Export-level

**Details:**
- Must match GitHub/GitLab naming rules
- 1-100 characters
- Alphanumeric, hyphens, underscores only
- Cannot start/end with hyphen
- Must be unique in user's namespace

**Validation Regex:**
```
^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$
```

**Error Message:** "Invalid repository name. Must be 1-100 characters, alphanumeric with hyphens/underscores."

---

### BR-10: Project Generation Validation

**Rule:** Project generation requests must be valid  
**Enforcement:** Backend validation  
**Scope:** Request-level

**Details:**
- Project must exist
- Project must be accessible to user
- Workflow must be valid
- Input data must be valid JSON
- Required parameters must be present

**Error Message:** "Invalid project generation request. {specific validation error}"

---

## 🔄 State Transition Rules

### BR-11: GeneratedProject State Transitions

**Rule:** State transitions must follow valid paths  
**Enforcement:** Backend validation  
**Scope:** GeneratedProject-level

**Valid Transitions:**
- `pending → generating` ✅
- `generating → completed` ✅
- `generating → failed` ✅
- `completed → archived` ✅

**Invalid Transitions:**
- `completed → generating` ❌
- `failed → completed` ❌
- `archived → generating` ❌

**Error Message:** "Invalid state transition from {current} to {new}"

---

### BR-12: RepositoryExport State Transitions

**Rule:** State transitions must follow valid paths  
**Enforcement:** Backend validation  
**Scope:** RepositoryExport-level

**Valid Transitions:**
- `pending → exporting` ✅
- `exporting → completed` ✅
- `exporting → failed` ✅

**Invalid Transitions:**
- `completed → exporting` ❌
- `failed → exporting` ❌

**Error Message:** "Invalid state transition from {current} to {new}"

---

## 🔐 Security Rules

### BR-13: API Call Authentication

**Rule:** All agent API calls must be authenticated  
**Enforcement:** Backend middleware  
**Scope:** API-level

**Details:**
- Must include valid JWT token
- Token must belong to valid user
- Token must not be expired
- User must be active

**Error Message:** "Authentication required" (401)

---

### BR-14: API Call Authorization

**Rule:** API calls must respect user permissions  
**Enforcement:** Backend permission check  
**Scope:** API-level

**Details:**
- User must have permission for requested action
- Resource must be accessible to user
- Organization-level checks apply

**Error Message:** "Permission denied" (403)

---

### BR-15: File Path Security

**Rule:** File paths must not allow path traversal  
**Enforcement:** Backend validation  
**Scope:** File-level

**Details:**
- No absolute paths allowed
- No ../ or ..\\ sequences
- Paths must be within project directory
- Symlinks not followed

**Error Message:** "Invalid file path. Path traversal not allowed."

---

## 📈 Business Calculation Rules

### BR-16: Generation Time Estimation

**Rule:** System must estimate generation time  
**Calculation:** See BR-16 in Business Logic

**Usage:**
- Display to user before generation
- Used for progress tracking
- Used for resource allocation

---

### BR-17: Storage Usage Calculation

**Rule:** System must track storage usage accurately  
**Calculation:**
```
Storage Used = Sum of total_size for non-archived GeneratedProjects
Storage Percentage = (Storage Used / Quota) × 100
```

**Usage:**
- Display to user
- Enforce quota limits
- Alert when approaching limit

---

## 🔄 Data Retention Rules

### BR-18: Generated Project Retention

**Rule:** Generated projects are retained for specified period  
**Enforcement:** Automated cleanup job  
**Scope:** Organization-level

**Details:**
- Default retention: 30 days
- Configurable per organization (7-365 days)
- Archived projects retained longer (90 days)
- Files deleted from filesystem on expiration

**Calculation:**
```
Should Delete = (current_date - created_at) > retention_period 
                AND status != 'archived'
```

---

## ✅ Rule Enforcement Summary

| Rule ID | Category | Enforcement | Scope | Super Admin Bypass |
|---------|----------|-------------|-------|-------------------|
| BR-1 | Access | Backend | Global | ✅ |
| BR-2 | Access | Backend | Project | ✅ |
| BR-3 | Access | Backend | Generated Project | ✅ |
| BR-4 | Resource | Backend | Organization | ✅ |
| BR-5 | Resource | Backend | File | ⚠️ Configurable |
| BR-6 | Resource | Backend | Organization | ✅ |
| BR-7 | Resource | Rate Limiting | User/Org | ✅ |
| BR-8 | Validation | Backend | File | ❌ |
| BR-9 | Validation | Backend | Export | ❌ |
| BR-10 | Validation | Backend | Request | ❌ |
| BR-11 | State | Backend | GeneratedProject | ❌ |
| BR-12 | State | Backend | RepositoryExport | ❌ |
| BR-13 | Security | Backend | API | ❌ |
| BR-14 | Security | Backend | API | ✅ |
| BR-15 | Security | Backend | File | ❌ |
| BR-16 | Calculation | Backend | System | N/A |
| BR-17 | Calculation | Backend | System | N/A |
| BR-18 | Retention | Automated | Organization | ⚠️ Configurable |

---

## 🔗 Related Documentation

- **Business Requirements:** `01_BUSINESS_REQUIREMENTS.md`
- **Business Logic:** `02_BUSINESS_LOGIC.md`
- **Permissions:** `../04_BACKEND/06_PERMISSIONS_IMPLEMENTATION.md`
- **Security:** `../08_SECURITY/`

---

**Document Owner:** Product Management & Security Team  
**Review Cycle:** Quarterly  
**Last Updated:** 2025-12-13

