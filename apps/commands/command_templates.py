"""
Command templates library for HishamOS.
Contains command template generators for all command categories.
"""

def get_requirements_commands(category, ba_agent):
    """Get all Requirements Engineering command templates."""
    commands = [
        # 1. Generate User Stories (already exists)
        {
            'category': category,
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

**Format each story as:**
**Story [Number]**: [Title]
**As a** [user type]
**I want** [feature/capability]
**So that** [benefit/value]

**Acceptance Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Story Points**: [estimate]
**Dependencies**: [story numbers or 'None']

Generate 5-10 comprehensive user stories.''',
            'parameters': [
                {'name': 'project_context', 'type': 'text', 'required': True, 'description': 'Brief project description and goals', 'example': 'E-commerce platform for artisan coffee'},
                {'name': 'requirements', 'type': 'long_text', 'required': True, 'description': 'Raw requirements or feature list', 'example': 'Users browse products, add to cart, checkout'},
                {'name': 'additional_context', 'type': 'text', 'required': False, 'description': 'Additional context or constraints', 'default': ''}
            ],
            'tags': ['user-stories', 'requirements', 'agile'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS', 'USER_STORY_GENERATION']
        },
        {
            'category': category,
            'name': 'Create Requirements Specification Document',
            'slug': 'create-requirements-specification',
            'description': 'Generate comprehensive requirements specification document (SRS)',
            'template': '''Create requirements specification document.

**Project:** {{project_name}}
**Project Type:** {{project_type}}
**Stakeholders:**
{{stakeholders}}

**High-Level Requirements:**
{{high_level_requirements}}

{{#if constraints}}
**Constraints:**
{{constraints}}
{{/if}}

Create comprehensive SRS including:
1. Introduction and scope
2. Overall description (product perspective, functions, user characteristics)
3. System features (functional requirements)
4. External interface requirements
5. Non-functional requirements (performance, security, usability)
6. System models (use cases, data models)
7. Appendices (glossary, references)''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'project_type', 'type': 'text', 'required': True, 'description': 'Project type', 'example': 'Web Application'},
                {'name': 'stakeholders', 'type': 'text', 'required': True, 'description': 'Key stakeholders', 'example': 'Product Manager, Engineering Lead, End Users'},
                {'name': 'high_level_requirements', 'type': 'long_text', 'required': True, 'description': 'High-level requirements', 'example': 'User authentication, Product catalog, Shopping cart...'},
                {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Project constraints', 'default': ''}
            ],
            'tags': ['srs', 'requirements', 'specification'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Generate Acceptance Criteria',
            'slug': 'generate-acceptance-criteria',
            'description': 'Create detailed acceptance criteria for user stories or features',
            'template': '''Generate acceptance criteria.

**Feature/Story:** {{feature_name}}
**Description:**
{{feature_description}}

{{#if user_persona}}
**User Persona:** {{user_persona}}
{{/if}}

{{#if business_rules}}
**Business Rules:**
{{business_rules}}
{{/if}}

Create comprehensive acceptance criteria including:
1. Given-When-Then format scenarios
2. Edge cases and error scenarios
3. Validation rules
4. Success criteria
5. Definition of Done
6. Test scenarios''',
            'parameters': [
                {'name': 'feature_name', 'type': 'text', 'required': True, 'description': 'Feature or story name', 'example': 'User Login'},
                {'name': 'feature_description', 'type': 'long_text', 'required': True, 'description': 'Feature description', 'example': 'Users can login with email and password'},
                {'name': 'user_persona', 'type': 'text', 'required': False, 'description': 'User persona', 'default': ''},
                {'name': 'business_rules', 'type': 'text', 'required': False, 'description': 'Business rules', 'default': ''}
            ],
            'tags': ['acceptance-criteria', 'testing', 'requirements'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Create Functional Requirements Document',
            'slug': 'create-functional-requirements',
            'description': 'Generate detailed functional requirements document',
            'template': '''Create functional requirements document.

**Feature/Module:** {{feature_name}}
**Business Objective:** {{business_objective}}

**High-Level Requirements:**
{{high_level_requirements}}

{{#if user_roles}}
**User Roles:**
{{user_roles}}
{{/if}}

Create comprehensive functional requirements including:
1. Feature overview and purpose
2. User roles and permissions
3. Functional requirements (detailed)
4. User interface requirements
5. Data requirements
6. Business rules and validations
7. Workflow diagrams
8. Error handling
9. Integration requirements
10. Non-functional requirements''',
            'parameters': [
                {'name': 'feature_name', 'type': 'text', 'required': True, 'description': 'Feature name', 'example': 'User Authentication'},
                {'name': 'business_objective', 'type': 'text', 'required': True, 'description': 'Business objective', 'example': 'Secure user access'},
                {'name': 'high_level_requirements', 'type': 'long_text', 'required': True, 'description': 'High-level requirements', 'example': 'Users can login, reset password, enable 2FA...'},
                {'name': 'user_roles', 'type': 'text', 'required': False, 'description': 'User roles', 'default': ''}
            ],
            'tags': ['functional-requirements', 'frd', 'requirements'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Generate Non-Functional Requirements',
            'slug': 'generate-non-functional-requirements',
            'description': 'Create non-functional requirements specification',
            'template': '''Generate non-functional requirements.

**System/Application:** {{system_name}}
**System Type:** {{system_type}}

**Functional Requirements:**
{{functional_requirements}}

{{#if constraints}}
**Constraints:**
{{constraints}}
{{/if}}

Create comprehensive NFRs including:
1. Performance requirements (response time, throughput)
2. Scalability requirements
3. Security requirements
4. Availability and reliability
5. Usability requirements
6. Maintainability requirements
7. Portability requirements
8. Compliance requirements
9. Disaster recovery
10. Monitoring and logging''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'E-commerce Platform'},
                {'name': 'system_type', 'type': 'text', 'required': True, 'description': 'System type', 'example': 'Web Application'},
                {'name': 'functional_requirements', 'type': 'long_text', 'required': True, 'description': 'Functional requirements summary', 'example': 'User management, Product catalog, Checkout...'},
                {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Constraints', 'default': ''}
            ],
            'tags': ['nfr', 'non-functional', 'requirements'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Create Requirements Traceability Matrix',
            'slug': 'create-requirements-traceability',
            'description': 'Generate requirements traceability matrix',
            'template': '''Create requirements traceability matrix.

**Project:** {{project_name}}
**Requirements:**
{{requirements}}

**Design Components:**
{{design_components}}

**Test Cases:**
{{test_cases}}

Create comprehensive traceability matrix including:
1. Requirements ID and description
2. Source (stakeholder, document)
3. Design components mapping
4. Test case mapping
5. Status (implemented, tested, verified)
6. Coverage analysis
7. Gaps identification
8. Change impact analysis''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'requirements', 'type': 'long_text', 'required': True, 'description': 'Requirements list', 'example': 'REQ-001: User login, REQ-002: Product search...'},
                {'name': 'design_components', 'type': 'text', 'required': False, 'description': 'Design components', 'default': ''},
                {'name': 'test_cases', 'type': 'text', 'required': False, 'description': 'Test cases', 'default': ''}
            ],
            'tags': ['traceability', 'requirements', 'matrix'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Generate Requirements Review Checklist',
            'slug': 'generate-requirements-review-checklist',
            'description': 'Create checklist for requirements review',
            'template': '''Generate requirements review checklist.

**Document Type:** {{document_type}}
**Review Scope:** {{review_scope}}

{{#if specific_concerns}}
**Specific Concerns:**
{{specific_concerns}}
{{/if}}

Create comprehensive review checklist including:
1. Completeness (all requirements captured)
2. Clarity and understandability
3. Consistency (no contradictions)
4. Verifiability (testable requirements)
5. Traceability (linked to business objectives)
6. Feasibility (technically achievable)
7. Prioritization (must-have, should-have, nice-to-have)
8. Dependencies identification
9. Risk assessment
10. Approval criteria''',
            'parameters': [
                {'name': 'document_type', 'type': 'text', 'required': True, 'description': 'Document type', 'example': 'SRS, BRD, User Stories'},
                {'name': 'review_scope', 'type': 'text', 'required': True, 'description': 'Review scope', 'example': 'All requirements, Specific module...'},
                {'name': 'specific_concerns', 'type': 'text', 'required': False, 'description': 'Specific concerns', 'default': ''}
            ],
            'tags': ['review', 'checklist', 'requirements'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Create Stakeholder Requirements Workshop Plan',
            'slug': 'create-requirements-workshop-plan',
            'description': 'Plan requirements elicitation workshop',
            'template': '''Create requirements workshop plan.

**Workshop Objective:** {{workshop_objective}}
**Stakeholders:**
{{stakeholders}}

**Duration:** {{duration}}

{{#if topics}}
**Topics to Cover:**
{{topics}}
{{/if}}

Create comprehensive workshop plan including:
1. Workshop objectives and agenda
2. Stakeholder roles and responsibilities
3. Pre-workshop preparation
4. Workshop activities and exercises
5. Facilitation techniques
6. Documentation approach
7. Follow-up actions
8. Success criteria
9. Risk mitigation
10. Materials and tools needed''',
            'parameters': [
                {'name': 'workshop_objective', 'type': 'text', 'required': True, 'description': 'Workshop objective', 'example': 'Elicit requirements for new feature'},
                {'name': 'stakeholders', 'type': 'long_text', 'required': True, 'description': 'Stakeholders', 'example': 'Product Manager, Engineering Lead, End Users...'},
                {'name': 'duration', 'type': 'text', 'required': True, 'description': 'Workshop duration', 'example': '4 hours, Full day'},
                {'name': 'topics', 'type': 'text', 'required': False, 'description': 'Topics to cover', 'default': ''}
            ],
            'tags': ['workshop', 'elicitation', 'requirements'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        # ... (keeping existing commands, adding new ones from commands_data)
    ]
    
    # Add commands from commands_data
    from apps.commands.commands_data import REQUIREMENTS_COMMANDS_DATA
    for cmd_data in REQUIREMENTS_COMMANDS_DATA:
        params = []
        for p in cmd_data['params']:
            param = {
                'name': p[0],
                'type': p[1],
                'required': p[2],
                'description': f'{p[0].replace("_", " ").title()}',
                'example': ''
            }
            if len(p) > 3 and isinstance(p[3], list):
                param['allowed_values'] = p[3]
            params.append(param)
        
        template = f'''Generate {cmd_data['name'].lower()}.

**Input:**
{chr(10).join(f"{{{{{{p[0]}}}}}}" for p in cmd_data['params'] if p[2])}

Create comprehensive output following best practices.'''
        
        commands.append({
            'category': category,
            'name': cmd_data['name'],
            'slug': cmd_data['slug'],
            'description': cmd_data['desc'],
            'template': template,
            'parameters': params,
            'tags': cmd_data['tags'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        })
    
    return commands


def get_code_generation_commands(category, coding_agent):
    """Get all Code Generation command templates."""
    from apps.commands.commands_data import CODE_GEN_COMMANDS_DATA
    
    commands = []
    for cmd_data in CODE_GEN_COMMANDS_DATA:
        params = []
        for p in cmd_data['params']:
            param = {
                'name': p[0],
                'type': p[1],
                'required': p[2],
                'description': f'{p[0].replace("_", " ").title()}',
                'example': ''
            }
            if len(p) > 3 and isinstance(p[3], list):
                param['allowed_values'] = p[3]
            params.append(param)
        
        template = f'''Generate {cmd_data['name'].lower()}.

**Input:**
{chr(10).join(f"{{{{{{p[0]}}}}}}" for p in cmd_data['params'] if p[2])}

Generate production-ready, well-documented code following best practices and design patterns.'''
        
        commands.append({
            'category': category,
            'name': cmd_data['name'],
            'slug': cmd_data['slug'],
            'description': cmd_data['desc'],
            'template': template,
            'parameters': params,
            'tags': cmd_data['tags'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        })
    
    # Add additional code generation commands
    commands.extend([
        {
            'category': category,
            'name': 'Generate GraphQL Resolvers',
            'slug': 'generate-graphql-resolvers',
            'description': 'Create GraphQL resolvers for schema',
            'template': '''Generate GraphQL resolvers.

**Schema:** {{schema}}
**Resolvers Needed:**
{{resolvers_needed}}

{{#if data_source}}
**Data Source:** {{data_source}}
{{/if}}

Create comprehensive resolvers including:
1. Query resolvers
2. Mutation resolvers
3. Field resolvers
4. Error handling
5. Data validation
6. Authentication checks
7. Performance optimization
8. Testing examples''',
            'parameters': [
                {'name': 'schema', 'type': 'long_text', 'required': True, 'description': 'GraphQL schema', 'example': 'type User { id: ID!, name: String! }'},
                {'name': 'resolvers_needed', 'type': 'long_text', 'required': True, 'description': 'Resolvers needed', 'example': 'getUser, createUser, updateUser...'},
                {'name': 'data_source', 'type': 'text', 'required': False, 'description': 'Data source', 'default': 'Database'}
            ],
            'tags': ['graphql', 'resolvers', 'api'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Create WebSocket Handler',
            'slug': 'create-websocket-handler',
            'description': 'Generate WebSocket connection and message handler',
            'template': '''Create WebSocket handler.

**Application Type:** {{application_type}}
**Use Case:** {{use_case}}

**Message Types:**
{{message_types}}

{{#if authentication}}
**Authentication:** {{authentication}}
{{/if}}

Create comprehensive WebSocket handler including:
1. Connection management
2. Message routing
3. Error handling
4. Heartbeat/ping-pong
5. Reconnection logic
6. Message validation
7. Broadcasting
8. Room/channel management
9. Security considerations
10. Testing examples''',
            'parameters': [
                {'name': 'application_type', 'type': 'text', 'required': True, 'description': 'Application type', 'example': 'Real-time chat, Live updates'},
                {'name': 'use_case', 'type': 'text', 'required': True, 'description': 'Use case', 'example': 'Chat messages, Notifications, Live data'},
                {'name': 'message_types', 'type': 'long_text', 'required': True, 'description': 'Message types', 'example': 'chat_message, user_joined, notification...'},
                {'name': 'authentication', 'type': 'text', 'required': False, 'description': 'Authentication method', 'default': 'JWT'}
            ],
            'tags': ['websocket', 'realtime', 'networking'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Generate Event Sourcing Implementation',
            'slug': 'generate-event-sourcing',
            'description': 'Create event sourcing implementation',
            'template': '''Generate event sourcing implementation.

**Domain:** {{domain}}
**Aggregates:**
{{aggregates}}

**Events:**
{{events}}

{{#if storage}}
**Storage:** {{storage}}
{{/if}}

Create comprehensive event sourcing including:
1. Event definitions
2. Aggregate root implementation
3. Event store interface
4. Event handlers
5. Snapshot strategy
6. Event replay logic
7. Projection builders
8. CQRS integration
9. Testing approach
10. Migration strategy''',
            'parameters': [
                {'name': 'domain', 'type': 'text', 'required': True, 'description': 'Domain', 'example': 'E-commerce, Banking'},
                {'name': 'aggregates', 'type': 'long_text', 'required': True, 'description': 'Aggregates', 'example': 'Order, User, Product...'},
                {'name': 'events', 'type': 'long_text', 'required': True, 'description': 'Events', 'example': 'OrderCreated, OrderPaid, OrderShipped...'},
                {'name': 'storage', 'type': 'text', 'required': False, 'description': 'Storage backend', 'default': 'Database'}
            ],
            'tags': ['event-sourcing', 'cqrs', 'architecture'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        }
    ])
    
    return commands


def get_code_review_commands(category, reviewer_agent):
    """Get all Code Review command templates."""
    from apps.commands.commands_data import CODE_REVIEW_COMMANDS_DATA
    
    commands = []
    for cmd_data in CODE_REVIEW_COMMANDS_DATA:
        params = []
        for p in cmd_data['params']:
            param = {
                'name': p[0],
                'type': p[1],
                'required': p[2],
                'description': f'{p[0].replace("_", " ").title()}',
                'example': ''
            }
            if len(p) > 3 and isinstance(p[3], list):
                param['allowed_values'] = p[3]
            params.append(param)
        
        template = f'''Review {cmd_data['name'].lower()}.

**Input:**
{chr(10).join(f"{{{{{{p[0]}}}}}}" for p in cmd_data['params'] if p[2])}

Perform comprehensive code review focusing on quality, security, performance, and best practices.'''
        
        commands.append({
            'category': category,
            'name': cmd_data['name'],
            'slug': cmd_data['slug'],
            'description': cmd_data['desc'],
            'template': template,
            'parameters': params,
            'tags': cmd_data['tags'],
            'recommended_agent': reviewer_agent,
            'required_capabilities': ['CODE_REVIEW']
        })
    
    # Add additional code review commands
    commands.extend([
        {
            'category': category,
            'name': 'Review Security Vulnerabilities',
            'slug': 'review-security-vulnerabilities',
            'description': 'Identify and analyze security vulnerabilities in code',
            'template': '''Review security vulnerabilities.

**Code/System:** {{code_system}}
**Technology Stack:** {{tech_stack}}

{{#if known_concerns}}
**Known Security Concerns:**
{{known_concerns}}
{{/if}}

Create comprehensive security review including:
1. OWASP Top 10 analysis
2. Authentication and authorization issues
3. Input validation vulnerabilities
4. SQL injection risks
5. XSS vulnerabilities
6. CSRF protection
7. Sensitive data exposure
8. Dependency vulnerabilities
9. Security best practices violations
10. Remediation recommendations''',
            'parameters': [
                {'name': 'code_system', 'type': 'text', 'required': True, 'description': 'Code or system', 'example': 'API endpoints, Authentication module'},
                {'name': 'tech_stack', 'type': 'text', 'required': True, 'description': 'Technology stack', 'example': 'Python/Django, Node.js/Express'},
                {'name': 'known_concerns', 'type': 'text', 'required': False, 'description': 'Known security concerns', 'default': ''}
            ],
            'tags': ['security', 'vulnerabilities', 'review'],
            'recommended_agent': reviewer_agent,
            'required_capabilities': ['CODE_REVIEW']
        },
        {
            'category': category,
            'name': 'Analyze Code Complexity',
            'slug': 'analyze-code-complexity',
            'description': 'Analyze code complexity and maintainability',
            'template': '''Analyze code complexity.

**Code/Module:** {{code_module}}
**Language:** {{language}}

{{#if metrics}}
**Current Metrics:**
{{metrics}}
{{/if}}

Create comprehensive complexity analysis including:
1. Cyclomatic complexity
2. Cognitive complexity
3. Code duplication analysis
4. Maintainability index
5. Technical debt assessment
6. Refactoring opportunities
7. Code smell identification
8. Complexity hotspots
9. Recommendations
10. Refactoring priority''',
            'parameters': [
                {'name': 'code_module', 'type': 'text', 'required': True, 'description': 'Code module', 'example': 'UserService, PaymentProcessor'},
                {'name': 'language', 'type': 'text', 'required': True, 'description': 'Programming language', 'example': 'Python, JavaScript, Java'},
                {'name': 'metrics', 'type': 'text', 'required': False, 'description': 'Current metrics', 'default': ''}
            ],
            'tags': ['complexity', 'maintainability', 'analysis'],
            'recommended_agent': reviewer_agent,
            'required_capabilities': ['CODE_REVIEW']
        },
        {
            'category': category,
            'name': 'Review API Design',
            'slug': 'review-api-design',
            'description': 'Review RESTful API design and best practices',
            'template': '''Review API design.

**API:** {{api_name}}
**Endpoints:**
{{endpoints}}

{{#if api_version}}
**API Version:** {{api_version}}
{{/if}}

Create comprehensive API review including:
1. RESTful principles compliance
2. Resource naming conventions
3. HTTP method usage
4. Status code usage
5. Request/response structure
6. Error handling
7. Versioning strategy
8. Documentation quality
9. Security considerations
10. Performance implications
11. Best practices violations
12. Improvement recommendations''',
            'parameters': [
                {'name': 'api_name', 'type': 'text', 'required': True, 'description': 'API name', 'example': 'User Management API'},
                {'name': 'endpoints', 'type': 'long_text', 'required': True, 'description': 'API endpoints', 'example': 'GET /users, POST /users, PUT /users/{id}...'},
                {'name': 'api_version', 'type': 'text', 'required': False, 'description': 'API version', 'default': 'v1'}
            ],
            'tags': ['api', 'rest', 'design-review'],
            'recommended_agent': reviewer_agent,
            'required_capabilities': ['CODE_REVIEW']
        },
        {
            'category': category,
            'name': 'Review Database Schema Design',
            'slug': 'review-database-schema',
            'description': 'Review database schema design and optimization',
            'template': '''Review database schema design.

**Database:** {{database_name}}
**Schema:**
{{schema}}

{{#if current_issues}}
**Current Issues:**
{{current_issues}}
{{/if}}

Create comprehensive schema review including:
1. Normalization (1NF, 2NF, 3NF)
2. Index strategy
3. Foreign key relationships
4. Data types and constraints
5. Query performance implications
6. Scalability considerations
7. Data integrity
8. Migration complexity
9. Best practices compliance
10. Optimization recommendations''',
            'parameters': [
                {'name': 'database_name', 'type': 'text', 'required': True, 'description': 'Database name', 'example': 'E-commerce DB'},
                {'name': 'schema', 'type': 'long_text', 'required': True, 'description': 'Schema description', 'example': 'Users table, Orders table, Products table...'},
                {'name': 'current_issues', 'type': 'text', 'required': False, 'description': 'Current issues', 'default': ''}
            ],
            'tags': ['database', 'schema', 'review'],
            'recommended_agent': reviewer_agent,
            'required_capabilities': ['CODE_REVIEW']
        },
        {
            'category': category,
            'name': 'Review Test Coverage',
            'slug': 'review-test-coverage',
            'description': 'Analyze test coverage and quality',
            'template': '''Review test coverage.

**Codebase/Module:** {{codebase}}
**Test Framework:** {{test_framework}}

{{#if coverage_data}}
**Current Coverage:**
{{coverage_data}}
{{/if}}

Create comprehensive test coverage review including:
1. Coverage metrics (line, branch, function)
2. Coverage gaps identification
3. Critical path coverage
4. Test quality assessment
5. Test maintainability
6. Missing test scenarios
7. Test organization
8. Test performance
9. Recommendations
10. Coverage goals''',
            'parameters': [
                {'name': 'codebase', 'type': 'text', 'required': True, 'description': 'Codebase or module', 'example': 'UserService, PaymentModule'},
                {'name': 'test_framework', 'type': 'text', 'required': True, 'description': 'Test framework', 'example': 'Jest, pytest, JUnit'},
                {'name': 'coverage_data', 'type': 'text', 'required': False, 'description': 'Current coverage data', 'default': ''}
            ],
            'tags': ['test-coverage', 'testing', 'review'],
            'recommended_agent': reviewer_agent,
            'required_capabilities': ['CODE_REVIEW']
        },
        {
            'category': category,
            'name': 'Review Code Architecture',
            'slug': 'review-code-architecture',
            'description': 'Review overall code architecture and design patterns',
            'template': '''Review code architecture.

**System/Application:** {{system_name}}
**Architecture Pattern:** {{architecture_pattern}}

**Components:**
{{components}}

{{#if concerns}}
**Architectural Concerns:**
{{concerns}}
{{/if}}

Create comprehensive architecture review including:
1. Architecture pattern compliance
2. Separation of concerns
3. Dependency management
4. Design patterns usage
5. Component coupling
6. Scalability assessment
7. Maintainability
8. Technical debt
9. Best practices
10. Refactoring recommendations''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'E-commerce Platform'},
                {'name': 'architecture_pattern', 'type': 'text', 'required': True, 'description': 'Architecture pattern', 'example': 'MVC, Microservices, Layered'},
                {'name': 'components', 'type': 'long_text', 'required': True, 'description': 'System components', 'example': 'API, Services, Database, Frontend...'},
                {'name': 'concerns', 'type': 'text', 'required': False, 'description': 'Architectural concerns', 'default': ''}
            ],
            'tags': ['architecture', 'design-patterns', 'review'],
            'recommended_agent': reviewer_agent,
            'required_capabilities': ['CODE_REVIEW']
        }
    ])
    
    return commands


def get_testing_commands(category, qa_agent):
    """Get all Testing & QA command templates."""
    from apps.commands.commands_data import TESTING_COMMANDS_DATA
    
    commands = []
    for cmd_data in TESTING_COMMANDS_DATA:
        params = []
        for p in cmd_data['params']:
            param = {
                'name': p[0],
                'type': p[1],
                'required': p[2],
                'description': f'{p[0].replace("_", " ").title()}',
                'example': ''
            }
            if len(p) > 3 and isinstance(p[3], list):
                param['allowed_values'] = p[3]
            params.append(param)
        
        template = f'''Generate {cmd_data['name'].lower()}.

**Input:**
{chr(10).join(f"{{{{{{p[0]}}}}}}" for p in cmd_data['params'] if p[2])}

Create comprehensive test cases following testing best practices.'''
        
        commands.append({
            'category': category,
            'name': cmd_data['name'],
            'slug': cmd_data['slug'],
            'description': cmd_data['desc'],
            'template': template,
            'parameters': params,
            'tags': cmd_data['tags'],
            'recommended_agent': qa_agent,
            'required_capabilities': ['TESTING']
        })
    
    # Add additional testing commands
    commands.extend([
        {
            'category': category,
            'name': 'Create Test Strategy Document',
            'slug': 'create-test-strategy',
            'description': 'Develop comprehensive test strategy for project',
            'template': '''Create test strategy document.

**Project:** {{project_name}}
**Project Type:** {{project_type}}

**Key Features:**
{{key_features}}

{{#if quality_requirements}}
**Quality Requirements:**
{{quality_requirements}}
{{/if}}

Create comprehensive test strategy including:
1. Testing objectives and scope
2. Test levels (unit, integration, system, acceptance)
3. Test types (functional, performance, security, usability)
4. Test environment requirements
5. Test data management
6. Defect management process
7. Test metrics and reporting
8. Risk-based testing approach
9. Resource requirements
10. Timeline and milestones''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'project_type', 'type': 'text', 'required': True, 'description': 'Project type', 'example': 'Web Application'},
                {'name': 'key_features', 'type': 'long_text', 'required': True, 'description': 'Key features', 'example': 'User authentication, Product catalog, Checkout...'},
                {'name': 'quality_requirements', 'type': 'text', 'required': False, 'description': 'Quality requirements', 'default': ''}
            ],
            'tags': ['test-strategy', 'planning', 'qa'],
            'recommended_agent': qa_agent,
            'required_capabilities': ['TESTING']
        },
        {
            'category': category,
            'name': 'Generate Test Cases from Requirements',
            'slug': 'generate-test-cases-from-requirements',
            'description': 'Create test cases from requirements or user stories',
            'template': '''Generate test cases from requirements.

**Requirement/User Story:**
{{requirement}}

**Acceptance Criteria:**
{{acceptance_criteria}}

{{#if test_scenarios}}
**Test Scenarios:**
{{test_scenarios}}
{{/if}}

Create comprehensive test cases including:
1. Test case ID and title
2. Preconditions
3. Test steps (detailed)
4. Expected results
5. Test data requirements
6. Priority (High, Medium, Low)
7. Test type (positive, negative, boundary)
8. Traceability to requirement''',
            'parameters': [
                {'name': 'requirement', 'type': 'long_text', 'required': True, 'description': 'Requirement or user story', 'example': 'As a user, I want to login...'},
                {'name': 'acceptance_criteria', 'type': 'long_text', 'required': True, 'description': 'Acceptance criteria', 'example': 'User can login with valid credentials...'},
                {'name': 'test_scenarios', 'type': 'text', 'required': False, 'description': 'Test scenarios', 'default': ''}
            ],
            'tags': ['test-cases', 'requirements', 'testing'],
            'recommended_agent': qa_agent,
            'required_capabilities': ['TESTING']
        },
        {
            'category': category,
            'name': 'Create Regression Test Suite',
            'slug': 'create-regression-test-suite',
            'description': 'Design regression test suite for application',
            'template': '''Create regression test suite.

**Application:** {{application_name}}
**Critical Features:**
{{critical_features}}

**Recent Changes:**
{{recent_changes}}

{{#if test_coverage_goal}}
**Test Coverage Goal:** {{test_coverage_goal}}
{{/if}}

Create comprehensive regression suite including:
1. Test suite structure
2. Critical path tests
3. Smoke tests
4. Sanity tests
5. Feature-specific tests
6. Integration tests
7. Test prioritization
8. Automation recommendations
9. Maintenance strategy
10. Execution schedule''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'E-commerce Platform'},
                {'name': 'critical_features', 'type': 'long_text', 'required': True, 'description': 'Critical features', 'example': 'Login, Checkout, Payment processing...'},
                {'name': 'recent_changes', 'type': 'text', 'required': True, 'description': 'Recent changes', 'example': 'Updated payment gateway, New user registration flow...'},
                {'name': 'test_coverage_goal', 'type': 'text', 'required': False, 'description': 'Test coverage goal', 'default': '80%'}
            ],
            'tags': ['regression', 'test-suite', 'automation'],
            'recommended_agent': qa_agent,
            'required_capabilities': ['TESTING']
        },
        {
            'category': category,
            'name': 'Design Load Testing Plan',
            'slug': 'design-load-testing-plan',
            'description': 'Create load testing plan for performance validation',
            'template': '''Design load testing plan.

**System/Application:** {{system_name}}
**Performance Requirements:**
{{performance_requirements}}

**Expected Load:**
{{expected_load}}

{{#if test_scenarios}}
**Test Scenarios:**
{{test_scenarios}}
{{/if}}

Create comprehensive load testing plan including:
1. Performance objectives
2. Load scenarios (normal, peak, stress)
3. Test data requirements
4. Test environment setup
5. Metrics to measure (response time, throughput, error rate)
6. Load ramp-up strategy
7. Success criteria
8. Monitoring and logging
9. Risk mitigation
10. Reporting structure''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'API Gateway'},
                {'name': 'performance_requirements', 'type': 'long_text', 'required': True, 'description': 'Performance requirements', 'example': 'Response time < 500ms, Handle 10K concurrent users...'},
                {'name': 'expected_load', 'type': 'text', 'required': True, 'description': 'Expected load', 'example': '10K requests/min, Peak at 50K'},
                {'name': 'test_scenarios', 'type': 'text', 'required': False, 'description': 'Test scenarios', 'default': ''}
            ],
            'tags': ['load-testing', 'performance', 'stress-testing'],
            'recommended_agent': qa_agent,
            'required_capabilities': ['TESTING']
        },
        {
            'category': category,
            'name': 'Generate Test Execution Report',
            'slug': 'generate-test-execution-report',
            'description': 'Create test execution report with results and metrics',
            'template': '''Generate test execution report.

**Test Run:** {{test_run_name}}
**Test Period:** {{test_period}}
**Test Suite:** {{test_suite}}

**Test Results:**
{{test_results}}

{{#if defects}}
**Defects Found:**
{{defects}}
{{/if}}

Create comprehensive test report including:
1. Executive summary
2. Test execution summary (total, passed, failed, blocked)
3. Test coverage metrics
4. Defect summary and trends
5. Risk assessment
6. Test environment status
7. Blockers and issues
8. Recommendations
9. Next steps''',
            'parameters': [
                {'name': 'test_run_name', 'type': 'text', 'required': True, 'description': 'Test run name', 'example': 'Sprint 3 Regression'},
                {'name': 'test_period', 'type': 'text', 'required': True, 'description': 'Test period', 'example': '2024-01-15 to 2024-01-22'},
                {'name': 'test_suite', 'type': 'text', 'required': True, 'description': 'Test suite', 'example': 'Regression Suite v2.1'},
                {'name': 'test_results', 'type': 'long_text', 'required': True, 'description': 'Test results', 'example': 'Total: 150, Passed: 140, Failed: 8, Blocked: 2'},
                {'name': 'defects', 'type': 'text', 'required': False, 'description': 'Defects found', 'default': ''}
            ],
            'tags': ['test-report', 'execution', 'metrics'],
            'recommended_agent': qa_agent,
            'required_capabilities': ['TESTING']
        },
        {
            'category': category,
            'name': 'Create Test Data Management Strategy',
            'slug': 'create-test-data-strategy',
            'description': 'Design test data management strategy',
            'template': '''Create test data management strategy.

**Application:** {{application_name}}
**Data Requirements:**
{{data_requirements}}

**Test Scenarios:**
{{test_scenarios}}

{{#if constraints}}
**Constraints:**
{{constraints}}
{{/if}}

Create comprehensive test data strategy including:
1. Test data types and sources
2. Data generation approach (synthetic, production copy, masked)
3. Data provisioning process
4. Test data refresh strategy
5. Data privacy and security
6. Test data catalog
7. Data maintenance procedures
8. Tools and automation
9. Best practices
10. Compliance considerations''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'E-commerce Platform'},
                {'name': 'data_requirements', 'type': 'long_text', 'required': True, 'description': 'Data requirements', 'example': 'User accounts, Product catalog, Order history...'},
                {'name': 'test_scenarios', 'type': 'long_text', 'required': True, 'description': 'Test scenarios', 'example': 'Login tests, Checkout tests, Payment tests...'},
                {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Constraints', 'default': ''}
            ],
            'tags': ['test-data', 'data-management', 'strategy'],
            'recommended_agent': qa_agent,
            'required_capabilities': ['TESTING']
        },
        {
            'category': category,
            'name': 'Design API Testing Strategy',
            'slug': 'design-api-testing-strategy',
            'description': 'Create comprehensive API testing strategy',
            'template': '''Design API testing strategy.

**API/Service:** {{api_name}}
**API Type:** {{api_type}}

**Endpoints:**
{{endpoints}}

{{#if authentication}}
**Authentication:** {{authentication}}
{{/if}}

Create comprehensive API testing strategy including:
1. API testing objectives
2. Test types (functional, performance, security, contract)
3. Test cases for each endpoint
4. Request/response validation
5. Error handling tests
6. Authentication and authorization tests
7. Rate limiting tests
8. Data validation tests
9. Integration test scenarios
10. Automation approach
11. Tools and frameworks
12. Test data management''',
            'parameters': [
                {'name': 'api_name', 'type': 'text', 'required': True, 'description': 'API name', 'example': 'User Management API'},
                {'name': 'api_type', 'type': 'text', 'required': True, 'description': 'API type', 'example': 'REST, GraphQL, gRPC'},
                {'name': 'endpoints', 'type': 'long_text', 'required': True, 'description': 'API endpoints', 'example': 'GET /users, POST /users, PUT /users/{id}...'},
                {'name': 'authentication', 'type': 'text', 'required': False, 'description': 'Authentication method', 'default': 'JWT'}
            ],
            'tags': ['api-testing', 'rest', 'integration'],
            'recommended_agent': qa_agent,
            'required_capabilities': ['TESTING']
        }
    ])
    
    return commands


def get_devops_commands(category, devops_agent):
    """Get all DevOps & Deployment command templates."""
    from apps.commands.commands_data import DEVOPS_COMMANDS_DATA
    
    commands = []
    for cmd_data in DEVOPS_COMMANDS_DATA:
        params = []
        for p in cmd_data['params']:
            param = {
                'name': p[0],
                'type': p[1],
                'required': p[2],
                'description': f'{p[0].replace("_", " ").title()}',
                'example': ''
            }
            if len(p) > 3 and isinstance(p[3], list):
                param['allowed_values'] = p[3]
            params.append(param)
        
        template = f'''Generate {cmd_data['name'].lower()}.

**Input:**
{chr(10).join(f"{{{{{{p[0]}}}}}}" for p in cmd_data['params'] if p[2])}

Create production-ready DevOps configuration following industry best practices.'''
        
        commands.append({
            'category': category,
            'name': cmd_data['name'],
            'slug': cmd_data['slug'],
            'description': cmd_data['desc'],
            'template': template,
            'parameters': params,
            'tags': cmd_data['tags'],
            'recommended_agent': devops_agent,
            'required_capabilities': ['DEVOPS', 'DEPLOYMENT']
        })
    
    # Add additional DevOps commands
    commands.extend([
        {
            'category': category,
            'name': 'Design Disaster Recovery Plan',
            'slug': 'design-disaster-recovery-plan',
            'description': 'Create comprehensive disaster recovery plan',
            'template': '''Design disaster recovery plan.

**System/Application:** {{system_name}}
**RTO (Recovery Time Objective):** {{rto}}
**RPO (Recovery Point Objective):** {{rpo}}

**Critical Systems:**
{{critical_systems}}

{{#if current_backup_strategy}}
**Current Backup Strategy:**
{{current_backup_strategy}}
{{/if}}

Create comprehensive DR plan including:
1. Risk assessment and scenarios
2. Recovery objectives (RTO, RPO)
3. Backup strategy and procedures
4. Data replication approach
5. Failover procedures
6. Recovery procedures
7. Communication plan
8. Testing schedule
9. Documentation and runbooks
10. Maintenance and updates''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'E-commerce Platform'},
                {'name': 'rto', 'type': 'text', 'required': True, 'description': 'Recovery Time Objective', 'example': '4 hours'},
                {'name': 'rpo', 'type': 'text', 'required': True, 'description': 'Recovery Point Objective', 'example': '1 hour'},
                {'name': 'critical_systems', 'type': 'long_text', 'required': True, 'description': 'Critical systems', 'example': 'Database, API, Payment gateway...'},
                {'name': 'current_backup_strategy', 'type': 'text', 'required': False, 'description': 'Current backup strategy', 'default': ''}
            ],
            'tags': ['disaster-recovery', 'backup', 'planning'],
            'recommended_agent': devops_agent,
            'required_capabilities': ['DEVOPS']
        },
        {
            'category': category,
            'name': 'Create Infrastructure Monitoring Setup',
            'slug': 'create-infrastructure-monitoring',
            'description': 'Design comprehensive infrastructure monitoring',
            'template': '''Create infrastructure monitoring setup.

**Infrastructure:** {{infrastructure}}
**Monitoring Scope:**
{{monitoring_scope}}

**Key Metrics:**
{{key_metrics}}

{{#if alerting_requirements}}
**Alerting Requirements:**
{{alerting_requirements}}
{{/if}}

Create comprehensive monitoring setup including:
1. Monitoring objectives
2. Metrics to monitor (CPU, memory, disk, network)
3. Application metrics
4. Log aggregation strategy
5. Alerting rules and thresholds
6. Dashboard design
7. Tools and platforms
8. Integration points
9. Maintenance procedures
10. Cost optimization''',
            'parameters': [
                {'name': 'infrastructure', 'type': 'text', 'required': True, 'description': 'Infrastructure', 'example': 'Kubernetes, AWS, Docker'},
                {'name': 'monitoring_scope', 'type': 'long_text', 'required': True, 'description': 'Monitoring scope', 'example': 'Servers, Databases, Applications, Networks...'},
                {'name': 'key_metrics', 'type': 'long_text', 'required': True, 'description': 'Key metrics', 'example': 'Response time, Error rate, Throughput, Availability...'},
                {'name': 'alerting_requirements', 'type': 'text', 'required': False, 'description': 'Alerting requirements', 'default': ''}
            ],
            'tags': ['monitoring', 'observability', 'infrastructure'],
            'recommended_agent': devops_agent,
            'required_capabilities': ['DEVOPS']
        },
        {
            'category': category,
            'name': 'Generate Container Orchestration Config',
            'slug': 'generate-container-orchestration',
            'description': 'Create container orchestration configuration',
            'template': '''Generate container orchestration configuration.

**Orchestration Platform:** {{platform}}
**Application:** {{application_name}}

**Services:**
{{services}}

{{#if requirements}}
**Requirements:**
{{requirements}}
{{/if}}

Create comprehensive orchestration config including:
1. Service definitions
2. Resource limits and requests
3. Scaling configuration
4. Health checks
5. Service discovery
6. Networking configuration
7. Storage volumes
8. Secrets management
9. Deployment strategy
10. Rollback procedures''',
            'parameters': [
                {'name': 'platform', 'type': 'string', 'required': True, 'description': 'Orchestration platform', 'allowed_values': ['Kubernetes', 'Docker Swarm', 'Nomad'], 'example': 'Kubernetes'},
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'E-commerce Platform'},
                {'name': 'services', 'type': 'long_text', 'required': True, 'description': 'Services', 'example': 'API, Frontend, Database, Cache...'},
                {'name': 'requirements', 'type': 'text', 'required': False, 'description': 'Requirements', 'default': ''}
            ],
            'tags': ['kubernetes', 'orchestration', 'containers'],
            'recommended_agent': devops_agent,
            'required_capabilities': ['DEVOPS']
        },
        {
            'category': category,
            'name': 'Create Blue-Green Deployment Strategy',
            'slug': 'create-blue-green-deployment',
            'description': 'Design blue-green deployment strategy',
            'template': '''Create blue-green deployment strategy.

**Application:** {{application_name}}
**Infrastructure:** {{infrastructure}}

**Deployment Requirements:**
{{deployment_requirements}}

{{#if current_setup}}
**Current Setup:**
{{current_setup}}
{{/if}}

Create comprehensive blue-green strategy including:
1. Architecture overview
2. Environment setup (blue and green)
3. Deployment process
4. Traffic switching mechanism
5. Health check configuration
6. Rollback procedure
7. Database migration strategy
8. Monitoring and validation
9. Cost considerations
10. Best practices''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'E-commerce Platform'},
                {'name': 'infrastructure', 'type': 'text', 'required': True, 'description': 'Infrastructure', 'example': 'AWS, Kubernetes, Docker'},
                {'name': 'deployment_requirements', 'type': 'long_text', 'required': True, 'description': 'Deployment requirements', 'example': 'Zero downtime, Fast rollback, A/B testing...'},
                {'name': 'current_setup', 'type': 'text', 'required': False, 'description': 'Current setup', 'default': ''}
            ],
            'tags': ['blue-green', 'deployment', 'strategy'],
            'recommended_agent': devops_agent,
            'required_capabilities': ['DEVOPS']
        },
        {
            'category': category,
            'name': 'Design CI/CD Pipeline',
            'slug': 'design-cicd-pipeline',
            'description': 'Create comprehensive CI/CD pipeline design',
            'template': '''Design CI/CD pipeline.

**Project:** {{project_name}}
**Repository:** {{repository}}
**Build Tool:** {{build_tool}}

**Pipeline Stages:**
{{pipeline_stages}}

{{#if deployment_targets}}
**Deployment Targets:**
{{deployment_targets}}
{{/if}}

Create comprehensive CI/CD pipeline including:
1. Pipeline architecture
2. Source control integration
3. Build stage configuration
4. Test stages (unit, integration, e2e)
5. Code quality checks
6. Security scanning
7. Deployment stages
8. Approval gates
9. Notification setup
10. Rollback procedures
11. Pipeline optimization
12. Best practices''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'repository', 'type': 'text', 'required': True, 'description': 'Repository', 'example': 'GitHub, GitLab, Bitbucket'},
                {'name': 'build_tool', 'type': 'text', 'required': True, 'description': 'Build tool', 'example': 'Jenkins, GitHub Actions, GitLab CI'},
                {'name': 'pipeline_stages', 'type': 'long_text', 'required': True, 'description': 'Pipeline stages', 'example': 'Build, Test, Deploy to staging, Deploy to production...'},
                {'name': 'deployment_targets', 'type': 'text', 'required': False, 'description': 'Deployment targets', 'default': ''}
            ],
            'tags': ['cicd', 'pipeline', 'automation'],
            'recommended_agent': devops_agent,
            'required_capabilities': ['DEVOPS']
        },
        {
            'category': category,
            'name': 'Create Infrastructure as Code Template',
            'slug': 'create-iac-template',
            'description': 'Generate Infrastructure as Code templates',
            'template': '''Create Infrastructure as Code template.

**Infrastructure Type:** {{infrastructure_type}}
**Cloud Provider:** {{cloud_provider}}
**IaC Tool:** {{iac_tool}}

**Resources:**
{{resources}}

{{#if requirements}}
**Requirements:**
{{requirements}}
{{/if}}

Create comprehensive IaC template including:
1. Provider configuration
2. Resource definitions
3. Networking setup
4. Security groups/rules
5. IAM roles and policies
6. Storage configuration
7. Monitoring and logging
8. Outputs and variables
9. Documentation
10. Best practices''',
            'parameters': [
                {'name': 'infrastructure_type', 'type': 'text', 'required': True, 'description': 'Infrastructure type', 'example': 'Web application, API, Database'},
                {'name': 'cloud_provider', 'type': 'string', 'required': True, 'description': 'Cloud provider', 'allowed_values': ['AWS', 'Azure', 'GCP'], 'example': 'AWS'},
                {'name': 'iac_tool', 'type': 'string', 'required': True, 'description': 'IaC tool', 'allowed_values': ['Terraform', 'CloudFormation', 'Pulumi'], 'example': 'Terraform'},
                {'name': 'resources', 'type': 'long_text', 'required': True, 'description': 'Resources needed', 'example': 'EC2 instances, RDS database, S3 buckets, Load balancer...'},
                {'name': 'requirements', 'type': 'text', 'required': False, 'description': 'Requirements', 'default': ''}
            ],
            'tags': ['iac', 'terraform', 'infrastructure'],
            'recommended_agent': devops_agent,
            'required_capabilities': ['DEVOPS']
        },
        {
            'category': category,
            'name': 'Generate Security Hardening Checklist',
            'slug': 'generate-security-hardening',
            'description': 'Create security hardening checklist for infrastructure',
            'template': '''Generate security hardening checklist.

**Infrastructure:** {{infrastructure}}
**Environment:** {{environment}}

{{#if compliance_requirements}}
**Compliance Requirements:**
{{compliance_requirements}}
{{/if}}

Create comprehensive security checklist including:
1. Network security
2. Access control
3. Encryption (at rest, in transit)
4. Patch management
5. Logging and monitoring
6. Incident response
7. Backup and recovery
8. Vulnerability management
9. Compliance checks
10. Security best practices''',
            'parameters': [
                {'name': 'infrastructure', 'type': 'text', 'required': True, 'description': 'Infrastructure', 'example': 'AWS, Kubernetes, Docker'},
                {'name': 'environment', 'type': 'string', 'required': True, 'description': 'Environment', 'allowed_values': ['Development', 'Staging', 'Production'], 'example': 'Production'},
                {'name': 'compliance_requirements', 'type': 'text', 'required': False, 'description': 'Compliance requirements', 'default': ''}
            ],
            'tags': ['security', 'hardening', 'checklist'],
            'recommended_agent': devops_agent,
            'required_capabilities': ['DEVOPS']
        }
    ])
    
    return commands


def get_documentation_commands(category, doc_agent):
    """Get all Documentation command templates."""
    from apps.commands.commands_data import DOCUMENTATION_COMMANDS_DATA
    
    commands = []
    for cmd_data in DOCUMENTATION_COMMANDS_DATA:
        params = []
        for p in cmd_data['params']:
            param = {
                'name': p[0],
                'type': p[1],
                'required': p[2],
                'description': f'{p[0].replace("_", " ").title()}',
                'example': ''
            }
            if len(p) > 3 and isinstance(p[3], list):
                param['allowed_values'] = p[3]
            params.append(param)
        
        template = f'''Generate {cmd_data['name'].lower()}.

**Input:**
{chr(10).join(f"{{{{{{p[0]}}}}}}" for p in cmd_data['params'] if p[2])}

Create comprehensive, clear, and professional documentation.
Follow documentation best practices and ensure clarity for target audience.'''
        
        commands.append({
            'category': category,
            'name': cmd_data['name'],
            'slug': cmd_data['slug'],
            'description': cmd_data['desc'],
            'template': template,
            'parameters': params,
            'tags': cmd_data['tags'],
            'recommended_agent': doc_agent,
            'required_capabilities': ['DOCUMENTATION']
        })
    
    # Add additional documentation commands
    commands.extend([
        {
            'category': category,
            'name': 'Create API Reference Documentation',
            'slug': 'create-api-reference-docs',
            'description': 'Generate comprehensive API reference documentation',
            'template': '''Create API reference documentation.

**API Name:** {{api_name}}
**API Version:** {{api_version}}

**Endpoints:**
{{endpoints}}

{{#if authentication}}
**Authentication:** {{authentication}}
{{/if}}

Create comprehensive API reference including:
1. API overview and introduction
2. Authentication and authorization
3. Base URL and versioning
4. Endpoint documentation (method, path, parameters, request/response)
5. Error codes and handling
6. Rate limiting
7. Code examples (multiple languages)
8. SDK information
9. Changelog
10. Support and contact''',
            'parameters': [
                {'name': 'api_name', 'type': 'text', 'required': True, 'description': 'API name', 'example': 'User Management API'},
                {'name': 'api_version', 'type': 'text', 'required': True, 'description': 'API version', 'example': 'v1.0'},
                {'name': 'endpoints', 'type': 'long_text', 'required': True, 'description': 'API endpoints', 'example': 'GET /users, POST /users, PUT /users/{id}...'},
                {'name': 'authentication', 'type': 'text', 'required': False, 'description': 'Authentication method', 'default': 'JWT'}
            ],
            'tags': ['api-docs', 'reference', 'documentation'],
            'recommended_agent': doc_agent,
            'required_capabilities': ['DOCUMENTATION']
        },
        {
            'category': category,
            'name': 'Generate Developer Onboarding Guide',
            'slug': 'generate-developer-onboarding',
            'description': 'Create developer onboarding documentation',
            'template': '''Generate developer onboarding guide.

**Project:** {{project_name}}
**Tech Stack:**
{{tech_stack}}

**Development Environment:**
{{dev_environment}}

{{#if prerequisites}}
**Prerequisites:**
{{prerequisites}}
{{/if}}

Create comprehensive onboarding guide including:
1. Welcome and overview
2. Prerequisites and setup
3. Development environment setup
4. Project structure
5. Getting started (first contribution)
6. Coding standards and conventions
7. Testing guidelines
8. Git workflow
9. Common tasks and workflows
10. Resources and links
11. Troubleshooting
12. Contact and support''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'HishamOS'},
                {'name': 'tech_stack', 'type': 'text', 'required': True, 'description': 'Tech stack', 'example': 'Python, Django, React, TypeScript'},
                {'name': 'dev_environment', 'type': 'text', 'required': True, 'description': 'Development environment', 'example': 'Docker, Local setup'},
                {'name': 'prerequisites', 'type': 'text', 'required': False, 'description': 'Prerequisites', 'default': 'Python 3.10+, Node.js 18+'}
            ],
            'tags': ['onboarding', 'developer', 'guide'],
            'recommended_agent': doc_agent,
            'required_capabilities': ['DOCUMENTATION']
        },
        {
            'category': category,
            'name': 'Create Deployment Guide',
            'slug': 'create-deployment-guide',
            'description': 'Generate deployment and operations guide',
            'template': '''Create deployment guide.

**Application:** {{application_name}}
**Deployment Environment:** {{deployment_env}}

**Infrastructure:**
{{infrastructure}}

{{#if deployment_steps}}
**Deployment Steps:**
{{deployment_steps}}
{{/if}}

Create comprehensive deployment guide including:
1. Prerequisites and requirements
2. Environment setup
3. Configuration management
4. Database migrations
5. Build and deployment process
6. Health checks and verification
7. Rollback procedures
8. Monitoring and logging
9. Troubleshooting
10. Post-deployment checklist
11. Maintenance procedures
12. Disaster recovery''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'HishamOS'},
                {'name': 'deployment_env', 'type': 'text', 'required': True, 'description': 'Deployment environment', 'example': 'Production, Staging, Development'},
                {'name': 'infrastructure', 'type': 'text', 'required': True, 'description': 'Infrastructure', 'example': 'AWS, Kubernetes, Docker'},
                {'name': 'deployment_steps', 'type': 'text', 'required': False, 'description': 'Deployment steps', 'default': ''}
            ],
            'tags': ['deployment', 'operations', 'guide'],
            'recommended_agent': doc_agent,
            'required_capabilities': ['DOCUMENTATION']
        },
        {
            'category': category,
            'name': 'Create Code Documentation Template',
            'slug': 'create-code-documentation-template',
            'description': 'Generate code documentation template',
            'template': '''Create code documentation template.

**Code Type:** {{code_type}}
**Language:** {{language}}

**Functions/Classes:**
{{functions_classes}}

{{#if documentation_style}}
**Documentation Style:** {{documentation_style}}
{{/if}}

Create comprehensive code documentation including:
1. Function/class descriptions
2. Parameter documentation
3. Return value documentation
4. Usage examples
5. Error handling
6. Side effects
7. Performance notes
8. Related functions/classes
9. Version history
10. Author information''',
            'parameters': [
                {'name': 'code_type', 'type': 'text', 'required': True, 'description': 'Code type', 'example': 'Function, Class, Module'},
                {'name': 'language', 'type': 'text', 'required': True, 'description': 'Programming language', 'example': 'Python, JavaScript, Java'},
                {'name': 'functions_classes', 'type': 'long_text', 'required': True, 'description': 'Functions or classes', 'example': 'def calculate_total(), class UserService...'},
                {'name': 'documentation_style', 'type': 'string', 'required': False, 'description': 'Documentation style', 'allowed_values': ['Google', 'NumPy', 'Sphinx', 'JSDoc'], 'default': 'Google'}
            ],
            'tags': ['code-docs', 'documentation', 'template'],
            'recommended_agent': doc_agent,
            'required_capabilities': ['DOCUMENTATION']
        },
        {
            'category': category,
            'name': 'Generate User Manual',
            'slug': 'generate-user-manual',
            'description': 'Create comprehensive user manual',
            'template': '''Generate user manual.

**Product/Application:** {{product_name}}
**Target Audience:** {{target_audience}}

**Key Features:**
{{key_features}}

{{#if use_cases}}
**Use Cases:**
{{use_cases}}
{{/if}}

Create comprehensive user manual including:
1. Introduction and overview
2. Getting started guide
3. Feature descriptions
4. Step-by-step tutorials
5. Screenshots and diagrams
6. Troubleshooting section
7. FAQ
8. Keyboard shortcuts
9. Tips and tricks
10. Support information''',
            'parameters': [
                {'name': 'product_name', 'type': 'text', 'required': True, 'description': 'Product name', 'example': 'HishamOS'},
                {'name': 'target_audience', 'type': 'text', 'required': True, 'description': 'Target audience', 'example': 'End users, Administrators'},
                {'name': 'key_features', 'type': 'long_text', 'required': True, 'description': 'Key features', 'example': 'User management, Project tracking, AI agents...'},
                {'name': 'use_cases', 'type': 'text', 'required': False, 'description': 'Use cases', 'default': ''}
            ],
            'tags': ['user-manual', 'guide', 'documentation'],
            'recommended_agent': doc_agent,
            'required_capabilities': ['DOCUMENTATION']
        },
        {
            'category': category,
            'name': 'Create API Integration Guide',
            'slug': 'create-api-integration-guide',
            'description': 'Generate API integration guide for developers',
            'template': '''Create API integration guide.

**API Name:** {{api_name}}
**API Version:** {{api_version}}

**Integration Scenarios:**
{{integration_scenarios}}

{{#if sdk_available}}
**SDK Available:** {{sdk_available}}
{{/if}}

Create comprehensive integration guide including:
1. API overview
2. Authentication setup
3. Getting started (quick start)
4. Common integration patterns
5. Code examples (multiple languages)
6. Error handling
7. Rate limiting
8. Webhooks setup
9. Testing integration
10. Troubleshooting
11. Best practices
12. Support resources''',
            'parameters': [
                {'name': 'api_name', 'type': 'text', 'required': True, 'description': 'API name', 'example': 'HishamOS API'},
                {'name': 'api_version', 'type': 'text', 'required': True, 'description': 'API version', 'example': 'v1.0'},
                {'name': 'integration_scenarios', 'type': 'long_text', 'required': True, 'description': 'Integration scenarios', 'example': 'User management, Command execution, Webhook integration...'},
                {'name': 'sdk_available', 'type': 'text', 'required': False, 'description': 'SDK availability', 'default': 'Yes'}
            ],
            'tags': ['api-integration', 'developer', 'guide'],
            'recommended_agent': doc_agent,
            'required_capabilities': ['DOCUMENTATION']
        }
    ])
    
    return commands


def get_project_management_commands(category, pm_agent):
    """Get all Project Management command templates."""
    commands = [
        {
            'category': category,
            'name': 'Generate Sprint Plan',
            'slug': 'generate-sprint-plan',
            'description': 'Create detailed sprint plan with user stories, tasks, and timeline',
            'template': '''Create a sprint plan for the following project.

**Project:** {{project_name}}
**Sprint Duration:** {{sprint_duration}} days
**Team Capacity:** {{team_capacity}} story points
**User Stories:**
{{user_stories}}

{{#if sprint_goals}}
**Sprint Goals:**
{{sprint_goals}}
{{/if}}

Create a comprehensive sprint plan including:
1. Sprint goal and objectives
2. Selected user stories with story points
3. Task breakdown for each story
4. Daily standup agenda items
5. Sprint backlog prioritization
6. Risk identification and mitigation
7. Definition of Done checklist''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'sprint_duration', 'type': 'integer', 'required': True, 'description': 'Sprint duration in days', 'example': '14'},
                {'name': 'team_capacity', 'type': 'integer', 'required': True, 'description': 'Team velocity in story points', 'example': '40'},
                {'name': 'user_stories', 'type': 'long_text', 'required': True, 'description': 'List of user stories for the sprint', 'example': 'Story 1: User login...'},
                {'name': 'sprint_goals', 'type': 'text', 'required': False, 'description': 'Sprint goals and objectives', 'default': ''}
            ],
            'tags': ['sprint', 'planning', 'agile'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Create Task Breakdown',
            'slug': 'create-task-breakdown',
            'description': 'Break down user stories into actionable tasks',
            'template': '''Break down the following user story into actionable tasks.

**User Story:**
{{user_story}}

{{#if acceptance_criteria}}
**Acceptance Criteria:**
{{acceptance_criteria}}
{{/if}}

Create a detailed task breakdown including:
1. Technical tasks (development, testing, deployment)
2. Design tasks (UI/UX, wireframes)
3. Documentation tasks
4. Testing tasks (unit, integration, e2e)
5. Estimated hours for each task
6. Task dependencies
7. Assigned roles/responsibilities''',
            'parameters': [
                {'name': 'user_story', 'type': 'long_text', 'required': True, 'description': 'User story description', 'example': 'As a user, I want to login...'},
                {'name': 'acceptance_criteria', 'type': 'text', 'required': False, 'description': 'Acceptance criteria', 'default': ''}
            ],
            'tags': ['task-breakdown', 'agile', 'planning'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Generate Project Timeline',
            'slug': 'generate-project-timeline',
            'description': 'Create project timeline with milestones and dependencies',
            'template': '''Create a project timeline.

**Project:** {{project_name}}
**Start Date:** {{start_date}}
**End Date:** {{end_date}}
**Milestones:**
{{milestones}}

{{#if dependencies}}
**Dependencies:**
{{dependencies}}
{{/if}}

Generate a comprehensive timeline including:
1. Major milestones with dates
2. Phase breakdown (Planning, Development, Testing, Deployment)
3. Critical path identification
4. Buffer time recommendations
5. Risk mitigation timeline
6. Resource allocation timeline''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'start_date', 'type': 'date', 'required': True, 'description': 'Project start date', 'example': '2024-01-01'},
                {'name': 'end_date', 'type': 'date', 'required': True, 'description': 'Project end date', 'example': '2024-06-30'},
                {'name': 'milestones', 'type': 'long_text', 'required': True, 'description': 'List of project milestones', 'example': 'MVP Launch, Beta Release...'},
                {'name': 'dependencies', 'type': 'text', 'required': False, 'description': 'Project dependencies', 'default': ''}
            ],
            'tags': ['timeline', 'milestones', 'planning'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Create Risk Assessment',
            'slug': 'create-risk-assessment',
            'description': 'Identify and assess project risks',
            'template': '''Perform risk assessment for the project.

**Project:** {{project_name}}
**Project Type:** {{project_type}}
**Team Size:** {{team_size}}
**Timeline:** {{timeline}}

{{#if known_risks}}
**Known Risks:**
{{known_risks}}
{{/if}}

Create a comprehensive risk assessment including:
1. Technical risks (architecture, scalability, integration)
2. Resource risks (team availability, skills gap)
3. Timeline risks (scope creep, delays)
4. Business risks (market changes, stakeholder alignment)
5. Risk probability and impact matrix
6. Mitigation strategies for each risk
7. Contingency plans''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'project_type', 'type': 'text', 'required': True, 'description': 'Type of project', 'example': 'Web Application'},
                {'name': 'team_size', 'type': 'integer', 'required': True, 'description': 'Team size', 'example': '8'},
                {'name': 'timeline', 'type': 'text', 'required': True, 'description': 'Project timeline', 'example': '6 months'},
                {'name': 'known_risks', 'type': 'text', 'required': False, 'description': 'Any known risks', 'default': ''}
            ],
            'tags': ['risk-assessment', 'planning', 'management'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Generate Status Report',
            'slug': 'generate-status-report',
            'description': 'Create project status report for stakeholders',
            'template': '''Generate project status report.

**Project:** {{project_name}}
**Reporting Period:** {{reporting_period}}
**Current Sprint:** {{current_sprint}}

**Completed:**
{{completed_items}}

**In Progress:**
{{in_progress_items}}

**Blockers:**
{{blockers}}

{{#if metrics}}
**Metrics:**
{{metrics}}
{{/if}}

Create a comprehensive status report including:
1. Executive summary
2. Completed work (sprint/period)
3. Work in progress
4. Upcoming work
5. Blockers and issues
6. Metrics and KPIs
7. Risk updates
8. Next steps and recommendations''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'reporting_period', 'type': 'text', 'required': True, 'description': 'Reporting period', 'example': 'Week 1-2, January 2024'},
                {'name': 'current_sprint', 'type': 'text', 'required': True, 'description': 'Current sprint', 'example': 'Sprint 3'},
                {'name': 'completed_items', 'type': 'long_text', 'required': True, 'description': 'Completed work items', 'example': 'User authentication, Product catalog...'},
                {'name': 'in_progress_items', 'type': 'long_text', 'required': True, 'description': 'Work in progress', 'example': 'Shopping cart, Checkout...'},
                {'name': 'blockers', 'type': 'text', 'required': False, 'description': 'Current blockers', 'default': 'None'},
                {'name': 'metrics', 'type': 'text', 'required': False, 'description': 'Key metrics', 'default': ''}
            ],
            'tags': ['status-report', 'reporting', 'stakeholders'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Estimate Story Points',
            'slug': 'estimate-story-points',
            'description': 'Estimate story points for user stories using Fibonacci scale',
            'template': '''Estimate story points for user stories.

**User Stories:**
{{user_stories}}

{{#if reference_stories}}
**Reference Stories (for comparison):**
{{reference_stories}}
{{/if}}

{{#if team_velocity}}
**Team Velocity:** {{team_velocity}} story points per sprint
{{/if}}

Estimate story points for each story including:
1. Story point assignment (Fibonacci: 1, 2, 3, 5, 8, 13, 21)
2. Complexity analysis (effort, risk, uncertainty)
3. Comparison with reference stories
4. Justification for each estimate
5. Sprint capacity planning
6. Risk factors affecting estimates''',
            'parameters': [
                {'name': 'user_stories', 'type': 'long_text', 'required': True, 'description': 'User stories to estimate', 'example': 'Story 1: User login...'},
                {'name': 'reference_stories', 'type': 'text', 'required': False, 'description': 'Reference stories for comparison', 'default': ''},
                {'name': 'team_velocity', 'type': 'integer', 'required': False, 'description': 'Team velocity in story points', 'default': ''}
            ],
            'tags': ['estimation', 'story-points', 'planning'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Create Release Plan',
            'slug': 'create-release-plan',
            'description': 'Plan product releases with features and timeline',
            'template': '''Create release plan.

**Product:** {{product_name}}
**Release Goal:** {{release_goal}}
**Target Date:** {{target_date}}
**Features:**
{{features}}

{{#if dependencies}}
**Dependencies:**
{{dependencies}}
{{/if}}

Create comprehensive release plan including:
1. Release objectives and goals
2. Feature prioritization
3. Sprint allocation per feature
4. Release timeline with milestones
5. Risk assessment
6. Resource requirements
7. Testing and QA schedule
8. Go-live checklist''',
            'parameters': [
                {'name': 'product_name', 'type': 'text', 'required': True, 'description': 'Product name', 'example': 'E-commerce Platform'},
                {'name': 'release_goal', 'type': 'text', 'required': True, 'description': 'Release goal', 'example': 'MVP Launch'},
                {'name': 'target_date', 'type': 'date', 'required': True, 'description': 'Target release date', 'example': '2024-06-30'},
                {'name': 'features', 'type': 'long_text', 'required': True, 'description': 'List of features', 'example': 'User authentication, Product catalog...'},
                {'name': 'dependencies', 'type': 'text', 'required': False, 'description': 'Feature dependencies', 'default': ''}
            ],
            'tags': ['release-planning', 'roadmap', 'milestones'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Generate Retrospective Report',
            'slug': 'generate-retrospective-report',
            'description': 'Create sprint retrospective with insights and action items',
            'template': '''Generate sprint retrospective report.

**Sprint:** {{sprint_name}}
**Sprint Duration:** {{sprint_duration}} days
**Team Members:**
{{team_members}}

**What Went Well:**
{{what_went_well}}

**What Could Be Improved:**
{{what_could_improve}}

**Action Items:**
{{action_items}}

Create comprehensive retrospective including:
1. Sprint summary and achievements
2. What went well (celebrations)
3. What could be improved (challenges)
4. Action items with owners
5. Team velocity and metrics
6. Process improvements
7. Next sprint focus areas''',
            'parameters': [
                {'name': 'sprint_name', 'type': 'text', 'required': True, 'description': 'Sprint name', 'example': 'Sprint 3'},
                {'name': 'sprint_duration', 'type': 'integer', 'required': True, 'description': 'Sprint duration in days', 'example': '14'},
                {'name': 'team_members', 'type': 'text', 'required': True, 'description': 'Team members', 'example': 'John, Jane, Bob...'},
                {'name': 'what_went_well', 'type': 'long_text', 'required': True, 'description': 'What went well', 'example': 'Completed all stories, good collaboration...'},
                {'name': 'what_could_improve', 'type': 'long_text', 'required': True, 'description': 'What could be improved', 'example': 'Better estimation, more testing...'},
                {'name': 'action_items', 'type': 'text', 'required': False, 'description': 'Action items', 'default': ''}
            ],
            'tags': ['retrospective', 'agile', 'improvement'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Create Resource Allocation Plan',
            'slug': 'create-resource-allocation',
            'description': 'Plan resource allocation across projects and tasks',
            'template': '''Create resource allocation plan.

**Project:** {{project_name}}
**Timeline:** {{timeline}}
**Team Members:**
{{team_members}}

**Tasks/Features:**
{{tasks}}

{{#if constraints}}
**Constraints:**
{{constraints}}
{{/if}}

Create comprehensive resource allocation including:
1. Resource inventory (skills, availability)
2. Task-resource mapping
3. Workload distribution
4. Capacity planning
5. Skill gap analysis
6. Resource conflicts and resolutions
7. Timeline adjustments
8. Recommendations''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'timeline', 'type': 'text', 'required': True, 'description': 'Project timeline', 'example': '6 months'},
                {'name': 'team_members', 'type': 'long_text', 'required': True, 'description': 'Team members with skills', 'example': 'John (Frontend), Jane (Backend)...'},
                {'name': 'tasks', 'type': 'long_text', 'required': True, 'description': 'Tasks or features', 'example': 'User auth, Product catalog...'},
                {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Resource constraints', 'default': ''}
            ],
            'tags': ['resource-allocation', 'planning', 'capacity'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Generate Burndown Chart Data',
            'slug': 'generate-burndown-chart',
            'description': 'Create burndown chart data for sprint tracking',
            'template': '''Generate burndown chart data.

**Sprint:** {{sprint_name}}
**Sprint Duration:** {{sprint_duration}} days
**Total Story Points:** {{total_story_points}}
**Daily Progress:**
{{daily_progress}}

{{#if completed_stories}}
**Completed Stories:**
{{completed_stories}}
{{/if}}

Generate burndown chart data including:
1. Ideal burndown line (linear)
2. Actual burndown line (daily progress)
3. Remaining work calculation
4. Velocity tracking
5. Trend analysis
6. Forecast completion date
7. Risk indicators
8. Recommendations''',
            'parameters': [
                {'name': 'sprint_name', 'type': 'text', 'required': True, 'description': 'Sprint name', 'example': 'Sprint 3'},
                {'name': 'sprint_duration', 'type': 'integer', 'required': True, 'description': 'Sprint duration in days', 'example': '14'},
                {'name': 'total_story_points', 'type': 'integer', 'required': True, 'description': 'Total story points', 'example': '40'},
                {'name': 'daily_progress', 'type': 'long_text', 'required': True, 'description': 'Daily progress (day: remaining points)', 'example': 'Day 1: 40, Day 2: 35...'},
                {'name': 'completed_stories', 'type': 'text', 'required': False, 'description': 'Completed stories', 'default': ''}
            ],
            'tags': ['burndown', 'tracking', 'metrics'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Create Stakeholder Communication Plan',
            'slug': 'create-stakeholder-communication',
            'description': 'Develop communication plan for project stakeholders',
            'template': '''Create stakeholder communication plan.

**Project:** {{project_name}}
**Stakeholders:**
{{stakeholders}}

**Communication Objectives:**
{{communication_objectives}}

{{#if communication_channels}}
**Available Channels:**
{{communication_channels}}
{{/if}}

Create comprehensive communication plan including:
1. Stakeholder analysis and mapping
2. Communication objectives
3. Message types and frequency
4. Communication channels and methods
5. Meeting schedules and formats
6. Reporting structure
7. Escalation procedures
8. Feedback mechanisms''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'stakeholders', 'type': 'long_text', 'required': True, 'description': 'Stakeholders', 'example': 'CEO, CTO, Product Manager, Engineering Lead...'},
                {'name': 'communication_objectives', 'type': 'long_text', 'required': True, 'description': 'Communication objectives', 'example': 'Keep stakeholders informed, Get approvals...'},
                {'name': 'communication_channels', 'type': 'text', 'required': False, 'description': 'Available channels', 'default': 'Email, Slack, Meetings, Reports'}
            ],
            'tags': ['communication', 'stakeholders', 'planning'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Generate Change Request Template',
            'slug': 'generate-change-request-template',
            'description': 'Create change request template for scope changes',
            'template': '''Generate change request template.

**Project:** {{project_name}}
**Change Type:** {{change_type}}
**Change Description:**
{{change_description}}

**Reason for Change:**
{{reason_for_change}}

{{#if impact_analysis}}
**Impact Analysis:**
{{impact_analysis}}
{{/if}}

Create comprehensive change request including:
1. Change description and rationale
2. Impact analysis (scope, timeline, budget, resources)
3. Alternatives considered
4. Risk assessment
5. Approval requirements
6. Implementation plan
7. Rollback strategy
8. Sign-off section''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'change_type', 'type': 'string', 'required': True, 'description': 'Change type', 'allowed_values': ['Scope', 'Timeline', 'Budget', 'Resources', 'Technical'], 'example': 'Scope'},
                {'name': 'change_description', 'type': 'long_text', 'required': True, 'description': 'Change description', 'example': 'Add payment gateway integration'},
                {'name': 'reason_for_change', 'type': 'long_text', 'required': True, 'description': 'Reason for change', 'example': 'Customer requirement, Market demand...'},
                {'name': 'impact_analysis', 'type': 'text', 'required': False, 'description': 'Impact analysis', 'default': ''}
            ],
            'tags': ['change-request', 'scope', 'management'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Create Project Charter',
            'slug': 'create-project-charter',
            'description': 'Generate comprehensive project charter document',
            'template': '''Create project charter.

**Project Name:** {{project_name}}
**Project Sponsor:** {{project_sponsor}}
**Project Manager:** {{project_manager}}
**Business Case:** {{business_case}}

**Project Objectives:**
{{objectives}}

{{#if success_criteria}}
**Success Criteria:**
{{success_criteria}}
{{/if}}

Create comprehensive project charter including:
1. Project overview and purpose
2. Business case and justification
3. Project objectives and goals
4. Scope definition (in-scope and out-of-scope)
5. Key stakeholders and roles
6. High-level timeline and milestones
7. Budget and resource requirements
8. Assumptions and constraints
9. Risks and mitigation strategies
10. Success criteria and KPIs
11. Approval and sign-off''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'project_sponsor', 'type': 'text', 'required': True, 'description': 'Project sponsor', 'example': 'CEO'},
                {'name': 'project_manager', 'type': 'text', 'required': True, 'description': 'Project manager', 'example': 'John Doe'},
                {'name': 'business_case', 'type': 'long_text', 'required': True, 'description': 'Business case', 'example': 'Expand market reach, increase revenue...'},
                {'name': 'objectives', 'type': 'long_text', 'required': True, 'description': 'Project objectives', 'example': 'Launch MVP, Acquire 1000 users...'},
                {'name': 'success_criteria', 'type': 'text', 'required': False, 'description': 'Success criteria', 'default': ''}
            ],
            'tags': ['project-charter', 'initiation', 'planning'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Generate Quality Assurance Plan',
            'slug': 'generate-qa-plan',
            'description': 'Create quality assurance and testing plan',
            'template': '''Generate quality assurance plan.

**Project:** {{project_name}}
**Quality Standards:** {{quality_standards}}
**Testing Scope:**
{{testing_scope}}

{{#if quality_metrics}}
**Quality Metrics:**
{{quality_metrics}}
{{/if}}

Create comprehensive QA plan including:
1. Quality objectives and standards
2. Testing strategy and approach
3. Test types (unit, integration, system, UAT)
4. Test environment requirements
5. Test data management
6. Defect management process
7. Quality metrics and KPIs
8. Risk-based testing approach
9. Test schedule and milestones
10. Resource requirements
11. Tools and automation strategy''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'quality_standards', 'type': 'text', 'required': True, 'description': 'Quality standards', 'example': 'ISO 9001, CMMI Level 3'},
                {'name': 'testing_scope', 'type': 'long_text', 'required': True, 'description': 'Testing scope', 'example': 'All features, API endpoints, UI components...'},
                {'name': 'quality_metrics', 'type': 'text', 'required': False, 'description': 'Quality metrics', 'default': 'Defect density, Test coverage, Pass rate'}
            ],
            'tags': ['qa', 'quality', 'testing', 'planning'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Create Lessons Learned Document',
            'slug': 'create-lessons-learned',
            'description': 'Document project lessons learned and best practices',
            'template': '''Create lessons learned document.

**Project:** {{project_name}}
**Project Duration:** {{project_duration}}
**Project Status:** {{project_status}}

**What Went Well:**
{{what_went_well}}

**What Could Be Improved:**
{{what_could_improve}}

**Challenges Faced:**
{{challenges}}

{{#if recommendations}}
**Recommendations:**
{{recommendations}}
{{/if}}

Create comprehensive lessons learned including:
1. Project summary
2. What went well (successes)
3. What could be improved (challenges)
4. Key learnings and insights
5. Process improvements
6. Tool and technology recommendations
7. Team dynamics and collaboration
8. Risk management lessons
9. Best practices identified
10. Recommendations for future projects''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'project_duration', 'type': 'text', 'required': True, 'description': 'Project duration', 'example': '6 months'},
                {'name': 'project_status', 'type': 'string', 'required': True, 'description': 'Project status', 'allowed_values': ['Completed', 'Cancelled', 'On Hold'], 'example': 'Completed'},
                {'name': 'what_went_well', 'type': 'long_text', 'required': True, 'description': 'What went well', 'example': 'Good team collaboration, Clear requirements...'},
                {'name': 'what_could_improve', 'type': 'long_text', 'required': True, 'description': 'What could be improved', 'example': 'Better estimation, More testing...'},
                {'name': 'challenges', 'type': 'long_text', 'required': True, 'description': 'Challenges faced', 'example': 'Scope creep, Resource constraints...'},
                {'name': 'recommendations', 'type': 'text', 'required': False, 'description': 'Recommendations', 'default': ''}
            ],
            'tags': ['lessons-learned', 'knowledge-management', 'improvement'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Generate Project Closure Report',
            'slug': 'generate-project-closure-report',
            'description': 'Create project closure and handover report',
            'template': '''Generate project closure report.

**Project:** {{project_name}}
**Project End Date:** {{end_date}}
**Final Status:** {{final_status}}

**Deliverables:**
{{deliverables}}

**Final Metrics:**
{{final_metrics}}

{{#if handover_items}}
**Handover Items:**
{{handover_items}}
{{/if}}

Create comprehensive closure report including:
1. Executive summary
2. Project objectives achievement
3. Deliverables summary
4. Final budget and timeline
5. Final metrics and KPIs
6. Lessons learned summary
7. Outstanding issues and risks
8. Handover documentation
9. Support and maintenance plan
10. Sign-off and approvals''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'end_date', 'type': 'date', 'required': True, 'description': 'Project end date', 'example': '2024-06-30'},
                {'name': 'final_status', 'type': 'string', 'required': True, 'description': 'Final status', 'allowed_values': ['Completed', 'Cancelled', 'On Hold'], 'example': 'Completed'},
                {'name': 'deliverables', 'type': 'long_text', 'required': True, 'description': 'Project deliverables', 'example': 'MVP launched, Documentation complete...'},
                {'name': 'final_metrics', 'type': 'long_text', 'required': True, 'description': 'Final metrics', 'example': 'Budget: $100k, Timeline: 6 months, Quality: 95%...'},
                {'name': 'handover_items', 'type': 'text', 'required': False, 'description': 'Handover items', 'default': ''}
            ],
            'tags': ['project-closure', 'handover', 'reporting'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Create Dependency Management Plan',
            'slug': 'create-dependency-management',
            'description': 'Plan and manage project dependencies',
            'template': '''Create dependency management plan.

**Project:** {{project_name}}
**Dependencies:**
{{dependencies}}

{{#if external_dependencies}}
**External Dependencies:**
{{external_dependencies}}
{{/if}}

Create comprehensive dependency plan including:
1. Dependency identification
2. Dependency types (internal, external, technical, business)
3. Dependency mapping and relationships
4. Critical path analysis
5. Risk assessment for each dependency
6. Mitigation strategies
7. Contingency plans
8. Monitoring and tracking approach
9. Escalation procedures
10. Communication plan''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'dependencies', 'type': 'long_text', 'required': True, 'description': 'Project dependencies', 'example': 'API integration, Payment gateway, Design system...'},
                {'name': 'external_dependencies', 'type': 'text', 'required': False, 'description': 'External dependencies', 'default': ''}
            ],
            'tags': ['dependencies', 'planning', 'risk-management'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Generate Team Performance Report',
            'slug': 'generate-team-performance-report',
            'description': 'Analyze and report on team performance',
            'template': '''Generate team performance report.

**Team:** {{team_name}}
**Reporting Period:** {{reporting_period}}
**Team Members:**
{{team_members}}

**Performance Metrics:**
{{performance_metrics}}

{{#if achievements}}
**Achievements:**
{{achievements}}
{{/if}}

Create comprehensive performance report including:
1. Team overview
2. Performance metrics (velocity, quality, delivery)
3. Individual contributions
4. Team achievements
5. Areas for improvement
6. Skill development needs
7. Team dynamics assessment
8. Recommendations
9. Recognition and rewards
10. Action items''',
            'parameters': [
                {'name': 'team_name', 'type': 'text', 'required': True, 'description': 'Team name', 'example': 'Frontend Team'},
                {'name': 'reporting_period', 'type': 'text', 'required': True, 'description': 'Reporting period', 'example': 'Q1 2024'},
                {'name': 'team_members', 'type': 'long_text', 'required': True, 'description': 'Team members', 'example': 'John, Jane, Bob...'},
                {'name': 'performance_metrics', 'type': 'long_text', 'required': True, 'description': 'Performance metrics', 'example': 'Velocity: 40 SP, Quality: 95%, On-time: 90%...'},
                {'name': 'achievements', 'type': 'text', 'required': False, 'description': 'Key achievements', 'default': ''}
            ],
            'tags': ['team-performance', 'metrics', 'reporting'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Create Project Budget Plan',
            'slug': 'create-project-budget-plan',
            'description': 'Develop comprehensive project budget',
            'template': '''Create project budget plan.

**Project:** {{project_name}}
**Budget Period:** {{budget_period}}
**Total Budget:** {{total_budget}}

**Budget Categories:**
{{budget_categories}}

{{#if assumptions}}
**Assumptions:**
{{assumptions}}
{{/if}}

Create comprehensive budget plan including:
1. Budget overview and summary
2. Budget breakdown by category (personnel, infrastructure, tools, etc.)
3. Cost estimates and rationale
4. Contingency allocation
5. Budget timeline and phasing
6. Cost tracking approach
7. Variance management
8. Approval requirements
9. Budget controls and limits
10. Reporting schedule''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'budget_period', 'type': 'text', 'required': True, 'description': 'Budget period', 'example': '6 months'},
                {'name': 'total_budget', 'type': 'text', 'required': True, 'description': 'Total budget', 'example': '$500,000'},
                {'name': 'budget_categories', 'type': 'long_text', 'required': True, 'description': 'Budget categories', 'example': 'Personnel: $300k, Infrastructure: $100k, Tools: $50k...'},
                {'name': 'assumptions', 'type': 'text', 'required': False, 'description': 'Budget assumptions', 'default': ''}
            ],
            'tags': ['budget', 'financial', 'planning'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        },
        {
            'category': category,
            'name': 'Generate Stakeholder Engagement Plan',
            'slug': 'generate-stakeholder-engagement-plan',
            'description': 'Plan stakeholder engagement and communication',
            'template': '''Generate stakeholder engagement plan.

**Project:** {{project_name}}
**Stakeholders:**
{{stakeholders}}

**Engagement Objectives:**
{{engagement_objectives}}

{{#if communication_preferences}}
**Communication Preferences:**
{{communication_preferences}}
{{/if}}

Create comprehensive engagement plan including:
1. Stakeholder analysis and mapping
2. Engagement objectives
3. Communication strategy
4. Engagement activities and frequency
5. Communication channels and methods
6. Meeting schedules
7. Reporting structure
8. Feedback mechanisms
9. Conflict resolution approach
10. Success metrics''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'stakeholders', 'type': 'long_text', 'required': True, 'description': 'Stakeholders', 'example': 'CEO, CTO, Product Manager, End Users...'},
                {'name': 'engagement_objectives', 'type': 'long_text', 'required': True, 'description': 'Engagement objectives', 'example': 'Keep informed, Get approvals, Gather feedback...'},
                {'name': 'communication_preferences', 'type': 'text', 'required': False, 'description': 'Communication preferences', 'default': ''}
            ],
            'tags': ['stakeholder-engagement', 'communication', 'planning'],
            'recommended_agent': pm_agent,
            'required_capabilities': ['PROJECT_MANAGEMENT']
        }
    ]
    
    return commands


def get_design_architecture_commands(category, coding_agent):
    """Get all Design & Architecture command templates."""
    commands = [
        {
            'category': category,
            'name': 'Create System Architecture Design',
            'slug': 'create-system-architecture',
            'description': 'Design system architecture with components and interactions',
            'template': '''Design system architecture.

**System:** {{system_name}}
**Requirements:**
{{requirements}}

{{#if constraints}}
**Constraints:**
{{constraints}}
{{/if}}

{{#if scale_requirements}}
**Scale Requirements:**
{{scale_requirements}}
{{/if}}

Create comprehensive architecture design including:
1. High-level system architecture diagram
2. Component breakdown and responsibilities
3. Data flow diagrams
4. Technology stack recommendations
5. Scalability and performance considerations
6. Security architecture
7. Integration points and APIs
8. Deployment architecture''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'E-commerce Platform'},
                {'name': 'requirements', 'type': 'long_text', 'required': True, 'description': 'System requirements', 'example': 'Handle 1M users, real-time inventory...'},
                {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Technical constraints', 'default': ''},
                {'name': 'scale_requirements', 'type': 'text', 'required': False, 'description': 'Scale and performance requirements', 'default': ''}
            ],
            'tags': ['architecture', 'system-design', 'scalability'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Design Database Schema',
            'slug': 'design-database-schema',
            'description': 'Create normalized database schema design',
            'template': '''Design database schema.

**Application:** {{application_name}}
**Entities:**
{{entities}}

{{#if relationships}}
**Relationships:**
{{relationships}}
{{/if}}

{{#if requirements}}
**Requirements:**
{{requirements}}
{{/if}}

Create comprehensive database design including:
1. Entity-Relationship Diagram (ERD)
2. Table definitions with columns and data types
3. Primary keys, foreign keys, and indexes
4. Normalization (1NF, 2NF, 3NF)
5. Relationships and cardinality
6. Data constraints and validations
7. Performance optimization recommendations
8. Migration strategy''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'E-commerce Platform'},
                {'name': 'entities', 'type': 'long_text', 'required': True, 'description': 'List of entities', 'example': 'User, Product, Order, Cart...'},
                {'name': 'relationships', 'type': 'text', 'required': False, 'description': 'Entity relationships', 'default': ''},
                {'name': 'requirements', 'type': 'text', 'required': False, 'description': 'Additional requirements', 'default': ''}
            ],
            'tags': ['database', 'schema', 'erd', 'design'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Create API Design',
            'slug': 'create-api-design',
            'description': 'Design RESTful API with endpoints and contracts',
            'template': '''Design RESTful API.

**Service:** {{service_name}}
**Functionality:**
{{functionality}}

{{#if entities}}
**Entities:**
{{entities}}
{{/if}}

{{#if authentication}}
**Authentication:** {{authentication}}
{{/if}}

Create comprehensive API design including:
1. API endpoints with HTTP methods
2. Request/response schemas
3. Authentication and authorization
4. Error handling and status codes
5. Rate limiting strategy
6. API versioning approach
7. Documentation structure
8. Testing strategy''',
            'parameters': [
                {'name': 'service_name', 'type': 'text', 'required': True, 'description': 'Service name', 'example': 'User Management Service'},
                {'name': 'functionality', 'type': 'long_text', 'required': True, 'description': 'Service functionality', 'example': 'User CRUD operations, authentication...'},
                {'name': 'entities', 'type': 'text', 'required': False, 'description': 'Main entities', 'default': ''},
                {'name': 'authentication', 'type': 'text', 'required': False, 'description': 'Authentication method', 'default': 'JWT'}
            ],
            'tags': ['api', 'rest', 'design', 'endpoints'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Design Microservices Architecture',
            'slug': 'design-microservices',
            'description': 'Design microservices architecture with service boundaries',
            'template': '''Design microservices architecture.

**System:** {{system_name}}
**Monolithic Components:**
{{monolithic_components}}

{{#if requirements}}
**Requirements:**
{{requirements}}
{{/if}}

Create comprehensive microservices design including:
1. Service boundaries and responsibilities
2. Service communication patterns (sync/async)
3. Data management strategy (database per service)
4. API gateway design
5. Service discovery and configuration
6. Distributed transaction handling
7. Monitoring and observability
8. Deployment and scaling strategy''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'E-commerce Platform'},
                {'name': 'monolithic_components', 'type': 'long_text', 'required': True, 'description': 'Current monolithic components', 'example': 'User service, Product service, Order service...'},
                {'name': 'requirements', 'type': 'text', 'required': False, 'description': 'Additional requirements', 'default': ''}
            ],
            'tags': ['microservices', 'architecture', 'distributed-systems'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Create Technical Design Document',
            'slug': 'create-technical-design-doc',
            'description': 'Generate comprehensive technical design document',
            'template': '''Create technical design document.

**Feature/System:** {{feature_name}}
**Requirements:**
{{requirements}}

{{#if current_system}}
**Current System:**
{{current_system}}
{{/if}}

Create comprehensive technical design document including:
1. Overview and objectives
2. Current state analysis
3. Proposed solution architecture
4. Component design and interactions
5. Data models and schemas
6. API specifications
7. Security considerations
8. Performance requirements
9. Testing strategy
10. Deployment plan
11. Risk assessment
12. Timeline and milestones''',
            'parameters': [
                {'name': 'feature_name', 'type': 'text', 'required': True, 'description': 'Feature or system name', 'example': 'User Authentication System'},
                {'name': 'requirements', 'type': 'long_text', 'required': True, 'description': 'Feature requirements', 'example': 'OAuth2, 2FA, password reset...'},
                {'name': 'current_system', 'type': 'text', 'required': False, 'description': 'Current system description', 'default': ''}
            ],
            'tags': ['design-doc', 'technical-spec', 'architecture'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Design Security Architecture',
            'slug': 'design-security-architecture',
            'description': 'Design security architecture with authentication and authorization',
            'template': '''Design security architecture.

**System:** {{system_name}}
**Security Requirements:**
{{security_requirements}}

{{#if compliance_requirements}}
**Compliance Requirements:**
{{compliance_requirements}}
{{/if}}

{{#if threat_model}}
**Threat Model:**
{{threat_model}}
{{/if}}

Create comprehensive security architecture including:
1. Authentication strategy (OAuth, JWT, SAML)
2. Authorization model (RBAC, ABAC)
3. Data encryption (at rest, in transit)
4. API security (rate limiting, input validation)
5. Network security (firewalls, VPN)
6. Security monitoring and logging
7. Incident response plan
8. Compliance mapping''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'E-commerce Platform'},
                {'name': 'security_requirements', 'type': 'long_text', 'required': True, 'description': 'Security requirements', 'example': 'PCI-DSS, GDPR, 2FA...'},
                {'name': 'compliance_requirements', 'type': 'text', 'required': False, 'description': 'Compliance requirements', 'default': ''},
                {'name': 'threat_model', 'type': 'text', 'required': False, 'description': 'Threat model', 'default': ''}
            ],
            'tags': ['security', 'architecture', 'compliance'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Design Scalable System Architecture',
            'slug': 'design-scalable-architecture',
            'description': 'Design system architecture for high scalability',
            'template': '''Design scalable system architecture.

**System:** {{system_name}}
**Expected Load:** {{expected_load}}
**Growth Projection:** {{growth_projection}}

{{#if current_architecture}}
**Current Architecture:**
{{current_architecture}}
{{/if}}

{{#if scalability_requirements}}
**Scalability Requirements:**
{{scalability_requirements}}
{{/if}}

Create comprehensive scalable architecture including:
1. Horizontal vs vertical scaling strategy
2. Load balancing architecture
3. Caching strategy (CDN, Redis, Memcached)
4. Database scaling (read replicas, sharding)
5. Message queue architecture
6. Auto-scaling configuration
7. Performance optimization
8. Cost analysis''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'E-commerce Platform'},
                {'name': 'expected_load', 'type': 'text', 'required': True, 'description': 'Expected load', 'example': '1M users, 10K requests/sec'},
                {'name': 'growth_projection', 'type': 'text', 'required': True, 'description': 'Growth projection', 'example': '10x in 2 years'},
                {'name': 'current_architecture', 'type': 'text', 'required': False, 'description': 'Current architecture', 'default': ''},
                {'name': 'scalability_requirements', 'type': 'text', 'required': False, 'description': 'Scalability requirements', 'default': ''}
            ],
            'tags': ['scalability', 'architecture', 'performance'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Create Component Architecture',
            'slug': 'create-component-architecture',
            'description': 'Design component-based architecture',
            'template': '''Create component architecture.

**Application:** {{application_name}}
**Framework:** {{framework}}
**Components:**
{{components}}

{{#if design_principles}}
**Design Principles:**
{{design_principles}}
{{/if}}

Create comprehensive component architecture including:
1. Component hierarchy and structure
2. Component responsibilities
3. Component interfaces and APIs
4. Data flow between components
5. State management strategy
6. Reusability patterns
7. Testing strategy
8. Documentation structure''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'Admin Dashboard'},
                {'name': 'framework', 'type': 'text', 'required': True, 'description': 'Framework used', 'example': 'React'},
                {'name': 'components', 'type': 'long_text', 'required': True, 'description': 'List of components', 'example': 'UserList, UserForm, Dashboard...'},
                {'name': 'design_principles', 'type': 'text', 'required': False, 'description': 'Design principles', 'default': ''}
            ],
            'tags': ['components', 'architecture', 'design'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Design Event-Driven Architecture',
            'slug': 'design-event-driven-architecture',
            'description': 'Design event-driven system architecture',
            'template': '''Design event-driven architecture.

**System:** {{system_name}}
**Event Sources:**
{{event_sources}}

**Event Consumers:**
{{event_consumers}}

{{#if event_types}}
**Event Types:**
{{event_types}}
{{/if}}

Create comprehensive event-driven architecture including:
1. Event sources and producers
2. Event bus/message broker selection
3. Event schema and versioning
4. Event consumers and handlers
5. Event routing and filtering
6. Eventual consistency patterns
7. Error handling and retry logic
8. Monitoring and observability''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'Order Processing System'},
                {'name': 'event_sources', 'type': 'long_text', 'required': True, 'description': 'Event sources', 'example': 'User actions, Payment gateway, Inventory...'},
                {'name': 'event_consumers', 'type': 'long_text', 'required': True, 'description': 'Event consumers', 'example': 'Email service, Analytics, Notifications...'},
                {'name': 'event_types', 'type': 'text', 'required': False, 'description': 'Event types', 'default': ''}
            ],
            'tags': ['event-driven', 'architecture', 'messaging'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Design Data Pipeline Architecture',
            'slug': 'design-data-pipeline',
            'description': 'Design data processing and pipeline architecture',
            'template': '''Design data pipeline architecture.

**Pipeline Purpose:** {{pipeline_purpose}}
**Data Sources:**
{{data_sources}}

**Data Destinations:**
{{data_destinations}}

{{#if processing_requirements}}
**Processing Requirements:**
{{processing_requirements}}
{{/if}}

{{#if volume}}
**Data Volume:** {{volume}}
{{/if}}

Create comprehensive data pipeline including:
1. Data ingestion strategy
2. Data transformation steps
3. Data validation and quality checks
4. Error handling and dead letter queues
5. Data storage and partitioning
6. Batch vs stream processing
7. Monitoring and alerting
8. Cost optimization''',
            'parameters': [
                {'name': 'pipeline_purpose', 'type': 'text', 'required': True, 'description': 'Pipeline purpose', 'example': 'ETL for analytics'},
                {'name': 'data_sources', 'type': 'long_text', 'required': True, 'description': 'Data sources', 'example': 'Database, APIs, Files...'},
                {'name': 'data_destinations', 'type': 'long_text', 'required': True, 'description': 'Data destinations', 'example': 'Data warehouse, Analytics DB...'},
                {'name': 'processing_requirements', 'type': 'text', 'required': False, 'description': 'Processing requirements', 'default': ''},
                {'name': 'volume', 'type': 'text', 'required': False, 'description': 'Data volume', 'default': ''}
            ],
            'tags': ['data-pipeline', 'etl', 'architecture'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Design Caching Strategy',
            'slug': 'design-caching-strategy',
            'description': 'Design comprehensive caching strategy for application',
            'template': '''Design caching strategy.

**Application:** {{application_name}}
**Performance Requirements:**
{{performance_requirements}}

**Data Types:**
{{data_types}}

{{#if current_performance}}
**Current Performance Issues:**
{{current_performance}}
{{/if}}

Create comprehensive caching strategy including:
1. Cache layers (browser, CDN, application, database)
2. Cache invalidation strategy
3. Cache key design
4. TTL (Time To Live) policies
5. Cache warming strategies
6. Distributed caching architecture
7. Cache monitoring and metrics
8. Cost-benefit analysis''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'E-commerce Platform'},
                {'name': 'performance_requirements', 'type': 'long_text', 'required': True, 'description': 'Performance requirements', 'example': 'Page load < 2s, API response < 500ms...'},
                {'name': 'data_types', 'type': 'long_text', 'required': True, 'description': 'Data types to cache', 'example': 'Product catalog, User sessions, API responses...'},
                {'name': 'current_performance', 'type': 'text', 'required': False, 'description': 'Current performance issues', 'default': ''}
            ],
            'tags': ['caching', 'performance', 'architecture'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Create Load Balancing Architecture',
            'slug': 'create-load-balancing-architecture',
            'description': 'Design load balancing architecture for high availability',
            'template': '''Create load balancing architecture.

**System:** {{system_name}}
**Traffic Patterns:**
{{traffic_patterns}}

**Availability Requirements:**
{{availability_requirements}}

{{#if current_setup}}
**Current Setup:**
{{current_setup}}
{{/if}}

Create comprehensive load balancing design including:
1. Load balancer types (application, network, DNS)
2. Load balancing algorithms (round-robin, least connections, weighted)
3. Health check configuration
4. Session persistence strategy
5. SSL termination
6. Failover and redundancy
7. Geographic distribution
8. Monitoring and alerting''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'API Gateway'},
                {'name': 'traffic_patterns', 'type': 'long_text', 'required': True, 'description': 'Traffic patterns', 'example': '10K requests/min, Peak at 50K...'},
                {'name': 'availability_requirements', 'type': 'text', 'required': True, 'description': 'Availability requirements', 'example': '99.9% uptime, < 1s failover'},
                {'name': 'current_setup', 'type': 'text', 'required': False, 'description': 'Current setup', 'default': ''}
            ],
            'tags': ['load-balancing', 'high-availability', 'architecture'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Design Multi-Tenant Architecture',
            'slug': 'design-multi-tenant-architecture',
            'description': 'Design multi-tenant system architecture',
            'template': '''Design multi-tenant architecture.

**Application:** {{application_name}}
**Tenant Model:** {{tenant_model}}

**Tenant Requirements:**
{{tenant_requirements}}

{{#if isolation_level}}
**Isolation Level:** {{isolation_level}}
{{/if}}

Create comprehensive multi-tenant design including:
1. Tenant model (shared database, separate databases, hybrid)
2. Data isolation strategy
3. Tenant identification
4. Resource isolation
5. Security and access control
6. Performance considerations
7. Scalability approach
8. Billing and metering
9. Tenant onboarding
10. Migration strategy''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'SaaS Platform'},
                {'name': 'tenant_model', 'type': 'string', 'required': True, 'description': 'Tenant model', 'allowed_values': ['Shared Database', 'Separate Databases', 'Hybrid'], 'example': 'Shared Database'},
                {'name': 'tenant_requirements', 'type': 'long_text', 'required': True, 'description': 'Tenant requirements', 'example': 'Data isolation, Custom branding, Resource limits...'},
                {'name': 'isolation_level', 'type': 'text', 'required': False, 'description': 'Isolation level', 'default': ''}
            ],
            'tags': ['multi-tenant', 'saas', 'architecture'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        },
        {
            'category': category,
            'name': 'Create Domain-Driven Design Model',
            'slug': 'create-ddd-model',
            'description': 'Design domain-driven design model',
            'template': '''Create domain-driven design model.

**Domain:** {{domain}}
**Bounded Contexts:**
{{bounded_contexts}}

**Core Domain:**
{{core_domain}}

{{#if strategic_patterns}}
**Strategic Patterns:**
{{strategic_patterns}}
{{/if}}

Create comprehensive DDD model including:
1. Domain analysis
2. Bounded contexts identification
3. Context mapping
4. Aggregate design
5. Entity and value objects
6. Domain services
7. Repository pattern
8. Domain events
9. Ubiquitous language
10. Implementation strategy''',
            'parameters': [
                {'name': 'domain', 'type': 'text', 'required': True, 'description': 'Domain', 'example': 'E-commerce, Banking, Healthcare'},
                {'name': 'bounded_contexts', 'type': 'long_text', 'required': True, 'description': 'Bounded contexts', 'example': 'User Management, Order Processing, Payment...'},
                {'name': 'core_domain', 'type': 'text', 'required': True, 'description': 'Core domain', 'example': 'Order fulfillment, Payment processing'},
                {'name': 'strategic_patterns', 'type': 'text', 'required': False, 'description': 'Strategic patterns', 'default': ''}
            ],
            'tags': ['ddd', 'domain-modeling', 'architecture'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['CODE_GENERATION']
        }
    ]
    
    return commands


def get_legal_compliance_commands(category, legal_agent):
    """Get all Legal & Compliance command templates."""
    commands = [
        {
            'category': category,
            'name': 'Generate Privacy Policy',
            'slug': 'generate-privacy-policy',
            'description': 'Create privacy policy document for application',
            'template': '''Generate privacy policy.

**Application:** {{application_name}}
**Application Type:** {{application_type}}
**Data Collected:**
{{data_collected}}

{{#if jurisdiction}}
**Jurisdiction:** {{jurisdiction}}
{{/if}}

{{#if third_parties}}
**Third Parties:**
{{third_parties}}
{{/if}}

Create comprehensive privacy policy including:
1. Information collection and use
2. Data storage and security
3. User rights (access, deletion, portability)
4. Cookies and tracking
5. Third-party services
6. Children's privacy (if applicable)
7. Changes to policy
8. Contact information''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'HishamOS'},
                {'name': 'application_type', 'type': 'text', 'required': True, 'description': 'Type of application', 'example': 'SaaS Platform'},
                {'name': 'data_collected', 'type': 'long_text', 'required': True, 'description': 'Types of data collected', 'example': 'Email, name, usage data...'},
                {'name': 'jurisdiction', 'type': 'text', 'required': False, 'description': 'Legal jurisdiction', 'default': 'US'},
                {'name': 'third_parties', 'type': 'text', 'required': False, 'description': 'Third-party services used', 'default': ''}
            ],
            'tags': ['privacy', 'legal', 'gdpr', 'compliance'],
            'recommended_agent': legal_agent,
            'required_capabilities': ['LEGAL_REVIEW']
        },
        {
            'category': category,
            'name': 'Generate Terms of Service',
            'slug': 'generate-terms-of-service',
            'description': 'Create terms of service document',
            'template': '''Generate terms of service.

**Service:** {{service_name}}
**Service Type:** {{service_type}}

{{#if key_features}}
**Key Features:**
{{key_features}}
{{/if}}

{{#if restrictions}}
**Restrictions:**
{{restrictions}}
{{/if}}

Create comprehensive terms of service including:
1. Acceptance of terms
2. Description of service
3. User accounts and responsibilities
4. Acceptable use policy
5. Intellectual property rights
6. Payment terms (if applicable)
7. Termination conditions
8. Limitation of liability
9. Dispute resolution
10. Changes to terms''',
            'parameters': [
                {'name': 'service_name', 'type': 'text', 'required': True, 'description': 'Service name', 'example': 'HishamOS'},
                {'name': 'service_type', 'type': 'text', 'required': True, 'description': 'Type of service', 'example': 'SaaS Platform'},
                {'name': 'key_features', 'type': 'text', 'required': False, 'description': 'Key service features', 'default': ''},
                {'name': 'restrictions', 'type': 'text', 'required': False, 'description': 'Service restrictions', 'default': ''}
            ],
            'tags': ['terms', 'legal', 'tos', 'agreement'],
            'recommended_agent': legal_agent,
            'required_capabilities': ['LEGAL_REVIEW']
        },
        {
            'category': category,
            'name': 'Create Data Processing Agreement',
            'slug': 'create-data-processing-agreement',
            'description': 'Generate DPA for GDPR compliance',
            'template': '''Create data processing agreement.

**Data Controller:** {{data_controller}}
**Data Processor:** {{data_processor}}
**Purpose:** {{purpose}}

{{#if data_categories}}
**Data Categories:**
{{data_categories}}
{{/if}}

{{#if security_measures}}
**Security Measures:**
{{security_measures}}
{{/if}}

Create comprehensive DPA including:
1. Definitions and scope
2. Processing details and purposes
3. Data controller and processor obligations
4. Security measures
5. Data subject rights
6. Sub-processors
7. Data breach procedures
8. International transfers
9. Audit rights
10. Termination and data return''',
            'parameters': [
                {'name': 'data_controller', 'type': 'text', 'required': True, 'description': 'Data controller name', 'example': 'Company ABC'},
                {'name': 'data_processor', 'type': 'text', 'required': True, 'description': 'Data processor name', 'example': 'Cloud Provider XYZ'},
                {'name': 'purpose', 'type': 'text', 'required': True, 'description': 'Purpose of data processing', 'example': 'Cloud hosting and storage'},
                {'name': 'data_categories', 'type': 'text', 'required': False, 'description': 'Categories of data', 'default': ''},
                {'name': 'security_measures', 'type': 'text', 'required': False, 'description': 'Security measures in place', 'default': ''}
            ],
            'tags': ['dpa', 'gdpr', 'compliance', 'data-protection'],
            'recommended_agent': legal_agent,
            'required_capabilities': ['LEGAL_REVIEW']
        },
        {
            'category': category,
            'name': 'Generate Cookie Policy',
            'slug': 'generate-cookie-policy',
            'description': 'Create cookie policy for website',
            'template': '''Generate cookie policy.

**Website:** {{website_name}}
**Cookies Used:**
{{cookies_used}}

{{#if third_party_cookies}}
**Third-Party Cookies:**
{{third_party_cookies}}
{{/if}}

Create comprehensive cookie policy including:
1. What are cookies
2. Types of cookies used (essential, analytics, marketing)
3. Purpose of each cookie
4. Cookie duration
5. Third-party cookies
6. How to manage cookies
7. Impact of disabling cookies''',
            'parameters': [
                {'name': 'website_name', 'type': 'text', 'required': True, 'description': 'Website name', 'example': 'hishamos.com'},
                {'name': 'cookies_used', 'type': 'long_text', 'required': True, 'description': 'List of cookies used', 'example': 'session_id, analytics_tracking...'},
                {'name': 'third_party_cookies', 'type': 'text', 'required': False, 'description': 'Third-party cookies', 'default': ''}
            ],
            'tags': ['cookies', 'legal', 'policy', 'gdpr'],
            'recommended_agent': legal_agent,
            'required_capabilities': ['LEGAL_REVIEW']
        },
        {
            'category': category,
            'name': 'Create Software License Agreement',
            'slug': 'create-software-license',
            'description': 'Generate software license agreement',
            'template': '''Create software license agreement.

**Software:** {{software_name}}
**License Type:** {{license_type}}
**Use Case:** {{use_case}}

{{#if restrictions}}
**Restrictions:**
{{restrictions}}
{{/if}}

Create comprehensive license agreement including:
1. Grant of license
2. License scope and limitations
3. Permitted uses
4. Prohibited uses
5. Intellectual property rights
6. Support and maintenance
7. Warranty disclaimers
8. Limitation of liability
9. Termination conditions
10. Governing law''',
            'parameters': [
                {'name': 'software_name', 'type': 'text', 'required': True, 'description': 'Software name', 'example': 'HishamOS'},
                {'name': 'license_type', 'type': 'string', 'required': True, 'description': 'License type', 'allowed_values': ['Commercial', 'Open Source', 'Enterprise'], 'example': 'Commercial'},
                {'name': 'use_case', 'type': 'text', 'required': True, 'description': 'Intended use case', 'example': 'Business operations'},
                {'name': 'restrictions', 'type': 'text', 'required': False, 'description': 'License restrictions', 'default': ''}
            ],
            'tags': ['license', 'legal', 'agreement', 'software'],
            'recommended_agent': legal_agent,
            'required_capabilities': ['LEGAL_REVIEW']
        },
        {
            'category': category,
            'name': 'Generate GDPR Compliance Checklist',
            'slug': 'generate-gdpr-checklist',
            'description': 'Create GDPR compliance checklist for application',
            'template': '''Generate GDPR compliance checklist.

**Application:** {{application_name}}
**Data Processing Activities:**
{{data_processing}}

{{#if user_location}}
**User Location:** {{user_location}}
{{/if}}

{{#if data_categories}}
**Data Categories:**
{{data_categories}}
{{/if}}

Create comprehensive GDPR checklist including:
1. Lawful basis for processing
2. Data minimization
3. Consent management
4. Data subject rights (access, deletion, portability)
5. Privacy by design
6. Data breach procedures
7. Data Protection Impact Assessment (DPIA)
8. Records of processing activities
9. Third-party data processors
10. International transfers''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'HishamOS'},
                {'name': 'data_processing', 'type': 'long_text', 'required': True, 'description': 'Data processing activities', 'example': 'User registration, Analytics, Marketing...'},
                {'name': 'user_location', 'type': 'text', 'required': False, 'description': 'Primary user location', 'default': 'EU'},
                {'name': 'data_categories', 'type': 'text', 'required': False, 'description': 'Data categories', 'default': ''}
            ],
            'tags': ['gdpr', 'compliance', 'checklist'],
            'recommended_agent': legal_agent,
            'required_capabilities': ['LEGAL_REVIEW']
        },
        {
            'category': category,
            'name': 'Create Acceptable Use Policy',
            'slug': 'create-acceptable-use-policy',
            'description': 'Generate acceptable use policy for service',
            'template': '''Create acceptable use policy.

**Service:** {{service_name}}
**Service Type:** {{service_type}}

{{#if prohibited_activities}}
**Prohibited Activities:**
{{prohibited_activities}}
{{/if}}

{{#if restrictions}}
**Restrictions:**
{{restrictions}}
{{/if}}

Create comprehensive AUP including:
1. Purpose and scope
2. Acceptable uses
3. Prohibited uses and activities
4. Content restrictions
5. Security requirements
6. Intellectual property
7. Enforcement and violations
8. Reporting procedures
9. Policy updates''',
            'parameters': [
                {'name': 'service_name', 'type': 'text', 'required': True, 'description': 'Service name', 'example': 'HishamOS'},
                {'name': 'service_type', 'type': 'text', 'required': True, 'description': 'Service type', 'example': 'SaaS Platform'},
                {'name': 'prohibited_activities', 'type': 'text', 'required': False, 'description': 'Prohibited activities', 'default': ''},
                {'name': 'restrictions', 'type': 'text', 'required': False, 'description': 'Service restrictions', 'default': ''}
            ],
            'tags': ['aup', 'policy', 'legal'],
            'recommended_agent': legal_agent,
            'required_capabilities': ['LEGAL_REVIEW']
        },
        {
            'category': category,
            'name': 'Generate Security Policy Document',
            'slug': 'generate-security-policy',
            'description': 'Create comprehensive security policy document',
            'template': '''Generate security policy document.

**Organization:** {{organization_name}}
**Scope:** {{scope}}

{{#if security_requirements}}
**Security Requirements:**
{{security_requirements}}
{{/if}}

Create comprehensive security policy including:
1. Security objectives and principles
2. Access control policies
3. Data classification and handling
4. Network security
5. Incident response procedures
6. Security awareness and training
7. Compliance requirements
8. Audit and monitoring
9. Vendor security requirements
10. Policy enforcement''',
            'parameters': [
                {'name': 'organization_name', 'type': 'text', 'required': True, 'description': 'Organization name', 'example': 'Company ABC'},
                {'name': 'scope', 'type': 'text', 'required': True, 'description': 'Policy scope', 'example': 'All IT systems and data'},
                {'name': 'security_requirements', 'type': 'text', 'required': False, 'description': 'Security requirements', 'default': ''}
            ],
            'tags': ['security-policy', 'compliance', 'policy'],
            'recommended_agent': legal_agent,
            'required_capabilities': ['LEGAL_REVIEW']
        },
        {
            'category': category,
            'name': 'Create Vendor Agreement Template',
            'slug': 'create-vendor-agreement',
            'description': 'Generate vendor service agreement template',
            'template': '''Create vendor agreement template.

**Service Type:** {{service_type}}
**Vendor Type:** {{vendor_type}}

{{#if service_description}}
**Service Description:**
{{service_description}}
{{/if}}

{{#if key_terms}}
**Key Terms:**
{{key_terms}}
{{/if}}

Create comprehensive vendor agreement including:
1. Parties and definitions
2. Service description and scope
3. Service levels and SLAs
4. Payment terms
5. Data protection and security
6. Intellectual property
7. Confidentiality
8. Liability and indemnification
9. Termination conditions
10. Dispute resolution''',
            'parameters': [
                {'name': 'service_type', 'type': 'text', 'required': True, 'description': 'Service type', 'example': 'Cloud Hosting'},
                {'name': 'vendor_type', 'type': 'text', 'required': True, 'description': 'Vendor type', 'example': 'SaaS Provider'},
                {'name': 'service_description', 'type': 'text', 'required': False, 'description': 'Service description', 'default': ''},
                {'name': 'key_terms', 'type': 'text', 'required': False, 'description': 'Key terms', 'default': ''}
            ],
            'tags': ['vendor-agreement', 'contract', 'legal'],
            'recommended_agent': legal_agent,
            'required_capabilities': ['LEGAL_REVIEW']
        },
        {
            'category': category,
            'name': 'Generate Compliance Audit Checklist',
            'slug': 'generate-compliance-audit',
            'description': 'Create compliance audit checklist',
            'template': '''Generate compliance audit checklist.

**Compliance Standard:** {{compliance_standard}}
**Organization:** {{organization_name}}
**Scope:** {{scope}}

{{#if applicable_regulations}}
**Applicable Regulations:**
{{applicable_regulations}}
{{/if}}

Create comprehensive audit checklist including:
1. Governance and oversight
2. Risk management
3. Access controls
4. Data protection measures
5. Incident response
6. Training and awareness
7. Third-party management
8. Monitoring and logging
9. Documentation requirements
10. Remediation tracking''',
            'parameters': [
                {'name': 'compliance_standard', 'type': 'text', 'required': True, 'description': 'Compliance standard', 'example': 'SOC 2, ISO 27001, HIPAA'},
                {'name': 'organization_name', 'type': 'text', 'required': True, 'description': 'Organization name', 'example': 'Company ABC'},
                {'name': 'scope', 'type': 'text', 'required': True, 'description': 'Audit scope', 'example': 'IT systems and processes'},
                {'name': 'applicable_regulations', 'type': 'text', 'required': False, 'description': 'Applicable regulations', 'default': ''}
            ],
            'tags': ['compliance', 'audit', 'checklist'],
            'recommended_agent': legal_agent,
            'required_capabilities': ['LEGAL_REVIEW']
        }
    ]
    
    return commands


def get_business_analysis_commands(category, ba_agent):
    """Get all Business Analysis command templates."""
    commands = [
        {
            'category': category,
            'name': 'Perform Market Analysis',
            'slug': 'perform-market-analysis',
            'description': 'Analyze market opportunities and competition',
            'template': '''Perform market analysis.

**Product/Service:** {{product_name}}
**Target Market:** {{target_market}}

{{#if competitors}}
**Competitors:**
{{competitors}}
{{/if}}

{{#if market_size}}
**Market Size:** {{market_size}}
{{/if}}

Create comprehensive market analysis including:
1. Market size and growth potential
2. Target customer segments
3. Competitive landscape
4. Competitive advantages
5. Market trends and opportunities
6. Barriers to entry
7. Pricing analysis
8. Go-to-market strategy recommendations''',
            'parameters': [
                {'name': 'product_name', 'type': 'text', 'required': True, 'description': 'Product or service name', 'example': 'AI Project Management Platform'},
                {'name': 'target_market', 'type': 'text', 'required': True, 'description': 'Target market description', 'example': 'SMB software development teams'},
                {'name': 'competitors', 'type': 'text', 'required': False, 'description': 'Known competitors', 'default': ''},
                {'name': 'market_size', 'type': 'text', 'required': False, 'description': 'Estimated market size', 'default': ''}
            ],
            'tags': ['market-analysis', 'competition', 'strategy'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Calculate ROI Analysis',
            'slug': 'calculate-roi-analysis',
            'description': 'Calculate return on investment for project or feature',
            'template': '''Calculate ROI analysis.

**Project/Feature:** {{project_name}}
**Investment:** {{investment}}
**Expected Benefits:**
{{expected_benefits}}

{{#if time_horizon}}
**Time Horizon:** {{time_horizon}}
{{/if}}

{{#if costs}}
**Costs:**
{{costs}}
{{/if}}

Create comprehensive ROI analysis including:
1. Investment breakdown (development, infrastructure, maintenance)
2. Expected benefits (revenue, cost savings, efficiency)
3. ROI calculation (simple and discounted)
4. Payback period
5. Risk factors and sensitivity analysis
6. Break-even analysis
7. Alternative scenarios
8. Recommendations''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project or feature name', 'example': 'AI Automation Feature'},
                {'name': 'investment', 'type': 'text', 'required': True, 'description': 'Total investment amount', 'example': '$100,000'},
                {'name': 'expected_benefits', 'type': 'long_text', 'required': True, 'description': 'Expected benefits', 'example': '20% efficiency gain, $50k cost savings...'},
                {'name': 'time_horizon', 'type': 'text', 'required': False, 'description': 'Analysis time horizon', 'default': '3 years'},
                {'name': 'costs', 'type': 'text', 'required': False, 'description': 'Ongoing costs', 'default': ''}
            ],
            'tags': ['roi', 'financial', 'analysis', 'business-case'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Create Business Requirements Document',
            'slug': 'create-business-requirements',
            'description': 'Generate comprehensive BRD',
            'template': '''Create business requirements document.

**Project:** {{project_name}}
**Business Objective:** {{business_objective}}
**Stakeholders:**
{{stakeholders}}

{{#if current_state}}
**Current State:**
{{current_state}}
{{/if}}

{{#if desired_state}}
**Desired State:**
{{desired_state}}
{{/if}}

Create comprehensive BRD including:
1. Executive summary
2. Business objectives and goals
3. Problem statement
4. Current state analysis
5. Proposed solution
6. Business requirements (functional and non-functional)
7. Success criteria and KPIs
8. Stakeholder analysis
9. Assumptions and constraints
10. Risks and mitigation
11. Timeline and milestones''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'Customer Portal'},
                {'name': 'business_objective', 'type': 'text', 'required': True, 'description': 'Business objective', 'example': 'Improve customer self-service'},
                {'name': 'stakeholders', 'type': 'text', 'required': True, 'description': 'Key stakeholders', 'example': 'Product Manager, Engineering Lead, Customer Success'},
                {'name': 'current_state', 'type': 'text', 'required': False, 'description': 'Current state description', 'default': ''},
                {'name': 'desired_state', 'type': 'text', 'required': False, 'description': 'Desired state description', 'default': ''}
            ],
            'tags': ['brd', 'requirements', 'business-analysis'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Generate SWOT Analysis',
            'slug': 'generate-swot-analysis',
            'description': 'Perform SWOT analysis for product or business',
            'template': '''Generate SWOT analysis.

**Subject:** {{subject}}
**Context:** {{context}}

{{#if current_situation}}
**Current Situation:**
{{current_situation}}
{{/if}}

Create comprehensive SWOT analysis including:
1. Strengths (internal positive factors)
2. Weaknesses (internal negative factors)
3. Opportunities (external positive factors)
4. Threats (external negative factors)
5. Strategic recommendations based on SWOT
6. Action items for each quadrant
7. Priority matrix''',
            'parameters': [
                {'name': 'subject', 'type': 'text', 'required': True, 'description': 'Subject of analysis', 'example': 'E-commerce Platform'},
                {'name': 'context', 'type': 'text', 'required': True, 'description': 'Analysis context', 'example': 'Market expansion strategy'},
                {'name': 'current_situation', 'type': 'text', 'required': False, 'description': 'Current situation', 'default': ''}
            ],
            'tags': ['swot', 'analysis', 'strategy', 'planning'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Create Stakeholder Analysis',
            'slug': 'create-stakeholder-analysis',
            'description': 'Analyze project stakeholders and their influence',
            'template': '''Create stakeholder analysis.

**Project:** {{project_name}}
**Stakeholders:**
{{stakeholders}}

{{#if project_goals}}
**Project Goals:**
{{project_goals}}
{{/if}}

Create comprehensive stakeholder analysis including:
1. Stakeholder identification
2. Stakeholder mapping (power vs interest matrix)
3. Influence and interest levels
4. Stakeholder expectations
5. Communication strategy for each stakeholder
6. Engagement plan
7. Risk assessment (stakeholder-related)
8. Mitigation strategies''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'Digital Transformation'},
                {'name': 'stakeholders', 'type': 'long_text', 'required': True, 'description': 'List of stakeholders', 'example': 'CEO, CTO, Product Manager, End Users...'},
                {'name': 'project_goals', 'type': 'text', 'required': False, 'description': 'Project goals', 'default': ''}
            ],
            'tags': ['stakeholders', 'analysis', 'management'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Create Business Process Model',
            'slug': 'create-business-process-model',
            'description': 'Model business processes with workflows',
            'template': '''Create business process model.

**Process:** {{process_name}}
**Process Type:** {{process_type}}
**Stakeholders:**
{{stakeholders}}

**Current Process:**
{{current_process}}

{{#if pain_points}}
**Pain Points:**
{{pain_points}}
{{/if}}

Create comprehensive process model including:
1. Process overview and objectives
2. Process steps and workflow
3. Roles and responsibilities
4. Decision points and branches
5. Inputs and outputs
6. Tools and systems used
7. Performance metrics
8. Improvement opportunities''',
            'parameters': [
                {'name': 'process_name', 'type': 'text', 'required': True, 'description': 'Process name', 'example': 'Customer Onboarding'},
                {'name': 'process_type', 'type': 'text', 'required': True, 'description': 'Process type', 'example': 'Operational'},
                {'name': 'stakeholders', 'type': 'text', 'required': True, 'description': 'Process stakeholders', 'example': 'Sales, Customer Success, Engineering'},
                {'name': 'current_process', 'type': 'long_text', 'required': True, 'description': 'Current process description', 'example': 'Step 1: Lead qualification...'},
                {'name': 'pain_points', 'type': 'text', 'required': False, 'description': 'Current pain points', 'default': ''}
            ],
            'tags': ['process-modeling', 'bpm', 'workflow'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Perform Cost-Benefit Analysis',
            'slug': 'perform-cost-benefit-analysis',
            'description': 'Analyze costs and benefits of project or decision',
            'template': '''Perform cost-benefit analysis.

**Project/Decision:** {{project_name}}
**Analysis Period:** {{analysis_period}}

**Costs:**
{{costs}}

**Benefits:**
{{benefits}}

{{#if assumptions}}
**Assumptions:**
{{assumptions}}
{{/if}}

Create comprehensive CBA including:
1. Cost breakdown (one-time and recurring)
2. Benefit quantification (tangible and intangible)
3. Net present value (NPV) calculation
4. Return on investment (ROI)
5. Payback period
6. Sensitivity analysis
7. Risk factors
8. Recommendations''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project or decision name', 'example': 'AI Automation'},
                {'name': 'analysis_period', 'type': 'text', 'required': True, 'description': 'Analysis period', 'example': '3 years'},
                {'name': 'costs', 'type': 'long_text', 'required': True, 'description': 'Cost breakdown', 'example': 'Development: $50k, Infrastructure: $20k/year...'},
                {'name': 'benefits', 'type': 'long_text', 'required': True, 'description': 'Benefits', 'example': 'Time savings: 20hrs/week, Cost reduction: $30k/year...'},
                {'name': 'assumptions', 'type': 'text', 'required': False, 'description': 'Key assumptions', 'default': ''}
            ],
            'tags': ['cba', 'cost-benefit', 'analysis'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Create Use Case Diagram',
            'slug': 'create-use-case-diagram',
            'description': 'Generate use case diagram and specifications',
            'template': '''Create use case diagram.

**System:** {{system_name}}
**Actors:**
{{actors}}

**Use Cases:**
{{use_cases}}

{{#if system_boundary}}
**System Boundary:** {{system_boundary}}
{{/if}}

Create comprehensive use case model including:
1. Actor identification
2. Use case list with descriptions
3. Use case relationships (include, extend)
4. Use case specifications (preconditions, postconditions, flow)
5. Alternative flows
6. Exception handling
7. Business rules
8. Non-functional requirements''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'E-commerce Platform'},
                {'name': 'actors', 'type': 'text', 'required': True, 'description': 'System actors', 'example': 'Customer, Admin, Seller'},
                {'name': 'use_cases', 'type': 'long_text', 'required': True, 'description': 'Use cases', 'example': 'Browse products, Add to cart, Checkout...'},
                {'name': 'system_boundary', 'type': 'text', 'required': False, 'description': 'System boundary', 'default': ''}
            ],
            'tags': ['use-case', 'uml', 'requirements'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Generate Business Case Document',
            'slug': 'generate-business-case',
            'description': 'Create comprehensive business case document',
            'template': '''Generate business case document.

**Initiative:** {{initiative_name}}
**Business Problem:** {{business_problem}}
**Proposed Solution:** {{proposed_solution}}

**Stakeholders:**
{{stakeholders}}

{{#if alternatives}}
**Alternatives Considered:**
{{alternatives}}
{{/if}}

Create comprehensive business case including:
1. Executive summary
2. Business problem and opportunity
3. Proposed solution
4. Alternatives analysis
5. Financial analysis (costs, benefits, ROI)
6. Risk assessment
7. Implementation plan
8. Success criteria and KPIs
9. Recommendations''',
            'parameters': [
                {'name': 'initiative_name', 'type': 'text', 'required': True, 'description': 'Initiative name', 'example': 'Digital Transformation'},
                {'name': 'business_problem', 'type': 'long_text', 'required': True, 'description': 'Business problem', 'example': 'Manual processes causing delays...'},
                {'name': 'proposed_solution', 'type': 'long_text', 'required': True, 'description': 'Proposed solution', 'example': 'Automate workflows with AI...'},
                {'name': 'stakeholders', 'type': 'text', 'required': True, 'description': 'Key stakeholders', 'example': 'CEO, CTO, Operations'},
                {'name': 'alternatives', 'type': 'text', 'required': False, 'description': 'Alternatives considered', 'default': ''}
            ],
            'tags': ['business-case', 'proposal', 'strategy'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Perform Gap Analysis',
            'slug': 'perform-gap-analysis',
            'description': 'Analyze gaps between current and desired state',
            'template': '''Perform gap analysis.

**Domain:** {{domain}}
**Current State:**
{{current_state}}

**Desired State:**
{{desired_state}}

{{#if constraints}}
**Constraints:**
{{constraints}}
{{/if}}

Create comprehensive gap analysis including:
1. Current state assessment
2. Desired state definition
3. Gap identification (functional, technical, process)
4. Gap prioritization
5. Root cause analysis
6. Solution recommendations
7. Implementation roadmap
8. Resource requirements''',
            'parameters': [
                {'name': 'domain', 'type': 'text', 'required': True, 'description': 'Analysis domain', 'example': 'Customer Service'},
                {'name': 'current_state', 'type': 'long_text', 'required': True, 'description': 'Current state', 'example': 'Manual ticketing, 24hr response time...'},
                {'name': 'desired_state', 'type': 'long_text', 'required': True, 'description': 'Desired state', 'example': 'Automated routing, 2hr response time...'},
                {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Constraints', 'default': ''}
            ],
            'tags': ['gap-analysis', 'assessment', 'improvement'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Perform Business Process Reengineering',
            'slug': 'perform-business-process-reengineering',
            'description': 'Reengineer business processes for optimization',
            'template': '''Perform business process reengineering.

**Process:** {{process_name}}
**Current Process:**
{{current_process}}

**Problems:**
{{problems}}

{{#if goals}}
**Reengineering Goals:**
{{goals}}
{{/if}}

Create comprehensive reengineering plan including:
1. Current state analysis
2. Problem identification
3. Root cause analysis
4. Reengineered process design
5. Technology enablement
6. Change management plan
7. Implementation roadmap
8. Success metrics
9. Risk assessment
10. Benefits realization''',
            'parameters': [
                {'name': 'process_name', 'type': 'text', 'required': True, 'description': 'Process name', 'example': 'Order Fulfillment'},
                {'name': 'current_process', 'type': 'long_text', 'required': True, 'description': 'Current process', 'example': 'Manual order entry, Email confirmation...'},
                {'name': 'problems', 'type': 'long_text', 'required': True, 'description': 'Problems', 'example': 'Slow processing, High error rate, Customer complaints...'},
                {'name': 'goals', 'type': 'text', 'required': False, 'description': 'Reengineering goals', 'default': ''}
            ],
            'tags': ['bpr', 'process-improvement', 'optimization'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Create Value Stream Map',
            'slug': 'create-value-stream-map',
            'description': 'Map value stream for process optimization',
            'template': '''Create value stream map.

**Product/Service:** {{product_service}}
**Value Stream:**
{{value_stream}}

**Stakeholders:**
{{stakeholders}}

{{#if metrics}}
**Current Metrics:**
{{metrics}}
{{/if}}

Create comprehensive value stream map including:
1. Process steps identification
2. Value vs non-value activities
3. Lead time analysis
4. Cycle time measurement
5. Wait times
6. Inventory levels
7. Information flow
8. Waste identification
9. Improvement opportunities
10. Future state design''',
            'parameters': [
                {'name': 'product_service', 'type': 'text', 'required': True, 'description': 'Product or service', 'example': 'Software Development, Customer Onboarding'},
                {'name': 'value_stream', 'type': 'long_text', 'required': True, 'description': 'Value stream', 'example': 'Requirements → Development → Testing → Deployment'},
                {'name': 'stakeholders', 'type': 'text', 'required': True, 'description': 'Stakeholders', 'example': 'Product Manager, Developers, QA, DevOps'},
                {'name': 'metrics', 'type': 'text', 'required': False, 'description': 'Current metrics', 'default': ''}
            ],
            'tags': ['value-stream', 'lean', 'optimization'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Generate Business Model Canvas',
            'slug': 'generate-business-model-canvas',
            'description': 'Create business model canvas',
            'template': '''Generate business model canvas.

**Business/Product:** {{business_name}}
**Industry:** {{industry}}

{{#if current_model}}
**Current Model:**
{{current_model}}
{{/if}}

Create comprehensive business model canvas including:
1. Value Propositions
2. Customer Segments
3. Channels
4. Customer Relationships
5. Revenue Streams
6. Key Resources
7. Key Activities
8. Key Partnerships
9. Cost Structure
10. Competitive advantages''',
            'parameters': [
                {'name': 'business_name', 'type': 'text', 'required': True, 'description': 'Business or product name', 'example': 'AI Project Management Platform'},
                {'name': 'industry', 'type': 'text', 'required': True, 'description': 'Industry', 'example': 'SaaS, E-commerce, FinTech'},
                {'name': 'current_model', 'type': 'text', 'required': False, 'description': 'Current model', 'default': ''}
            ],
            'tags': ['business-model', 'canvas', 'strategy'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Create Requirements Elicitation Plan',
            'slug': 'create-requirements-elicitation-plan',
            'description': 'Plan requirements elicitation activities',
            'template': '''Create requirements elicitation plan.

**Project:** {{project_name}}
**Stakeholders:**
{{stakeholders}}

**Elicitation Techniques:**
{{elicitation_techniques}}

{{#if timeline}}
**Timeline:** {{timeline}}
{{/if}}

Create comprehensive elicitation plan including:
1. Elicitation objectives
2. Stakeholder analysis
3. Elicitation techniques (interviews, workshops, surveys)
4. Schedule and timeline
5. Roles and responsibilities
6. Documentation approach
7. Validation process
8. Risk mitigation
9. Success criteria
10. Follow-up activities''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'Customer Portal'},
                {'name': 'stakeholders', 'type': 'long_text', 'required': True, 'description': 'Stakeholders', 'example': 'Product Manager, End Users, Engineering Lead...'},
                {'name': 'elicitation_techniques', 'type': 'long_text', 'required': True, 'description': 'Elicitation techniques', 'example': 'Interviews, Workshops, Surveys, Observation...'},
                {'name': 'timeline', 'type': 'text', 'required': False, 'description': 'Timeline', 'default': ''}
            ],
            'tags': ['elicitation', 'requirements', 'planning'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Perform Requirements Prioritization',
            'slug': 'perform-requirements-prioritization',
            'description': 'Prioritize requirements using various techniques',
            'template': '''Perform requirements prioritization.

**Project:** {{project_name}}
**Requirements:**
{{requirements}}

**Prioritization Method:** {{prioritization_method}}

{{#if constraints}}
**Constraints:**
{{constraints}}
{{/if}}

Create comprehensive prioritization including:
1. Requirements list
2. Prioritization criteria
3. Scoring/ranking
4. Priority levels (Must-have, Should-have, Nice-to-have)
5. Dependencies analysis
6. Risk-based prioritization
7. Value-based prioritization
8. Effort vs value matrix
9. Release planning
10. Recommendations''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'requirements', 'type': 'long_text', 'required': True, 'description': 'Requirements list', 'example': 'User login, Product search, Shopping cart...'},
                {'name': 'prioritization_method', 'type': 'string', 'required': True, 'description': 'Prioritization method', 'allowed_values': ['MoSCoW', 'Value vs Effort', 'Kano Model', 'Weighted Scoring'], 'example': 'MoSCoW'},
                {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Constraints', 'default': ''}
            ],
            'tags': ['prioritization', 'requirements', 'planning'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Create Data Flow Diagram',
            'slug': 'create-data-flow-diagram',
            'description': 'Generate data flow diagram for system analysis',
            'template': '''Create data flow diagram.

**System:** {{system_name}}
**Processes:**
{{processes}}

**Data Stores:**
{{data_stores}}

**External Entities:**
{{external_entities}}

{{#if data_flows}}
**Data Flows:**
{{data_flows}}
{{/if}}

Create comprehensive DFD including:
1. Context diagram (Level 0)
2. Level 1 decomposition
3. Process specifications
4. Data store definitions
5. External entity descriptions
6. Data flow definitions
7. Data dictionary
8. Process logic descriptions
9. Error handling flows
10. Security considerations''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name', 'example': 'Order Management System'},
                {'name': 'processes', 'type': 'long_text', 'required': True, 'description': 'System processes', 'example': 'Process Order, Validate Payment, Update Inventory...'},
                {'name': 'data_stores', 'type': 'text', 'required': True, 'description': 'Data stores', 'example': 'Orders DB, Customer DB, Inventory DB'},
                {'name': 'external_entities', 'type': 'text', 'required': True, 'description': 'External entities', 'example': 'Customer, Payment Gateway, Warehouse'},
                {'name': 'data_flows', 'type': 'text', 'required': False, 'description': 'Data flows', 'default': ''}
            ],
            'tags': ['data-flow', 'diagram', 'analysis'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Perform Feasibility Study',
            'slug': 'perform-feasibility-study',
            'description': 'Conduct feasibility study for project or initiative',
            'template': '''Perform feasibility study.

**Project/Initiative:** {{project_name}}
**Study Scope:** {{study_scope}}

**Business Requirements:**
{{business_requirements}}

{{#if constraints}}
**Constraints:**
{{constraints}}
{{/if}}

Create comprehensive feasibility study including:
1. Technical feasibility (technology, resources, skills)
2. Economic feasibility (costs, benefits, ROI)
3. Operational feasibility (processes, change management)
4. Schedule feasibility (timeline, resources)
5. Legal and regulatory feasibility
6. Risk assessment
7. Alternative solutions
8. Recommendations
9. Go/No-go decision criteria
10. Implementation considerations''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'AI Automation System'},
                {'name': 'study_scope', 'type': 'text', 'required': True, 'description': 'Study scope', 'example': 'Technical, Economic, Operational'},
                {'name': 'business_requirements', 'type': 'long_text', 'required': True, 'description': 'Business requirements', 'example': 'Automate workflows, Reduce costs by 30%...'},
                {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Constraints', 'default': ''}
            ],
            'tags': ['feasibility', 'study', 'analysis'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Create Business Rules Document',
            'slug': 'create-business-rules-document',
            'description': 'Document business rules and logic',
            'template': '''Create business rules document.

**Domain:** {{domain}}
**Business Rules:**
{{business_rules}}

{{#if rule_categories}}
**Rule Categories:**
{{rule_categories}}
{{/if}}

Create comprehensive business rules document including:
1. Rule identification and numbering
2. Rule categories (validation, calculation, workflow)
3. Rule descriptions and logic
4. Conditions and triggers
5. Actions and outcomes
6. Priority and importance
7. Dependencies between rules
8. Exception handling
9. Rule versioning
10. Implementation notes''',
            'parameters': [
                {'name': 'domain', 'type': 'text', 'required': True, 'description': 'Business domain', 'example': 'E-commerce, Banking, Healthcare'},
                {'name': 'business_rules', 'type': 'long_text', 'required': True, 'description': 'Business rules', 'example': 'Order must have valid payment, Discount applies if order > $100...'},
                {'name': 'rule_categories', 'type': 'text', 'required': False, 'description': 'Rule categories', 'default': ''}
            ],
            'tags': ['business-rules', 'documentation', 'logic'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Generate Requirements Traceability Matrix',
            'slug': 'generate-requirements-traceability-matrix',
            'description': 'Create requirements traceability matrix',
            'template': '''Generate requirements traceability matrix.

**Project:** {{project_name}}
**Requirements:**
{{requirements}}

**Design Components:**
{{design_components}}

{{#if test_cases}}
**Test Cases:**
{{test_cases}}
{{/if}}

Create comprehensive traceability matrix including:
1. Requirements list with IDs
2. Business objectives mapping
3. Design components mapping
4. Test cases mapping
5. Code modules mapping
6. User stories mapping
7. Change request tracking
8. Coverage analysis
9. Gaps identification
10. Compliance verification''',
            'parameters': [
                {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name', 'example': 'E-commerce Platform'},
                {'name': 'requirements', 'type': 'long_text', 'required': True, 'description': 'Requirements list', 'example': 'REQ-001: User login, REQ-002: Product search...'},
                {'name': 'design_components', 'type': 'long_text', 'required': True, 'description': 'Design components', 'example': 'AuthService, ProductService, SearchService...'},
                {'name': 'test_cases', 'type': 'text', 'required': False, 'description': 'Test cases', 'default': ''}
            ],
            'tags': ['traceability', 'requirements', 'matrix'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        },
        {
            'category': category,
            'name': 'Perform Root Cause Analysis',
            'slug': 'perform-root-cause-analysis',
            'description': 'Analyze root causes of problems or issues',
            'template': '''Perform root cause analysis.

**Problem/Issue:** {{problem_description}}
**Impact:** {{impact}}
**When Occurred:** {{when_occurred}}

**Symptoms:**
{{symptoms}}

{{#if initial_hypotheses}}
**Initial Hypotheses:**
{{initial_hypotheses}}
{{/if}}

Create comprehensive RCA including:
1. Problem statement
2. Impact assessment
3. Timeline of events
4. Data collection
5. Cause identification (5 Whys, Fishbone diagram)
6. Root cause validation
7. Contributing factors
8. Solution recommendations
9. Preventive measures
10. Action plan''',
            'parameters': [
                {'name': 'problem_description', 'type': 'long_text', 'required': True, 'description': 'Problem description', 'example': 'System crashes during peak hours'},
                {'name': 'impact', 'type': 'text', 'required': True, 'description': 'Impact', 'example': 'High - Affects 50% of users'},
                {'name': 'when_occurred', 'type': 'text', 'required': True, 'description': 'When occurred', 'example': 'Last 2 weeks, Daily at 2 PM'},
                {'name': 'symptoms', 'type': 'long_text', 'required': True, 'description': 'Symptoms', 'example': 'Slow response, Error messages, Timeouts...'},
                {'name': 'initial_hypotheses', 'type': 'text', 'required': False, 'description': 'Initial hypotheses', 'default': ''}
            ],
            'tags': ['root-cause', 'analysis', 'problem-solving'],
            'recommended_agent': ba_agent,
            'required_capabilities': ['REQUIREMENTS_ANALYSIS']
        }
    ]
    
    return commands


def get_research_analysis_commands(category, research_agent):
    """Get all Research & Analysis command templates."""
    commands = [
        {
            'category': category,
            'name': 'Technology Research Report',
            'slug': 'technology-research-report',
            'description': 'Research and compare technology options',
            'template': '''Create technology research report.

**Research Topic:** {{research_topic}}
**Use Case:** {{use_case}}

{{#if requirements}}
**Requirements:**
{{requirements}}
{{/if}}

{{#if constraints}}
**Constraints:**
{{constraints}}
{{/if}}

Create comprehensive research report including:
1. Research objectives
2. Technology options overview
3. Feature comparison matrix
4. Pros and cons for each option
5. Performance benchmarks (if available)
6. Cost analysis
7. Learning curve and adoption
8. Community and support
9. Recommendations with rationale
10. Implementation considerations''',
            'parameters': [
                {'name': 'research_topic', 'type': 'text', 'required': True, 'description': 'Technology to research', 'example': 'React vs Vue.js'},
                {'name': 'use_case', 'type': 'text', 'required': True, 'description': 'Intended use case', 'example': 'Building admin dashboard'},
                {'name': 'requirements', 'type': 'text', 'required': False, 'description': 'Key requirements', 'default': ''},
                {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Technical constraints', 'default': ''}
            ],
            'tags': ['research', 'technology', 'comparison'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Competitive Analysis',
            'slug': 'competitive-analysis',
            'description': 'Analyze competitors and market positioning',
            'template': '''Perform competitive analysis.

**Product/Service:** {{product_name}}
**Competitors:**
{{competitors}}

{{#if market_segment}}
**Market Segment:** {{market_segment}}
{{/if}}

Create comprehensive competitive analysis including:
1. Competitor overview
2. Feature comparison matrix
3. Pricing analysis
4. Market positioning
5. Strengths and weaknesses
6. Differentiation opportunities
7. Market gaps
8. Strategic recommendations''',
            'parameters': [
                {'name': 'product_name', 'type': 'text', 'required': True, 'description': 'Your product name', 'example': 'HishamOS'},
                {'name': 'competitors', 'type': 'long_text', 'required': True, 'description': 'List of competitors', 'example': 'Jira, Asana, Monday.com...'},
                {'name': 'market_segment', 'type': 'text', 'required': False, 'description': 'Market segment', 'default': ''}
            ],
            'tags': ['competitive', 'analysis', 'market-research'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'User Research Summary',
            'slug': 'user-research-summary',
            'description': 'Summarize user research findings',
            'template': '''Create user research summary.

**Research Objective:** {{research_objective}}
**Research Methods:** {{research_methods}}
**Findings:**
{{findings}}

{{#if user_segments}}
**User Segments:**
{{user_segments}}
{{/if}}

Create comprehensive research summary including:
1. Research objectives and methods
2. Key findings and insights
3. User pain points
4. User needs and goals
5. Behavioral patterns
6. Quotes and anecdotes
7. Recommendations
8. Next steps and follow-up research''',
            'parameters': [
                {'name': 'research_objective', 'type': 'text', 'required': True, 'description': 'Research objective', 'example': 'Understand user onboarding experience'},
                {'name': 'research_methods', 'type': 'text', 'required': True, 'description': 'Research methods used', 'example': 'Interviews, surveys, usability testing'},
                {'name': 'findings', 'type': 'long_text', 'required': True, 'description': 'Research findings', 'example': 'Users struggle with initial setup...'},
                {'name': 'user_segments', 'type': 'text', 'required': False, 'description': 'User segments studied', 'default': ''}
            ],
            'tags': ['user-research', 'ux', 'insights'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Performance Benchmarking',
            'slug': 'performance-benchmarking',
            'description': 'Benchmark system performance against industry standards',
            'template': '''Perform performance benchmarking.

**System/Component:** {{system_name}}
**Metrics to Benchmark:**
{{metrics}}

{{#if current_performance}}
**Current Performance:**
{{current_performance}}
{{/if}}

{{#if industry_standards}}
**Industry Standards:**
{{industry_standards}}
{{/if}}

Create comprehensive benchmarking report including:
1. Benchmarking objectives
2. Metrics definition and methodology
3. Current performance baseline
4. Industry standards and best practices
5. Gap analysis
6. Performance targets
7. Improvement recommendations
8. Monitoring and measurement plan''',
            'parameters': [
                {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System or component name', 'example': 'API Response Time'},
                {'name': 'metrics', 'type': 'text', 'required': True, 'description': 'Metrics to benchmark', 'example': 'Response time, throughput, error rate'},
                {'name': 'current_performance', 'type': 'text', 'required': False, 'description': 'Current performance data', 'default': ''},
                {'name': 'industry_standards', 'type': 'text', 'required': False, 'description': 'Industry standards', 'default': ''}
            ],
            'tags': ['benchmarking', 'performance', 'metrics'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Trend Analysis Report',
            'slug': 'trend-analysis-report',
            'description': 'Analyze industry trends and predictions',
            'template': '''Create trend analysis report.

**Topic:** {{topic}}
**Time Period:** {{time_period}}

{{#if data_sources}}
**Data Sources:**
{{data_sources}}
{{/if}}

Create comprehensive trend analysis including:
1. Historical trends
2. Current state analysis
3. Emerging trends
4. Future predictions
5. Impact analysis
6. Opportunities and threats
7. Strategic recommendations
8. Action items''',
            'parameters': [
                {'name': 'topic', 'type': 'text', 'required': True, 'description': 'Analysis topic', 'example': 'AI in Software Development'},
                {'name': 'time_period', 'type': 'text', 'required': True, 'description': 'Time period for analysis', 'example': '2020-2024'},
                {'name': 'data_sources', 'type': 'text', 'required': False, 'description': 'Data sources used', 'default': ''}
            ],
            'tags': ['trends', 'analysis', 'forecasting'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Generate Technology Stack Recommendation',
            'slug': 'generate-tech-stack-recommendation',
            'description': 'Recommend technology stack based on requirements',
            'template': '''Generate technology stack recommendation.

**Project Type:** {{project_type}}
**Requirements:**
{{requirements}}

**Team Expertise:**
{{team_expertise}}

{{#if constraints}}
**Constraints:**
{{constraints}}
{{/if}}

Create comprehensive tech stack recommendation including:
1. Frontend framework/library
2. Backend framework/runtime
3. Database selection
4. Caching solution
5. Message queue
6. Cloud provider
7. CI/CD tools
8. Monitoring and logging
9. Justification for each choice
10. Migration path if applicable''',
            'parameters': [
                {'name': 'project_type', 'type': 'text', 'required': True, 'description': 'Project type', 'example': 'Web Application, Mobile App, API Service'},
                {'name': 'requirements', 'type': 'long_text', 'required': True, 'description': 'Project requirements', 'example': 'High performance, Scalable, Real-time...'},
                {'name': 'team_expertise', 'type': 'text', 'required': True, 'description': 'Team expertise', 'example': 'JavaScript, Python, React'},
                {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Constraints', 'default': ''}
            ],
            'tags': ['tech-stack', 'recommendation', 'architecture'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Perform Security Research',
            'slug': 'perform-security-research',
            'description': 'Research security best practices and vulnerabilities',
            'template': '''Perform security research.

**Topic:** {{research_topic}}
**Context:** {{context}}

{{#if specific_concerns}}
**Specific Concerns:**
{{specific_concerns}}
{{/if}}

Create comprehensive security research including:
1. Threat landscape analysis
2. Common vulnerabilities
3. Security best practices
4. Compliance requirements
5. Security tools and frameworks
6. Risk assessment
7. Mitigation strategies
8. References and resources''',
            'parameters': [
                {'name': 'research_topic', 'type': 'text', 'required': True, 'description': 'Research topic', 'example': 'API Security, Authentication, Data Encryption'},
                {'name': 'context', 'type': 'text', 'required': True, 'description': 'Research context', 'example': 'RESTful API for financial services'},
                {'name': 'specific_concerns', 'type': 'text', 'required': False, 'description': 'Specific security concerns', 'default': ''}
            ],
            'tags': ['security', 'research', 'best-practices'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Create Data Analysis Report',
            'slug': 'create-data-analysis-report',
            'description': 'Analyze data and generate insights report',
            'template': '''Create data analysis report.

**Dataset:** {{dataset_description}}
**Analysis Objective:** {{analysis_objective}}

**Data Points:**
{{data_points}}

{{#if questions}}
**Key Questions:**
{{questions}}
{{/if}}

Create comprehensive analysis report including:
1. Executive summary
2. Data overview and quality
3. Key findings and insights
4. Statistical analysis
5. Trends and patterns
6. Anomalies and outliers
7. Visualizations recommendations
8. Conclusions and recommendations''',
            'parameters': [
                {'name': 'dataset_description', 'type': 'text', 'required': True, 'description': 'Dataset description', 'example': 'User behavior data, Sales data, Performance metrics'},
                {'name': 'analysis_objective', 'type': 'text', 'required': True, 'description': 'Analysis objective', 'example': 'Identify user engagement patterns'},
                {'name': 'data_points', 'type': 'long_text', 'required': True, 'description': 'Key data points', 'example': 'User sessions, Page views, Conversion rates...'},
                {'name': 'questions', 'type': 'text', 'required': False, 'description': 'Key questions to answer', 'default': ''}
            ],
            'tags': ['data-analysis', 'insights', 'reporting'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Generate Industry Best Practices',
            'slug': 'generate-industry-best-practices',
            'description': 'Research and document industry best practices',
            'template': '''Generate industry best practices.

**Industry/Domain:** {{industry}}
**Topic:** {{topic}}

{{#if specific_area}}
**Specific Area:**
{{specific_area}}
{{/if}}

Create comprehensive best practices guide including:
1. Industry standards and frameworks
2. Proven methodologies
3. Common patterns and anti-patterns
4. Tools and technologies
5. Case studies and examples
6. Implementation guidelines
7. Pitfalls to avoid
8. Continuous improvement strategies''',
            'parameters': [
                {'name': 'industry', 'type': 'text', 'required': True, 'description': 'Industry or domain', 'example': 'Software Development, E-commerce, FinTech'},
                {'name': 'topic', 'type': 'text', 'required': True, 'description': 'Topic', 'example': 'API Design, Database Management, Security'},
                {'name': 'specific_area', 'type': 'text', 'required': False, 'description': 'Specific area', 'default': ''}
            ],
            'tags': ['best-practices', 'industry', 'standards'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Create Vendor Evaluation Matrix',
            'slug': 'create-vendor-evaluation-matrix',
            'description': 'Evaluate and compare vendors or solutions',
            'template': '''Create vendor evaluation matrix.

**Evaluation Purpose:** {{purpose}}
**Vendors/Solutions:**
{{vendors}}

**Evaluation Criteria:**
{{criteria}}

{{#if requirements}}
**Requirements:**
{{requirements}}
{{/if}}

Create comprehensive evaluation including:
1. Vendor overviews
2. Feature comparison matrix
3. Pricing analysis
4. Support and SLA comparison
5. Integration capabilities
6. Security and compliance
7. Pros and cons for each
8. Scoring and ranking
9. Recommendations
10. Implementation considerations''',
            'parameters': [
                {'name': 'purpose', 'type': 'text', 'required': True, 'description': 'Evaluation purpose', 'example': 'Choose payment gateway, Select cloud provider'},
                {'name': 'vendors', 'type': 'long_text', 'required': True, 'description': 'Vendors or solutions', 'example': 'Stripe, PayPal, Square...'},
                {'name': 'criteria', 'type': 'long_text', 'required': True, 'description': 'Evaluation criteria', 'example': 'Cost, Features, Support, Security...'},
                {'name': 'requirements', 'type': 'text', 'required': False, 'description': 'Specific requirements', 'default': ''}
            ],
            'tags': ['vendor-evaluation', 'comparison', 'selection'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Create Research Methodology Plan',
            'slug': 'create-research-methodology-plan',
            'description': 'Plan research methodology and approach',
            'template': '''Create research methodology plan.

**Research Topic:** {{research_topic}}
**Research Objectives:**
{{research_objectives}}

**Research Questions:**
{{research_questions}}

{{#if constraints}}
**Constraints:**
{{constraints}}
{{/if}}

Create comprehensive methodology plan including:
1. Research objectives
2. Research questions and hypotheses
3. Research design (qualitative, quantitative, mixed)
4. Data collection methods
5. Sampling strategy
6. Data analysis approach
7. Ethical considerations
8. Timeline and milestones
9. Resource requirements
10. Success criteria''',
            'parameters': [
                {'name': 'research_topic', 'type': 'text', 'required': True, 'description': 'Research topic', 'example': 'User Adoption of AI Tools'},
                {'name': 'research_objectives', 'type': 'long_text', 'required': True, 'description': 'Research objectives', 'example': 'Understand user behavior, Identify barriers...'},
                {'name': 'research_questions', 'type': 'long_text', 'required': True, 'description': 'Research questions', 'example': 'What factors influence adoption? How do users perceive AI?...'},
                {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Constraints', 'default': ''}
            ],
            'tags': ['research-methodology', 'planning', 'analysis'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Generate Literature Review',
            'slug': 'generate-literature-review',
            'description': 'Create comprehensive literature review',
            'template': '''Generate literature review.

**Topic:** {{topic}}
**Research Scope:** {{research_scope}}

**Key Themes:**
{{key_themes}}

{{#if research_questions}}
**Research Questions:**
{{research_questions}}
{{/if}}

Create comprehensive literature review including:
1. Introduction and scope
2. Search strategy and sources
3. Key themes and topics
4. Theoretical frameworks
5. Empirical findings
6. Methodological approaches
7. Gaps in existing research
8. Synthesis and analysis
9. Implications
10. Future research directions''',
            'parameters': [
                {'name': 'topic', 'type': 'text', 'required': True, 'description': 'Review topic', 'example': 'AI in Software Development'},
                {'name': 'research_scope', 'type': 'text', 'required': True, 'description': 'Research scope', 'example': '2019-2024, Academic and industry sources'},
                {'name': 'key_themes', 'type': 'long_text', 'required': True, 'description': 'Key themes', 'example': 'Code generation, Testing automation, Project management...'},
                {'name': 'research_questions', 'type': 'text', 'required': False, 'description': 'Research questions', 'default': ''}
            ],
            'tags': ['literature-review', 'research', 'academic'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Perform Data Analysis Report',
            'slug': 'perform-data-analysis-report',
            'description': 'Analyze data and generate insights report',
            'template': '''Perform data analysis report.

**Dataset:** {{dataset_name}}
**Analysis Objective:** {{analysis_objective}}
**Data Period:** {{data_period}}

**Data Overview:**
{{data_overview}}

{{#if key_metrics}}
**Key Metrics:**
{{key_metrics}}
{{/if}}

Create comprehensive analysis report including:
1. Executive summary
2. Data overview and quality
3. Descriptive statistics
4. Trend analysis
5. Pattern identification
6. Correlation analysis
7. Statistical tests
8. Visualizations and charts
9. Key insights and findings
10. Recommendations
11. Limitations
12. Next steps''',
            'parameters': [
                {'name': 'dataset_name', 'type': 'text', 'required': True, 'description': 'Dataset name', 'example': 'User Engagement Data'},
                {'name': 'analysis_objective', 'type': 'text', 'required': True, 'description': 'Analysis objective', 'example': 'Understand user behavior patterns'},
                {'name': 'data_period', 'type': 'text', 'required': True, 'description': 'Data period', 'example': 'January - March 2024'},
                {'name': 'data_overview', 'type': 'long_text', 'required': True, 'description': 'Data overview', 'example': '10,000 records, 5 variables, Daily frequency...'},
                {'name': 'key_metrics', 'type': 'text', 'required': False, 'description': 'Key metrics', 'default': ''}
            ],
            'tags': ['data-analysis', 'statistics', 'insights'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Create Benchmarking Study',
            'slug': 'create-benchmarking-study',
            'description': 'Conduct benchmarking study against industry standards',
            'template': '''Create benchmarking study.

**Subject:** {{subject}}
**Benchmarking Scope:** {{benchmarking_scope}}
**Comparison Targets:**
{{comparison_targets}}

**Metrics to Benchmark:**
{{metrics}}

{{#if current_performance}}
**Current Performance:**
{{current_performance}}
{{/if}}

Create comprehensive benchmarking study including:
1. Benchmarking objectives
2. Scope and methodology
3. Comparison targets (industry leaders, competitors)
4. Metrics definition
5. Data collection approach
6. Current state assessment
7. Gap analysis
8. Best practices identification
9. Improvement opportunities
10. Action plan
11. Success metrics''',
            'parameters': [
                {'name': 'subject', 'type': 'text', 'required': True, 'description': 'Subject', 'example': 'API Performance, Customer Support, Development Velocity'},
                {'name': 'benchmarking_scope', 'type': 'text', 'required': True, 'description': 'Benchmarking scope', 'example': 'Industry-wide, Competitor analysis'},
                {'name': 'comparison_targets', 'type': 'long_text', 'required': True, 'description': 'Comparison targets', 'example': 'Google, Amazon, Microsoft...'},
                {'name': 'metrics', 'type': 'long_text', 'required': True, 'description': 'Metrics to benchmark', 'example': 'Response time, Throughput, Error rate...'},
                {'name': 'current_performance', 'type': 'text', 'required': False, 'description': 'Current performance', 'default': ''}
            ],
            'tags': ['benchmarking', 'comparison', 'analysis'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        },
        {
            'category': category,
            'name': 'Generate Market Research Report',
            'slug': 'generate-market-research-report',
            'description': 'Create comprehensive market research report',
            'template': '''Generate market research report.

**Market:** {{market_name}}
**Research Objective:** {{research_objective}}
**Target Audience:** {{target_audience}}

**Research Questions:**
{{research_questions}}

{{#if data_sources}}
**Data Sources:**
{{data_sources}}
{{/if}}

Create comprehensive market research including:
1. Executive summary
2. Market overview and size
3. Market segmentation
4. Target customer analysis
5. Competitive landscape
6. Market trends and drivers
7. Opportunities and threats
8. Pricing analysis
9. Distribution channels
10. Recommendations
11. Market entry strategy''',
            'parameters': [
                {'name': 'market_name', 'type': 'text', 'required': True, 'description': 'Market name', 'example': 'AI Project Management Tools'},
                {'name': 'research_objective', 'type': 'text', 'required': True, 'description': 'Research objective', 'example': 'Assess market opportunity'},
                {'name': 'target_audience', 'type': 'text', 'required': True, 'description': 'Target audience', 'example': 'SMB software development teams'},
                {'name': 'research_questions', 'type': 'long_text', 'required': True, 'description': 'Research questions', 'example': 'What is market size? Who are competitors?...'},
                {'name': 'data_sources', 'type': 'text', 'required': False, 'description': 'Data sources', 'default': ''}
            ],
            'tags': ['market-research', 'analysis', 'strategy'],
            'recommended_agent': research_agent,
            'required_capabilities': ['RESEARCH']
        }
    ]
    
    return commands


def get_ux_ui_design_commands(category, coding_agent):
    """Get all UX/UI Design command templates."""
    commands = [
        {
            'category': category,
            'name': 'Create User Journey Map',
            'slug': 'create-user-journey-map',
            'description': 'Map user journey through product or service',
            'template': '''Create user journey map.

**User Persona:** {{user_persona}}
**Scenario:** {{scenario}}
**Journey Stages:**
{{journey_stages}}

{{#if touchpoints}}
**Touchpoints:**
{{touchpoints}}
{{/if}}

Create comprehensive user journey map including:
1. User persona and context
2. Journey stages (awareness, consideration, purchase, use, support)
3. User actions at each stage
4. Touchpoints and channels
5. User emotions and pain points
6. Opportunities for improvement
7. Metrics and KPIs
8. Recommendations''',
            'parameters': [
                {'name': 'user_persona', 'type': 'text', 'required': True, 'description': 'User persona', 'example': 'Small business owner'},
                {'name': 'scenario', 'type': 'text', 'required': True, 'description': 'User scenario', 'example': 'Setting up new account'},
                {'name': 'journey_stages', 'type': 'long_text', 'required': True, 'description': 'Journey stages', 'example': 'Discovery, Sign-up, Onboarding, First use...'},
                {'name': 'touchpoints', 'type': 'text', 'required': False, 'description': 'Touchpoints', 'default': ''}
            ],
            'tags': ['user-journey', 'ux', 'design'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Design Wireframe Mockup',
            'slug': 'design-wireframe-mockup',
            'description': 'Create wireframe design for interface',
            'template': '''Design wireframe mockup.

**Page/Screen:** {{page_name}}
**Purpose:** {{purpose}}
**Key Features:**
{{key_features}}

{{#if user_flow}}
**User Flow:**
{{user_flow}}
{{/if}}

{{#if content_requirements}}
**Content Requirements:**
{{content_requirements}}
{{/if}}

Create comprehensive wireframe including:
1. Layout structure and grid
2. Navigation elements
3. Content areas and hierarchy
4. Interactive elements (buttons, forms, links)
5. Information architecture
6. Responsive breakpoints
7. Accessibility considerations
8. Annotations and notes''',
            'parameters': [
                {'name': 'page_name', 'type': 'text', 'required': True, 'description': 'Page or screen name', 'example': 'User Dashboard'},
                {'name': 'purpose', 'type': 'text', 'required': True, 'description': 'Page purpose', 'example': 'Display user analytics'},
                {'name': 'key_features', 'type': 'long_text', 'required': True, 'description': 'Key features', 'example': 'Stats cards, Charts, Quick actions...'},
                {'name': 'user_flow', 'type': 'text', 'required': False, 'description': 'User flow', 'default': ''},
                {'name': 'content_requirements', 'type': 'text', 'required': False, 'description': 'Content requirements', 'default': ''}
            ],
            'tags': ['wireframe', 'ui', 'design'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Create Design System Guidelines',
            'slug': 'create-design-system',
            'description': 'Generate design system with components and guidelines',
            'template': '''Create design system guidelines.

**Product:** {{product_name}}
**Design Principles:**
{{design_principles}}

**Brand Guidelines:**
{{brand_guidelines}}

{{#if target_platforms}}
**Target Platforms:**
{{target_platforms}}
{{/if}}

Create comprehensive design system including:
1. Design principles and philosophy
2. Color palette and usage
3. Typography system
4. Spacing and layout grid
5. Component library (buttons, forms, cards)
6. Iconography
7. Animation and motion
8. Accessibility standards
9. Usage guidelines
10. Code examples''',
            'parameters': [
                {'name': 'product_name', 'type': 'text', 'required': True, 'description': 'Product name', 'example': 'HishamOS'},
                {'name': 'design_principles', 'type': 'long_text', 'required': True, 'description': 'Design principles', 'example': 'Simplicity, Consistency, Accessibility...'},
                {'name': 'brand_guidelines', 'type': 'text', 'required': True, 'description': 'Brand guidelines', 'example': 'Modern, Professional, Trustworthy'},
                {'name': 'target_platforms', 'type': 'text', 'required': False, 'description': 'Target platforms', 'default': 'Web, Mobile'}
            ],
            'tags': ['design-system', 'ui', 'guidelines'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Perform Usability Heuristic Evaluation',
            'slug': 'perform-usability-evaluation',
            'description': 'Evaluate interface using Nielsen\'s usability heuristics',
            'template': '''Perform usability heuristic evaluation.

**Interface/Product:** {{product_name}}
**Evaluation Scope:** {{evaluation_scope}}

**Interface Screens/Pages:**
{{interface_screens}}

{{#if user_tasks}}
**User Tasks:**
{{user_tasks}}
{{/if}}

Create comprehensive evaluation including:
1. Visibility of system status
2. Match between system and real world
3. User control and freedom
4. Consistency and standards
5. Error prevention
6. Recognition rather than recall
7. Flexibility and efficiency
8. Aesthetic and minimalist design
9. Help users recognize, diagnose, recover from errors
10. Help and documentation
11. Severity ratings for each issue
12. Recommendations for improvement''',
            'parameters': [
                {'name': 'product_name', 'type': 'text', 'required': True, 'description': 'Product name', 'example': 'Admin Dashboard'},
                {'name': 'evaluation_scope', 'type': 'text', 'required': True, 'description': 'Evaluation scope', 'example': 'User management section'},
                {'name': 'interface_screens', 'type': 'long_text', 'required': True, 'description': 'Screens/pages evaluated', 'example': 'User list, User form, User details...'},
                {'name': 'user_tasks', 'type': 'text', 'required': False, 'description': 'User tasks', 'default': ''}
            ],
            'tags': ['usability', 'heuristics', 'evaluation'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Create Accessibility Audit',
            'slug': 'create-accessibility-audit',
            'description': 'Audit interface for WCAG accessibility compliance',
            'template': '''Create accessibility audit.

**Product/Interface:** {{product_name}}
**Audit Scope:** {{audit_scope}}

**Pages/Screens:**
{{pages_screens}}

{{#if target_level}}
**Target WCAG Level:** {{target_level}}
{{/if}}

Create comprehensive accessibility audit including:
1. Perceivable (text alternatives, captions, color contrast)
2. Operable (keyboard navigation, no seizures, navigation)
3. Understandable (readable, predictable, input assistance)
4. Robust (compatible with assistive technologies)
5. Automated testing results
6. Manual testing findings
7. Screen reader compatibility
8. Keyboard navigation
9. Color contrast analysis
10. Remediation recommendations
11. Priority and effort estimates''',
            'parameters': [
                {'name': 'product_name', 'type': 'text', 'required': True, 'description': 'Product name', 'example': 'E-commerce Platform'},
                {'name': 'audit_scope', 'type': 'text', 'required': True, 'description': 'Audit scope', 'example': 'Checkout flow'},
                {'name': 'pages_screens', 'type': 'long_text', 'required': True, 'description': 'Pages/screens audited', 'example': 'Cart, Checkout, Payment...'},
                {'name': 'target_level', 'type': 'string', 'required': False, 'description': 'Target WCAG level', 'allowed_values': ['A', 'AA', 'AAA'], 'default': 'AA'}
            ],
            'tags': ['accessibility', 'wcag', 'a11y'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Create User Flow Diagram',
            'slug': 'create-user-flow-diagram',
            'description': 'Design user flow diagrams for features',
            'template': '''Create user flow diagram.

**Feature:** {{feature_name}}
**User Goal:** {{user_goal}}
**Entry Point:** {{entry_point}}

**User Actions:**
{{user_actions}}

{{#if decision_points}}
**Decision Points:**
{{decision_points}}
{{/if}}

Create comprehensive user flow including:
1. Flow start and end points
2. User actions at each step
3. Decision points and branches
4. Error states and recovery paths
5. Success states
6. Alternative flows
7. System responses
8. Annotations and notes''',
            'parameters': [
                {'name': 'feature_name', 'type': 'text', 'required': True, 'description': 'Feature name', 'example': 'User Registration'},
                {'name': 'user_goal', 'type': 'text', 'required': True, 'description': 'User goal', 'example': 'Create new account'},
                {'name': 'entry_point', 'type': 'text', 'required': True, 'description': 'Entry point', 'example': 'Landing page'},
                {'name': 'user_actions', 'type': 'long_text', 'required': True, 'description': 'User actions', 'example': 'Click sign up, Fill form, Submit...'},
                {'name': 'decision_points', 'type': 'text', 'required': False, 'description': 'Decision points', 'default': ''}
            ],
            'tags': ['user-flow', 'ux', 'diagram'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Design Information Architecture',
            'slug': 'design-information-architecture',
            'description': 'Create information architecture for application',
            'template': '''Design information architecture.

**Application:** {{application_name}}
**Content Types:**
{{content_types}}

**User Needs:**
{{user_needs}}

{{#if navigation_requirements}}
**Navigation Requirements:**
{{navigation_requirements}}
{{/if}}

Create comprehensive IA including:
1. Content inventory and categorization
2. Site map structure
3. Navigation hierarchy
4. Content organization patterns
5. Labeling system
6. Search and filtering strategy
7. User mental models
8. Accessibility considerations''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'Admin Dashboard'},
                {'name': 'content_types', 'type': 'long_text', 'required': True, 'description': 'Content types', 'example': 'Users, Projects, Reports, Settings...'},
                {'name': 'user_needs', 'type': 'long_text', 'required': True, 'description': 'User needs', 'example': 'Quick access to key features, Easy navigation...'},
                {'name': 'navigation_requirements', 'type': 'text', 'required': False, 'description': 'Navigation requirements', 'default': ''}
            ],
            'tags': ['information-architecture', 'ia', 'navigation'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Create Prototype Specifications',
            'slug': 'create-prototype-specifications',
            'description': 'Generate specifications for UI prototypes',
            'template': '''Create prototype specifications.

**Prototype Type:** {{prototype_type}}
**Screens/Pages:**
{{screens}}

**Interactions:**
{{interactions}}

{{#if fidelity_level}}
**Fidelity Level:** {{fidelity_level}}
{{/if}}

Create comprehensive prototype specs including:
1. Screen layouts and components
2. Interactive elements and states
3. Navigation patterns
4. Animation and transitions
5. Responsive breakpoints
6. Interaction flows
7. Content requirements
8. Technical constraints''',
            'parameters': [
                {'name': 'prototype_type', 'type': 'text', 'required': True, 'description': 'Prototype type', 'example': 'High-fidelity, Interactive'},
                {'name': 'screens', 'type': 'long_text', 'required': True, 'description': 'Screens/pages', 'example': 'Login, Dashboard, Profile...'},
                {'name': 'interactions', 'type': 'long_text', 'required': True, 'description': 'Key interactions', 'example': 'Click, Hover, Form submission...'},
                {'name': 'fidelity_level', 'type': 'string', 'required': False, 'description': 'Fidelity level', 'allowed_values': ['Low', 'Medium', 'High'], 'default': 'High'}
            ],
            'tags': ['prototype', 'specifications', 'ui'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Create Responsive Design Guidelines',
            'slug': 'create-responsive-design-guidelines',
            'description': 'Generate responsive design guidelines for multi-device support',
            'template': '''Create responsive design guidelines.

**Application:** {{application_name}}
**Target Devices:**
{{target_devices}}

**Design Principles:**
{{design_principles}}

{{#if breakpoints}}
**Breakpoints:**
{{breakpoints}}
{{/if}}

Create comprehensive responsive guidelines including:
1. Breakpoint strategy (mobile, tablet, desktop)
2. Layout patterns (fluid, adaptive, hybrid)
3. Typography scaling
4. Image and media handling
5. Navigation patterns
6. Touch target sizes
7. Performance considerations
8. Testing approach
9. Implementation examples
10. Best practices''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'E-commerce Platform'},
                {'name': 'target_devices', 'type': 'text', 'required': True, 'description': 'Target devices', 'example': 'Mobile, Tablet, Desktop'},
                {'name': 'design_principles', 'type': 'text', 'required': True, 'description': 'Design principles', 'example': 'Mobile-first, Progressive enhancement'},
                {'name': 'breakpoints', 'type': 'text', 'required': False, 'description': 'Breakpoints', 'default': '320px, 768px, 1024px, 1440px'}
            ],
            'tags': ['responsive', 'mobile', 'design'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Design Error State Patterns',
            'slug': 'design-error-state-patterns',
            'description': 'Create error state design patterns and guidelines',
            'template': '''Design error state patterns.

**Application:** {{application_name}}
**Error Types:**
{{error_types}}

{{#if user_context}}
**User Context:**
{{user_context}}
{{/if}}

Create comprehensive error state patterns including:
1. Error message design principles
2. Error state types (validation, system, network, not found)
3. Visual design (icons, colors, typography)
4. Error message copy guidelines
5. Recovery actions and CTAs
6. Error prevention strategies
7. Accessibility considerations
8. Examples and patterns
9. Implementation guidelines
10. Testing approach''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'Admin Dashboard'},
                {'name': 'error_types', 'type': 'long_text', 'required': True, 'description': 'Error types', 'example': 'Form validation, API errors, Network failures, 404 pages...'},
                {'name': 'user_context', 'type': 'text', 'required': False, 'description': 'User context', 'default': ''}
            ],
            'tags': ['error-states', 'ux', 'patterns'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Create Interaction Design Specifications',
            'slug': 'create-interaction-design-specs',
            'description': 'Generate interaction design specifications',
            'template': '''Create interaction design specifications.

**Feature/Component:** {{feature_name}}
**Interaction Type:** {{interaction_type}}

**User Actions:**
{{user_actions}}

{{#if feedback_requirements}}
**Feedback Requirements:**
{{feedback_requirements}}
{{/if}}

Create comprehensive interaction specs including:
1. Interaction flow and states
2. Trigger conditions
3. User feedback (visual, haptic, audio)
4. Animation and transitions
5. Error handling
6. Loading states
7. Success states
8. Accessibility considerations
9. Implementation details
10. Testing criteria''',
            'parameters': [
                {'name': 'feature_name', 'type': 'text', 'required': True, 'description': 'Feature name', 'example': 'Form Submission'},
                {'name': 'interaction_type', 'type': 'text', 'required': True, 'description': 'Interaction type', 'example': 'Form submission, Button click, Drag and drop'},
                {'name': 'user_actions', 'type': 'long_text', 'required': True, 'description': 'User actions', 'example': 'Click submit, Fill form fields, Confirm action...'},
                {'name': 'feedback_requirements', 'type': 'text', 'required': False, 'description': 'Feedback requirements', 'default': ''}
            ],
            'tags': ['interaction-design', 'ux', 'specifications'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Design Empty State Patterns',
            'slug': 'design-empty-state-patterns',
            'description': 'Create empty state design patterns',
            'template': '''Design empty state patterns.

**Application:** {{application_name}}
**Empty State Scenarios:**
{{empty_scenarios}}

{{#if user_goals}}
**User Goals:**
{{user_goals}}
{{/if}}

Create comprehensive empty state patterns including:
1. Empty state types (first use, no data, no results, error)
2. Visual design (illustrations, icons, messaging)
3. Copywriting guidelines
4. Call-to-action placement
5. Onboarding integration
6. Progressive disclosure
7. Examples and variations
8. Implementation guidelines
9. A/B testing considerations
10. Best practices''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'Task Management App'},
                {'name': 'empty_scenarios', 'type': 'long_text', 'required': True, 'description': 'Empty state scenarios', 'example': 'No tasks, No search results, First login...'},
                {'name': 'user_goals', 'type': 'text', 'required': False, 'description': 'User goals', 'default': ''}
            ],
            'tags': ['empty-states', 'ux', 'patterns'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Create Microinteractions Design Guide',
            'slug': 'create-microinteractions-guide',
            'description': 'Design microinteractions for enhanced UX',
            'template': '''Create microinteractions design guide.

**Application:** {{application_name}}
**Key Interactions:**
{{key_interactions}}

{{#if design_philosophy}}
**Design Philosophy:**
{{design_philosophy}}
{{/if}}

Create comprehensive microinteractions guide including:
1. Microinteraction principles
2. Trigger types (user, system, hybrid)
3. Feedback mechanisms (visual, motion, sound)
4. Animation principles (timing, easing, duration)
5. Common patterns (buttons, forms, notifications)
6. Accessibility considerations
7. Performance guidelines
8. Implementation examples
9. Testing approach
10. Best practices''',
            'parameters': [
                {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name', 'example': 'Social Media App'},
                {'name': 'key_interactions', 'type': 'long_text', 'required': True, 'description': 'Key interactions', 'example': 'Like button, Form validation, Loading states...'},
                {'name': 'design_philosophy', 'type': 'text', 'required': False, 'description': 'Design philosophy', 'default': 'Delightful, Subtle, Purposeful'}
            ],
            'tags': ['microinteractions', 'animation', 'ux'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Create Information Architecture',
            'slug': 'create-information-architecture',
            'description': 'Design information architecture for product or system',
            'template': '''Create information architecture.

**Product/System:** {{product_name}}
**Content Types:**
{{content_types}}

**User Goals:**
{{user_goals}}

{{#if existing_structure}}
**Existing Structure:**
{{existing_structure}}
{{/if}}

Create comprehensive IA including:
1. Content inventory
2. Content categorization
3. Hierarchical structure
4. Navigation design
5. Labeling system
6. Search strategy
7. User flows
8. Wireframe structure
9. Metadata schema
10. Accessibility considerations''',
            'parameters': [
                {'name': 'product_name', 'type': 'text', 'required': True, 'description': 'Product name', 'example': 'Admin Dashboard'},
                {'name': 'content_types', 'type': 'long_text', 'required': True, 'description': 'Content types', 'example': 'Pages, Documents, Settings, Reports...'},
                {'name': 'user_goals', 'type': 'long_text', 'required': True, 'description': 'User goals', 'example': 'Manage users, View analytics, Configure settings...'},
                {'name': 'existing_structure', 'type': 'text', 'required': False, 'description': 'Existing structure', 'default': ''}
            ],
            'tags': ['information-architecture', 'ia', 'structure'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Perform User Testing Plan',
            'slug': 'perform-user-testing-plan',
            'description': 'Create user testing plan and methodology',
            'template': '''Perform user testing plan.

**Product/Feature:** {{product_name}}
**Testing Objective:** {{testing_objective}}
**Target Users:** {{target_users}}

**Test Scenarios:**
{{test_scenarios}}

{{#if success_criteria}}
**Success Criteria:**
{{success_criteria}}
{{/if}}

Create comprehensive testing plan including:
1. Testing objectives
2. Research questions
3. Participant recruitment
4. Test scenarios and tasks
5. Testing methodology (moderated, unmoderated)
6. Metrics and measurements
7. Data collection approach
8. Analysis framework
9. Reporting structure
10. Action items template''',
            'parameters': [
                {'name': 'product_name', 'type': 'text', 'required': True, 'description': 'Product name', 'example': 'Checkout Flow'},
                {'name': 'testing_objective', 'type': 'text', 'required': True, 'description': 'Testing objective', 'example': 'Evaluate checkout usability'},
                {'name': 'target_users', 'type': 'text', 'required': True, 'description': 'Target users', 'example': 'First-time buyers, Returning customers'},
                {'name': 'test_scenarios', 'type': 'long_text', 'required': True, 'description': 'Test scenarios', 'example': 'Complete purchase, Apply discount code, Change shipping...'},
                {'name': 'success_criteria', 'type': 'text', 'required': False, 'description': 'Success criteria', 'default': ''}
            ],
            'tags': ['user-testing', 'usability', 'research'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        },
        {
            'category': category,
            'name': 'Create Responsive Design Guidelines',
            'slug': 'create-responsive-design-guidelines',
            'description': 'Generate responsive design guidelines and breakpoints',
            'template': '''Create responsive design guidelines.

**Product:** {{product_name}}
**Target Devices:**
{{target_devices}}

**Content Types:**
{{content_types}}

{{#if design_constraints}}
**Design Constraints:**
{{design_constraints}}
{{/if}}

Create comprehensive responsive guidelines including:
1. Breakpoint strategy (mobile, tablet, desktop)
2. Grid system and layout rules
3. Typography scaling
4. Image and media handling
5. Navigation patterns
6. Touch target sizes
7. Performance considerations
8. Testing approach
9. Implementation guidelines
10. Best practices''',
            'parameters': [
                {'name': 'product_name', 'type': 'text', 'required': True, 'description': 'Product name', 'example': 'E-commerce Platform'},
                {'name': 'target_devices', 'type': 'text', 'required': True, 'description': 'Target devices', 'example': 'Mobile (320px+), Tablet (768px+), Desktop (1024px+)'},
                {'name': 'content_types', 'type': 'long_text', 'required': True, 'description': 'Content types', 'example': 'Product cards, Forms, Navigation, Charts...'},
                {'name': 'design_constraints', 'type': 'text', 'required': False, 'description': 'Design constraints', 'default': ''}
            ],
            'tags': ['responsive', 'design', 'mobile'],
            'recommended_agent': coding_agent,
            'required_capabilities': ['UX_DESIGN']
        }
    ]
    
    return commands
