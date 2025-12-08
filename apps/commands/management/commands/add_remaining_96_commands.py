"""
Django management command to add remaining 96 commands to reach 325 total.
Distributes commands across all categories to balance the library.
"""
from django.core.management.base import BaseCommand
from apps.commands.models import CommandCategory, CommandTemplate
from apps.agents.models import Agent


class Command(BaseCommand):
    help = 'Add remaining 96 commands to reach 325 total command library'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("  ADDING REMAINING 96 COMMANDS TO REACH 325 TOTAL")
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
            'research-agent': 'research_agent',
            'ux-ui-designer': 'ux_agent',
            'senior-software-engineer': 'senior_agent',
            'design-architect': 'architect_agent'
        }
        
        for agent_id, var_name in agent_mapping.items():
            try:
                agents[var_name] = Agent.objects.get(agent_id=agent_id)
            except Agent.DoesNotExist:
                try:
                    # Try alternative naming
                    agents[var_name] = Agent.objects.filter(agent_id__icontains=agent_id.split('-')[0]).first()
                except:
                    agents[var_name] = None
        
        # 96 new commands distributed across categories
        new_commands = [
            # Requirements Engineering (8 more to balance)
            {
                'category_slug': 'requirements-engineering',
                'name': 'Generate Requirements Impact Analysis',
                'slug': 'requirements-impact-analysis',
                'description': 'Analyze the impact of requirement changes on existing system components',
                'template': '''Analyze requirements impact.

**Project:** {{project_name}}
**Requirement Change:** {{requirement_change}}
**Affected Components:** {{affected_components}}

Analyze:
1. Direct impact on components
2. Indirect dependencies
3. Testing requirements
4. Timeline impact
5. Resource requirements
6. Risk assessment
7. Mitigation strategies''',
                'parameters': [
                    {'name': 'project_name', 'type': 'text', 'required': True},
                    {'name': 'requirement_change', 'type': 'long_text', 'required': True},
                    {'name': 'affected_components', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('requirements-engineering')
            },
            {
                'category_slug': 'requirements-engineering',
                'name': 'Create Requirements Baseline Document',
                'slug': 'requirements-baseline-document',
                'description': 'Create a baseline document capturing approved requirements at a point in time',
                'template': '''Create requirements baseline.

**Project:** {{project_name}}
**Baseline Date:** {{baseline_date}}
**Requirements:** {{requirements}}

Include:
1. Approved requirements list
2. Version information
3. Approval signatures
4. Change control process
5. Baseline comparison''',
                'parameters': [
                    {'name': 'project_name', 'type': 'text', 'required': True},
                    {'name': 'baseline_date', 'type': 'date', 'required': True},
                    {'name': 'requirements', 'type': 'long_text', 'required': True}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('requirements-engineering')
            },
            {
                'category_slug': 'requirements-engineering',
                'name': 'Generate Requirements Quality Metrics',
                'slug': 'requirements-quality-metrics',
                'description': 'Generate metrics to measure requirements quality and completeness',
                'template': '''Generate requirements quality metrics.

**Project:** {{project_name}}
**Requirements Set:** {{requirements_set}}

Metrics to include:
1. Completeness score
2. Clarity index
3. Traceability coverage
4. Testability percentage
5. Stakeholder approval rate
6. Change frequency
7. Quality trends''',
                'parameters': [
                    {'name': 'project_name', 'type': 'text', 'required': True},
                    {'name': 'requirements_set', 'type': 'long_text', 'required': True}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('requirements-engineering')
            },
            {
                'category_slug': 'requirements-engineering',
                'name': 'Create Requirements Communication Plan',
                'slug': 'requirements-communication-plan',
                'description': 'Develop a plan for communicating requirements to stakeholders',
                'template': '''Create requirements communication plan.

**Project:** {{project_name}}
**Stakeholders:** {{stakeholders}}
**Communication Channels:** {{channels}}

Plan should include:
1. Stakeholder mapping
2. Communication frequency
3. Format and channels
4. Feedback mechanisms
5. Escalation procedures''',
                'parameters': [
                    {'name': 'project_name', 'type': 'text', 'required': True},
                    {'name': 'stakeholders', 'type': 'text', 'required': True},
                    {'name': 'channels', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('requirements-engineering')
            },
            {
                'category_slug': 'requirements-engineering',
                'name': 'Generate Requirements Risk Register',
                'slug': 'requirements-risk-register',
                'description': 'Create a risk register for requirements-related risks',
                'template': '''Generate requirements risk register.

**Project:** {{project_name}}
**Requirements:** {{requirements}}

For each risk include:
1. Risk description
2. Likelihood
3. Impact
4. Mitigation strategy
5. Owner
6. Status''',
                'parameters': [
                    {'name': 'project_name', 'type': 'text', 'required': True},
                    {'name': 'requirements', 'type': 'long_text', 'required': True}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('requirements-engineering')
            },
            {
                'category_slug': 'requirements-engineering',
                'name': 'Create Requirements Test Plan',
                'slug': 'requirements-test-plan',
                'description': 'Develop a test plan to verify requirements are met',
                'template': '''Create requirements test plan.

**Project:** {{project_name}}
**Requirements:** {{requirements}}

Plan should include:
1. Test objectives
2. Test scope
3. Test approach
4. Test cases mapping
5. Success criteria
6. Test schedule''',
                'parameters': [
                    {'name': 'project_name', 'type': 'text', 'required': True},
                    {'name': 'requirements', 'type': 'long_text', 'required': True}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('requirements-engineering')
            },
            {
                'category_slug': 'requirements-engineering',
                'name': 'Generate Requirements Sign-off Document',
                'slug': 'requirements-sign-off-document',
                'description': 'Create a sign-off document for stakeholder approval of requirements',
                'template': '''Generate requirements sign-off document.

**Project:** {{project_name}}
**Requirements Version:** {{version}}
**Stakeholders:** {{stakeholders}}

Document should include:
1. Requirements summary
2. Approval sections
3. Sign-off dates
4. Conditions/assumptions
5. Next steps''',
                'parameters': [
                    {'name': 'project_name', 'type': 'text', 'required': True},
                    {'name': 'version', 'type': 'text', 'required': True},
                    {'name': 'stakeholders', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('requirements-engineering')
            },
            {
                'category_slug': 'requirements-engineering',
                'name': 'Create Requirements Glossary',
                'slug': 'requirements-glossary',
                'description': 'Create a glossary of terms and definitions for requirements documentation',
                'template': '''Create requirements glossary.

**Project:** {{project_name}}
**Domain:** {{domain}}

Include:
1. Term definitions
2. Acronyms
3. Domain-specific terms
4. Cross-references
5. Version history''',
                'parameters': [
                    {'name': 'project_name', 'type': 'text', 'required': True},
                    {'name': 'domain', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('requirements-engineering')
            },
            
            # Code Generation (10 more)
            {
                'category_slug': 'code-generation',
                'name': 'Generate GraphQL Resolvers',
                'slug': 'generate-graphql-resolvers',
                'description': 'Generate GraphQL resolvers for queries and mutations',
                'template': '''Generate GraphQL resolvers.

**Schema:** {{schema}}
**Type:** {{type}}
**Operations:** {{operations}}

Generate:
1. Query resolvers
2. Mutation resolvers
3. Field resolvers
4. Error handling
5. Data loaders
6. Authentication checks''',
                'parameters': [
                    {'name': 'schema', 'type': 'text', 'required': True},
                    {'name': 'type', 'type': 'text', 'required': True},
                    {'name': 'operations', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            {
                'category_slug': 'code-generation',
                'name': 'Create Event-Driven Architecture Code',
                'slug': 'create-event-driven-architecture',
                'description': 'Generate code for event-driven architecture patterns',
                'template': '''Create event-driven architecture.

**Events:** {{events}}
**Handlers:** {{handlers}}
**Message Broker:** {{broker}}

Generate:
1. Event definitions
2. Event publishers
3. Event handlers
4. Event consumers
5. Event store
6. Saga orchestrator''',
                'parameters': [
                    {'name': 'events', 'type': 'text', 'required': True},
                    {'name': 'handlers', 'type': 'text', 'required': True},
                    {'name': 'broker', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            {
                'category_slug': 'code-generation',
                'name': 'Generate CQRS Implementation',
                'slug': 'generate-cqrs-implementation',
                'description': 'Generate Command Query Responsibility Segregation pattern implementation',
                'template': '''Generate CQRS implementation.

**Domain:** {{domain}}
**Commands:** {{commands}}
**Queries:** {{queries}}

Generate:
1. Command handlers
2. Query handlers
3. Read models
4. Write models
5. Event handlers
6. Aggregates''',
                'parameters': [
                    {'name': 'domain', 'type': 'text', 'required': True},
                    {'name': 'commands', 'type': 'text', 'required': True},
                    {'name': 'queries', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            {
                'category_slug': 'code-generation',
                'name': 'Create Microservices Communication Layer',
                'slug': 'create-microservices-communication',
                'description': 'Generate code for inter-service communication in microservices',
                'template': '''Create microservices communication.

**Services:** {{services}}
**Communication Type:** {{comm_type}}
**Protocol:** {{protocol}}

Generate:
1. Service clients
2. API gateways
3. Service discovery
4. Circuit breakers
5. Retry logic
6. Load balancing''',
                'parameters': [
                    {'name': 'services', 'type': 'text', 'required': True},
                    {'name': 'comm_type', 'type': 'text', 'required': True},
                    {'name': 'protocol', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            {
                'category_slug': 'code-generation',
                'name': 'Generate Rate Limiting Middleware',
                'slug': 'generate-rate-limiting-middleware',
                'description': 'Create rate limiting middleware for API protection',
                'template': '''Generate rate limiting middleware.

**Framework:** {{framework}}
**Strategy:** {{strategy}}
**Limits:** {{limits}}

Generate:
1. Rate limiter implementation
2. Configuration
3. Error responses
4. Headers
5. Redis integration
6. Testing''',
                'parameters': [
                    {'name': 'framework', 'type': 'text', 'required': True},
                    {'name': 'strategy', 'type': 'text', 'required': True},
                    {'name': 'limits', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            {
                'category_slug': 'code-generation',
                'name': 'Create Distributed Lock Implementation',
                'slug': 'create-distributed-lock',
                'description': 'Generate distributed locking mechanism for concurrent operations',
                'template': '''Create distributed lock.

**Use Case:** {{use_case}}
**Storage:** {{storage}}
**TTL:** {{ttl}}

Generate:
1. Lock interface
2. Redis/Zookeeper implementation
3. Lock acquisition
4. Lock release
5. Deadlock prevention
6. Testing''',
                'parameters': [
                    {'name': 'use_case', 'type': 'text', 'required': True},
                    {'name': 'storage', 'type': 'text', 'required': True},
                    {'name': 'ttl', 'type': 'number', 'required': False}
                ],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            {
                'category_slug': 'code-generation',
                'name': 'Generate WebSocket Server Implementation',
                'slug': 'generate-websocket-server',
                'description': 'Create WebSocket server for real-time communication',
                'template': '''Generate WebSocket server.

**Framework:** {{framework}}
**Use Case:** {{use_case}}
**Features:** {{features}}

Generate:
1. WebSocket handler
2. Connection management
3. Message routing
4. Broadcasting
5. Error handling
6. Authentication''',
                'parameters': [
                    {'name': 'framework', 'type': 'text', 'required': True},
                    {'name': 'use_case', 'type': 'text', 'required': True},
                    {'name': 'features', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            {
                'category_slug': 'code-generation',
                'name': 'Create Feature Flag System',
                'slug': 'create-feature-flag-system',
                'description': 'Generate feature flag/toggle system for gradual rollouts',
                'template': '''Create feature flag system.

**Framework:** {{framework}}
**Storage:** {{storage}}
**Features:** {{features}}

Generate:
1. Feature flag service
2. Configuration management
3. A/B testing support
4. Analytics
5. Admin interface
6. Testing utilities''',
                'parameters': [
                    {'name': 'framework', 'type': 'text', 'required': True},
                    {'name': 'storage', 'type': 'text', 'required': True},
                    {'name': 'features', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            {
                'category_slug': 'code-generation',
                'name': 'Generate Message Queue Consumer',
                'slug': 'generate-message-queue-consumer',
                'description': 'Create message queue consumer for async processing',
                'template': '''Generate message queue consumer.

**Queue System:** {{queue_system}}
**Message Format:** {{message_format}}
**Processing Logic:** {{processing}}

Generate:
1. Consumer setup
2. Message handlers
3. Error handling
4. Retry logic
5. Dead letter queue
6. Monitoring''',
                'parameters': [
                    {'name': 'queue_system', 'type': 'text', 'required': True},
                    {'name': 'message_format', 'type': 'text', 'required': True},
                    {'name': 'processing', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            {
                'category_slug': 'code-generation',
                'name': 'Create API Gateway Configuration',
                'slug': 'create-api-gateway-config',
                'description': 'Generate API gateway configuration and routing rules',
                'template': '''Create API gateway configuration.

**Gateway:** {{gateway}}
**Services:** {{services}}
**Routes:** {{routes}}

Generate:
1. Route definitions
2. Load balancing
3. Rate limiting
4. Authentication
5. Request/response transformation
6. Monitoring''',
                'parameters': [
                    {'name': 'gateway', 'type': 'text', 'required': True},
                    {'name': 'services', 'type': 'text', 'required': True},
                    {'name': 'routes', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('coding_agent'),
                'category': categories.get('code-generation')
            },
            
            # Code Review (8 more)
            {
                'category_slug': 'code-review',
                'name': 'Security Vulnerability Scan',
                'slug': 'security-vulnerability-scan',
                'description': 'Scan code for security vulnerabilities and suggest fixes',
                'template': '''Scan for security vulnerabilities.

**Code:** {{code}}
**Language:** {{language}}
**Framework:** {{framework}}

Check for:
1. SQL injection
2. XSS vulnerabilities
3. CSRF issues
4. Authentication flaws
5. Authorization gaps
6. Sensitive data exposure
7. Insecure dependencies
8. Security best practices''',
                'parameters': [
                    {'name': 'code', 'type': 'long_text', 'required': True},
                    {'name': 'language', 'type': 'text', 'required': True},
                    {'name': 'framework', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('reviewer_agent'),
                'category': categories.get('code-review')
            },
            {
                'category_slug': 'code-review',
                'name': 'Code Complexity Analysis',
                'slug': 'code-complexity-analysis',
                'description': 'Analyze code complexity and suggest refactoring opportunities',
                'template': '''Analyze code complexity.

**Code:** {{code}}
**Metrics:** {{metrics}}

Analyze:
1. Cyclomatic complexity
2. Cognitive complexity
3. Code duplication
4. Function length
5. Nesting depth
6. Refactoring suggestions''',
                'parameters': [
                    {'name': 'code', 'type': 'long_text', 'required': True},
                    {'name': 'metrics', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('reviewer_agent'),
                'category': categories.get('code-review')
            },
            {
                'category_slug': 'code-review',
                'name': 'Memory Leak Detection',
                'slug': 'memory-leak-detection',
                'description': 'Detect potential memory leaks and resource management issues',
                'template': '''Detect memory leaks.

**Code:** {{code}}
**Language:** {{language}}

Check for:
1. Unclosed resources
2. Memory leaks
3. Resource management
4. Garbage collection issues
5. Circular references
6. Best practices''',
                'parameters': [
                    {'name': 'code', 'type': 'long_text', 'required': True},
                    {'name': 'language', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('reviewer_agent'),
                'category': categories.get('code-review')
            },
            {
                'category_slug': 'code-review',
                'name': 'Concurrency Issue Review',
                'slug': 'concurrency-issue-review',
                'description': 'Review code for concurrency and thread-safety issues',
                'template': '''Review concurrency issues.

**Code:** {{code}}
**Concurrency Model:** {{model}}

Check for:
1. Race conditions
2. Deadlocks
3. Thread safety
4. Synchronization issues
5. Lock ordering
6. Atomic operations
7. Best practices''',
                'parameters': [
                    {'name': 'code', 'type': 'long_text', 'required': True},
                    {'name': 'model', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('reviewer_agent'),
                'category': categories.get('code-review')
            },
            {
                'category_slug': 'code-review',
                'name': 'API Design Review',
                'slug': 'api-design-review-detailed',
                'description': 'Comprehensive review of API design and RESTful principles',
                'template': '''Review API design.

**API Specification:** {{api_spec}}
**Endpoints:** {{endpoints}}

Review:
1. RESTful principles
2. Resource naming
3. HTTP methods
4. Status codes
5. Error handling
6. Versioning
7. Documentation
8. Security''',
                'parameters': [
                    {'name': 'api_spec', 'type': 'long_text', 'required': True},
                    {'name': 'endpoints', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('reviewer_agent'),
                'category': categories.get('code-review')
            },
            {
                'category_slug': 'code-review',
                'name': 'Database Query Optimization Review',
                'slug': 'database-query-optimization-review',
                'description': 'Review and optimize database queries for performance',
                'template': '''Review database queries.

**Queries:** {{queries}}
**Database:** {{database}}

Review:
1. Query performance
2. Index usage
3. N+1 problems
4. Join optimization
5. Query plans
6. Caching opportunities
7. Optimization suggestions''',
                'parameters': [
                    {'name': 'queries', 'type': 'long_text', 'required': True},
                    {'name': 'database', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('reviewer_agent'),
                'category': categories.get('code-review')
            },
            {
                'category_slug': 'code-review',
                'name': 'Error Handling Review',
                'slug': 'error-handling-review',
                'description': 'Review error handling patterns and exception management',
                'template': '''Review error handling.

**Code:** {{code}}
**Language:** {{language}}

Review:
1. Exception handling
2. Error messages
3. Logging
4. Error recovery
5. User experience
6. Best practices''',
                'parameters': [
                    {'name': 'code', 'type': 'long_text', 'required': True},
                    {'name': 'language', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('reviewer_agent'),
                'category': categories.get('code-review')
            },
            {
                'category_slug': 'code-review',
                'name': 'Code Maintainability Review',
                'slug': 'code-maintainability-review',
                'description': 'Assess code maintainability and suggest improvements',
                'template': '''Review code maintainability.

**Code:** {{code}}
**Context:** {{context}}

Assess:
1. Code organization
2. Naming conventions
3. Documentation
4. Testability
5. Modularity
6. Dependencies
7. Technical debt
8. Improvement suggestions''',
                'parameters': [
                    {'name': 'code', 'type': 'long_text', 'required': True},
                    {'name': 'context', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('reviewer_agent'),
                'category': categories.get('code-review')
            },
            
            # Testing & QA (10 more)
            {
                'category_slug': 'testing-qa',
                'name': 'Generate Chaos Engineering Tests',
                'slug': 'generate-chaos-engineering-tests',
                'description': 'Create chaos engineering test scenarios for resilience',
                'template': '''Generate chaos engineering tests.

**System:** {{system}}
**Components:** {{components}}
**Scenarios:** {{scenarios}}

Generate:
1. Failure scenarios
2. Network partitions
3. Resource exhaustion
4. Latency injection
5. Service degradation
6. Recovery tests
7. Runbooks''',
                'parameters': [
                    {'name': 'system', 'type': 'text', 'required': True},
                    {'name': 'components', 'type': 'text', 'required': True},
                    {'name': 'scenarios', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            {
                'category_slug': 'testing-qa',
                'name': 'Create Accessibility Test Suite',
                'slug': 'create-accessibility-test-suite',
                'description': 'Generate accessibility tests for WCAG compliance',
                'template': '''Create accessibility test suite.

**Application:** {{application}}
**WCAG Level:** {{level}}
**Framework:** {{framework}}

Generate:
1. Screen reader tests
2. Keyboard navigation tests
3. Color contrast tests
4. ARIA label tests
5. Focus management tests
6. Compliance report''',
                'parameters': [
                    {'name': 'application', 'type': 'text', 'required': True},
                    {'name': 'level', 'type': 'text', 'required': True},
                    {'name': 'framework', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            {
                'category_slug': 'testing-qa',
                'name': 'Generate Load Testing Scripts',
                'slug': 'generate-load-testing-scripts',
                'description': 'Create load testing scripts for performance validation',
                'template': '''Generate load testing scripts.

**Tool:** {{tool}}
**Endpoints:** {{endpoints}}
**Load Profile:** {{load_profile}}

Generate:
1. Test scenarios
2. User profiles
3. Ramp-up patterns
4. Assertions
5. Monitoring setup
6. Report templates''',
                'parameters': [
                    {'name': 'tool', 'type': 'text', 'required': True},
                    {'name': 'endpoints', 'type': 'text', 'required': True},
                    {'name': 'load_profile', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            {
                'category_slug': 'testing-qa',
                'name': 'Create Mutation Testing Suite',
                'slug': 'create-mutation-testing-suite',
                'description': 'Generate mutation testing to assess test quality',
                'template': '''Create mutation testing suite.

**Code:** {{code}}
**Tests:** {{tests}}
**Framework:** {{framework}}

Generate:
1. Mutation operators
2. Mutant generation
3. Test execution
4. Mutation score
5. Coverage analysis
6. Report''',
                'parameters': [
                    {'name': 'code', 'type': 'text', 'required': True},
                    {'name': 'tests', 'type': 'text', 'required': True},
                    {'name': 'framework', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            {
                'category_slug': 'testing-qa',
                'name': 'Generate Visual Regression Tests',
                'slug': 'generate-visual-regression-tests',
                'description': 'Create visual regression tests for UI consistency',
                'template': '''Generate visual regression tests.

**Application:** {{application}}
**Pages:** {{pages}}
**Tool:** {{tool}}

Generate:
1. Baseline screenshots
2. Test scenarios
3. Comparison logic
4. Thresholds
5. CI/CD integration
6. Report generation''',
                'parameters': [
                    {'name': 'application', 'type': 'text', 'required': True},
                    {'name': 'pages', 'type': 'text', 'required': True},
                    {'name': 'tool', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            {
                'category_slug': 'testing-qa',
                'name': 'Create API Contract Testing',
                'slug': 'create-api-contract-testing',
                'description': 'Generate contract tests for API compatibility',
                'template': '''Create API contract testing.

**API:** {{api}}
**Contracts:** {{contracts}}
**Framework:** {{framework}}

Generate:
1. Contract definitions
2. Provider tests
3. Consumer tests
4. Versioning tests
5. Breaking change detection
6. Documentation''',
                'parameters': [
                    {'name': 'api', 'type': 'text', 'required': True},
                    {'name': 'contracts', 'type': 'text', 'required': True},
                    {'name': 'framework', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            {
                'category_slug': 'testing-qa',
                'name': 'Generate Security Test Cases',
                'slug': 'generate-security-test-cases-detailed',
                'description': 'Create comprehensive security test cases',
                'template': '''Generate security test cases.

**Application:** {{application}}
**Threat Model:** {{threat_model}}

Generate:
1. Authentication tests
2. Authorization tests
3. Input validation tests
4. SQL injection tests
5. XSS tests
6. CSRF tests
7. Security headers tests
8. OWASP Top 10 coverage''',
                'parameters': [
                    {'name': 'application', 'type': 'text', 'required': True},
                    {'name': 'threat_model', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            {
                'category_slug': 'testing-qa',
                'name': 'Create Test Data Management Strategy',
                'slug': 'create-test-data-management',
                'description': 'Develop strategy for managing test data',
                'template': '''Create test data management strategy.

**Application:** {{application}}
**Data Types:** {{data_types}}

Strategy should include:
1. Data generation
2. Data masking
3. Data refresh
4. Data isolation
5. Data cleanup
6. Data versioning''',
                'parameters': [
                    {'name': 'application', 'type': 'text', 'required': True},
                    {'name': 'data_types', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            {
                'category_slug': 'testing-qa',
                'name': 'Generate Test Automation Framework',
                'slug': 'generate-test-automation-framework',
                'description': 'Create test automation framework structure',
                'template': '''Generate test automation framework.

**Type:** {{type}}
**Language:** {{language}}
**Tools:** {{tools}}

Generate:
1. Framework structure
2. Page Object Model
3. Test utilities
4. Configuration
5. Reporting
6. CI/CD integration''',
                'parameters': [
                    {'name': 'type', 'type': 'text', 'required': True},
                    {'name': 'language', 'type': 'text', 'required': True},
                    {'name': 'tools', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            {
                'category_slug': 'testing-qa',
                'name': 'Create Test Metrics Dashboard',
                'slug': 'create-test-metrics-dashboard',
                'description': 'Generate test metrics dashboard configuration',
                'template': '''Create test metrics dashboard.

**Metrics:** {{metrics}}
**Tool:** {{tool}}

Dashboard should show:
1. Test coverage
2. Pass/fail rates
3. Execution time
4. Flaky tests
5. Test trends
6. Quality gates''',
                'parameters': [
                    {'name': 'metrics', 'type': 'text', 'required': True},
                    {'name': 'tool', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('qa_agent'),
                'category': categories.get('testing-qa')
            },
            
            # DevOps & Deployment (12 more)
            {
                'category_slug': 'devops-deployment',
                'name': 'Generate Terraform Infrastructure Code',
                'slug': 'generate-terraform-infrastructure',
                'description': 'Create Terraform code for infrastructure provisioning',
                'template': '''Generate Terraform infrastructure.

**Cloud Provider:** {{provider}}
**Resources:** {{resources}}
**Environment:** {{environment}}

Generate:
1. Provider configuration
2. Resource definitions
3. Variables
4. Outputs
5. Modules
6. State management''',
                'parameters': [
                    {'name': 'provider', 'type': 'text', 'required': True},
                    {'name': 'resources', 'type': 'text', 'required': True},
                    {'name': 'environment', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Create Ansible Playbook',
                'slug': 'create-ansible-playbook',
                'description': 'Generate Ansible playbook for configuration management',
                'template': '''Create Ansible playbook.

**Target:** {{target}}
**Tasks:** {{tasks}}
**Variables:** {{variables}}

Generate:
1. Playbook structure
2. Tasks
3. Handlers
4. Variables
5. Templates
6. Roles''',
                'parameters': [
                    {'name': 'target', 'type': 'text', 'required': True},
                    {'name': 'tasks', 'type': 'text', 'required': True},
                    {'name': 'variables', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Generate Helm Chart',
                'slug': 'generate-helm-chart',
                'description': 'Create Helm chart for Kubernetes deployment',
                'template': '''Generate Helm chart.

**Application:** {{application}}
**Components:** {{components}}
**Dependencies:** {{dependencies}}

Generate:
1. Chart structure
2. Values.yaml
3. Templates
4. Dependencies
5. Hooks
6. Documentation''',
                'parameters': [
                    {'name': 'application', 'type': 'text', 'required': True},
                    {'name': 'components', 'type': 'text', 'required': True},
                    {'name': 'dependencies', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Create GitOps Configuration',
                'slug': 'create-gitops-configuration',
                'description': 'Generate GitOps configuration for continuous deployment',
                'template': '''Create GitOps configuration.

**Tool:** {{tool}}
**Repositories:** {{repositories}}
**Environments:** {{environments}}

Generate:
1. Repository structure
2. Sync policies
3. Application definitions
4. Environment configs
5. Promotion workflows
6. Rollback procedures''',
                'parameters': [
                    {'name': 'tool', 'type': 'text', 'required': True},
                    {'name': 'repositories', 'type': 'text', 'required': True},
                    {'name': 'environments', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Generate Service Mesh Configuration',
                'slug': 'generate-service-mesh-config',
                'description': 'Create service mesh configuration (Istio, Linkerd)',
                'template': '''Generate service mesh configuration.

**Mesh:** {{mesh}}
**Services:** {{services}}
**Policies:** {{policies}}

Generate:
1. Service definitions
2. Virtual services
3. Destination rules
4. Traffic policies
5. Security policies
6. Observability config''',
                'parameters': [
                    {'name': 'mesh', 'type': 'text', 'required': True},
                    {'name': 'services', 'type': 'text', 'required': True},
                    {'name': 'policies', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Create Disaster Recovery Plan',
                'slug': 'create-disaster-recovery-plan',
                'description': 'Develop disaster recovery plan and runbooks',
                'template': '''Create disaster recovery plan.

**System:** {{system}}
**RTO:** {{rto}}
**RPO:** {{rpo}}

Plan should include:
1. Risk assessment
2. Recovery procedures
3. Backup strategy
4. Failover procedures
5. Testing schedule
6. Communication plan''',
                'parameters': [
                    {'name': 'system', 'type': 'text', 'required': True},
                    {'name': 'rto', 'type': 'text', 'required': True},
                    {'name': 'rpo', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Generate Observability Stack Configuration',
                'slug': 'generate-observability-stack',
                'description': 'Create configuration for observability tools (Prometheus, Grafana, etc.)',
                'template': '''Generate observability stack.

**Stack:** {{stack}}
**Services:** {{services}}
**Metrics:** {{metrics}}

Generate:
1. Prometheus config
2. Grafana dashboards
3. Alert rules
4. Log aggregation
5. Tracing setup
6. SLO/SLI definitions''',
                'parameters': [
                    {'name': 'stack', 'type': 'text', 'required': True},
                    {'name': 'services', 'type': 'text', 'required': True},
                    {'name': 'metrics', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Create Blue-Green Deployment Strategy',
                'slug': 'create-blue-green-deployment',
                'description': 'Generate blue-green deployment configuration',
                'template': '''Create blue-green deployment.

**Platform:** {{platform}}
**Application:** {{application}}
**Traffic Split:** {{traffic_split}}

Generate:
1. Environment setup
2. Traffic routing
3. Health checks
4. Rollback procedures
5. Monitoring
6. Automation scripts''',
                'parameters': [
                    {'name': 'platform', 'type': 'text', 'required': True},
                    {'name': 'application', 'type': 'text', 'required': True},
                    {'name': 'traffic_split', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Generate Container Security Scanning',
                'slug': 'generate-container-security-scanning',
                'description': 'Create container security scanning configuration',
                'template': '''Generate container security scanning.

**Registry:** {{registry}}
**Images:** {{images}}
**Tool:** {{tool}}

Generate:
1. Scan policies
2. CI/CD integration
3. Vulnerability reporting
4. Compliance checks
5. Remediation workflows
6. Monitoring''',
                'parameters': [
                    {'name': 'registry', 'type': 'text', 'required': True},
                    {'name': 'images', 'type': 'text', 'required': True},
                    {'name': 'tool', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Create Infrastructure Cost Optimization Plan',
                'slug': 'create-infrastructure-cost-optimization',
                'description': 'Develop plan for optimizing cloud infrastructure costs',
                'template': '''Create cost optimization plan.

**Cloud Provider:** {{provider}}
**Current Costs:** {{costs}}
**Budget:** {{budget}}

Plan should include:
1. Cost analysis
2. Right-sizing recommendations
3. Reserved instances
4. Spot instances
5. Auto-scaling
6. Monitoring
7. Optimization actions''',
                'parameters': [
                    {'name': 'provider', 'type': 'text', 'required': True},
                    {'name': 'costs', 'type': 'text', 'required': True},
                    {'name': 'budget', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Generate Multi-Region Deployment Config',
                'slug': 'generate-multi-region-deployment',
                'description': 'Create multi-region deployment configuration',
                'template': '''Generate multi-region deployment.

**Regions:** {{regions}}
**Application:** {{application}}
**Strategy:** {{strategy}}

Generate:
1. Region configuration
2. Replication setup
3. Failover procedures
4. Data synchronization
5. Traffic routing
6. Monitoring''',
                'parameters': [
                    {'name': 'regions', 'type': 'text', 'required': True},
                    {'name': 'application', 'type': 'text', 'required': True},
                    {'name': 'strategy', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            {
                'category_slug': 'devops-deployment',
                'name': 'Create Secrets Rotation Automation',
                'slug': 'create-secrets-rotation-automation',
                'description': 'Generate automation for rotating secrets and credentials',
                'template': '''Create secrets rotation automation.

**Secrets Type:** {{secrets_type}}
**Rotation Frequency:** {{frequency}}
**Tool:** {{tool}}

Generate:
1. Rotation schedule
2. Automation scripts
3. Validation tests
4. Rollback procedures
5. Monitoring
6. Notification setup''',
                'parameters': [
                    {'name': 'secrets_type', 'type': 'text', 'required': True},
                    {'name': 'frequency', 'type': 'text', 'required': True},
                    {'name': 'tool', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('devops_agent'),
                'category': categories.get('devops-deployment')
            },
            
            # UX/UI Design (8 more)
            {
                'category_slug': 'ux-ui-design',
                'name': 'Generate Design System Components',
                'slug': 'generate-design-system-components',
                'description': 'Create design system component library',
                'template': '''Generate design system components.

**Framework:** {{framework}}
**Components:** {{components}}
**Style Guide:** {{style_guide}}

Generate:
1. Component library
2. Style tokens
3. Documentation
4. Usage examples
5. Accessibility guidelines
6. Testing guidelines''',
                'parameters': [
                    {'name': 'framework', 'type': 'text', 'required': True},
                    {'name': 'components', 'type': 'text', 'required': True},
                    {'name': 'style_guide', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('ux_agent'),
                'category': categories.get('ux-ui-design')
            },
            {
                'category_slug': 'ux-ui-design',
                'name': 'Create User Journey Map',
                'slug': 'create-user-journey-map',
                'description': 'Generate user journey map for UX analysis',
                'template': '''Create user journey map.

**User Persona:** {{persona}}
**Goal:** {{goal}}
**Touchpoints:** {{touchpoints}}

Map should include:
1. User stages
2. Actions
3. Emotions
4. Pain points
5. Opportunities
6. Metrics''',
                'parameters': [
                    {'name': 'persona', 'type': 'text', 'required': True},
                    {'name': 'goal', 'type': 'text', 'required': True},
                    {'name': 'touchpoints', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('ux_agent'),
                'category': categories.get('ux-ui-design')
            },
            {
                'category_slug': 'ux-ui-design',
                'name': 'Generate A/B Testing Plan',
                'slug': 'generate-ab-testing-plan',
                'description': 'Create A/B testing plan for UI/UX optimization',
                'template': '''Generate A/B testing plan.

**Feature:** {{feature}}
**Hypothesis:** {{hypothesis}}
**Metrics:** {{metrics}}

Plan should include:
1. Test variants
2. Success metrics
3. Sample size
4. Duration
5. Statistical significance
6. Implementation plan''',
                'parameters': [
                    {'name': 'feature', 'type': 'text', 'required': True},
                    {'name': 'hypothesis', 'type': 'text', 'required': True},
                    {'name': 'metrics', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('ux_agent'),
                'category': categories.get('ux-ui-design')
            },
            {
                'category_slug': 'ux-ui-design',
                'name': 'Create Responsive Design Guidelines',
                'slug': 'create-responsive-design-guidelines',
                'description': 'Generate responsive design guidelines and breakpoints',
                'template': '''Create responsive design guidelines.

**Platforms:** {{platforms}}
**Breakpoints:** {{breakpoints}}

Guidelines should include:
1. Breakpoint definitions
2. Grid system
3. Typography scaling
4. Component behavior
5. Image optimization
6. Testing checklist''',
                'parameters': [
                    {'name': 'platforms', 'type': 'text', 'required': True},
                    {'name': 'breakpoints', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('ux_agent'),
                'category': categories.get('ux-ui-design')
            },
            {
                'category_slug': 'ux-ui-design',
                'name': 'Generate Accessibility Audit Checklist',
                'slug': 'generate-accessibility-audit-checklist',
                'description': 'Create comprehensive accessibility audit checklist',
                'template': '''Generate accessibility audit checklist.

**WCAG Level:** {{level}}
**Application Type:** {{app_type}}

Checklist should cover:
1. Perceivable
2. Operable
3. Understandable
4. Robust
5. Testing tools
6. Remediation steps''',
                'parameters': [
                    {'name': 'level', 'type': 'text', 'required': True},
                    {'name': 'app_type', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('ux_agent'),
                'category': categories.get('ux-ui-design')
            },
            {
                'category_slug': 'ux-ui-design',
                'name': 'Create Prototype Specifications',
                'slug': 'create-prototype-specifications',
                'description': 'Generate detailed specifications from design prototypes',
                'template': '''Create prototype specifications.

**Prototype:** {{prototype}}
**Components:** {{components}}

Specifications should include:
1. Component details
2. Interactions
3. States
4. Animations
5. Responsive behavior
6. Implementation notes''',
                'parameters': [
                    {'name': 'prototype', 'type': 'text', 'required': True},
                    {'name': 'components', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('ux_agent'),
                'category': categories.get('ux-ui-design')
            },
            {
                'category_slug': 'ux-ui-design',
                'name': 'Generate Design Token System',
                'slug': 'generate-design-token-system',
                'description': 'Create design token system for consistent theming',
                'template': '''Generate design token system.

**Theme:** {{theme}}
**Platforms:** {{platforms}}

Generate:
1. Color tokens
2. Typography tokens
3. Spacing tokens
4. Shadow tokens
5. Animation tokens
6. Platform exports''',
                'parameters': [
                    {'name': 'theme', 'type': 'text', 'required': True},
                    {'name': 'platforms', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('ux_agent'),
                'category': categories.get('ux-ui-design')
            },
            {
                'category_slug': 'ux-ui-design',
                'name': 'Create Micro-interaction Design',
                'slug': 'create-micro-interaction-design',
                'description': 'Design micro-interactions for enhanced UX',
                'template': '''Create micro-interaction design.

**Interactions:** {{interactions}}
**Context:** {{context}}

Design should include:
1. Trigger conditions
2. Feedback mechanisms
3. Animation specs
4. Timing
5. Easing functions
6. Implementation guide''',
                'parameters': [
                    {'name': 'interactions', 'type': 'text', 'required': True},
                    {'name': 'context', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('ux_agent'),
                'category': categories.get('ux-ui-design')
            },
            
            # Documentation (8 more)
            {
                'category_slug': 'documentation',
                'name': 'Generate API Reference Documentation',
                'slug': 'generate-api-reference-documentation',
                'description': 'Create comprehensive API reference documentation',
                'template': '''Generate API reference documentation.

**API:** {{api}}
**Format:** {{format}}
**Examples:** {{examples}}

Generate:
1. Endpoint documentation
2. Request/response schemas
3. Authentication
4. Error codes
5. Code examples
6. SDK documentation''',
                'parameters': [
                    {'name': 'api', 'type': 'text', 'required': True},
                    {'name': 'format', 'type': 'text', 'required': False},
                    {'name': 'examples', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('doc_agent'),
                'category': categories.get('documentation')
            },
            {
                'category_slug': 'documentation',
                'name': 'Create Developer Onboarding Guide',
                'slug': 'create-developer-onboarding-guide',
                'description': 'Generate developer onboarding documentation',
                'template': '''Create developer onboarding guide.

**Project:** {{project}}
**Tech Stack:** {{tech_stack}}

Guide should include:
1. Setup instructions
2. Development environment
3. Project structure
4. Coding standards
5. Testing guidelines
6. Contribution process''',
                'parameters': [
                    {'name': 'project', 'type': 'text', 'required': True},
                    {'name': 'tech_stack', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('doc_agent'),
                'category': categories.get('documentation')
            },
            {
                'category_slug': 'documentation',
                'name': 'Generate Architecture Decision Records',
                'slug': 'generate-architecture-decision-records',
                'description': 'Create Architecture Decision Records (ADRs)',
                'template': '''Generate Architecture Decision Records.

**Decision:** {{decision}}
**Context:** {{context}}
**Status:** {{status}}

Record should include:
1. Context
2. Decision
3. Consequences
4. Alternatives considered
5. Status
6. Date''',
                'parameters': [
                    {'name': 'decision', 'type': 'text', 'required': True},
                    {'name': 'context', 'type': 'text', 'required': True},
                    {'name': 'status', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('doc_agent'),
                'category': categories.get('documentation')
            },
            {
                'category_slug': 'documentation',
                'name': 'Create Runbook Documentation',
                'slug': 'create-runbook-documentation',
                'description': 'Generate operational runbooks for common tasks',
                'template': '''Create runbook documentation.

**Task:** {{task}}
**System:** {{system}}
**Frequency:** {{frequency}}

Runbook should include:
1. Prerequisites
2. Step-by-step procedures
3. Verification steps
4. Troubleshooting
5. Rollback procedures
6. Contacts''',
                'parameters': [
                    {'name': 'task', 'type': 'text', 'required': True},
                    {'name': 'system', 'type': 'text', 'required': True},
                    {'name': 'frequency', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('doc_agent'),
                'category': categories.get('documentation')
            },
            {
                'category_slug': 'documentation',
                'name': 'Generate Code Review Guidelines',
                'slug': 'generate-code-review-guidelines',
                'description': 'Create code review guidelines and checklist',
                'template': '''Generate code review guidelines.

**Team:** {{team}}
**Language:** {{language}}

Guidelines should include:
1. Review process
2. Checklist items
3. Best practices
4. Common issues
5. Review templates
6. Tools and automation''',
                'parameters': [
                    {'name': 'team', 'type': 'text', 'required': True},
                    {'name': 'language', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('doc_agent'),
                'category': categories.get('documentation')
            },
            {
                'category_slug': 'documentation',
                'name': 'Create Incident Response Playbook',
                'slug': 'create-incident-response-playbook',
                'description': 'Generate incident response playbook',
                'template': '''Create incident response playbook.

**Incident Type:** {{incident_type}}
**Severity Levels:** {{severity}}

Playbook should include:
1. Detection procedures
2. Escalation paths
3. Response procedures
4. Communication plan
5. Post-incident review
6. Prevention measures''',
                'parameters': [
                    {'name': 'incident_type', 'type': 'text', 'required': True},
                    {'name': 'severity', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('doc_agent'),
                'category': categories.get('documentation')
            },
            {
                'category_slug': 'documentation',
                'name': 'Generate Performance Tuning Guide',
                'slug': 'generate-performance-tuning-guide',
                'description': 'Create performance tuning documentation',
                'template': '''Generate performance tuning guide.

**Application:** {{application}}
**Bottlenecks:** {{bottlenecks}}

Guide should include:
1. Performance metrics
2. Profiling techniques
3. Optimization strategies
4. Database tuning
5. Caching strategies
6. Monitoring setup''',
                'parameters': [
                    {'name': 'application', 'type': 'text', 'required': True},
                    {'name': 'bottlenecks', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('doc_agent'),
                'category': categories.get('documentation')
            },
            {
                'category_slug': 'documentation',
                'name': 'Create Security Documentation',
                'slug': 'create-security-documentation',
                'description': 'Generate security documentation and guidelines',
                'template': '''Create security documentation.

**Application:** {{application}}
**Threat Model:** {{threat_model}}

Documentation should include:
1. Security architecture
2. Threat model
3. Security controls
4. Vulnerability management
5. Incident response
6. Compliance requirements''',
                'parameters': [
                    {'name': 'application', 'type': 'text', 'required': True},
                    {'name': 'threat_model', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('doc_agent'),
                'category': categories.get('documentation')
            },
            
            # Project Management (6 more)
            {
                'category_slug': 'project-management',
                'name': 'Generate Resource Capacity Plan',
                'slug': 'generate-resource-capacity-plan',
                'description': 'Create resource capacity planning document',
                'template': '''Generate resource capacity plan.

**Project:** {{project}}
**Timeline:** {{timeline}}
**Resources:** {{resources}}

Plan should include:
1. Resource allocation
2. Capacity analysis
3. Skill requirements
4. Availability
5. Constraints
6. Recommendations''',
                'parameters': [
                    {'name': 'project', 'type': 'text', 'required': True},
                    {'name': 'timeline', 'type': 'text', 'required': True},
                    {'name': 'resources', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('pm_agent'),
                'category': categories.get('project-management')
            },
            {
                'category_slug': 'project-management',
                'name': 'Create Stakeholder Engagement Plan',
                'slug': 'create-stakeholder-engagement-plan',
                'description': 'Develop stakeholder engagement and communication plan',
                'template': '''Create stakeholder engagement plan.

**Project:** {{project}}
**Stakeholders:** {{stakeholders}}

Plan should include:
1. Stakeholder mapping
2. Communication frequency
3. Channels
4. Meeting schedule
5. Reporting structure
6. Feedback mechanisms''',
                'parameters': [
                    {'name': 'project', 'type': 'text', 'required': True},
                    {'name': 'stakeholders', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('pm_agent'),
                'category': categories.get('project-management')
            },
            {
                'category_slug': 'project-management',
                'name': 'Generate Project Health Dashboard',
                'slug': 'generate-project-health-dashboard',
                'description': 'Create project health dashboard configuration',
                'template': '''Generate project health dashboard.

**Project:** {{project}}
**Metrics:** {{metrics}}
**Tool:** {{tool}}

Dashboard should show:
1. Schedule status
2. Budget status
3. Quality metrics
4. Risk status
5. Team velocity
6. Health score''',
                'parameters': [
                    {'name': 'project', 'type': 'text', 'required': True},
                    {'name': 'metrics', 'type': 'text', 'required': True},
                    {'name': 'tool', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('pm_agent'),
                'category': categories.get('project-management')
            },
            {
                'category_slug': 'project-management',
                'name': 'Create Change Management Process',
                'slug': 'create-change-management-process',
                'description': 'Develop change management process for project changes',
                'template': '''Create change management process.

**Project:** {{project}}
**Change Types:** {{change_types}}

Process should include:
1. Change request form
2. Impact analysis
3. Approval workflow
4. Implementation plan
5. Communication plan
6. Tracking mechanism''',
                'parameters': [
                    {'name': 'project', 'type': 'text', 'required': True},
                    {'name': 'change_types', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('pm_agent'),
                'category': categories.get('project-management')
            },
            {
                'category_slug': 'project-management',
                'name': 'Generate Project Closure Report',
                'slug': 'generate-project-closure-report',
                'description': 'Create project closure and lessons learned report',
                'template': '''Generate project closure report.

**Project:** {{project}}
**Duration:** {{duration}}
**Outcomes:** {{outcomes}}

Report should include:
1. Project summary
2. Objectives achieved
3. Lessons learned
4. Best practices
5. Recommendations
6. Team feedback''',
                'parameters': [
                    {'name': 'project', 'type': 'text', 'required': True},
                    {'name': 'duration', 'type': 'text', 'required': True},
                    {'name': 'outcomes', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('pm_agent'),
                'category': categories.get('project-management')
            },
            {
                'category_slug': 'project-management',
                'name': 'Create Dependency Management Plan',
                'slug': 'create-dependency-management-plan',
                'description': 'Develop plan for managing project dependencies',
                'template': '''Create dependency management plan.

**Project:** {{project}}
**Dependencies:** {{dependencies}}

Plan should include:
1. Dependency mapping
2. Critical path
3. Risk assessment
4. Mitigation strategies
5. Monitoring
6. Escalation procedures''',
                'parameters': [
                    {'name': 'project', 'type': 'text', 'required': True},
                    {'name': 'dependencies', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('pm_agent'),
                'category': categories.get('project-management')
            },
            
            # Design & Architecture (6 more)
            {
                'category_slug': 'design-architecture',
                'name': 'Generate Event Sourcing Architecture',
                'slug': 'generate-event-sourcing-architecture',
                'description': 'Create event sourcing architecture design',
                'template': '''Generate event sourcing architecture.

**Domain:** {{domain}}
**Events:** {{events}}

Design should include:
1. Event store
2. Aggregates
3. Event handlers
4. Projections
5. Snapshots
6. Replay mechanism''',
                'parameters': [
                    {'name': 'domain', 'type': 'text', 'required': True},
                    {'name': 'events', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('architect_agent'),
                'category': categories.get('design-architecture')
            },
            {
                'category_slug': 'design-architecture',
                'name': 'Create Domain-Driven Design Model',
                'slug': 'create-domain-driven-design-model',
                'description': 'Generate Domain-Driven Design (DDD) model',
                'template': '''Create DDD model.

**Domain:** {{domain}}
**Bounded Contexts:** {{contexts}}

Model should include:
1. Domain entities
2. Value objects
3. Aggregates
4. Domain services
5. Repositories
6. Bounded contexts''',
                'parameters': [
                    {'name': 'domain', 'type': 'text', 'required': True},
                    {'name': 'contexts', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('architect_agent'),
                'category': categories.get('design-architecture')
            },
            {
                'category_slug': 'design-architecture',
                'name': 'Generate Hexagonal Architecture Design',
                'slug': 'generate-hexagonal-architecture',
                'description': 'Create hexagonal (ports and adapters) architecture',
                'template': '''Generate hexagonal architecture.

**Application:** {{application}}
**Ports:** {{ports}}

Design should include:
1. Core domain
2. Ports (interfaces)
3. Adapters
4. Dependency rules
5. Testing strategy
6. Implementation guide''',
                'parameters': [
                    {'name': 'application', 'type': 'text', 'required': True},
                    {'name': 'ports', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('architect_agent'),
                'category': categories.get('design-architecture')
            },
            {
                'category_slug': 'design-architecture',
                'name': 'Create Scalability Architecture Plan',
                'slug': 'create-scalability-architecture-plan',
                'description': 'Develop architecture plan for horizontal and vertical scaling',
                'template': '''Create scalability architecture plan.

**System:** {{system}}
**Scale Requirements:** {{scale_requirements}}

Plan should include:
1. Scaling strategy
2. Load distribution
3. Caching strategy
4. Database scaling
5. Monitoring
6. Cost analysis''',
                'parameters': [
                    {'name': 'system', 'type': 'text', 'required': True},
                    {'name': 'scale_requirements', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('architect_agent'),
                'category': categories.get('design-architecture')
            },
            {
                'category_slug': 'design-architecture',
                'name': 'Generate API Gateway Architecture',
                'slug': 'generate-api-gateway-architecture',
                'description': 'Design API gateway architecture pattern',
                'template': '''Generate API gateway architecture.

**Services:** {{services}}
**Gateway Type:** {{gateway_type}}

Design should include:
1. Gateway components
2. Routing rules
3. Aggregation patterns
4. Security
5. Rate limiting
6. Monitoring''',
                'parameters': [
                    {'name': 'services', 'type': 'text', 'required': True},
                    {'name': 'gateway_type', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('architect_agent'),
                'category': categories.get('design-architecture')
            },
            {
                'category_slug': 'design-architecture',
                'name': 'Create Data Architecture Design',
                'slug': 'create-data-architecture-design',
                'description': 'Design data architecture and data flow',
                'template': '''Create data architecture design.

**Data Sources:** {{data_sources}}
**Use Cases:** {{use_cases}}

Design should include:
1. Data models
2. Data flow
3. Storage strategy
4. Processing pipeline
5. Data governance
6. Security model''',
                'parameters': [
                    {'name': 'data_sources', 'type': 'text', 'required': True},
                    {'name': 'use_cases', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('architect_agent'),
                'category': categories.get('design-architecture')
            },
            
            # Business Analysis (5 more)
            {
                'category_slug': 'business-analysis',
                'name': 'Generate Business Process Model',
                'slug': 'generate-business-process-model',
                'description': 'Create business process model and workflow',
                'template': '''Generate business process model.

**Process:** {{process}}
**Stakeholders:** {{stakeholders}}

Model should include:
1. Process steps
2. Decision points
3. Roles and responsibilities
4. Systems involved
5. Metrics
6. Improvement opportunities''',
                'parameters': [
                    {'name': 'process', 'type': 'text', 'required': True},
                    {'name': 'stakeholders', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('business-analysis')
            },
            {
                'category_slug': 'business-analysis',
                'name': 'Create Cost-Benefit Analysis',
                'slug': 'create-cost-benefit-analysis',
                'description': 'Generate cost-benefit analysis for business decisions',
                'template': '''Create cost-benefit analysis.

**Initiative:** {{initiative}}
**Timeframe:** {{timeframe}}
**Costs:** {{costs}}
**Benefits:** {{benefits}}

Analysis should include:
1. Cost breakdown
2. Benefit quantification
3. ROI calculation
4. Risk assessment
5. Sensitivity analysis
6. Recommendations''',
                'parameters': [
                    {'name': 'initiative', 'type': 'text', 'required': True},
                    {'name': 'timeframe', 'type': 'text', 'required': True},
                    {'name': 'costs', 'type': 'text', 'required': True},
                    {'name': 'benefits', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('business-analysis')
            },
            {
                'category_slug': 'business-analysis',
                'name': 'Generate Market Analysis Report',
                'slug': 'generate-market-analysis-report',
                'description': 'Create market analysis and competitive intelligence report',
                'template': '''Generate market analysis report.

**Market:** {{market}}
**Product:** {{product}}

Report should include:
1. Market size
2. Trends
3. Competitors
4. Customer segments
5. Opportunities
6. Threats
7. Recommendations''',
                'parameters': [
                    {'name': 'market', 'type': 'text', 'required': True},
                    {'name': 'product', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('business-analysis')
            },
            {
                'category_slug': 'business-analysis',
                'name': 'Create Business Case Document',
                'slug': 'create-business-case-document',
                'description': 'Generate comprehensive business case document',
                'template': '''Create business case document.

**Initiative:** {{initiative}}
**Sponsor:** {{sponsor}}
**Objectives:** {{objectives}}

Document should include:
1. Executive summary
2. Problem statement
3. Proposed solution
4. Benefits
5. Costs
6. Risks
7. Recommendations''',
                'parameters': [
                    {'name': 'initiative', 'type': 'text', 'required': True},
                    {'name': 'sponsor', 'type': 'text', 'required': True},
                    {'name': 'objectives', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('business-analysis')
            },
            {
                'category_slug': 'business-analysis',
                'name': 'Generate Stakeholder Analysis Matrix',
                'slug': 'generate-stakeholder-analysis-matrix',
                'description': 'Create stakeholder analysis and influence matrix',
                'template': '''Generate stakeholder analysis matrix.

**Project:** {{project}}
**Stakeholders:** {{stakeholders}}

Matrix should include:
1. Stakeholder identification
2. Influence level
3. Interest level
4. Engagement strategy
5. Communication plan
6. Risk assessment''',
                'parameters': [
                    {'name': 'project', 'type': 'text', 'required': True},
                    {'name': 'stakeholders', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('ba_agent'),
                'category': categories.get('business-analysis')
            },
            
            # Legal & Compliance (5 more)
            {
                'category_slug': 'legal-compliance',
                'name': 'Generate Privacy Policy Template',
                'slug': 'generate-privacy-policy-template',
                'description': 'Create privacy policy template compliant with GDPR/CCPA',
                'template': '''Generate privacy policy template.

**Application:** {{application}}
**Jurisdiction:** {{jurisdiction}}
**Data Collected:** {{data_collected}}

Template should include:
1. Data collection
2. Data usage
3. Data sharing
4. User rights
5. Security measures
6. Contact information''',
                'parameters': [
                    {'name': 'application', 'type': 'text', 'required': True},
                    {'name': 'jurisdiction', 'type': 'text', 'required': True},
                    {'name': 'data_collected', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('legal_agent'),
                'category': categories.get('legal-compliance')
            },
            {
                'category_slug': 'legal-compliance',
                'name': 'Create Terms of Service Template',
                'slug': 'create-terms-of-service-template',
                'description': 'Generate terms of service template',
                'template': '''Create terms of service template.

**Service:** {{service}}
**Jurisdiction:** {{jurisdiction}}

Template should include:
1. Service description
2. User obligations
3. Intellectual property
4. Limitation of liability
5. Dispute resolution
6. Governing law''',
                'parameters': [
                    {'name': 'service', 'type': 'text', 'required': True},
                    {'name': 'jurisdiction', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('legal_agent'),
                'category': categories.get('legal-compliance')
            },
            {
                'category_slug': 'legal-compliance',
                'name': 'Generate Data Processing Agreement',
                'slug': 'generate-data-processing-agreement',
                'description': 'Create data processing agreement (DPA) template',
                'template': '''Generate data processing agreement.

**Data Controller:** {{controller}}
**Data Processor:** {{processor}}
**Data Types:** {{data_types}}

Agreement should include:
1. Purpose of processing
2. Data types
3. Security measures
4. Sub-processors
5. Data subject rights
6. Breach notification''',
                'parameters': [
                    {'name': 'controller', 'type': 'text', 'required': True},
                    {'name': 'processor', 'type': 'text', 'required': True},
                    {'name': 'data_types', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('legal_agent'),
                'category': categories.get('legal-compliance')
            },
            {
                'category_slug': 'legal-compliance',
                'name': 'Create Compliance Audit Checklist',
                'slug': 'create-compliance-audit-checklist',
                'description': 'Generate compliance audit checklist for regulations',
                'template': '''Create compliance audit checklist.

**Regulation:** {{regulation}}
**Organization:** {{organization}}

Checklist should cover:
1. Data protection
2. Security controls
3. Documentation
4. Training
5. Incident response
6. Reporting requirements''',
                'parameters': [
                    {'name': 'regulation', 'type': 'text', 'required': True},
                    {'name': 'organization', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('legal_agent'),
                'category': categories.get('legal-compliance')
            },
            {
                'category_slug': 'legal-compliance',
                'name': 'Generate Intellectual Property Review',
                'slug': 'generate-intellectual-property-review',
                'description': 'Create IP review and licensing analysis',
                'template': '''Generate IP review.

**Product:** {{product}}
**Technologies:** {{technologies}}
**Dependencies:** {{dependencies}}

Review should include:
1. IP ownership
2. License compliance
3. Third-party licenses
4. Open source usage
5. Patent considerations
6. Recommendations''',
                'parameters': [
                    {'name': 'product', 'type': 'text', 'required': True},
                    {'name': 'technologies', 'type': 'text', 'required': True},
                    {'name': 'dependencies', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('legal_agent'),
                'category': categories.get('legal-compliance')
            },
            
            # Research & Analysis (5 more)
            {
                'category_slug': 'research-analysis',
                'name': 'Generate Technology Research Report',
                'slug': 'generate-technology-research-report',
                'description': 'Create technology research and evaluation report',
                'template': '''Generate technology research report.

**Technology:** {{technology}}
**Use Case:** {{use_case}}

Report should include:
1. Technology overview
2. Features
3. Pros and cons
4. Alternatives
5. Adoption considerations
6. Recommendations''',
                'parameters': [
                    {'name': 'technology', 'type': 'text', 'required': True},
                    {'name': 'use_case', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('research_agent'),
                'category': categories.get('research-analysis')
            },
            {
                'category_slug': 'research-analysis',
                'name': 'Create Competitive Analysis Report',
                'slug': 'create-competitive-analysis-report',
                'description': 'Generate competitive analysis and benchmarking report',
                'template': '''Create competitive analysis report.

**Product:** {{product}}
**Competitors:** {{competitors}}

Report should include:
1. Competitor overview
2. Feature comparison
3. Pricing analysis
4. Market positioning
5. Strengths/weaknesses
6. Opportunities''',
                'parameters': [
                    {'name': 'product', 'type': 'text', 'required': True},
                    {'name': 'competitors', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('research_agent'),
                'category': categories.get('research-analysis')
            },
            {
                'category_slug': 'research-analysis',
                'name': 'Generate User Research Report',
                'slug': 'generate-user-research-report',
                'description': 'Create user research findings and insights report',
                'template': '''Generate user research report.

**Research Method:** {{method}}
**Participants:** {{participants}}
**Findings:** {{findings}}

Report should include:
1. Research objectives
2. Methodology
3. Key findings
4. User insights
5. Pain points
6. Recommendations''',
                'parameters': [
                    {'name': 'method', 'type': 'text', 'required': True},
                    {'name': 'participants', 'type': 'text', 'required': False},
                    {'name': 'findings', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('research_agent'),
                'category': categories.get('research-analysis')
            },
            {
                'category_slug': 'research-analysis',
                'name': 'Create Feasibility Study',
                'slug': 'create-feasibility-study',
                'description': 'Generate feasibility study for project or initiative',
                'template': '''Create feasibility study.

**Project:** {{project}}
**Objectives:** {{objectives}}

Study should include:
1. Technical feasibility
2. Economic feasibility
3. Operational feasibility
4. Schedule feasibility
5. Risk assessment
6. Recommendations''',
                'parameters': [
                    {'name': 'project', 'type': 'text', 'required': True},
                    {'name': 'objectives', 'type': 'text', 'required': True}
                ],
                'recommended_agent': agents.get('research_agent'),
                'category': categories.get('research-analysis')
            },
            {
                'category_slug': 'research-analysis',
                'name': 'Generate Trend Analysis Report',
                'slug': 'generate-trend-analysis-report',
                'description': 'Create trend analysis and forecasting report',
                'template': '''Generate trend analysis report.

**Domain:** {{domain}}
**Timeframe:** {{timeframe}}
**Data Sources:** {{data_sources}}

Report should include:
1. Historical trends
2. Current state
3. Future projections
4. Key drivers
5. Implications
6. Recommendations''',
                'parameters': [
                    {'name': 'domain', 'type': 'text', 'required': True},
                    {'name': 'timeframe', 'type': 'text', 'required': True},
                    {'name': 'data_sources', 'type': 'text', 'required': False}
                ],
                'recommended_agent': agents.get('research_agent'),
                'category': categories.get('research-analysis')
            }
        ]
        
        created = 0
        updated = 0
        errors = 0
        
        self.stdout.write(f"Processing {len(new_commands)} commands...")
        self.stdout.write("")
        
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
        
        # Show final count
        total_commands = CommandTemplate.objects.count()
        self.stdout.write("")
        self.stdout.write(f"   Total Commands: {total_commands}/325 ({total_commands/325*100:.1f}%)")
        self.stdout.write("=" * 60)

