"""
Story Generator Service

AI-powered user story generation from product vision using Business Analyst agent.
"""

from typing import List, Dict, Any
from apps.agents.models import Agent
from apps.agents.services.execution_engine import execution_engine
from apps.projects.models import UserStory, Epic, Project
# Alias for backward compatibility
Story = UserStory


class StoryGenerator:
    """
    Generate user stories from product ideas using AI.
    
    Leverages Business Analyst agent to convert high-level product vision
    into concrete, actionable user stories with acceptance criteria.
    """
    
    async def generate_stories(
        self,
        product_vision: str,
        context: Dict[str, Any],
        project_id: str,
        epic_id: str = None
    ) -> List[Story]:
        """
        Generate user stories from product vision.
        
        Args:
            product_vision: High-level product description or feature idea
            context: Additional context (target users, constraints, etc.)
            project_id: Project UUID
            epic_id: Optional epic to associate stories with
            
        Returns:
            List of generated Story objects
        """
        # Get Business Analyst agent
        ba_agent = await Agent.objects.aget(name="Business Analyst Agent")
        
        # Prepare prompt for BA agent
        task_description = f"""
        Generate 5-10 user stories for the following product vision:
        
        Product Vision: {product_vision}
        
        Additional Context:
        {self._format_context(context)}
        
        For each story, provide:
        1. Story title (As a [user], I want [goal], so that [benefit])
        2. Description
        3. Acceptance criteria (3-5 specific, testable criteria)
        4. Estimated story points (1, 2, 3, 5, 8, 13, 21)
        
        Return as JSON array with format:
        [{{
            "title": "...",
            "description": "...",
            "acceptance_criteria": ["criterion1", "criterion2", ...],
            "story_points": X
        }}, ...]
        """
        
        # Execute BA agent
        result = await execution_engine.execute_agent(
            agent_id=str(ba_agent.id),
            task_description=task_description,
            context=context
        )
        
        # Parse result and create Story objects
        stories = []
        
        if isinstance(result, dict) and 'stories' in result:
            story_data_list = result['stories']
        elif isinstance(result, list):
            story_data_list = result
        else:
            # Try to parse from text
            import json
            story_data_list = json.loads(result)
        
        # Get project and epic
        project = await Project.objects.aget(id=project_id)
        epic = await Epic.objects.aget(id=epic_id) if epic_id else None
        
        for story_data in story_data_list:
            story = await Story.objects.acreate(
                project=project,
                epic=epic,
                title=story_data['title'],
                description=story_data.get('description', ''),
                acceptance_criteria=story_data.get('acceptance_criteria', []),
                story_points=story_data.get('story_points', 3),
                status='backlog',
                # AI-specific fields
                generated_by=ba_agent,
                ai_confidence=0.8,  # Could be calculated from agent response
                assigned_to_ai=False  # Default, can be changed later
            )
            stories.append(story)
        
        return stories
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dict into readable string."""
        formatted = []
        for key, value in context.items():
            formatted.append(f"- {key}: {value}")
        return "\n".join(formatted) if formatted else "No additional context provided."
    
    async def validate_story(self, story: Story) -> Dict[str, Any]:
        """
        Validate a story using AI.
        
        Checks if story meets INVEST criteria:
        - Independent
        - Negotiable
        - Valuable
        - Estimable
        - Small
        - Testable
        
        Returns:
            Dict with validation results and suggestions
        """
        ba_agent = await Agent.objects.aget(name="Business Analyst Agent")
        
        task_description = f"""
        Validate the following user story against INVEST criteria:
        
        Title: {story.title}
        Description: {story.description}
        Acceptance Criteria: {story.acceptance_criteria}
        
        Return validation results with:
        1. Overall score (0-100)
        2. Issues found
        3. Suggestions for improvement
        
        Format as JSON: {{"score": X, "issues": [...], "suggestions": [...]}}
        """
        
        result = await execution_engine.execute_agent(
            agent_id=str(ba_agent.id),
            task_description=task_description,
            context={}
        )
        
        return result


# Global instance
story_generator = StoryGenerator()
