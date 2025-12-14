# Backend Serializers Implementation - Data Serialization

**Document Type:** Serializers Implementation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 02_MODELS_IMPLEMENTATION.md, 04_VIEWS_IMPLEMENTATION.md, ../03_ARCHITECTURE/04_API_ARCHITECTURE.md  
**File Size:** 491 lines

---

## 📋 Purpose

This document specifies the Django REST Framework serializers for the AI agent workflow enhancement models.

---

## 🎯 New Serializers

### Serializer 1: GeneratedProjectSerializer

**Location:** `backend/apps/projects/serializers.py`

**Purpose:** Serialize GeneratedProject model

**Implementation:**

```python
class GeneratedProjectSerializer(serializers.ModelSerializer):
    """Serializer for GeneratedProject model."""
    
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    project_name = serializers.CharField(source='project.name', read_only=True)
    workflow_execution = serializers.PrimaryKeyRelatedField(
        queryset=WorkflowExecution.objects.all(),
        required=False,
        allow_null=True
    )
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    files_count = serializers.IntegerField(source='files.count', read_only=True)
    exports_count = serializers.IntegerField(source='exports.count', read_only=True)
    
    # File list (nested)
    files = ProjectFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = GeneratedProject
        fields = [
            'id',
            'project',
            'project_name',
            'workflow_execution',
            'output_directory',
            'status',
            'error_message',
            'total_files',
            'total_size',
            'files_count',
            'exports_count',
            'files',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_at',
            'updated_at',
            'completed_at',
            'total_files',
            'total_size',
        ]
    
    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance:
            current_status = self.instance.status
            valid_transitions = {
                'pending': ['generating'],
                'generating': ['completed', 'failed'],
                'completed': ['archived'],
                'failed': [],
                'archived': [],
            }
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Invalid transition from {current_status} to {value}"
                )
        return value
```

---

### Serializer 2: ProjectFileSerializer

**Location:** `backend/apps/projects/serializers.py`

**Purpose:** Serialize ProjectFile model

**Implementation:**

```python
class ProjectFileSerializer(serializers.ModelSerializer):
    """Serializer for ProjectFile model."""
    
    generated_project = serializers.PrimaryKeyRelatedField(
        queryset=GeneratedProject.objects.all()
    )
    file_size_display = serializers.SerializerMethodField()
    file_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectFile
        fields = [
            'id',
            'generated_project',
            'file_path',
            'file_name',
            'file_type',
            'file_type_display',
            'file_size',
            'file_size_display',
            'content_hash',
            'content_preview',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'content_hash',
            'created_at',
            'updated_at',
        ]
    
    def validate_file_path(self, value):
        """Validate file path."""
        # Prevent path traversal
        if '..' in value or value.startswith('/'):
            raise serializers.ValidationError("Invalid file path")
        return value
    
    def get_file_size_display(self, obj):
        """Format file size."""
        return format_file_size(obj.file_size)
    
    def get_file_type_display(self, obj):
        """Format file type."""
        return obj.file_type.upper() if obj.file_type else None
```

---

### Serializer 3: RepositoryExportSerializer

**Location:** `backend/apps/projects/serializers.py`

**Purpose:** Serialize RepositoryExport model

**Implementation:**

```python
class RepositoryExportSerializer(serializers.ModelSerializer):
    """Serializer for RepositoryExport model."""
    
    generated_project = serializers.PrimaryKeyRelatedField(
        queryset=GeneratedProject.objects.all()
    )
    export_type_display = serializers.CharField(
        source='get_export_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    archive_size_display = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = RepositoryExport
        fields = [
            'id',
            'generated_project',
            'export_type',
            'export_type_display',
            'repository_name',
            'repository_url',
            'archive_path',
            'archive_size',
            'archive_size_display',
            'status',
            'status_display',
            'error_message',
            'config',
            'download_url',
            'created_by',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'created_at',
            'updated_at',
            'completed_at',
            'archive_path',
            'archive_size',
            'repository_url',
            'status',
            'error_message',
        ]
    
    def validate_export_type(self, value):
        """Validate export type."""
        valid_types = ['zip', 'tar', 'tar.gz', 'github', 'gitlab']
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid export type: {value}")
        return value
    
    def validate_repository_name(self, value):
        """Validate repository name."""
        if value:
            # GitHub/GitLab naming rules
            import re
            pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$'
            if not re.match(pattern, value) or len(value) > 100:
                raise serializers.ValidationError("Invalid repository name")
        return value
    
    def get_archive_size_display(self, obj):
        """Format archive size."""
        return format_file_size(obj.archive_size) if obj.archive_size else None
    
    def get_download_url(self, obj):
        """Get download URL if available."""
        if obj.status == 'completed' and obj.archive_path:
            return reverse('export-download', kwargs={'export_id': obj.id})
        return None
```

