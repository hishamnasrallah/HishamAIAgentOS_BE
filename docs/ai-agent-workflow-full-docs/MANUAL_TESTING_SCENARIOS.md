# Manual Testing Scenarios - Complete Test Cases

**Document Type:** Manual Testing Guide  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Purpose:** Comprehensive manual testing scenarios covering all use cases

---

## 📋 Test Scenario Organization

Scenarios are organized by:
- **Feature Area** (Authentication, Projects, Workflows, etc.)
- **User Type** (Regular User, Admin, Agent)
- **Priority** (P0 - Critical, P1 - High, P2 - Medium, P3 - Low)
- **Complexity** (Simple, Medium, Complex)

---

## 🔐 Authentication & Authorization Scenarios

### TC-AUTH-001: Login and Access Control

**Priority:** P0 (Critical)  
**Complexity:** Simple  
**User Type:** Regular User

**Steps:**
1. Navigate to login page
2. Enter valid credentials
3. Submit login form

**Expected Results:**
- ✅ User is authenticated
- ✅ JWT token is received and stored
- ✅ User is redirected to dashboard
- ✅ Token is included in all subsequent API requests

**Validation:**
- Check browser localStorage/sessionStorage for token
- Check Network tab - Authorization header present in requests

---

### TC-AUTH-002: Permission-Based Access

**Priority:** P0  
**Complexity:** Medium  
**User Type:** Regular User (Non-Project Member)

**Prerequisites:**
- User exists but is NOT member of Project A
- Project A has generated projects

**Steps:**
1. Login as non-member user
2. Navigate to `/projects/{project-a-id}/generated`
3. Attempt to view generated projects
4. Attempt to generate new project

**Expected Results:**
- ✅ Generated projects list is empty (or 403 error)
- ✅ Generate button is disabled/hidden (or 403 error)
- ✅ API returns 403 Forbidden or empty results

**Validation:**
- Check API response status codes
- Check frontend error messages
- Verify organization-based filtering works

---

## 📁 Project Generation Scenarios

### TC-GEN-001: Simple Project Generation via API

**Priority:** P0  
**Complexity:** Simple  
**User Type:** Regular User

**Prerequisites:**
- User is authenticated
- User has a project
- A workflow exists with file_generation steps

**Steps:**
1. Create workflow with single file_generation step:
   ```json
   {
     "step_type": "file_generation",
     "config": {
       "file_path": "hello.txt",
       "content": "Hello, World!"
     }
   }
   ```
2. Call generation API:
   ```bash
   POST /api/v1/projects/generated-projects/generate/
   {
     "workflow_id": "<workflow-id>",
     "input_data": {
       "project_id": "<project-id>"
     }
   }
   ```
3. Wait for task completion (poll status)
4. Check generated files

**Expected Results:**
- ✅ API returns 202 Accepted with task_id
- ✅ GeneratedProject created with status 'generating'
- ✅ Celery task executes
- ✅ Status changes to 'completed'
- ✅ File `hello.txt` exists in generated project
- ✅ ProjectFile record created
- ✅ File content is correct

**Validation:**
- Check GeneratedProject.status
- Check ProjectFile records
- Verify file exists on filesystem
- Verify file content matches

---

### TC-GEN-002: Complex Multi-File Project Generation

**Priority:** P1  
**Complexity:** Complex  
**User Type:** Regular User

**Prerequisites:**
- User authenticated
- Project exists
- Workflow with multiple file_generation steps

**Steps:**
1. Create workflow with multiple files:
   - `src/main.py` - Python code
   - `src/utils.py` - Python code
   - `tests/test_main.py` - Python test
   - `requirements.txt` - Dependencies
   - `README.md` - Documentation
   - `.gitignore` - Git ignore file
2. Execute generation
3. Verify all files created
4. Verify directory structure
5. Verify file types detected correctly

**Expected Results:**
- ✅ All 6 files created
- ✅ Directory structure preserved (`src/`, `tests/`)
- ✅ File types correct (python, markdown, text)
- ✅ Total file count = 6
- ✅ Total size > 0
- ✅ All files accessible via API

**Validation:**
- List all ProjectFile records
- Verify file_paths are correct
- Check file_type assignments
- Verify content_hash for each file

---

### TC-GEN-003: Project Generation with Large Files

**Priority:** P2  
**Complexity:** Medium  
**User Type:** Regular User

**Steps:**
1. Create workflow generating file close to MAX_FILE_SIZE limit
2. Execute generation
3. Try generating file exceeding MAX_FILE_SIZE

