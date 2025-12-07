"""
Direct command library loader - adds 30 more commands efficiently.
Run: python load_additional_commands.py
"""

import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')
django.setup()

from apps.commands.models import CommandCategory, CommandTemplate

# Get categories
cats = {cat.slug: cat for cat in CommandCategory.objects.all()}

# Note: Agent references set to null since agents table not migrated to SQLite yet

# Additional Requirements Engineering commands
req_commands = [
    {
        'category': cats['requirements-engineering'],
        'name': 'Generate Use Case Documentation',
        'slug': 'generate-use-case-docs',
        'description': 'Create detailed use case documentation with actors, flows, and scenarios',
        'template': 'Create detailed use case documentation for: {{use_case_title}}\n\nActors: {{actors}}\nGoal: {{goal}}\n\nProvide comprehensive use case with main flow, alternative flows, and exception flows.',
        'parameters': [
            {'name': 'use_case_title', 'type': 'text', 'required': True, 'description': 'Use case title'},
            {'name': 'actors', 'type': 'text', 'required': True, 'description': 'List of actors'},
            {'name': 'goal', 'type': 'text', 'required': True, 'description': 'Primary goal'}
        ],
        'tags': ['use-case', 'documentation'],
        'recommended_agent': ba_agent,
        'required_capabilities': ['REQUIREMENTS_ANALYSIS']
    },
    {
        'category': cats['requirements-engineering'],
        'name': 'Create RICE Prioritization Matrix',
        'slug': 'rice-prioritization',
        'description': 'Prioritize features using RICE (Reach, Impact, Confidence, Effort) framework',
        'template': 'Create RICE prioritization for:\n{{features}}\n\nScore each feature on Reach (0-10), Impact (0-10), Confidence (0-100%), Effort (person-weeks). Calculate RICE score.',
        'parameters': [
            {'name': 'features', 'type': 'long_text', 'required': True, 'description': 'List of features to prioritize'}
        ],
        'tags': ['prioritization', 'rice', 'product-management'],
        'recommended_agent': ba_agent,
        'required_capabilities': []
    },
    {
        'category': cats['requirements-engineering'],
        'name': 'Requirements Gap Analysis',
        'slug': 'gap-analysis',
        'description': 'Identify gaps between current and desired state',
        'template': 'Perform gap analysis:\n\nCurrent State:\n{{current_state}}\n\nDesired State:\n{{desired_state}}\n\nIdentify gaps, impacts, and recommendations.',
        'parameters': [
            {'name': 'current_state', 'type': 'long_text', 'required': True, 'description': 'Current state description'},
            {'name': 'desired_state', 'type': 'long_text', 'required': True, 'description': 'Desired state description'}
        ],
        'tags': ['gap-analysis', 'requirements'],
        'recommended_agent': None,
        'required_capabilities': []
    },
    {
        'category': cats['requirements-engineering'],
        'name': 'Generate Product Backlog',
        'slug': 'generate-backlog',
        'description': 'Create prioritized product backlog from requirements',
        'template': 'Create product backlog for:\n\nVision: {{product_vision}}\n\nRequirements:\n{{requirements}}\n\nGenerate prioritized backlog with epics and stories.',
        'parameters': [
            {'name': 'product_vision', 'type': 'text', 'required': True, 'description': 'Product vision statement'},
            {'name': 'requirements', 'type': 'long_text', 'required': True, 'description': 'Requirements list'}
        ],
        'tags': ['backlog', 'agile', 'product-management'],
        'recommended_agent': None,
        'required_capabilities': []
    },
    {
        'category': cats['requirements-engineering'],
        'name': 'Epic Breakdown',
        'slug': 'epic-breakdown',
        'description': 'Break down epic into user stories',
        'template': 'Break down this epic into user stories:\n\n{{epic_description}}\n\nCreate 5-10 user stories, each under 8 story points.',
        'parameters': [
            {'name': 'epic_description', 'type': 'long_text', 'required': True, 'description': 'Epic description'}
        ],
        'tags': ['epic', 'user-stories', 'agile'],
        'recommended_agent': None,
        'required_capabilities': []
    },
]

