"""
Story Operations Service.
Handles story cloning, merging, duplicate detection, and other operations.
"""

from django.db.models import Q
from typing import Dict, List, Optional, Tuple
from apps.projects.models import UserStory, StoryClone, StoryVersion
from django.utils import timezone
import uuid


class StoryOperationsService:
    """Service for story operations like clone, merge, duplicate detection."""
    
    @staticmethod
    def clone_story(story_id: str, project_id: Optional[str] = None, user=None) -> Dict:
        """
        Clone a story.
        
        Returns:
            Dict with cloned story info
        """
        try:
            original_story = UserStory.objects.select_related('project').get(pk=story_id)
        except UserStory.DoesNotExist:
            return {'error': 'Story not found'}
        
        # Determine target project
        target_project = original_story.project
        if project_id:
            try:
                from apps.projects.models import Project
                target_project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                return {'error': 'Target project not found'}
        
        # Create cloned story
        cloned_story = UserStory.objects.create(
            project=target_project,
            title=f"{original_story.title} (Copy)",
            description=original_story.description,
            acceptance_criteria=original_story.acceptance_criteria,
            status='backlog',  # Reset status
            priority=original_story.priority,
            story_points=original_story.story_points,
            story_type=original_story.story_type,
            component=original_story.component,
            labels=original_story.labels.copy() if original_story.labels else [],
            tags=original_story.tags.copy() if original_story.tags else [],
            custom_fields=original_story.custom_fields.copy() if original_story.custom_fields else {},
            created_by=user,
        )
        
        # Create clone record
        StoryClone.objects.create(
            original_story=original_story,
            cloned_story=cloned_story,
            cloned_by=user,
        )
        
        return {
            'original_story_id': str(original_story.id),
            'cloned_story_id': str(cloned_story.id),
            'cloned_story_title': cloned_story.title,
        }
    
    @staticmethod
    def detect_duplicates(story_id: str, threshold: float = 0.8) -> List[Dict]:
        """
        Detect potential duplicate stories.
        
        Args:
            story_id: Story ID to check for duplicates
            threshold: Similarity threshold (0-1)
        
        Returns:
            List of potential duplicates with similarity scores
        """
        try:
            story = UserStory.objects.get(pk=story_id)
        except UserStory.DoesNotExist:
            return []
        
        # Get stories from the same project
        candidates = UserStory.objects.filter(
            project=story.project
        ).exclude(pk=story.id)
        
        duplicates = []
        
        # Simple similarity check based on title and description
        story_text = f"{story.title} {story.description}".lower()
        
        for candidate in candidates:
            candidate_text = f"{candidate.title} {candidate.description}".lower()
            
            # Calculate simple word overlap similarity
            story_words = set(story_text.split())
            candidate_words = set(candidate_text.split())
            
            if len(story_words) == 0:
                continue
            
            intersection = story_words.intersection(candidate_words)
            similarity = len(intersection) / len(story_words.union(candidate_words))
            
            if similarity >= threshold:
                duplicates.append({
                    'story_id': str(candidate.id),
                    'title': candidate.title,
                    'similarity': round(similarity, 2),
                    'status': candidate.status,
                })
        
        # Sort by similarity
        duplicates.sort(key=lambda x: x['similarity'], reverse=True)
        
        return duplicates
    
    @staticmethod
    def merge_stories(source_story_id: str, target_story_id: str, user=None) -> Dict:
        """
        Merge source story into target story.
        
        Returns:
            Dict with merge result
        """
        try:
            source_story = UserStory.objects.get(pk=source_story_id)
            target_story = UserStory.objects.get(pk=target_story_id)
        except UserStory.DoesNotExist:
            return {'error': 'Story not found'}
        
        # Merge data
        # Combine descriptions
        if source_story.description and target_story.description:
            target_story.description = f"{target_story.description}\n\n--- Merged from: {source_story.title} ---\n{source_story.description}"
        elif source_story.description:
            target_story.description = source_story.description
        
        # Combine acceptance criteria
        if source_story.acceptance_criteria and target_story.acceptance_criteria:
            target_story.acceptance_criteria = f"{target_story.acceptance_criteria}\n\n--- Merged from: {source_story.title} ---\n{source_story.acceptance_criteria}"
        elif source_story.acceptance_criteria:
            target_story.acceptance_criteria = source_story.acceptance_criteria
        
        # Merge tags
        if source_story.tags:
            existing_tags = set(target_story.tags or [])
            existing_tags.update(source_story.tags)
            target_story.tags = list(existing_tags)
        
        # Merge labels
        if source_story.labels:
            existing_labels = set(str(l) for l in (target_story.labels or []))
            existing_labels.update(str(l) for l in source_story.labels)
            target_story.labels = list(existing_labels)
        
        # Use higher priority
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        if priority_order.get(source_story.priority, 0) > priority_order.get(target_story.priority, 0):
            target_story.priority = source_story.priority
        
        # Use higher story points
        if source_story.story_points and (not target_story.story_points or source_story.story_points > target_story.story_points):
            target_story.story_points = source_story.story_points
        
        target_story.save()
        
        # Archive source story
        from apps.projects.models import StoryArchive
        StoryArchive.objects.create(
            story=source_story,
            archived_by=user,
            reason=f"Merged into story: {target_story.title}"
        )
        
        return {
            'source_story_id': str(source_story.id),
            'target_story_id': str(target_story.id),
            'target_story_title': target_story.title,
            'merged': True,
        }
    
    @staticmethod
    def create_version(story_id: str, user=None) -> Dict:
        """
        Create a version snapshot of a story.
        
        Returns:
            Dict with version info
        """
        try:
            story = UserStory.objects.get(pk=story_id)
        except UserStory.DoesNotExist:
            return {'error': 'Story not found'}
        
        # Get next version number
        last_version = StoryVersion.objects.filter(story=story).order_by('-version_number').first()
        version_number = (last_version.version_number + 1) if last_version else 1
        
        # Create version
        version = StoryVersion.objects.create(
            story=story,
            version_number=version_number,
            title=story.title,
            description=story.description,
            acceptance_criteria=story.acceptance_criteria,
            status=story.status,
            priority=story.priority,
            story_points=story.story_points,
            story_data={
                'labels': story.labels,
                'tags': story.tags,
                'custom_fields': story.custom_fields,
                'component': story.component,
                'story_type': story.story_type,
            },
            created_by=user,
        )
        
        return {
            'version_id': str(version.id),
            'version_number': version_number,
            'created_at': version.created_at,
        }

