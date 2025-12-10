"""
Reports and analytics service.
Provides time reports, burndown charts, velocity tracking, and other analytics.
"""

from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
from typing import Dict, List, Any, Optional
from apps.projects.models import UserStory, Task, Bug, Issue, Sprint, TimeLog, Epic


class ReportsService:
    """Service for generating reports and analytics."""
    
    @staticmethod
    def get_time_reports(project_id: str, start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None, user_id: Optional[str] = None):
        """Generate time reports."""
        filters = Q(project_id=project_id)
        if start_date:
            filters &= Q(created_at__gte=start_date)
        if end_date:
            filters &= Q(created_at__lte=end_date)
        if user_id:
            filters &= Q(assigned_to_id=user_id)
        
        stories = UserStory.objects.filter(filters)
        tasks = Task.objects.filter(filters)
        bugs = Bug.objects.filter(filters)
        issues = Issue.objects.filter(filters)
        
        # Get time logs
        time_logs = TimeLog.objects.filter(
            project_id=project_id,
            logged_at__gte=start_date if start_date else timezone.now() - timedelta(days=30),
            logged_at__lte=end_date if end_date else timezone.now()
        )
        
        if user_id:
            time_logs = time_logs.filter(user_id=user_id)
        
        total_hours = time_logs.aggregate(total=Sum('hours'))['total'] or 0
        
        return {
            'total_hours': total_hours,
            'total_stories': stories.count(),
            'total_tasks': tasks.count(),
            'total_bugs': bugs.count(),
            'total_issues': issues.count(),
            'time_by_user': time_logs.values('user__email', 'user__username').annotate(
                total_hours=Sum('hours')
            ),
            'time_by_story': time_logs.values('story__title', 'story__id').annotate(
                total_hours=Sum('hours')
            ),
        }
    
    @staticmethod
    def get_burndown_chart(sprint_id: str):
        """Generate burndown chart data for a sprint."""
        try:
            sprint = Sprint.objects.get(id=sprint_id)
        except Sprint.DoesNotExist:
            return None
        
        # Get all stories in sprint
        stories = UserStory.objects.filter(sprint_id=sprint_id)
        total_points = stories.aggregate(total=Sum('story_points'))['total'] or 0
        
        # Calculate daily progress
        dates = []
        remaining_points = []
        completed_points = []
        
        current_date = sprint.start_date
        while current_date <= sprint.end_date:
            completed = stories.filter(
                status='done',
                updated_at__date__lte=current_date
            ).aggregate(total=Sum('story_points'))['total'] or 0
            
            remaining = total_points - completed
            
            dates.append(current_date.isoformat())
            remaining_points.append(remaining)
            completed_points.append(completed)
            
            current_date += timedelta(days=1)
        
        return {
            'sprint_id': sprint_id,
            'sprint_name': sprint.name,
            'start_date': sprint.start_date.isoformat(),
            'end_date': sprint.end_date.isoformat(),
            'total_points': total_points,
            'dates': dates,
            'remaining_points': remaining_points,
            'completed_points': completed_points,
        }
    
    @staticmethod
    def get_velocity_tracking(project_id: str, num_sprints: int = 5):
        """Track velocity across sprints."""
        sprints = Sprint.objects.filter(
            project_id=project_id,
            status='completed'
        ).order_by('-sprint_number')[:num_sprints]
        
        velocity_data = []
        for sprint in sprints:
            stories = UserStory.objects.filter(sprint_id=sprint.id)
            completed_stories = stories.filter(status='done')
            
            total_points = stories.aggregate(total=Sum('story_points'))['total'] or 0
            completed_points = completed_stories.aggregate(total=Sum('story_points'))['total'] or 0
            
            velocity_data.append({
                'sprint_id': str(sprint.id),
                'sprint_name': sprint.name,
                'sprint_number': sprint.sprint_number,
                'total_points': total_points,
                'completed_points': completed_points,
                'completion_rate': (completed_points / total_points * 100) if total_points > 0 else 0,
            })
        
        return {
            'project_id': project_id,
            'sprints': velocity_data,
            'average_velocity': sum(v['completed_points'] for v in velocity_data) / len(velocity_data) if velocity_data else 0,
        }
    
    @staticmethod
    def get_estimation_history(project_id: str, story_id: Optional[str] = None):
        """Get estimation history for stories."""
        filters = Q(project_id=project_id)
        if story_id:
            filters &= Q(id=story_id)
        
        stories = UserStory.objects.filter(filters)
        
        # Get edit history for story_points changes
        from .models import EditHistory
        estimation_changes = EditHistory.objects.filter(
            content_type__model='userstory',
            field='story_points',
            object_id__in=[str(s.id) for s in stories]
        ).order_by('-timestamp')
        
        return {
            'stories': [
                {
                    'story_id': str(s.id),
                    'story_title': s.title,
                    'current_points': s.story_points,
                    'estimation_history': [
                        {
                            'timestamp': change.timestamp.isoformat(),
                            'old_value': change.old_value,
                            'new_value': change.new_value,
                            'changed_by': str(change.user.id) if change.user else None,
                        }
                        for change in estimation_changes.filter(object_id=str(s.id))
                    ]
                }
                for s in stories
            ]
        }
    
    @staticmethod
    def get_actual_vs_estimated(project_id: str):
        """Compare actual time vs estimated time."""
        stories = UserStory.objects.filter(project_id=project_id)
        
        results = []
        for story in stories:
            # Get time logs for this story
            time_logs = TimeLog.objects.filter(story_id=story.id)
            actual_hours = time_logs.aggregate(total=Sum('hours'))['total'] or 0
            
            # Estimate: 1 story point = 8 hours (configurable)
            estimated_hours = story.story_points * 8 if story.story_points else 0
            
            results.append({
                'story_id': str(story.id),
                'story_title': story.title,
                'story_points': story.story_points,
                'estimated_hours': estimated_hours,
                'actual_hours': actual_hours,
                'variance': actual_hours - estimated_hours,
                'variance_percentage': ((actual_hours - estimated_hours) / estimated_hours * 100) if estimated_hours > 0 else 0,
            })
        
        return {
            'project_id': project_id,
            'stories': results,
            'total_estimated': sum(r['estimated_hours'] for r in results),
            'total_actual': sum(r['actual_hours'] for r in results),
        }
    
    @staticmethod
    def get_epic_progress(project_id: str, epic_id: Optional[str] = None):
        """Get progress tracking for epics."""
        filters = Q(project_id=project_id)
        if epic_id:
            filters &= Q(id=epic_id)
        
        epics = Epic.objects.filter(filters)
        
        results = []
        for epic in epics:
            stories = UserStory.objects.filter(epic_id=epic.id)
            total_stories = stories.count()
            completed_stories = stories.filter(status='done').count()
            total_points = stories.aggregate(total=Sum('story_points'))['total'] or 0
            completed_points = stories.filter(status='done').aggregate(total=Sum('story_points'))['total'] or 0
            
            results.append({
                'epic_id': str(epic.id),
                'epic_title': epic.title,
                'epic_status': epic.status,
                'total_stories': total_stories,
                'completed_stories': completed_stories,
                'completion_percentage': (completed_stories / total_stories * 100) if total_stories > 0 else 0,
                'total_points': total_points,
                'completed_points': completed_points,
                'points_completion_percentage': (completed_points / total_points * 100) if total_points > 0 else 0,
            })
        
        return {
            'project_id': project_id,
            'epics': results,
        }

