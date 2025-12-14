# Backend Views Implementation - API Endpoints

**Document Type:** Views Implementation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 03_SERVICES_IMPLEMENTATION.md, 05_SERIALIZERS_IMPLEMENTATION.md, 06_PERMISSIONS_IMPLEMENTATION.md  
**File Size:** 498 lines

---

## 📋 Purpose

This document specifies the implementation of Django REST Framework ViewSets for the AI agent workflow enhancement API endpoints.

---

## 🎯 New ViewSets

### ViewSet 1: GeneratedProjectViewSet

**Location:** `backend/apps/projects/views.py`

**Purpose:** Manage generated projects

**Base Class:** `viewsets.ModelViewSet`

**Permissions:** `[IsAuthenticated, IsProjectMember]`

**Endpoints:**

#### List Generated Projects
**GET** `/api/v1/projects/{project_id}/generated/`

**Query Parameters:**
- `status` - Filter by status
- `page` - Page number
- `page_size` - Items per page

**Response:** Paginated list of GeneratedProject

**Implementation:**
```python
class GeneratedProjectViewSet(viewsets.ModelViewSet):
    serializer_class = GeneratedProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectMember]
    
    def get_queryset(self):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(self.request, project)
        
        queryset = GeneratedProject.objects.filter(project=project)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('project', 'workflow_execution', 'created_by')
    
    @action(detail=False, methods=['post'])
    def generate(self, request, project_id=None):
        """Trigger project generation."""
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        
        # Validate input
        serializer = ProjectGenerationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Start generation (async via Celery)
        task = start_project_generation.delay(
            project_id=str(project.id),
            workflow_id=serializer.validated_data['workflow_id'],
            input_data=serializer.validated_data['input_data'],
            user_id=str(request.user.id)
        )
        
        return Response({
            'task_id': task.id,
            'status': 'started'
        }, status=status.HTTP_202_ACCEPTED)
```

---

#### Retrieve Generated Project
**GET** `/api/v1/projects/{project_id}/generated/{generated_id}/`

**Response:** GeneratedProject with files list

**Implementation:**
```python
def retrieve(self, request, project_id=None, generated_id=None):
    generated_project = self.get_object()
    serializer = self.get_serializer(generated_project)
    return Response(serializer.data)
```

---

### ViewSet 2: ProjectFileViewSet

**Location:** `backend/apps/projects/views.py`

**Purpose:** Manage project files

**Base Class:** `viewsets.ReadOnlyModelViewSet` (read-only for files)

**Permissions:** `[IsAuthenticated, IsProjectMember]`

**Endpoints:**

#### List Files
**GET** `/api/v1/projects/{project_id}/generated/{generated_id}/files/`

**Query Parameters:**
- `file_type` - Filter by file type
- `path` - Filter by path prefix
- `page` - Page number
- `page_size` - Items per page

**Response:** Paginated list of ProjectFile

**Implementation:**
```python
class ProjectFileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectFileSerializer
    permission_classes = [IsAuthenticated, IsProjectMember]
    
    def get_queryset(self):
        generated_id = self.kwargs['generated_id']
        generated_project = get_object_or_404(
            GeneratedProject,
            id=generated_id,
            project_id=self.kwargs['project_id']
        )
        
        # Check permissions
        self.check_object_permissions(self.request, generated_project.project)
        
        queryset = ProjectFile.objects.filter(generated_project=generated_project)
        
        # Filters
        file_type = self.request.query_params.get('file_type')
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        
        path_prefix = self.request.query_params.get('path')
        if path_prefix:
            queryset = queryset.filter(file_path__startswith=path_prefix)
        
        return queryset.order_by('file_path')
```

---

#### Get File Content
**GET** `/api/v1/projects/{project_id}/generated/{generated_id}/files/content/`

**Query Parameters:**
- `path` - File path (required)

**Response:** File content with appropriate Content-Type

**Implementation:**
```python
@action(detail=False, methods=['get'])
def content(self, request, project_id=None, generated_id=None):
    """Download file content."""
    file_path = request.query_params.get('path')
    if not file_path:
        return Response(
            {'error': 'path parameter required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get file
    project_file = get_object_or_404(
        ProjectFile,
        generated_project_id=generated_id,
        file_path=file_path
    )
    
    # Check permissions
    self.check_object_permissions(request, project_file.generated_project.project)
    
    # Read file content
    full_path = project_file.generated_project.output_directory / file_path
    if not full_path.exists():
        return Response(
            {'error': 'File not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    content = full_path.read_bytes()
    
    # Determine content type
    content_type = mimetypes.guess_type(str(full_path))[0] or 'application/octet-stream'
    
    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{project_file.file_name}"'
    return response
```

