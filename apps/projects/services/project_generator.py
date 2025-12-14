"""
Project Generator Service

Generates complete project file structures on the filesystem.
"""

import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, Any, List, Optional
from django.conf import settings
from django.utils import timezone
import logging

from apps.projects.models import GeneratedProject, ProjectFile

logger = logging.getLogger(__name__)


class ProjectGenerationError(Exception):
    """Raised when project generation fails."""
    pass


class ProjectGenerator:
    """
    Service for generating project file structures.
    
    Provides:
    - Directory structure creation
    - File generation from templates
    - Project packaging
    - Repository initialization
    """
    
    def __init__(self, generated_project: GeneratedProject):
        """
        Initialize project generator.
        
        Args:
            generated_project: GeneratedProject instance
        """
        self.generated_project = generated_project
        self.project = generated_project.project
        self.base_dir = Path(generated_project.output_directory)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_file_path(self, path: str) -> bool:
        """
        Validate file path is safe.
        
        Prevents:
        - Path traversal (../, ..\\)
        - Absolute paths
        - Null bytes
        
        Args:
            path: File path to validate
            
        Returns:
            True if valid, False otherwise
        """
        # No absolute paths
        if path.startswith('/') or (path.startswith('\\') and os.name == 'nt'):
            return False
        
        # No path traversal
        if '..' in path or '..\\' in path or '../' in path:
            return False
        
        # No null bytes
        if '\0' in path:
            return False
        
        # Valid characters only (relaxed - allow most characters)
        # Check max length
        if len(path) > 500:
            return False
        
        return True
    
    def get_file_type(self, file_path: str) -> str:
        """
        Determine file type from extension.
        
        Args:
            file_path: File path
            
        Returns:
            File type (e.g., 'python', 'javascript', 'markdown')
        """
        ext = Path(file_path).suffix.lower()
        
        type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text',
            '.sh': 'bash',
            '.bat': 'batch',
            '.sql': 'sql',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.dart': 'dart',
            '.r': 'r',
            '.m': 'matlab',
        }
        
        return type_map.get(ext, 'unknown')
    
    def create_directory(self, path: str) -> Path:
        """
        Create a directory.
        
        Args:
            path: Directory path (relative to project base)
            
        Returns:
            Created Path object
            
        Raises:
            ProjectGenerationError: If path is invalid
        """
        if not self.validate_file_path(path):
            raise ProjectGenerationError(f"Invalid directory path: {path}")
        
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
        Write a file and create ProjectFile record.
        
        Args:
            path: File path (relative to project base)
            content: File content
            encoding: File encoding
            
        Returns:
            Created Path object
            
        Raises:
            ProjectGenerationError: If path is invalid or file too large
        """
        if not self.validate_file_path(path):
            raise ProjectGenerationError(f"Invalid file path: {path}")
        
        # Validate file size
        content_bytes = content.encode(encoding)
        file_size = len(content_bytes)
        
        max_file_size = settings.MAX_FILE_SIZE
        if file_size > max_file_size:
            raise ProjectGenerationError(
                f"File size {file_size} exceeds maximum {max_file_size} bytes"
            )
        
        full_path = self.base_dir / path
        
        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        try:
            with open(full_path, 'w', encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to write file {path}: {e}")
            raise ProjectGenerationError(f"Failed to write file: {str(e)}")
        
        # Calculate content hash
        content_hash = hashlib.sha256(content_bytes).hexdigest()
        
        # Get file type
        file_type = self.get_file_type(path)
        
        # Create ProjectFile record
        file_name = Path(path).name
        content_preview = content[:1000] if len(content) > 1000 else content
        
        ProjectFile.objects.create(
            generated_project=self.generated_project,
            file_path=path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            content_hash=content_hash,
            content_preview=content_preview
        )
        
        return full_path
    
    def generate_project_structure(
        self,
        structure: Dict[str, Any]
    ) -> Dict[str, Path]:
        """
        Generate project structure from definition.
        
        Args:
            structure: Structure definition (dict with files/dirs)
                Example:
                {
                    'src/main.py': '# code...',
                    'tests/': {},
                    'README.md': '# Project...'
                }
            
        Returns:
            Dictionary mapping paths to created Path objects
        """
        created = {}
        
        def process_item(path: str, item: Any):
            """Recursively process structure items."""
            if isinstance(item, dict):
                if not item:  # Empty dict means directory
                    # Create empty directory
                    created[path] = self.create_directory(path)
                else:
                    # Directory with contents
                    if not path.endswith('/'):
                        path = f"{path}/"
                    created[path] = self.create_directory(path)
                    for key, value in item.items():
                        nested_path = f"{path}{key}" if path.endswith('/') else f"{path}/{key}"
                        process_item(nested_path, value)
            elif isinstance(item, str):
                # File with content
                created[path] = self.write_file(path, item)
            else:
                logger.warning(f"Unknown structure item type for {path}: {type(item)}")
        
        # Process structure
        for key, value in structure.items():
            process_item(key, value)
        
        # Update generated project statistics
        self._update_statistics()
        
        return created
    
    def _update_statistics(self):
        """Update GeneratedProject statistics from ProjectFile records."""
        from django.db.models import Sum, Count
        
        stats = ProjectFile.objects.filter(
            generated_project=self.generated_project
        ).aggregate(
            total_files=Count('id'),
            total_size=Sum('file_size')
        )
        
        self.generated_project.total_files = stats['total_files'] or 0
        self.generated_project.total_size = stats['total_size'] or 0
        self.generated_project.save(update_fields=['total_files', 'total_size'])
    
    async def generate_from_workflow_output(
        self,
        workflow_output: Dict[str, Any]
    ) -> Dict[str, Path]:
        """
        Generate project from workflow output.
        
        Args:
            workflow_output: Workflow execution output containing file structure
            
        Returns:
            Dictionary mapping paths to created Path objects
        """
        structure = workflow_output.get('project_structure', {})
        if not structure:
            logger.warning("No project_structure in workflow output")
            return {}
        
        return self.generate_project_structure(structure)
    
    def cleanup(self):
        """Clean up generated project directory."""
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)
            logger.info(f"Cleaned up project directory: {self.base_dir}")