**Expected Results:**
- ✅ File within limit: Generated successfully
- ✅ File exceeding limit: Generation fails with error
- ✅ Error message indicates file size limit
- ✅ GeneratedProject status = 'failed'
- ✅ error_message contains size limit information

**Validation:**
- Check error_message field
- Verify no partial files created
- Check service logs

---

### TC-GEN-004: Project Generation with Path Traversal Attempt

**Priority:** P0  
**Complexity:** Simple  
**User Type:** Regular User (Security Test)

**Steps:**
1. Create workflow with malicious file paths:
   - `../../../etc/passwd`
   - `..\\..\\windows\\system32\\config\\sam`
   - `/absolute/path/file.txt`
   - `file\0with\0null.txt`
2. Execute generation

**Expected Results:**
- ✅ All malicious paths rejected
- ✅ Generation fails or paths sanitized
- ✅ No files created outside project directory
- ✅ Error logged

**Validation:**
- Verify no files created outside GENERATED_PROJECTS_DIR
- Check ProjectGenerationError raised
- Review security logs

---

### TC-GEN-005: Concurrent Project Generation

**Priority:** P2  
**Complexity:** Complex  
**User Type:** Regular User

**Steps:**
1. Start 5 generation tasks simultaneously
2. Monitor all tasks
3. Verify all complete successfully

**Expected Results:**
- ✅ All 5 tasks accepted (202 responses)
- ✅ All execute concurrently
- ✅ All complete without conflicts
- ✅ All generated projects accessible
- ✅ No database deadlocks
- ✅ No file system conflicts

**Validation:**
- Check all GeneratedProject records
- Verify unique output directories
- Check Celery worker logs

---

## 🔄 Workflow Integration Scenarios

### TC-WF-001: API Call Step Execution

**Priority:** P0  
**Complexity:** Medium  
**User Type:** Regular User

**Prerequisites:**
- Workflow with api_call step type

**Steps:**
1. Create workflow with api_call step:
   ```json
   {
     "step_type": "api_call",
     "config": {
       "method": "POST",
       "endpoint": "/api/v1/projects/stories/",
       "data": {
         "project": "<project-id>",
         "title": "Story from Workflow",
         "description": "Created by agent"
       }
     }
   }
   ```
2. Execute workflow
3. Verify story was created

**Expected Results:**
- ✅ Workflow executes successfully
- ✅ Story created in project
- ✅ Story has correct title and description
- ✅ API call authenticated correctly
- ✅ Response captured in workflow context

**Validation:**
- Check UserStory records in database
- Verify story.project matches
- Check workflow execution logs

---

### TC-WF-002: File Generation Step Execution

**Priority:** P0  
**Complexity:** Simple  
**User Type:** Regular User

**Steps:**
1. Create workflow with file_generation step
2. Execute workflow
3. Verify files generated

**Expected Results:**
- ✅ Step executes successfully
- ✅ Files created
- ✅ ProjectFile records created
- ✅ Statistics updated

**Validation:**
- Same as TC-GEN-001

---

### TC-WF-003: Repository Creation Step Execution

**Priority:** P1  
**Complexity:** Medium  
**User Type:** Regular User

**Prerequisites:**
- GitHub/GitLab token available (optional)

**Steps:**
1. Create workflow with repo_creation step
2. Configure for ZIP export
3. Execute workflow
4. Verify export created

**Expected Results:**
- ✅ RepositoryExport record created
- ✅ Export status = 'completed'
- ✅ Archive file created
- ✅ Archive_path populated

**Validation:**
- Check RepositoryExport record
- Verify archive file exists
- Check archive contents

---

### TC-WF-004: Multi-Step Workflow Execution

**Priority:** P1  
**Complexity:** Complex  
**User Type:** Regular User

**Steps:**
1. Create workflow with sequence:
   - Step 1: api_call (create story)
   - Step 2: file_generation (create config)
   - Step 3: file_generation (create README)
   - Step 4: repo_creation (export to ZIP)
2. Execute workflow
3. Verify all steps execute in order
4. Verify step outputs available to subsequent steps

**Expected Results:**
- ✅ All steps execute in order
- ✅ Step 1 creates story
- ✅ Steps 2-3 create files
- ✅ Step 4 creates export
- ✅ Context passed between steps
- ✅ Workflow completes successfully

**Validation:**
- Check story creation
- Check file creation
- Check export creation
- Review workflow execution logs

---

## 📤 Export Scenarios

