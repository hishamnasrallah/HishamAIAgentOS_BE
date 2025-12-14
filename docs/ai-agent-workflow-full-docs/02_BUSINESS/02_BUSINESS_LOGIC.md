# Business Logic - AI Agent Workflow Full SDLC

**Document Type:** Business Logic Specification  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 01_BUSINESS_REQUIREMENTS.md, 04_BUSINESS_RULES.md, ../04_BACKEND/03_SERVICES_IMPLEMENTATION.md  
**File Size:** 498 lines

---

## 📋 Purpose

This document defines the core business logic, workflows, and decision rules that govern the AI agent workflow enhancement system.

---

## 🔄 Core Business Workflows

### Workflow 1: Complete Project Generation

**Purpose:** Generate a production-ready project from an idea

**Steps:**
1. User submits project idea/requirements
2. System validates user permissions and organization limits
3. Workflow execution starts
4. Requirements generation (Agent)
5. User stories creation (API call via agent)
6. Sprint planning (API call via agent)
7. Code generation (Agent + File generation)
8. Test generation (Agent + File generation)
9. Documentation generation (Agent + File generation)
10. CI/CD config generation (File generation)
11. Repository initialization (Repository export)
12. Project packaging and export

**Business Rules:**
- BR-1: Check organization subscription tier limits
- BR-2: Validate file size limits
- BR-3: Check concurrent generation limits

**Error Handling:**
- If any step fails, rollback previous steps
- Log error for debugging
- Notify user of failure

---

### Workflow 2: Agent API Call

**Purpose:** Allow agent to call HishamOS API directly

**Steps:**
1. Agent requests API call via context
2. System validates agent has API calling capability
3. Authenticate request with user context
4. Authorize based on user permissions
5. Execute API call
6. Handle errors/retries
7. Return response to agent

**Business Rules:**
- BR-4: Only authenticated agents can make API calls
- BR-5: API calls must respect user permissions
- BR-6: Rate limiting applies to agent API calls

**Error Handling:**
- Retry failed requests (max 3 attempts)
- Log all API calls for audit
- Return structured error to agent

---

### Workflow 3: File Generation

**Purpose:** Generate project files on filesystem

**Steps:**
1. Receive file generation request
2. Validate project and user permissions
3. Create directory structure
4. Generate files from templates
5. Validate file paths and sizes
6. Write files to filesystem
7. Update database with file metadata
8. Return generation result

**Business Rules:**
- BR-7: Validate all file paths (prevent path traversal)
- BR-8: Enforce file size limits
- BR-9: Track file generation for audit

**Error Handling:**
- Rollback on file generation failure
- Cleanup partial files
- Log errors for debugging

---

### Workflow 4: Repository Export

**Purpose:** Export generated project as Git repository

**Steps:**
1. User requests repository export
2. Validate export limits (rate limiting)
3. Initialize Git repository
4. Add all generated files
5. Create initial commit
6. Generate .gitignore and README
7. Export based on type:
   - ZIP/TAR: Package and return download link
   - GitHub: Create repo and push code
   - GitLab: Create repo and push code
8. Update export status in database

**Business Rules:**
- BR-10: Check export frequency limits
- BR-11: Validate repository name format
- BR-12: Support private/public repositories

**Error Handling:**
- Handle Git operations errors
- Handle external API errors (GitHub/GitLab)
- Retry on transient failures

---

## 🎯 Decision Points and Business Rules

### Decision Point 1: Can User Generate Project?

**Condition:** User requests project generation

**Rules:**
- User must be authenticated
- User must have permission on project
- Organization must be active
- Must not exceed concurrent generation limit
- Must not exceed subscription tier limits

**Action:**
- Allow: Proceed with generation
- Deny: Return error with reason

---

### Decision Point 2: Can Agent Call API?

**Condition:** Agent requests API call

**Rules:**
- Agent must have API calling capability
- User context must be valid
- Request must be authenticated
- Must respect rate limits
- Must have required permissions

**Action:**
- Allow: Execute API call
- Deny: Return error to agent

---

### Decision Point 3: Can File Be Generated?

**Condition:** System receives file generation request

**Rules:**
- File path must be valid (no path traversal)
- File size must be within limits
- Directory must be writable
- User must have permission
- Must not exceed storage quota

**Action:**
- Allow: Generate file
- Deny: Return error with reason

