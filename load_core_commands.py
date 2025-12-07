"""
Load 50 core commands into the command library.

Categories:
- Requirements Engineering (10 commands)
- Code Generation (20 commands)  
- Code Review (15 commands)
- Testing & QA (5 commands)
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from apps.commands.models import CommandCategory, CommandTemplate

# Core command definitions
CORE_COMMANDS = {
    'requirements-engineering': [
        {
            'name': 'Generate User Story',
            'slug': 'generate-user-story',
            'description': 'Generate a detailed user story from a feature description',
            'template': '''Generate a user story for: {{feature}}

Context: {{context}}

Please provide:
1. Title (As a [role], I want [goal], so that [benefit])
2. Detailed description
3. Acceptance criteria (Given/When/Then format)
4. Estimated story points (1, 2, 3, 5, 8, 13)
5. Priority recommendation (High/Medium/Low)''',
            'parameters': [
                {
                    'name': 'feature',
                    'type': 'string',
                    'required': True,
                    'description': 'Feature or capability to create a story for'
                },
                {
                    'name': 'context',
                    'type': 'string',
                    'required': False,
                    'description': 'Additional context (target users, technical constraints, etc.)'
                }
            ],
            'recommended_agent': 'Business Analyst Agent',
            'example_usage': 'feature: "User login with JWT authentication"',
            'tags': ['agile', 'requirements', 'user-story']
        },
        {
            'name': 'Extract Requirements',
            'slug': 'extract-requirements',
            'description': 'Extract structured requirements from unstructured text',
            'template': '''Analyze the following description and extract clear, testable requirements:

{{description}}

Please provide:
1. Functional requirements (numbered list)
2. Non-functional requirements (performance, security, usability)
3. Dependencies and constraints
4. Out of scope items''',
            'parameters': [
                {
                    'name': 'description',
                    'type': 'text',
                    'required': True,
                    'description': 'Unstructured description or requirements document'
                }
            ],
            'recommended_agent': 'Requirements Engineer Agent',
            'example_usage': 'description: "We need a system that allows users to..."',
            'tags': ['requirements', 'analysis']
        },
        {
            'name': 'Create Acceptance Criteria',
            'slug': 'create-acceptance-criteria',
            'description': 'Generate acceptance criteria for a user story',
            'template': '''Create comprehensive acceptance criteria for this user story:

Story: {{story}}

Provide criteria in Given/When/Then format:
- Given [initial context]
- When [action occurs]
- Then [expected outcome]

Include edge cases and error scenarios.''',
            'parameters': [
                {
                    'name': 'story',
                    'type': 'text',
                    'required': True,
                    'description': 'User story description'
                }
            ],
            'recommended_agent': 'Business Analyst Agent',
            'example_usage': 'story: "As a user, I want to reset my password"',
            'tags': ['acceptance-criteria', 'testing']
        },
        {
            'name': 'Prioritize Backlog',
            'slug': 'prioritize-backlog',
            'description': 'Prioritize backlog items using MoSCoW or Value/Effort matrix',
            'template': '''Prioritize these backlog items:

{{stories}}

Method: {{method}}

Provide:
1. Prioritized list with rationale
2. Value/Effort assessment for each
3. Dependencies identified
4. Recommended sprint groupings''',
            'parameters': [
                {
                    'name': 'stories',
                    'type': 'text',
                    'required': True,
                    'description': 'List of backlog items (one per line)'
                },
                {
                    'name': 'method',
                    'type': 'choice',
                    'choices': ['MoSCoW', 'Value-Effort', 'RICE', 'Kano'],
                    'required': False,
                    'description': 'Prioritization method to use'
                }
            ],
            'recommended_agent': 'Project Manager Agent',
            'example_usage': 'stories: "Login, Password reset, User profile" method: "Value-Effort"',
            'tags': ['prioritization', 'backlog']
        },
        {
            'name': 'Generate Epic',
            'slug': 'generate-epic',
            'description': 'Create an epic from a high-level theme or initiative',
            'template': '''Create an epic for: {{theme}}

Business context: {{business_context}}

Provide:
1. Epic title and description
2. Business value and goals
3. Key user personas affected
4. High-level user stories (3-5 stories)
5. Success metrics
6. Timeline estimate''',
            'parameters': [
                {
                    'name': 'theme',
                    'type': 'string',
                    'required': True,
                    'description': 'High-level theme or initiative'
                },
                {
                    'name': 'business_context',
                    'type': 'text',
                    'required': False,
                    'description': 'Business context and objectives'
                }
            ],
            'recommended_agent': 'Business Analyst Agent',
            'example_usage': 'theme: "User Authentication System"',
            'tags': ['epic', 'planning']
        },
        {
            'name': 'Define Use Cases',
            'slug': 'define-use-cases',
            'description': 'Define use cases for a feature or system',
            'template': '''Define use cases for: {{feature}}

For each use case provide:
1. Use case name
2. Primary actor
3. Preconditions
4. Main flow (numbered steps)
5. Alternative flows
6. Postconditions
7. Exception handling''',
            'parameters': [
                {
                    'name': 'feature',
                    'type': 'string',
                    'required': True,
                    'description': 'Feature to define use cases for'
                }
            ],
            'recommended_agent': 'Requirements Engineer Agent',
            'example_usage': 'feature: "E-commerce checkout process"',
            'tags': ['use-cases', 'requirements']
        },
        {
            'name': 'Create User Personas',
            'slug': 'create-user-personas',
            'description': 'Create detailed user personas for product design',
            'template': '''Create 2-3 user personas for: {{product}}

Target audience: {{target_audience}}

For each persona include:
1. Name and photo description
2. Demographics (age, location, occupation)
3. Goals and motivations
4. Pain points and frustrations
5. Technical proficiency
6. Key behaviors and preferences
7. Quote that captures their mindset''',
            'parameters': [
                {
                    'name': 'product',
                    'type': 'string',
                    'required': True,
                    'description': 'Product or system'
                },
                {
                    'name': 'target_audience',
                    'type': 'text',
                    'required': False,
                    'description': 'Description of target audience'
                }
            ],
            'recommended_agent': 'UX Designer Agent',
            'example_usage': 'product: "Project management tool for developers"',
            'tags': ['personas', 'ux']
        },
        {
            'name': 'Map User Journey',
            'slug': 'map-user-journey',
            'description': 'Create a user journey map for a specific flow',
            'template': '''Create a user journey map for: {{journey}}

Persona: {{persona}}

Map the journey with:
1. Stages (Awareness, Consideration, Purchase, Retention, Advocacy)
2. User actions at each stage
3. Touchpoints (where user interacts with product)
4. Emotions (emotional state at each stage)
5. Pain points
6. Opportunities for improvement''',
            'parameters': [
                {
                    'name': 'journey',
                    'type': 'string',
                    'required': True,
                    'description': 'User journey to map (e.g., "signing up for service")'
                },
                {
                    'name': 'persona',
                    'type': 'string',
                    'required': False,
                    'description': 'User persona for this journey'
                }
            ],
            'recommended_agent': 'UX Designer Agent',
            'example_usage': 'journey: "First-time user onboarding"',
            'tags': ['journey-map', 'ux']
        },
        {
            'name': 'Analyze Stakeholders',
            'slug': 'analyze-stakeholders',
            'description': 'Identify and analyze project stakeholders',
            'template': '''Analyze stakeholders for: {{project}}

Provide:
1. Stakeholder list (grouped by category)
2. Power/Interest matrix
3. Influence and impact assessment
4. Communication strategy for each group
5. Potential risks from stakeholder resistance''',
            'parameters': [
                {
                    'name': 'project',
                    'type': 'string',
                    'required': True,
                    'description': 'Project or initiative'
                }
            ],
            'recommended_agent': 'Business Analyst Agent',
            'example_usage': 'project: "Legacy system migration"',
            'tags': ['stakeholders', 'analysis']
        },
        {
            'name': 'Generate BRD',
            'slug': 'generate-brd',
            'description': 'Generate a Business Requirements Document outline',
            'template': '''Create a Business Requirements Document (BRD) for: {{project}}

Business objectives: {{objectives}}

Include sections:
1. Executive Summary
2. Business Objectives
3. Scope (In-scope / Out-of-scope)
4. Stakeholders
5. Business Requirements (numbered)
6. Assumptions and Constraints
7. Success Criteria
8. Timeline and Milestones''',
            'parameters': [
                {
                    'name': 'project',
                    'type': 'string',
                    'required': True,
                    'description': 'Project name'
                },
                {
                    'name': 'objectives',
                    'type': 'text',
                    'required': False,
                    'description': 'Business objectives'
                }
            ],
            'recommended_agent': 'Business Analyst Agent',
            'example_usage': 'project: "Customer portal implementation"',
            'tags': ['brd', 'documentation']
        },
    ],
    
    'code-generation': [
        {
            'name': 'Generate Django Model',
            'slug': 'generate-django-model',
            'description': 'Create a Django model with fields and relationships',
            'template': '''Create a Django model for: {{entity}}

Fields: {{fields}}

Requirements:
- Use appropriate field types
- Add validators where needed
- Include Meta class with db_table, ordering, indexes
- Add __str__ method
- Use UUID as primary key
- Add created_at/updated_at timestamps''',
            'parameters': [
                {
                    'name': 'entity',
                    'type': 'string',
                    'required': True,
                    'description': 'Name of the entity (e.g., "Product", "Order")'
                },
                {
                    'name': 'fields',
                    'type': 'text',
                    'required': True,
                    'description': 'List of fields with types (e.g., "title:string, price:decimal")'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'entity: "Product" fields: "name:string, price:decimal, category:foreign_key"',
            'tags': ['django', 'model', 'backend']
        },
        {
            'name': 'Generate API Endpoint',
            'slug': 'generate-api-endpoint',
            'description': 'Create a Django REST Framework API endpoint',
            'template': '''Create a DRF API endpoint for: {{resource}}

Actions needed: {{actions}}

Generate:
1. ViewSet class with proper methods
2. URL routing configuration
3. Permission classes
4. Filtering and pagination setup
5. Swagger/OpenAPI documentation''',
            'parameters': [
                {
                    'name': 'resource',
                    'type': 'string',
                    'required': True,
                    'description': 'Resource name (e.g., "posts", "users")'
                },
                {
                    'name': 'actions',
                    'type': 'string',
                    'required': False,
                    'description': 'CRUD actions needed (default: all)'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'resource: "products" actions: "list, retrieve, create"',
            'tags': ['django', 'api', 'rest']
        },
        {
            'name': 'Generate DRF Serializer',
            'slug': 'generate-drf-serializer',
            'description': 'Create a Django REST Framework serializer',
            'template': '''Create a DRF serializer for model: {{model}}

Include:
- All model fields
- Read-only fields (id, timestamps)
- Nested serializers for relationships
- Custom validation methods
- SerializerMethodFields for computed properties''',
            'parameters': [
                {
                    'name': 'model',
                    'type': 'string',
                    'required': True,
                    'description': 'Model name'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'model: "Product"',
            'tags': ['django', 'serializer', 'drf']
        },
        {
            'name': 'Generate React Component',
            'slug': 'generate-react-component',
            'description': 'Create a React functional component with TypeScript',
            'template': '''Create a React component: {{component_name}}

Type: {{component_type}}
Props: {{props}}

Generate:
1. TypeScript interface for props
2. Functional component with hooks
3. Event handlers
4. Tailwind CSS styling
5. PropTypes/prop validation''',
            'parameters': [
                {
                    'name': 'component_name',
                    'type': 'string',
                    'required': True,
                    'description': 'Component name (PascalCase)'
                },
                {
                    'name': 'component_type',
                    'type': 'choice',
                    'choices': ['form', 'list', 'card', 'modal', 'table', 'custom'],
                    'required': False,
                    'description': 'Type of component'
                },
                {
                    'name': 'props',
                    'type': 'text',
                    'required': False,
                    'description': 'Props definition'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'component_name: "ProductCard" component_type: "card"',
            'tags': ['react', 'typescript', 'frontend']
        },
        {
            'name': 'Generate Test Suite',
            'slug': 'generate-test-suite',
            'description': 'Generate comprehensive test suite for a module',
            'template': '''Generate tests for: {{module}}

Code:
{{code}}

Create tests for:
1. Happy path scenarios
2. Edge cases
3. Error handling
4. Boundary conditions
5. Mock external dependencies''',
            'parameters': [
                {
                    'name': 'module',
                    'type': 'string',
                    'required': True,
                    'description': 'Module or function name'
                },
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Code to test'
                }
            ],
            'recommended_agent': 'QA Agent',
            'example_usage': 'module: "authentication_service"',
            'tags': ['testing', 'unit-tests']
        },
        # Continue with 15 more code generation commands...
        {
            'name': 'Generate Database Migration',
            'slug': 'generate-database-migration',
            'description': 'Create a Django database migration',
            'template': '''Create a migration for these changes:

{{changes}}

Generate migration that:
- Adds/modifies fields safely
- Includes data migrations if needed
- Handles indexes and constraints
- Is reversible''',
            'parameters': [
                {
                    'name': 'changes',
                    'type': 'text',
                    'required': True,
                    'description': 'Description of database changes'
                }
            ],
            'recommended_agent': 'Database Specialist Agent',
            'example_usage': 'changes: "Add email_verified field to User model"',
            'tags': ['django', 'migration', 'database']
        },
        {
            'name': 'Generate Form Validation',
            'slug': 'generate-form-validation',
            'description': 'Create form validation logic',
            'template': '''Create validation for form with fields:

{{fields}}

Requirements:
- Client-side validation (JavaScript/TypeScript)
- Server-side validation
- Error messages
- Regex patterns for complex fields
- Custom validators''',
            'parameters': [
                {
                    'name': 'fields',
                    'type': 'text',
                    'required': True,
                    'description': 'Form fields to validate'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'fields: "email, password, age"',
            'tags': ['validation', 'forms']
        },
        {
            'name': 'Generate API Client',
            'slug': 'generate-api-client',
            'description': 'Create API client/SDK for service integration',
            'template': '''Create an API client for: {{service}}

Base URL: {{base_url}}
Authentication: {{auth_type}}

Generate:
1. Client class with methods for each endpoint
2. Request/response type definitions
3. Error handling
4. Retry logic
5. Rate limiting''',
            'parameters': [
                {
                    'name': 'service',
                    'type': 'string',
                    'required': True,
                    'description': 'Service name'
                },
                {
                    'name': 'base_url',
                    'type': 'string',
                    'required': False,
                    'description': 'API base URL'
                },
                {
                    'name': 'auth_type',
                    'type': 'choice',
                    'choices': ['API-Key', 'Bearer-Token', 'OAuth2', 'Basic-Auth'],
                    'required': False,
                    'description': 'Authentication method'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'service: "Stripe Payment API"',
            'tags': ['api-client', 'integration']
        },
        {
            'name': 'Generate Celery Task',
            'slug': 'generate-celery-task',
            'description': 'Create async Celery task for background processing',
            'template': '''Create a Celery task for: {{task_description}}

Requirements:
- Task definition with @shared_task decorator
- Error handling and retries
- Progress tracking
- Result backend configuration
- Logging''',
            'parameters': [
                {
                    'name': 'task_description',
                    'type': 'text',
                    'required': True,
                    'description': 'What the task should do'
                }
            ],
            'recommended_agent': 'DevOps Agent',
            'example_usage': 'task_description: "Send email notification to users"',
            'tags': ['celery', 'async', 'background-jobs']
        },
        {
            'name': 'Generate Docker Configuration',
            'slug': 'generate-docker-config',
            'description': 'Create Dockerfile and docker-compose.yml',
            'template': '''Create Docker configuration for: {{app_type}}

Tech stack: {{tech_stack}}

Generate:
1. Dockerfile (multi-stage if applicable)
2. docker-compose.yml
3. .dockerignore
4. Environment variable template''',
            'parameters': [
                {
                    'name': 'app_type',
                    'type': 'choice',
                    'choices': ['django', 'react', 'nodejs', 'python', 'fullstack'],
                    'required': True,
                    'description': 'Application type'
                },
                {
                    'name': 'tech_stack',
                    'type': 'text',
                    'required': False,
                    'description': 'Technology stack details'
                }
            ],
            'recommended_agent': 'DevOps Agent',
            'example_usage': 'app_type: "django" tech_stack: "Django 5.0, PostgreSQL, Redis"',
            'tags': ['docker', 'devops']
        },
        # Adding 10 more code generation commands to reach 20 total
        {
            'name': 'Generate GraphQL Schema',
            'slug': 'generate-graphql-schema',
            'description': 'Create GraphQL schema and resolvers',
            'template': '''Create GraphQL schema for: {{entity}}

Include:
- Type definitions
- Query resolvers
- Mutation resolvers
- Input types
- Pagination''',
            'parameters': [
                {
                    'name': 'entity',
                    'type': 'string',
                    'required': True,
                    'description': 'Entity name'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'entity: "User"',
            'tags': ['graphql', 'api']
        },
        {
            'name': 'Generate Redux Slice',
            'slug': 'generate-redux-slice',
            'description': 'Create Redux Toolkit slice with actions and reducers',
            'template': '''Create Redux slice for: {{feature}}

State shape: {{state}}

Include:
- Initial state
- Reducers
- Actions
- Selectors
- Async thunks''',
            'parameters': [
                {
                    'name': 'feature',
                    'type': 'string',
                    'required': True,
                    'description': 'Feature name'
                },
                {
                    'name': 'state',
                    'type': 'text',
                    'required': False,
                    'description': 'State structure'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'feature: "authentication"',
            'tags': ['redux', 'state-management']
        },
        {
            'name': 'Generate SQL Query',
            'slug': 'generate-sql-query',
            'description': 'Generate optimized SQL query from requirements',
            'template': '''Create SQL query for: {{requirement}}

Tables: {{tables}}

Requirements:
- Use proper JOINs
- Add indexes where needed
- Optimize for performance
- Include WHERE clauses''',
            'parameters': [
                {
                    'name': 'requirement',
                    'type': 'text',
                    'required': True,
                    'description': 'Query requirement description'
                },
                {
                    'name': 'tables',
                    'type': 'text',
                    'required': False,
                    'description': 'Involved tables and columns'
                }
            ],
            'recommended_agent': 'Database Specialist Agent',
            'example_usage': 'requirement: "Get all orders with customer details from last month"',
            'tags': ['sql', 'database']
        },
        {
            'name': 'Generate REST API Documentation',
            'slug': 'generate-api-docs',
            'description': 'Create OpenAPI/Swagger documentation',
            'template': '''Generate API documentation for endpoint:

Method: {{method}}
Path: {{path}}
Description: {{description}}

Include:
- Request parameters
- Request body schema
- Response schemas (200, 400, 500)
- Examples
- Authentication requirements''',
            'parameters': [
                {
                    'name': 'method',
                    'type': 'choice',
                    'choices': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                    'required': True,
                    'description': 'HTTP method'
                },
                {
                    'name': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'API path'
                },
                {
                    'name': 'description',
                    'type': 'text',
                    'required': False,
                    'description': 'Endpoint description'
                }
            ],
            'recommended_agent': 'Documentation Agent',
            'example_usage': 'method: "POST" path: "/api/users/" description: "Create new user"',
            'tags': ['documentation', 'api']
        },
        {
            'name': 'Generate Middleware',
            'slug': 'generate-middleware',
            'description': 'Create Django middleware component',
            'template': '''Create Django middleware for: {{purpose}}

Requirements:
- Process request/response
- Handle exceptions
- Add custom headers
- Logging
- Performance tracking''',
            'parameters': [
                {
                    'name': 'purpose',
                    'type': 'text',
                    'required': True,
                    'description': 'Middleware purpose (e.g., "request logging", "CORS handling")'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'purpose: "Request/Response logging with timing"',
            'tags': ['django', 'middleware']
        },
        {
            'name': 'Generate WebSocket Handler',
            'slug': 'generate-websocket-handler',
            'description': 'Create WebSocket connection handler',
            'template': '''Create WebSocket handler for: {{feature}}

Framework: {{framework}}

Include:
- Connection/disconnection handlers
- Message handlers
- Broadcasting
- Error handling
- Authentication''',
            'parameters': [
                {
                    'name': 'feature',
                    'type': 'string',
                    'required': True,
                    'description': 'Feature using WebSocket'
                },
                {
                    'name': 'framework',
                    'type': 'choice',
                    'choices': ['Django Channels', 'Socket.io', 'FastAPI WebSocket'],
                    'required': False,
                    'description': 'WebSocket framework'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'feature: "Real-time chat"',
            'tags': ['websocket', 'realtime']
        },
        {
            'name': 'Generate Custom Hook',
            'slug': 'generate-custom-hook',
            'description': 'Create React custom hook',
            'template': '''Create React custom hook: {{hook_name}}

Purpose: {{purpose}}

Include:
- Hook implementation with proper dependencies
- TypeScript types
- Error handling
- Cleanup logic
- Usage example''',
            'parameters': [
                {
                    'name': 'hook_name',
                    'type': 'string',
                    'required': True,
                    'description': 'Hook name (e.g., useFetchData, useAuth)'
                },
                {
                    'name': 'purpose',
                    'type': 'text',
                    'required': True,
                    'description': 'What the hook does'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'hook_name: "useFetchData" purpose: "Fetch data with loading and error states"',
            'tags': ['react', 'hooks']
        },
        {
            'name': 'Generate Authentication System',
            'slug': 'generate-auth-system',
            'description': 'Create complete authentication system',
            'template': '''Generate authentication system using: {{auth_type}}

Include:
- User model/schema
- Registration endpoint
- Login endpoint
- Token generation/validation
- Password reset flow
- Email verification''',
            'parameters': [
                {
                    'name': 'auth_type',
                    'type': 'choice',
                    'choices': ['JWT', 'Session', 'OAuth2', 'API-Key'],
                    'required': True,
                    'description': 'Authentication type'
                }
            ],
            'recommended_agent': 'Security Specialist Agent',
            'example_usage': 'auth_type: "JWT"',
            'tags': ['authentication', 'security']
        },
        {
            'name': 'Generate CRUD Service',
            'slug': 'generate-crud-service',
            'description': 'Create complete CRUD service layer',
            'template': '''Create CRUD service for: {{entity}}

Include:
- Create method with validation
- Read (single and list) with filtering
- Update (full and partial)
- Delete with soft delete option
- Pagination
- Error handling''',
            'parameters': [
                {
                    'name': 'entity',
                    'type': 'string',
                    'required': True,
                    'description': 'Entity name'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'entity: "Product"',
            'tags': ['crud', 'service']
        },
        {
            'name': 'Generate Email Template',
            'slug': 'generate-email-template',
            'description': 'Create HTML email template',
            'template': '''Create email template for: {{purpose}}

Include:
- HTML structure
- Inline CSS for email clients
- Responsive design
- Dynamic content placeholders
- Plain text fallback''',
            'parameters': [
                {
                    'name': 'purpose',
                    'type': 'string',
                    'required': True,
                    'description': 'Email purpose (e.g., "welcome email", "password reset")'
                }
            ],
            'recommended_agent': 'Coding Agent',
            'example_usage': 'purpose: "Welcome email for new users"',
            'tags': ['email', 'template']
        },
    ],
    
    # Code Review commands (15)
    'code-review': [
        {
            'name': 'Review Code Quality',
            'slug': 'review-code-quality',
            'description': 'Comprehensive code quality review',
            'template': '''Review this code for quality issues:

{{code}}

Language: {{language}}

Check for:
1. Code readability and maintainability
2. Naming conventions
3. Code duplication  
4. Complexity (cyclomatic complexity)
5. SOLID principles violations
6. Design patterns usage
7. Error handling
8. Logging and debugging
9. Performance issues
10. Best practices compliance

Provide:
- Issues found (severity: Critical/High/Medium/Low)
- Suggested improvements
- Code examples of fixes''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Code to review'
                },
                {
                    'name': 'language',
                    'type': 'choice',
                    'choices': ['Python', 'JavaScript', 'TypeScript', 'Java', 'C#', 'Go'],
                    'required': False,
                    'description': 'Programming language'
                }
            ],
            'recommended_agent': 'Code Review Agent',
            'example_usage': 'code: "def process_data(data): ..."',
            'tags': ['code-review', 'quality']
        },
        {
            'name': 'Security Audit',
            'slug': 'security-audit',
            'description': 'Security vulnerability assessment',
            'template': '''Perform security audit on:

{{code}}

Check for:
1. SQL injection vulnerabilities
2. XSS (Cross-Site Scripting)
3. CSRF protection
4. Authentication/Authorization flaws
5. Sensitive data exposure
6. Cryptographic issues
7. Input validation
8. Output encoding
9. Dependency vulnerabilities
10. Security misconfigurations

OWASP Top 10 compliance check.

Provide:
- Vulnerabilities found (with CVE if applicable)
- Risk level  
- Remediation steps''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Code or configuration to audit'
                }
            ],
            'recommended_agent': 'Security Specialist Agent',
            'example_usage': 'code: "SQL query building code"',
            'tags': ['security', 'audit', 'owasp']
        },
        {
            'name': 'Identify Code Smells',
            'slug': 'identify-code-smells',
            'description': 'Detect code smells and anti-patterns',
            'template': '''Identify code smells in:

{{code}}

Look for:
1. Long methods/functions
2. Large classes
3. Long parameter lists
4. Feature envy
5. Data clumps
6. Primitive obsession
7. Switch statements
8. Speculative generality
9. Dead code
10. Comments (excessive or outdated)

For each smell found:
- Location
- Type of smell
- Why it's problematic
- Refactoring suggestion''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Code to analyze'
                }
            ],
            'recommended_agent': 'Code Review Agent',
            'example_usage': 'code: "class with 1000 lines"',
            'tags': ['code-smells', 'refactoring']
        },
        {
            'name': 'Suggest Refactoring',
            'slug': 'suggest-refactoring',
            'description': 'Provide refactoring recommendations',
            'template': '''Suggest refactorings for:

{{code}}

Focus areas: {{focus}}

Provide:
1. Current problems
2. Refactoring techniques to apply
3. Before/after code examples
4. Benefits of refactoring
5. Potential risks
6. Step-by-step refactoring plan''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Code to refactor'
                },
                {
                    'name': 'focus',
                    'type': 'string',
                    'required': False,
                    'description': 'Specific areas to focus on'
                }
            ],
            'recommended_agent': 'Architect Agent',
            'example_usage': 'code: "legacy function with multiple responsibilities"',
            'tags': ['refactoring', 'architecture']
        },
        {
            'name': 'Check Best Practices',
            'slug': 'check-best-practices',
            'description': 'Verify adherence to language best practices',
            'template': '''Check best practices for {{language}} code:

{{code}}

Verify:
1. PEP 8 (Python) / ESLint (JS) / Language-specific style guide
2. Naming conventions
3. Module/package structure
4. Documentation standards
5. Testing conventions
6. Error handling patterns
7. Resource management
8. Concurrency patterns
9. Framework-specific best practices

List violations and corrections.''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Code to check'
                },
                {
                    'name': 'language',
                    'type': 'choice',
                    'choices': ['Python', 'JavaScript', 'TypeScript', 'Java', 'Go', 'Rust'],
                    'required': True,
                    'description': 'Programming language'
                }
            ],
            'recommended_agent': 'Code Review Agent',
            'example_usage': 'language: "Python" code: "class MyClass: ..."',
            'tags': ['best-practices', 'style-guide']
        },
        {
            'name': 'Performance Review',
            'slug': 'performance-review',
            'description': 'Analyze code for performance issues',
            'template': '''Review performance of:

{{code}}

Check for:
1. Big O complexity issues
2. N+1 query problems
3. Inefficient algorithms
4. Memory leaks
5. Unnecessary computations
6. Caching opportunities
7. Database query optimization
8. API call optimization
9. Resource usage
10. Scalability concerns

Provide benchmarks and optimized versions.''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Code to analyze'
                }
            ],
            'recommended_agent': 'Architect Agent',
            'example_usage': 'code: "database query with multiple joins"',
            'tags': ['performance', 'optimization']
        },
        # Adding 9 more code review commands
        {
            'name': 'Check Test Coverage',
            'slug': 'check-test-coverage',
            'description': 'Analyze test coverage and identify gaps',
            'template': '''Analyze test coverage for:

{{code}}

Tests:
{{tests}}

Report:
- Coverage percentage by component
- Uncovered code paths
- Missing edge cases
- Test quality assessment
- Recommendations for additional tests''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Production code'
                },
                {
                    'name': 'tests',
                    'type': 'text',
                    'required': False,
                    'description': 'Existing test code'
                }
            ],
            'recommended_agent': 'QA Agent',
            'example_usage': 'code: "authentication service"',
            'tags': ['testing', 'coverage']
        },
        {
            'name': 'Review API Design',
            'slug': 'review-api-design',
            'description': 'Review RESTful API design',
            'template': '''Review API design:

{{api_spec}}

Check:
- RESTful principles
- Resource naming
- HTTP methods usage
- Status codes
- Versioning strategy
- Pagination
- Filtering/sorting
- Error responses
- Rate limiting
- Documentation

Provide improvement suggestions.''',
            'parameters': [
                {
                    'name': 'api_spec',
                    'type': 'text',
                    'required': True,
                    'description': 'API specification or code'
                }
            ],
            'recommended_agent': 'Architect Agent',
            'example_usage': 'api_spec: "OpenAPI/Swagger definition"',
            'tags': ['api', 'rest', 'design']
        },
        {
            'name': 'Check Accessibility',
            'slug': 'check-accessibility',
            'description': 'Review code for accessibility compliance',
            'template': '''Check accessibility (WCAG 2.1) for:

{{code}}

Verify:
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader compatibility
- Color contrast
- Focus management
- Alt text for images
- Form labels
- Error messages

Provide WCAG compliance report.''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'HTML/React/Vue component code'
                }
            ],
            'recommended_agent': 'UX Designer Agent',
            'example_usage': 'code: "React form component"',
            'tags': ['accessibility', 'wcag', 'a11y']
        },
        {
            'name': 'Review Database Schema',
            'slug': 'review-database-schema',
            'description': 'Analyze database schema design',
            'template': '''Review database schema:

{{schema}}

Check:
- Normalization (1NF, 2NF, 3NF)
- Indexes and keys
- Relationships and constraints
- Data types
- Naming conventions
- Scalability
- Performance optimization
- Denormalization opportunities

Provide optimization recommendations.''',
            'parameters': [
                {
                    'name': 'schema',
                    'type': 'text',
                    'required': True,
                    'description': 'Database schema (SQL or ORM models)'
                }
            ],
            'recommended_agent': 'Database Specialist Agent',
            'example_usage': 'schema: "Django models or SQL CREATE statements"',
            'tags': ['database', 'schema']
        },
        {
            'name': 'Check Error Handling',
            'slug': 'check-error-handling',
            'description': 'Review error handling implementation',
            'template': '''Review error handling in:

{{code}}

Check for:
- Try-catch blocks usage
- Exception hierarchies
- Error logging
- User-friendly error messages
- Recovery mechanisms
- Resource cleanup
- Error propagation
- Circuit breakers

Identify missing error handling.''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Code to review'
                }
            ],
            'recommended_agent': 'Code Review Agent',
            'example_usage': 'code: "API endpoint with database calls"',
            'tags': ['error-handling', 'reliability']
        },
        {
            'name': 'Review Concurrency',
            'slug': 'review-concurrency',
            'description': 'Check concurrent code for race conditions',
            'template': '''Review concurrent code:

{{code}}

Check for:
- Race conditions
- Deadlocks
- Thread safety
- Atomic operations
- Lock usage
- Async/await patterns
- Shared state management
- Memory visibility

Suggest improvements.''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Concurrent/parallel code'
                }
            ],
            'recommended_agent': 'Architect Agent',
            'example_usage': 'code: "multi-threaded worker"',
            'tags': ['concurrency', 'threading']
        },
        {
            'name': 'Check Dependencies',
            'slug': 'check-dependencies',
            'description': 'Review project dependencies for issues',
            'template': '''Analyze dependencies:

{{dependencies}}

Check:
- Outdated packages
- Security vulnerabilities (CVE)
- License compliance
- Dependency conflicts
- Unused dependencies
- Bundle size impact
- Update recommendations

Provide upgrade plan.''',
            'parameters': [
                {
                    'name': 'dependencies',
                    'type': 'text',
                    'required': True,
                    'description': 'package.json, requirements.txt, or similar'
                }
            ],
            'recommended_agent': 'DevOps Agent',
            'example_usage': 'dependencies: "requirements.txt content"',
            'tags': ['dependencies', 'security']
        },
        {
            'name': 'Review Documentation',
            'slug': 'review-documentation',
            'description': 'Check code documentation quality',
            'template': '''Review documentation for:

{{code}}

Check:
- Docstrings/JSDoc completeness
- API documentation
- README clarity
- Code comments quality
- Examples and usage
- Architecture diagrams
- Changelog
- Contributing guide

Suggest improvements.''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Code or documentation to review'
                }
            ],
            'recommended_agent': 'Documentation Agent',
            'example_usage': 'code: "module with functions"',
            'tags': ['documentation', 'comments']
        },
        {
            'name': 'Check Mobile Responsiveness',
            'slug': 'check-mobile-responsiveness',
            'description': 'Review UI code for mobile responsiveness',
            'template': '''Check mobile responsiveness:

{{code}}

Verify:
- Media queries
- Flexbox/Grid usage
- Touch targets (44x44px minimum)
- Text readability
- Image optimization
- Viewport meta tag
- Mobile-first approach
- Cross-device testing

Provide improvement suggestions.''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'CSS/HTML/React code'
                }
            ],
            'recommended_agent': 'UX Designer Agent',
            'example_usage': 'code: "React component with styles"',
            'tags': ['mobile', 'responsive', 'ui']
        },
    ],
    
    # Testing commands (5)
    'testing-qa': [
        {
            'name': 'Generate Unit Tests',
            'slug': 'generate-unit-tests',
            'description': 'Create comprehensive unit tests',
            'template': '''Generate unit tests for:

{{code}}

Framework: {{framework}}

Include:
- Test setup and teardown
- Happy path tests
- Edge cases
- Error scenarios
- Mocking external dependencies
- Assertions for all outcomes
- Test data fixtures''',
            'parameters': [
                {
                    'name': 'code',
                    'type': 'text',
                    'required': True,
                    'description': 'Code to test'
                },
                {
                    'name': 'framework',
                    'type': 'choice',
                    'choices': ['pytest', 'unittest', 'jest', 'mocha', 'JUnit'],
                    'required': False,
                    'description': 'Testing framework'
                }
            ],
            'recommended_agent': 'QA Agent',
            'example_usage': 'code: "function calculate_total(items)" framework: "pytest"',
            'tags': ['testing', 'unit-tests']
        },
        {
            'name': 'Generate Integration Tests',
            'slug': 'generate-integration-tests',
            'description': 'Create integration/E2E tests',
            'template': '''Create integration tests for:

{{feature}}

Test type: {{test_type}}

Include:
- Multi-component interactions
- Database operations
- API calls
- Authentication flows
- Data consistency checks
- Cleanup procedures''',
            'parameters': [
                {
                    'name': 'feature',
                    'type': 'text',
                    'required': True,
                    'description': 'Feature to test'
                },
                {
                    'name': 'test_type',
                    'type': 'choice',
                    'choices': ['integration', 'e2e', 'api'],
                    'required': False,
                    'description': 'Type of test'
                }
            ],
            'recommended_agent': 'QA Agent',
            'example_usage': 'feature: "User registration flow"',
            'tags': ['integration-tests', 'e2e']
        },
        {
            'name': 'Create Test Data',
            'slug': 'create-test-data',
            'description': 'Generate test data and fixtures',
            'template': '''Create test data for: {{model}}

Quantity: {{quantity}}
Format: {{format}}

Generate:
- Realistic sample data
- Edge cases (null, empty, max length)
- Invalid data for negative tests
- Related object data
- Factory/fixture code''',
            'parameters': [
                {
                    'name': 'model',
                    'type': 'string',
                    'required': True,
                    'description': 'Model or entity name'
                },
                {
                    'name': 'quantity',
                    'type': 'integer',
                    'required': False,
                    'description': 'Number of records to generate'
                },
                {
                    'name': 'format',
                    'type': 'choice',
                    'choices': ['JSON', 'SQL', 'Python', 'CSV'],
                    'required': False,
                    'description': 'Output format'
                }
            ],
            'recommended_agent': 'QA Agent',
            'example_usage': 'model: "User" quantity: 10 format: "JSON"',
            'tags': ['test-data', 'fixtures']
        },
        {
            'name': 'Generate Load Tests',
            'slug': 'generate-load-tests',
            'description': 'Create performance/load tests',
            'template': '''Create load test for: {{endpoint}}

Tool: {{tool}}
Target: {{target_rps}} requests/second

Include:
- Ramp-up scenarios
- Steady-state load
- Spike testing
- Response time assertions
- Error rate monitoring
- Resource utilization tracking''',
            'parameters': [
                {
                    'name': 'endpoint',
                    'type': 'string',
                    'required': True,
                    'description': 'API endpoint or feature to load test'
                },
                {
                    'name': 'tool',
                    'type': 'choice',
                    'choices': ['locust', 'k6', 'JMeter', 'Artillery'],
                    'required': False,
                    'description': 'Load testing tool'
                },
                {
                    'name': 'target_rps',
                    'type': 'integer',
                    'required': False,
                    'description': 'Target requests per second'
                }
            ],
            'recommended_agent': 'QA Agent',
            'example_usage': 'endpoint: "/api/products/" tool: "locust" target_rps: 100',
            'tags': ['load-testing', 'performance']
        },
        {
            'name': 'Create Smoke Tests',
            'slug': 'create-smoke-tests',
            'description': 'Generate smoke test suite for critical paths',
            'template': '''Create smoke tests for: {{application}}

Critical flows: {{flows}}

Generate quick tests for:
- Application startup
- Database connectivity
- API health checks
- Authentication
- Core user flows
- External service connectivity

Keep tests fast (<30 seconds total).''',
            'parameters': [
                {
                    'name': 'application',
                    'type': 'string',
                    'required': True,
                    'description': 'Application name'
                },
                {
                    'name': 'flows',
                    'type': 'text',
                    'required': False,
                    'description': 'Critical user flows to test'
                }
            ],
            'recommended_agent': 'QA Agent',
            'example_usage': 'application: "E-commerce Platform"',
            'tags': ['smoke-tests', 'sanity-tests']
        },
    ],
}


def load_core_commands():
    """Load 50 core commands into database."""
    
    print("Loading 50 core commands...")
    
    total_loaded = 0
    
    for category_slug, commands in CORE_COMMANDS.items():
        # Get or create category
        try:
            category = CommandCategory.objects.get(slug=category_slug)
            print(f"\nCategory: {category.name}")
        except CommandCategory.DoesNotExist:
            print(f"\nWarning: Category '{category_slug}' not found. Skipping...")
            continue
        
        # Create commands
        for cmd_data in commands:
            # Check if command already exists
            if CommandTemplate.objects.filter(slug=cmd_data['slug']).exists():
                print(f"  [SKIP] {cmd_data['name']} (already exists)")
                continue
            
            # Lookup recommended agent
            agent = None
            agent_name = cmd_data.get('recommended_agent', '')
            if agent_name:
                try:
                    # Try to find agent by name (case-insensitive)
                    agent = Agent.objects.filter(name__icontains=agent_name.split()[0]).first()
                except:
                    pass
            
            # Create command
            command = CommandTemplate.objects.create(
                category=category,
                name=cmd_data['name'],
                slug=cmd_data['slug'],
                description=cmd_data['description'],
                template=cmd_data['template'],
                parameters=cmd_data['parameters'],
                recommended_agent=agent,  # Agent instance or None
                example_usage=cmd_data.get('example_usage', ''),
                tags=cmd_data.get('tags', []),
                is_active=True,
                usage_count=0
            )
            
            total_loaded += 1
            print(f"  [OK] {command.name}")
    
    print(f"\n{'='*60}")
    print(f"Successfully loaded {total_loaded} commands!")
    print(f"{'='*60}")
    
    # Show summary
    total_commands = CommandTemplate.objects.count()
    print(f"\nTotal commands in library: {total_commands}")
    print("\nCommands by category:")
    for category in CommandCategory.objects.all():
        count = CommandTemplate.objects.filter(category=category).count()
        print(f"  - {category.name}: {count} commands")


if __name__ == '__main__':
    load_core_commands()
