"""
Create command categories and load command templates.

Run: python create_command_library.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')
django.setup()

from django.utils.text import slugify
from apps.commands.models import CommandCategory, CommandTemplate
from apps.agents.models import Agent


def create_categories():
    """Create all 12 command categories."""
    categories_data = [
        {
            'name': 'Requirements Engineering',
            'slug': 'requirements-engineering',
            'description': 'Transform ideas into detailed requirements, user stories, and specifications',
            'icon': '📋',
            'order': 1
        },
        {
            'name': 'Code Generation',
            'slug': 'code-generation',
            'description': 'Generate high-quality production code across multiple languages and frameworks',
            'icon': '💻',
            'order': 2
        },
        {
            'name': 'Code Review',
            'slug': 'code-review',
            'description': 'Comprehensive code review and quality analysis',
            'icon': '🔍',
            'order': 3
        },
        {
            'name': 'Testing & QA',
            'slug': 'testing-qa',
            'description': 'Test generation, quality assurance, and validation',
            'icon': '✅',
            'order': 4
        },
        {
            'name': 'DevOps & Deployment',
            'slug': 'devops-deployment',
            'description': 'CI/CD, infrastructure, and deployment automation',
            'icon': '🚀',
            'order': 5
        },
        {
            'name': 'Documentation',
            'slug': 'documentation',
            'description': 'Technical writing, API docs, and user guides',
            'icon': '📚',
            'order': 6
        },
        {
            'name': 'Project Management',
            'slug': 'project-management',
            'description': 'Sprint planning, task breakdown, and project tracking',
            'icon': '📊',
            'order': 7
        },
        {
            'name': 'Design & Architecture',
            'slug': 'design-architecture',
            'description': 'System design, architecture decisions, and technical planning',
            'icon': '🏗️',
            'order': 8
        },
        {
            'name': 'Legal & Compliance',
            'slug': 'legal-compliance',
            'description': 'Contracts, policies, and regulatory compliance',
            'icon': '⚖️',
            'order': 9
        },
        {
            'name': 'Business Analysis',
            'slug': 'business-analysis',
            'description': 'Market research, ROI analysis, and business strategy',
            'icon': '💼',
            'order': 10
        },
        {
            'name': 'UX/UI Design',
            'slug': 'ux-ui-design',
            'description': 'User experience, interface design, and usability',
            'icon': '🎨',
            'order': 11
        },
        {
            'name': 'Research & Analysis',
            'slug': 'research-analysis',
            'description': 'Technology research, competitive analysis, and insights',
            'icon': '🔬',
            'order': 12
        }
    ]
    
    created = 0
    updated = 0
    
    for cat_data in categories_data:
        category, created_flag = CommandCategory.objects.update_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        if created_flag:
            created += 1
            print(f"✓ Created category: {category.name}")
        else:
            updated += 1
            print(f"↻ Updated category: {category.name}")
    
    print(f"\n📁 Categories: {created} created, {updated} updated")
    return CommandCategory.objects.all()


def get_agent_by_id(agent_id):
    """Get agent by agent_id."""
    try:
        return Agent.objects.get(agent_id=agent_id)
    except Agent.DoesNotExist:
        return None


def create_requirements_commands(category):
    """Create Requirements Engineering commands."""
    commands = [
        {
            'name': 'Generate User Stories from Requirements',
            'slug': 'generate-user-stories',
            'description': 'Convert raw requirements into well-formed INVEST user stories with acceptance criteria',
            'template': '''You are creating user stories for a software project.

**Project Context:** {{project_context}}

**Requirements:**
{{requirements}}

{{#if additional_context}}
**Additional Context:**
{{additional_context}}
{{/if}}

Please create user stories that:
1. Follow the INVEST criteria (Independent, Negotiable, Valuable, Estimable, Small, Testable)
2. Include clear acceptance criteria for each story
3. Provide story point estimates (Fibonacci: 1, 2, 3, 5, 8, 13)
4. Identify dependencies between stories
{{#if include_technical_notes}}5. Include technical implementation notes{{/if}}

**Format each story as:**

**Story [Number]**: [Title]

**As a** [user type]  
**I want** [feature/capability]  
**So that** [benefit/value]

**Acceptance Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

**Story Points**: [estimate]  
**Dependencies**: [story numbers or 'None']  
{{#if include_technical_notes}}**Technical Notes**: [implementation guidance]{{/if}}

Generate 5-10 comprehensive user stories.''',
            'parameters': [
                {
                    'name': 'project_context',
                    'type': 'text',
                    'required': True,
                    'description': 'Brief project description and goals',
                    'example': 'E-commerce platform for selling artisan coffee'
                },
                {
                    'name': 'requirements',
                    'type': 'long_text',
                    'required': True,
                    'description': 'Raw requirements or feature list',
                    'example': 'Users need to browse products, add to cart, checkout with payment, track orders'
                },
                {
                    'name': 'additional_context',
                    'type': 'text',
                    'required': False,
                    'description': 'Any additional context, constraints, or preferences',
                    'default': ''
                },
                {
                    'name': 'include_technical_notes',
                    'type': 'boolean',
                    'required': False,
                    'description': 'Include technical implementation guidance',
                    'default': False
                }
            ],
            'tags': ['agile', 'scrum', 'user-stories', 'requirements', 'invest'],
            'example_usage': {
                'input': {
                    'project_context': 'Task management SaaS application for distributed teams',
                    'requirements': 'Users should be able to create projects, add tasks, assign team members, set deadlines, and track progress with visual dashboards',
                    'include_technical_notes': True
                },
                'output_preview': '**Story 1**: Create New Project Workspace\n\n**As a** project manager\n**I want** to create a new project workspace with a unique name and description\n**So that** I can organize related tasks and collaborate with my team...'
            },
            'recommended_agent': get_agent_by_id('business-analyst'),
            'required_capabilities': ['USER_STORY_GENERATION', 'REQUIREMENTS_ANALYSIS']
        },
        {
            'name': 'Create Acceptance Criteria',
            'slug': 'create-acceptance-criteria',
            'description': 'Generate clear, testable acceptance criteria for user stories or features',
            'template': '''Generate comprehensive acceptance criteria for the following feature or user story.

**Feature/Story:**
{{feature_description}}

{{#if user_role}}
**Target User Role:** {{user_role}}
{{/if}}

{{#if business_rules}}
**Business Rules:**
{{business_rules}}
{{/if}}

Create acceptance criteria that are:
1. **Specific** - Clear and unambiguous
2. **Testable** - Can be verified objectively
3. **Complete** - Cover all scenarios including edge cases
4. **Concise** - Easy to understand

**Format:**

**Given** [initial context/state]  
**When** [action is taken]  
**Then** [expected outcome]

Include:
- Happy path scenarios (3-5 criteria)
- Alternative flows (2-3 criteria)
- Edge cases and error scenarios (2-3 criteria)
- Non-functional requirements if applicable (performance, security, usability)

Use checkbox format for each criterion:
- [ ] Criterion description''',
            'parameters': [
                {
                    'name': 'feature_description',
                    'type': 'long_text',
                    'required': True,
                    'description': 'Description of the feature or user story',
                    'example': 'User login with email and password, including remember me functionality'
                },
                {
                    'name': 'user_role',
                    'type': 'string',
                    'required': False,
                    'description': 'Target user role for this feature',
                    'example': 'End user, Administrator, Guest'
                },
                {
                    'name': 'business_rules',
                    'type': 'text',
                    'required': False,
                    'description': 'Specific business rules that apply',
                    'example': 'Passwords must be at least 8 characters, Maximum 5 failed login attempts'
                }
            ],
            'tags': ['acceptance-criteria', 'testing', 'requirements', 'bdd'],
            'example_usage': {
                'input': {
                    'feature_description': 'Shopping cart checkout process with multiple payment options',
                    'user_role': 'Customer',
                    'business_rules': 'Minimum order $10, Free shipping over $50, Accept credit cards and PayPal'
                },
                'output_preview': '**Happy Path:**\n- [ ] Given a cart with items totaling $25, When user proceeds to checkout, Then payment options (Credit Card, PayPal) are displayed...'
            },
            'recommended_agent': get_agent_by_id('business-analyst'),
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        # Add more requirements commands...
    ]
    
    return commands


def create_code_generation_commands(category):
    """Create Code Generation commands."""
    commands = [
        {
            'name': 'Generate REST API Endpoint',
            'slug': 'generate-api-endpoint',
            'description': 'Create a complete REST API endpoint with validation, error handling, and documentation',
            'template': '''Generate a production-ready REST API endpoint.

**Framework:** {{framework}}  
**Language:** {{language}}  
**Endpoint:** {{http_method}} {{endpoint_path}}

**Purpose:** {{purpose}}

**Request Body Schema:**
{{request_schema}}

**Response Schema:**
{{response_schema}}

{{#if authentication_required}}
**Authentication:** Required - {{authentication_method}}
{{/if}}

{{#if business_logic}}
**Business Logic:**
{{business_logic}}
{{/if}}

Generate complete code including:

1. **Route/Controller** - Endpoint definition with proper HTTP method
2. **Request Validation** - Input validation using framework best practices
3. **Business Logic** - Core functionality implementation
4. **Error Handling** - Proper error responses with status codes
5. **Response Formatting** - Structured JSON responses
6. **Documentation** - OpenAPI/Swagger documentation comments
{{#if include_tests}}7. **Unit Tests** - Test cases covering happy path and error scenarios{{/if}}

**Requirements:**
- Follow {{framework}} best practices
- Use proper HTTP status codes (200, 201, 400, 401, 404, 500)
- Include input validation
- Handle errors gracefully
- Add logging for debugging
- Security: Prevent SQL injection, XSS, validate all inputs

Provide complete, production-ready code.''',
            'parameters': [
                {
                    'name': 'framework',
                    'type': 'string',
                    'required': True,
                    'description': 'Web framework (Django, FastAPI, Express, Spring Boot, etc.)',
                    'example': 'Django REST Framework'
                },
                {
                    'name': 'language',
                    'type': 'string',
                    'required': True,
                    'description': 'Programming language',
                    'example': 'Python'
                },
                {
                    'name': 'http_method',
                    'type': 'string',
                    'required': True,
                    'allowed_values': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                    'description': 'HTTP method for the endpoint'
                },
                {
                    'name': 'endpoint_path',
                    'type': 'string',
                    'required': True,
                    'description': 'API endpoint path',
                    'example': '/api/v1/users'
                },
                {
                    'name': 'purpose',
                    'type': 'text',
                    'required': True,
                    'description': 'What this endpoint does',
                    'example': 'Create a new user account'
                },
                {
                    'name': 'request_schema',
                    'type': 'text',
                    'required': True,
                    'description': 'Expected request body structure',
                    'example': '{"email": "string", "password": "string", "name": "string"}'
                },
                {
                    'name': 'response_schema',
                    'type': 'text',
                    'required': True,
                    'description': 'Expected response structure',
                    'example': '{"user_id": "uuid", "email": "string", "created_at": "datetime"}'
                },
                {
                    'name': 'authentication_required',
                    'type': 'boolean',
                    'required': False,
                    'default': False,
                    'description': 'Does this endpoint require authentication?'
                },
                {
                    'name': 'authentication_method',
                    'type': 'string',
                    'required': False,
                    'default': 'JWT',
                    'description': 'Authentication method (JWT, API Key, OAuth, etc.)'
                },
                {
                    'name': 'business_logic',
                    'type': 'text',
                    'required': False,
                    'description': 'Specific business logic or rules to implement'
                },
                {
                    'name': 'include_tests',
                    'type': 'boolean',
                    'required': False,
                    'default': True,
                    'description': 'Include unit tests'
                }
            ],
            'tags': ['api', 'rest', 'backend', 'endpoints', 'web-development'],
            'example_usage': {
                'input': {
                    'framework': 'FastAPI',
                    'language': 'Python',
                    'http_method': 'POST',
                    'endpoint_path': '/api/v1/tasks',
                    'purpose': 'Create a new task',
                    'request_schema': '{"title": "string", "description": "string", "due_date": "date", "priority": "high|medium|low"}',
                    'response_schema': '{"task_id": "uuid", "title": "string", "status": "pending"}',
                    'authentication_required': True,
                    'include_tests': True
                },
                'output_preview': 'from fastapi import APIRouter, Depends, HTTPException...'
            },
            'recommended_agent': get_agent_by_id('coding-agent'),
            'required_capabilities': ['CODE_GENERATION']
        },
        # Add more code generation commands...
    ]
    
    return commands


def create_code_review_commands(category):
    """Create Code Review commands."""
    commands = [
        {
            'name': 'Security Audit - OWASP Top 10',
            'slug': 'security-audit-owasp',
            'description': 'Comprehensive security audit checking for OWASP Top 10 vulnerabilities',
            'template': '''Perform a comprehensive security audit on the following code.

**Language:** {{language}}  
**Framework:** {{framework}}

**Code to Audit:**
```{{language}}
{{code}}
```

{{#if code_context}}
**Context:** {{code_context}}
{{/if}}

Analyze for **OWASP Top 10** security vulnerabilities:

1. **Injection** (SQL, NoSQL, Command, LDAP)
2. **Broken Authentication** (weak passwords, session management)
3. **Sensitive Data Exposure** (encryption, data protection)
4. **XML External Entities (XXE)**
5. **Broken Access Control** (authorization, IDOR)
6. **Security Misconfiguration**
7. **Cross-Site Scripting (XSS)**
8. **Insecure Deserialization**
9. **Using Components with Known Vulnerabilities**
10. **Insufficient Logging & Monitoring**

For each finding, provide:

**[SEVERITY: Critical/High/Medium/Low] - [Vulnerability Type]**

**Location:** Line X-Y or Function name  
**Issue:** Detailed explanation of the vulnerability  
**Risk:** Potential impact if exploited  
**Recommendation:** Specific fix with code example  

**Security Score: X/100**

Provide:
- List of all vulnerabilities found (prioritized by severity)
- Remediation code snippets
- Best practices recommendations
- Dependencies security check (if applicable)
{{#if compliance_check}}
- Compliance status for: {{compliance_standards}}
{{/if}}''',
            'parameters': [
                {
                    'name': 'language',
                    'type': 'string',
                    'required': True,
                    'description': 'Programming language',
                    'example': 'Python'
                },
                {
                    'name': 'framework',
                    'type': 'string',
                    'required': False,
                    'description': 'Framework or libraries used',
                    'example': 'Django'
                },
                {
                    'name': 'code',
                    'type': 'long_text',
                    'required': True,
                    'description': 'Code to audit for security issues'
                },
                {
                    'name': 'code_context',
                    'type': 'text',
                    'required': False,
                    'description': 'Additional context about the code purpose'
                },
                {
                    'name': 'compliance_check',
                    'type': 'boolean',
                    'required': False,
                    'default': False,
                    'description': 'Check compliance with specific standards'
                },
                {
                    'name': 'compliance_standards',
                    'type': 'string',
                    'required': False,
                    'description': 'Compliance standards to check (GDPR, HIPAA, PCI-DSS, etc.)'
                }
            ],
            'tags': ['security', 'audit', 'owasp', 'vulnerabilities', 'code-review'],
            'example_usage': {
                'input': {
                    'language': 'Python',
                    'framework': 'Flask',
                    'code': 'user_input = request.args.get("id")\nquery = f"SELECT * FROM users WHERE id = {user_input}"\ndb.execute(query)',
                    'compliance_check': True,
                    'compliance_standards': 'GDPR, SOC 2'
                },
                'output_preview': '[SEVERITY: Critical] - SQL Injection\n\nLocation: Line 2...'
            },
            'recommended_agent': get_agent_by_id('code-reviewer'),
            'required_capabilities': ['CODE_REVIEW', 'SECURITY_AUDIT']
        },
        # Add more code review commands...
    ]
    
    return commands


def main():
    """Main execution."""
    print("=" * 60)
    print("  HISHAMOS COMMAND LIBRARY SETUP")
    print("=" * 60)
    print()
    
    # Step 1: Create categories
    print("Step 1: Creating command categories...")
    categories = create_categories()
    
    # Step 2: Create commands
    print("\nStep 2: Creating command templates...")
    
    total_created = 0
    total_updated = 0
    
    cat_map = {cat.slug: cat for cat in categories}
    
    # Requirements Engineering
    req_commands = create_requirements_commands(cat_map['requirements-engineering'])
    for cmd_data in req_commands:
        cmd_data['category'] = cat_map['requirements-engineering']
        command, created = CommandTemplate.objects.update_or_create(
            slug=cmd_data['slug'],
            defaults=cmd_data
        )
        if created:
            total_created += 1
            print(f"  ✓ {command.name}")
        else:
            total_updated += 1
            print(f"  ↻ {command.name}")
    
    # Code Generation
    code_commands = create_code_generation_commands(cat_map['code-generation'])
    for cmd_data in code_commands:
        cmd_data['category'] = cat_map['code-generation']
        command, created = CommandTemplate.objects.update_or_create(
            slug=cmd_data['slug'],
            defaults=cmd_data
        )
        if created:
            total_created += 1
            print(f"  ✓ {command.name}")
        else:
            total_updated += 1
            print(f"  ↻ {command.name}")
    
    # Code Review
    review_commands = create_code_review_commands(cat_map['code-review'])
    for cmd_data in review_commands:
        cmd_data['category'] = cat_map['code-review']
        command, created = CommandTemplate.objects.update_or_create(
            slug=cmd_data['slug'],
            defaults=cmd_data
        )
        if created:
            total_created += 1
            print(f"  ✓ {command.name}")
        else:
            total_updated += 1
            print(f"  ↻ {command.name}")
    
    print()
    print("=" * 60)
    print(f"✅ COMPLETE!")
    print(f"   Commands: {total_created} created, {total_updated} updated")
    print(f"   Categories: {categories.count()} total")
    print("=" * 60)


if __name__ == '__main__':
    main()
