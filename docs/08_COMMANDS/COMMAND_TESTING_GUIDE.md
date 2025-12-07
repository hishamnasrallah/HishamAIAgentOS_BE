---
title: "Command Library Testing Guide"
description: "**Last Updated:** December 6, 2024"

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Developer
    - QA / Tester
  secondary:
    - Technical Writer
    - CTO / Technical Lead

applicable_phases:
  primary:
    - Testing
    - QA
  secondary:
    - Development

tags:
  - commands
  - testing
  - test
  - core
  - guide

status: "active"
priority: "medium"
difficulty: "intermediate"
completeness: "100%"
quality_status: "draft"

estimated_read_time: "10 minutes"

version: "1.0"
last_updated: "2025-12-06"
last_reviewed: "2025-12-06"
review_frequency: "quarterly"

author: "Development Team"
maintainer: "Development Team"

related: []
see_also: []
depends_on: []
prerequisite_for: []

aliases: []

changelog:
  - version: "1.0"
    date: "2025-12-06"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---

# Command Library Testing Guide

**Last Updated:** December 6, 2024  
**Purpose:** Comprehensive guide for testing command library functionality

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Testing Tools](#testing-tools)
3. [Manual Testing](#manual-testing)
4. [Automated Testing](#automated-testing)
5. [API Testing](#api-testing)
6. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides comprehensive instructions for testing the HishamOS Command Library, including command execution, template rendering, parameter validation, and API endpoints.

### Testing Objectives

- ✅ Verify all commands can be executed
- ✅ Validate parameter validation works correctly
- ✅ Test template rendering with various inputs
- ✅ Verify API endpoints function properly
- ✅ Ensure agent linking works correctly
- ✅ Test error handling and edge cases

---

## Testing Tools

### 1. Verification Script

**Command:** `python manage.py verify_commands`

**Purpose:** Verify command library statistics and status

**Output:**
- Total command count
- Commands by category
- Commands by agent
- Commands by capability
- Progress to targets
- Recently added commands

**Usage:**
```bash
python manage.py verify_commands
```

### 2. Command Testing Script

**Command:** `python manage.py test_commands`

**Purpose:** Test command execution and template rendering

**Options:**
- `--command-slug <slug>` - Test specific command
- `--category <category>` - Test all commands in category
- `--sample` - Test one command from each category
- `--preview-only` - Only test template rendering (no execution)

**Examples:**
```bash
# Test specific command
python manage.py test_commands --command-slug generate-user-stories

# Test all commands in a category
python manage.py test_commands --category requirements-engineering

# Test sample from each category
python manage.py test_commands --sample

# Preview only (no execution)
python manage.py test_commands --preview-only
```

### 3. Agent Linking Script

**Command:** `python manage.py link_commands_to_agents`

**Purpose:** Automatically link commands to recommended agents based on capabilities

**Usage:**
```bash
python manage.py link_commands_to_agents
```

**What it does:**
- Finds all commands without agent assignments
- Matches commands to agents based on `required_capabilities`
- Falls back to category-based matching if capability match fails
- Updates commands with recommended agents

### 4. Endpoint Testing Script

**Command:** `python manage.py test_command_endpoints`

**Purpose:** Test command API endpoints to verify they work correctly

**Options:**
- `--verbose` - Show detailed output for each test

**Usage:**
```bash
# Run all endpoint tests
python manage.py test_command_endpoints

# Run with detailed output
python manage.py test_command_endpoints --verbose
```

**What it tests:**
1. **Popular Commands Endpoint** (`GET /api/v1/commands/templates/popular/`)
   - Verifies endpoint returns list of popular commands
   - Checks response structure and data format

2. **Preview Endpoint** (`POST /api/v1/commands/templates/{id}/preview/`)
   - Tests parameter validation
   - Verifies template rendering
   - Checks response structure

3. **Execute Endpoint** (`POST /api/v1/commands/templates/{id}/execute/`)
   - Tests endpoint structure (does not make actual LLM calls)
   - Verifies response format
   - Checks error handling

**Output:**
- Shows test results for each endpoint
- Displays success/failure status
- Provides error messages if tests fail
- Shows success rate percentage

**See also:** `docs/07_TRACKING/COMMAND_ENDPOINTS_TESTING.md` for detailed documentation

---

## Manual Testing

### Test Command Execution

1. **Get Command ID:**
   ```bash
   curl http://localhost:8000/api/v1/commands/templates/?slug=generate-user-stories
   ```

2. **Test Preview:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/commands/templates/{id}/preview/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {token}" \
     -d '{
       "parameters": {
         "project_context": "E-commerce platform",
         "requirements": "User authentication, Product catalog"
       }
     }'
   ```

3. **Test Execution:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/commands/templates/{id}/execute/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {token}" \
     -d '{
       "parameters": {
         "project_context": "E-commerce platform",
         "requirements": "User authentication, Product catalog"
       }
     }'
   ```

### Test Parameter Validation

1. **Valid Parameters:**
   - Should return 200 OK
   - Should render template successfully

2. **Missing Required Parameters:**
   - Should return 400 Bad Request
   - Should include error messages

3. **Invalid Parameter Types:**
   - Should return 400 Bad Request
   - Should validate type constraints

4. **Invalid Parameter Values:**
   - Should return 400 Bad Request
   - Should validate allowed_values if specified

### Test Template Rendering

1. **Basic Rendering:**
   - Test with all required parameters
   - Verify placeholders are replaced
   - Check for template syntax errors

2. **Conditional Rendering:**
   - Test `{{#if}}` blocks with true/false values
   - Verify optional sections appear/disappear correctly

3. **Edge Cases:**
   - Empty strings
   - Very long text
   - Special characters
   - HTML/XML content

---

## Automated Testing

### Using the Test Script

**Basic Test:**
```bash
python manage.py test_commands --sample
```

**Full Test (Preview Only):**
```bash
python manage.py test_commands --preview-only
```

**Category Test:**
```bash
python manage.py test_commands --category code-generation
```

### Expected Results

**Success:**
```
✅ Passed: 10
❌ Failed: 0
Total: 10
```

**Failure:**
```
✅ Passed: 8
❌ Failed: 2
Total: 10
```

---

## API Testing

### Endpoints to Test

#### 1. List Commands
```bash
GET /api/v1/commands/templates/
```

**Test Cases:**
- [ ] Returns list of commands
- [ ] Supports pagination
- [ ] Supports filtering by category
- [ ] Supports search
- [ ] Returns correct count

#### 2. Get Command Details
```bash
GET /api/v1/commands/templates/{id}/
```

**Test Cases:**
- [ ] Returns command details
- [ ] Includes all fields
- [ ] Returns 404 for invalid ID

#### 3. Preview Command
```bash
POST /api/v1/commands/templates/{id}/preview/
```

**Test Cases:**
- [ ] Renders template with valid parameters
- [ ] Returns 400 for invalid parameters
- [ ] Returns 400 for missing required parameters
- [ ] Handles optional parameters correctly

#### 4. Execute Command
```bash
POST /api/v1/commands/templates/{id}/execute/
```

**Test Cases:**
- [ ] Executes command with valid parameters
- [ ] Returns agent response
- [ ] Handles errors gracefully
- [ ] Requires authentication
- [ ] Records execution in database

#### 5. Get Popular Commands
```bash
GET /api/v1/commands/templates/popular/
```

**Test Cases:**
- [ ] Returns top 10 commands
- [ ] Ordered by usage_count
- [ ] Only active commands

---

## Troubleshooting

### Common Issues

#### 1. Template Rendering Errors

**Error:** `Template syntax error`

**Solution:**
- Check Handlebars syntax
- Verify all `{{}}` are properly closed
- Check for typos in parameter names

#### 2. Parameter Validation Errors

**Error:** `Parameter validation failed`

**Solution:**
- Verify parameter names match template
- Check required vs optional parameters
- Validate parameter types

#### 3. Agent Not Found

**Error:** `Agent not found`

**Solution:**
- Run `python manage.py link_commands_to_agents`
- Verify agents are loaded in database
- Check agent_id matches in create_commands.py

#### 4. Command Execution Fails

**Error:** `Command execution failed`

**Solution:**
- Check agent is active
- Verify API keys are configured
- Check agent capabilities match command requirements

---

## Test Checklist

### Pre-Testing
- [ ] Backend server running
- [ ] Database migrations applied
- [ ] Agents loaded in database
- [ ] API keys configured
- [ ] Authentication token available

### Command Testing
- [ ] All commands load successfully
- [ ] Parameter validation works
- [ ] Template rendering works
- [ ] Commands can be executed
- [ ] Error handling works

### API Testing
- [ ] List endpoint works
- [ ] Detail endpoint works
- [ ] Preview endpoint works
- [ ] Execute endpoint works
- [ ] Popular commands endpoint works
- [ ] Filtering and search work

### Agent Linking
- [ ] Commands linked to agents
- [ ] Agent matching is correct
- [ ] Capability matching works
- [ ] Category fallback works

---

## Best Practices

1. **Test Incrementally**
   - Test after adding new commands
   - Test after modifying templates
   - Test after agent linking

2. **Test Edge Cases**
   - Empty parameters
   - Very long text
   - Special characters
   - Missing optional parameters

3. **Monitor Performance**
   - Check execution times
   - Monitor API response times
   - Track error rates

4. **Document Issues**
   - Record any failures
   - Note edge cases found
   - Update this guide with new findings

---

**Last Updated:** December 6, 2024  
**Maintained By:** HishamOS Development Team

