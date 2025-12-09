"""
Edit history service for tracking and diffing object changes.
"""

from django.contrib.contenttypes.models import ContentType
from apps.projects.models import EditHistory, Project
from typing import Optional, Dict, Any, List
import difflib
import json


class EditHistoryService:
    """Service for managing edit history and calculating diffs."""
    
    @staticmethod
    def calculate_text_diff(old_text: str, new_text: str) -> Dict[str, Any]:
        """
        Calculate diff between two text strings.
        
        Returns:
            dict with keys: 'unified_diff', 'added_lines', 'removed_lines', 'context'
        """
        if old_text == new_text:
            return {
                'unified_diff': '',
                'added_lines': [],
                'removed_lines': [],
                'context': []
            }
        
        old_lines = old_text.splitlines(keepends=True) if old_text else []
        new_lines = new_text.splitlines(keepends=True) if new_text else []
        
        # Calculate unified diff
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
            n=3  # Context lines
        ))
        unified_diff = ''.join(diff)
        
        # Calculate added/removed lines
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
        added_lines = []
        removed_lines = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                added_lines.extend([(j, line) for j, line in enumerate(new_lines[j1:j2], start=j1)])
            elif tag == 'delete':
                removed_lines.extend([(i, line) for i, line in enumerate(old_lines[i1:i2], start=i1)])
            elif tag == 'replace':
                removed_lines.extend([(i, line) for i, line in enumerate(old_lines[i1:i2], start=i1)])
                added_lines.extend([(j, line) for j, line in enumerate(new_lines[j1:j2], start=j1)])
        
        return {
            'unified_diff': unified_diff,
            'added_lines': added_lines,
            'removed_lines': removed_lines,
            'context': matcher.get_opcodes()
        }
    
    @staticmethod
    def serialize_value(value: Any) -> Any:
        """
        Serialize a value for storage in JSON.
        Handles dates, UUIDs, and other special types.
        """
        if value is None:
            return None
        
        # Handle UUID
        if hasattr(value, 'hex'):  # UUID
            return str(value)
        
        # Handle date/datetime
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        
        # Handle model instances
        if hasattr(value, 'id'):
            return str(value.id)
        
        # Handle lists/dicts
        if isinstance(value, (list, dict)):
            return json.loads(json.dumps(value, default=str))
        
        return value
    
    @staticmethod
    def get_object_snapshot(obj, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get a snapshot of an object's field values.
        
        Args:
            obj: The model instance
            fields: Optional list of field names to include (if None, includes all fields)
        
        Returns:
            dict mapping field_name -> value
        """
        snapshot = {}
        
        if fields is None:
            # Get all field names from the model
            fields = [f.name for f in obj._meta.get_fields() if not f.many_to_many and not f.one_to_many]
        
        for field_name in fields:
            if hasattr(obj, field_name):
                try:
                    value = getattr(obj, field_name)
                    snapshot[field_name] = EditHistoryService.serialize_value(value)
                except Exception:
                    # Skip fields that can't be accessed
                    pass
        
        return snapshot
    
    @staticmethod
    def calculate_diffs(old_values: Dict[str, Any], new_values: Dict[str, Any], text_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Calculate diffs for all changed fields.
        
        Args:
            old_values: Dictionary of old field values
            new_values: Dictionary of new field values
            text_fields: List of field names that should be diffed as text
        
        Returns:
            dict mapping field_name -> diff_data
        """
        if text_fields is None:
            # Common text fields
            text_fields = ['description', 'title', 'name', 'content', 'acceptance_criteria', 'reproduction_steps', 'expected_behavior', 'actual_behavior']
        
        diffs = {}
        changed_fields = []
        
        # Find all changed fields
        all_fields = set(old_values.keys()) | set(new_values.keys())
        
        for field_name in all_fields:
            old_value = old_values.get(field_name)
            new_value = new_values.get(field_name)
            
            # Skip if values are the same
            if old_value == new_value:
                continue
            
            changed_fields.append(field_name)
            
            # Calculate diff for text fields
            if field_name in text_fields:
                old_text = str(old_value) if old_value is not None else ''
                new_text = str(new_value) if new_value is not None else ''
                diffs[field_name] = EditHistoryService.calculate_text_diff(old_text, new_text)
            else:
                # For non-text fields, just store the change
                diffs[field_name] = {
                    'old_value': old_value,
                    'new_value': new_value,
                }
        
        return diffs
    
    @staticmethod
    def create_edit_history(
        obj,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        user,
        comment: Optional[str] = None,
        project: Optional[Project] = None
    ) -> EditHistory:
        """
        Create an edit history record for an object.
        
        Args:
            obj: The model instance that was edited
            old_values: Dictionary of old field values
            new_values: Dictionary of new field values
            user: User who made the edit
            comment: Optional comment about the edit
            project: Optional project (will try to infer from obj)
        
        Returns:
            EditHistory instance
        """
        # Try to infer project from obj if not provided
        if not project and obj:
            if hasattr(obj, 'project'):
                project = obj.project
            elif hasattr(obj, 'story') and hasattr(obj.story, 'project'):
                project = obj.story.project
            elif hasattr(obj, 'task') and hasattr(obj.task, 'story') and hasattr(obj.task.story, 'project'):
                project = obj.task.story.project
        
        # Get content type
        content_type = ContentType.objects.get_for_model(obj)
        object_id = obj.id if hasattr(obj, 'id') else None
        
        # Get current version number
        latest_version = EditHistory.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).order_by('-version').first()
        
        next_version = (latest_version.version + 1) if latest_version else 1
        
        # Calculate changed fields
        changed_fields = []
        all_fields = set(old_values.keys()) | set(new_values.keys())
        for field_name in all_fields:
            if old_values.get(field_name) != new_values.get(field_name):
                changed_fields.append(field_name)
        
        # Calculate diffs
        text_fields = ['description', 'title', 'name', 'content', 'acceptance_criteria', 'reproduction_steps', 'expected_behavior', 'actual_behavior']
        diffs = EditHistoryService.calculate_diffs(old_values, new_values, text_fields)
        
        # Create edit history
        edit_history = EditHistory.objects.create(
            user=user,
            project=project,
            content_type=content_type,
            object_id=object_id,
            version=next_version,
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields,
            diffs=diffs,
            comment=comment or ''
        )
        
        return edit_history
    
    @staticmethod
    def get_edit_history(obj, limit: Optional[int] = None) -> List[EditHistory]:
        """
        Get edit history for an object.
        
        Args:
            obj: The model instance
            limit: Optional limit on number of records to return
        
        Returns:
            List of EditHistory instances, ordered by version (newest first)
        """
        content_type = ContentType.objects.get_for_model(obj)
        object_id = obj.id if hasattr(obj, 'id') else None
        
        queryset = EditHistory.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).order_by('-version')
        
        if limit:
            queryset = queryset[:limit]
        
        return list(queryset)
    
    @staticmethod
    def get_version(obj, version: int) -> Optional[EditHistory]:
        """
        Get a specific version of an object's edit history.
        
        Args:
            obj: The model instance
            version: Version number
        
        Returns:
            EditHistory instance or None
        """
        content_type = ContentType.objects.get_for_model(obj)
        object_id = obj.id if hasattr(obj, 'id') else None
        
        try:
            return EditHistory.objects.get(
                content_type=content_type,
                object_id=object_id,
                version=version
            )
        except EditHistory.DoesNotExist:
            return None
    
    @staticmethod
    def compare_versions(obj, version1: int, version2: int) -> Dict[str, Any]:
        """
        Compare two versions of an object.
        
        Args:
            obj: The model instance
            version1: First version number
            version2: Second version number
        
        Returns:
            dict with keys: 'version1', 'version2', 'differences'
        """
        v1 = EditHistoryService.get_version(obj, version1)
        v2 = EditHistoryService.get_version(obj, version2)
        
        if not v1 or not v2:
            return {
                'version1': v1,
                'version2': v2,
                'differences': {}
            }
        
        # Compare the new_values of v1 with old_values of v2
        # (v1 represents state after edit, v2 represents state before its edit)
        differences = EditHistoryService.calculate_diffs(
            v1.new_values if v1 else {},
            v2.old_values if v2 else {}
        )
        
        return {
            'version1': v1,
            'version2': v2,
            'differences': differences
        }


# Convenience function
def create_edit_history(*args, **kwargs):
    """Convenience function to create edit history."""
    return EditHistoryService.create_edit_history(*args, **kwargs)

