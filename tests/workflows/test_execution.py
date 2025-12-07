"""
Integration Tests for Workflow Execution

Tests complete workflow execution end-to-end.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from apps.workflows.services.workflow_executor import workflow_executor
from apps.workflows.models import Workflow, WorkflowExecution


class TestWorkflowExecution(unittest.TestCase):
    """Integration tests for workflow execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workflow_definition = {
            "name": "Test Bug Lifecycle",
            "version": "1.0",
            "steps": [
                {
                    "id": "triage",
                    "agent": "Bug Triage Agent",
                    "inputs": {
                        "bug_description": "{{input.bug_description}}"
                    },
                    "on_success": "assign"
                },
                {
                    "id": "assign",
                    "agent": "Project Manager Agent",
                    "inputs": {
                        "bug_info": "{{steps.triage.output}}"
                    },
                    "condition": "{{steps.triage.output.severity}} > 2"
                }
            ]
        }
    
    @patch('apps.workflows.models.Workflow.objects')
    @patch('apps.workflows.models.WorkflowExecution.objects')
    @patch('apps.workflows.services.workflow_executor.execution_engine')
    def test_successful_workflow_execution(self, mock_execution_engine, mock_execution_qs, mock_workflow_qs):
        """Test successful complete workflow execution."""
        # Mock workflow
        mock_workflow = Mock()
        mock_workflow.id = "test-workflow-id"
        mock_workflow.definition = self.workflow_definition
        mock_workflow.execution_count = 0
        mock_workflow.asave = AsyncMock()
        mock_workflow_qs.aget = AsyncMock(return_value=mock_workflow)
        
        # Mock execution
        mock_execution = Mock()
        mock_execution.id = "test-execution-id"
        mock_execution_qs.acreate = AsyncMock(return_value=mock_execution)
        
        # Mock agent execution
        mock_execution_engine.execute_agent = AsyncMock(side_effect=[
            {"severity": 5, "description": "Critical bug"},  # Triage output
            {"developer": "john_doe", "assigned": True}  # Assign output
        ])
        
        # Execute workflow
        input_data = {"bug_description": "Critical production bug"}
        result = asyncio.run(workflow_executor.execute(
            workflow_id=str(mock_workflow.id),
            input_data=input_data
        ))
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['output'])
        self.assertEqual(mock_execution_engine.execute_agent.call_count, 2)
    
    @patch('apps.workflows.models.Workflow.objects')
    @patch('apps.workflows.models.WorkflowExecution.objects')
    @patch('apps.workflows.services.workflow_executor.execution_engine')
    def test_workflow_with_conditional_skip(self, mock_execution_engine, mock_execution_qs, mock_workflow_qs):
        """Test workflow with step skipped due to condition."""
        # Mock workflow with condition
        mock_workflow = Mock()
        mock_workflow.id = "test-workflow-id"
        mock_workflow.definition = {
            "name": "Conditional Workflow",
            "version": "1.0",
            "steps": [
                {
                    "id": "check",
                    "agent": "Test Agent",
                    "inputs": {},
                    "on_success": "action"
                },
                {
                    "id": "action",
                    "agent": "Test Agent",
                    "inputs": {},
                    "condition": "{{steps.check.output.should_continue}} == true"
                }
            ]
        }
        mock_workflow.execution_count = 0
        mock_workflow.asave = AsyncMock()
        mock_workflow_qs.aget = AsyncMock(return_value=mock_workflow)
        
        # Mock execution
        mock_execution = Mock()
        mock_execution.id = "test-execution-id"
        mock_execution_qs.acreate = AsyncMock(return_value=mock_execution)
        
        # Mock agent execution - check returns false
        mock_execution_engine.execute_agent = AsyncMock(return_value={
            "should_continue": False
        })
        
        # Execute workflow
        result = asyncio.run(workflow_executor.execute(
            workflow_id=str(mock_workflow.id),
            input_data={}
        ))
        
        # Should execute only first step
        self.assertEqual(mock_execution_engine.execute_agent.call_count, 1)
    
    def tearDown(self):
        """Clean up after tests."""
        pass


if __name__ == '__main__':
    unittest.main()
