"""
Tests for Sprint Planning Service

Tests AI-powered sprint planning and capacity calculation.
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from apps.projects.services.sprint_planner import sprint_planner
from apps.projects.models import Sprint, Story, Project


class TestSprintPlanning(unittest.TestCase):
    """Test suite for sprint planning."""
    
    @patch('apps.projects.models.Sprint.objects')
    @patch('apps.projects.models.Story.objects')
    @patch('apps.agents.models.Agent.objects')
    @patch('apps.agents.services.execution_engine.execution_engine')
    def test_plan_sprint(
        self,
        mock_exec_engine,
        mock_agent_qs,
        mock_story_qs,
        mock_sprint_qs
    ):
        """Test sprint planning with AI."""
        # Mock agent
        mock_agent = Mock()
        mock_agent.id = "scrum-agent-id"
        mock_agent_qs.aget = AsyncMock(return_value=mock_agent)
        
        # Mock sprint
        mock_sprint = Mock()
        mock_sprint.id = "sprint-id"
        mock_sprint_qs.aget = AsyncMock(return_value=mock_sprint)
        
        # Mock backlog stories
        backlog = [
            Mock(id="story-1", title="Story 1", story_points=5, priority=1),
            Mock(id="story-2", title="Story 2", story_points=3, priority=2),
            Mock(id="story-3", title="Story 3", story_points=8, priority=3)
        ]
        
        # Mock agent response
        mock_exec_engine.execute_agent = AsyncMock(return_value={
            'selected_stories': ["story-1", "story-2"],
            'total_points': 8,
            'daily_breakdown': {
                '1': ["story-1"],
                '2': ["story-2"]
            },
            'risks': [],
            'recommendations': ["Consider splitting story-3"]
        })
        
        # Mock story updates
        for story in backlog:
            story.asave = AsyncMock()
        
        mock_story_qs.aget = AsyncMock(side_effect=lambda id: next(s for s in backlog if s.id == id))
        
        # Execute
        result = asyncio.run(sprint_planner.plan_sprint(
            sprint_id="sprint-id",
            backlog_stories=backlog,
            team_velocity=10,
            constraints={'must_include': []}
        ))
        
        # Assertions
        self.assertEqual(len(result['selected_stories']), 2)
        self.assertEqual(result['total_points'], 8)
        self.assertLessEqual(result['total_points'], 10)  # Within capacity
    
    def test_calculate_sprint_capacity(self):
        """Test sprint capacity calculation."""
        result = asyncio.run(sprint_planner.calculate_sprint_capacity(
            sprint_id="sprint-id",
            team_size=5,
            sprint_days=10
        ))
        
        self.assertEqual(result['team_size'], 5)
        self.assertEqual(result['sprint_days'], 10)
        self.assertTrue(result['realistic_capacity'] > 0)
        self.assertLess(result['realistic_capacity'], result['theoretical_capacity'])


if __name__ == '__main__':
    unittest.main()