### TC-EXP-001: ZIP Export

**Priority:** P0  
**Complexity:** Simple  
**User Type:** Regular User

**Prerequisites:**
- Generated project exists with files

**Steps:**
1. Navigate to generated project detail
2. Go to Exports tab
3. Select "ZIP Archive"
4. Click "Export Project"
5. Wait for completion
6. Download archive
7. Extract and verify contents

**Expected Results:**
- ✅ Export status: 'exporting' → 'completed'
- ✅ Archive_path populated
- ✅ Archive_size > 0
- ✅ Download button appears
- ✅ ZIP file downloads
- ✅ Extracted files match original structure
- ✅ All files present and readable

**Validation:**
- Check RepositoryExport record
- Verify archive file on filesystem
- Extract and compare files
- Check file permissions

---

### TC-EXP-002: TAR.GZ Export

**Priority:** P1  
**Complexity:** Simple  
**User Type:** Regular User

**Steps:**
1. Create export with type 'tar.gz'
2. Wait for completion
3. Download and verify

**Expected Results:**
- ✅ TAR.GZ archive created
- ✅ File extension is .tar.gz
- ✅ Archive is gzip compressed
- ✅ Contents match original

**Validation:**
- Extract TAR.GZ and verify
- Check compression ratio

---

### TC-EXP-003: GitHub Export (Success)

**Priority:** P1  
**Complexity:** Medium  
**User Type:** Regular User

**Prerequisites:**
- Valid GitHub Personal Access Token
- Generated project exists
- Git installed on server

**Steps:**
1. Navigate to Exports tab
2. Select "GitHub Repository"
3. Enter repository name
4. Enter GitHub token
5. Select private/public
6. Click "Export Project"
7. Wait for completion
8. Visit GitHub repository URL

**Expected Results:**
- ✅ Export status: 'exporting' → 'completed'
- ✅ Repository created on GitHub
- ✅ repository_url populated
- ✅ All files pushed to repository
- ✅ Repository accessible on GitHub
- ✅ Files match generated project

**Validation:**
- Visit repository_url
- Verify files on GitHub
- Check commit history
- Verify repository settings (private/public)

---

### TC-EXP-004: GitHub Export (Invalid Token)

**Priority:** P1  
**Complexity:** Simple  
**User Type:** Regular User

**Steps:**
1. Use invalid/expired GitHub token
2. Attempt export
3. Monitor error

**Expected Results:**
- ✅ Export status: 'exporting' → 'failed'
- ✅ error_message contains authentication error
- ✅ No repository created
- ✅ User sees error message

**Validation:**
- Check RepositoryExport.error_message
- Verify no repository on GitHub
- Check frontend error display

---

### TC-EXP-005: GitLab Export

**Priority:** P1  
**Complexity:** Medium  
**User Type:** Regular User

**Prerequisites:**
- Valid GitLab Personal Access Token
- Generated project exists

**Steps:**
1. Select "GitLab Repository"
2. Enter project name
3. Enter namespace (optional)
4. Enter GitLab token
5. Select visibility
6. Export and verify

**Expected Results:**
- ✅ Repository created on GitLab
- ✅ repository_url populated
- ✅ All files present
- ✅ Visibility settings correct

**Validation:**
- Visit repository_url
- Verify files and settings

---

### TC-EXP-006: Export Failure Recovery

**Priority:** P2  
**Complexity:** Medium  
**User Type:** Regular User

**Steps:**
1. Start export
2. Simulate failure (kill Celery worker mid-export)
3. Restart worker
4. Check export status
5. Retry export

**Expected Results:**
- ✅ Export status remains 'exporting' or 'failed'
- ✅ Error logged
- ✅ Retry possible
- ✅ Second attempt succeeds

**Validation:**
- Check export status
- Review error logs
- Verify retry works

---

## 🖥️ Frontend UI Scenarios

### TC-UI-001: Generated Projects List Page

**Priority:** P0  
**Complexity:** Simple  
**User Type:** Regular User

**Steps:**
1. Navigate to `/projects/{id}/generated`
2. View list of generated projects

**Expected Results:**
- ✅ Page loads without errors
- ✅ All generated projects displayed
- ✅ Status badges show correct colors
- ✅ File counts displayed
- ✅ Export counts displayed
- ✅ Creation dates shown
- ✅ "Generate New Project" button visible
- ✅ Clicking project navigates to detail page

**Validation:**
- Check browser console for errors
- Verify data matches API response
- Test all interactive elements

---

### TC-UI-002: Project Generator Page

