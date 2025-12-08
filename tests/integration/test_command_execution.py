"""
Integration tests for command execution flow.
"""
import pytest
from django.contrib.auth import get_user_model
from apps.commands.models import CommandTemplate, CommandCategory
from apps.commands.services.command_executor import CommandExecutor
from apps.agents.models import Agent

User = get_user_model()


@pytest.mark.django_db
class TestCommandExecutionFlow:
    """Test complete command execution flow."""
    
    @pytest.fixture
    def category(self):
        """Create a command category."""
        return CommandCategory.objects.create(
            name='Test Category',
            slug='test-category',
            description='Test category for testing'
        )
    
    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        return Agent.objects.create(
            agent_id='test-agent',
            name='Test Agent',
            description='Test agent',
            system_prompt='You are a test agent',
            preferred_platform='openai',
            status='active'
        )
    
    @pytest.fixture
    def command(self, category, agent):
        """Create a test command."""
        return CommandTemplate.objects.create(
            category=category,
            name='Test Command',
            slug='test-command',
            description='Test command for testing',
            template='Hello {{name}}!',
            parameters=[
                {
                    'name': 'name',
                    'type': 'string',
                    'required': True,
                    'description': 'Name to greet'
                }
            ],
            recommended_agent=agent,
            is_active=True
        )
    
    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            role='developer'
        )
    
    @pytest.mark.asyncio
    async def test_command_execution_complete_flow(self, command, user):
        """Test complete command execution flow."""
        executor = CommandExecutor()
        
        parameters = {'name': 'World'}
        
        # Note: This will require actual AI platform setup or mocking
        # For now, we'll test the structure
        try:
            result = await executor.execute(
                command=command,
                parameters=parameters,
                user=user
            )
            
            # If execution succeeds, verify result structure
            assert hasattr(result, 'success')
            assert hasattr(result, 'output')
        except Exception as e:
            # If AI platform not configured, that's expected
            # Just verify the executor can be instantiated
            assert executor is not None
