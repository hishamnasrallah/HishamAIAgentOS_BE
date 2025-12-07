"""
Analytics Service

Burndown charts, velocity tracking, and sprint health metrics.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from apps.projects.models import Sprint, Story, Project


class ProjectAnalytics:
    """
    Project analytics and metrics calculation.
    
    Provides burndown charts, velocity tracking, and health metrics.
    """
    
    async def calculate_burndown(
        self,
        sprint_id: str
    ) -> Dict[str, Any]:
        """
        Calculate burndown chart data for a sprint.
        
        Args:
            sprint_id: Sprint UUID
            
        Returns:
            Dict with daily remaining points and ideal burndown
        """
        sprint = await Sprint.objects.aget(id=sprint_id)
        
        # Get all stories in sprint
        stories = await Story.objects.filter(sprint=sprint).alist()
        stories_list = list(stories)
        
        # Calculate total points
        total_points = sum(s.story_points for s in stories_list)
        
        # Calculate sprint duration in days
        if sprint.start_date and sprint.end_date:
            sprint_days = (sprint.end_date - sprint.start_date).days + 1
        else:
            sprint_days = 10  # Default 2-week sprint
        
        # Calculate ideal burndown (linear)
        ideal_burndown = {}
        points_per_day = total_points / sprint_days if sprint_days > 0 else 0
        
        for day in range(sprint_days + 1):
            ideal_burndown[f"day_{day}"] = max(0, total_points - (points_per_day * day))
        
        # Calculate actual burndown (based on completed stories)
        actual_burndown = {}
        completed_points = 0
        
        for day in range(sprint_days + 1):
            # Count points completed by this day
            # In production, would use story completion timestamps
            completed_stories = [s for s in stories_list if s.status == 'done']
            completed_points = sum(s.story_points for s in completed_stories)
            
            actual_burndown[f"day_{day}"] = total_points - completed_points
        
        return {
            "sprint_id": str(sprint.id),
            "sprint_name": sprint.name,
            "total_points": total_points,
            "completed_points": completed_points,
            "remaining_points": total_points - completed_points,
            "sprint_days": sprint_days,
            "ideal_burndown": ideal_burndown,
            "actual_burndown": actual_burndown,
            "on_track": completed_points >= (total_points / 2) if sprint_days > 5 else True
        }
    
    async def calculate_velocity(
        self,
        project_id: str,
        num_sprints: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate team velocity over recent sprints.
        
        Args:
            project_id: Project UUID
            num_sprints: Number of recent sprints to analyze
            
        Returns:
            Dict with velocity metrics
        """
        # Get recent completed sprints
        sprints = await Sprint.objects.filter(
            project_id=project_id,
            status='completed'
        ).order_by('-end_date')[:num_sprints].alist()
        
        sprints_list = list(sprints)
        
        if not sprints_list:
            return {
                "average_velocity": 0,
                "velocity_trend": "unknown",
                "sprint_velocities": []
            }
        
        # Calculate velocity for each sprint
        sprint_velocities = []
        
        for sprint in sprints_list:
            completed_stories = await Story.objects.filter(
                sprint=sprint,
                status='done'
            ).alist()
            
            velocity = sum(s.story_points for s in completed_stories)
            
            sprint_velocities.append({
                "sprint_name": sprint.name,
                "velocity": velocity,
                "end_date": sprint.end_date.isoformat() if sprint.end_date else None
            })
        
        # Calculate average
        velocities = [sv['velocity'] for sv in sprint_velocities]
        average_velocity = sum(velocities) / len(velocities) if velocities else 0
        
        # Determine trend
        if len(velocities) >= 2:
            recent_avg = sum(velocities[:2]) / 2
            older_avg = sum(velocities[2:]) / len(velocities[2:]) if len(velocities) > 2 else recent_avg
            
            if recent_avg > older_avg * 1.1:
                trend = "increasing"
            elif recent_avg < older_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "project_id": str(project_id),
            "average_velocity": round(average_velocity, 2),
            "velocity_trend": trend,
            "sprint_velocities": sprint_velocities,
            "num_sprints_analyzed": len(sprint_velocities)
        }
    
    async def calculate_sprint_health(
        self,
        sprint_id: str
    ) -> Dict[str, Any]:
        """
        Calculate overall sprint health metrics.
        
        Args:
            sprint_id: Sprint UUID
            
        Returns:
            Dict with health indicators
        """
        sprint = await Sprint.objects.aget(id=sprint_id)
        
        # Get stories
        all_stories = await Story.objects.filter(sprint=sprint).alist()
        all_stories_list = list(all_stories)
        
        if not all_stories_list:
            return {"health_score": 0, "status": "empty"}
        
        # Count by status
        done_count = len([s for s in all_stories_list if s.status == 'done'])
        in_progress_count = len([s for s in all_stories_list if s.status == 'in_progress'])
        todo_count = len([s for s in all_stories_list if s.status in ['todo', 'planned']])
        
        # Calculate completion percentage
        completion_percentage = (done_count / len(all_stories_list)) * 100 if all_stories_list else 0
        
        # Calculate health score (0-100)
        # Based on completion percentage and days remaining
        if sprint.end_date:
            days_remaining = (sprint.end_date - datetime.now().date()).days
            if days_remaining < 0:
                health_score = completion_percentage  # Sprint is over
            else:
                # Expected completion by now
                sprint_duration = (sprint.end_date - sprint.start_date).days if sprint.start_date else 10
                expected_completion = ((sprint_duration - days_remaining) / sprint_duration) * 100
                
                # Health is how close actual is to expected
                if completion_percentage >= expected_completion:
                    health_score = min(100, completion_percentage + 10)
                else:
                    health_score = max(0, completion_percentage - 10)
        else:
            health_score = completion_percentage
        
        # Determine status
        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "at_risk"
        else:
            status = "critical"
        
        return {
            "sprint_id": str(sprint.id),
            "health_score": round(health_score, 2),
            "status": status,
            "completion_percentage": round(completion_percentage, 2),
            "total_stories": len(all_stories_list),
            "done": done_count,
            "in_progress": in_progress_count,
            "todo": todo_count
        }


# Global instance
analytics = ProjectAnalytics()
