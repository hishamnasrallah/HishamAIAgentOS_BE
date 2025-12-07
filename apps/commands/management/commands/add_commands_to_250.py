"""
Django management command to add commands to reach 250 total.
Adds 21 more commands across various categories.
"""

from django.core.management.base import BaseCommand
from apps.commands.models import CommandCategory, CommandTemplate
from apps.agents.models import Agent


class Command(BaseCommand):
    help = 'Add 21 more commands to reach 250 total command library'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("  ADDING COMMANDS TO REACH 250 TOTAL")
        self.stdout.write("=" * 60)
        self.stdout.write("")
        
        # Get categories
        categories = {cat.slug: cat for cat in CommandCategory.objects.all()}
        
        # Get agents
        agents = {}
        agent_mapping = {
            'business-analyst': 'ba_agent',
            'coding-agent': 'coding_agent',
            'code-reviewer': 'reviewer_agent',
            'qa-testing-agent': 'qa_agent',
            'devops-agent': 'devops_agent',
            'documentation-agent': 'doc_agent',
            'project-manager': 'pm_agent',
            'legal-agent': 'legal_agent',
            'research-agent': 'research_agent'
        }
        
        for agent_id, var_name in agent_mapping.items():
            try:
                agents[var_name] = Agent.objects.get(agent_id=agent_id)
            except Agent.DoesNotExist:
                agents[var_name] = None
        
        # New commands to add (21 total)
        new_commands = [
            # Requirements Engineering (2 more)
            {
                'category_slug': 'requirements-engineering',
                'name': 'Generate Requirements Validation Checklist',
                'slug': 'requirements-validation-checklist',
                'description': 'Create a comprehensive checklist for validating requirements completeness and quality',
                'template': '''Create a requirements validation checklist.

**Project:** {{project_name}}
**Requirements Type:** {{requirements_type}}

**Requirements to Validate:**
{{requirements}}

Generate a validation checklist covering:
1. Completeness (all necessary requirements present)
2. Consistency (no contradictions)
3. Correctness (accurate and feasible)
4. Clarity (unambiguous and understandable)
5. Traceability (linked to business objectives)
6. Testability (can be verified)
7. Prioritization (importance and urgency)
8. Dependencies (relationships between requirements)
9. Risk assessment (potential issues)
10. Stakeholder approval status''',
                'parameters': [
                    {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name'},
                    {'name': 'requirements_type', 'type': 'text', 'required': True, 'description': 'Type of requirements', 'example': 'Functional, Non-functional'},
                    {'name': 'requirements', 'type': 'long_text', 'required': True, 'description': 'Requirements to validate'}
                ],
                'tags': ['validation', 'checklist', 'requirements'],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('requirements-engineering')
            },
            {
                'category_slug': 'requirements-engineering',
                'name': 'Create Requirements Change Management Process',
                'slug': 'requirements-change-management',
                'description': 'Define process for managing requirements changes and impact analysis',
                'template': '''Create requirements change management process.

**Project:** {{project_name}}
**Change Type:** {{change_type}}

**Proposed Change:**
{{proposed_change}}

**Current Requirements:**
{{current_requirements}}

Create a change management process including:
1. Change request submission process
2. Impact analysis framework
3. Stakeholder approval workflow
4. Change prioritization criteria
5. Version control for requirements
6. Communication plan for changes
7. Rollback procedures
8. Documentation requirements
9. Timeline and resource impact
10. Risk assessment''',
                'parameters': [
                    {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name'},
                    {'name': 'change_type', 'type': 'text', 'required': True, 'description': 'Type of change', 'example': 'New feature, Modification, Removal'},
                    {'name': 'proposed_change', 'type': 'long_text', 'required': True, 'description': 'Proposed change description'},
                    {'name': 'current_requirements', 'type': 'long_text', 'required': True, 'description': 'Current requirements affected'}
                ],
                'tags': ['change-management', 'requirements', 'process'],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('requirements-engineering')
            },
            
            # Code Generation (2 more)
            {
                'category_slug': 'code-generation',
                'name': 'Generate GraphQL Schema and Resolvers',
                'slug': 'generate-graphql-schema-resolvers',
                'description': 'Create GraphQL schema definitions and resolver implementations',
                'template': '''Generate GraphQL schema and resolvers.

**API Type:** {{api_type}}
**Data Models:**
{{data_models}}

**Operations Required:**
{{operations}}

{{#if authentication}}
**Authentication:** {{authentication}}
{{/if}}

Create:
1. GraphQL schema (types, queries, mutations, subscriptions)
2. Resolver implementations
3. Input validation
4. Error handling
5. Data loaders (if needed)
6. Authentication/authorization
7. Documentation comments
8. Example queries and mutations''',
                'parameters': [
                    {'name': 'api_type', 'type': 'text', 'required': True, 'description': 'API type', 'example': 'REST to GraphQL, New GraphQL API'},
                    {'name': 'data_models', 'type': 'long_text', 'required': True, 'description': 'Data models and relationships'},
                    {'name': 'operations', 'type': 'text', 'required': True, 'description': 'Required operations', 'example': 'CRUD operations, Search, Filtering'},
                    {'name': 'authentication', 'type': 'text', 'required': False, 'description': 'Authentication method', 'default': ''}
                ],
                'tags': ['graphql', 'api', 'schema'],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            {
                'category_slug': 'code-generation',
                'name': 'Generate Microservices Communication Layer',
                'slug': 'generate-microservices-communication',
                'description': 'Create inter-service communication code (REST, gRPC, message queues)',
                'template': '''Generate microservices communication layer.

**Service Architecture:**
{{service_architecture}}

**Communication Pattern:** {{communication_pattern}}
**Protocol:** {{protocol}}

**Services:**
{{services}}

Create:
1. Service client implementations
2. API contracts/interfaces
3. Request/response models
4. Error handling and retries
5. Circuit breaker pattern (if applicable)
6. Service discovery integration
7. Logging and monitoring
8. Testing utilities
9. Documentation''',
                'parameters': [
                    {'name': 'service_architecture', 'type': 'text', 'required': True, 'description': 'Service architecture', 'example': 'Microservices, Service mesh'},
                    {'name': 'communication_pattern', 'type': 'text', 'required': True, 'description': 'Communication pattern', 'example': 'Synchronous, Asynchronous, Event-driven'},
                    {'name': 'protocol', 'type': 'text', 'required': True, 'description': 'Protocol', 'example': 'REST, gRPC, Message Queue'},
                    {'name': 'services', 'type': 'long_text', 'required': True, 'description': 'Services and their endpoints'}
                ],
                'tags': ['microservices', 'communication', 'api'],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            
            # Code Review (2 more)
            {
                'category_slug': 'code-review',
                'name': 'Security Vulnerability Scan',
                'slug': 'security-vulnerability-scan',
                'description': 'Perform security-focused code review to identify vulnerabilities',
                'template': '''Perform security vulnerability scan.

**Code/Repository:** {{code_location}}
**Language:** {{language}}
**Framework:** {{framework}}

**Code to Review:**
{{code}}

{{#if security_requirements}}
**Security Requirements:**
{{security_requirements}}
{{/if}}

Analyze for:
1. Injection vulnerabilities (SQL, XSS, Command)
2. Authentication and authorization flaws
3. Sensitive data exposure
4. XML external entities (XXE)
5. Broken access control
6. Security misconfiguration
7. Cross-site scripting (XSS)
8. Insecure deserialization
9. Using components with known vulnerabilities
10. Insufficient logging and monitoring
11. OWASP Top 10 compliance
12. Secure coding best practices''',
                'parameters': [
                    {'name': 'code_location', 'type': 'text', 'required': True, 'description': 'Code location or repository'},
                    {'name': 'language', 'type': 'text', 'required': True, 'description': 'Programming language'},
                    {'name': 'framework', 'type': 'text', 'required': True, 'description': 'Framework used'},
                    {'name': 'code', 'type': 'long_text', 'required': True, 'description': 'Code to review'},
                    {'name': 'security_requirements', 'type': 'text', 'required': False, 'description': 'Security requirements', 'default': ''}
                ],
                'tags': ['security', 'vulnerability', 'owasp'],
                'recommended_agent': agents.get('reviewer_agent'),
                'category': categories.get('code-review')
            },
            {
                'category_slug': 'code-review',
                'name': 'Performance Optimization Review',
                'slug': 'performance-optimization-review',
                'description': 'Review code for performance bottlenecks and optimization opportunities',
                'template': '''Review code for performance optimization.

**Code/Module:** {{code_location}}
**Performance Context:** {{performance_context}}

**Code to Review:**
{{code}}

{{#if performance_requirements}}
**Performance Requirements:**
{{performance_requirements}}
{{/if}}

Analyze for:
1. Algorithm complexity (time and space)
2. Database query optimization
3. Caching opportunities
4. Memory leaks and resource management
5. I/O operations efficiency
6. Concurrency and parallelism
7. Network request optimization
8. Bundle size and asset optimization
9. Lazy loading opportunities
10. Code splitting
11. Profiling recommendations
12. Performance metrics and benchmarks''',
                'parameters': [
                    {'name': 'code_location', 'type': 'text', 'required': True, 'description': 'Code location or module'},
                    {'name': 'performance_context', 'type': 'text', 'required': True, 'description': 'Performance context', 'example': 'Web application, API, Batch processing'},
                    {'name': 'code', 'type': 'long_text', 'required': True, 'description': 'Code to review'},
                    {'name': 'performance_requirements', 'type': 'text', 'required': False, 'description': 'Performance requirements', 'default': ''}
                ],
                'tags': ['performance', 'optimization', 'review'],
                'recommended_agent': agents.get('reviewer_agent'),
                'category': categories.get('code-review')
            },
            
            # Testing & QA (2 more)
            {
                'category_slug': 'testing-qa',
                'name': 'Generate Load Testing Scripts',
                'slug': 'generate-load-testing-scripts',
                'description': 'Create load testing scripts and scenarios for performance testing',
                'template': '''Generate load testing scripts.

**Application Type:** {{application_type}}
**Test Scenarios:**
{{test_scenarios}}

**Performance Targets:**
{{performance_targets}}

{{#if tools}}
**Testing Tools:** {{tools}}
{{/if}}

Create:
1. Load testing scenarios
2. Test scripts (JMeter, k6, Locust, etc.)
3. User journey definitions
4. Load profiles (ramp-up, steady-state, ramp-down)
5. Performance metrics to monitor
6. Threshold definitions
7. Test data setup
8. Environment configuration
9. Results analysis guidelines
10. Reporting templates''',
                'parameters': [
                    {'name': 'application_type', 'type': 'text', 'required': True, 'description': 'Application type', 'example': 'Web API, Web Application, Mobile API'},
                    {'name': 'test_scenarios', 'type': 'long_text', 'required': True, 'description': 'Test scenarios to cover'},
                    {'name': 'performance_targets', 'type': 'text', 'required': True, 'description': 'Performance targets', 'example': '1000 RPS, <200ms response time'},
                    {'name': 'tools', 'type': 'text', 'required': False, 'description': 'Preferred testing tools', 'default': ''}
                ],
                'tags': ['load-testing', 'performance', 'testing'],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            {
                'category_slug': 'testing-qa',
                'name': 'Create Accessibility Test Suite',
                'slug': 'create-accessibility-test-suite',
                'description': 'Generate accessibility testing scripts and WCAG compliance checks',
                'template': '''Create accessibility test suite.

**Application:** {{application_name}}
**WCAG Level:** {{wcag_level}}

**Features to Test:**
{{features}}

{{#if tools}}
**Testing Tools:** {{tools}}
{{/if}}

Create:
1. WCAG compliance checklist
2. Automated test scripts (axe-core, Pa11y, etc.)
3. Manual testing procedures
4. Keyboard navigation tests
5. Screen reader compatibility tests
6. Color contrast validation
7. ARIA attribute verification
8. Focus management tests
9. Responsive design accessibility
10. Test reporting format''',
                'parameters': [
                    {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name'},
                    {'name': 'wcag_level', 'type': 'text', 'required': True, 'description': 'WCAG compliance level', 'example': 'WCAG 2.1 AA'},
                    {'name': 'features', 'type': 'long_text', 'required': True, 'description': 'Features to test'},
                    {'name': 'tools', 'type': 'text', 'required': False, 'description': 'Preferred testing tools', 'default': ''}
                ],
                'tags': ['accessibility', 'wcag', 'testing'],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            
            # DevOps & Deployment (2 more)
            {
                'category_slug': 'devops-deployment',
                'name': 'Generate Kubernetes Helm Charts',
                'slug': 'generate-kubernetes-helm-charts',
                'description': 'Create Helm charts for Kubernetes application deployment',
                'template': '''Generate Kubernetes Helm charts.

**Application:** {{application_name}}
**Deployment Type:** {{deployment_type}}

**Application Components:**
{{components}}

**Requirements:**
{{requirements}}

{{#if environment}}
**Environment:** {{environment}}
{{/if}}

Create:
1. Chart structure and metadata
2. Values.yaml with configurable parameters
3. Deployment manifests
4. Service definitions
5. Ingress configuration
6. ConfigMaps and Secrets
7. PersistentVolumeClaims
8. HorizontalPodAutoscaler
9. Resource limits and requests
10. Health checks (liveness, readiness)
11. Documentation and usage examples''',
                'parameters': [
                    {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name'},
                    {'name': 'deployment_type', 'type': 'text', 'required': True, 'description': 'Deployment type', 'example': 'Stateless, Stateful, Microservices'},
                    {'name': 'components', 'type': 'long_text', 'required': True, 'description': 'Application components'},
                    {'name': 'requirements', 'type': 'text', 'required': True, 'description': 'Deployment requirements'},
                    {'name': 'environment', 'type': 'text', 'required': False, 'description': 'Target environment', 'default': ''}
                ],
                'tags': ['kubernetes', 'helm', 'deployment'],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Create Infrastructure as Code (Terraform)',
                'slug': 'create-terraform-infrastructure',
                'description': 'Generate Terraform configurations for cloud infrastructure',
                'template': '''Create Terraform infrastructure code.

**Cloud Provider:** {{cloud_provider}}
**Infrastructure Type:** {{infrastructure_type}}

**Requirements:**
{{requirements}}

**Components:**
{{components}}

{{#if existing_resources}}
**Existing Resources:** {{existing_resources}}
{{/if}}

Create:
1. Provider configuration
2. Variable definitions
3. Resource definitions (compute, storage, network)
4. Security groups and IAM roles
5. Load balancers and auto-scaling
6. Database configurations
7. Monitoring and logging setup
8. Output definitions
9. State management configuration
10. Documentation and usage guide''',
                'parameters': [
                    {'name': 'cloud_provider', 'type': 'text', 'required': True, 'description': 'Cloud provider', 'example': 'AWS, Azure, GCP'},
                    {'name': 'infrastructure_type', 'type': 'text', 'required': True, 'description': 'Infrastructure type', 'example': 'Web application, API, Data pipeline'},
                    {'name': 'requirements', 'type': 'long_text', 'required': True, 'description': 'Infrastructure requirements'},
                    {'name': 'components', 'type': 'text', 'required': True, 'description': 'Components needed'},
                    {'name': 'existing_resources', 'type': 'text', 'required': False, 'description': 'Existing resources to reference', 'default': ''}
                ],
                'tags': ['terraform', 'iac', 'infrastructure'],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            
            # Documentation (2 more)
            {
                'category_slug': 'documentation',
                'name': 'Generate API Documentation (OpenAPI/Swagger)',
                'slug': 'generate-openapi-documentation',
                'description': 'Create comprehensive OpenAPI/Swagger documentation from code or specifications',
                'template': '''Generate OpenAPI/Swagger documentation.

**API Name:** {{api_name}}
**API Version:** {{api_version}}

**Endpoints:**
{{endpoints}}

**Authentication:** {{authentication}}

{{#if data_models}}
**Data Models:**
{{data_models}}
{{/if}}

Create:
1. OpenAPI 3.0 specification
2. API information and metadata
3. Server definitions
4. Path definitions with operations
5. Request/response schemas
6. Authentication schemes
7. Error response definitions
8. Examples for each endpoint
9. Tags and organization
10. Interactive documentation setup''',
                'parameters': [
                    {'name': 'api_name', 'type': 'text', 'required': True, 'description': 'API name'},
                    {'name': 'api_version', 'type': 'text', 'required': True, 'description': 'API version', 'example': 'v1.0.0'},
                    {'name': 'endpoints', 'type': 'long_text', 'required': True, 'description': 'API endpoints and methods'},
                    {'name': 'authentication', 'type': 'text', 'required': True, 'description': 'Authentication method', 'example': 'JWT, OAuth2, API Key'},
                    {'name': 'data_models', 'type': 'long_text', 'required': False, 'description': 'Data models', 'default': ''}
                ],
                'tags': ['openapi', 'swagger', 'api-docs'],
                'recommended_agent': agents.get('doc_agent'),
                'category': categories.get('documentation')
            },
            {
                'category_slug': 'documentation',
                'name': 'Create Runbook Documentation',
                'slug': 'create-runbook-documentation',
                'description': 'Generate operational runbooks for common tasks and incident response',
                'template': '''Create runbook documentation.

**System/Service:** {{system_name}}
**Runbook Type:** {{runbook_type}}

**Common Tasks/Incidents:**
{{tasks_incidents}}

{{#if procedures}}
**Existing Procedures:** {{procedures}}
{{/if}}

Create:
1. System overview and architecture
2. Common operational tasks
3. Incident response procedures
4. Troubleshooting guides
5. Step-by-step instructions
6. Rollback procedures
7. Escalation paths
8. Monitoring and alerting
9. Health check procedures
10. Emergency contacts''',
                'parameters': [
                    {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System or service name'},
                    {'name': 'runbook_type', 'type': 'text', 'required': True, 'description': 'Runbook type', 'example': 'Operations, Incident Response, Maintenance'},
                    {'name': 'tasks_incidents', 'type': 'long_text', 'required': True, 'description': 'Common tasks or incidents'},
                    {'name': 'procedures', 'type': 'text', 'required': False, 'description': 'Existing procedures', 'default': ''}
                ],
                'tags': ['runbook', 'operations', 'incident-response'],
                'recommended_agent': agents.get('doc_agent'),
                'category': categories.get('documentation')
            },
            
            # Project Management (2 more)
            {
                'category_slug': 'project-management',
                'name': 'Generate Sprint Retrospective Report',
                'slug': 'generate-sprint-retrospective',
                'description': 'Create comprehensive sprint retrospective analysis and action items',
                'template': '''Generate sprint retrospective report.

**Sprint:** {{sprint_name}}
**Sprint Duration:** {{sprint_duration}}
**Team:** {{team}}

**Sprint Goals:**
{{sprint_goals}}

**Completed Work:**
{{completed_work}}

**Challenges:**
{{challenges}}

Create:
1. Sprint summary and metrics
2. What went well (successes)
3. What didn't go well (challenges)
4. Action items for improvement
5. Team velocity analysis
6. Burndown chart analysis
7. Blockers and resolutions
8. Process improvements
9. Team feedback and suggestions
10. Next sprint preparation''',
                'parameters': [
                    {'name': 'sprint_name', 'type': 'text', 'required': True, 'description': 'Sprint name or number'},
                    {'name': 'sprint_duration', 'type': 'text', 'required': True, 'description': 'Sprint duration', 'example': '2 weeks'},
                    {'name': 'team', 'type': 'text', 'required': True, 'description': 'Team members'},
                    {'name': 'sprint_goals', 'type': 'text', 'required': True, 'description': 'Sprint goals'},
                    {'name': 'completed_work', 'type': 'long_text', 'required': True, 'description': 'Completed work items'},
                    {'name': 'challenges', 'type': 'long_text', 'required': True, 'description': 'Challenges faced'}
                ],
                'tags': ['retrospective', 'sprint', 'agile'],
                'recommended_agent': agents.get('pm_agent'),
                'category': categories.get('project-management')
            },
            {
                'category_slug': 'project-management',
                'name': 'Create Risk Register',
                'slug': 'create-risk-register',
                'description': 'Generate comprehensive risk register with mitigation strategies',
                'template': '''Create risk register.

**Project:** {{project_name}}
**Project Phase:** {{project_phase}}

**Identified Risks:**
{{risks}}

{{#if existing_risks}}
**Existing Risks:** {{existing_risks}}
{{/if}}

Create:
1. Risk identification and description
2. Risk categories (technical, schedule, budget, quality)
3. Probability assessment (Low, Medium, High)
4. Impact assessment (Low, Medium, High)
5. Risk score (Probability × Impact)
6. Risk owner assignment
7. Mitigation strategies
8. Contingency plans
9. Risk monitoring and review schedule
10. Risk status tracking''',
                'parameters': [
                    {'name': 'project_name', 'type': 'text', 'required': True, 'description': 'Project name'},
                    {'name': 'project_phase', 'type': 'text', 'required': True, 'description': 'Project phase', 'example': 'Planning, Development, Testing'},
                    {'name': 'risks', 'type': 'long_text', 'required': True, 'description': 'Identified risks'},
                    {'name': 'existing_risks', 'type': 'text', 'required': False, 'description': 'Existing risks to review', 'default': ''}
                ],
                'tags': ['risk-management', 'project-management', 'planning'],
                'recommended_agent': agents.get('pm_agent'),
                'category': categories.get('project-management')
            },
            
            # Design & Architecture (2 more)
            {
                'category_slug': 'design-architecture',
                'name': 'Design Event-Driven Architecture',
                'slug': 'design-event-driven-architecture',
                'description': 'Create event-driven architecture design with event sourcing and CQRS patterns',
                'template': '''Design event-driven architecture.

**System:** {{system_name}}
**Domain:** {{domain}}

**Business Events:**
{{business_events}}

**Requirements:**
{{requirements}}

{{#if existing_systems}}
**Existing Systems:** {{existing_systems}}
{{/if}}

Create:
1. Event-driven architecture overview
2. Event types and schemas
3. Event producers and consumers
4. Event bus/message broker design
5. Event sourcing strategy
6. CQRS implementation (if applicable)
7. Event flow diagrams
8. Scalability and performance considerations
9. Error handling and dead letter queues
10. Monitoring and observability
11. Implementation roadmap''',
                'parameters': [
                    {'name': 'system_name', 'type': 'text', 'required': True, 'description': 'System name'},
                    {'name': 'domain', 'type': 'text', 'required': True, 'description': 'Business domain'},
                    {'name': 'business_events', 'type': 'long_text', 'required': True, 'description': 'Business events to handle'},
                    {'name': 'requirements', 'type': 'long_text', 'required': True, 'description': 'System requirements'},
                    {'name': 'existing_systems', 'type': 'text', 'required': False, 'description': 'Existing systems to integrate', 'default': ''}
                ],
                'tags': ['event-driven', 'architecture', 'event-sourcing'],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('design-architecture')
            },
            {
                'category_slug': 'design-architecture',
                'name': 'Create Database Schema Design',
                'slug': 'create-database-schema-design',
                'description': 'Design normalized database schema with relationships and constraints',
                'template': '''Create database schema design.

**Application:** {{application_name}}
**Database Type:** {{database_type}}

**Data Entities:**
{{data_entities}}

**Business Rules:**
{{business_rules}}

{{#if performance_requirements}}
**Performance Requirements:** {{performance_requirements}}
{{/if}}

Create:
1. Entity-relationship diagram (ERD)
2. Table definitions with columns
3. Primary keys and foreign keys
4. Indexes for performance
5. Constraints (unique, check, not null)
6. Relationships (one-to-one, one-to-many, many-to-many)
7. Normalization (1NF, 2NF, 3NF)
8. Data types and sizes
9. Migration strategy
10. Documentation''',
                'parameters': [
                    {'name': 'application_name', 'type': 'text', 'required': True, 'description': 'Application name'},
                    {'name': 'database_type', 'type': 'text', 'required': True, 'description': 'Database type', 'example': 'PostgreSQL, MySQL, MongoDB'},
                    {'name': 'data_entities', 'type': 'long_text', 'required': True, 'description': 'Data entities and attributes'},
                    {'name': 'business_rules', 'type': 'long_text', 'required': True, 'description': 'Business rules and constraints'},
                    {'name': 'performance_requirements', 'type': 'text', 'required': False, 'description': 'Performance requirements', 'default': ''}
                ],
                'tags': ['database', 'schema', 'erd'],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('design-architecture')
            },
            
            # Legal & Compliance (1 more)
            {
                'category_slug': 'legal-compliance',
                'name': 'Generate GDPR Compliance Checklist',
                'slug': 'generate-gdpr-compliance-checklist',
                'description': 'Create GDPR compliance checklist and data protection impact assessment',
                'template': '''Generate GDPR compliance checklist.

**Organization:** {{organization_name}}
**Data Processing Activities:**
{{data_processing}}

**Personal Data Types:**
{{personal_data_types}}

{{#if existing_policies}}
**Existing Policies:** {{existing_policies}}
{{/if}}

Create:
1. GDPR compliance checklist
2. Data processing inventory
3. Legal basis for processing
4. Data subject rights procedures
5. Privacy policy requirements
6. Data breach notification procedures
7. Data Protection Impact Assessment (DPIA)
8. Third-party data processor agreements
9. Consent management procedures
10. Data retention and deletion policies
11. Compliance monitoring and audit''',
                'parameters': [
                    {'name': 'organization_name', 'type': 'text', 'required': True, 'description': 'Organization name'},
                    {'name': 'data_processing', 'type': 'long_text', 'required': True, 'description': 'Data processing activities'},
                    {'name': 'personal_data_types', 'type': 'text', 'required': True, 'description': 'Types of personal data processed'},
                    {'name': 'existing_policies', 'type': 'text', 'required': False, 'description': 'Existing privacy policies', 'default': ''}
                ],
                'tags': ['gdpr', 'compliance', 'data-protection'],
                'recommended_agent': agents.get('legal_agent'),
                'category': categories.get('legal-compliance')
            },
            
            # Business Analysis (1 more)
            {
                'category_slug': 'business-analysis',
                'name': 'Create Business Process Model',
                'slug': 'create-business-process-model',
                'description': 'Generate business process models using BPMN notation',
                'template': '''Create business process model.

**Process Name:** {{process_name}}
**Process Type:** {{process_type}}

**Process Steps:**
{{process_steps}}

**Stakeholders:**
{{stakeholders}}

**Business Rules:**
{{business_rules}}

Create:
1. Process overview and objectives
2. BPMN diagram (activities, gateways, events)
3. Process flow description
4. Roles and responsibilities
5. Decision points and business rules
6. Exception handling
7. Performance metrics (KPIs)
8. Process optimization opportunities
9. Implementation requirements
10. Documentation''',
                'parameters': [
                    {'name': 'process_name', 'type': 'text', 'required': True, 'description': 'Process name'},
                    {'name': 'process_type', 'type': 'text', 'required': True, 'description': 'Process type', 'example': 'Operational, Management, Supporting'},
                    {'name': 'process_steps', 'type': 'long_text', 'required': True, 'description': 'Process steps'},
                    {'name': 'stakeholders', 'type': 'text', 'required': True, 'description': 'Stakeholders involved'},
                    {'name': 'business_rules', 'type': 'text', 'required': True, 'description': 'Business rules'}
                ],
                'tags': ['bpmn', 'business-process', 'modeling'],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('business-analysis')
            },
            
            # Research & Analysis (1 more)
            {
                'category_slug': 'research-analysis',
                'name': 'Generate Technology Stack Comparison',
                'slug': 'generate-technology-stack-comparison',
                'description': 'Compare technology stacks and provide recommendations',
                'template': '''Generate technology stack comparison.

**Project Requirements:**
{{project_requirements}}

**Technology Options:**
{{technology_options}}

**Evaluation Criteria:**
{{evaluation_criteria}}

{{#if constraints}}
**Constraints:** {{constraints}}
{{/if}}

Create:
1. Technology stack overview
2. Feature comparison matrix
3. Performance comparison
4. Cost analysis (licensing, hosting, development)
5. Community and ecosystem
6. Learning curve and developer experience
7. Scalability and maintainability
8. Security considerations
9. Migration path (if applicable)
10. Recommendations with rationale''',
                'parameters': [
                    {'name': 'project_requirements', 'type': 'long_text', 'required': True, 'description': 'Project requirements'},
                    {'name': 'technology_options', 'type': 'long_text', 'required': True, 'description': 'Technology options to compare'},
                    {'name': 'evaluation_criteria', 'type': 'text', 'required': True, 'description': 'Evaluation criteria', 'example': 'Performance, Cost, Community, Learning curve'},
                    {'name': 'constraints', 'type': 'text', 'required': False, 'description': 'Constraints', 'default': ''}
                ],
                'tags': ['technology', 'comparison', 'research'],
                'recommended_agent': agents.get('research_agent'),
                'category': categories.get('research-analysis')
            },
            
            # UX/UI Design (1 more)
            {
                'category_slug': 'ux-ui-design',
                'name': 'Create Design System Documentation',
                'slug': 'create-design-system-documentation',
                'description': 'Generate comprehensive design system documentation with components and guidelines',
                'template': '''Create design system documentation.

**Design System Name:** {{design_system_name}}
**Brand Guidelines:**
{{brand_guidelines}}

**Components:**
{{components}}

**Design Tokens:**
{{design_tokens}}

Create:
1. Design system overview and principles
2. Color palette and usage guidelines
3. Typography system
4. Spacing and layout grid
5. Component library documentation
6. Interaction patterns
7. Accessibility guidelines
8. Usage examples and code snippets
9. Implementation guidelines
10. Versioning and maintenance''',
                'parameters': [
                    {'name': 'design_system_name', 'type': 'text', 'required': True, 'description': 'Design system name'},
                    {'name': 'brand_guidelines', 'type': 'text', 'required': True, 'description': 'Brand guidelines'},
                    {'name': 'components', 'type': 'long_text', 'required': True, 'description': 'Components to document'},
                    {'name': 'design_tokens', 'type': 'text', 'required': True, 'description': 'Design tokens (colors, spacing, typography)'}
                ],
                'tags': ['design-system', 'components', 'documentation'],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('ux-ui-design')
            },
            
            # Code Generation (1 more)
            {
                'category_slug': 'code-generation',
                'name': 'Generate REST API Client Library',
                'slug': 'generate-rest-api-client-library',
                'description': 'Create REST API client library with authentication and error handling',
                'template': '''Generate REST API client library.

**API Base URL:** {{api_base_url}}
**API Version:** {{api_version}}
**Authentication:** {{authentication}}

**Endpoints:**
{{endpoints}}

{{#if language}}
**Target Language:** {{language}}
{{/if}}

Create:
1. Client class structure
2. Authentication handling
3. Request/response models
4. Error handling and exceptions
5. Retry logic and timeouts
6. Request/response interceptors
7. Type definitions (if TypeScript)
8. Usage examples
9. Documentation
10. Testing utilities''',
                'parameters': [
                    {'name': 'api_base_url', 'type': 'text', 'required': True, 'description': 'API base URL'},
                    {'name': 'api_version', 'type': 'text', 'required': True, 'description': 'API version', 'example': 'v1'},
                    {'name': 'authentication', 'type': 'text', 'required': True, 'description': 'Authentication method', 'example': 'Bearer Token, API Key, OAuth2'},
                    {'name': 'endpoints', 'type': 'long_text', 'required': True, 'description': 'API endpoints and methods'},
                    {'name': 'language', 'type': 'text', 'required': False, 'description': 'Target language', 'default': 'TypeScript/JavaScript'}
                ],
                'tags': ['api-client', 'rest', 'sdk'],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            
            # Testing & QA (1 more)
            {
                'category_slug': 'testing-qa',
                'name': 'Generate Contract Testing Suite',
                'slug': 'generate-contract-testing-suite',
                'description': 'Create contract testing suite for API contracts (Pact, Spring Cloud Contract)',
                'template': '''Generate contract testing suite.

**API Provider:** {{api_provider}}
**API Consumer:** {{api_consumer}}

**API Contracts:**
{{api_contracts}}

**Testing Framework:** {{testing_framework}}

{{#if existing_contracts}}
**Existing Contracts:** {{existing_contracts}}
{{/if}}

Create:
1. Contract definitions
2. Provider tests
3. Consumer tests
4. Contract verification setup
5. Mock server configuration
6. Contract versioning strategy
7. CI/CD integration
8. Test data setup
9. Documentation
10. Best practices''',
                'parameters': [
                    {'name': 'api_provider', 'type': 'text', 'required': True, 'description': 'API provider service'},
                    {'name': 'api_consumer', 'type': 'text', 'required': True, 'description': 'API consumer service'},
                    {'name': 'api_contracts', 'type': 'long_text', 'required': True, 'description': 'API contracts to test'},
                    {'name': 'testing_framework', 'type': 'text', 'required': True, 'description': 'Testing framework', 'example': 'Pact, Spring Cloud Contract'},
                    {'name': 'existing_contracts', 'type': 'text', 'required': False, 'description': 'Existing contracts', 'default': ''}
                ],
                'tags': ['contract-testing', 'api', 'testing'],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            }
        ]
        
        created = 0
        updated = 0
        errors = 0
        
        for cmd_data in new_commands:
            try:
                category_slug = cmd_data.pop('category_slug')
                category = categories.get(category_slug)
                if not category:
                    self.stdout.write(self.style.ERROR(f"  [!] Category '{category_slug}' not found for {cmd_data.get('name', 'unknown')}"))
                    errors += 1
                    continue
                recommended_agent = cmd_data.pop('recommended_agent', None)
                
                # Prepare parameters as JSON
                if 'parameters' in cmd_data:
                    cmd_data['parameters'] = cmd_data['parameters']
                
                # Create or update command
                command, created_flag = CommandTemplate.objects.update_or_create(
                    slug=cmd_data['slug'],
                    defaults={
                        **cmd_data,
                        'category': category,
                        'recommended_agent': recommended_agent,
                        'is_active': True,
                        'version': '1.0.0',
                        'estimated_cost': 0.0
                    }
                )
                
                if created_flag:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f"  [+] Created: {command.name}"))
                else:
                    updated += 1
                    self.stdout.write(self.style.WARNING(f"  [*] Updated: {command.name}"))
                    
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f"  [!] Error creating {cmd_data.get('name', 'unknown')}: {e}"))
        
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS(f"[COMPLETE]"))
        self.stdout.write(f"   Created: {created}")
        self.stdout.write(f"   Updated: {updated}")
        if errors > 0:
            self.stdout.write(self.style.ERROR(f"   Errors: {errors}"))
        
        # Show total count
        total = CommandTemplate.objects.count()
        self.stdout.write(f"   Total Commands: {total}")
        self.stdout.write("=" * 60)