---

### Decision Point 4: Can Repository Be Exported?

**Condition:** User requests repository export

**Rules:**
- Export type must be valid
- Must not exceed export frequency limits
- Repository name must be valid format
- User must have required tokens (GitHub/GitLab)
- Project must be generated successfully

**Action:**
- Allow: Proceed with export
- Deny: Return error with reason

---

## 📊 Business Calculations

### Calculation 1: Project Generation Time Estimate

**Formula:**
```
Estimated Time = 
  (Number of Files × Avg File Generation Time) +
  (Number of API Calls × Avg API Call Time) +
  (Repository Initialization Time) +
  (Buffer Time)
```

**Typical Values:**
- Avg File Generation Time: 50ms
- Avg API Call Time: 200ms
- Repository Initialization: 2s
- Buffer Time: 10s

**Example:**
- 100 files, 10 API calls
- Estimated: (100 × 0.05) + (10 × 0.2) + 2 + 10 = 19 seconds

---

### Calculation 2: Storage Quota Usage

**Formula:**
```
Storage Used = Sum of all file sizes in generated projects
Storage Quota = Organization subscription tier limit
Usage Percentage = (Storage Used / Storage Quota) × 100
```

**Business Rules:**
- Free tier: 1GB quota
- Pro tier: 10GB quota
- Enterprise tier: Unlimited

---

### Calculation 3: Export Rate Limit Check

**Formula:**
```
Exports Today = Count of exports in last 24 hours
Rate Limit = Organization subscription tier limit
Can Export = Exports Today < Rate Limit
```

**Business Rules:**
- Free tier: 10 exports/day
- Pro tier: 100 exports/day
- Enterprise tier: Unlimited

---

## 🔐 Permission Logic

### Permission 1: Project Generation

**Required Permission:** `projects.generate_project`

**Check:**
- User must be project member or owner
- Organization must have active subscription
- User must not be blocked

**Super Admin Bypass:** ✅ Yes

---

### Permission 2: File Generation

**Required Permission:** `projects.generate_files`

**Check:**
- User must have project generation permission
- User must have write access to project

**Super Admin Bypass:** ✅ Yes

---

### Permission 3: Repository Export

**Required Permission:** `projects.export_repository`

**Check:**
- User must have project generation permission
- User must own generated project or be project owner

**Super Admin Bypass:** ✅ Yes

---

## 🔄 State Transitions

### GeneratedProject State Machine

```
Pending → Generating → Completed
   ↓          ↓           ↓
Failed    Failed      Archived
```

**Transitions:**
- `Pending → Generating`: Workflow starts
- `Generating → Completed`: All files generated successfully
- `Generating → Failed`: Error during generation
- `Completed → Archived`: Project archived after retention period

---

### RepositoryExport State Machine

```
Pending → Exporting → Completed
   ↓         ↓           ↓
Failed    Failed      (End)
```

**Transitions:**
- `Pending → Exporting`: Export job starts
- `Exporting → Completed`: Export successful
- `Exporting → Failed`: Error during export

---

## 📈 Business Metrics and KPIs

### Metric 1: Project Generation Success Rate

**Calculation:**
```
Success Rate = (Successful Generations / Total Generations) × 100
Target: > 95%
```

**Tracking:**
- Monitor daily
- Alert if < 90%
- Review failures weekly

---

### Metric 2: Average Generation Time

**Calculation:**
```
Average Time = Sum of Generation Times / Number of Generations
Target: < 5 minutes for typical project
```

**Tracking:**
- Monitor daily
- Alert if > 10 minutes
- Optimize slow workflows

---

### Metric 3: Export Success Rate

**Calculation:**
```
Success Rate = (Successful Exports / Total Exports) × 100
Target: > 98%
```

**Tracking:**
- Monitor daily
- Alert if < 95%
- Review failures weekly

---

## 🔗 Related Documentation

- **Business Requirements:** `01_BUSINESS_REQUIREMENTS.md`
- **Business Rules:** `04_BUSINESS_RULES.md`
- **User Stories:** `03_USER_STORIES.md`
- **Services Implementation:** `../04_BACKEND/03_SERVICES_IMPLEMENTATION.md`

---

**Document Owner:** Product Management  
**Review Cycle:** Quarterly  
**Last Updated:** 2025-12-13

