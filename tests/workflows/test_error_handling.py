"""
Tests for Error Handling and Retry Logic

Tests workflow behavior under failure conditions.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from apps.workflows.services.workflow_executor import workflow_executor


class TestWorkflowErrorHandling(unittest.TestCase):
    """Test suite for workflow error handling and retry."""
    
    @patch('apps.workflows.models.Workflow.objects')
    @patch('apps.workflows.models.WorkflowExecution.objects')
    @patch('apps.workflows.services.workflow_executor.execution_engine')
    def test_retry_on_failure(self, mock_execution_engine, mock_execution_qs, mock_workflow_qs):
        """Test retry mechanism on step failure."""
        # Mock workflow with retry
        mock_workflow = Mock()
        mock_workflow.id = "test-workflow-id"
        mock_workflow.definition = {
            "name": "Retry Workflow",
            "version": "1.0",
            "steps": [
                {
                    "id": "flaky_step",
                    "agent": "Test Agent",
                    "inputs": {},
                    "max_retries": 3
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
        
        # Mock agent execution - fail twice, succeed third time
        mock_execution_engine.execute_agent = AsyncMock(side_effect=[
            Exception("First failure"),
            Exception("Second failure"),
            {"success": True}  # Success on third attempt
        ])
        
        # Execute workflow
        result = asyncio.run(workflow_executor.execute(
            workflow_id=str(mock_workflow.id),
            input_data={}
        ))
        
        # Should have retried 3 times
        self.assertEqual(mock_execution_engine.execute_agent.call_count, 3)
        self.assertTrue(result['success'])
    
    @patch('apps.workflows.models.Workflow.objects')
    @patch('apps.workflows.models.WorkflowExecution.objects')
    @patch('apps.workflows.services.workflow_executor.execution_engine')
    def test_timeout_handling(self, mock_execution_engine, mock_execution_qs, mock_workflow_qs):
        """Test timeout handling."""
        # Mock workflow with short timeout
        mock_workflow = Mock()
        mock_workflow.id = "test-workflow-id"
        mock_workflow.definition = {
            "name": "Timeout Workflow",
            "version": "1.0",
            "steps": [
                {
                    "id": "slow_step",
                    "agent": "Test Agent",
                    "inputs": {},
                    "timeout_seconds": 1,
                    "max_retries": 0
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
        
        # Mock agent execution - sleep longer than timeout
        async def slow_execution(*args, **kwargs):
            await asyncio.sleep(5)  # Longer than timeout
            return {}
        
        mock_execution_engine.execute_agent = slow_execution
        
        # Execute workflow - should timeout
        with self.assertRaises(Exception) as context:
            asyncio.run(workflow_executor.execute(
                workflow_id=str(mock_workflow.id),
                input_data={}
            ))
        
        self.assertIn("timed out", str(context.exception).lower())


if __name__ == '__main__':
    unittest.main()