# Code Generation commands
code_commands = [
    {
        'category': cats['code-generation'],
        'name': 'Generate Database Model',
        'slug': 'generate-db-model',
        'description': 'Create ORM database model with relationships',
        'template': 'Generate {{framework}} database model:\n\nModel: {{model_name}}\nFields: {{fields}}\n\nInclude relationships, indexes, and validation.',
        'parameters': [
            {'name': 'framework', 'type': 'string', 'required': True, 'description': 'ORM framework'},
            {'name': 'model_name', 'type': 'string', 'required': True, 'description': 'Model name'},
            {'name': 'fields', 'type': 'long_text', 'required': True, 'description': 'Field definitions'}
        ],
        'tags': ['database', 'orm', 'models'],
        'recommended_agent': coding_agent,
        'required_capabilities': ['CODE_GENERATION']
    },
    {
        'category': cats['code-generation'],
        'name': 'Create React Component',
        'slug': 'create-react-component',
        'description': 'Generate React component with TypeScript',
        'template': 'Create React component:\n\nName: {{component_name}}\nProps: {{props}}\n\nInclude TypeScript types, hooks, and styling.',
        'parameters': [
            {'name': 'component_name', 'type': 'string', 'required': True, 'description': 'Component name'},
            {'name': 'props', 'type': 'text', 'required': True, 'description': 'Component props'}
        ],
        'tags': ['react', 'frontend', 'typescript'],
        'recommended_agent': coding_agent,
        'required_capabilities': ['CODE_GENERATION']
    },
    {
        'category': cats['code-generation'],
        'name': 'Generate Unit Tests',
        'slug': 'generate-unit-tests',
        'description': 'Create comprehensive unit tests',
        'template': 'Generate {{test_framework}} unit tests for:\n\n```{{language}}\n{{code}}\n```\n\nInclude happy path, edge cases, and error scenarios.',
        'parameters': [
            {'name': 'language', 'type': 'string', 'required': True, 'description': 'Programming language'},
            {'name': 'test_framework', 'type': 'string', 'required': False, 'description': 'Test framework', 'default': 'pytest'},
            {'name': 'code', 'type': 'long_text', 'required': True, 'description': 'Code to test'}
        ],
        'tags': ['testing', 'unit-tests', 'tdd'],
        'recommended_agent': qa_agent,
        'required_capabilities': []
    },
    {
        'category': cats['code-generation'],
        'name': 'Create Service Layer',
        'slug': 'create-service-layer',
        'description': 'Generate service/business logic layer',
        'template': 'Create service layer in {{language}}:\n\nPurpose: {{service_purpose}}\n\nInclude error handling, logging, and validation.',
        'parameters': [
            {'name': 'language', 'type': 'string', 'required': True, 'description': 'Programming language'},
            {'name': 'service_purpose', 'type': 'text', 'required': True, 'description': 'Service purpose'}
        ],
        'tags': ['service-layer', 'architecture'],
        'recommended_agent': coding_agent,
        'required_capabilities': ['CODE_GENERATION']
    },
    {
        'category': cats['code-generation'],
        'name': 'Generate GraphQL Schema',
        'slug': 'generate-graphql-schema',
        'description': 'Create GraphQL schema with types and resolvers',
        'template': 'Create GraphQL schema for {{entity_name}}:\n\nFields: {{fields}}\n\nInclude types, queries, mutations, and resolvers.',
        'parameters': [
            {'name': 'entity_name', 'type': 'string', 'required': True, 'description': 'Entity name'},
            {'name': 'fields', 'type': 'text', 'required': True, 'description': 'Field definitions'}
        ],
        'tags': ['graphql', 'api', 'schema'],
        'recommended_agent': coding_agent,
        'required_capabilities': ['CODE_GENERATION']
    },
    {
        'category': cats['code-generation'],
        'name': 'Create Database Migration',
        'slug': 'create-migration',
        'description': 'Generate database migration script',
        'template': 'Create {{framework}} migration:\n\n{{migration_description}}\n\nInclude up and down migrations with data safety.',
        'parameters': [
            {'name': 'framework', 'type': 'string', 'required': True, 'description': 'Migration framework'},
            {'name': 'migration_description', 'type': 'text', 'required': True, 'description': 'Migration description'}
        ],
        'tags': ['migration', 'database'],
        'recommended_agent': coding_agent,
        'required_capabilities': ['CODE_GENERATION']
    },
    {
        'category': cats['code-generation'],
        'name': 'Generate Authentication Code',
        'slug': 'generate-auth-code',
        'description': 'Create authentication and authorization logic',
        'template': 'Generate {{auth_method}} authentication for {{framework}}.\n\nInclude login, logout, token refresh, and middleware.',
        'parameters': [
            {'name': 'framework', 'type': 'string', 'required': True, 'description': 'Web framework'},
            {'name': 'auth_method', 'type': 'string', 'required': True, 'description': 'Auth method (JWT, OAuth, etc.)'}
        ],
        'tags': ['authentication', 'security'],
        'recommended_agent': coding_agent,
        'required_capabilities': ['CODE_GENERATION']
    },
    {
        'category': cats['code-generation'],
        'name': 'Generate CRUD Operations',
        'slug': 'generate-crud',
        'description': 'Create complete CRUD operations',
        'template': 'Generate CRUD for {{entity_name}} in {{framework}}.\n\nInclude Create, Read, Update, Delete with validation.',
        'parameters': [
            {'name': 'framework', 'type': 'string', 'required': True, 'description': 'Framework'},
            {'name': 'entity_name', 'type': 'string', 'required': True, 'description': 'Entity name'}
        ],
        'tags': ['crud', 'operations'],
        'recommended_agent': coding_agent,
        'required_capabilities': ['CODE_GENERATION']
    },
    {
        'category': cats['code-generation'],
        'name': 'Create Validation Schemas',
        'slug': 'create-validation',
        'description': 'Generate input validation schemas',
        'template': 'Create validation schema in {{language}}:\n\n{{schema_description}}\n\nInclude type checking, constraints, and error messages.',
        'parameters': [
            {'name': 'language', 'type': 'string', 'required': True, 'description': 'Programming language'},
            {'name': 'schema_description', 'type': 'text', 'required': True, 'description': 'Schema requirements'}
        ],
        'tags': ['validation', 'schema'],
        'recommended_agent': coding_agent,
        'required_capabilities': ['CODE_GENERATION']
    },
    {
        'category': cats['code-generation'],
        'name': 'Generate API Documentation',
        'slug': 'generate-api-docs',
        'description': 'Create OpenAPI/Swagger documentation',
        'template': 'Generate API documentation for:\n\nEndpoint: {{endpoint}}\nDescription: {{description}}\n\nCreate OpenAPI 3.0 spec.',
        'parameters': [
            {'name': 'endpoint', 'type': 'string', 'required': True, 'description': 'API endpoint'},
            {'name': 'description', 'type': 'text', 'required': True, 'description': 'Endpoint description'}
        ],
        'tags': ['documentation', 'api', 'openapi'],
        'recommended_agent': doc_agent,
        'required_capabilities': []
    },
]

