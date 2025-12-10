"""
Dependency Impact Analysis Service.
Analyzes the impact of dependencies on stories and provides insights.
"""

from django.db.models import Q, Count, Prefetch
from typing import Dict, List, Optional, Set
from apps.projects.models import UserStory, StoryDependency, StoryLink


class DependencyImpactService:
    """Service for analyzing dependency impact."""
    
    @staticmethod
    def analyze_impact(story_id: str) -> Dict:
        """
        Analyze the impact of a story's dependencies.
        
        Returns:
            Dict with impact analysis including:
            - blocking_stories: Stories that block this one
            - blocked_stories: Stories blocked by this one
            - impact_score: Overall impact score
            - critical_path: Whether this story is on a critical path
            - estimated_delay: Estimated delay if dependencies aren't resolved
        """
        try:
            story = UserStory.objects.select_related('project').prefetch_related(
                'dependencies',
                'blocking_dependencies',
                'story_links'
            ).get(pk=story_id)
        except UserStory.DoesNotExist:
            return {'error': 'Story not found'}
        
        # Get blocking dependencies (stories this one depends on)
        # StoryDependency uses source_story and target_story, not story and depends_on
        blocking_deps = StoryDependency.objects.filter(
            source_story=story,
            resolved=False
        ).select_related('target_story')
        
        # Get blocked dependencies (stories that depend on this one)
        blocked_deps = StoryDependency.objects.filter(
            target_story=story,
            resolved=False
        ).select_related('source_story')
        
        # Get story links
        blocking_links = StoryLink.objects.filter(
            target_content_type__model='userstory',
            target_object_id=story_id,
            link_type__in=['blocks', 'depends_on']
        ).select_related('source_content_type')
        
        blocked_links = StoryLink.objects.filter(
            source_content_type__model='userstory',
            source_object_id=story_id,
            link_type__in=['blocks', 'depends_on']
        ).select_related('target_content_type')
        
        # Calculate impact metrics
        blocking_stories = []
        for dep in blocking_deps:
            blocking_stories.append({
                'id': str(dep.target_story.id),
                'title': dep.target_story.title,
                'status': dep.target_story.status,
                'dependency_type': dep.dependency_type,
                'resolved': dep.resolved,
            })
        
        blocked_stories = []
        for dep in blocked_deps:
            blocked_stories.append({
                'id': str(dep.source_story.id),
                'title': dep.source_story.title,
                'status': dep.source_story.status,
                'dependency_type': dep.dependency_type,
                'resolved': dep.resolved,
            })
        
        # Calculate impact score (0-100)
        # Higher score = more critical
        impact_score = 0
        
        # Blocking stories increase impact
        impact_score += len(blocking_stories) * 10
        
        # Blocked stories increase impact
        impact_score += len(blocked_stories) * 15
        
        # Unresolved dependencies increase impact
        unresolved_blocking = sum(1 for s in blocking_stories if not s.get('resolved', True))
        impact_score += unresolved_blocking * 20
        
        # Status-based impact
        if story.status in ['in_progress', 'review']:
            impact_score += 20
        elif story.status == 'done':
            impact_score -= 10
        
        # Priority-based impact
        priority_weights = {'critical': 30, 'high': 20, 'medium': 10, 'low': 5}
        impact_score += priority_weights.get(story.priority, 0)
        
        impact_score = min(100, max(0, impact_score))
        
        # Check if on critical path
        is_critical = len(blocked_stories) > 0 and len(blocking_stories) > 0
        
        # Estimate delay
        estimated_delay = 0
        for blocking in blocking_stories:
            if not blocking.get('resolved', True):
                # Estimate delay based on blocking story status
                if blocking['status'] in ['backlog', 'todo']:
                    estimated_delay += 3  # days
                elif blocking['status'] == 'in_progress':
                    estimated_delay += 1  # days
        
        return {
            'story_id': str(story.id),
            'story_title': story.title,
            'blocking_stories': blocking_stories,
            'blocked_stories': blocked_stories,
            'blocking_count': len(blocking_stories),
            'blocked_count': len(blocked_stories),
            'impact_score': impact_score,
            'is_critical_path': is_critical,
            'estimated_delay_days': estimated_delay,
            'unresolved_blocking': unresolved_blocking,
            'risk_level': 'high' if impact_score > 70 else 'medium' if impact_score > 40 else 'low',
        }
    
    @staticmethod
    def analyze_project_impact(project_id: str) -> Dict:
        """
        Analyze dependency impact for all stories in a project.
        
        Returns:
            Dict with project-wide impact analysis
        """
        stories = UserStory.objects.filter(project_id=project_id).select_related('project')
        
        impact_data = []
        total_blocking = 0
        total_blocked = 0
        critical_stories = []
        
        for story in stories:
            analysis = DependencyImpactService.analyze_impact(str(story.id))
            if 'error' not in analysis:
                impact_data.append(analysis)
                total_blocking += analysis['blocking_count']
                total_blocked += analysis['blocked_count']
                
                if analysis['is_critical_path']:
                    critical_stories.append({
                        'id': analysis['story_id'],
                        'title': analysis['story_title'],
                        'impact_score': analysis['impact_score'],
                    })
        
        # Sort by impact score
        impact_data.sort(key=lambda x: x['impact_score'], reverse=True)
        critical_stories.sort(key=lambda x: x['impact_score'], reverse=True)
        
        return {
            'project_id': project_id,
            'total_stories': len(impact_data),
            'total_blocking_dependencies': total_blocking,
            'total_blocked_dependencies': total_blocked,
            'critical_path_stories': critical_stories,
            'high_impact_stories': [s for s in impact_data if s['impact_score'] > 70],
            'medium_impact_stories': [s for s in impact_data if 40 < s['impact_score'] <= 70],
            'low_impact_stories': [s for s in impact_data if s['impact_score'] <= 40],
            'stories_by_impact': impact_data[:20],  # Top 20
        }
    
    @staticmethod
    def get_dependency_chain(story_id: str, direction: str = 'both') -> Dict:
        """
        Get the full dependency chain for a story.
        
        Args:
            story_id: Story ID
            direction: 'up' (blocking), 'down' (blocked), or 'both'
        
        Returns:
            Dict with dependency chain
        """
        try:
            story = UserStory.objects.get(pk=story_id)
        except UserStory.DoesNotExist:
            return {'error': 'Story not found'}
        
        def get_upstream(story, visited=None):
            """Get all stories that block this one."""
            if visited is None:
                visited = set()
            
            if str(story.id) in visited:
                return []
            
            visited.add(str(story.id))
            
            deps = StoryDependency.objects.filter(
                source_story=story,
                resolved=False
            ).select_related('target_story')
            
            upstream = []
            for dep in deps:
                upstream.append({
                    'id': str(dep.target_story.id),
                    'title': dep.target_story.title,
                    'status': dep.target_story.status,
                })
                # Recursively get upstream
                upstream.extend(get_upstream(dep.target_story, visited))
            
            return upstream
        
        def get_downstream(story, visited=None):
            """Get all stories blocked by this one."""
            if visited is None:
                visited = set()
            
            if str(story.id) in visited:
                return []
            
            visited.add(str(story.id))
            
            deps = StoryDependency.objects.filter(
                target_story=story,
                resolved=False
            ).select_related('source_story')
            
            downstream = []
            for dep in deps:
                downstream.append({
                    'id': str(dep.source_story.id),
                    'title': dep.source_story.title,
                    'status': dep.source_story.status,
                })
                # Recursively get downstream
                downstream.extend(get_downstream(dep.source_story, visited))
            
            return downstream
        
        result = {
            'story_id': str(story.id),
            'story_title': story.title,
        }
        
        if direction in ['up', 'both']:
            result['upstream'] = get_upstream(story)
        
        if direction in ['down', 'both']:
            result['downstream'] = get_downstream(story)
        
        return result

