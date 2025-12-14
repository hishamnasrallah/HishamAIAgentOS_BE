# Backend Services Implementation - AI Agent Workflow Enhancement

**Document Type:** Backend Services Implementation Specification  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 02_MODELS_IMPLEMENTATION.md, 04_VIEWS_IMPLEMENTATION.md, 06_PERMISSIONS_IMPLEMENTATION.md  
**File Size:** 498 lines

---

## 📋 Overview

This document specifies the implementation of new backend services required to enable full SDLC automation and project generation capabilities.

---

## 🔧 Service 1: AgentAPICaller

### Purpose
Allow agents to directly call HishamOS REST APIs without requiring service layer parsing.

### Location
`backend/apps/agents/services/api_caller.py`

### Implementation Specification

```python
"""
Agent API Caller Service

Allows agents to make authenticated API calls to HishamOS services.
"""

from typing import Dict, Any, Optional, List
import httpx
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.authentication.services.jwt_service import jwt_service

User = get_user_model()


class AgentAPICaller:
    """
    Service for agents to call HishamOS APIs directly.
    
    Provides:
    - Authenticated API requests
    - Endpoint discovery
    - Error handling and retries
    - Response formatting for agents
    """
    
    def __init__(self, user: User):
        """
        Initialize API caller with user context.
        
        Args:
            user: User making the API call (for auth/permissions)
        """
        self.user = user
        self.base_url = settings.BACKEND_URL
        self.token = self._get_auth_token()
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={'Authorization': f'Bearer {self.token}'},
            timeout=30.0
        )
    
    def _get_auth_token(self) -> str:
        """Generate JWT token for API authentication."""
        return jwt_service.generate_token(self.user)
    
    async def call(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an API call.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (e.g., '/api/v1/projects/')
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            APIError: If API call fails
        """
        try:
            # Ensure endpoint starts with /
            if not endpoint.startswith('/'):
                endpoint = f'/{endpoint}'
            
            # Ensure endpoint includes /api/v1/ prefix
            if not endpoint.startswith('/api/v1/'):
                endpoint = f'/api/v1{endpoint}'
            
            response = await self.client.request(
                method=method.upper(),
                url=endpoint,
                json=data,
                params=params
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise APIError(
                f"API call failed: {e.response.status_code} - {e.response.text}",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            raise APIError(f"Request error: {str(e)}")
    
    async def create_story(
        self,
        project_id: str,
        title: str,
        description: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a user story via API.
        
        Args:
            project_id: Project UUID
            title: Story title
            description: Story description
            **kwargs: Additional story fields
            
        Returns:
            Created story data
        """
        data = {
            'project': project_id,
            'title': title,
            'description': description,
            **kwargs
        }
        return await self.call('POST', f'/projects/{project_id}/stories/', data=data)
    
    async def update_story_status(
        self,
        story_id: str,
        status: str
    ) -> Dict[str, Any]:
        """
        Update story status via API.
        
        Args:
            story_id: Story UUID
            status: New status
            
        Returns:
            Updated story data
        """
        return await self.call(
            'PATCH',
            f'/stories/{story_id}/',
            data={'status': status}
        )
    
    async def create_sprint(
        self,
        project_id: str,
        name: str,
        start_date: str,
        end_date: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a sprint via API.
        
        Args:
            project_id: Project UUID
            name: Sprint name
            start_date: Sprint start date (ISO format)
            end_date: Sprint end date (ISO format)
            **kwargs: Additional sprint fields
            
        Returns:
            Created sprint data
        """
        data = {
            'project': project_id,
            'name': name,
            'start_date': start_date,
            'end_date': end_date,
            **kwargs
        }
        return await self.call('POST', f'/projects/{project_id}/sprints/', data=data)
    
    async def discover_endpoints(self) -> List[Dict[str, Any]]:
        """
        Discover available API endpoints.
        
        Returns:
            List of endpoint definitions
        """
        # Implementation would fetch from OpenAPI/Swagger schema
        # or maintain a static list of available endpoints
        pass
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class APIError(Exception):
    """Raised when API call fails."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
```

### Integration Points

