# Data Architecture - AI Agent Workflow Enhancement

**Document Type:** Data Architecture  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 02_COMPONENT_ARCHITECTURE.md, ../04_BACKEND/02_MODELS_IMPLEMENTATION.md, ../04_BACKEND/05_SERIALIZERS_IMPLEMENTATION.md  
**File Size:** 495 lines

---

## 📋 Purpose

This document describes the data architecture for the AI agent workflow enhancement, including data models, relationships, storage strategies, and data flow.

---

## 🗄️ Data Model Overview

### Entity Relationship Diagram

```
Project (Existing)
  │
  ├──> GeneratedProject (NEW - 1:N)
  │      │
  │      ├──> ProjectFile (NEW - 1:N)
  │      │
  │      └──> RepositoryExport (NEW - 1:N)
  │
  └──> WorkflowExecution (Existing - 1:N)
         │
         └──> GeneratedProject (N:1)
```

---

## 📊 Core Data Models

### Model 1: GeneratedProject

**Purpose:** Track generated project metadata

**Key Fields:**
- `id`: UUID (Primary Key)
- `project`: FK to Project
- `workflow_execution`: FK to WorkflowExecution (nullable)
- `output_directory`: CharField (filesystem path)
- `status`: CharField (pending, generating, completed, failed, archived)
- `total_files`: IntegerField
- `total_size`: BigIntegerField (bytes)
- Timestamps: created_at, updated_at, completed_at

**Indexes:**
- `(project, -created_at)` - Fast project listing
- `status` - Fast status filtering
- `(created_by, -created_at)` - Fast user listing

**Relationships:**
- Many-to-One with Project
- One-to-Many with ProjectFile
- One-to-Many with RepositoryExport
- Many-to-One with WorkflowExecution

---

### Model 2: ProjectFile

**Purpose:** Track individual files in generated projects

**Key Fields:**
- `id`: UUID (Primary Key)
- `generated_project`: FK to GeneratedProject
- `file_path`: CharField (relative path)
- `file_name`: CharField
- `file_type`: CharField (python, javascript, etc.)
- `file_size`: BigIntegerField (bytes)
- `content_hash`: CharField (SHA-256)
- `content_preview`: TextField (first 1000 chars)
- Timestamps: created_at, updated_at

**Indexes:**
- `(generated_project, file_path)` - Fast file lookup
- `file_type` - Fast type filtering
- `content_hash` - Duplicate detection

**Relationships:**
- Many-to-One with GeneratedProject

**Constraints:**
- Unique: (generated_project, file_path)

---

### Model 3: RepositoryExport

**Purpose:** Track repository export jobs

**Key Fields:**
- `id`: UUID (Primary Key)
- `generated_project`: FK to GeneratedProject
- `export_type`: CharField (zip, tar, tar.gz, github, gitlab)
- `repository_name`: CharField
- `repository_url`: URLField
- `archive_path`: CharField (filesystem path)
- `archive_size`: BigIntegerField (bytes)
- `status`: CharField (pending, exporting, completed, failed)
- `config`: JSONField (export configuration)
- Timestamps: created_at, updated_at, completed_at

**Indexes:**
- `(generated_project, -created_at)` - Fast export listing
- `status` - Fast status filtering
- `export_type` - Fast type filtering

**Relationships:**
- Many-to-One with GeneratedProject
- Many-to-One with User (created_by)

---

## 🔄 Data Flow

### Flow 1: Project Generation Data Flow

```
User Request
    │
    ▼
Create GeneratedProject (status='pending')
    │
    ▼
WorkflowExecution starts
    │
    ▼
Update GeneratedProject (status='generating')
    │
    ▼
Generate Files → Create ProjectFile records
    │
    ▼
Update GeneratedProject (total_files, total_size)
    │
    ▼
Update GeneratedProject (status='completed', completed_at)
```

---

### Flow 2: Repository Export Data Flow

```
User Request
    │
    ▼
Create RepositoryExport (status='pending')
    │
    ▼
Update RepositoryExport (status='exporting')
    │
    ▼
Export Process
    │
    ├──> Success: Update (status='completed', repository_url/archive_path)
    │
    └──> Failure: Update (status='failed', error_message)
```

---

## 💾 Storage Architecture

### Storage Type 1: Relational Database (PostgreSQL)

**Purpose:** Structured metadata and relationships

**Tables:**
- `generated_projects` - Project metadata
- `project_files` - File metadata
- `repository_exports` - Export job tracking

