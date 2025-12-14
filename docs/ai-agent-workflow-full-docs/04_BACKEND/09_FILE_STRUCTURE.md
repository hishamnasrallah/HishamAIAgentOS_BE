# Backend File Structure - Project Organization

**Document Type:** File Structure Documentation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 01_BACKEND_OVERVIEW.md, 03_SERVICES_IMPLEMENTATION.md  
**File Size:** 485 lines

---

## 📋 Purpose

This document describes the file structure and organization for the backend implementation of the AI agent workflow enhancement.

---

## 📁 File Structure

### Complete Structure

```
backend/
├── apps/
│   ├── agents/
│   │   ├── services/
│   │   │   ├── api_caller.py (NEW)
│   │   │   ├── api_discovery.py (NEW)
│   │   │   └── execution_engine.py (existing)
│   │   ├── models.py (existing)
│   │   └── ...
│   │
│   ├── projects/
│   │   ├── models.py (enhanced - add new models)
│   │   ├── views.py (enhanced - add new ViewSets)
│   │   ├── serializers.py (enhanced - add new serializers)
│   │   ├── permissions.py (enhanced - add new permissions)
│   │   ├── signals.py (enhanced - add new signals)
│   │   ├── tasks.py (enhanced - add new Celery tasks)
│   │   ├── services/
│   │   │   ├── project_generator.py (NEW)
│   │   │   ├── repository_exporter.py (NEW)
│   │   │   └── ... (existing services)
│   │   ├── migrations/
│   │   │   └── XXXX_add_generated_project_models.py (NEW)
│   │   └── ...
│   │
│   └── workflows/
│       ├── services/
│       │   ├── workflow_executor.py (enhanced)
│       │   └── step_executors/
│       │       ├── api_call_step.py (NEW)
│       │       ├── file_generation_step.py (NEW)
│       │       └── repo_creation_step.py (NEW)
│       └── ...
│
├── generated-projects/ (NEW directory)
│   ├── {project-id-1}/
│   │   ├── src/
│   │   ├── tests/
│   │   └── .git/
│   └── {project-id-2}/
│
└── core/
    └── settings/
        ├── base.py (enhanced - add new settings)
        └── ...
```

---

## 📝 New Files

### File 1: agents/services/api_caller.py

**Purpose:** Agent API calling service

**Contents:**
- `AgentAPICaller` class
- API calling methods
- Authentication handling
- Error handling

**Lines:** ~300-400

---

### File 2: agents/services/api_discovery.py

**Purpose:** API endpoint discovery

**Contents:**
- Endpoint discovery logic
- API documentation generation
- Endpoint registry

**Lines:** ~200-300

---

### File 3: projects/services/project_generator.py

**Purpose:** Project file generation service

**Contents:**
- `ProjectGenerator` class
- File generation methods
- Directory creation
- Template rendering

**Lines:** ~400-500

---

### File 4: projects/services/repository_exporter.py

**Purpose:** Repository export service

**Contents:**
- `RepositoryExporter` class
- GitHub integration
- GitLab integration
- Archive generation

**Lines:** ~400-500

---

### File 5: workflows/services/step_executors/api_call_step.py

**Purpose:** API call step executor

**Contents:**
- `APICallStepExecutor` class
- Step execution logic
- Error handling

**Lines:** ~200-300

---

### File 6: workflows/services/step_executors/file_generation_step.py

**Purpose:** File generation step executor

**Contents:**
- `FileGenerationStepExecutor` class
- Step execution logic
- File generation orchestration

**Lines:** ~300-400

---

### File 7: workflows/services/step_executors/repo_creation_step.py

**Purpose:** Repository creation step executor

**Contents:**
- `RepoCreationStepExecutor` class
- Step execution logic
- Repository export orchestration

**Lines:** ~300-400

---

## 🔧 Enhanced Files

### File 1: projects/models.py

**Additions:**
- `GeneratedProject` model
- `ProjectFile` model
- `RepositoryExport` model

**Location:** End of file or new section

---

### File 2: projects/views.py

**Additions:**
- `GeneratedProjectViewSet`
- `ProjectFileViewSet`
- `RepositoryExportViewSet`
- Custom action methods

**Location:** New ViewSet classes

---

### File 3: projects/serializers.py

**Additions:**
- `GeneratedProjectSerializer`
- `ProjectFileSerializer`
- `RepositoryExportSerializer`
- Request serializers

**Location:** New serializer classes

---

### File 4: projects/permissions.py

**Additions:**
- `CanGenerateProject` permission class
- `CanExportRepository` permission class
- Enhanced `IsProjectMemberOrReadOnly`

**Location:** New permission classes

---

### File 5: projects/signals.py

**Additions:**
- `generated_project_pre_save` signal handler
- `generated_project_post_save` signal handler
- `project_file_post_save` signal handler
- `repository_export_post_save` signal handler

**Location:** New signal handlers

---

### File 6: projects/tasks.py

**Additions:**
- `start_project_generation` task
- `execute_repository_export` task
- `cleanup_old_generated_projects` task

**Location:** New task definitions

---

### File 7: workflows/services/workflow_executor.py

**Enhancements:**
- Support for new step types
- Step type registry integration
- Enhanced step execution

**Location:** Enhanced existing methods

---

### File 8: core/settings/base.py

**Additions:**
```python
# Generated Projects Settings
GENERATED_PROJECTS_DIR = os.path.join(BASE_DIR, 'generated-projects')
GENERATED_PROJECTS_RETENTION_DAYS = 30
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

---

## 📊 Migration Files

### Migration 1: Create GeneratedProject

**File:** `XXXX_add_generated_project_models.py`

**Contents:**
- Create `GeneratedProject` table
- Create indexes
- Create foreign keys

---

### Migration 2: Create ProjectFile

**File:** `XXXX_add_project_file_model.py`

**Contents:**
- Create `ProjectFile` table
- Create indexes
- Create foreign keys

---

### Migration 3: Create RepositoryExport

**File:** `XXXX_add_repository_export_model.py`

**Contents:**
- Create `RepositoryExport` table
- Create indexes
- Create foreign keys

---

## 🔗 URL Configuration

### Enhanced URLs

**File:** `backend/apps/projects/urls.py`

**Additions:**
```python
# New routes for generated projects
router.register(
    r'projects/(?P<project_id>[^/.]+)/generated',
    GeneratedProjectViewSet,
    basename='generated-project'
)

router.register(
    r'projects/(?P<project_id>[^/.]+)/generated/(?P<generated_id>[^/.]+)/files',
    ProjectFileViewSet,
    basename='project-file'
)

router.register(
    r'projects/(?P<project_id>[^/.]+)/generated/(?P<generated_id>[^/.]+)/exports',
    RepositoryExportViewSet,
    basename='repository-export'
)
```

---

## ✅ File Organization Guidelines

### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Import Organization
1. Standard library imports
2. Third-party imports
3. Django imports
4. Local application imports

### Code Organization
- Models at top of file
- Serializers after models
- Views after serializers
- Services in separate files

---

## 🔗 Related Documentation

- **Backend Overview:** `01_BACKEND_OVERVIEW.md`
- **Models:** `02_MODELS_IMPLEMENTATION.md`
- **Services:** `03_SERVICES_IMPLEMENTATION.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