**Priority:** P0  
**Complexity:** Simple  
**User Type:** Regular User

**Steps:**
1. Navigate to `/projects/{id}/generate`
2. Fill in form fields
3. Submit form
4. Monitor progress

**Expected Results:**
- ✅ Form renders correctly
- ✅ Validation works (required fields)
- ✅ Submit button triggers generation
- ✅ Loading state shown during submission
- ✅ Success notification appears
- ✅ Redirects to generated project detail
- ✅ Error messages shown if validation fails

**Validation:**
- Test form validation
- Test submission
- Verify redirect
- Check notifications

---

### TC-UI-003: Generated Project Detail Page

**Priority:** P0  
**Complexity:** Medium  
**User Type:** Regular User

**Steps:**
1. Navigate to generated project detail
2. View Overview section
3. Click Files tab
4. Click Exports tab
5. Test file selection
6. Test export controls

**Expected Results:**
- ✅ Overview shows correct statistics
- ✅ Status badge displays correctly
- ✅ Files tab shows file tree
- ✅ File tree is navigable
- ✅ Selecting file shows content
- ✅ Syntax highlighting works
- ✅ Exports tab shows export controls
- ✅ Recent exports list displays
- ✅ Download buttons work

**Validation:**
- Test all tabs
- Test file tree interaction
- Test file viewer
- Test export functionality

---

### TC-UI-004: File Tree Component

**Priority:** P1  
**Complexity:** Medium  
**User Type:** Regular User

**Steps:**
1. Open Files tab with multiple files in subdirectories
2. Test folder expansion/collapse
3. Test file selection
4. Test tree navigation

**Expected Results:**
- ✅ Tree structure built correctly from flat list
- ✅ Folders show expand/collapse icons
- ✅ Clicking folder toggles expansion
- ✅ Clicking file selects it
- ✅ Selected file highlighted
- ✅ Icons differentiate files and folders
- ✅ Proper indentation for hierarchy

**Validation:**
- Test with various directory structures
- Test with many files
- Verify selection callback works

---

### TC-UI-005: File Viewer Component

**Priority:** P1  
**Complexity:** Medium  
**User Type:** Regular User

**Steps:**
1. Select different file types:
   - Python file (.py)
   - JavaScript file (.js)
   - Markdown file (.md)
   - JSON file (.json)
   - Text file (.txt)
2. Verify syntax highlighting
3. Test with large files
4. Test with binary files (should show error)

**Expected Results:**
- ✅ Python files show Python syntax highlighting
- ✅ JavaScript files show JS highlighting
- ✅ Markdown files formatted correctly
- ✅ JSON files formatted and highlighted
- ✅ Text files show as plain text
- ✅ Line numbers displayed (if enabled)
- ✅ Large files load (or show warning)
- ✅ Binary files show appropriate message

**Validation:**
- Test all supported languages
- Verify highlighting accuracy
- Test edge cases

---

### TC-UI-006: Export Controls Component

**Priority:** P1  
**Complexity:** Medium  
**User Type:** Regular User

**Steps:**
1. Test ZIP export flow
2. Test GitHub export flow
3. Test GitLab export flow
4. Test form validation
5. Test export status updates

**Expected Results:**
- ✅ Export type selector works
- ✅ Conditional fields show/hide correctly
- ✅ Form validation prevents invalid submissions
- ✅ Loading state during export
- ✅ Success/error notifications
- ✅ Recent exports list updates
- ✅ Download buttons appear when ready
- ✅ Repository links work

**Validation:**
- Test all export types
- Test validation
- Test real-time updates

---

## 🔧 Edge Cases & Error Scenarios

### TC-ERR-001: Workflow Execution Failure

**Priority:** P1  
**Complexity:** Medium  
**User Type:** Regular User

**Steps:**
1. Create workflow with invalid step configuration
2. Execute workflow
3. Monitor error handling

**Expected Results:**
- ✅ Workflow execution fails gracefully
- ✅ GeneratedProject status = 'failed'
- ✅ Error message stored
- ✅ User sees error notification
- ✅ No partial state left behind

**Validation:**
- Check error_message field
- Verify status update
- Check cleanup

---

### TC-ERR-002: Network Failure During Export

**Priority:** P2  
**Complexity:** Medium  
**User Type:** Regular User

**Steps:**
1. Start GitHub export
2. Simulate network failure (disable internet)
3. Check error handling

**Expected Results:**
- ✅ Export status = 'failed'
- ✅ Error message indicates network issue
- ✅ Retry possible
- ✅ No corrupted state