1. **Agent Execution Engine:**
   - Pass `AgentAPICaller` instance to agents via context
   - Agents can use `api_caller.call()` method

2. **Workflow Steps:**
   - New `api_call` step type uses `AgentAPICaller`
   - Step definition includes method, endpoint, data

3. **Permissions:**
   - Uses user context for authorization
   - Respects existing permission classes

---

## 🔧 Service 2: ProjectGenerator

### Purpose
Generate complete project file structures on the filesystem.

### Location
`backend/apps/projects/services/project_generator.py`

### Implementation Specification

```python
"""
Project Generator Service

Generates complete project file structures on the filesystem.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from django.conf import settings
from django.core.files.storage import default_storage


class ProjectGenerator:
    """
    Service for generating project file structures.
    
    Provides:
    - Directory structure creation
    - File generation from templates
    - Project packaging
    - Repository initialization
    """
    
    def __init__(self, project_id: str):
        """
        Initialize project generator.
        
        Args:
            project_id: Project UUID
        """
        self.project_id = project_id
        self.base_dir = Path(settings.GENERATED_PROJECTS_DIR) / str(project_id)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def create_directory(self, path: str) -> Path:
        """
        Create a directory.
        
        Args:
            path: Directory path (relative to project base)
            
        Returns:
            Created Path object
        """
        full_path = self.base_dir / path
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path
    
    def write_file(
        self,
        path: str,
        content: str,
        encoding: str = 'utf-8'
    ) -> Path:
        """
        Write a file.
        
        Args:
            path: File path (relative to project base)
            content: File content
            encoding: File encoding
            
        Returns:
            Created Path object
        """
        full_path = self.base_dir / path
        
        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(full_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return full_path
    
    def generate_project_structure(
        self,
        structure: Dict[str, Any]
    ) -> Dict[str, Path]:
        """
        Generate project structure from definition.
        
        Args:
            structure: Structure definition (dict with files/dirs)
            
        Returns:
            Dictionary mapping paths to created Path objects
        """
        created = {}
        
        def process_item(path: str, item: Any):
            if isinstance(item, dict):
                # Directory with contents
                self.create_directory(path)
                for key, value in item.items():
                    process_item(f"{path}/{key}", value)
            elif isinstance(item, str):
                # File with content
                created[path] = self.write_file(path, item)
            elif isinstance(item, list):
                # List of files (empty directory)
                self.create_directory(path)
        
        for key, value in structure.items():
            process_item(key, value)
        
        return created
    
    def generate_from_template(
        self,
        template_path: str,
        output_path: str,
        context: Dict[str, Any]
    ) -> Path:
        """
        Generate file from template.
        
        Args:
            template_path: Template file path
            output_path: Output file path
            context: Template context variables
            
        Returns:
            Created Path object
        """
        from django.template import Template, Context
        
        # Load template
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        template = Template(template_content)
        content = template.render(Context(context))
        
        return self.write_file(output_path, content)
    
    def initialize_git_repository(self) -> bool:
        """
        Initialize Git repository.
        
        Returns:
            True if successful
        """
        import subprocess
        
        try:
            subprocess.run(
                ['git', 'init'],
                cwd=self.base_dir,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def create_gitignore(self, patterns: List[str]) -> Path:
        """
        Create .gitignore file.
        
        Args:
            patterns: List of ignore patterns
            
        Returns:
            Created Path object
        """
        content = '\n'.join(patterns)
        return self.write_file('.gitignore', content)
    
    def create_readme(self, content: str) -> Path:
        """
        Create README.md file.
        
        Args:
            content: README content
            
        Returns:
            Created Path object
        """
        return self.write_file('README.md', content)
    
    def package_project(
        self,
        format: str = 'zip'
    ) -> Path:
        """
        Package project for export.
        
        Args:
            format: Archive format (zip, tar, tar.gz)
            
        Returns:
            Path to archive file
        """
        import shutil
        
        archive_path = self.base_dir.parent / f"{self.project_id}.{format}"
        
        if format == 'zip':
            shutil.make_archive(
                str(archive_path.with_suffix('')),
                'zip',
                self.base_dir
            )
        elif format in ('tar', 'tar.gz'):
            shutil.make_archive(
                str(archive_path.with_suffix('')),
                format.replace('tar.gz', 'gztar'),
                self.base_dir
            )
        
        return archive_path
    
    def cleanup(self):
        """Clean up generated files."""
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)
```