# Code Review commands
review_commands = [
    {
        'category': cats['code-review'],
        'name': 'Performance Review',
        'slug': 'performance-review',
        'description': 'Analyze code for performance bottlenecks',
        'template': 'Perform performance review on {{language}} code:\n\n```{{language}}\n{{code}}\n```\n\nIdentify bottlenecks, memory issues, and optimization opportunities.',
        'parameters': [
            {'name': 'language', 'type': 'string', 'required': True, 'description': 'Programming language'},
            {'name': 'code', 'type': 'long_text', 'required': True, 'description': 'Code to review'}
        ],
        'tags': ['performance', 'optimization'],
        'recommended_agent': reviewer_agent,
        'required_capabilities': ['CODE_REVIEW']
    },
    {
        'category': cats['code-review'],
        'name': 'Best Practices Check',
        'slug': 'best-practices',
        'description': 'Review code against best practices',
        'template': 'Check {{language}} code against best practices:\n\n```{{language}}\n{{code}}\n```\n\nEvaluate naming, structure, patterns, and conventions.',
        'parameters': [
            {'name': 'language', 'type': 'string', 'required': True, 'description': 'Programming language'},
            {'name': 'code', 'type': 'long_text', 'required': True, 'description': 'Code to review'}
        ],
        'tags': ['best-practices', 'code-quality'],
        'recommended_agent': reviewer_agent,
        'required_capabilities': ['CODE_REVIEW']
    },
    {
        'category': cats['code-review'],
        'name': 'Code Smell Detection',
        'slug': 'code-smells',
        'description': 'Identify code smells and suggest refactoring',
        'template': 'Detect code smells in:\n\n```{{language}}\n{{code}}\n```\n\nIdentify smells and provide refactoring recommendations.',
        'parameters': [
            {'name': 'language', 'type': 'string', 'required': True, 'description': 'Programming language'},
            {'name': 'code', 'type': 'long_text', 'required': True, 'description': 'Code to analyze'}
        ],
        'tags': ['code-smells', 'refactoring'],
        'recommended_agent': reviewer_agent,
        'required_capabilities': ['CODE_REVIEW']
    },
    {
        'category': cats['code-review'],
        'name': 'Dependency Security Audit',
        'slug': 'dependency-audit',
        'description': 'Analyze dependencies for security vulnerabilities',
        'template': 'Audit dependencies in {{language}} project:\n\n{{package_file}}\n\nCheck for vulnerabilities, outdated packages, and license issues.',
        'parameters': [
            {'name': 'language', 'type': 'string', 'required': True, 'description': 'Programming language'},
            {'name': 'package_file', 'type': 'long_text', 'required': True, 'description': 'Package file content'}
        ],
        'tags': ['dependencies', 'security'],
        'recommended_agent': reviewer_agent,
        'required_capabilities': ['CODE_REVIEW', 'SECURITY_AUDIT']
    },
    {
        'category': cats['code-review'],
        'name': 'Test Coverage Analysis',
        'slug': 'test-coverage',
        'description': 'Identify untested code paths',
        'template': 'Analyze test coverage:\n\nCode:\n```\n{{code}}\n```\n\nIdentify untested paths and suggest test cases.',
        'parameters': [
            {'name': 'code', 'type': 'long_text', 'required': True, 'description': 'Code to analyze'}
        ],
        'tags': ['testing', 'coverage'],
        'recommended_agent': qa_agent,
        'required_capabilities': []
    },
    {
        'category': cats['code-review'],
        'name': 'API Design Review',
        'slug': 'api-design-review',
        'description': 'Review API design for consistency',
        'template': 'Review API design:\n\n{{api_spec}}\n\nCheck REST principles, consistency, naming, versioning.',
        'parameters': [
            {'name': 'api_spec', 'type': 'long_text', 'required': True, 'description': 'API specification'}
        ],
        'tags': ['api', 'design-review'],
        'recommended_agent': reviewer_agent,
        'required_capabilities': ['CODE_REVIEW']
    },
    {
        'category': cats['code-review'],
        'name': 'Database Query Optimization',
        'slug': 'query-optimization',
        'description': 'Optimize database queries',
        'template': 'Optimize {{database_type}} query:\n\n```sql\n{{query}}\n```\n\nSuggest indexes, rewrites, and performance improvements.',
        'parameters': [
            {'name': 'database_type', 'type': 'string', 'required': True, 'description': 'Database type'},
            {'name': 'query', 'type': 'long_text', 'required': True, 'description': 'SQL query'}
        ],
        'tags': ['database', 'optimization'],
        'recommended_agent': reviewer_agent,
        'required_capabilities': ['CODE_REVIEW']
    },
    {
        'category': cats['code-review'],
        'name': 'Accessibility Audit',
        'slug': 'accessibility-audit',
        'description': 'Check WCAG accessibility compliance',
        'template': 'Audit accessibility:\n\n```\n{{code}}\n```\n\nCheck WCAG {{wcag_level}} compliance.',
        'parameters': [
            {'name': 'code', 'type': 'long_text', 'required': True, 'description': 'Code to audit'},
            {'name': 'wcag_level', 'type': 'string', 'required': False, 'default': 'AA', 'description': 'WCAG level (A, AA, AAA)'}
        ],
        'tags': ['accessibility', 'wcag'],
        'recommended_agent': reviewer_agent,
        'required_capabilities': []
    },
]

# Load commands
total = 0
for cmd_list in [req_commands, code_commands, review_commands]:
    for cmd in cmd_list:
        command, created = CommandTemplate.objects.update_or_create(
            slug=cmd['slug'],
            defaults=cmd
        )
        if created:
            total += 1
            print(f"[+] {command.name}")
        else:
            print(f"[*] {command.name}")

print(f"\n✅ Loaded {total} new commands")
print(f"Total commands in database: {CommandTemplate.objects.count()}")
