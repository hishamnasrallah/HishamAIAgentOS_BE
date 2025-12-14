"""
Repository Exporter Service

Exports generated projects as Git repositories with GitHub/GitLab integration.
"""

import os
import subprocess
import shutil
import logging
import httpx
from pathlib import Path
from typing import Optional, Dict, Any
from django.conf import settings
from django.utils import timezone

from apps.projects.models import GeneratedProject, RepositoryExport

logger = logging.getLogger(__name__)


class RepositoryExportError(Exception):
    """Raised when repository export fails."""
    pass


class RepositoryExporter:
    """
    Service for exporting projects as Git repositories.
    
    Provides:
    - Git repository initialization
    - GitHub/GitLab integration
    - Repository packaging (ZIP, TAR)
    """
    
    def __init__(self, generated_project: GeneratedProject):
        """
        Initialize repository exporter.
        
        Args:
            generated_project: GeneratedProject instance
        """
        self.generated_project = generated_project
        self.project = generated_project.project
        self.base_dir = Path(generated_project.output_directory)
    
    def initialize_git_repository(self) -> bool:
        """
        Initialize Git repository in project directory.
        
        Returns:
            True if successful
        """
        if not self.base_dir.exists():
            raise RepositoryExportError(f"Project directory does not exist: {self.base_dir}")
        
        try:
            # Check if git is installed
            subprocess.run(['git', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Git is not installed or not in PATH")
            return False
        
        try:
            # Initialize git repository
            result = subprocess.run(
                ['git', 'init'],
                cwd=self.base_dir,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Configure git user (use project name or default)
            subprocess.run(
                ['git', 'config', 'user.name', 'HishamOS'],
                cwd=self.base_dir,
                check=True,
                capture_output=True
            )
            subprocess.run(
                ['git', 'config', 'user.email', 'noreply@hishamos.com'],
                cwd=self.base_dir,
                check=True,
                capture_output=True
            )
            
            logger.info(f"Initialized Git repository in {self.base_dir}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to initialize Git repository: {e.stderr}")
            return False
    
    def add_files_to_git(self) -> bool:
        """
        Add all files to Git and create initial commit.
        
        Returns:
            True if successful
        """
        if not self.base_dir.exists():
            return False
        
        try:
            # Add all files
            subprocess.run(
                ['git', 'add', '.'],
                cwd=self.base_dir,
                check=True,
                capture_output=True
            )
            
            # Create initial commit
            subprocess.run(
                ['git', 'commit', '-m', f'Initial commit: {self.project.name}'],
                cwd=self.base_dir,
                check=True,
                capture_output=True
            )
            
            logger.info(f"Added files and created initial commit")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add files to Git: {e.stderr}")
            return False
    
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
            Repository information with URL
        """
        # Initialize Git repository
        if not self.initialize_git_repository():
            raise RepositoryExportError("Failed to initialize Git repository")
        
        if not self.add_files_to_git():
            raise RepositoryExportError("Failed to add files to Git")
        
        # Create repository via GitHub API
        async with httpx.AsyncClient() as client:
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            # Determine repository owner
            if organization:
                owner = organization
                url = f"https://api.github.com/orgs/{owner}/repos"
            else:
                # Get authenticated user
                user_response = await client.get(
                    'https://api.github.com/user',
                    headers=headers
                )
                user_response.raise_for_status()
                user_data = user_response.json()
                owner = user_data['login']
                url = 'https://api.github.com/user/repos'
            
            # Create repository
            repo_data = {
                'name': repository_name,
                'private': private,
                'auto_init': False,
            }
            
            response = await client.post(url, json=repo_data, headers=headers)
            
            if response.status_code == 201:
                repo_info = response.json()
                repository_url = repo_info['clone_url']
                
                # Add remote and push
                try:
                    subprocess.run(
                        ['git', 'remote', 'add', 'origin', repository_url],
                        cwd=self.base_dir,
                        check=True,
                        capture_output=True
                    )
                    
                    # Push to GitHub
                    subprocess.run(
                        ['git', 'push', '-u', 'origin', 'main'],
                        cwd=self.base_dir,
                        check=True,
                        capture_output=True,
                        env={**os.environ, 'GIT_ASKPASS': 'echo', 'GIT_TERMINAL_PROMPT': '0'}
                    )
                    
                    # Try master branch if main fails
                except subprocess.CalledProcessError:
                    try:
                        subprocess.run(
                            ['git', 'branch', '-M', 'main'],
                            cwd=self.base_dir,
                            check=True,
                            capture_output=True
                        )
                        subprocess.run(
                            ['git', 'push', '-u', 'origin', 'main'],
                            cwd=self.base_dir,
                            check=True,
                            capture_output=True,
                            env={**os.environ, 'GIT_ASKPASS': 'echo', 'GIT_TERMINAL_PROMPT': '0'}
                        )
                    except subprocess.CalledProcessError as e:
                        logger.warning(f"Git push failed: {e.stderr}")
                        # Repository was created but push failed
                
                return {
                    'repository_url': repository_url,
                    'repository_name': repository_name,
                    'owner': owner,
                    'private': private
                }
            else:
                error_text = response.text
                raise RepositoryExportError(
                    f"Failed to create GitHub repository: {response.status_code} - {error_text}"
                )
    
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
            namespace: GitLab namespace/group (optional)
            visibility: Repository visibility (private, internal, public)
            
        Returns:
            Project information with URL
        """
        # Initialize Git repository
        if not self.initialize_git_repository():
            raise RepositoryExportError("Failed to initialize Git repository")
        
        if not self.add_files_to_git():
            raise RepositoryExportError("Failed to add files to Git")
        
        # Create project via GitLab API
        async with httpx.AsyncClient() as client:
            headers = {
                'PRIVATE-TOKEN': gitlab_token,
                'Content-Type': 'application/json'
            }
            
            # Determine namespace
            if not namespace:
                # Get authenticated user's namespace
                user_response = await client.get(
                    'https://gitlab.com/api/v4/user',
                    headers=headers
                )
                user_response.raise_for_status()
                user_data = user_response.json()
                namespace = user_data['username']
            
            # Create project
            project_data = {
                'name': project_name,
                'visibility': visibility,
                'initialize_with_readme': False,
            }
            
            url = f'https://gitlab.com/api/v4/projects'
            if namespace:
                # Create under namespace
                url = f'https://gitlab.com/api/v4/projects?namespace_id={namespace}'
                # First, get namespace ID
                ns_response = await client.get(
                    f'https://gitlab.com/api/v4/namespaces?search={namespace}',
                    headers=headers
                )
                if ns_response.status_code == 200:
                    namespaces = ns_response.json()
                    if namespaces:
                        project_data['namespace_id'] = namespaces[0]['id']
            
            response = await client.post(url, json=project_data, headers=headers)
            
            if response.status_code == 201:
                project_info = response.json()
                repository_url = project_info['http_url_to_repo']
                
                # Add remote and push
                try:
                    subprocess.run(
                        ['git', 'remote', 'add', 'origin', repository_url],
                        cwd=self.base_dir,
                        check=True,
                        capture_output=True
                    )
                    
                    subprocess.run(
                        ['git', 'push', '-u', 'origin', 'main'],
                        cwd=self.base_dir,
                        check=True,
                        capture_output=True,
                        env={**os.environ, 'GIT_ASKPASS': 'echo', 'GIT_TERMINAL_PROMPT': '0'}
                    )
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Git push failed: {e.stderr}")
                
                return {
                    'repository_url': repository_url,
                    'project_name': project_name,
                    'namespace': namespace,
                    'visibility': visibility
                }
            else:
                error_text = response.text
                raise RepositoryExportError(
                    f"Failed to create GitLab project: {response.status_code} - {error_text}"
                )
    
    def export_as_zip(self) -> Path:
        """
        Export project as ZIP archive.
        
        Returns:
            Path to ZIP archive
        """
        import os
        
        if not self.base_dir.exists():
            raise RepositoryExportError(f"Project directory does not exist: {self.base_dir}")
        
        # Create archive directory if it doesn't exist
        archive_dir = Path(settings.GENERATED_PROJECTS_DIR) / 'archives'
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        archive_path = archive_dir / f"{self.generated_project.id}.zip"
        
        # Create ZIP archive
        shutil.make_archive(
            str(archive_path.with_suffix('')),
            'zip',
            self.base_dir
        )
        
        logger.info(f"Created ZIP archive: {archive_path}")
        return archive_path
    
    def export_as_tar(self, gzip: bool = False) -> Path:
        """
        Export project as TAR archive.
        
        Args:
            gzip: Whether to compress with gzip
            
        Returns:
            Path to TAR archive
        """
        import os
        
        if not self.base_dir.exists():
            raise RepositoryExportError(f"Project directory does not exist: {self.base_dir}")
        
        # Create archive directory if it doesn't exist
        archive_dir = Path(settings.GENERATED_PROJECTS_DIR) / 'archives'
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        format_type = 'gztar' if gzip else 'tar'
        ext = '.tar.gz' if gzip else '.tar'
        archive_path = archive_dir / f"{self.generated_project.id}{ext}"
        
        # Create TAR archive
        shutil.make_archive(
            str(archive_path.with_suffix('').with_suffix('') if gzip else archive_path.with_suffix('')),
            format_type,
            self.base_dir
        )
        
        logger.info(f"Created TAR archive: {archive_path}")
        return archive_path

