"""
Additional command templates - compact definitions.
These will be expanded by the main templates file.
"""

# Requirements Engineering Commands (7 more = 10 total)
REQUIREMENTS_COMMANDS_DATA = [
    {
        'name': 'Generate Use Case Documentation',
        'slug': 'generate-use-case-docs',
        'desc': 'Create detailed use case documentation with actors, preconditions, and flows',
        'params': [('use_case_title', 'text', True), ('actors', 'text', True), ('goal', 'text', True)],
        'tags': ['use-case', 'documentation', 'uml']
    },
    {
        'name': 'Create Feature Prioritization Matrix',
        'slug': 'feature-prioritization-matrix',
        'desc': 'Generate RICE or MoSCoW prioritization for features',
        'params': [('features_list', 'long_text', True), ('method', 'string', True, ['RICE', 'MoSCoW'])],
        'tags': ['prioritization', 'rice', 'moscow']
    },
    {
        'name': 'Requirements Gap Analysis',
        'slug': 'requirements-gap-analysis',
        'desc': 'Identify gaps between current and desired requirements',
        'params': [('current_state', 'long_text', True), ('desired_state', 'long_text', True)],
        'tags': ['gap-analysis', 'requirements']
    },
    {
        'name': 'Generate Product Backlog',
        'slug': 'generate-product-backlog',
        'desc': 'Create prioritized product backlog from requirements',
        'params': [('product_vision', 'text', True), ('requirements', 'long_text', True)],
        'tags': ['backlog', 'agile', 'scrum']
    },
    {
        'name': 'Create Requirements Traceability Matrix',
        'slug': 'requirements-traceability-matrix',
        'desc': 'Generate RTM linking requirements to test cases',
        'params': [('requirements', 'long_text', True)],
        'tags': ['traceability', 'rtm', 'testing']
    },
    {
        'name': 'Epic Breakdown to Stories',
        'slug': 'epic-breakdown-stories',
        'desc': 'Break down epic into smaller user stories',
        'params': [('epic_description', 'long_text', True), ('max_story_points', 'integer', False)],
        'tags': ['epic', 'user-stories', 'agile']
    },
    {
        'name': 'Requirements Review Checklist',
        'slug': 'requirements-review-checklist',
        'desc': 'Generate checklist for requirements review meetings',
        'params': [('project_type', 'string', True)],
        'tags': ['checklist', 'review', 'quality']
    },
]

