"""
Sprint Automation Service.
Automates sprint-related operations like auto-closing, auto-assignment, etc.
"""

from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List, Optional
from apps.projects.models import Sprint, UserStory, Project, ProjectConfiguration


class SprintAutomationService:
    """Service for automating sprint operations."""
    
    @staticmethod
    def auto_close_sprints(project_id: Optional[str] = None) -> List[Dict]:
        """
        Automatically close sprints that have passed their end date.
        
        Returns:
            List of closed sprints
        """
        from apps.projects.services.notifications import get_notification_service
        
        now = timezone.now().date()
        queryset = Sprint.objects.filter(
            status='active',
            end_date__lt=now
        )
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        closed_sprints = []
        notification_service = get_notification_service()
        
        for sprint in queryset:
            # Check if project has auto_close_sprints enabled
            try:
                config = sprint.project.configuration
                if not config.auto_close_sprints:
                    continue
            except ProjectConfiguration.DoesNotExist:
                continue
            
            # Move incomplete stories back to backlog
            incomplete_stories = UserStory.objects.filter(
                sprint=sprint,
                status__in=['backlog', 'todo', 'in_progress', 'review']
            )
            
            incomplete_count = incomplete_stories.count()
            
            # Update sprint status
            sprint.status = 'completed'
            sprint.save(update_fields=['status'])
            
            # Notify team
            members = list(sprint.project.members.all())
            if sprint.project.owner:
                members.append(sprint.project.owner)
            
            for member in set(members):
                notification_service.create_notification(
                    recipient=member,
                    notification_type='sprint_closed',
                    title=f'Sprint {sprint.name} Auto-Closed',
                    message=f'Sprint {sprint.name} has been automatically closed. {incomplete_count} stories moved to backlog.',
                    project=sprint.project,
                    metadata={
                        'sprint_id': str(sprint.id),
                        'incomplete_stories': incomplete_count,
                    }
                )
            
            closed_sprints.append({
                'sprint_id': str(sprint.id),
                'sprint_name': sprint.name,
                'project_id': str(sprint.project.id),
                'incomplete_stories': incomplete_count,
            })
        
        return closed_sprints
    
    @staticmethod
    def auto_create_sprint(project_id: str) -> Optional[Dict]:
        """
        Automatically create the next sprint based on project configuration.
        
        Returns:
            Created sprint info or None
        """
        try:
            project = Project.objects.get(pk=project_id)
            config = project.configuration
        except (Project.DoesNotExist, ProjectConfiguration.DoesNotExist):
            return None
        
        # Get the last sprint
        last_sprint = Sprint.objects.filter(project=project).order_by('-sprint_number').first()
        
        if not last_sprint:
            # First sprint
            sprint_number = 1
            start_date = project.start_date or timezone.now().date()
        else:
            sprint_number = last_sprint.sprint_number + 1
            # Start date is day after last sprint's end date
            start_date = last_sprint.end_date + timedelta(days=1)
        
        # Calculate end date based on default duration
        end_date = start_date + timedelta(days=config.default_sprint_duration_days - 1)
        
        # Create sprint
        sprint = Sprint.objects.create(
            project=project,
            name=f'Sprint {sprint_number}',
            sprint_number=sprint_number,
            start_date=start_date,
            end_date=end_date,
            status='planned',
            created_by=project.owner,
        )
        
        return {
            'sprint_id': str(sprint.id),
            'sprint_name': sprint.name,
            'sprint_number': sprint_number,
            'start_date': start_date,
            'end_date': end_date,
        }
    
    @staticmethod
    def auto_assign_stories_to_sprint(project_id: str, sprint_id: str) -> Dict:
        """
        Automatically assign stories to a sprint based on priority and capacity.
        
        Returns:
            Dict with assignment results
        """
        try:
            sprint = Sprint.objects.get(pk=sprint_id, project_id=project_id)
            config = sprint.project.configuration
        except (Sprint.DoesNotExist, ProjectConfiguration.DoesNotExist):
            return {'error': 'Sprint or configuration not found'}
        
        # Get available story points
        max_points = config.max_story_points_per_sprint
        current_points = UserStory.objects.filter(sprint=sprint).aggregate(
            total=Sum('story_points')
        )['total'] or 0
        available_points = max_points - current_points
        
        # Get unassigned stories ordered by priority
        unassigned_stories = UserStory.objects.filter(
            project_id=project_id,
            sprint__isnull=True,
            status__in=['backlog', 'todo']
        ).order_by(
            '-priority',  # Critical first
            'story_points'  # Smaller stories first
        )
        
        assigned_stories = []
        total_assigned_points = 0
        
        for story in unassigned_stories:
            story_points = story.story_points or 0
            
            # Check if we have capacity
            if not config.allow_overcommitment and total_assigned_points + story_points > available_points:
                break
            
            # Assign to sprint
            story.sprint = sprint
            story.save(update_fields=['sprint'])
            
            assigned_stories.append({
                'id': str(story.id),
                'title': story.title,
                'story_points': story_points,
            })
            
            total_assigned_points += story_points
        
        # Update sprint metrics
        sprint.total_story_points = UserStory.objects.filter(sprint=sprint).aggregate(
            total=Sum('story_points')
        )['total'] or 0
        sprint.save(update_fields=['total_story_points'])
        
        return {
            'sprint_id': str(sprint.id),
            'assigned_count': len(assigned_stories),
            'assigned_points': total_assigned_points,
            'assigned_stories': assigned_stories,
        }
    
    @staticmethod
    def check_sprint_health(sprint_id: str) -> Dict:
        """
        Check sprint health and provide recommendations.
        
        Returns:
            Dict with health metrics and recommendations
        """
        try:
            sprint = Sprint.objects.select_related('project').prefetch_related('stories').get(pk=sprint_id)
        except Sprint.DoesNotExist:
            return {'error': 'Sprint not found'}
        
        stories = sprint.stories.all()
        total_stories = stories.count()
        
        # Calculate metrics
        completed_stories = stories.filter(status='done').count()
        in_progress_stories = stories.filter(status='in_progress').count()
        todo_stories = stories.filter(status__in=['backlog', 'todo']).count()
        
        total_points = sum(s.story_points or 0 for s in stories)
        completed_points = sum(s.story_points or 0 for s in stories if s.status == 'done')
        
        # Calculate progress
        days_elapsed = (timezone.now().date() - sprint.start_date).days
        days_total = (sprint.end_date - sprint.start_date).days
        time_progress = (days_elapsed / days_total * 100) if days_total > 0 else 0
        
        story_progress = (completed_stories / total_stories * 100) if total_stories > 0 else 0
        points_progress = (completed_points / total_points * 100) if total_points > 0 else 0
        
        # Health score (0-100)
        health_score = (story_progress + points_progress) / 2
        
        # Check if on track
        is_on_track = story_progress >= time_progress - 10  # Allow 10% variance
        
        # Recommendations
        recommendations = []
        
        if not is_on_track:
            recommendations.append({
                'type': 'warning',
                'message': f'Sprint is behind schedule. {story_progress:.1f}% complete vs {time_progress:.1f}% time elapsed.',
            })
        
        if in_progress_stories > total_stories * 0.5:
            recommendations.append({
                'type': 'info',
                'message': 'Many stories in progress. Consider focusing on completing current work.',
            })
        
        if todo_stories > total_stories * 0.3 and days_elapsed > days_total * 0.5:
            recommendations.append({
                'type': 'warning',
                'message': 'Many stories still in backlog. Consider reassigning or extending sprint.',
            })
        
        return {
            'sprint_id': str(sprint.id),
            'sprint_name': sprint.name,
            'health_score': round(health_score, 2),
            'is_on_track': is_on_track,
            'metrics': {
                'total_stories': total_stories,
                'completed_stories': completed_stories,
                'in_progress_stories': in_progress_stories,
                'todo_stories': todo_stories,
                'total_points': total_points,
                'completed_points': completed_points,
                'days_elapsed': days_elapsed,
                'days_remaining': max(0, days_total - days_elapsed),
            },
            'progress': {
                'time_progress': round(time_progress, 2),
                'story_progress': round(story_progress, 2),
                'points_progress': round(points_progress, 2),
            },
            'recommendations': recommendations,
        }

