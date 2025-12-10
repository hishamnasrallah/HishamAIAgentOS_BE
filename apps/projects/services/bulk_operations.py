"""
Bulk operations service for stories, tasks, bugs, and issues.
Supports bulk updates, deletions, and status changes.
"""

from django.db import transaction
from django.db.models import Q
from typing import List, Dict, Any, Optional
from apps.projects.models import UserStory, Task, Bug, Issue
from apps.authentication.models import User


class BulkOperationsService:
    """Service for performing bulk operations on work items."""
    
    @staticmethod
    @transaction.atomic
    def bulk_update_status(items: List[Dict[str, Any]], new_status: str, user: User):
        """Bulk update status for multiple items."""
        updated_count = 0
        errors = []
        
        for item in items:
            item_type = item.get('type')  # 'story', 'task', 'bug', 'issue'
            item_id = item.get('id')
            
            try:
                if item_type == 'story':
                    obj = UserStory.objects.get(id=item_id)
                elif item_type == 'task':
                    obj = Task.objects.get(id=item_id)
                elif item_type == 'bug':
                    obj = Bug.objects.get(id=item_id)
                elif item_type == 'issue':
                    obj = Issue.objects.get(id=item_id)
                else:
                    errors.append(f"Unknown item type: {item_type}")
                    continue
                
                obj.status = new_status
                obj.updated_by = user
                obj.save(update_fields=['status', 'updated_at', 'updated_by'])
                updated_count += 1
                
            except Exception as e:
                errors.append(f"Failed to update {item_type} {item_id}: {str(e)}")
        
        return {
            'updated_count': updated_count,
            'errors': errors,
        }
    
    @staticmethod
    @transaction.atomic
    def bulk_assign(items: List[Dict[str, Any]], assignee_id: str, user: User):
        """Bulk assign items to a user."""
        updated_count = 0
        errors = []
        
        try:
            assignee = User.objects.get(id=assignee_id)
        except User.DoesNotExist:
            return {
                'updated_count': 0,
                'errors': ['Assignee not found'],
            }
        
        for item in items:
            item_type = item.get('type')
            item_id = item.get('id')
            
            try:
                if item_type == 'story':
                    obj = UserStory.objects.get(id=item_id)
                elif item_type == 'task':
                    obj = Task.objects.get(id=item_id)
                elif item_type == 'bug':
                    obj = Bug.objects.get(id=item_id)
                elif item_type == 'issue':
                    obj = Issue.objects.get(id=item_id)
                else:
                    errors.append(f"Unknown item type: {item_type}")
                    continue
                
                obj.assigned_to = assignee
                obj.updated_by = user
                obj.save(update_fields=['assigned_to', 'updated_at', 'updated_by'])
                updated_count += 1
                
            except Exception as e:
                errors.append(f"Failed to assign {item_type} {item_id}: {str(e)}")
        
        return {
            'updated_count': updated_count,
            'errors': errors,
        }
    
    @staticmethod
    @transaction.atomic
    def bulk_add_labels(items: List[Dict[str, Any]], labels: List[str], user: User):
        """Bulk add labels to items."""
        updated_count = 0
        errors = []
        
        for item in items:
            item_type = item.get('type')
            item_id = item.get('id')
            
            try:
                if item_type == 'story':
                    obj = UserStory.objects.get(id=item_id)
                elif item_type == 'task':
                    obj = Task.objects.get(id=item_id)
                elif item_type == 'bug':
                    obj = Bug.objects.get(id=item_id)
                elif item_type == 'issue':
                    obj = Issue.objects.get(id=item_id)
                else:
                    errors.append(f"Unknown item type: {item_type}")
                    continue
                
                # Merge labels
                current_labels = obj.labels if isinstance(obj.labels, list) else []
                new_labels = list(set(current_labels + labels))
                obj.labels = new_labels
                obj.updated_by = user
                obj.save(update_fields=['labels', 'updated_at', 'updated_by'])
                updated_count += 1
                
            except Exception as e:
                errors.append(f"Failed to update labels for {item_type} {item_id}: {str(e)}")
        
        return {
            'updated_count': updated_count,
            'errors': errors,
        }
    
    @staticmethod
    @transaction.atomic
    def bulk_delete(items: List[Dict[str, Any]], user: User):
        """Bulk delete items."""
        deleted_count = 0
        errors = []
        
        for item in items:
            item_type = item.get('type')
            item_id = item.get('id')
            
            try:
                if item_type == 'story':
                    obj = UserStory.objects.get(id=item_id)
                elif item_type == 'task':
                    obj = Task.objects.get(id=item_id)
                elif item_type == 'bug':
                    obj = Bug.objects.get(id=item_id)
                elif item_type == 'issue':
                    obj = Issue.objects.get(id=item_id)
                else:
                    errors.append(f"Unknown item type: {item_type}")
                    continue
                
                obj.delete()
                deleted_count += 1
                
            except Exception as e:
                errors.append(f"Failed to delete {item_type} {item_id}: {str(e)}")
        
        return {
            'deleted_count': deleted_count,
            'errors': errors,
        }
    
    @staticmethod
    @transaction.atomic
    def bulk_move_to_sprint(items: List[Dict[str, Any]], sprint_id: str, user: User):
        """Bulk move items to a sprint."""
        updated_count = 0
        errors = []
        
        from apps.projects.models import Sprint
        try:
            sprint = Sprint.objects.get(id=sprint_id)
        except Sprint.DoesNotExist:
            return {
                'updated_count': 0,
                'errors': ['Sprint not found'],
            }
        
        for item in items:
            item_type = item.get('type')
            item_id = item.get('id')
            
            try:
                if item_type == 'story':
                    obj = UserStory.objects.get(id=item_id)
                    obj.sprint = sprint
                    obj.updated_by = user
                    obj.save(update_fields=['sprint', 'updated_at', 'updated_by'])
                    updated_count += 1
                else:
                    errors.append(f"Cannot move {item_type} to sprint (only stories supported)")
                
            except Exception as e:
                errors.append(f"Failed to move {item_type} {item_id}: {str(e)}")
        
        return {
            'updated_count': updated_count,
            'errors': errors,
        }