# Code Generation Commands (14 more = 15 total)
CODE_GEN_COMMANDS_DATA = [
    {
        'name': 'Generate Database Model/ORM',
        'slug': 'generate-database-model',
        'desc': 'Create database model with relationships',
        'params': [('framework', 'string', True), ('model_name', 'string', True), ('fields', 'long_text', True)],
        'tags': ['database', 'orm', 'models']
    },
    {
        'name': 'Create React/Vue Component',
        'slug': 'create-frontend-component',
        'desc': 'Generate React or Vue component with props and state',
        'params': [('framework', 'string', True, ['React', 'Vue']), ('component_name', 'string', True), ('props', 'text', True)],
        'tags': ['frontend', 'react', 'vue', 'components']
    },
    {
        'name': 'Generate Unit Tests',
        'slug': 'generate-unit-tests',
        'desc': 'Create comprehensive unit tests for code',
        'params': [('language', 'string', True), ('code', 'long_text', True), ('test_framework', 'string', False)],
        'tags': ['testing', 'unit-tests', 'tdd']
    },
    {
        'name': 'Create Service/Business Logic Layer',
        'slug': 'create-service-layer', 
        'desc': 'Generate service layer with business logic',
        'params': [('language', 'string', True), ('service_purpose', 'text', True)],
        'tags': ['service-layer', 'business-logic', 'architecture']
    },
    {
        'name': 'Generate Data Transfer Objects (DTOs)',
        'slug': 'generate-dtos',
        'desc': 'Create DTOs for API request/response',
        'params': [('language', 'string', True), ('dto_purpose', 'text', True), ('fields', 'text', True)],
        'tags': ['dto', 'api', 'data-transfer']
    },
    {
        'name': 'Create Middleware/Interceptor',
        'slug': 'create-middleware',
        'desc': 'Generate middleware for request/response processing',
        'params': [('framework', 'string', True), ('middleware_purpose', 'text', True)],
        'tags': ['middleware', 'interceptor', 'request-processing']
    },
    {
        'name': 'Generate GraphQL Schema',
        'slug': 'generate-graphql-schema',
        'desc': 'Create GraphQL schema with types and resolvers',
        'params': [('entity_name', 'string', True), ('fields', 'text', True)],
        'tags': ['graphql', 'schema', 'api']
    },
    {
        'name': 'Create Database Migration',
        'slug': 'create-database-migration',
        'desc': 'Generate database migration script',
        'params': [('framework', 'string', True), ('migration_description', 'text', True)],
        'tags': ['migration', 'database', 'schema']
    },
    {
        'name': 'Generate Authentication/Authorization Code',
        'slug': 'generate-auth-code',
        'desc': 'Create authentication and authorization logic',
        'params': [('framework', 'string', True), ('auth_method', 'string', True, ['JWT', 'OAuth', 'Session'])],
        'tags': ['authentication', 'authorization', 'security']
    },
    {
        'name': 'Create Error Handling Utility',
        'slug': 'create-error-handling',
        'desc': 'Generate error handling and logging utilities',
        'params': [('language', 'string', True)],
        'tags': ['error-handling', 'logging', 'utilities']
    },
    {
        'name': 'Generate CRUD Operations',
        'slug': 'generate-crud-operations',
        'desc': 'Create complete CRUD operations for entity',  
        'params': [('framework', 'string', True), ('entity_name', 'string', True)],
        'tags': ['crud', 'operations', 'database']
    },
    {
        'name': 'Create Validation Schemas',
        'slug': 'create-validation-schemas',
        'desc': 'Generate input validation schemas',
        'params': [('language', 'string', True), ('schema_description', 'text', True)],
        'tags': ['validation', 'schema', 'input-validation']
    },
    {
        'name': 'Generate API Documentation',
        'slug': 'generate-api-docs',
        'desc': 'Create OpenAPI/Swagger documentation for API',
        'params': [('endpoint', 'string', True), ('description', 'text', True)],
        'tags': ['documentation', 'api', 'swagger', 'openapi']
    },
    {
        'name': 'Create Background Job/Task',
        'slug': 'create-background-job',
        'desc': 'Generate background job with queue integration',
        'params': [('framework', 'string', True), ('job_purpose', 'text', True)],
        'tags': ['background-jobs', 'queues', 'async']
    },
]

# Code Review Commands (9 more = 10 total) 
CODE_REVIEW_COMMANDS_DATA = [
    {
        'name': 'Performance Review & Optimization',
        'slug': 'performance-review',
        'desc': 'Analyze code for performance bottlenecks',
        'params': [('language', 'string', True), ('code', 'long_text', True)],
        'tags': ['performance', 'optimization', 'bottlenecks']
    },
    {
        'name': 'Best Practices Check',
        'slug': 'best-practices-check',
        'desc': 'Review code against language/framework best practices',
        'params': [('language', 'string', True), ('framework', 'string', False), ('code', 'long_text', True)],
        'tags': ['best-practices', 'code-quality', 'standards']
    },
    {
        'name': 'Code Smell Detection',
        'slug': 'code-smell-detection',
        'desc': 'Identify code smells and suggest refactoring',
        'params': [('language', 'string', True), ('code', 'long_text', True)],
        'tags': ['code-smells', 'refactoring', 'quality']
    },
    {
        'name': 'Dependency Analysis',
        'slug': 'dependency-analysis',
        'desc': 'Analyze dependencies for security and updates',
        'params': [('package_file', 'long_text', True), ('language', 'string', True)],
        'tags': ['dependencies', 'security', 'npm', 'pip']
    },
    {
        'name': 'Test Coverage Analysis',
        'slug': 'test-coverage-analysis',
        'desc': 'Identify untested code paths',
        'params': [('code', 'long_text', True), ('test_file', 'long_text', False)],
        'tags': ['testing', 'coverage', 'quality']
    },
    {
        'name': 'API Design Review',
        'slug': 'api-design-review',
        'desc': 'Review API design for consistency and best practices',
        'params': [('api_spec', 'long_text', True)],
        'tags': ['api', 'design', 'review', 'rest']
    },
    {
        'name': 'Database Query Optimization',
        'slug': 'database-query-optimization',
        'desc': 'Optimize database queries for performance',
        'params': [('database_type', 'string', True), ('query', 'long_text', True)],
        'tags': ['database', 'optimization', 'queries']
    },
    {
        'name': 'Accessibility Audit',
        'slug': 'accessibility-audit',
        'desc': 'Check code for WCAG accessibility compliance',
        'params': [('code', 'long_text', True), ('wcag_level', 'string', False, ['A', 'AA', 'AAA'])],
        'tags': ['accessibility', 'wcag', 'a11y']
    },
    {
        'name': 'Code Documentation Review',
        'slug': 'code-documentation-review',
        'desc': 'Review code documentation completeness',
        'params': [('code', 'long_text', True), ('language', 'string', True)],
        'tags': ['documentation', 'comments', 'quality']
    },
]

