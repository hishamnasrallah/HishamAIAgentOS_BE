# HishamOS Test Suite

## Overview

This directory contains the comprehensive test suite for HishamOS, including unit tests, integration tests, and E2E tests.

## Test Structure

```
tests/
├── unit/              # Unit tests for individual components
│   ├── commands/      # Command service tests
│   ├── workflows/    # Workflow service tests
│   └── agents/       # Agent service tests
├── integration/       # Integration tests for complete flows
└── conftest.py       # Pytest fixtures and configuration
```

## Running Tests

### Run All Tests
```bash
cd backend
pytest
```

### Run with Coverage
```bash
pytest --cov=apps --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/unit/commands/test_parameter_validator.py
```

### Run Specific Test Class
```bash
pytest tests/unit/commands/test_parameter_validator.py::TestParameterValidator
```

### Run Specific Test Method
```bash
pytest tests/unit/commands/test_parameter_validator.py::TestParameterValidator::test_validate_required_parameters_missing
```

## Test Coverage Goals

- **Current Target:** 60% coverage
- **Short-term Goal:** 80% coverage
- **Long-term Goal:** 90% coverage

## Writing Tests

### Unit Test Example

```python
import pytest
from apps.commands.services.parameter_validator import ParameterValidator

class TestParameterValidator:
    @pytest.fixture
    def validator(self):
        return ParameterValidator()
    
    def test_validate_required_parameters_missing(self, validator):
        schema = [{'name': 'param', 'type': 'string', 'required': True}]
        provided = {}
        
        result = validator.validate(schema, provided)
        
        assert not result.is_valid
        assert len(result.errors) > 0
```

### Integration Test Example

```python
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestCommandExecutionFlow:
    def test_command_execution(self, user):
        # Test complete flow
        pass
```

## Test Fixtures

Available fixtures (in `conftest.py`):
- `user` - Regular test user
- `admin_user` - Admin test user
- `api_client` - DRF API client
- `authenticated_client` - Authenticated API client
- `admin_client` - Admin API client
- `django_client` - Django test client

## Test Configuration

- **Settings:** `core.settings.testing`
- **Database:** In-memory SQLite
- **Migrations:** Disabled for speed
- **Caching:** Dummy cache backend
- **Celery:** Eager mode (synchronous)

## Coverage Reports

After running tests with coverage, view HTML report:
```bash
# Open in browser
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

## Continuous Integration

Tests should be run automatically in CI/CD pipeline:
- On every pull request
- Before merging to main
- On scheduled basis

## Best Practices

1. **Test Naming:** Use descriptive test names
2. **Test Isolation:** Each test should be independent
3. **Test Data:** Use fixtures for reusable test data
4. **Assertions:** Use specific assertions, not just `assert True`
5. **Coverage:** Aim for 80%+ coverage on critical paths
6. **Speed:** Keep tests fast (use in-memory DB, disable migrations)

## Troubleshooting

### Tests Failing
1. Check database migrations are applied
2. Verify test settings are correct
3. Check for missing dependencies
4. Review test logs for errors

### Coverage Not Working
1. Ensure `pytest-cov` is installed
2. Check `pytest.ini` configuration
3. Verify `--cov` flag is included

### Slow Tests
1. Use `--reuse-db` flag
2. Disable migrations in test settings
3. Use in-memory database
4. Mock external API calls

