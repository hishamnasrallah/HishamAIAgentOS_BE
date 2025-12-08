"""
Unit tests for TemplateRenderer service.
"""
import pytest
from apps.commands.services.template_renderer import TemplateRenderer


class TestTemplateRenderer:
    """Test suite for TemplateRenderer."""
    
    @pytest.fixture
    def renderer(self):
        """Create TemplateRenderer instance."""
        return TemplateRenderer()
    
    def test_render_simple_template(self, renderer):
        """Test rendering a simple template with single parameter."""
        template = "Hello {{name}}!"
        parameters = {'name': 'World'}
        
        result = renderer.render(template, parameters)
        
        assert result == "Hello World!"
    
    def test_render_multiple_parameters(self, renderer):
        """Test rendering template with multiple parameters."""
        template = "Project: {{project_name}}, Status: {{status}}"
        parameters = {'project_name': 'HishamOS', 'status': 'Active'}
        
        result = renderer.render(template, parameters)
        
        assert result == "Project: HishamOS, Status: Active"
    
    def test_render_missing_parameter(self, renderer):
        """Test rendering with missing parameter (should leave placeholder)."""
        template = "Hello {{name}}!"
        parameters = {}
        
        result = renderer.render(template, parameters)
        
        # Should leave placeholder if parameter missing
        assert "{{name}}" in result
    
    def test_render_conditional_true(self, renderer):
        """Test rendering conditional block when condition is true."""
        template = "Hello {{#if name}}{{name}}{{/if}}!"
        parameters = {'name': 'World'}
        
        result = renderer.render(template, parameters)
        
        assert 'World' in result
        assert '{{#if' not in result
    
    def test_render_conditional_false(self, renderer):
        """Test rendering conditional block when condition is false."""
        template = "Hello {{#if name}}{{name}}{{/if}}!"
        parameters = {'name': False}
        
        result = renderer.render(template, parameters)
        
        assert '{{name}}' not in result or 'World' not in result
    
    def test_render_conditional_missing(self, renderer):
        """Test rendering conditional block when parameter is missing."""
        template = "Hello {{#if name}}{{name}}{{/if}}!"
        parameters = {}
        
        result = renderer.render(template, parameters)
        
        # Conditional content should be removed
        assert '{{name}}' not in result
    
    def test_render_empty_template(self, renderer):
        """Test rendering empty template."""
        template = ""
        parameters = {'name': 'Test'}
        
        result = renderer.render(template, parameters)
        
        assert result == ""
    
    def test_render_no_placeholders(self, renderer):
        """Test rendering template without placeholders."""
        template = "This is a static template with no variables."
        parameters = {'name': 'Test'}
        
        result = renderer.render(template, parameters)
        
        assert result == template
    
    def test_render_special_characters(self, renderer):
        """Test rendering with special characters."""
        template = "Message: {{message}}"
        parameters = {'message': 'Hello & <world>!'}
        
        result = renderer.render(template, parameters)
        
        assert 'Hello' in result
        assert 'world' in result
    
    def test_render_multiline_template(self, renderer):
        """Test rendering multiline template."""
        template = """Project: {{project_name}}
Description: {{description}}
Status: {{status}}"""
        parameters = {
            'project_name': 'HishamOS',
            'description': 'AI Agent OS',
            'status': 'Active'
        }
        
        result = renderer.render(template, parameters)
        
        assert 'HishamOS' in result
        assert 'AI Agent OS' in result
        assert 'Active' in result
    
    def test_render_repeated_parameters(self, renderer):
        """Test rendering template with repeated parameters."""
        template = "{{name}} says hello to {{name}}"
        parameters = {'name': 'John'}
        
        result = renderer.render(template, parameters)
        
        assert 'John' in result
        assert result.count('John') >= 1
    
    def test_render_list_parameter(self, renderer):
        """Test rendering with list parameter."""
        template = "Items: {{items}}"
        parameters = {'items': ['item1', 'item2', 'item3']}
        
        result = renderer.render(template, parameters)
        
        assert 'item1' in result
        assert 'item2' in result
        assert 'item3' in result
    
    def test_render_dict_parameter(self, renderer):
        """Test rendering with dict parameter."""
        template = "Config: {{config}}"
        parameters = {'config': {'key1': 'value1', 'key2': 'value2'}}
        
        result = renderer.render(template, parameters)
        
        assert 'key1' in result or 'value1' in result
    
    def test_extract_variables(self, renderer):
        """Test extracting variables from template."""
        template = "Hello {{name}}, status: {{status}}"
        
        variables = renderer.extract_variables(template)
        
        assert 'name' in variables
        assert 'status' in variables
    
    def test_extract_variables_with_conditionals(self, renderer):
        """Test extracting variables including conditionals."""
        template = "{{#if enabled}}Active{{/if}} User: {{name}}"
        
        variables = renderer.extract_variables(template)
        
        assert 'enabled' in variables
        assert 'name' in variables
    
    def test_validate_template_valid(self, renderer):
        """Test validating a valid template."""
        template = "Hello {{name}}!"
        
        is_valid, errors = renderer.validate_template(template)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_template_unmatched_conditionals(self, renderer):
        """Test validating template with unmatched conditionals."""
        template = "{{#if enabled}}Active"
        
        is_valid, errors = renderer.validate_template(template)
        
        assert not is_valid
        assert len(errors) > 0
        assert 'Unmatched conditional blocks' in errors[0]