---

### Serializer 4: ProjectGenerationRequestSerializer

**Location:** `backend/apps/projects/serializers.py`

**Purpose:** Validate project generation requests

**Implementation:**

```python
class ProjectGenerationRequestSerializer(serializers.Serializer):
    """Serializer for project generation requests."""
    
    workflow_id = serializers.UUIDField(required=True)
    input_data = serializers.JSONField(required=True)
    
    def validate_workflow_id(self, value):
        """Validate workflow exists."""
        try:
            workflow = Workflow.objects.get(id=value)
            if workflow.status != 'active':
                raise serializers.ValidationError("Workflow is not active")
        except Workflow.DoesNotExist:
            raise serializers.ValidationError("Workflow not found")
        return value
```

---

### Serializer 5: GitHubExportRequestSerializer

**Location:** `backend/apps/projects/serializers.py`

**Purpose:** Validate GitHub export requests

**Implementation:**

```python
class GitHubExportRequestSerializer(serializers.Serializer):
    """Serializer for GitHub export requests."""
    
    repository_name = serializers.CharField(required=True, max_length=100)
    organization = serializers.CharField(required=False, allow_blank=True)
    private = serializers.BooleanField(default=False)
    github_token = serializers.CharField(required=False, write_only=True)
    
    def validate_repository_name(self, value):
        """Validate repository name."""
        import re
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$'
        if not re.match(pattern, value) or len(value) > 100:
            raise serializers.ValidationError("Invalid repository name")
        return value
```

---

### Serializer 6: GitLabExportRequestSerializer

**Location:** `backend/apps/projects/serializers.py`

**Purpose:** Validate GitLab export requests

**Implementation:**

```python
class GitLabExportRequestSerializer(serializers.Serializer):
    """Serializer for GitLab export requests."""
    
    project_name = serializers.CharField(required=True, max_length=255)
    namespace = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(
        choices=['private', 'internal', 'public'],
        default='private'
    )
    gitlab_token = serializers.CharField(required=False, write_only=True)
```

---

## 🔄 Nested Serialization

### Nested Files in GeneratedProject

**Usage:**
```python
class GeneratedProjectDetailSerializer(GeneratedProjectSerializer):
    """Detailed serializer with nested files."""
    
    files = ProjectFileSerializer(many=True, read_only=True)
    exports = RepositoryExportSerializer(many=True, read_only=True)
```

**Performance:**
- Use `prefetch_related` in views
- Limit file count for list views
- Full files only in detail view

---

## ✅ Validation Rules

### Field Validation

#### GeneratedProject
- `status`: Valid state transitions
- `output_directory`: Valid path format
- `total_files`: >= 0
- `total_size`: >= 0

#### ProjectFile
- `file_path`: Relative path, no traversal
- `file_size`: >= 0
- `content_hash`: Valid SHA-256 format

#### RepositoryExport
- `export_type`: Valid choice
- `repository_name`: Valid format
- `archive_size`: >= 0 if archive_path provided

---

## 🔧 Custom Methods

### Format File Size

```python
def format_file_size(size_bytes):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
```

---

## 📊 Serializer Optimization

### Optimizations

1. **Select Related:**
   - Use `select_related` for foreign keys
   - Use `prefetch_related` for reverse FKs

2. **Field Selection:**
   - Only include necessary fields
   - Use `fields` or `exclude` explicitly

3. **Lazy Loading:**
   - Nested serializers only when needed
   - Use `SerializerMethodField` for computed values

---

## 🔗 Related Documentation

- **Models:** `02_MODELS_IMPLEMENTATION.md`
- **Views:** `04_VIEWS_IMPLEMENTATION.md`
- **API Architecture:** `../03_ARCHITECTURE/04_API_ARCHITECTURE.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

