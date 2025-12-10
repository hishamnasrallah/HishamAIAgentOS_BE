"""
Statistics Service for Project Management

Provides backend statistics calculation for story types, components, and other metrics.
Includes caching for performance optimization.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from django.db.models import Count, Q, Sum, Avg, F
from django.core.cache import cache
from django.utils import timezone
from apps.projects.models import UserStory, Task, Bug, Issue, Project

logger = logging.getLogger(__name__)


class StatisticsService:
    """
    Service for calculating project statistics.
    Includes caching for performance.
    """
    
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @staticmethod
    def _get_cache_key(project_id: str, stat_type: str, **kwargs) -> str:
        """Generate cache key for statistics."""
        key_parts = [f'stats:{project_id}:{stat_type}']
        for k, v in sorted(kwargs.items()):
            key_parts.append(f'{k}:{v}')
        return ':'.join(key_parts)
    
    def get_story_type_distribution(
        self,
        project_id: str,
        use_cache: bool = True
    ) -> Dict[str, int]:
        """
        Get distribution of story types in a project.
        
        Args:
            project_id: UUID of the project
            use_cache: Whether to use cache
            
        Returns:
            Dictionary mapping story type to count
        """
        cache_key = self._get_cache_key(project_id, 'story_type_distribution')
        
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            # Get all work items (UserStory, Task, Bug, Issue)
            stories = UserStory.objects.filter(project_id=project_id)
            # Tasks are related to projects through stories
            tasks = Task.objects.filter(story__project_id=project_id)
            bugs = Bug.objects.filter(project_id=project_id)
            issues = Issue.objects.filter(project_id=project_id)
            
            distribution = {}
            
            # Count by story_type for UserStory
            story_counts = stories.values('story_type').annotate(count=Count('id'))
            for item in story_counts:
                story_type = item['story_type'] or 'unknown'
                distribution[story_type] = distribution.get(story_type, 0) + item['count']
            
            # Tasks, Bugs, Issues don't have story_type, but we can count them
            distribution['task'] = distribution.get('task', 0) + tasks.count()
            distribution['bug'] = distribution.get('bug', 0) + bugs.count()
            distribution['issue'] = distribution.get('issue', 0) + issues.count()
            
            # Ensure all standard types are present
            standard_types = ['feature', 'bug', 'enhancement', 'technical_debt', 'documentation', 'research', 'task', 'issue']
            for stype in standard_types:
                if stype not in distribution:
                    distribution[stype] = 0
            
            if use_cache:
                cache.set(cache_key, distribution, self.CACHE_TIMEOUT)
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error calculating story type distribution for project {project_id}: {e}", exc_info=True)
            return {}
    
    def get_component_distribution(
        self,
        project_id: str,
        use_cache: bool = True
    ) -> Dict[str, int]:
        """
        Get distribution of components in a project.
        
        Args:
            project_id: UUID of the project
            use_cache: Whether to use cache
            
        Returns:
            Dictionary mapping component name to count
        """
        cache_key = self._get_cache_key(project_id, 'component_distribution')
        
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            # Get all work items with components
            stories = UserStory.objects.filter(
                project_id=project_id,
                component__isnull=False
            ).exclude(component='')
            
            # Tasks are related to projects through stories
            tasks = Task.objects.filter(
                story__project_id=project_id,
                component__isnull=False
            ).exclude(component='')
            
            bugs = Bug.objects.filter(
                project_id=project_id,
                component__isnull=False
            ).exclude(component='')
            
            issues = Issue.objects.filter(
                project_id=project_id,
                component__isnull=False
            ).exclude(component='')
            
            distribution = {}
            
            # Count by component
            for model in [stories, tasks, bugs, issues]:
                component_counts = model.values('component').annotate(count=Count('id'))
                for item in component_counts:
                    component = item['component']
                    if component:
                        distribution[component] = distribution.get(component, 0) + item['count']
            
            if use_cache:
                cache.set(cache_key, distribution, self.CACHE_TIMEOUT)
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error calculating component distribution for project {project_id}: {e}", exc_info=True)
            return {}
    
    def get_story_type_trends(
        self,
        project_id: str,
        days: int = 30,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Get story type trends over time.
        
        Args:
            project_id: UUID of the project
            days: Number of days to look back
            use_cache: Whether to use cache
            
        Returns:
            List of dictionaries with date and counts per story type
        """
        cache_key = self._get_cache_key(project_id, 'story_type_trends', days=days)
        
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            # Get stories created in the time period
            stories = UserStory.objects.filter(
                project_id=project_id,
                created_at__gte=start_date
            )
            
            # Group by date and story_type
            trends = []
            current_date = start_date.date()
            end_date = timezone.now().date()
            
            while current_date <= end_date:
                day_stories = stories.filter(
                    created_at__date=current_date
                )
                
                day_counts = {}
                for story in day_stories:
                    story_type = story.story_type or 'unknown'
                    day_counts[story_type] = day_counts.get(story_type, 0) + 1
                
                trends.append({
                    'date': current_date.isoformat(),
                    'counts': day_counts,
                    'total': day_stories.count()
                })
                
                current_date += timedelta(days=1)
            
            if use_cache:
                cache.set(cache_key, trends, self.CACHE_TIMEOUT)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating story type trends for project {project_id}: {e}", exc_info=True)
            return []
    
    def get_component_trends(
        self,
        project_id: str,
        days: int = 30,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Get component trends over time.
        
        Args:
            project_id: UUID of the project
            days: Number of days to look back
            use_cache: Whether to use cache
            
        Returns:
            List of dictionaries with date and counts per component
        """
        cache_key = self._get_cache_key(project_id, 'component_trends', days=days)
        
        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            # Get all work items with components created in the time period
            stories = UserStory.objects.filter(
                project_id=project_id,
                component__isnull=False,
                component__gt='',
                created_at__gte=start_date
            )
            
            # Tasks are related to projects through stories
            tasks = Task.objects.filter(
                story__project_id=project_id,
                component__isnull=False,
                component__gt='',
                created_at__gte=start_date
            )
            
            bugs = Bug.objects.filter(
                project_id=project_id,
                component__isnull=False,
                component__gt='',
                created_at__gte=start_date
            )
            
            issues = Issue.objects.filter(
                project_id=project_id,
                component__isnull=False,
                component__gt='',
                created_at__gte=start_date
            )
            
            # Combine all items
            all_items = []
            for model in [stories, tasks, bugs, issues]:
                all_items.extend(list(model))
            
            # Group by date and component
            trends = []
            current_date = start_date.date()
            end_date = timezone.now().date()
            
            while current_date <= end_date:
                day_items = [
                    item for item in all_items
                    if item.created_at.date() == current_date
                ]
                
                day_counts = {}
                for item in day_items:
                    component = item.component
                    if component:
                        day_counts[component] = day_counts.get(component, 0) + 1
                
                trends.append({
                    'date': current_date.isoformat(),
                    'counts': day_counts,
                    'total': len(day_items)
                })
                
                current_date += timedelta(days=1)
            
            if use_cache:
                cache.set(cache_key, trends, self.CACHE_TIMEOUT)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating component trends for project {project_id}: {e}", exc_info=True)
            return []
    
    def invalidate_cache(self, project_id: str, stat_type: Optional[str] = None):
        """
        Invalidate cache for project statistics.
        
        Args:
            project_id: UUID of the project
            stat_type: Specific stat type to invalidate, or None for all
        """
        if stat_type:
            # Invalidate specific stat type
            pattern = f'stats:{project_id}:{stat_type}*'
            # Note: Django cache doesn't support pattern deletion directly
            # This would need Redis or similar for pattern matching
            logger.warning(f"Cache invalidation for pattern {pattern} not fully supported with default cache backend")
        else:
            # Invalidate all stats for project
            patterns = [
                f'stats:{project_id}:story_type_distribution',
                f'stats:{project_id}:component_distribution',
                f'stats:{project_id}:story_type_trends*',
                f'stats:{project_id}:component_trends*',
            ]
            for pattern in patterns:
                logger.warning(f"Cache invalidation for pattern {pattern} not fully supported with default cache backend")


# Singleton instance
statistics_service = StatisticsService()

