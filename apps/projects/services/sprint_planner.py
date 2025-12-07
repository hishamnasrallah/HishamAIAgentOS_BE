"""
Sprint Planner Service

AI-powered sprint planning with intelligent story distribution.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from apps.projects.models import Sprint, Story, Project
from apps.agents.models import Agent
from apps.agents.services.execution_engine import execution_engine


class SprintPlanner:
    """
    AI-powered sprint planning.
    
    Analyzes backlog, team capacity, and story dependencies to create
    optimized sprint plans.
    """
    
    async def plan_sprint(
        self,
        sprint_id: str,
        backlog_stories: List[Story],
        team_velocity: int,
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create optimized sprint plan.
        
        Args:
            sprint_id: Sprint UUID
            backlog_stories: Available stories in backlog
            team_velocity: Team's average velocity (story points per sprint)
            constraints: Optional constraints (dependencies, priorities, etc.)
            
        Returns:
            Dict with planned stories and sprint schedule
        """
        # Get Scrum Master agent for planning
        scrum_agent = await Agent.objects.aget(name="Scrum Master Agent")
        
        # Prepare story data for agent
        story_data = self._prepare_story_data(backlog_stories)
        
        task_description = f"""
        Plan a sprint with the following parameters:
        
        Team Velocity: {team_velocity} story points
        Available Stories: {len(backlog_stories)} stories
        
        Story Details:
        {story_data}
        
        Constraints:
        {self._format_constraints(constraints)}
        
        Create an optimized sprint plan that:
        1. Maximizes value delivery
        2. Respects team capacity ({team_velocity} points)
        3. Considers dependencies
        4. Balances story types
        
        Return JSON: {{
            "selected_stories": [story_ids],
            "total_points": X,
            "daily_breakdown": {{day: [story_ids]}},
            "risks": [...],
            "recommendations": [...]
        }}
        """
        
        result = await execution_engine.execute_agent(
            agent_id=str(scrum_agent.id),
            task_description=task_description,
            context={"constraints": constraints or {}}
        )
        
        # Update sprint with selected stories
        await self._assign_stories_to_sprint(sprint_id, result['selected_stories'])
        
        return result
    
    def _prepare_story_data(self, stories: List[Story]) -> str:
        """Format stories for agent consumption."""
        formatted = []
        for story in stories:
            formatted.append(
                f"ID: {story.id} | Title: {story.title} | "
                f"Points: {story.story_points} | Priority: {story.priority}"
            )
        return "\n".join(formatted)
    
    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format constraints."""
        if not constraints:
            return "No specific constraints"
        
        formatted = []
        for key, value in constraints.items():
            formatted.append(f"- {key}: {value}")
        return "\n".join(formatted)
    
    async def _assign_stories_to_sprint(self, sprint_id: str, story_ids: List[str]):
        """Assign selected stories to sprint."""
        sprint = await Sprint.objects.aget(id=sprint_id)
        
        for story_id in story_ids:
            story = await Story.objects.aget(id=story_id)
            story.sprint = sprint
            story.status = 'planned'
            await story.asave()
    
    async def calculate_sprint_capacity(
        self,
        sprint_id: str,
        team_size: int,
        sprint_days: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate sprint capacity based on team size and availability.
        
        Args:
            sprint_id: Sprint UUID
            team_size: Number of team members
            sprint_days: Sprint duration in working days
            
        Returns:
            Dict with capacity metrics
        """
        # Typical capacity per person per day: 6 hours
        # Typical story point to hours ratio: 1 point = 4 hours
        hours_per_day_per_person = 6
        hours_per_point = 4
        
        total_hours = team_size * sprint_days * hours_per_day_per_person
        total_capacity_points = total_hours / hours_per_point
        
        # Apply 80% factor for meetings, interruptions, etc.
        realistic_capacity = total_capacity_points * 0.8
        
        return {
            "team_size": team_size,
            "sprint_days": sprint_days,
            "total_hours": total_hours,
            "theoretical_capacity": total_capacity_points,
            "realistic_capacity": int(realistic_capacity),
            "hours_per_point": hours_per_point
        }


# Global instance
sprint_planner = SprintPlanner()
