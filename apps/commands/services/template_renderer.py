"""
Template rendering service for command templates.

Renders command templates with user-provided parameters using Jinja2-style syntax.
"""

import re
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Renders command templates with parameter substitution."""
    
    # Simple pattern for {{variable}} syntax
    VARIABLE_PATTERN = re.compile(r'\{\{(\w+)\}\}')
    
    # Pattern for conditional blocks {{#if variable}}...{{/if}}
    CONDITIONAL_PATTERN = re.compile(
        r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}',
        re.DOTALL
    )
    
    def render(self, template: str, parameters: Dict[str, Any]) -> str:
        """
        Render template with parameters.
        
        Supports:
        - Simple variable substitution: {{variable_name}}
        - Conditional blocks: {{#if variable}}content{{/if}}
        
        Args:
            template: Template string with placeholders
            parameters: Dictionary of parameter values
            
        Returns:
            Rendered template string
        """
        rendered = template
        
        # First, handle conditional blocks
        rendered = self._render_conditionals(rendered, parameters)
        
        # Then, handle simple variable substitution
        rendered = self._render_variables(rendered, parameters)
        
        return rendered
    
    def _render_conditionals(self, template: str, parameters: Dict[str, Any]) -> str:
        """Render conditional blocks."""
        def replace_conditional(match):
            var_name = match.group(1)
            content = match.group(2)
            
            # Check if variable exists and is truthy
            if var_name in parameters and parameters[var_name]:
                return content
            else:
                return ''
        
        return self.CONDITIONAL_PATTERN.sub(replace_conditional, template)
    
    def _render_variables(self, template: str, parameters: Dict[str, Any]) -> str:
        """Render simple variable substitutions."""
        def replace_variable(match):
            var_name = match.group(1)
            
            if var_name in parameters:
                value = parameters[var_name]
                # Convert to string, handling various types
                if isinstance(value, (list, dict)):
                    # For complex types, format nicely
                    if isinstance(value, list):
                        return '\n'.join(f"- {item}" for item in value)
                    else:
                        return '\n'.join(f"- {k}: {v}" for k, v in value.items())
                else:
                    return str(value)
            else:
                # Leave placeholder as-is if parameter not provided
                logger.warning(f"Parameter '{var_name}' not provided for template rendering")
                return match.group(0)
        
        return self.VARIABLE_PATTERN.sub(replace_variable, template)
    
    def extract_variables(self, template: str) -> set:
        """Extract all variable names from template."""
        variables = set()
        
        # Extract from simple variables
        for match in self.VARIABLE_PATTERN.finditer(template):
            variables.add(match.group(1))
        
        # Extract from conditionals
        for match in self.CONDITIONAL_PATTERN.finditer(template):
            variables.add(match.group(1))
        
        return variables
    
    def validate_template(self, template: str) -> tuple[bool, list[str]]:
        """
        Validate template syntax.
        
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        # Check for unmatched conditional blocks
        open_ifs = len(re.findall(r'\{\{#if\s+\w+\}\}', template))
        close_ifs = len(re.findall(r'\{\{/if\}\}', template))
        
        if open_ifs != close_ifs:
            errors.append(
                f"Unmatched conditional blocks: {open_ifs} opening tags, "
                f"{close_ifs} closing tags"
            )
        
        # Check for valid variable names (alphanumeric + underscore)
        invalid_vars = re.findall(r'\{\{([^\w\s#/]+)\}\}', template)
        if invalid_vars:
            errors.append(
                f"Invalid variable names: {', '.join(invalid_vars)}. "
                "Variable names must be alphanumeric with underscores only."
            )
        
        return len(errors) == 0, errors