**Characteristics:**
- ACID transactions
- Foreign key constraints
- Indexes for performance
- JSON fields for flexible data

---

### Storage Type 2: File System

**Purpose:** Generated project files

**Structure:**
```
backend/generated-projects/
├── {project-id-1}/
│   ├── src/
│   ├── tests/
│   ├── docs/
│   ├── .git/
│   └── README.md
├── {project-id-2}/
└── ...
```

**Characteristics:**
- Hierarchical structure
- Direct file access
- Git repository support
- Archive generation support

**Configuration:**
- Base directory: `settings.GENERATED_PROJECTS_DIR`
- Permissions: Read/write for application user
- Cleanup: Automated retention policy

---

### Storage Type 3: External APIs

**Purpose:** Remote repository hosting

**Services:**
- GitHub API
- GitLab API

**Data Stored:**
- Repository URLs
- Authentication tokens (encrypted)
- Export configuration

---

## 🔐 Data Security

### Security Measures

#### Database Security
- Encryption at rest (database-level)
- Encrypted connections (SSL/TLS)
- Access control (database users)
- Audit logging

#### File System Security
- Path validation (prevent traversal)
- Permission checks
- Access control (user-based)
- Secure deletion

#### API Security
- Token encryption
- Secure transmission (HTTPS)
- Access token rotation
- Rate limiting

---

## 📈 Data Performance

### Optimization Strategies

#### Database Optimization
- Indexes on frequently queried fields
- Query optimization (select_related, prefetch_related)
- Connection pooling
- Read replicas (future)

#### File System Optimization
- Efficient file operations (batch writes)
- Async I/O where possible
- File system caching
- Cleanup of old files

---

## 🔄 Data Migration Strategy

### Migration Plan

#### Phase 1: Schema Creation
- Create new tables
- Add foreign keys
- Create indexes
- Add constraints

#### Phase 2: Data Migration
- No existing data to migrate
- Tables are new

#### Phase 3: Backfill (if needed)
- Historical data backfill
- Validation
- Verification

---

## 📊 Data Lifecycle

### GeneratedProject Lifecycle

```
Created → Generating → Completed → Archived → Deleted
   ↓         ↓            ↓           ↓          ↓
Pending   Failed      Active     Retained   Cleaned
```

**Retention Rules:**
- Active: 30 days (default)
- Archived: 90 days
- After retention: Files deleted, metadata retained

---

### RepositoryExport Lifecycle

```
Created → Exporting → Completed → Archived
   ↓         ↓           ↓
Pending   Failed      (End)
```

**Retention Rules:**
- Completed exports: 90 days
- Failed exports: 30 days
- After retention: Metadata retained, files deleted

---

## 🔗 Data Relationships

### Relationship Details

#### GeneratedProject ↔ Project
- **Type:** Many-to-One
- **Cardinality:** Many GeneratedProjects per Project
- **Cascade:** CASCADE delete
- **Purpose:** Track project generations

#### GeneratedProject ↔ ProjectFile
- **Type:** One-to-Many
- **Cardinality:** Many ProjectFiles per GeneratedProject
- **Cascade:** CASCADE delete
- **Purpose:** Track generated files

#### GeneratedProject ↔ RepositoryExport
- **Type:** One-to-Many
- **Cardinality:** Many RepositoryExports per GeneratedProject
- **Cascade:** CASCADE delete
- **Purpose:** Track export jobs

#### GeneratedProject ↔ WorkflowExecution
- **Type:** Many-to-One
- **Cardinality:** Many GeneratedProjects per WorkflowExecution
- **Cascade:** SET_NULL
- **Purpose:** Link to workflow that generated project

---

## 📝 Data Validation Rules

### GeneratedProject Validation
- `output_directory` must be valid path
- `status` must be valid choice
- `total_files` >= 0
- `total_size` >= 0
- `completed_at` only if `status='completed'`

### ProjectFile Validation
- `file_path` must be relative (no absolute paths)
- `file_size` >= 0
- `content_hash` must be valid SHA-256
- `file_path` unique per `generated_project`

### RepositoryExport Validation
- `export_type` must be valid choice
- `archive_size` >= 0 if `archive_path` provided
- `repository_url` valid URL if provided

---

## 🔗 Related Documentation

- **Models Implementation:** `../04_BACKEND/02_MODELS_IMPLEMENTATION.md`
- **Serializers:** `../04_BACKEND/05_SERIALIZERS_IMPLEMENTATION.md`
- **Component Architecture:** `02_COMPONENT_ARCHITECTURE.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