# Testing & QA Commands (10 total)
TESTING_COMMANDS_DATA = [
    {
        'name': 'Generate Integration Tests',
        'slug': 'generate-integration-tests',
        'desc': 'Create integration tests for API endpoints or services',
        'params': [('language', 'string', True), ('test_framework', 'string', True), ('endpoints', 'long_text', True)],
        'tags': ['testing', 'integration', 'api']
    },
    {
        'name': 'Create E2E Test Scenarios',
        'slug': 'create-e2e-test-scenarios',
        'desc': 'Generate end-to-end test scenarios for user flows',
        'params': [('user_flow', 'long_text', True), ('test_tool', 'string', False, ['Playwright', 'Cypress', 'Selenium'])],
        'tags': ['testing', 'e2e', 'automation']
    },
    {
        'name': 'Generate Test Data',
        'slug': 'generate-test-data',
        'desc': 'Create realistic test data for testing scenarios',
        'params': [('data_schema', 'long_text', True), ('record_count', 'integer', False)],
        'tags': ['testing', 'test-data', 'fixtures']
    },
    {
        'name': 'Create Performance Test Plan',
        'slug': 'create-performance-test-plan',
        'desc': 'Generate performance testing strategy and test cases',
        'params': [('application_type', 'string', True), ('performance_requirements', 'long_text', True)],
        'tags': ['testing', 'performance', 'load-testing']
    },
    {
        'name': 'Generate Security Test Cases',
        'slug': 'generate-security-test-cases',
        'desc': 'Create security test cases for vulnerability testing',
        'params': [('application_type', 'string', True), ('security_requirements', 'long_text', False)],
        'tags': ['testing', 'security', 'penetration']
    },
    {
        'name': 'Create Test Plan Document',
        'slug': 'create-test-plan-document',
        'desc': 'Generate comprehensive test plan document',
        'params': [('project_scope', 'long_text', True), ('test_objectives', 'text', True)],
        'tags': ['testing', 'test-plan', 'documentation']
    },
    {
        'name': 'Generate Mock Objects',
        'slug': 'generate-mock-objects',
        'desc': 'Create mock objects and stubs for unit testing',
        'params': [('language', 'string', True), ('interface_description', 'long_text', True)],
        'tags': ['testing', 'mocks', 'stubs', 'unit-tests']
    },
    {
        'name': 'Create Test Automation Script',
        'slug': 'create-test-automation-script',
        'desc': 'Generate automated test scripts for regression testing',
        'params': [('test_framework', 'string', True), ('test_scenarios', 'long_text', True)],
        'tags': ['testing', 'automation', 'regression']
    },
    {
        'name': 'Generate Bug Report Template',
        'slug': 'generate-bug-report-template',
        'desc': 'Create standardized bug report template',
        'params': [('bug_severity', 'string', False, ['Critical', 'High', 'Medium', 'Low'])],
        'tags': ['testing', 'bug-report', 'qa']
    },
    {
        'name': 'Create Test Metrics Dashboard',
        'slug': 'create-test-metrics-dashboard',
        'desc': 'Generate test metrics and reporting structure',
        'params': [('metrics_requirements', 'long_text', True)],
        'tags': ['testing', 'metrics', 'reporting', 'dashboard']
    },
]

