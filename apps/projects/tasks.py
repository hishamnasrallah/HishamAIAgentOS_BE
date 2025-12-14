"""
Celery tasks for project generation and export operations.
"""

from celery import shared_task
from django.utils import timezone
import asyncio
import logging
from typing import Dict, Any

from apps.projects.models import GeneratedProject, RepositoryExport
from apps.projects.services.project_generator import ProjectGenerator, ProjectGenerationError
from apps.projects.services.repository_exporter import RepositoryExporter, RepositoryExportError
from apps.workflows.services.workflow_executor import WorkflowExecutor, WorkflowExecutionError

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_project_task(
    self,
    generated_project_id: str,
    workflow_id: str,
    input_data: Dict[str, Any],
    user_id: str
):
    """
    Async task to generate a project from a workflow.
    
    Args:
        generated_project_id: GeneratedProject UUID
        workflow_id: Workflow UUID
        input_data: Workflow input data
        user_id: User UUID
    """
    try:
        generated_project = GeneratedProject.objects.get(id=generated_project_id)
        generated_project.status = 'generating'
        generated_project.save(update_fields=['status'])
        
        # Execute workflow
        executor = WorkflowExecutor()
        execution_result = asyncio.run(
            executor.execute(
                workflow_id=workflow_id,
                input_data=input_data,
                user_id=user_id
            )
        )
        
        # Generate files from workflow output
        generator = ProjectGenerator(generated_project)
        asyncio.run(generator.generate_from_workflow_output(execution_result))
        
        # Update statistics
        generator._update_statistics()
        
        # Mark as completed
        generated_project.status = 'completed'
        generated_project.completed_at = timezone.now()
        generated_project.save(update_fields=['status', 'completed_at'])
        
        logger.info(f"Successfully generated project {generated_project_id}")
        return {'status': 'completed', 'generated_project_id': generated_project_id}
        
    except WorkflowExecutionError as e:
        logger.error(f"Workflow execution error for project {generated_project_id}: {e}")
        try:
            generated_project = GeneratedProject.objects.get(id=generated_project_id)
            generated_project.status = 'failed'
            generated_project.error_message = str(e)
            generated_project.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        raise
        
    except ProjectGenerationError as e:
        logger.error(f"Project generation error for project {generated_project_id}: {e}")
        try:
            generated_project = GeneratedProject.objects.get(id=generated_project_id)
            generated_project.status = 'failed'
            generated_project.error_message = str(e)
            generated_project.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error generating project {generated_project_id}: {e}", exc_info=True)
        try:
            generated_project = GeneratedProject.objects.get(id=generated_project_id)
            generated_project.status = 'failed'
            generated_project.error_message = f"Unexpected error: {str(e)}"
            generated_project.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        
        # Retry on transient errors
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        raise


@shared_task(bind=True, max_retries=3)
def export_repository_task(
    self,
    export_id: str,
    export_type: str,
    config: Dict[str, Any]
):
    """
    Async task to export a generated project to a repository.
    
    Args:
        export_id: RepositoryExport UUID
        export_type: Export type (zip, tar, tar.gz, github, gitlab)
        config: Export configuration
    """
    try:
        export = RepositoryExport.objects.get(id=export_id)
        export.status = 'exporting'
        export.save(update_fields=['status'])
        
        exporter = RepositoryExporter(export.generated_project)
        
        if export_type == 'zip':
            archive_path = exporter.export_as_zip()
            export.archive_path = str(archive_path)
            export.archive_size = archive_path.stat().st_size
            
        elif export_type in ('tar', 'tar.gz'):
            gzip = export_type == 'tar.gz'
            archive_path = exporter.export_as_tar(gzip=gzip)
            export.archive_path = str(archive_path)
            export.archive_size = archive_path.stat().st_size
            
        elif export_type == 'github':
            github_token = config.get('github_token')
            if not github_token:
                raise RepositoryExportError('github_token is required')
            
            repo_info = asyncio.run(
                exporter.export_to_github(
                    github_token=github_token,
                    repository_name=config.get('repository_name', ''),
                    organization=config.get('organization'),
                    private=config.get('private', False)
                )
            )
            export.repository_url = repo_info.get('repository_url', '')
            
        elif export_type == 'gitlab':
            gitlab_token = config.get('gitlab_token')
            if not gitlab_token:
                raise RepositoryExportError('gitlab_token is required')
            
            repo_info = asyncio.run(
                exporter.export_to_gitlab(
                    gitlab_token=gitlab_token,
                    project_name=config.get('project_name', ''),
                    namespace=config.get('namespace'),
                    visibility=config.get('visibility', 'private')
                )
            )
            export.repository_url = repo_info.get('repository_url', '')
        else:
            raise RepositoryExportError(f'Unsupported export type: {export_type}')
        
        export.status = 'completed'
        export.completed_at = timezone.now()
        export.save(update_fields=['status', 'completed_at', 'archive_path', 'archive_size', 'repository_url'])
        
        logger.info(f"Successfully exported {export_type} for export {export_id}")
        return {'status': 'completed', 'export_id': export_id}
        
    except RepositoryExportError as e:
        logger.error(f"Export error for export {export_id}: {e}")
        try:
            export = RepositoryExport.objects.get(id=export_id)
            export.status = 'failed'
            export.error_message = str(e)
            export.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error exporting {export_id}: {e}", exc_info=True)
        try:
            export = RepositoryExport.objects.get(id=export_id)
            export.status = 'failed'
            export.error_message = f"Unexpected error: {str(e)}"
            export.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        
        # Retry on transient errors
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        raise
