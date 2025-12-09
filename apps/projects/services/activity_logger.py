"""
Activity logging service for tracking changes and events in the project management system.
"""

from django.contrib.contenttypes.models import ContentType
from apps.projects.models import Activity, Project
from typing import Optional, Dict, Any
import uuid


class ActivityLogger:
    """Service for logging activities in the project management system."""
    
    @staticmethod
    def log_activity(
        activity_type: str,
        user,
        description: str,
        project: Optional[Project] = None,
        content_object=None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Activity:
        """
        Log an activity.
        
        Args:
            activity_type: Type of activity (from Activity.ACTIVITY_TYPE_CHOICES)
            user: User who performed the activity (can be None for system activities)
            description: Human-readable description of the activity
            project: Project this activity belongs to (optional, will try to infer from content_object)
            content_object: The object this activity relates to (optional)
            metadata: Additional data about the activity (e.g., old_value, new_value, changed_fields)
        
        Returns:
            Activity instance
        """
        # Try to infer project from content_object if not provided
        if not project and content_object:
            if hasattr(content_object, 'project'):
                project = content_object.project
            elif hasattr(content_object, 'story') and hasattr(content_object.story, 'project'):
                project = content_object.story.project
            elif hasattr(content_object, 'task') and hasattr(content_object.task, 'story') and hasattr(content_object.task.story, 'project'):
                project = content_object.task.story.project
        
        # Get content type and object ID if content_object is provided
        content_type = None
        object_id = None
        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            object_id = content_object.id if hasattr(content_object, 'id') else None
        
        activity = Activity.objects.create(
            activity_type=activity_type,
            user=user,
            project=project,
            content_type=content_type,
            object_id=object_id,
            description=description,
            metadata=metadata or {}
        )
        
        return activity
    
    @staticmethod
    def log_story_created(story, user):
        """Log story creation."""
        return ActivityLogger.log_activity(
            activity_type='story_created',
            user=user,
            description=f'Created story: {story.title}',
            content_object=story,
            metadata={
                'story_id': str(story.id),
                'story_title': story.title,
                'status': story.status,
                'priority': story.priority,
            }
        )
    
    @staticmethod
    def log_story_updated(story, user, changed_fields: Optional[Dict[str, Any]] = None):
        """Log story update."""
        metadata = {
            'story_id': str(story.id),
            'story_title': story.title,
        }
        if changed_fields:
            metadata['changed_fields'] = changed_fields
        
        return ActivityLogger.log_activity(
            activity_type='story_updated',
            user=user,
            description=f'Updated story: {story.title}',
            content_object=story,
            metadata=metadata
        )
    
    @staticmethod
    def log_story_status_changed(story, user, old_status: str, new_status: str):
        """Log story status change."""
        return ActivityLogger.log_activity(
            activity_type='story_status_changed',
            user=user,
            description=f'Changed story status from {old_status} to {new_status}: {story.title}',
            content_object=story,
            metadata={
                'story_id': str(story.id),
                'story_title': story.title,
                'old_status': old_status,
                'new_status': new_status,
            }
        )
    
    @staticmethod
    def log_story_assigned(story, user, assignee):
        """Log story assignment."""
        return ActivityLogger.log_activity(
            activity_type='story_assigned',
            user=user,
            description=f'Assigned story "{story.title}" to {assignee.email}',
            content_object=story,
            metadata={
                'story_id': str(story.id),
                'story_title': story.title,
                'assignee_id': str(assignee.id),
                'assignee_email': assignee.email,
            }
        )
    
    @staticmethod
    def log_comment_added(comment, user):
        """Log comment addition."""
        return ActivityLogger.log_activity(
            activity_type='comment_added',
            user=user,
            description=f'Added comment on story: {comment.story.title}',
            content_object=comment,
            metadata={
                'comment_id': str(comment.id),
                'story_id': str(comment.story.id),
                'story_title': comment.story.title,
            }
        )
    
    @staticmethod
    def log_task_created(task, user):
        """Log task creation."""
        return ActivityLogger.log_activity(
            activity_type='task_created',
            user=user,
            description=f'Created task: {task.title}',
            content_object=task,
            metadata={
                'task_id': str(task.id),
                'task_title': task.title,
                'status': task.status,
            }
        )
    
    @staticmethod
    def log_bug_created(bug, user):
        """Log bug creation."""
        return ActivityLogger.log_activity(
            activity_type='bug_created',
            user=user,
            description=f'Created bug: {bug.title}',
            content_object=bug,
            metadata={
                'bug_id': str(bug.id),
                'bug_title': bug.title,
                'severity': bug.severity,
                'status': bug.status,
            }
        )
    
    @staticmethod
    def log_issue_created(issue, user):
        """Log issue creation."""
        return ActivityLogger.log_activity(
            activity_type='issue_created',
            user=user,
            description=f'Created issue: {issue.title}',
            content_object=issue,
            metadata={
                'issue_id': str(issue.id),
                'issue_title': issue.title,
                'issue_type': issue.issue_type,
                'status': issue.status,
            }
        )


# Convenience function for easy import
def log_activity(*args, **kwargs):
    """Convenience function to log an activity."""
    return ActivityLogger.log_activity(*args, **kwargs)

