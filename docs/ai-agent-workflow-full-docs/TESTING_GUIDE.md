# Complete Testing Guide - AI Agent Workflow System

**Document Type:** Testing Guide  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Related Documents:** IMPLEMENTATION_CHECKLIST.md, MANUAL_TESTING_SCENARIOS.md

---

## 📋 Table of Contents

1. [High-Level Overview](#high-level-overview)
2. [System Architecture Overview](#system-architecture-overview)
3. [Testing Environment Setup](#testing-environment-setup)
4. [Low-Level Step-by-Step Testing](#low-level-step-by-step-testing)
5. [Workflow Testing](#workflow-testing)
6. [Integration Testing](#integration-testing)
7. [Troubleshooting Guide](#troubleshooting-guide)

---

## 🎯 High-Level Overview

### What Are We Testing?

The AI Agent Workflow System enables:
1. **Agent API Integration** - AI agents can call HishamOS APIs directly
2. **Project File Generation** - Automatically generate project file structures
3. **Repository Export** - Export generated projects to ZIP, TAR, GitHub, or GitLab
4. **Full Workflow Automation** - Complete SDLC automation through workflows

### System Flow (High-Level)

```
User → Workflow Builder → Define Workflow → Execute Workflow
                                 ↓
                    [Agent Steps Execute]
                                 ↓
                    [API Calls, File Generation, Export]
                                 ↓
                    Generated Project → Files → Exports
```

---

## 🏗️ System Architecture Overview

### Components to Test

1. **Backend Services**
   - `AgentAPICaller` - Agent API integration
   - `ProjectGenerator` - File generation
   - `RepositoryExporter` - Project export

2. **Backend Models**
   - `GeneratedProject` - Tracks generated projects
   - `ProjectFile` - Tracks individual files
   - `RepositoryExport` - Tracks export operations

3. **API Endpoints**
   - `/api/v1/projects/generated-projects/` - Project management
   - `/api/v1/projects/project-files/` - File management
   - `/api/v1/projects/repository-exports/` - Export management

4. **Frontend Pages**
   - Generated Projects List
   - Project Generator
   - Project Detail (with files and exports)

5. **Workflow Integration**
   - New step types: `api_call`, `file_generation`, `repo_creation`

---

## 🔧 Testing Environment Setup

### Prerequisites

```bash
# 1. Activate virtual environment
cd backend
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# 2. Install dependencies (if needed)
pip install -r requirements.txt

# 3. Ensure database is migrated
python manage.py migrate

# 4. Start backend server
python manage.py runserver

# 5. In another terminal, start Celery worker (for async tasks)
celery -A core worker --loglevel=info

# 6. In another terminal, start frontend
cd frontend
npm install  # If needed
npm run dev
```

### Environment Variables Needed

```bash
# backend/.env
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3  # or your DB URL
CELERY_BROKER_URL=redis://localhost:6379/0  # or your broker
GENERATED_PROJECTS_DIR=./generated_projects
BACKEND_URL=http://localhost:8000
MAX_FILE_SIZE=10485760  # 10MB in bytes
```

### Test Data Setup

```python
# Create test user (via Django admin or shell)
python manage.py createsuperuser

# Or via Django shell:
python manage.py shell
>>> from apps.authentication.models import User
>>> user = User.objects.create_user(
...     email='test@example.com',
...     password='testpass123',
...     username='testuser'
... )
```

---

## 📝 Low-Level Step-by-Step Testing

### Phase 1: Backend API Testing (Manual via API Client)

#### Step 1.1: Test Authentication

```bash
# Get authentication token
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Save the token from response
TOKEN="your-token-here"
```

**Expected Result:** Returns JWT token

---

#### Step 1.2: Create a Test Project

```bash
curl -X POST http://localhost:8000/api/v1/projects/projects/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project for AI Generation",
    "description": "Testing AI agent workflow",
    "status": "active"
  }'

# Save project ID from response
PROJECT_ID="your-project-id"
```

**Expected Result:** Returns project object with ID

---

#### Step 1.3: Create a Workflow

```bash
curl -X POST http://localhost:8000/api/v1/workflows/workflows/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project Generation Workflow",
    "description": "Generate a simple Python project",
    "status": "active",
    "steps": [
      {
        "step_type": "file_generation",
        "name": "Generate main.py",
        "order": 1,
        "config": {
          "file_path": "main.py",
          "content": "print(\"Hello, World!\")"
        }
      },
      {
        "step_type": "file_generation",
        "name": "Generate README",
        "order": 2,
        "config": {
          "file_path": "README.md",
          "content": "# Test Project\n\nGenerated by AI Agent"
        }
      }
    ]
  }'

# Save workflow ID
WORKFLOW_ID="your-workflow-id"
```

**Expected Result:** Returns workflow object with ID

---

#### Step 1.4: Generate Project via API

```bash
curl -X POST http://localhost:8000/api/v1/projects/generated-projects/generate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"workflow_id\": \"$WORKFLOW_ID\",
    \"input_data\": {
      \"project_id\": \"$PROJECT_ID\",
      \"project_name\": \"Test Generated Project\"
    }
  }"
```

**Expected Result:** 
- Returns `202 Accepted` status
- Returns task_id for tracking
- Creates `GeneratedProject` with status `generating`

**What to Check:**
1. Check Celery worker logs - task should start executing
2. Poll the generated project endpoint to see status change
3. After completion, status should be `completed`

---

#### Step 1.5: Check Generated Project Status

```bash
# List all generated projects
curl -X GET "http://localhost:8000/api/v1/projects/generated-projects/?project=$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN"

# Get specific generated project
GENERATED_PROJECT_ID="generated-project-id-from-step-1.4"
curl -X GET "http://localhost:8000/api/v1/projects/generated-projects/$GENERATED_PROJECT_ID/" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:**
- Status: `completed`
- `total_files`: 2
- `total_size`: > 0
- `files_count`: 2
- `exports_count`: 0

---

#### Step 1.6: List Generated Files

```bash
curl -X GET "http://localhost:8000/api/v1/projects/project-files/?generated_project=$GENERATED_PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:**
- Returns array with 2 files:
  - `main.py`
  - `README.md`
- Each file has: `file_path`, `file_type`, `file_size`, `content_hash`

---

#### Step 1.7: Get File Content

```bash
# First, get file ID from step 1.6
FILE_ID="file-id-from-step-1.6"

curl -X GET "http://localhost:8000/api/v1/projects/project-files/$FILE_ID/content/" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:**
- Returns file content as text
- For `main.py`: `print("Hello, World!")`
- For `README.md`: `# Test Project\n\nGenerated by AI Agent`

---

#### Step 1.8: Export as ZIP

```bash
curl -X POST "http://localhost:8000/api/v1/projects/repository-exports/export-zip/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"generated_project_id\": \"$GENERATED_PROJECT_ID\"
  }"
```

**Expected Result:**
- Returns `202 Accepted`
- Returns export object with status `exporting`
- Task runs in Celery worker

---

#### Step 1.9: Check Export Status

```bash
# Get export ID from step 1.8
EXPORT_ID="export-id-from-step-1.8"

curl -X GET "http://localhost:8000/api/v1/projects/repository-exports/$EXPORT_ID/" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:**
- After completion: status = `completed`
- `archive_path`: path to ZIP file
- `archive_size`: > 0

---

#### Step 1.10: Download Export

```bash
curl -X GET "http://localhost:8000/api/v1/projects/repository-exports/$EXPORT_ID/download/" \
  -H "Authorization: Bearer $TOKEN" \
  -o test-export.zip
```

**Expected Result:**
- Downloads ZIP file
- ZIP contains `main.py` and `README.md`
- Files are readable after extraction

---

### Phase 2: Frontend Testing (Manual UI Testing)

#### Step 2.1: Login to Frontend

1. Navigate to `http://localhost:5173`
2. Login with test credentials
3. **Expected:** Dashboard loads successfully

---

#### Step 2.2: Navigate to Project Generator

1. Click on "Projects" in sidebar
2. Select a project (or create new one)
3. Click on "Generate New Project" or navigate to `/projects/{project_id}/generate`
4. **Expected:** Project Generator page loads

---

#### Step 2.3: Generate Project via UI

1. Fill in form:
   - Project Name: "My AI Generated Project"
   - Project Description: "Testing the generator"
2. Select workflow (if dropdown exists)
3. Click "Start Generation"
4. **Expected:**
   - Loading spinner appears
   - Success toast notification
   - Redirects to generated project detail page

---

#### Step 2.4: View Generated Project

1. Navigate to `/projects/{project_id}/generated`
2. **Expected:** List of generated projects appears
3. Click on the newly generated project
4. **Expected:** Detail page shows:
   - Status badge (should show "generating" then "completed")
   - Files count
   - Size information
   - Export count

---

#### Step 2.5: View Files

1. On generated project detail page, click "Files" tab
2. **Expected:**
   - File tree appears on left
   - Shows all generated files in tree structure
3. Click on a file in the tree
4. **Expected:**
   - File content appears on right
   - Syntax highlighting works (for code files)
   - Line numbers appear (if enabled)

---

#### Step 2.6: Export Project via UI

1. Click "Exports" tab
2. **Expected:** Export controls appear
3. Select export type: "ZIP Archive"
4. Click "Export Project"
5. **Expected:**
   - Loading state
   - Export appears in "Recent Exports" list
   - Status changes from "exporting" to "completed"

---

#### Step 2.7: Download Export

1. After export completes, click "Download" button
2. **Expected:** ZIP file downloads to your computer
3. Extract ZIP file
4. **Expected:** Contains all generated project files

---

### Phase 3: Workflow Integration Testing

#### Step 3.1: Create Workflow with New Step Types

```python
# Via Django shell or API
workflow_steps = [
    {
        "step_type": "api_call",
        "name": "Create Story",
        "config": {
            "method": "POST",
            "endpoint": "/api/v1/projects/stories/",
            "data": {
                "project": "<project_id>",
                "title": "Test Story from Workflow",
                "description": "Created by AI agent"
            }
        }
    },
    {
        "step_type": "file_generation",
        "name": "Generate Config",
        "config": {
            "file_path": "config.json",
            "content": '{"version": "1.0.0"}'
        }
    },
    {
        "step_type": "repo_creation",
        "name": "Export to GitHub",
        "config": {
            "export_type": "github",
            "repository_name": "test-repo",
            "private": False
        }
    }
]
```

---

#### Step 3.2: Execute Workflow

1. Via Workflow Executor API or UI
2. **Expected:**
   - Story gets created via API call
   - Config file gets generated
   - Repository gets exported to GitHub (if token provided)

---

## 🔗 Integration Testing

### Test Agent API Integration

```python
# Test script: test_agent_api.py
from apps.agents.services.api_caller import AgentAPICaller
from apps.authentication.models import User

user = User.objects.get(email='test@example.com')
api_caller = AgentAPICaller(user)

# Test creating a story
response = await api_caller.call(
    method='POST',
    endpoint='/api/v1/projects/stories/',
    data={
        'project': '<project_id>',
        'title': 'Test Story',
        'description': 'Created by agent'
    }
)
print(response)
```

### Test Project Generator

```python
from apps.projects.services.project_generator import ProjectGenerator
from apps.projects.models import GeneratedProject

generated_project = GeneratedProject.objects.get(id='<id>')
generator = ProjectGenerator(generated_project)

# Generate files
structure = {
    'src/main.py': 'print("Hello")',
    'tests/test.py': 'def test(): pass',
    'README.md': '# Project'
}

generator.generate_project_structure(structure)

# Verify files were created
files = generated_project.files.all()
assert files.count() == 3
```

### Test Repository Exporter

```python
from apps.projects.services.repository_exporter import RepositoryExporter

exporter = RepositoryExporter(generated_project)

# Export as ZIP
archive_path = exporter.export_as_zip()
assert archive_path.exists()

# Verify ZIP contains files
import zipfile
with zipfile.ZipFile(archive_path) as z:
    files_in_zip = z.namelist()
    assert 'main.py' in files_in_zip
```

---

## 🐛 Troubleshooting Guide

### Common Issues

#### Issue 1: Celery Tasks Not Running

**Symptoms:** Generated projects stuck in "generating" status

**Solution:**
```bash
# Check if Celery worker is running
celery -A core worker --loglevel=info

# Check Celery logs for errors
# Verify Redis/RabbitMQ is running (if using)
```

---

#### Issue 2: Files Not Generating

**Symptoms:** Generated project completes but no files appear

**Solution:**
1. Check `GENERATED_PROJECTS_DIR` setting
2. Check file system permissions
3. Check Celery task logs for errors
4. Verify workflow output contains `project_structure`

---

#### Issue 3: Export Fails

**Symptoms:** Export status stays "exporting" or becomes "failed"

**Solution:**
1. Check export error message in database
2. Verify file system permissions for archive directory
3. Check Celery logs
4. For GitHub/GitLab: Verify tokens are valid

---

#### Issue 4: Permission Denied Errors

**Symptoms:** 403 Forbidden on API calls

**Solution:**
1. Verify user is project member
2. Check organization membership
3. Verify JWT token is valid and not expired

---

#### Issue 5: Frontend Not Loading Generated Projects

**Symptoms:** Empty list or errors in browser console

**Solution:**
1. Check browser console for API errors
2. Verify backend is running
3. Check CORS settings
4. Verify authentication token is valid

---

## 📊 Testing Checklist Summary

### Quick Test Checklist

- [ ] Authentication works
- [ ] Can create project
- [ ] Can create workflow
- [ ] Can generate project via API
- [ ] Generated project status updates correctly
- [ ] Files are created and trackable
- [ ] Can view file content
- [ ] Can export as ZIP
- [ ] Can download export
- [ ] Frontend pages load
- [ ] UI shows correct data
- [ ] Workflow steps execute correctly

---

## 📝 Next Steps

1. **Run Automated Tests** (when created)
2. **Performance Testing** - Test with large projects
3. **Load Testing** - Multiple concurrent generations
4. **Security Testing** - Permission boundaries
5. **User Acceptance Testing** - Real-world scenarios

---

**Last Updated:** 2025-12-13  
**Version:** 1.0.0

