"""
Unit Tests for WorkflowParser

Tests schema validation, circular dependency detection, and step validation.
"""

import unittest
import json
from pathlib import Path
from apps.workflows.services.workflow_parser import (
    WorkflowParser,
    WorkflowParseError,
    ParsedWorkflow
)


class TestWorkflowParser(unittest.TestCase):
    """Test suite for WorkflowParser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = WorkflowParser()
    
    def test_parse_valid_workflow(self):
        """Test parsing a valid workflow definition."""
        definition = {
            "name": "Test Workflow",
            "version": "1.0",
            "description": "Test workflow",
            "steps": [
                {
                    "id": "step1",
                    "agent": "test-agent",
                    "on_success": "step2"
                },
                {
                    "id": "step2",
                    "agent": "test-agent"
                }
            ]
        }
        
        result = self.parser.parse(definition)
        
        self.assertIsInstance(result, ParsedWorkflow)
        self.assertEqual(result.name, "Test Workflow")
        self.assertEqual(len(result.steps), 2)
        self.assertEqual(result.entry_step.id, "step1")
    
    def test_parse_invalid_schema(self):
        """Test that invalid schema raises error."""
        definition = {
            "name": "Test",
            # Missing required 'version' and 'steps'
        }
        
        with self.assertRaises(WorkflowParseError) as context:
            self.parser.parse(definition)
        
        self.assertIn("Schema validation failed", str(context.exception))
    
    def test_detect_circular_dependencies(self):
        """Test circular dependency detection."""
        definition = {
            "name": "Circular Workflow",
            "version": "1.0",
            "steps": [
                {
                    "id": "step1",
                    "agent": "test-agent",
                    "on_success": "step2"
                },
                {
                    "id": "step2",
                    "agent": "test-agent",
                    "on_success": "step3"
                },
                {
                    "id": "step3",
                    "agent": "test-agent",
                    "on_success": "step1"  # Circular!
                }
            ]
        }
        
        with self.assertRaises(WorkflowParseError) as context:
            self.parser.parse(definition)
        
        self.assertIn("Circular dependency detected", str(context.exception))
    
    def test_invalid_step_reference(self):
        """Test invalid step reference detection."""
        definition = {
            "name": "Invalid Ref Workflow",
            "version": "1.0",
            "steps": [
                {
                    "id": "step1",
                    "agent": "test-agent",
                    "on_success": "nonexistent_step"  # Invalid!
                }
            ]
        }
        
        with self.assertRaises(WorkflowParseError) as context:
            self.parser.parse(definition)
        
        self.assertIn("non-existent step", str(context.exception))
    
    def test_duplicate_step_ids(self):
        """Test duplicate step ID detection."""
        definition = {
            "name": "Duplicate Workflow",
            "version": "1.0",
            "steps": [
                {
                    "id": "step1",
                    "agent": "test-agent"
                },
                {
                    "id": "step1",  # Duplicate!
                    "agent": "test-agent"
                }
            ]
        }
        
        with self.assertRaises(WorkflowParseError) as context:
            self.parser.parse(definition)
        
        self.assertIn("Duplicate step ID", str(context.exception))
    
    def test_get_execution_order(self):
        """Test topological sort execution order."""
        definition = {
            "name": "Ordered Workflow",
            "version": "1.0",
            "steps": [
                {
                    "id": "step1",
                    "agent": "test-agent",
                    "on_success": "step2"
                },
                {
                    "id": "step2",
                    "agent": "test-agent",
                    "on_success": "step3"
                },
                {
                    "id": "step3",
                    "agent": "test-agent"
                }
            ]
        }
        
        parsed = self.parser.parse(definition)
        order = self.parser.get_execution_order(parsed)
        
        self.assertEqual(order, ["step1", "step2", "step3"])


if __name__ == '__main__':
    unittest.main()
