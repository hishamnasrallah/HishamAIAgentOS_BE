"""
Unit tests for ParameterValidator service.
"""
import pytest
from apps.commands.services.parameter_validator import ParameterValidator, ValidationResult


class TestParameterValidator:
    """Test suite for ParameterValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create ParameterValidator instance."""
        return ParameterValidator()
    
    def test_validate_required_parameters_missing(self, validator):
        """Test validation fails when required parameters are missing."""
        schema = [
            {'name': 'project_name', 'type': 'string', 'required': True},
            {'name': 'description', 'type': 'text', 'required': False}
        ]
        provided = {}
        
        result = validator.validate(schema, provided)
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert "Required parameter 'project_name' is missing" in result.errors
    
    def test_validate_required_parameters_present(self, validator):
        """Test validation passes when all required parameters are present."""
        schema = [
            {'name': 'project_name', 'type': 'string', 'required': True},
            {'name': 'description', 'type': 'text', 'required': False}
        ]
        provided = {'project_name': 'Test Project'}
        
        result = validator.validate(schema, provided)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_type_string(self, validator):
        """Test string type validation."""
        schema = [{'name': 'name', 'type': 'string', 'required': True}]
        
        # Valid string
        result = validator.validate(schema, {'name': 'Test'})
        assert result.is_valid
        
        # Invalid type
        result = validator.validate(schema, {'name': 123})
        assert not result.is_valid
        assert any('must be of type string' in error for error in result.errors)
    
    def test_validate_type_integer(self, validator):
        """Test integer type validation."""
        schema = [{'name': 'count', 'type': 'integer', 'required': True}]
        
        # Valid integer
        result = validator.validate(schema, {'count': 42})
        assert result.is_valid
        
        # Invalid type
        result = validator.validate(schema, {'count': '42'})
        assert not result.is_valid
        assert any('must be of type integer' in error for error in result.errors)
    
    def test_validate_type_boolean(self, validator):
        """Test boolean type validation."""
        schema = [{'name': 'enabled', 'type': 'boolean', 'required': True}]
        
        # Valid boolean
        result = validator.validate(schema, {'enabled': True})
        assert result.is_valid
        
        result = validator.validate(schema, {'enabled': False})
        assert result.is_valid
        
        # Invalid type
        result = validator.validate(schema, {'enabled': 'true'})
        assert not result.is_valid
    
    def test_validate_min_length(self, validator):
        """Test min_length validation."""
        schema = [
            {
                'name': 'password',
                'type': 'string',
                'required': True,
                'min_length': 8
            }
        ]
        
        # Valid length
        result = validator.validate(schema, {'password': 'longpassword'})
        assert result.is_valid
        
        # Too short
        result = validator.validate(schema, {'password': 'short'})
        assert not result.is_valid
        assert any('must be at least 8 characters' in error for error in result.errors)
    
    def test_validate_max_length(self, validator):
        """Test max_length validation."""
        schema = [
            {
                'name': 'title',
                'type': 'string',
                'required': True,
                'max_length': 50
            }
        ]
        
        # Valid length
        result = validator.validate(schema, {'title': 'Short Title'})
        assert result.is_valid
        
        # Too long
        long_title = 'A' * 51
        result = validator.validate(schema, {'title': long_title})
        assert not result.is_valid
        assert any('must not exceed 50 characters' in error for error in result.errors)
    
    def test_validate_min_value(self, validator):
        """Test min_value validation."""
        schema = [
            {
                'name': 'age',
                'type': 'integer',
                'required': True,
                'min_value': 18
            }
        ]
        
        # Valid value
        result = validator.validate(schema, {'age': 25})
        assert result.is_valid
        
        # Too small
        result = validator.validate(schema, {'age': 15})
        assert not result.is_valid
        assert any('must be at least 18' in error for error in result.errors)
    
    def test_validate_max_value(self, validator):
        """Test max_value validation."""
        schema = [
            {
                'name': 'score',
                'type': 'integer',
                'required': True,
                'max_value': 100
            }
        ]
        
        # Valid value
        result = validator.validate(schema, {'score': 85})
        assert result.is_valid
        
        # Too large
        result = validator.validate(schema, {'score': 150})
        assert not result.is_valid
        assert any('must not exceed 100' in error for error in result.errors)
    
    def test_validate_allowed_values(self, validator):
        """Test allowed_values validation."""
        schema = [
            {
                'name': 'status',
                'type': 'string',
                'required': True,
                'allowed_values': ['active', 'inactive', 'pending']
            }
        ]
        
        # Valid value
        result = validator.validate(schema, {'status': 'active'})
        assert result.is_valid
        
        # Invalid value
        result = validator.validate(schema, {'status': 'invalid'})
        assert not result.is_valid
        assert any('must be one of' in error for error in result.errors)
    
    def test_validate_unknown_parameter(self, validator):
        """Test warning for unknown parameters."""
        schema = [{'name': 'known', 'type': 'string', 'required': False}]
        provided = {'known': 'value', 'unknown': 'value'}
        
        result = validator.validate(schema, provided)
        
        assert result.is_valid  # Should not fail, just warn
        assert len(result.warnings) == 1
        assert "Unknown parameter 'unknown' will be ignored" in result.warnings
    
    def test_get_defaults(self, validator):
        """Test extracting default values from schema."""
        schema = [
            {'name': 'param1', 'type': 'string', 'default': 'default1'},
            {'name': 'param2', 'type': 'string'},  # No default
            {'name': 'param3', 'type': 'string', 'default': 'default3'}
        ]
        
        defaults = validator.get_defaults(schema)
        
        assert defaults == {'param1': 'default1', 'param3': 'default3'}
        assert 'param2' not in defaults
    
    def test_merge_with_defaults(self, validator):
        """Test merging provided parameters with defaults."""
        schema = [
            {'name': 'param1', 'type': 'string', 'default': 'default1'},
            {'name': 'param2', 'type': 'string', 'default': 'default2'},
            {'name': 'param3', 'type': 'string'}  # No default
        ]
        provided = {'param1': 'provided1', 'param3': 'provided3'}
        
        merged = validator.merge_with_defaults(schema, provided)
        
        assert merged['param1'] == 'provided1'  # Provided value takes precedence
        assert merged['param2'] == 'default2'  # Default value used
        assert merged['param3'] == 'provided3'  # Provided value used
    
    def test_validate_complex_schema(self, validator):
        """Test validation with complex schema."""
        schema = [
            {'name': 'name', 'type': 'string', 'required': True, 'min_length': 3, 'max_length': 50},
            {'name': 'age', 'type': 'integer', 'required': True, 'min_value': 0, 'max_value': 120},
            {'name': 'email', 'type': 'string', 'required': False},
            {'name': 'active', 'type': 'boolean', 'required': False, 'default': True}
        ]
        
        # Valid complex input
        provided = {
            'name': 'John Doe',
            'age': 30,
            'email': 'john@example.com',
            'active': True
        }
        result = validator.validate(schema, provided)
        assert result.is_valid
        
        # Invalid complex input (multiple errors)
        provided = {
            'name': 'Jo',  # Too short
            'age': 150,  # Too large
            'email': 'invalid'  # Valid but not validated further
        }
        result = validator.validate(schema, provided)
        assert not result.is_valid
        assert len(result.errors) >= 2  # At least 2 errors