**Validation:**
- Check error handling
- Test retry mechanism

---

### TC-ERR-003: Concurrent Modifications

**Priority:** P2  
**Complexity:** Complex  
**User Type:** Multiple Users

**Steps:**
1. User A starts generation
2. User B deletes project
3. Check error handling

**Expected Results:**
- ✅ Error handled gracefully
- ✅ No crashes
- ✅ User A sees appropriate error
- ✅ Database integrity maintained

**Validation:**
- Test concurrent operations
- Verify error messages

---

### TC-ERR-004: Disk Space Exhaustion

**Priority:** P2  
**Complexity:** Medium  
**User Type:** System Test

**Steps:**
1. Fill disk to near capacity
2. Attempt project generation
3. Monitor error handling

**Expected Results:**
- ✅ Generation fails gracefully
- ✅ Error message indicates disk space
- ✅ No partial files left
- ✅ System remains stable

**Validation:**
- Check error handling
- Verify cleanup

---

## 📊 Performance Scenarios

### TC-PERF-001: Large Project Generation

**Priority:** P2  
**Complexity:** Complex  
**User Type:** Regular User

**Steps:**
1. Generate project with 1000+ files
2. Monitor generation time
3. Verify all files created
4. Test UI performance with large file list

**Expected Results:**
- ✅ Generation completes successfully
- ✅ All files created
- ✅ UI remains responsive
- ✅ File tree renders efficiently
- ✅ Pagination works (if implemented)

**Validation:**
- Check generation time
- Verify file count
- Test UI responsiveness

---

### TC-PERF-002: Multiple Concurrent Exports

**Priority:** P2  
**Complexity:** Complex  
**User Type:** Regular User

**Steps:**
1. Start 10 ZIP exports simultaneously
2. Monitor system resources
3. Verify all complete

**Expected Results:**
- ✅ All exports accepted
- ✅ System handles load
- ✅ All exports complete
- ✅ No resource exhaustion

**Validation:**
- Monitor CPU/memory
- Check all exports succeed

---

## 🔒 Security Scenarios

### TC-SEC-001: Path Traversal Prevention

**Priority:** P0  
**Complexity:** Simple  
**User Type:** Security Test

**Steps:**
1. Attempt to generate files with path traversal:
   - `../../etc/passwd`
   - `..\\..\\windows\\system32\\config\\sam`
2. Verify prevention

**Expected Results:**
- ✅ All attempts blocked
- ✅ Error logged
- ✅ No files outside project directory

**Validation:**
- Verify file system
- Check logs

---

### TC-SEC-002: Permission Bypass Attempt

**Priority:** P0  
**Complexity:** Simple  
**User Type:** Security Test

**Steps:**
1. User A (non-member) attempts to access Project B's generated projects
2. Attempt to modify another user's generated project
3. Attempt to delete another user's export

**Expected Results:**
- ✅ All unauthorized access blocked
- ✅ 403 Forbidden returned
- ✅ Frontend shows error
- ✅ No data exposed

**Validation:**
- Test all CRUD operations
- Verify permission checks

---

### TC-SEC-003: File Size Limit Enforcement

**Priority:** P1  
**Complexity:** Simple  
**User Type:** Security Test

**Steps:**
1. Attempt to generate file exceeding MAX_FILE_SIZE
2. Verify rejection

**Expected Results:**
- ✅ File rejected
- ✅ Error message clear
- ✅ No partial writes

**Validation:**
- Test with various sizes
- Verify limits enforced

---

## 📝 Regression Testing Scenarios

### TC-REG-001: Existing Features Still Work

**Priority:** P0  
**Complexity:** Medium  
**User Type:** Regular User

**Steps:**
1. Test existing project management features
2. Test existing workflow features
3. Verify no regressions

**Expected Results:**
- ✅ All existing features work
- ✅ No breaking changes
- ✅ Performance maintained

**Validation:**
- Full regression suite
- Compare before/after

---

## ✅ Test Execution Summary

### Pre-Testing Checklist

- [ ] Backend server running
- [ ] Celery worker running
- [ ] Frontend dev server running
- [ ] Database migrated
- [ ] Test user created
- [ ] Test project created
- [ ] Workflows created

### Post-Testing Checklist

- [ ] All P0 scenarios passed
- [ ] Critical bugs fixed
- [ ] Documentation updated
- [ ] Test results documented

---

**Last Updated:** 2025-12-13  
**Version:** 1.0.0

