# Component Architecture - Detailed Component Design

**Document Type:** Component Architecture  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 01_SYSTEM_ARCHITECTURE.md, 03_DATA_ARCHITECTURE.md, ../04_BACKEND/  
**File Size:** 498 lines

---

## 📋 Purpose

This document provides detailed component-level architecture for the AI agent workflow enhancement, including interfaces, dependencies, and interactions.

---

## 🧩 Core Components

### Component 1: AgentAPICaller

**Location:** `backend/apps/agents/services/api_caller.py`

**Purpose:** Enable agents to call HishamOS APIs directly

**Interfaces:**
```python
class AgentAPICaller:
    async def call(method, endpoint, data, params) -> Dict
    async def create_story(project_id, title, description, **kwargs) -> Dict
    async def update_story_status(story_id, status) -> Dict
    async def create_sprint(project_id, name, start_date, end_date, **kwargs) -> Dict
    async def discover_endpoints() -> List[Dict]
    async def close()
```

**Dependencies:**
- `httpx` (HTTP client)
- `jwt_service` (authentication)
- Django settings

**Dependents:**
- Agent execution engine
- Workflow executor
- Workflow steps (api_call type)

**Error Handling:**
- HTTP errors → APIError exception
- Network errors → Retry logic
- Authentication errors → Re-authenticate

---

### Component 2: ProjectGenerator

**Location:** `backend/apps/projects/services/project_generator.py`

**Purpose:** Generate project files on filesystem

**Interfaces:**
```python
class ProjectGenerator:
    def create_directory(path) -> Path
    def write_file(path, content, encoding) -> Path
    def generate_project_structure(structure) -> Dict[str, Path]
    def generate_from_template(template_path, output_path, context) -> Path
    def initialize_git_repository() -> bool
    def create_gitignore(patterns) -> Path
    def create_readme(content) -> Path
    def package_project(format) -> Path
    def cleanup()
```

**Dependencies:**
- `pathlib` (file operations)
- Django settings (output directory)
- File system

**Dependents:**
- Workflow executor (file_generation step)
- RepositoryExporter
- API endpoints (export)

**Error Handling:**
- File system errors → Rollback
- Permission errors → Security exception
- Path validation errors → Validation exception

---

### Component 3: RepositoryExporter

**Location:** `backend/apps/projects/services/repository_exporter.py`

**Purpose:** Export projects as Git repositories

**Interfaces:**
```python
class RepositoryExporter:
    async def export_to_github(token, repository_name, organization, private) -> Dict
    async def export_to_gitlab(token, project_name, namespace, visibility) -> Dict
    def export_as_zip() -> Path
    def export_as_tar() -> Path
```

**Dependencies:**
- `ProjectGenerator` (file access)
- GitHub API client
- GitLab API client
- Git operations

**Dependents:**
- Workflow executor (repo_creation step)
- API endpoints (export)

**Error Handling:**
- Git errors → GitException
- API errors → Retry with backoff
- Network errors → Retry logic

---

### Component 4: Enhanced Workflow Executor

**Location:** `backend/apps/workflows/services/workflow_executor.py`

**Purpose:** Execute workflows with new step types

**New Step Types:**
- `api_call`: Execute API call via AgentAPICaller
- `file_generation`: Generate files via ProjectGenerator
- `repo_creation`: Create repository via RepositoryExporter

**Enhancements:**
- Step type registry
- Step executor factory
- Error handling for new types
- Progress tracking

---

## 🔗 Component Relationships

### Dependency Graph

```
WorkflowExecutor
    │
    ├──> AgentExecutionEngine
    │       └──> AgentAPICaller
    │
    ├──> ProjectGenerator
    │       └──> FileSystem
    │
    └──> RepositoryExporter
            ├──> ProjectGenerator
            ├──> GitHubAPI
            └──> GitLabAPI
```

---

## 📊 Component Interfaces

### Interface 1: IAPICaller

**Purpose:** Abstract interface for API calling

**Methods:**
- `call(method, endpoint, data, params)`
- `authenticate()`
- `handle_error(error)`

**Implementations:**
- `AgentAPICaller`

---

### Interface 2: IFileGenerator

**Purpose:** Abstract interface for file generation

**Methods:**
- `generate_file(path, content)`
- `generate_structure(structure)`
- `validate_path(path)`

**Implementations:**
- `ProjectGenerator`

---

### Interface 3: IRepositoryExporter

**Purpose:** Abstract interface for repository export

**Methods:**
- `export(format)`
- `initialize_repository()`
- `push_to_remote()`

**Implementations:**
- `RepositoryExporter`

---

## 🔄 Component Interactions

### Interaction 1: Agent API Call

```
Agent (via ExecutionEngine)
    │
    ▼
AgentAPICaller.call()
    │
    ├──> Authenticate (JWT)
    │
    ├──> Validate Request
    │
    ├──> Execute HTTP Request
    │
    ├──> Handle Response
    │
    └──> Return Result
```

---

### Interaction 2: File Generation

```
Workflow Step (file_generation)
    │
    ▼
ProjectGenerator.generate_project_structure()
    │
    ├──> Validate Structure
    │
    ├──> Create Directories
    │
    ├──> Generate Files
    │
    ├──> Update Database
    │
    └──> Return File Metadata
```

---

### Interaction 3: Repository Export

```
User Request
    │
    ▼
RepositoryExporter.export_to_github()
    │
    ├──> Initialize Git Repository
    │
    ├──> Add Files
    │
    ├──> Create Commit
    │
    ├──> Create GitHub Repository (API)
    │
    ├──> Push Code
    │
    └──> Return Repository URL
```

---

## 🏗️ Component Design Patterns

### Pattern 1: Service Locator

**Application:** Component discovery

**Implementation:**
- Service registry for step types
- Factory pattern for service creation

---

### Pattern 2: Dependency Injection

**Application:** Service dependencies

**Implementation:**
- Constructor injection
- Interface-based design

---

### Pattern 3: Strategy Pattern

**Application:** Different export strategies

**Implementation:**
- IRepositoryExporter interface
- Multiple implementations (GitHub, GitLab, ZIP)

---

## 🔐 Component Security

### Security Considerations

#### AgentAPICaller
- Authentication required
- Permission checks
- Rate limiting
- Audit logging

#### ProjectGenerator
- Path validation
- File size limits
- Permission checks
- Secure file operations

#### RepositoryExporter
- Token security
- Repository name validation
- Access control
- Secure API communication

---

## 📈 Component Scalability

### Scalability Strategies

#### Stateless Components
- AgentAPICaller (stateless)
- ProjectGenerator (per project instance)
- RepositoryExporter (per export job)

#### Stateful Components
- Workflow executor (state tracking)
- Progress tracking (in-memory + DB)

#### Caching
- API responses (temporary)
- Endpoint discovery (long-term)
- File metadata (medium-term)

---

## ✅ Component Quality Criteria

### Performance
- AgentAPICaller: < 200ms per call
- ProjectGenerator: < 50ms per file
- RepositoryExporter: < 10s per export

### Reliability
- Error handling for all failure modes
- Retry logic for transient failures
- Graceful degradation

### Testability
- Interface-based design
- Dependency injection
- Mock-friendly interfaces

---

## 🔗 Related Documentation

- **System Architecture:** `01_SYSTEM_ARCHITECTURE.md`
- **Data Architecture:** `03_DATA_ARCHITECTURE.md`
- **Backend Services:** `../04_BACKEND/03_SERVICES_IMPLEMENTATION.md`
- **Integration:** `../06_INTEGRATION/`

---

**Document Owner:** Architecture Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