# DevOps & Deployment Commands (15 total)
DEVOPS_COMMANDS_DATA = [
    {
        'name': 'Generate Dockerfile',
        'slug': 'generate-dockerfile',
        'desc': 'Create optimized Dockerfile for application',
        'params': [('application_type', 'string', True), ('base_image', 'string', False), ('requirements', 'text', False)],
        'tags': ['docker', 'containerization', 'devops']
    },
    {
        'name': 'Create CI/CD Pipeline',
        'slug': 'create-cicd-pipeline',
        'desc': 'Generate CI/CD pipeline configuration',
        'params': [('platform', 'string', True, ['GitHub Actions', 'GitLab CI', 'Jenkins', 'Azure DevOps']), ('stages', 'text', True)],
        'tags': ['cicd', 'pipeline', 'automation']
    },
    {
        'name': 'Generate Kubernetes Deployment',
        'slug': 'generate-kubernetes-deployment',
        'desc': 'Create Kubernetes deployment manifests',
        'params': [('application_name', 'string', True), ('replicas', 'integer', False), ('resources', 'text', False)],
        'tags': ['kubernetes', 'k8s', 'deployment', 'orchestration']
    },
    {
        'name': 'Create Infrastructure as Code',
        'slug': 'create-infrastructure-as-code',
        'desc': 'Generate IaC scripts (Terraform/CloudFormation)',
        'params': [('tool', 'string', True, ['Terraform', 'CloudFormation', 'Pulumi']), ('infrastructure_type', 'text', True)],
        'tags': ['iac', 'terraform', 'infrastructure']
    },
    {
        'name': 'Generate Environment Configuration',
        'slug': 'generate-environment-config',
        'desc': 'Create environment-specific configuration files',
        'params': [('environments', 'text', True), ('config_variables', 'long_text', True)],
        'tags': ['configuration', 'environments', 'devops']
    },
    {
        'name': 'Create Monitoring Setup',
        'slug': 'create-monitoring-setup',
        'desc': 'Generate monitoring and alerting configuration',
        'params': [('monitoring_tool', 'string', True, ['Prometheus', 'Datadog', 'New Relic']), ('metrics', 'text', True)],
        'tags': ['monitoring', 'alerting', 'observability']
    },
    {
        'name': 'Generate Backup Strategy',
        'slug': 'generate-backup-strategy',
        'desc': 'Create backup and disaster recovery plan',
        'params': [('data_type', 'string', True), ('retention_policy', 'text', False)],
        'tags': ['backup', 'disaster-recovery', 'data-protection']
    },
    {
        'name': 'Create Deployment Script',
        'slug': 'create-deployment-script',
        'desc': 'Generate deployment automation scripts',
        'params': [('deployment_type', 'string', True, ['Blue-Green', 'Canary', 'Rolling']), ('target_environment', 'string', True)],
        'tags': ['deployment', 'automation', 'scripts']
    },
    {
        'name': 'Generate Security Hardening Guide',
        'slug': 'generate-security-hardening',
        'desc': 'Create server and application security hardening checklist',
        'params': [('platform', 'string', True), ('security_level', 'string', False, ['Basic', 'Enhanced', 'Hardened'])],
        'tags': ['security', 'hardening', 'devops']
    },
    {
        'name': 'Create Logging Strategy',
        'slug': 'create-logging-strategy',
        'desc': 'Generate logging and log aggregation setup',
        'params': [('logging_tool', 'string', True, ['ELK', 'Loki', 'CloudWatch']), ('log_levels', 'text', False)],
        'tags': ['logging', 'log-aggregation', 'observability']
    },
    {
        'name': 'Generate Auto-scaling Configuration',
        'slug': 'generate-autoscaling-config',
        'desc': 'Create auto-scaling rules and policies',
        'params': [('platform', 'string', True), ('scaling_metrics', 'text', True)],
        'tags': ['autoscaling', 'cloud', 'performance']
    },
    {
        'name': 'Create Database Migration Script',
        'slug': 'create-db-migration-script',
        'desc': 'Generate database migration and rollback scripts',
        'params': [('database_type', 'string', True), ('migration_description', 'text', True)],
        'tags': ['database', 'migration', 'devops']
    },
    {
        'name': 'Generate Health Check Endpoint',
        'slug': 'generate-health-check',
        'desc': 'Create health check and readiness probe endpoints',
        'params': [('framework', 'string', True), ('check_components', 'text', False)],
        'tags': ['health-check', 'monitoring', 'api']
    },
    {
        'name': 'Create Secrets Management Setup',
        'slug': 'create-secrets-management',
        'desc': 'Generate secrets management configuration',
        'params': [('secrets_manager', 'string', True, ['AWS Secrets Manager', 'HashiCorp Vault', 'Azure Key Vault']), ('secret_types', 'text', True)],
        'tags': ['secrets', 'security', 'configuration']
    },
    {
        'name': 'Generate Load Balancer Configuration',
        'slug': 'generate-load-balancer-config',
        'desc': 'Create load balancer configuration and rules',
        'params': [('load_balancer_type', 'string', True, ['Application', 'Network', 'Classic']), ('routing_rules', 'text', True)],
        'tags': ['load-balancer', 'networking', 'high-availability']
    },
]

