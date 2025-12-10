"""
Analytics Service

Burndown charts, velocity tracking, and sprint health metrics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
from django.db.models import Sum, Count, Q, Avg, F, Max, Min
from django.utils import timezone
from apps.projects.models import Sprint, UserStory, Project, Task, Bug, Issue, TimeLog, EditHistory
# Alias for backward compatibility
Story = UserStory


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


    async def calculate_cycle_time(
        self,
        project_id: str,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Calculate cycle time (time from start to completion) for stories.
        
        Args:
            project_id: Project UUID
            days: Number of days to look back
            
        Returns:
            Dict with cycle time metrics
        """
        start_date = timezone.now() - timedelta(days=days)
        
        # Get completed stories
        completed_stories = await Story.objects.filter(
            project_id=project_id,
            status='done',
            updated_at__gte=start_date
        ).alist()
        
        if not completed_stories:
            return {
                "average_cycle_time_days": 0,
                "median_cycle_time_days": 0,
                "min_cycle_time_days": 0,
                "max_cycle_time_days": 0,
                "total_stories": 0
            }
        
        cycle_times = []
        for story in completed_stories:
            # Find when story was moved to 'in_progress' or 'todo'
            # Using EditHistory to find status changes
            history = await EditHistory.objects.filter(
                content_type__model='userstory',
                object_id=story.id,
                changed_fields__contains='status'
            ).order_by('created_at').afirst()
            
            if history:
                start_time = history.created_at
            else:
                start_time = story.created_at
            
            cycle_time = (story.updated_at - start_time).days
            cycle_times.append(cycle_time)
        
        cycle_times.sort()
        n = len(cycle_times)
        
        return {
            "average_cycle_time_days": round(sum(cycle_times) / n, 2) if n > 0 else 0,
            "median_cycle_time_days": cycle_times[n // 2] if n > 0 else 0,
            "min_cycle_time_days": min(cycle_times) if cycle_times else 0,
            "max_cycle_time_days": max(cycle_times) if cycle_times else 0,
            "total_stories": n,
            "cycle_time_distribution": {
                "0-3_days": len([t for t in cycle_times if t <= 3]),
                "4-7_days": len([t for t in cycle_times if 4 <= t <= 7]),
                "8-14_days": len([t for t in cycle_times if 8 <= t <= 14]),
                "15+_days": len([t for t in cycle_times if t > 14]),
            }
        }
    
    async def calculate_lead_time(
        self,
        project_id: str,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Calculate lead time (time from creation to completion) for stories.
        
        Args:
            project_id: Project UUID
            days: Number of days to look back
            
        Returns:
            Dict with lead time metrics
        """
        start_date = timezone.now() - timedelta(days=days)
        
        # Get completed stories
        completed_stories = await Story.objects.filter(
            project_id=project_id,
            status='done',
            updated_at__gte=start_date
        ).alist()
        
        if not completed_stories:
            return {
                "average_lead_time_days": 0,
                "median_lead_time_days": 0,
                "min_lead_time_days": 0,
                "max_lead_time_days": 0,
                "total_stories": 0
            }
        
        lead_times = []
        for story in completed_stories:
            lead_time = (story.updated_at - story.created_at).days
            lead_times.append(lead_time)
        
        lead_times.sort()
        n = len(lead_times)
        
        return {
            "average_lead_time_days": round(sum(lead_times) / n, 2) if n > 0 else 0,
            "median_lead_time_days": lead_times[n // 2] if n > 0 else 0,
            "min_lead_time_days": min(lead_times) if lead_times else 0,
            "max_lead_time_days": max(lead_times) if lead_times else 0,
            "total_stories": n
        }
    
    async def calculate_throughput(
        self,
        project_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate throughput (stories completed per time period).
        
        Args:
            project_id: Project UUID
            days: Number of days to analyze
            
        Returns:
            Dict with throughput metrics
        """
        start_date = timezone.now() - timedelta(days=days)
        
        # Get completed stories
        completed_stories = await Story.objects.filter(
            project_id=project_id,
            status='done',
            updated_at__gte=start_date
        ).alist()
        
        # Group by week
        weekly_throughput = {}
        for story in completed_stories:
            week_start = story.updated_at.date() - timedelta(days=story.updated_at.weekday())
            week_key = week_start.isoformat()
            weekly_throughput[week_key] = weekly_throughput.get(week_key, 0) + 1
        
        return {
            "total_completed": len(completed_stories),
            "average_per_week": round(len(completed_stories) / (days / 7), 2) if days > 0 else 0,
            "weekly_throughput": weekly_throughput,
            "period_days": days
        }
    
    async def calculate_project_health(
        self,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Calculate overall project health metrics.
        
        Args:
            project_id: Project UUID
            
        Returns:
            Dict with project health indicators
        """
        project = await Project.objects.aget(id=project_id)
        
        # Get all stories
        all_stories = await Story.objects.filter(project_id=project_id).alist()
        total_stories = len(all_stories)
        
        if total_stories == 0:
            return {
                "health_score": 0,
                "status": "no_data",
                "metrics": {}
            }
        
        # Count by status
        done_count = len([s for s in all_stories if s.status == 'done'])
        in_progress_count = len([s for s in all_stories if s.status == 'in_progress'])
        blocked_count = len([s for s in all_stories if 'blocked' in s.status.lower()])
        
        # Calculate completion rate
        completion_rate = (done_count / total_stories) * 100 if total_stories > 0 else 0
        
        # Calculate active work rate
        active_rate = (in_progress_count / total_stories) * 100 if total_stories > 0 else 0
        
        # Calculate health score (0-100)
        health_score = (
            completion_rate * 0.4 +  # Completion is 40%
            active_rate * 0.3 +  # Active work is 30%
            (100 - (blocked_count / total_stories * 100)) * 0.3 if total_stories > 0 else 0  # Low blockers is 30%
        )
        
        # Determine status
        if health_score >= 75:
            status = "healthy"
        elif health_score >= 50:
            status = "at_risk"
        else:
            status = "critical"
        
        return {
            "project_id": str(project_id),
            "health_score": round(health_score, 2),
            "status": status,
            "metrics": {
                "total_stories": total_stories,
                "completed": done_count,
                "in_progress": in_progress_count,
                "blocked": blocked_count,
                "completion_rate": round(completion_rate, 2),
                "active_rate": round(active_rate, 2)
            }
        }
    
    async def calculate_team_performance(
        self,
        project_id: str,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Calculate team performance metrics.
        
        Args:
            project_id: Project UUID
            days: Number of days to analyze
            
        Returns:
            Dict with team performance metrics
        """
        start_date = timezone.now() - timedelta(days=days)
        
        # Get completed work by assignee
        completed_stories = await Story.objects.filter(
            project_id=project_id,
            status='done',
            updated_at__gte=start_date,
            assigned_to__isnull=False
        ).select_related('assigned_to').alist()
        
        # Group by assignee
        assignee_stats = {}
        for story in completed_stories:
            assignee_id = str(story.assigned_to.id)
            if assignee_id not in assignee_stats:
                assignee_stats[assignee_id] = {
                    "user_id": assignee_id,
                    "user_name": f"{story.assigned_to.first_name} {story.assigned_to.last_name}".strip() or story.assigned_to.email,
                    "stories_completed": 0,
                    "story_points_completed": 0,
                    "tasks_completed": 0
                }
            
            assignee_stats[assignee_id]["stories_completed"] += 1
            assignee_stats[assignee_id]["story_points_completed"] += (story.story_points or 0)
        
        # Get completed tasks
        completed_tasks = await Task.objects.filter(
            story__project_id=project_id,
            status='done',
            updated_at__gte=start_date,
            assigned_to__isnull=False
        ).select_related('assigned_to').alist()
        
        for task in completed_tasks:
            assignee_id = str(task.assigned_to.id)
            if assignee_id not in assignee_stats:
                assignee_stats[assignee_id] = {
                    "user_id": assignee_id,
                    "user_name": f"{task.assigned_to.first_name} {task.assigned_to.last_name}".strip() or task.assigned_to.email,
                    "stories_completed": 0,
                    "story_points_completed": 0,
                    "tasks_completed": 0
                }
            assignee_stats[assignee_id]["tasks_completed"] += 1
        
        return {
            "period_days": days,
            "team_members": list(assignee_stats.values()),
            "total_team_members": len(assignee_stats)
        }


# Global instance
analytics = ProjectAnalytics()
