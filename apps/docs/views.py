"""
Documentation viewer API views.
"""

import os
import re
from pathlib import Path
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from django.conf import settings
import markdown
import logging

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger(__name__)


class DocumentationViewSet(viewsets.ViewSet):
    """
    ViewSet for documentation viewer.
    
    Provides endpoints to:
    - List all markdown files
    - Get file content
    - Search documentation
    """
    
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List all markdown files - alias for list_files."""
        return self.list_files(request)
    
    def get_docs_path(self):
        """Get the documentation directory path.
        
        Priority order:
        1. DOCS_PATH environment variable (for separate docs repo)
        2. Project root/docs (new organized location)
        3. backend/docs (old location - deprecated)
        """
        base_dir = Path(settings.BASE_DIR)
        
        # Option 1: Environment variable (for separate docs repo or custom path)
        docs_path_env = os.getenv('DOCS_PATH')
        if docs_path_env:
            docs_path = Path(docs_path_env)
            if docs_path.exists():
                logger.info(f"Using DOCS_PATH from environment: {docs_path}")
                return docs_path
            else:
                logger.warning(f"DOCS_PATH set but path does not exist: {docs_path_env}")
        
        # Option 2: Project root/docs (new organized location)
        project_root = base_dir.parent
        docs_path_root = project_root / 'docs'
        if docs_path_root.exists():
            return docs_path_root
        
        # Option 3: Fallback to backend/docs (old location - deprecated)
        docs_path_backend = base_dir / 'docs'
        if docs_path_backend.exists():
            logger.warning("Using deprecated backend/docs location. Consider moving to root/docs or using DOCS_PATH")
            return docs_path_backend
        
        # Return root/docs as default (will be created if needed)
        logger.warning(f"Documentation directory not found. Returning default path: {docs_path_root}")
        return docs_path_root
    
    @action(detail=False, methods=['get'], url_path='list_files')
    def list_files(self, request):
        """
        List all markdown files in the docs directory.
        
        Query params:
        - view: 'tree' (default) or 'topics' - how to organize the files
        
        Returns a tree structure or topic-based organization of all .md files.
        """
        try:
            docs_path = self.get_docs_path()
            
            if not docs_path.exists():
                return Response({
                    'error': 'Documentation directory not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            view_type = request.query_params.get('view', 'tree')  # 'tree' or 'topics'
            
            files = []
            directories = {}
            
            # Walk through all files
            for root, dirs, filenames in os.walk(docs_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # Get relative path from docs directory
                rel_path = os.path.relpath(root, docs_path)
                if rel_path == '.':
                    rel_path = ''
                
                # Process markdown files
                for filename in filenames:
                    if filename.endswith('.md'):
                        file_path = os.path.join(root, filename)
                        rel_file_path = os.path.relpath(file_path, docs_path)
                        
                        # Get file stats
                        stat = os.stat(file_path)
                        
                        # Extract directory structure
                        dir_parts = rel_file_path.split(os.sep)
                        if len(dir_parts) > 1:
                            directory = os.sep.join(dir_parts[:-1])
                        else:
                            directory = ''
                        
                        # Try to read file content for better role classification
                        description = None
                        metadata = None
                        roles_from_metadata = []
                        file_content = None
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                file_content = content  # Store for role classification
                                
                            # Try to parse YAML frontmatter
                            yaml_metadata, _ = self._parse_yaml_frontmatter(content)
                            if yaml_metadata:
                                metadata = yaml_metadata
                                # Get description from metadata if available
                                description = yaml_metadata.get('description', None)
                                if description and isinstance(description, str):
                                    description = description[:200]  # Limit length
                                
                                # Get roles from metadata if available (support multiple roles)
                                target_audience = yaml_metadata.get('target_audience', {})
                                if isinstance(target_audience, dict):
                                    roles_from_metadata = []
                                    # Add primary roles
                                    if target_audience.get('primary'):
                                        primary = target_audience['primary']
                                        if isinstance(primary, list):
                                            roles_from_metadata.extend(primary)
                                        elif isinstance(primary, str):
                                            roles_from_metadata.append(primary)
                                    # Add secondary roles
                                    if target_audience.get('secondary'):
                                        secondary = target_audience['secondary']
                                        if isinstance(secondary, list):
                                            roles_from_metadata.extend(secondary)
                                        elif isinstance(secondary, str):
                                            roles_from_metadata.append(secondary)
                                    # Remove duplicates while preserving order
                                    roles_from_metadata = list(dict.fromkeys(roles_from_metadata))
                                
                                # Also check for direct roles field in metadata (backward compatibility)
                                if not roles_from_metadata and yaml_metadata.get('roles'):
                                    roles_field = yaml_metadata['roles']
                                    if isinstance(roles_field, list):
                                        roles_from_metadata = roles_field
                                    elif isinstance(roles_field, str):
                                        roles_from_metadata = [roles_field]
                            
                            # Fallback: extract description from markdown if no metadata
                            if not description:
                                lines = content.split('\n')[:10]
                                for line in lines:
                                    line = line.strip()
                                    if line and not line.startswith('#') and not line.startswith('---'):
                                        description = line[:150]  # First 150 characters
                                        break
                        except Exception:
                            pass  # If we can't read, just skip description
                        
                        # Classify by role/interest (use metadata roles if available, otherwise classify)
                        # Use file content for more accurate classification
                        if roles_from_metadata:
                            # Start with metadata roles (they are more accurate)
                            roles = roles_from_metadata.copy()
                            # Add classified roles that aren't already present (for coverage)
                            classified_roles = self._classify_by_roles(
                                filename, rel_file_path, directory, description or '', file_content
                            )
                            for classified_role in classified_roles:
                                if classified_role not in roles:
                                    roles.append(classified_role)
                        else:
                            # Use enhanced classification with content analysis
                            roles = self._classify_by_roles(
                                filename, rel_file_path, directory, description or '', file_content
                            )
                        
                        # Ensure at least one role exists
                        if not roles:
                            roles = ['General']
                        
                        # Remove duplicates while preserving order
                        seen = set()
                        unique_roles = []
                        for role in roles:
                            if role not in seen:
                                seen.add(role)
                                unique_roles.append(role)
                        roles = unique_roles
                        
                        file_info = {
                            'name': filename,
                            'path': rel_file_path.replace(os.sep, '/'),  # Use forward slashes
                            'directory': directory.replace(os.sep, '/') if directory else '',
                            'size': stat.st_size,
                            'modified': stat.st_mtime,
                            'full_path': file_path,
                            'description': description,  # Add description if available
                            'roles': roles,  # Add role tags
                            'metadata': metadata  # Add parsed YAML metadata if available
                        }
                        files.append(file_info)
            
            # Sort files by path
            files.sort(key=lambda x: x['path'])
            
            # Filter by role if provided
            role_filter = request.query_params.get('role')
            if role_filter:
                files = [f for f in files if role_filter in f.get('roles', [])]
            
            # Build response based on view type
            if view_type == 'topics':
                # Classify by topics
                topics = self._classify_by_topics(files)
                return Response({
                    'files': files,
                    'topics': topics,
                    'view': 'topics',
                    'total_files': len(files),
                    'total_topics': len(topics),
                    'available_roles': self._get_available_roles(files)
                })
            else:
                # Build directory tree (default)
                tree = self._build_directory_tree(files)
                return Response({
                    'files': files,
                    'tree': tree,
                    'view': 'tree',
                    'total_files': len(files),
                    'available_roles': self._get_available_roles(files)
                })
            
        except Exception as e:
            logger.error(f"Error listing documentation files: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _build_directory_tree(self, files):
        """Build a directory tree structure from file list."""
        tree = {}
        
        for file_info in files:
            path_parts = file_info['path'].split('/')
            current = tree
            
            # Navigate/create directory structure
            for part in path_parts[:-1]:  # All parts except filename
                if part not in current:
                    current[part] = {
                        'type': 'directory',
                        'children': {}
                    }
                elif 'children' not in current[part]:
                    # Convert existing entry to directory if it's not already
                    existing = current[part]
                    current[part] = {
                        'type': 'directory',
                        'children': existing if isinstance(existing, dict) else {}
                    }
                current = current[part]['children']
            
            # Add file to current directory
            filename = path_parts[-1]
            current[filename] = {
                'type': 'file',
                'path': file_info['path'],
                'name': file_info['name'],
                'size': file_info['size'],
                'modified': file_info.get('modified'),
                'description': file_info.get('description'),
                'roles': file_info.get('roles', []),
                'metadata': file_info.get('metadata')
            }
        
        return tree
    
    def _classify_by_roles(self, filename, path, directory, description, content=None):
        """
        Classify files by role/interest (BA, QA, Developer, Technical Writer, etc.)
        Returns a list of role tags for the file.
        Enhanced version that analyzes actual file content for better accuracy.
        """
        roles = []
        filename_lower = filename.lower()
        path_lower = path.lower()
        directory_lower = directory.lower() if directory else ''
        description_lower = description.lower() if description else ''
        content_lower = (content or '').lower()[:5000]  # First 5000 chars for performance
        
        # Combine all text for pattern matching
        all_text = f"{filename_lower} {path_lower} {directory_lower} {description_lower} {content_lower}"
        
        # Enhanced role patterns with weighted scoring
        role_patterns = {
            'Business Analyst': {
                'strong': [
                    'requirements', 'requirement', 'business requirements', 'user story', 'user stories',
                    'stakeholder', 'stakeholders', 'elicitation', 'business analysis', 'ba ',
                    'business process', 'use case', 'use cases', 'functional requirements',
                    'business rules', 'acceptance criteria', 'product owner', 'product backlog',
                    'business value', 'business needs', 'business goals', 'project plan',
                    'project planning', 'roadmap', 'project status', 'milestone', 'sprint planning'
                ],
                'medium': [
                    'planning', 'plan', 'specification', 'project', 'status report', 'phase status',
                    'tracking', 'comprehensive audit', 'project roadmap'
                ]
            },
            'QA / Tester': {
                'strong': [
                    'test', 'testing', 'qa', 'quality assurance', 'uat', 'test case', 'test cases',
                    'manual test', 'automation', 'test execution', 'test checklist', 'test guide',
                    'test results', 'bug', 'bugs', 'defect', 'verification', 'validation',
                    'test coverage', 'test plan', 'user acceptance testing'
                ],
                'medium': [
                    'checklist', 'quick start', 'guide', 'manual testing'
                ]
            },
            'Developer': {
                'strong': [
                    'development', 'developer', 'coding', 'code', 'implementation', 'api',
                    'backend', 'frontend', 'programming', 'technical', 'architecture', 'design',
                    'sdlc', 'dev', 'deployment', 'infrastructure', 'docker', 'database', 'db',
                    'class', 'function', 'method', 'module', 'component', 'service', 'endpoint',
                    'framework', 'library', 'migration', 'model', 'view', 'controller'
                ],
                'medium': [
                    'guide', 'manual', 'reference', 'technical architecture', 'system design'
                ]
            },
            'Project Manager': {
                'strong': [
                    'project management', 'project manager', 'pm', 'sprint', 'sprints',
                    'milestone', 'milestones', 'roadmap', 'project plan', 'project planning',
                    'release plan', 'status report', 'status reports', 'project status',
                    'progress', 'tracking', 'task', 'tasks', 'backlog', 'sprint planning',
                    'project timeline', 'project schedule', 'delivery', 'deadline'
                ],
                'medium': [
                    'plan', 'planning', 'status', 'phase', 'phase status', 'completion',
                    'tracking', 'audit', 'summary', 'overview', 'report'
                ]
            },
            'CTO / Technical Lead': {
                'strong': [
                    'architecture', 'technical architecture', 'system architecture', 'design',
                    'system design', 'technical design', 'cto', 'technical lead', 'leadership',
                    'strategy', 'roadmap', 'vision', 'complete design', 'technical reference',
                    'master development', 'technical strategy', 'technology stack'
                ],
                'medium': [
                    'overview', 'summary', 'guide', 'reference', 'specification'
                ]
            },
            'Technical Writer': {
                'strong': [
                    'documentation', 'doc', 'guide', 'manual', 'tutorial', 'walkthrough',
                    'reference', 'specification', 'specs', 'documentation_maintenance',
                    'api_documentation', 'docs_viewer', 'user guide', 'user manual'
                ],
                'medium': [
                    'readme', 'index', 'overview', 'introduction', 'getting started'
                ]
            },
            'DevOps': {
                'strong': [
                    'devops', 'deployment', 'infrastructure', 'docker', 'ci/cd', 'cicd',
                    'production', 'environment', 'server', 'kubernetes', 'k8s', 'terraform',
                    'dockerfile', 'docker-compose', 'container', 'containers', 'orchestration'
                ],
                'medium': [
                    'deployment guide', 'infrastructure guide', 'deployment infrastructure'
                ]
            },
            'Scrum Master': {
                'strong': [
                    'scrum', 'agile', 'sprint', 'retrospective', 'standup', 'ceremony',
                    'backlog', 'velocity', 'burndown', 'kanban', 'sprint planning',
                    'sprint review', 'daily standup', 'scrum master'
                ],
                'medium': [
                    'agile', 'sprint', 'planning', 'tracking'
                ]
            },
            'Infrastructure': {
                'strong': [
                    'infrastructure', 'infra', 'server', 'network', 'security', 'monitoring',
                    'logging', 'tracking', 'audit', 'performance', 'scalability', 'availability',
                    'backup', 'disaster recovery', 'cloud', 'aws', 'azure', 'gcp'
                ],
                'medium': [
                    'infrastructure', 'deployment', 'configuration', 'setup'
                ]
            }
        }
        
        # Score each role
        role_scores = {}
        for role, patterns in role_patterns.items():
            score = 0
            # Strong patterns = 3 points
            for pattern in patterns.get('strong', []):
                if pattern.lower() in all_text:
                    score += 3
                    break  # Count once per role
            # Medium patterns = 1 point
            for pattern in patterns.get('medium', []):
                if pattern.lower() in all_text:
                    score += 1
                    break  # Count once per role
            role_scores[role] = score
        
        # Special rules based on directory structure
        if 'testing' in directory_lower or 'test' in directory_lower:
            role_scores['QA / Tester'] = role_scores.get('QA / Tester', 0) + 2
        if 'planning' in directory_lower or 'project' in directory_lower:
            role_scores['Project Manager'] = role_scores.get('Project Manager', 0) + 2
            role_scores['Business Analyst'] = role_scores.get('Business Analyst', 0) + 1
        if 'tracking' in directory_lower or 'status' in directory_lower:
            role_scores['Project Manager'] = role_scores.get('Project Manager', 0) + 2
        
        # Get roles with score >= 2 (at least medium match)
        roles = [role for role, score in role_scores.items() if score >= 2]
        
        # If no roles found, add default based on context
        if not roles:
            if 'test' in filename_lower or 'testing' in directory_lower:
                roles = ['QA / Tester']
            elif 'project' in filename_lower or 'status' in filename_lower:
                roles = ['Project Manager']
            elif 'development' in filename_lower or 'dev' in filename_lower:
                roles = ['Developer']
            else:
                roles = ['General']
        
        return roles
    
    def _get_available_roles(self, files):
        """Get list of all available roles from files."""
        roles_set = set()
        for file_info in files:
            roles = file_info.get('roles', [])
            if isinstance(roles, list):
                roles_set.update(roles)
            elif isinstance(roles, str):
                roles_set.add(roles)
        # Remove 'General' if there are other roles, and ensure sorted
        roles_list = sorted([r for r in roles_set if r != 'General'] or ['General'])
        return roles_list
    
    def _classify_by_topics(self, files):
        """Classify files by topics/categories based on الفهرس_المحتوى.md structure."""
        # Topics based on الفهرس_المحتوى.md
        topics = {
            'Core Documentation': {
                'description': 'التوثيق الأساسي - Core documentation and overview files',
                'icon': '📋',
                'files': []
            },
            'Testing Documentation': {
                'description': 'التوثيق الخاص بالاختبار - Testing guides, checklists, and test documentation',
                'icon': '🧪',
                'files': []
            },
            'Tracking & Monitoring': {
                'description': 'التوثيق الخاص بالتتبع والمراقبة - Tracking, logging, and audit documentation',
                'icon': '📊',
                'files': []
            },
            'Design & Specifications': {
                'description': 'التصميم والمواصفات - Design documents and UI/UX plans',
                'icon': '📖',
                'files': []
            },
            'Development & Deployment': {
                'description': 'التطوير والنشر - Development guides and deployment documentation',
                'icon': '🚀',
                'files': []
            },
            'Planning & Projects': {
                'description': 'التخطيط والمشاريع - Project planning, user stories, and technical architecture',
                'icon': '📝',
                'files': []
            },
            'Commands & Libraries': {
                'description': 'الأوامر والمكتبات - Command library and command-related documentation',
                'icon': '🔧',
                'files': []
            },
            'Status & Reports': {
                'description': 'الحالة والتقارير - Status reports and project tracking',
                'icon': '📈',
                'files': []
            }
        }
        
        # Map directory names and file patterns to topics based on الفهرس_المحتوى.md
        topic_mapping = {
            # Core Documentation
            'core': 'Core Documentation',
            'general': 'Core Documentation',
            '': 'Core Documentation',  # Root level files
            
            # Testing
            'testing': 'Testing Documentation',
            'test': 'Testing Documentation',
            
            # Tracking & Monitoring
            'tracking': 'Tracking & Monitoring',
            'monitoring': 'Tracking & Monitoring',
            
            # Design & Specifications
            'design': 'Design & Specifications',
            'specifications': 'Design & Specifications',
            'specs': 'Design & Specifications',
            
            # Development & Deployment
            'deployment': 'Development & Deployment',
            'how_to_develop': 'Development & Deployment',
            'how-to-develop': 'Development & Deployment',
            'development': 'Development & Deployment',
            
            # Planning & Projects
            'project_planning': 'Planning & Projects',
            'project-planning': 'Planning & Projects',
            'planning': 'Planning & Projects',
            'implementation_plan': 'Planning & Projects',
            'implementation-plan': 'Planning & Projects',
            'implementation': 'Planning & Projects',
            
            # Commands & Libraries
            'commands': 'Commands & Libraries',
            'command': 'Commands & Libraries',
            
            # Status & Reports
            'status': 'Status & Reports',
            'reports': 'Status & Reports',
            'report': 'Status & Reports'
        }
        
        # File name patterns that indicate specific topics
        file_patterns = {
            'Core Documentation': [
                'project_status', 'release_notes', 'completion_summary', 'start_testing',
                'project_management_user_guide', 'walkthrough', 'admin_user_management',
                'analysis_hishamos', 'hishamos_complete_design', 'hishamos_index',
                'final_summary', 'hishamos_critical_gaps', 'hishamos_missing_features'
            ],
            'Testing Documentation': [
                'quick_start_testing', 'test_execution', 'uat_testing', 'user_journey',
                'admin_ui_manual_testing', 'system_settings_ui', 'usage_analytics_ui',
                'phase_', 'command_testing', 'testing'
            ],
            'Tracking & Monitoring': [
                'tracking_logging_audit', 'websocket', 'permissions_', 'refresh_token',
                'admin_ui_', 'django_admin', 'user_facing', 'frontend_comprehensive',
                'dropdown_actions', 'edit_form', 'story_', 'requirements_',
                'phase_status', 'immediate_next', 'project_roadmap', 'blockers',
                'command_library_progress', 'workflow_improvements', 'command_endpoints_test',
                'api_documentation_fix'
            ],
            'Design & Specifications': [
                'ui_redesign', 'hishamos_admin_management', 'hishamos_ai_project',
                'hishamos_complete_prompts', 'reference_prompts'
            ],
            'Development & Deployment': [
                'master_development', 'documentation_maintenance', 'verification_checklist',
                'production_deployment', 'deployment_infrastructure', 'api_documentation_fixes'
            ],
            'Planning & Projects': [
                'ba_artifacts', 'user_stories', 'technical_architecture', 'project_plan',
                'implementation_specs', 'full_technical_reference', 'master_development_plan',
                'implementation_plan', 'phase_6_implementation', 'phase_11_12_implementation',
                'phase_13_14_implementation', 'phase_15_16_implementation', 'phase_17_18_implementation',
                'phase_3_completion', 'phase_4_completion', 'phase_5_', 'phase_6_',
                'phase_9', 'phase_10', 'restructuring_summary'
            ],
            'Commands & Libraries': [
                'command_library', 'command_testing'
            ],
            'Status & Reports': [
                'task_tracker', 'hishamos_index', 'tasks', 'future_phases', 'hishamos_ba_agent'
            ]
        }
        
        for file_info in files:
            directory = file_info.get('directory', '').lower()
            path = file_info.get('path', '').lower()
            filename = file_info.get('name', '').lower()
            
            # Determine topic based on directory, path, or filename
            topic = 'Core Documentation'  # Default
            
            # First, check directory
            if directory:
                dir_name = directory.split('/')[0]  # Get first directory
                topic = topic_mapping.get(dir_name, topic)
            elif '/' in path:
                # Check path for topic indicators
                path_parts = path.split('/')
                if len(path_parts) > 1:
                    first_dir = path_parts[0]
                    topic = topic_mapping.get(first_dir, topic)
            
            # Then, check filename patterns for more specific classification
            for topic_name, patterns in file_patterns.items():
                for pattern in patterns:
                    if pattern in filename or pattern in path:
                        topic = topic_name
                        break
                if topic != 'Core Documentation':
                    break
            
            # Add file to appropriate topic
            if topic in topics:
                topics[topic]['files'].append(file_info)
            else:
                topics['Core Documentation']['files'].append(file_info)
        
        # Remove empty topics
        topics = {k: v for k, v in topics.items() if v['files']}
        
        # Sort files within each topic by name
        for topic in topics:
            topics[topic]['files'].sort(key=lambda x: x['name'])
        
        return topics
    
    @action(detail=False, methods=['get'], url_path='get_file')
    def get_file(self, request):
        """
        Get content of a specific markdown file.
        
        Query params:
        - path: Relative path to the markdown file (e.g., 'testing/QUICK_START_TESTING_GUIDE.md')
        - output_format: 'raw' for raw markdown, 'html' for rendered HTML (default)
        """
        file_path = request.query_params.get('path')
        format_type = request.query_params.get('output_format', 'html')  # Changed from 'format' to 'output_format'
        
        if not file_path:
            return Response({
                'error': 'path parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            docs_path = self.get_docs_path()
            
            # Security: Prevent directory traversal
            if '..' in file_path or file_path.startswith('/'):
                return Response({
                    'error': 'Invalid file path'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Normalize path
            file_path = file_path.replace('/', os.sep)
            full_path = docs_path / file_path
            
            # Ensure file is within docs directory
            try:
                full_path.resolve().relative_to(docs_path.resolve())
            except ValueError:
                return Response({
                    'error': 'File path outside documentation directory'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not full_path.exists():
                return Response({
                    'error': 'File not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if not full_path.is_file():
                return Response({
                    'error': 'Path is not a file'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Read file content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML frontmatter if present
            yaml_metadata, content_body = self._parse_yaml_frontmatter(content)
            
            # Get file metadata
            stat = full_path.stat()
            
            response_data = {
                'path': file_path.replace(os.sep, '/'),
                'name': full_path.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'content': content if format_type == 'raw' else None,
                'html': None,
                'metadata': yaml_metadata  # Add parsed metadata
            }
            
            # Convert to HTML if requested
            if format_type == 'html':
                html_content = self._markdown_to_html(content, file_path)
                response_data['html'] = html_content
            
            return Response(response_data)
            
        except UnicodeDecodeError:
            return Response({
                'error': 'File encoding error'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error reading documentation file: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _parse_yaml_frontmatter(self, content: str):
        """Parse YAML frontmatter from markdown content."""
        if not YAML_AVAILABLE:
            return None, content
        
        # Check if content starts with YAML frontmatter
        frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
        match = frontmatter_pattern.match(content)
        
        if match:
            try:
                yaml_content = match.group(1)
                metadata = yaml.safe_load(yaml_content)
                # Remove frontmatter from content
                remaining_content = content[match.end():]
                return metadata if isinstance(metadata, dict) else None, remaining_content
            except Exception as e:
                logger.warning(f"Error parsing YAML frontmatter: {e}")
                return None, content
        
        return None, content
    
    def _markdown_to_html(self, markdown_content, file_path):
        """Convert markdown content to HTML."""
        try:
            # Parse and remove YAML frontmatter if present
            _, markdown_body = self._parse_yaml_frontmatter(markdown_content)
            
            # Configure markdown extensions
            extensions = [
                'extra',  # Includes tables, fenced_code, etc.
                'codehilite',  # Syntax highlighting
                'toc',  # Table of contents
            ]
            
            # Create markdown instance
            md = markdown.Markdown(extensions=extensions)
            
            # Convert to HTML
            html = md.convert(markdown_body)
            
            # Add table of contents if available
            if md.toc:
                html = f'<div class="table-of-contents">{md.toc}</div>\n{html}'
            
            return html
            
        except Exception as e:
            logger.error(f"Error converting markdown to HTML: {e}", exc_info=True)
            return f"<p>Error rendering markdown: {str(e)}</p>"
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search documentation files with advanced metadata support.
        
        Query params:
        - q: Search query
        - limit: Maximum number of results (default: 50)
        - role: Filter by role
        - phase: Filter by phase
        - category: Filter by category
        - tag: Filter by tag (can be used multiple times)
        """
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 50))
        filter_role = request.query_params.get('role', '').strip()
        filter_phase = request.query_params.get('phase', '').strip()
        filter_category = request.query_params.get('category', '').strip()
        filter_tags = request.query_params.getlist('tag')  # Multiple tag filters
        
        if not query:
            return Response({
                'error': 'q parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            docs_path = self.get_docs_path()
            
            if not docs_path.exists():
                return Response({
                    'error': 'Documentation directory not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            results = []
            query_lower = query.lower()
            query_terms = query_lower.split()  # Split into terms for better matching
            
            # Search through all markdown files
            for root, dirs, filenames in os.walk(docs_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for filename in filenames:
                    if filename.endswith('.md'):
                        file_path = os.path.join(root, filename)
                        rel_file_path = os.path.relpath(file_path, docs_path)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Parse metadata
                            yaml_metadata, content_body = self._parse_yaml_frontmatter(content)
                            
                            # Apply filters based on metadata
                            if filter_role and yaml_metadata:
                                target_audience = yaml_metadata.get('target_audience', {})
                                roles = []
                                if isinstance(target_audience, dict):
                                    if target_audience.get('primary'):
                                        roles.extend(target_audience['primary'] if isinstance(target_audience['primary'], list) else [target_audience['primary']])
                                    if target_audience.get('secondary'):
                                        roles.extend(target_audience['secondary'] if isinstance(target_audience['secondary'], list) else [target_audience['secondary']])
                                if filter_role not in [r.lower() for r in roles]:
                                    continue  # Skip if role filter doesn't match
                            
                            if filter_phase and yaml_metadata:
                                applicable_phases = yaml_metadata.get('applicable_phases', {})
                                phases = []
                                if isinstance(applicable_phases, dict):
                                    if applicable_phases.get('primary'):
                                        phases.extend(applicable_phases['primary'] if isinstance(applicable_phases['primary'], list) else [applicable_phases['primary']])
                                    if applicable_phases.get('secondary'):
                                        phases.extend(applicable_phases['secondary'] if isinstance(applicable_phases['secondary'], list) else [applicable_phases['secondary']])
                                if filter_phase not in [p.lower() for p in phases]:
                                    continue  # Skip if phase filter doesn't match
                            
                            if filter_category and yaml_metadata:
                                file_category = yaml_metadata.get('category', '').lower()
                                if filter_category.lower() not in file_category:
                                    continue  # Skip if category filter doesn't match
                            
                            if filter_tags:
                                file_tags = yaml_metadata.get('tags', []) if yaml_metadata else []
                                if isinstance(file_tags, str):
                                    file_tags = [file_tags]
                                file_tags_lower = [t.lower() for t in file_tags]
                                filter_tags_lower = [t.lower() for t in filter_tags]
                                if not any(t in file_tags_lower for t in filter_tags_lower):
                                    continue  # Skip if none of the tag filters match
                            
                            # Enhanced search: check filename, content, and metadata
                            matches_in_metadata = 0
                            search_text = f"{filename} {content_body}".lower()
                            
                            # Search in metadata fields
                            if yaml_metadata:
                                metadata_searchable = [
                                    yaml_metadata.get('title', ''),
                                    yaml_metadata.get('description', ''),
                                    ' '.join(yaml_metadata.get('tags', []) if isinstance(yaml_metadata.get('tags'), list) else []),
                                    ' '.join(yaml_metadata.get('keywords', []) if isinstance(yaml_metadata.get('keywords'), list) else []),
                                ]
                                metadata_text = ' '.join(metadata_searchable).lower()
                                search_text = f"{metadata_text} {search_text}"
                                
                                # Count matches in metadata
                                for term in query_terms:
                                    if term in metadata_text:
                                        matches_in_metadata += 1
                            
                            # Calculate match score (metadata matches weighted higher)
                            match_score = 0
                            content_matches = 0
                            for term in query_terms:
                                if term in filename.lower():
                                    match_score += 3  # Filename matches weighted highest
                                if term in content_body.lower():
                                    content_matches += 1
                                    match_score += 1
                            
                            match_score += matches_in_metadata * 2  # Metadata matches weighted higher
                            
                            # Only include if there's a match
                            if match_score > 0:
                                # Find matching lines in content
                                lines = content_body.split('\n')
                                matching_lines = []
                                for i, line in enumerate(lines[:100]):  # Limit to first 100 lines
                                    line_lower = line.lower()
                                    if any(term in line_lower for term in query_terms):
                                        matching_lines.append({
                                            'line_number': i + 1,
                                            'content': line.strip()[:200]  # First 200 chars
                                        })
                                
                                results.append({
                                    'path': rel_file_path.replace(os.sep, '/'),
                                    'name': filename,
                                    'matches': len(matching_lines) + matches_in_metadata,
                                    'match_score': match_score,  # Add score for sorting
                                    'snippets': matching_lines[:5],  # Top 5 matches
                                    'metadata': yaml_metadata  # Include metadata in results
                                })
                                
                                if len(results) >= limit:
                                    break
                                
                        except Exception as e:
                            logger.warning(f"Error reading file {file_path}: {e}")
                            continue
                
                if len(results) >= limit:
                    break
            
            # Sort results by match score (descending), then by matches
            results.sort(key=lambda x: (x.get('match_score', 0), x['matches']), reverse=True)
            
            # Limit results
            results = results[:limit]
            
            # Remove match_score from response (internal use only)
            for result in results:
                if 'match_score' in result:
                    del result['match_score']
            
            return Response({
                'query': query,
                'results': results,
                'total': len(results),
                'filters_applied': {
                    'role': filter_role if filter_role else None,
                    'phase': filter_phase if filter_phase else None,
                    'category': filter_category if filter_category else None,
                    'tags': filter_tags if filter_tags else None
                }
            })
            
        except Exception as e:
            logger.error(f"Error searching documentation: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Separate function-based views for explicit URL routing
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def documentation_list_files(request):
    """API view for listing documentation files."""
    viewset = DocumentationViewSet()
    viewset.request = request
    viewset.format_kwarg = None
    return viewset.list_files(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def documentation_get_file(request):
    """API view for getting a documentation file."""
    viewset = DocumentationViewSet()
    viewset.request = request
    viewset.format_kwarg = None
    return viewset.get_file(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def documentation_search(request):
    """API view for searching documentation."""
    viewset = DocumentationViewSet()
    viewset.request = request
    viewset.format_kwarg = None
    return viewset.search(request)