# Documentation Commands (10 total)
DOCUMENTATION_COMMANDS_DATA = [
    {
        'name': 'Generate API Documentation',
        'slug': 'generate-api-documentation',
        'desc': 'Create comprehensive API documentation from code',
        'params': [('api_spec', 'long_text', True), ('format', 'string', False, ['OpenAPI', 'Markdown', 'HTML'])],
        'tags': ['documentation', 'api', 'openapi']
    },
    {
        'name': 'Create User Guide',
        'slug': 'create-user-guide',
        'desc': 'Generate user-friendly guide for end users',
        'params': [('feature_description', 'long_text', True), ('target_audience', 'string', True)],
        'tags': ['documentation', 'user-guide', 'tutorial']
    },
    {
        'name': 'Generate Technical Specification',
        'slug': 'generate-technical-spec',
        'desc': 'Create detailed technical specification document',
        'params': [('system_description', 'long_text', True), ('requirements', 'long_text', True)],
        'tags': ['documentation', 'technical-spec', 'architecture']
    },
    {
        'name': 'Create README File',
        'slug': 'create-readme',
        'desc': 'Generate comprehensive README for project',
        'params': [('project_description', 'text', True), ('setup_instructions', 'long_text', False)],
        'tags': ['documentation', 'readme', 'project']
    },
    {
        'name': 'Generate Architecture Diagram',
        'slug': 'generate-architecture-diagram',
        'desc': 'Create system architecture diagram description',
        'params': [('system_components', 'long_text', True), ('diagram_type', 'string', False, ['UML', 'C4', 'Flowchart'])],
        'tags': ['documentation', 'architecture', 'diagrams']
    },
    {
        'name': 'Create Changelog',
        'slug': 'create-changelog',
        'desc': 'Generate changelog document from version history',
        'params': [('version_history', 'long_text', True), ('format', 'string', False, ['Keep a Changelog', 'Conventional Commits'])],
        'tags': ['documentation', 'changelog', 'versioning']
    },
    {
        'name': 'Generate Code Comments',
        'slug': 'generate-code-comments',
        'desc': 'Add comprehensive comments to code',
        'params': [('code', 'long_text', True), ('language', 'string', True), ('comment_style', 'string', False)],
        'tags': ['documentation', 'code-comments', 'inline-docs']
    },
    {
        'name': 'Create Troubleshooting Guide',
        'slug': 'create-troubleshooting-guide',
        'desc': 'Generate troubleshooting guide for common issues',
        'params': [('common_issues', 'long_text', True), ('system_type', 'string', True)],
        'tags': ['documentation', 'troubleshooting', 'support']
    },
    {
        'name': 'Generate Installation Guide',
        'slug': 'generate-installation-guide',
        'desc': 'Create step-by-step installation instructions',
        'params': [('platform', 'string', True), ('prerequisites', 'text', True)],
        'tags': ['documentation', 'installation', 'setup']
    },
    {
        'name': 'Create Release Notes',
        'slug': 'create-release-notes',
        'desc': 'Generate release notes for version release',
        'params': [('version', 'string', True), ('changes', 'long_text', True), ('breaking_changes', 'text', False)],
        'tags': ['documentation', 'release-notes', 'versioning']
    },
]