### Configuration

Add to `settings.py`:
```python
GENERATED_PROJECTS_DIR = os.path.join(BASE_DIR, 'generated-projects')
```

### Integration Points

1. **Workflow Steps:**
   - New `file_generation` step type uses `ProjectGenerator`
   - Step definition includes file paths and content

2. **Agent Execution:**
   - Agents can request file generation via context
   - File generation results stored in workflow state

3. **API Endpoints:**
   - Export endpoint uses `package_project()`
   - Download endpoint serves packaged files

---

## 🔧 Service 3: RepositoryExporter

### Purpose
Export generated projects as Git repositories with GitHub/GitLab integration.

### Location
`backend/apps/projects/services/repository_exporter.py`

### Implementation Specification

```python
"""
Repository Exporter Service

Exports generated projects as Git repositories.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from .project_generator import ProjectGenerator


class RepositoryExporter:
    """
    Service for exporting projects as Git repositories.
    
    Provides:
    - Git repository initialization
    - GitHub/GitLab integration
    - Repository packaging
    """
    
    def __init__(self, project_id: str):
        """
        Initialize repository exporter.
        
        Args:
            project_id: Project UUID
        """
        self.project_id = project_id
        self.generator = ProjectGenerator(project_id)
    
    async def export_to_github(
        self,
        github_token: str,
        repository_name: str,
        organization: Optional[str] = None,
        private: bool = False
    ) -> Dict[str, Any]:
        """
        Export project to GitHub.
        
        Args:
            github_token: GitHub personal access token
            repository_name: Repository name
            organization: GitHub organization (optional)
            private: Whether repository is private
            
        Returns:
            Repository information
        """
        # Implementation would use GitHub API
        # 1. Create repository via GitHub API
        # 2. Initialize Git repo locally
        # 3. Add remote
        # 4. Push files
        pass
    
    async def export_to_gitlab(
        self,
        gitlab_token: str,
        project_name: str,
        namespace: Optional[str] = None,
        visibility: str = 'private'
    ) -> Dict[str, Any]:
        """
        Export project to GitLab.
        
        Args:
            gitlab_token: GitLab personal access token
            project_name: Project name
            namespace: GitLab namespace (optional)
            visibility: Repository visibility (private, internal, public)
            
        Returns:
            Project information
        """
        # Similar to GitHub implementation
        pass
    
    def export_as_zip(self) -> Path:
        """Export project as ZIP archive."""
        return self.generator.package_project('zip')
    
    def export_as_tar(self) -> Path:
        """Export project as TAR archive."""
        return self.generator.package_project('tar.gz')
```

---

## 🔄 Service Integration

### Workflow Integration

```python
# In workflow step execution
if step.type == 'api_call':
    api_caller = AgentAPICaller(user=user)
    result = await api_caller.call(**step.config)

elif step.type == 'file_generation':
    generator = ProjectGenerator(project_id=project_id)
    result = generator.generate_project_structure(**step.config)

elif step.type == 'repo_creation':
    exporter = RepositoryExporter(project_id=project_id)
    result = await exporter.export_to_github(**step.config)
```

---

## 📊 Testing Requirements

1. **Unit Tests:**
   - Test each service method independently
   - Mock external dependencies
   - > 90% code coverage

2. **Integration Tests:**
   - Test service interactions
   - Test with real file system (temp directories)
   - Test API integration

3. **End-to-End Tests:**
   - Test complete workflow execution
   - Test file generation and export
   - Test repository creation

---

## 🔗 Related Documentation

- **Models:** `02_MODELS_IMPLEMENTATION.md`
- **Views:** `04_VIEWS_IMPLEMENTATION.md`
- **Permissions:** `06_PERMISSIONS_IMPLEMENTATION.md`
- **Integration:** `../06_INTEGRATION/`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13


