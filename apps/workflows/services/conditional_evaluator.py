"""
Conditional Evaluator Service

Safely evaluates conditions in workflow definitions.
Supports {{variable}} syntax and boolean logic.
"""

import re
from typing import Dict, Any, Optional
import operator


class ConditionalEvaluationError(Exception):
    """Raised when condition evaluation fails."""
    pass


class ConditionalEvaluator:
    """
    Evaluate workflow conditions safely.
    
    Supports:
    - {{variable}} syntax for accessing context variables
    - Comparison operators: ==, !=, >, <, >=, <=
    - Boolean operators: and, or, not
    - Nested variable access: {{steps.triage.output.severity}}
    
    Security:
    - No eval() or exec() - uses safe expression parsing
    - Only allows whitelisted operations
    - No arbitrary code execution
    """
    
    # Whitelisted operators
    OPERATORS = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
    }
    
    def __init__(self):
        # Pattern to match {{variable}} syntax
        self.variable_pattern = re.compile(r'\{\{([^}]+)\}\}')
    
    def evaluate(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition string against acontext.
        
        Args:
            condition: Condition string (e.g., "{{steps.triage.output.severity}} > 3")
            context: Context dictionary with variables
            
        Returns:
            Boolean result of condition evaluation
            
        Raises:
            ConditionalEvaluationError: If evaluation fails
            
        Examples:
            >>> evaluator = ConditionalEvaluator()
            >>> context = {'input': {'priority': 'high'}}
            >>> evaluator.evaluate("{{input.priority}} == 'high'", context)
            True
        """
        if not condition or not condition.strip():
            return True  # Empty condition = always true
        
        try:
            # Step 1: Replace all {{variable}} references with their values
            resolved_condition = self._resolve_variables(condition, context)
            
            # Step 2: Parse and evaluate the expression
            result = self._evaluate_expression(resolved_condition)
            
            return bool(result)
            
        except Exception as e:
            raise ConditionalEvaluationError(
                f"Failed to evaluate condition '{condition}': {str(e)}"
            )
    
    def _resolve_variables(self, condition: str, context: Dict[str, Any]) -> str:
        """
        Replace {{variable}} references with actual values.
        
        Args:
            condition: Condition with {{variable}} placeholders
            context: Context with variable values
            
        Returns:
            Condition with variables replaced
        """
        def replace_variable(match):
            var_path = match.group(1).strip()
            value = self._get_nested_value(context, var_path)
            
            # Convert value to string representation for comparison
            if isinstance(value, str):
                return f"'{value}'"  # Quote strings
            elif value is None:
                return 'None'
            elif isinstance(value, bool):
                return str(value)
            else:
                return str(value)
        
        return self.variable_pattern.sub(replace_variable, condition)
    
    def _get_nested_value(self, context: Dict[str, Any], path: str) -> Any:
        """
        Get nested value from context using dot notation.
        
        Args:
            context: Context dictionary
            path: Dot-separated path (e.g., "steps.triage.output.severity")
            
        Returns:
            Value at the path
            
        Raises:
            KeyError: If path doesn't exist
        """
        parts = path.split('.')
        value = context
        current_path = []
        
        for part in parts:
            current_path.append(part)
            current_path_str = '.'.join(current_path)
            
            if value is None:
                raise KeyError(f"Value is None at '{current_path_str}' in path {path}")
            
            if isinstance(value, dict):
                if part not in value:
                    raise KeyError(f"Key '{part}' not found in path {path} (at {current_path_str})")
                value = value[part]
            elif isinstance(value, (list, tuple)):
                # Try to access list by index
                try:
                    index = int(part)
                    if 0 <= index < len(value):
                        value = value[index]
                    else:
                        raise KeyError(f"Index {index} out of range for list at {current_path_str} in path {path}")
                except ValueError:
                    raise KeyError(f"Cannot access '{part}' in list/tuple value at {current_path_str} in path {path}")
            else:
                # Value is not a dict or list - provide more helpful error message
                value_type = type(value).__name__
                raise KeyError(
                    f"Cannot access '{part}' in non-dict value (type: {value_type}, value: {repr(value)}) "
                    f"at {current_path_str} in path {path}"
                )
        
        return value
    
    def _evaluate_expression(self, expression: str) -> bool:
        """
        Safely evaluate a boolean expression.
        
        Args:
            expression: Expression to evaluate (variables already resolved)
            
        Returns:
            Boolean result
            
        Examples:
            >>> _evaluate_expression("5 > 3")
            True
            >>> _evaluate_expression("'high' == 'high'")
            True
        """
        # Handle simple boolean values
        expression = expression.strip()
        if expression in ('True', 'true'):
            return True
        if expression in ('False', 'false'):
            return False
        
        # Parse comparison expressions
        for op_str, op_func in self.OPERATORS.items():
            if op_str in expression:
                left, right = expression.split(op_str, 1)
                left_val = self._parse_value(left.strip())
                right_val = self._parse_value(right.strip())
                return op_func(left_val, right_val)
        
        # Handle boolean expressions (and, or, not)
        if ' and ' in expression:
            parts = expression.split(' and ')
            return all(self._evaluate_expression(part) for part in parts)
        
        if ' or ' in expression:
            parts = expression.split(' or ')
            return any(self._evaluate_expression(part) for part in parts)
        
        if expression.startswith('not '):
            return not self._evaluate_expression(expression[4:])
        
        # Try to parse as single value
        value = self._parse_value(expression)
        return bool(value)
    
    def _parse_value(self, value_str: str) -> Any:
        """
        Parse a value string to its Python type.
        
        Args:
            value_str: String representation of a value
            
        Returns:
            Parsed value (int, float, str, bool, or None)
        """
        value_str = value_str.strip()
        
        # None
        if value_str == 'None':
            return None
        
        # Boolean (handle both capitalized and lowercase)
        if value_str in ('True', 'true'):
            return True
        if value_str in ('False', 'false'):
            return False
        
        # String (quoted)
        if value_str.startswith("'") and value_str.endswith("'"):
            return value_str[1:-1]
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]
        
        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        # Default: treat as string
        return value_str


# Global instance
conditional_evaluator = ConditionalEvaluator()
