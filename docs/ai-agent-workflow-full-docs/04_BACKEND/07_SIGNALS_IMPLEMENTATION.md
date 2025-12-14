# Backend Signals Implementation - Django Signals

**Document Type:** Signals Implementation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** 02_MODELS_IMPLEMENTATION.md, 08_CELERY_TASKS.md  
**File Size:** 489 lines

---

## 📋 Purpose

This document specifies the Django signals for the AI agent workflow enhancement, including signal handlers for model lifecycle events.

---

## 🔔 Signal Handlers

### Signal 1: GeneratedProject Status Change

**Purpose:** Trigger actions when GeneratedProject status changes

**Location:** `backend/apps/projects/signals.py`

**Implementation:**

```python
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import GeneratedProject

@receiver(pre_save, sender=GeneratedProject)
def generated_project_pre_save(sender, instance, **kwargs):
    """Handle GeneratedProject pre-save."""
    if instance.pk:
        # Get old instance
        try:
            old_instance = GeneratedProject.objects.get(pk=instance.pk)
            old_status = old_instance.status
            new_status = instance.status
            
            # Status changed
            if old_status != new_status:
                # Validate state transition
                valid_transitions = {
                    'pending': ['generating'],
                    'generating': ['completed', 'failed'],
                    'completed': ['archived'],
                    'failed': [],
                    'archived': [],
                }
                
                if new_status not in valid_transitions.get(old_status, []):
                    raise ValueError(
                        f"Invalid state transition from {old_status} to {new_status}"
                    )

@receiver(post_save, sender=GeneratedProject)
def generated_project_post_save(sender, instance, created, **kwargs):
    """Handle GeneratedProject post-save."""
    if created:
        # New generated project created
        # Send notification
        from apps.projects.services.notifications import NotificationService
        notification_service = NotificationService(project=instance.project)
        notification_service.send_generation_started(instance)
    
    # Status changed
    if not created and 'status' in kwargs.get('update_fields', []):
        if instance.status == 'completed':
            # Generation completed
            from apps.projects.services.notifications import NotificationService
            notification_service = NotificationService(project=instance.project)
            notification_service.send_generation_completed(instance)
        
        elif instance.status == 'failed':
            # Generation failed
            from apps.projects.services.notifications import NotificationService
            notification_service = NotificationService(project=instance.project)
            notification_service.send_generation_failed(instance)
```

---

### Signal 2: ProjectFile Creation

**Purpose:** Update GeneratedProject statistics when files are created

**Location:** `backend/apps/projects/signals.py`

**Implementation:**

```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, Count
from .models import ProjectFile, GeneratedProject

@receiver(post_save, sender=ProjectFile)
def project_file_post_save(sender, instance, created, **kwargs):
    """Update GeneratedProject statistics when file is created."""
    if created:
        # Update statistics
        generated_project = instance.generated_project
        GeneratedProject.objects.filter(id=generated_project.id).update(
            total_files=ProjectFile.objects.filter(
                generated_project=generated_project
            ).count(),
            total_size=ProjectFile.objects.filter(
                generated_project=generated_project
            ).aggregate(total=Sum('file_size'))['total'] or 0
        )

@receiver(post_delete, sender=ProjectFile)
def project_file_post_delete(sender, instance, **kwargs):
    """Update GeneratedProject statistics when file is deleted."""
    generated_project = instance.generated_project
    GeneratedProject.objects.filter(id=generated_project.id).update(
        total_files=ProjectFile.objects.filter(
            generated_project=generated_project
        ).count(),
        total_size=ProjectFile.objects.filter(
            generated_project=generated_project
        ).aggregate(total=Sum('file_size'))['total'] or 0
    )
```

---

### Signal 3: RepositoryExport Status Change

**Purpose:** Handle export status changes

**Location:** `backend/apps/projects/signals.py`

**Implementation:**

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RepositoryExport

@receiver(post_save, sender=RepositoryExport)
def repository_export_post_save(sender, instance, created, **kwargs):
    """Handle RepositoryExport status changes."""
    if not created and 'status' in kwargs.get('update_fields', []):
        if instance.status == 'completed':
            # Export completed
            from apps.projects.services.notifications import NotificationService
            notification_service = NotificationService(
                project=instance.generated_project.project
            )
            notification_service.send_export_completed(instance)
        
        elif instance.status == 'failed':
            # Export failed
            from apps.projects.services.notifications import NotificationService
            notification_service = NotificationService(
                project=instance.generated_project.project
            )
            notification_service.send_export_failed(instance)
```

---

## 🔄 Signal Registration

### App Configuration

**Location:** `backend/apps/projects/apps.py`

**Implementation:**

```python
from django.apps import AppConfig

class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.projects'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.projects.signals
```

---

## 📊 Signal Performance

### Optimization Strategies

1. **Use `update_fields`:** Only process when relevant fields change
2. **Async Processing:** Move heavy operations to Celery
3. **Bulk Operations:** Batch updates for multiple files
4. **Transaction Handling:** Use `transaction.on_commit()` for DB operations

---

## 🔗 Related Documentation

- **Models:** `02_MODELS_IMPLEMENTATION.md`
- **Celery Tasks:** `08_CELERY_TASKS.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

