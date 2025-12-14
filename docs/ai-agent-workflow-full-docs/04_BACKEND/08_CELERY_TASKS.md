# Backend Celery Tasks - Background Processing

**Document Type:** Celery Tasks Implementation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 03_SERVICES_IMPLEMENTATION.md, 07_SIGNALS_IMPLEMENTATION.md  
**File Size:** 495 lines

---

## 📋 Purpose

This document specifies the Celery background tasks for the AI agent workflow enhancement, including task definitions, error handling, and retry logic.

---

## 🔧 Task Definitions

### Task 1: start_project_generation

**Purpose:** Start project generation asynchronously

**Location:** `backend/apps/projects/tasks.py`

**Implementation:**

```python
from celery import shared_task
from django.utils import timezone
from .models import GeneratedProject, Project
from .services.project_generator import ProjectGenerator
from apps.workflows.services.workflow_executor import WorkflowExecutor

@shared_task(bind=True, max_retries=3)
def start_project_generation(
    self,
    project_id: str,
    workflow_id: str,
    input_data: dict,
    user_id: str
):
    """
    Start project generation workflow.
    
    Args:
        project_id: Project UUID
        workflow_id: Workflow UUID
        input_data: Workflow input data
        user_id: User UUID who triggered generation
    """
    try:
        # Get project
        project = Project.objects.get(id=project_id)
        
        # Create GeneratedProject
        generated_project = GeneratedProject.objects.create(
            project=project,
            status='generating',
            output_directory=f"generated-projects/{project_id}",
            created_by_id=user_id
        )
        
        # Execute workflow
        executor = WorkflowExecutor()
        result = executor.execute(
            workflow_id=workflow_id,
            input_data={
                **input_data,
                'project_id': project_id,
                'generated_project_id': str(generated_project.id)
            },
            user_id=user_id
        )
        
        # Update status
        GeneratedProject.objects.filter(id=generated_project.id).update(
            status='completed',
            completed_at=timezone.now()
        )
        
        return {
            'generated_project_id': str(generated_project.id),
            'status': 'completed'
        }
        
    except Exception as exc:
        # Update status to failed
        if 'generated_project' in locals():
            GeneratedProject.objects.filter(id=generated_project.id).update(
                status='failed',
                error_message=str(exc)
            )
        
        # Retry if applicable
        raise self.retry(exc=exc, countdown=60)
```

---

### Task 2: execute_repository_export

**Purpose:** Execute repository export asynchronously

**Location:** `backend/apps/projects/tasks.py`

**Implementation:**

```python
@shared_task(bind=True, max_retries=3)
def execute_repository_export(
    self,
    export_id: str,
    user_id: str
):
    """
    Execute repository export.
    
    Args:
        export_id: RepositoryExport UUID
        user_id: User UUID
    """
    from .models import RepositoryExport
    from .services.repository_exporter import RepositoryExporter
    
    try:
        export = RepositoryExport.objects.get(id=export_id)
        
        # Update status
        RepositoryExport.objects.filter(id=export_id).update(
            status='exporting'
        )
        
        # Get generated project
        generated_project = export.generated_project
        
        # Create exporter
        exporter = RepositoryExporter(str(generated_project.id))
        
        # Execute export based on type
        if export.export_type in ['zip', 'tar', 'tar.gz']:
            archive_path = exporter.export_as_zip() if export.export_type == 'zip' else exporter.export_as_tar()
            
            RepositoryExport.objects.filter(id=export_id).update(
                status='completed',
                archive_path=str(archive_path),
                archive_size=archive_path.stat().st_size,
                completed_at=timezone.now()
            )
        
        elif export.export_type == 'github':
            result = exporter.export_to_github(
                github_token=export.config.get('github_token'),
                repository_name=export.repository_name,
                organization=export.config.get('organization'),
                private=export.config.get('private', False)
            )
            
            RepositoryExport.objects.filter(id=export_id).update(
                status='completed',
                repository_url=result['repository_url'],
                completed_at=timezone.now()
            )
        
        elif export.export_type == 'gitlab':
            result = exporter.export_to_gitlab(
                gitlab_token=export.config.get('gitlab_token'),
                project_name=export.repository_name,
                namespace=export.config.get('namespace'),
                visibility=export.config.get('visibility', 'private')
            )
            
            RepositoryExport.objects.filter(id=export_id).update(
                status='completed',
                repository_url=result['repository_url'],
                completed_at=timezone.now()
            )
        
        return {
            'export_id': export_id,
            'status': 'completed'
        }
        
    except Exception as exc:
        # Update status to failed
        RepositoryExport.objects.filter(id=export_id).update(
            status='failed',
            error_message=str(exc)
        )
        
        # Retry if applicable
        raise self.retry(exc=exc, countdown=60)
```

---

### Task 3: cleanup_old_generated_projects

**Purpose:** Cleanup old generated projects based on retention policy

**Location:** `backend/apps/projects/tasks.py`

**Implementation:**

```python
from datetime import timedelta
from django.utils import timezone

@shared_task
def cleanup_old_generated_projects():
    """
    Cleanup old generated projects based on retention policy.
    Runs daily via Celery Beat.
    """
    from .models import GeneratedProject
    from django.conf import settings
    import shutil
    
    # Default retention: 30 days
    retention_days = getattr(settings, 'GENERATED_PROJECTS_RETENTION_DAYS', 30)
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    
    # Find projects to cleanup
    projects_to_cleanup = GeneratedProject.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['completed', 'failed']
    ).exclude(status='archived')
    
    for generated_project in projects_to_cleanup:
        try:
            # Delete files from filesystem
            output_dir = Path(generated_project.output_directory)
            if output_dir.exists():
                shutil.rmtree(output_dir)
            
            # Archive project (don't delete, just mark as archived)
            GeneratedProject.objects.filter(id=generated_project.id).update(
                status='archived'
            )
        except Exception as e:
            # Log error but continue
            logger.error(f"Error cleaning up project {generated_project.id}: {e}")
```

---

## ⏰ Scheduled Tasks (Celery Beat)

### Task Schedule

**Location:** `backend/core/celery.py`

**Configuration:**

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'cleanup-old-generated-projects': {
        'task': 'apps.projects.tasks.cleanup_old_generated_projects',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

---

## 🔄 Task Retry Logic

### Retry Configuration

**Default Settings:**
- `max_retries`: 3
- `countdown`: 60 seconds (exponential backoff)
- `retry_backoff`: True
- `retry_backoff_max`: 600 seconds

**Per-Task Override:**
```python
@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def custom_task(self):
    ...
```

---

## 📊 Task Monitoring

### Task State Tracking

**States:**
- `PENDING` - Task waiting to be processed
- `STARTED` - Task is executing
- `SUCCESS` - Task completed successfully
- `FAILURE` - Task failed
- `RETRY` - Task is being retried

**Storage:**
- Celery Result Backend (Redis)
- Task metadata stored
- Results available for querying

---

## 🔗 Related Documentation

- **Services:** `03_SERVICES_IMPLEMENTATION.md`
- **Signals:** `07_SIGNALS_IMPLEMENTATION.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

