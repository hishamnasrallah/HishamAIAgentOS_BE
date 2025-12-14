# Backend Models Implementation - New Models for Project Generation

**Document Type:** Backend Models Implementation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 03_SERVICES_IMPLEMENTATION.md, 04_VIEWS_IMPLEMENTATION.md, ../03_ARCHITECTURE/03_DATA_ARCHITECTURE.md  
**File Size:** 495 lines

---

## 📋 Purpose

This document specifies the new database models required for project generation and repository export functionality.

---

## 🗄️ New Models

### Model 1: GeneratedProject

**Purpose:** Track generated project metadata and status

**Location:** `backend/apps/projects/models.py`

**Implementation:**

```python
class GeneratedProject(models.Model):
    """Tracks a generated project's metadata and status."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='generated_projects'
    )
    workflow_execution = models.ForeignKey(
        'workflows.WorkflowExecution',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_projects'
    )
    
    # File system path
    output_directory = models.CharField(max_length=500)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Statistics
    total_files = models.IntegerField(default=0)
    total_size = models.BigIntegerField(default=0)  # in bytes
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_generated_projects'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'generated_projects'
        verbose_name = 'Generated Project'
        verbose_name_plural = 'Generated Projects'
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['created_by', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.status}"
```

**Relationships:**
- One-to-Many with `Project`
- One-to-Many with `ProjectFile`
- One-to-Many with `RepositoryExport`
- Many-to-One with `WorkflowExecution`

---

### Model 2: ProjectFile

**Purpose:** Track individual files in a generated project

**Location:** `backend/apps/projects/models.py`

**Implementation:**

```python
class ProjectFile(models.Model):
    """Tracks individual files in a generated project."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generated_project = models.ForeignKey(
        GeneratedProject,
        on_delete=models.CASCADE,
        related_name='files'
    )
    
    # File metadata
    file_path = models.CharField(max_length=500, db_index=True)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)  # e.g., 'python', 'javascript', 'markdown'
    file_size = models.BigIntegerField(default=0)  # in bytes
    content_hash = models.CharField(max_length=64)  # SHA-256 hash
    
    # File content (optional, for small files)
    content_preview = models.TextField(blank=True, help_text="First 1000 chars")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_files'
        verbose_name = 'Project File'
        verbose_name_plural = 'Project Files'
        indexes = [
            models.Index(fields=['generated_project', 'file_path']),
            models.Index(fields=['file_type']),
            models.Index(fields=['content_hash']),
        ]
        unique_together = [['generated_project', 'file_path']]
        ordering = ['file_path']
    
    def __str__(self):
        return f"{self.file_path} ({self.generated_project.project.name})"
```

**Relationships:**
- Many-to-One with `GeneratedProject`

---

### Model 3: RepositoryExport

**Purpose:** Track repository export jobs and status

**Location:** `backend/apps/projects/models.py`

**Implementation:**

```python
class RepositoryExport(models.Model):
    """Tracks repository export jobs."""
    
    EXPORT_TYPE_CHOICES = [
        ('zip', 'ZIP Archive'),
        ('tar', 'TAR Archive'),
        ('tar.gz', 'TAR GZIP Archive'),
        ('github', 'GitHub Repository'),
        ('gitlab', 'GitLab Repository'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('exporting', 'Exporting'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generated_project = models.ForeignKey(
        GeneratedProject,
        on_delete=models.CASCADE,
        related_name='exports'
    )
    
    # Export configuration
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPE_CHOICES)
    repository_name = models.CharField(max_length=255, blank=True)
    repository_url = models.URLField(blank=True)
    
    # Export result
    archive_path = models.CharField(max_length=500, blank=True)
    archive_size = models.BigIntegerField(null=True, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Configuration (for GitHub/GitLab)
    config = models.JSONField(default=dict, blank=True)
    
    # User tracking
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'repository_exports'
        verbose_name = 'Repository Export'
        verbose_name_plural = 'Repository Exports'
        indexes = [
            models.Index(fields=['generated_project', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['export_type']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.generated_project.project.name} - {self.export_type} - {self.status}"
```

**Relationships:**
- Many-to-One with `GeneratedProject`
- Many-to-One with `User`

---

## 🔄 Model Relationships

### Entity Relationship Diagram

```
Project
  │
  ├──> GeneratedProject (1:N)
  │      │
  │      ├──> ProjectFile (1:N)
  │      │
  │      └──> RepositoryExport (1:N)
  │
  └──> WorkflowExecution (1:N)
         │
         └──> GeneratedProject (N:1)
```

---

## 📊 Database Indexes

### Performance Optimization

**GeneratedProject:**
- `(project, -created_at)` - Fast project listing
- `status` - Fast status filtering
- `(created_by, -created_at)` - Fast user listing

**ProjectFile:**
- `(generated_project, file_path)` - Fast file lookup
- `file_type` - Fast type filtering
- `content_hash` - Duplicate detection

**RepositoryExport:**
- `(generated_project, -created_at)` - Fast export listing
- `status` - Fast status filtering
- `export_type` - Fast type filtering

---

## 🔄 Migrations

### Migration 1: Create GeneratedProject

```python
# Generated by Django migration
operations = [
    migrations.CreateModel(
        name='GeneratedProject',
        fields=[
            # ... all fields
        ],
        options={
            'db_table': 'generated_projects',
            # ... meta options
        },
    ),
]
```

### Migration 2: Create ProjectFile

```python
operations = [
    migrations.CreateModel(
        name='ProjectFile',
        fields=[
            # ... all fields
        ],
    ),
]
```

### Migration 3: Create RepositoryExport

```python
operations = [
    migrations.CreateModel(
        name='RepositoryExport',
        fields=[
            # ... all fields
        ],
    ),
]
```

---

## 🔗 Integration with Existing Models

### Project Model Integration

**Existing Model:** `Project`  
**New Relationship:** `generated_projects` (reverse FK)  
**Impact:** Projects can have multiple generated versions

### WorkflowExecution Model Integration

**Existing Model:** `WorkflowExecution`  
**New Relationship:** `generated_projects` (reverse FK)  
**Impact:** Workflow executions can generate projects

---

## ✅ Model Validation

### GeneratedProject Validation

- `output_directory` must be valid path
- `status` must be valid choice
- `total_files` >= 0
- `total_size` >= 0

### ProjectFile Validation

- `file_path` must be valid relative path
- `file_size` >= 0
- `content_hash` must be valid SHA-256 hash
- `file_path` unique per `generated_project`

### RepositoryExport Validation

- `export_type` must be valid choice
- `archive_size` >= 0 if archive_path provided
- `repository_url` valid URL if provided

---

## 🔗 Related Documentation

- **Services:** `03_SERVICES_IMPLEMENTATION.md`
- **Views:** `04_VIEWS_IMPLEMENTATION.md`
- **Data Architecture:** `../03_ARCHITECTURE/03_DATA_ARCHITECTURE.md`
- **Serializers:** `05_SERIALIZERS_IMPLEMENTATION.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