---

### ViewSet 3: RepositoryExportViewSet

**Location:** `backend/apps/projects/views.py`

**Purpose:** Manage repository exports

**Base Class:** `viewsets.ModelViewSet`

**Permissions:** `[IsAuthenticated, IsProjectMember]`

**Endpoints:**

#### List Exports
**GET** `/api/v1/projects/{project_id}/generated/{generated_id}/exports/`

**Response:** Paginated list of RepositoryExport

---

#### Create Export
**POST** `/api/v1/projects/{project_id}/generated/{generated_id}/export/`

**Request:**
```json
{
  "export_type": "zip",
  "repository_name": "my-project",
  "config": {}
}
```

**Response:** Created RepositoryExport

**Implementation:**
```python
@action(detail=False, methods=['post'], url_path='export')
def create_export(self, request, project_id=None, generated_id=None):
    """Create repository export."""
    generated_project = get_object_or_404(
        GeneratedProject,
        id=generated_id,
        project_id=project_id
    )
    
    # Check permissions
    self.check_object_permissions(request, generated_project.project)
    
    # Validate export can be created
    if generated_project.status != 'completed':
        return Response(
            {'error': 'Project generation must be completed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = RepositoryExportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Create export job
    export = serializer.save(
        generated_project=generated_project,
        created_by=request.user
    )
    
    # Start export task (async)
    task = execute_repository_export.delay(
        export_id=str(export.id),
        user_id=str(request.user.id)
    )
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)
```

---

#### Export to GitHub
**POST** `/api/v1/projects/{project_id}/generated/{generated_id}/export-to-github/`

**Request:**
```json
{
  "repository_name": "my-project",
  "organization": "myorg",
  "private": false,
  "github_token": "token"
}
```

**Response:** Created RepositoryExport with status

---

#### Export to GitLab
**POST** `/api/v1/projects/{project_id}/generated/{generated_id}/export-to-gitlab/`

**Request:**
```json
{
  "project_name": "my-project",
  "namespace": "mygroup",
  "visibility": "private",
  "gitlab_token": "token"
}
```

**Response:** Created RepositoryExport with status

---

#### Download Export
**GET** `/api/v1/exports/{export_id}/download/`

**Response:** Archive file download

**Implementation:**
```python
class ExportDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, export_id):
        export = get_object_or_404(RepositoryExport, id=export_id)
        
        # Check permissions
        self.check_object_permissions(request, export.generated_project.project)
        
        if export.status != 'completed' or not export.archive_path:
            return Response(
                {'error': 'Export not ready'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        archive_path = Path(export.archive_path)
        if not archive_path.exists():
            return Response(
                {'error': 'Archive not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        content = archive_path.read_bytes()
        content_type = 'application/zip' if export.export_type == 'zip' else 'application/tar+gzip'
        
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{archive_path.name}"'
        return response
```

---

## 🔐 Permission Implementation

### Permission Classes

**IsProjectMember:**
- Check user is project member or owner
- Super admin bypass
- Organization admin access

**Implementation:** See `06_PERMISSIONS_IMPLEMENTATION.md`

---

## 📊 Pagination

**Class:** `PageNumberPagination`

**Configuration:**
- `page_size`: 25 (default)
- `page_size_query_param`: `page_size`
- `max_page_size`: 100

---

## ⚠️ Error Handling

### Custom Exceptions

```python
class ProjectGenerationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Project generation failed'

class FileNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'File not found'

class ExportError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Export failed'
```

---

## 🔗 URL Configuration

**Location:** `backend/apps/projects/urls.py`

**Routes:**
```python
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

## 🔗 Related Documentation

- **Services:** `03_SERVICES_IMPLEMENTATION.md`
- **Serializers:** `05_SERIALIZERS_IMPLEMENTATION.md`
- **Permissions:** `06_PERMISSIONS_IMPLEMENTATION.md`
- **API Architecture:** `../03_ARCHITECTURE/04_API_ARCHITECTURE.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

