"""
Tests for Story Generation Service

Tests AI-powered story generation from product vision.
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from apps.projects.services.story_generator import story_generator
from apps.projects.models import Story, Project, Epic


class TestStoryGeneration(unittest.TestCase):
    """Test suite for story generation."""
    
    @patch('apps.projects.models.Project.objects')
    @patch('apps.projects.models.Epic.objects')
    @patch('apps.projects.models.Story.objects')
    @patch('apps.agents.models.Agent.objects')
    @patch('apps.agents.services.execution_engine.execution_engine')
    def test_generate_stories_from_vision(
        self,
        mock_exec_engine,
        mock_agent_qs,
        mock_story_qs,
        mock_epic_qs,
        mock_project_qs
    ):
        """Test generating stories from product vision."""
        # Mock BA agent
        mock_agent = Mock()
        mock_agent.id = "ba-agent-id"
        mock_agent_qs.aget = AsyncMock(return_value=mock_agent)
        
        # Mock project and epic
        mock_project = Mock()
        mock_project.id = "project-id"
        mock_project_qs.aget = AsyncMock(return_value=mock_project)
        
        mock_epic = Mock()
        mock_epic.id = "epic-id"
        mock_epic_qs.aget = AsyncMock(return_value=mock_epic)
        
        # Mock agent execution response
        mock_exec_engine.execute_agent = AsyncMock(return_value={
            'stories': [
                {
                    'title': 'As a user I want to login',
                    'description': 'User login functionality',
                    'acceptance_criteria': ['Form validation', 'Error handling'],
                    'story_points': 3
                },
                {
                    'title': 'As a user I want to register',
                    'description': 'User registration',
                    'acceptance_criteria': ['Email validation', 'Password strength'],
                    'story_points': 5
                }
            ]
        })
        
        # Mock story creation
        created_stories = []
        
        async def mock_create(**kwargs):
            mock_story = Mock()
            mock_story.id = f"story-{len(created_stories)}"
            mock_story.title = kwargs['title']
            for k, v in kwargs.items():
                setattr(mock_story, k, v)
            created_stories.append(mock_story)
            return mock_story
        
        mock_story_qs.acreate = mock_create
        
        # Execute
        vision = "Build e-commerce platform for artisan coffee"
        stories = asyncio.run(story_generator.generate_stories(
            product_vision=vision,
            context={'target_users': 'coffee enthusiasts'},
            project_id="project-id",
            epic_id="epic-id"
        ))
        
        # Assertions
        self.assertEqual(len(stories), 2)
        self.assertIn('login', stories[0].title.lower())
        self.assertEqual(stories[0].story_points, 3)
        self.assertTrue(len(stories[0].acceptance_criteria) > 0)
    
    @patch('apps.projects.models.Story.objects')
    @patch('apps.agents.models.Agent.objects')
    @patch('apps.agents.services.execution_engine.execution_engine')
    def test_validate_story(
        self,
        mock_exec_engine,
        mock_agent_qs,
        mock_story_qs
    ):
        """Test story validation against INVEST criteria."""
        # Mock agent
        mock_agent = Mock()
        mock_agent.id = "ba-agent-id"
        mock_agent_qs.aget = AsyncMock(return_value=mock_agent)
        
        # Mock story
        mock_story = Mock()
        mock_story.title = "As a user I want to login"
        mock_story.description = "User authentication"
        mock_story.acceptance_criteria = ["Valid credentials work", "Invalid credentials fail"]
        
        # Mock validation response
        mock_exec_engine.execute_agent = AsyncMock(return_value={
            'score': 85,
            'issues': [],
            'suggestions': ['Consider adding password reset flow']
        })
        
        # Execute
        result = asyncio.run(story_generator.validate_story(mock_story))
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertEqual(result['score'], 85)
        self.assertIsInstance(result['suggestions'], list)


if __name__ == '__main__':
    unittest.main()
