"""
Estimation Engine Service

AI-powered story point estimation using historical data and complexity analysis.
"""

from typing import Dict, Any, List
from apps.projects.models import Story, Project
from apps.agents.models import Agent
from apps.agents.services.execution_engine import execution_engine


class EstimationEngine:
    """
    AI-powered story point estimation.
    
    Uses historical data, complexity analysis, and AI judgment to estimate
    story points with confidence scores.
    """
    
    async def estimate_story(
        self,
        story: Story,
        use_historical: bool = True
    ) -> Dict[str, Any]:
        """
        Estimate story points for a story.
        
        Args:
            story: Story to estimate
            use_historical: Whether to use historical data for estimation
            
        Returns:
            Dict with estimated_points, confidence, rationale
        """
        # Get Business Analyst agent for estimation
        ba_agent = await Agent.objects.aget(name="Business Analyst Agent")
        
        # Get historical data if requested
        historical_context = ""
        if use_historical:
            similar_stories = await self._find_similar_stories(story)
            historical_context = self._format_historical_data(similar_stories)
        
        task_description = f"""
        Estimate story points for the following user story:
        
        Title: {story.title}
        Description: {story.description}
        Acceptance Criteria:
        {self._format_criteria(story.acceptance_criteria)}
        
        Historical Context (similar completed stories):
        {historical_context}
        
        Provide estimation using Fibonacci sequence: 1, 2, 3, 5, 8, 13, 21
        
        Consider:
        1. Complexity of implementation
        2. Amount of work required
        3. Uncertainty/risk
        4. Dependencies
        
        Return JSON: {{
            "estimated_points": X,
            "confidence": 0.0-1.0,
            "rationale": "explanation",
            "complexity_factors": ["factor1", "factor2", ...],
            "risks": [...]
        }}
        """
        
        result = await execution_engine.execute_agent(
            agent_id=str(ba_agent.id),
            task_description=task_description,
            context={"historical_stories": historical_context}
        )
        
        # Update story with estimation
        story.estimated_points = result['estimated_points']
        story.ai_confidence = result.get('confidence', 0.7)
        await story.asave()
        
        return result
    
    async def _find_similar_stories(self, story: Story, limit: int = 5) -> List[Story]:
        """
        Find similar completed stories for comparison.
        
        Uses simple keyword matching. In production, could use embeddings.
        """
        # Get completed stories from same project
        completed = await Story.objects.filter(
            project=story.project,
            status='done',
            actual_points__isnull=False
        ).order_by('-created_at')[:limit].alist()
        
        return list(completed)
    
    def _format_historical_data(self, stories: List[Story]) -> str:
        """Format historical stories for agent."""
        if not stories:
            return "No historical data available"
        
        formatted = []
        for s in stories:
            formatted.append(
                f"- {s.title[:50]}... | "
                f"Estimated: {s.estimated_points} | "
                f"Actual: {s.actual_points} points"
            )
        return "\n".join(formatted)
    
    def _format_criteria(self, criteria: List[str]) -> str:
        """Format acceptance criteria."""
        if not criteria:
            return "No acceptance criteria specified"
        
        return "\n".join([f"- {c}" for c in criteria])
    
    async def batch_estimate(
        self,
        stories: List[Story]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Estimate multiple stories in batch.
        
        More efficient than individual estimation.
        
        Args:
            stories: List of stories to estimate
            
        Returns:
            Dict mapping story ID to estimation results
        """
        results = {}
        
        for story in stories:
            estimation = await self.estimate_story(story)
            results[str(story.id)] = estimation
        
        return results
    
    async def calculate_estimation_accuracy(
        self,
        project_id: str
    ) -> Dict[str, Any]:
        """
        Calculate estimation accuracy for completed stories.
        
        Args:
            project_id: Project UUID
            
        Returns:
            Dict with accuracy metrics
        """
        # Get completed stories with both estimated and actual points
        stories = await Story.objects.filter(
            project_id=project_id,
            status='done',
            estimated_points__isnull=False,
            actual_points__isnull=False
        ).alist()
        
        stories_list = list(stories)
        
        if not stories_list:
            return {
                "accuracy": 0,
                "total_stories": 0,
                "average_error": 0
            }
        
        total_error = 0
        exact_matches = 0
        
        for story in stories_list:
            error = abs(story.estimated_points - story.actual_points)
            total_error += error
            
            if story.estimated_points == story.actual_points:
                exact_matches += 1
        
        avg_error = total_error / len(stories_list)
        accuracy = (exact_matches / len(stories_list)) * 100
        
        return {
            "accuracy": round(accuracy, 2),
            "total_stories": len(stories_list),
            "exact_matches": exact_matches,
            "average_error": round(avg_error, 2)
        }


# Global instance
estimation_engine = EstimationEngine()
