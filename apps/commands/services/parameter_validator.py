"""
Parameter validation for command templates.

Validates user-provided parameters against command template schemas.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of parameter validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class ParameterValidator:
    """Validates parameters for command templates."""
    
    SUPPORTED_TYPES = {
        'string', 'text', 'long_text', 'number', 'integer',
        'float', 'boolean', 'list', 'dict', 'json'
    }
    
    def validate(
        self,
        parameters_schema: List[Dict[str, Any]],
        provided_parameters: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate provided parameters against schema.
        
        Args:
            parameters_schema: List of parameter definitions from command template
            provided_parameters: User-provided parameters
            
        Returns:
            ValidationResult with validation status and messages
        """
        errors = []
        warnings = []
        
        # Check required parameters
        required_params = {
            param['name'] for param in parameters_schema
            if param.get('required', False)
        }
        
        missing_params = required_params - set(provided_parameters.keys())
        if missing_params:
            errors.extend([
                f"Required parameter '{param}' is missing"
                for param in missing_params
            ])
        
        # Validate each provided parameter
        schema_map = {param['name']: param for param in parameters_schema}
        
        for param_name, param_value in provided_parameters.items():
            # Check if parameter exists in schema
            if param_name not in schema_map:
                warnings.append(f"Unknown parameter '{param_name}' will be ignored")
                continue
            
            param_schema = schema_map[param_name]
            
            # Type validation
            param_type = param_schema.get('type', 'string')
            validation_errors = self._validate_type(param_name, param_value, param_type)
            errors.extend(validation_errors)
            
            # Custom validation rules
            if 'min_length' in param_schema:
                if isinstance(param_value, str) and len(param_value) < param_schema['min_length']:
                    errors.append(
                        f"Parameter '{param_name}' must be at least "
                        f"{param_schema['min_length']} characters"
                    )
            
            if 'max_length' in param_schema:
                if isinstance(param_value, str) and len(param_value) > param_schema['max_length']:
                    errors.append(
                        f"Parameter '{param_name}' must not exceed "
                        f"{param_schema['max_length']} characters"
                    )
            
            if 'min_value' in param_schema:
                if isinstance(param_value, (int, float)) and param_value < param_schema['min_value']:
                    errors.append(
                        f"Parameter '{param_name}' must be at least {param_schema['min_value']}"
                    )
            
            if 'max_value' in param_schema:
                if isinstance(param_value, (int, float)) and param_value > param_schema['max_value']:
                    errors.append(
                        f"Parameter '{param_name}' must not exceed {param_schema['max_value']}"
                    )
            
            if 'allowed_values' in param_schema:
                if param_value not in param_schema['allowed_values']:
                    errors.append(
                        f"Parameter '{param_name}' must be one of: "
                        f"{', '.join(str(v) for v in param_schema['allowed_values'])}"
                    )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_type(self, param_name: str, value: Any, expected_type: str) -> List[str]:
        """Validate parameter type."""
        errors = []
        
        if expected_type not in self.SUPPORTED_TYPES:
            errors.append(f"Unsupported parameter type: {expected_type}")
            return errors
        
        type_validators = {
            'string': lambda v: isinstance(v, str),
            'text': lambda v: isinstance(v, str),
            'long_text': lambda v: isinstance(v, str),
            'number': lambda v: isinstance(v, (int, float)),
            'integer': lambda v: isinstance(v, int),
            'float': lambda v: isinstance(v, float),
            'boolean': lambda v: isinstance(v, bool),
            'list': lambda v: isinstance(v, list),
            'dict': lambda v: isinstance(v, dict),
            'json': lambda v: isinstance(v, (dict, list)),
        }
        
        validator = type_validators.get(expected_type)
        if validator and not validator(value):
            errors.append(
                f"Parameter '{param_name}' must be of type {expected_type}, "
                f"got {type(value).__name__}"
            )
        
        return errors
    
    def get_defaults(self, parameters_schema: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract default values from parameter schema."""
        return {
            param['name']: param['default']
            for param in parameters_schema
            if 'default' in param
        }
    
    def merge_with_defaults(
        self,
        parameters_schema: List[Dict[str, Any]],
        provided_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge provided parameters with defaults."""
        defaults = self.get_defaults(parameters_schema)
        return {**defaults, **provided_parameters}
