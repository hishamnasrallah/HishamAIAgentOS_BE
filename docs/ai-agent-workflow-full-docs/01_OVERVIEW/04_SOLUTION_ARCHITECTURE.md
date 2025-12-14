# Solution Architecture - AI Agent Workflow Enhancement

**Document Type:** Solution Architecture  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 02_CURRENT_STATE_ANALYSIS.md, 03_GAP_ANALYSIS_SUMMARY.md, ../03_ARCHITECTURE/  
**File Size:** 496 lines

---

## 📋 Purpose

This document describes the high-level solution architecture for enabling full SDLC automation and production-ready project generation.

---

## 🏗️ Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Workflow   │  │   Project    │  │  Repository  │      │
│  │   Builder    │  │   Generator  │  │    Export    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER (Django REST)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Workflow    │  │   Project    │  │  Repository  │      │
│  │  ViewSets    │  │   ViewSets   │  │   ViewSets   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  SERVICE LAYER (NEW)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ AgentAPI     │  │   Project    │  │  Repository  │      │
│  │ Caller       │  │  Generator   │  │  Exporter    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              EXISTING CORE SERVICES                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Workflow    │  │    Agent     │  │   Project    │      │
│  │  Executor    │  │  Execution   │  │ Management   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Database    │  │  File System │  │  Git Repos   │      │
│  │  (PostgreSQL)│  │ (Generated   │  │  (GitHub/    │      │
│  │              │  │  Projects)   │  │  GitLab)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Solution Components

### Component 1: AgentAPICaller Service

**Purpose:** Enable agents to call HishamOS APIs directly

**Key Features:**
- Authenticated API requests
- Endpoint discovery
- Error handling and retries
- Response formatting

**Integration Points:**
- Agent Execution Engine
- Workflow Executor
- Project Management APIs

**Location:** `backend/apps/agents/services/api_caller.py`

---

### Component 2: ProjectGenerator Service

**Purpose:** Generate project files on filesystem

**Key Features:**
- Directory structure creation
- File generation from templates
- Project packaging
- Configuration file generation

**Integration Points:**
- Workflow Executor (file_generation step)
- Repository Exporter
- File System

**Location:** `backend/apps/projects/services/project_generator.py`

---

### Component 3: RepositoryExporter Service

**Purpose:** Export projects as Git repositories

**Key Features:**
- Git repository initialization
- GitHub/GitLab integration
- ZIP/TAR export
- Repository configuration

**Integration Points:**
- Project Generator
- External APIs (GitHub/GitLab)
- File System

**Location:** `backend/apps/projects/services/repository_exporter.py`

---

### Component 4: Enhanced Workflow System

**Purpose:** Support new workflow step types

**Key Features:**
- `api_call` step type
- `file_generation` step type
- `repo_creation` step type
- Step type registry

**Integration Points:**
- Workflow Executor
- All new services
- Agent System

**Location:** `backend/apps/workflows/services/`

---

## 🔄 Data Flow

### Complete Project Generation Flow

```
User Input (Idea/Vision)
    │
    ▼
Workflow Trigger
    │
    ▼
Step 1: Generate Requirements (Agent)
    │
    ▼
Step 2: Create Stories (API Call via AgentAPICaller)
    │
    ▼
Step 3: Plan Sprint (API Call via AgentAPICaller)
    │
    ▼
Step 4: Generate Code (Agent + File Generation)
    │
    ▼
Step 5: Generate Tests (Agent + File Generation)
    │
    ▼
Step 6: Generate Docs (Agent + File Generation)
    │
    ▼
Step 7: Generate CI/CD Configs (File Generation)
    │
    ▼
Step 8: Create Repository (RepositoryExporter)
    │
    ▼
Step 9: Export/Publish (RepositoryExporter)
    │
    ▼
Complete Project (Ready for Deployment)
```

---

## 🗄️ Data Architecture

### New Models

#### GeneratedProject
```python
- id: UUID
- project: ForeignKey(Project)
- output_directory: Path
- status: CharField
- created_at: DateTimeField
- completed_at: DateTimeField
```

#### ProjectFile
```python
- id: UUID
- generated_project: ForeignKey(GeneratedProject)
- file_path: CharField
- file_size: IntegerField
- content_hash: CharField
- created_at: DateTimeField
```

#### RepositoryExport
```python
- id: UUID
- generated_project: ForeignKey(GeneratedProject)
- export_type: CharField (github, gitlab, zip, tar)
- status: CharField
- repository_url: URLField
- created_at: DateTimeField
```

### File System Structure

```
backend/
├── generated-projects/
│   ├── {project-id-1}/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── docs/
│   │   ├── .git/
│   │   ├── .gitignore
│   │   └── README.md
│   ├── {project-id-2}/
│   └── ...
```

---

## 🔌 Integration Patterns

### Pattern 1: Agent-API Integration

**Flow:**
1. Agent receives task with API call instruction
2. Agent uses `AgentAPICaller` from context
3. `AgentAPICaller` makes authenticated request
4. Response returned to agent
5. Agent processes response

**Example:**
```python
# In agent execution context
api_caller = AgentAPICaller(user=user)
story_data = await api_caller.create_story(
    project_id=project_id,
    title="User login",
    description="As a user, I want to log in..."
)
```

### Pattern 2: File Generation Integration

**Flow:**
1. Workflow step specifies file generation
2. Step executor calls `ProjectGenerator`
3. `ProjectGenerator` creates files on filesystem
4. File metadata stored in database
5. Files available for export

**Example:**
```python
# In workflow step
generator = ProjectGenerator(project_id=project_id)
generator.write_file(
    path="src/main.py",
    content=code_content
)
```

### Pattern 3: Repository Export Integration

**Flow:**
1. Project generation completes
2. User triggers export
3. `RepositoryExporter` initializes Git repo
4. Files committed to repository
5. Repository published to GitHub/GitLab or exported as archive

**Example:**
```python
# In export endpoint
exporter = RepositoryExporter(project_id=project_id)
result = await exporter.export_to_github(
    github_token=token,
    repository_name="my-project"
)
```

---

## 🛡️ Security Architecture

### Authentication & Authorization

- **Agent-API Calls:** Use user context for authentication
- **File Operations:** Permission checks before file generation
- **Repository Export:** Token-based authentication for external APIs

### Data Security

- **File Path Validation:** Prevent path traversal attacks
- **File Size Limits:** Prevent resource exhaustion
- **Rate Limiting:** Prevent API abuse

---

## 📈 Scalability Considerations

### Horizontal Scaling

- **File Generation:** Stateless operations, can scale horizontally
- **Repository Export:** Can use background tasks (Celery)
- **API Calls:** Stateless, can scale horizontally

### Resource Management

- **File System:** Cleanup old generated projects
- **Storage:** Configurable storage backends (local, S3, etc.)
- **Memory:** Streaming for large files

---

## 🔗 Related Documentation

- **Component Architecture:** `../03_ARCHITECTURE/02_COMPONENT_ARCHITECTURE.md`
- **Data Architecture:** `../03_ARCHITECTURE/03_DATA_ARCHITECTURE.md`
- **API Architecture:** `../03_ARCHITECTURE/04_API_ARCHITECTURE.md`
- **Backend Implementation:** `../04_BACKEND/`
- **Integration Patterns:** `../06_INTEGRATION/`

---

**Document Owner:** Architecture Team  
**Review Cycle:** Quarterly  
**Last Updated:** 2025-12-13

