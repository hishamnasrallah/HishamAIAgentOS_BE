"""
Unit Tests for ConditionalEvaluator

Tests safe condition evaluation with {{variable}} syntax.
"""

import unittest
from apps.workflows.services.conditional_evaluator import (
    ConditionalEvaluator,
    ConditionalEvaluationError
)


class TestConditionalEvaluator(unittest.TestCase):
    """Test suite for ConditionalEvaluator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = ConditionalEvaluator()
    
    def test_evaluate_simple_equality(self):
        """Test simple equality comparison."""
        context = {"input": {"priority": "high"}}
        result = self.evaluator.evaluate("{{input.priority}} == 'high'", context)
        self.assertTrue(result)
    
    def test_evaluate_numeric_comparison(self):
        """Test numeric comparisons."""
        context = {"steps": {"triage": {"output": {"severity": 5}}}}
        
        self.assertTrue(self.evaluator.evaluate("{{steps.triage.output.severity}} > 3", context))
        self.assertFalse(self.evaluator.evaluate("{{steps.triage.output.severity}} < 3", context))
        self.assertTrue(self.evaluator.evaluate("{{steps.triage.output.severity}} >= 5", context))
    
    def test_evaluate_boolean_logic(self):
        """Test boolean AND/OR/NOT operators."""
        context = {"input": {"value": 10}}
        
        # AND
        self.assertTrue(self.evaluator.evaluate("{{input.value}} > 5 and {{input.value}} < 15", context))
        self.assertFalse(self.evaluator.evaluate("{{input.value}} > 5 and {{input.value}} > 15", context))
        
        # OR
        self.assertTrue(self.evaluator.evaluate("{{input.value}} > 15 or {{input.value}} < 15", context))
    
    def test_evaluate_nested_access(self):
        """Test nested variable access."""
        context = {
            "steps": {
                "step1": {
                    "output": {
                        "nested": {
                            "value": 42
                        }
                    }
                }
            }
        }
        
        result = self.evaluator.evaluate("{{steps.step1.output.nested.value}} == 42", context)
        self.assertTrue(result)
    
    def test_undefined_variable_error(self):
        """Test error on undefined variable."""
        context = {"input": {}}
        
        with self.assertRaises(ConditionalEvaluationError):
            self.evaluator.evaluate("{{input.nonexistent}} == 5", context)
    
    def test_empty_condition(self):
        """Test empty condition returns True."""
        result = self.evaluator.evaluate("", {})
        self.assertTrue(result)
    
    def test_boolean_values(self):
        """Test boolean value evaluation."""
        context = {"input": {"flag": True}}
        
        self.assertTrue(self.evaluator.evaluate("{{input.flag}} == true", context))
        self.assertFalse(self.evaluator.evaluate("{{input.flag}} == false", context))


if __name__ == '__main__':
    unittest.main()
