---
title: "HishamOS - Architecture Decision Records (ADR)"
description: "**Last Updated:** December 1, 2024"

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Project Manager
    - CTO / Technical Lead
  secondary:
    - All

applicable_phases:
  primary:
    - Development

tags:
  - core

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

# HishamOS - Architecture Decision Records (ADR)

**Last Updated:** December 1, 2024  
**Purpose:** Document important technical and architectural decisions with context and reasoning

---

## ADR-001: Use SQLite for Development, PostgreSQL for Production

**Date:** October 15, 2024  
**Status:** ✅ ACCEPTED  
**Deciders:** Development Team  
**Phase:** 0 (Project Foundation)

### Context
Need database for development and production. PostgreSQL is production-grade but requires setup. SQLite is lightweight but has limitations.

### Decision
Use SQLite for local development, PostgreSQL for production environments.

**Rationale:**
- **Development Speed:** SQLite requires ZERO setup (file-based)
- **Production Quality:** PostgreSQL handles concurrent writes, advanced features
- **Django Support:** Django supports both natively, migrations mostly compatible

### Consequences

**Positive:**
- Developers can start immediately (no DB setup)
- Production gets enterprise-grade database
- Lower development machine requirements

**Negative:**
- Must test migrations on BOTH databases
- Some PostgreSQL features unavailable in dev (ArrayField compatibility)
- Risk of SQLite-specific bugs not caught in dev

**Mitigation:**
- Run CI/CD tests against PostgreSQL
- Document PostgreSQL-specific features
- Periodic manual testing on PostgreSQL

### Alternatives Considered

**Option 1:** PostgreSQL everywhere
- **Rejected:** Too heavy for local development, slower startup

**Option 2:** SQLite everywhere
- **Rejected:** Cannot handle production load, missing features

**Option 3:** Docker PostgreSQL for dev
- **Rejected:** Slower than SQLite, adds Docker dependency

### Current Status
- Phase 0-5: Successfully using SQLite for dev
- **Issue:** Phase 6 SQLite missing agents table (BLOCKER-002)
- **Learning:** Migration compatibility more important than anticipated

---

## ADR-002: Monorepo Structure with 8 Django Apps

**Date:** October 15, 2024  
**Status:** ✅ ACCEPTED  
**Deciders:** Development Team  
**Phase:** 0 (Project Foundation)

### Context
Need to organize codebase for large AI platform with many features. Options: single app, multiple apps, microservices.

### Decision
Monorepo with 8 Django apps: authentication, agents, commands, workflows, projects, integrations, results, monitoring.

**Rationale:**
- **Separation of Concerns:** Each app handles specific domain
- **Modularity:** Apps can be developed independently
- **Django Best Practice:** Aligns with Django app philosophy
- **Not Microservices:** Avoids network overhead, simpler deployment

### Consequences

**Positive:**
- Clear code organization
- Easy to find code (know which app it's in)
- Can assign different agents to different apps
- Future: Could extract to microservices if needed

**Negative:**
- More boilerplate (each app needs models, views, etc.)
- Cross-app dependencies need management
- 8 migration folders to track

### App Breakdown
1. **authentication:** Users, JWT, API keys, permissions
2. **agents:** AI agent engine, execution, dispatcher
3. **commands:** Command library, templates, execution
4. **workflows:** Workflow orchestration, state machines
5. **projects:** Project management (Jira-like features)
6. **integrations:** AI platform adapters, external APIs
7. **results:** Output storage, execution history
8. **monitoring:** System health, metrics, logging

### Alternatives Considered

**Option 1:** Single Django app
- **Rejected:** Would become unmaintainable at scale

**Option 2:** Microservices
- **Rejected:** Over-engineering for current scope, adds complexity

---

## ADR-003: Django REST Framework for API Layer

**Date:** October 15, 2024  
**Status:** ✅ ACCEPTED  
**Deciders:** Development Team  
**Phase:** 0 (Project Foundation)

### Context
Need robust API for frontend and external integrations. Options: Django REST Framework (DRF), FastAPI, plain Django views.

### Decision
Use Django REST Framework as primary API layer.

**Rationale:**
- **Django Integration:** Native Django integration
- **Mature Ecosystem:** Battle-tested, extensive documentation
- **Serializers:** Automatic request/response validation
- **ViewSets:** Reduces boilerplate for CRUD operations
- **Authentication:** Built-in JWT support (djangorestframework-simplejwt)
- **OpenAPI:** Automatic API docs with drf-spectacular

### Consequences

**Positive:**
- Automatic API documentation (Swagger UI)
- Less code to write (ViewSets vs manual views)
- Strong validation
- Easy to add permissions per endpoint

**Negative:**
- Learning curve for serializers
- Some performance overhead vs FastAPI
- Less flexible than plain Django views

### Alternatives Considered

**Option 1:** FastAPI
- **Rejected:** Not Django-native, would need two frameworks

**Option 2:** Plain Django views
- **Rejected:** Too much boilerplate, no automatic docs

**Option 3:** GraphQL
- **Rejected:** Over-engineering, REST sufficient for needs

---

## ADR-004: JWT for Authentication, API Keys for External Access

**Date:** November 10, 2024  
**Status:** ✅ ACCEPTED  
**Deciders:** Development Team  
**Phase:** 2 (Authentication)

### Context
Need authentication for both users (web/mobile) and external systems (API integrations).

### Decision
Dual authentication: JWT tokens for users, API keys for external systems.

**Rationale:**
- **JWT for Users:** Stateless, works with SPA frontend, short-lived tokens
- **API Keys for APIs:** Long-lived, simpler for external integrations
- **Security:** JWT auto-expires, API keys can be rotated
- **Flexibility:** Each use case gets appropriate auth method

### Consequences

**Positive:**
- Users get modern token-based auth
- External systems get simple API key auth
- Can revoke API keys without affecting users
- Rate limiting per API key

**Negative:**
- Two authentication systems to maintain
- Must test both auth methods
- API key storage security critical

### Configuration
- **JWT Access Token:** 30 minutes
- **JWT Refresh Token:** 30 days
- **API Keys:** Configurable expiration (default: no expiry)

### Alternatives Considered

**Option 1:** JWT only
- **Rejected:** Awkward for external systems (need refresh tokens)

**Option 2:** API keys only
- **Rejected:** Not ideal for web users (no auto-expiry)

**Option 3:** OAuth 2.0
- **Rejected:** Over-engineering for current needs

---

## ADR-005: Multi-Platform AI Support with Fallback

**Date:** November 15, 2024  
**Status:** ✅ ACCEPTED  
**Deciders:** Development Team  
**Phase:** 3 (AI Platform Integration)

### Context
Depends on AI APIs (OpenAI, Claude, Gemini). Single provider = vendor lock-in, downtime risk.

### Decision
Support multiple AI platforms with automatic fallback mechanism.

**Rationale:**
- **Reliability:** If OpenAI is down, fallback to Claude
- **Cost Optimization:** Choose cheapest platform for task
- **Vendor Independence:** Not locked to one provider
- **Flexibility:** Can add new platforms easily

### Implementation
- **BaseAdapter:** Abstract interface all adapters implement
- **AdapterRegistry:** Central platform registration
- **FallbackHandler:** Automatic retry with different platforms
- **CostTracker:** Track spend per platform

### Consequences

**Positive:**
- 99.9%+ uptime (multiple platforms reduce downtime)
- Cost flexibility (use cheaper platform when possible)
- Future-proof (easy to add new AI providers)

**Negative:**
- More complex code (adapter pattern)
- Must maintain 3+ platform integrations
- Prompt engineering may differ per platform

### Supported Platforms (as of Dec 2024)
1. **OpenAI:** GPT-3.5, GPT-4, GPT-4-Turbo
2. **Anthropic:** Claude 3 (Opus, Sonnet, Haiku)
3. **Google:** Gemini Pro, Gemini Flash

### Alternatives Considered

**Option 1:** OpenAI only
- **Rejected:** Vendor lock-in, downtime risk

**Option 2:** LangChain
- **Rejected:** Heavyweight dependency, want more control

---

## ADR-006: Celery for Async Task Processing

**Date:** October 20, 2024  
**Status:** ✅ ACCEPTED  
**Deciders:** Development Team  
**Phase:** 0 (Project Foundation)

### Context
Need to run long-running tasks (AI calls, workflows) asynchronously without blocking API requests.

### Decision
Use Celery with Redis as message broker.

**Rationale:**
- **Django Standard:** De facto async solution for Django
- **Reliability:** Battle-tested, handles retries
- **Monitoring:** Flower for task monitoring
- **Distributed:** Can scale workers horizontally

### Consequences

**Positive:**
- API requests return immediately
- Can retry failed tasks
- Can prioritize tasks
- Worker scalability

**Negative:**
- Additional infrastructure (Redis)
- More complex debugging
- Must handle task failures gracefully

### Configuration
- **Broker:** Redis
- **Result Backend:** Database (Django ORM)
- **Task Time Limit:** 5 minutes default
- **Max Retries:** 3

### Alternatives Considered

**Option 1:** Django-background-tasks
- **Rejected:** Less mature, fewer features

**Option 2:** RQ (Redis Queue)
- **Rejected:** Celery more feature-rich

**Option 3:** Kafka + custom workers
- **Rejected:** Over-engineering

---

## ADR-007: React + TypeScript for Frontend

**Date:** November hint 30, 2024  
**Status:** ✅ ACCEPTED (Planned for Phase 9)  
**Deciders:** Development Team  
**Phase:** 9 (Frontend Foundation)

### Context
Need modern frontend framework for responsive, interactive UI.

### Decision
React 18 + TypeScript + Tailwind CSS + Shadcn/UI

**Rationale:**
- **React:** Most popular, huge ecosystem, component-based
- **TypeScript:** Type safety prevents bugs, better IDE support
- **Tailwind:** Utility-first CSS, rapid development
- **Shadcn/UI:** Beautiful components, accessible, customizable

### Consequences

**Positive:**
- Modern, responsive UI
- Type safety across stack (Python types + TypeScript)
- Fast development with Tailwind utilities
- Rich component library (Shadcn)

**Negative:**
- Learning curve for Tailwind
- Build step complexity
- Bundle size management needed

### Alternatives Considered

**Option 1:** Vue.js
- **Rejected:** React has larger talent pool

**Option 2:** Angular
- **Rejected:** Too opinionated, heavyweight

**Option 3:** Svelte
- **Rejected:** Smaller ecosystem

---

## ADR Template

Use this template for future decisions:

```markdown
## ADR-XXX: Decision Title

**Date:** YYYY-MM-DD  
**Status:** PROPOSED | ACCEPTED | REJECTED | DEPRECATED  
**Deciders:** Who decided  
**Phase:** Which phase

### Context
What problem are we solving? Why does this decision matter?

### Decision
What did we decide to do?

### Rationale
Why did we make this decision? List key reasons.

### Consequences

**Positive:**
- What benefits does this bring?

**Negative:**
- What downsides or tradeoffs?

**Mitigation:**
- How do we address the negatives?

### Alternatives Considered

**Option 1:** Description
- **Rejected:** Why not this one?

**Option 2:** Description
- **Rejected:** Why not this one?

### Follow-up
- Any open questions?
- When to revisit?
```

---

*Add new decisions as they're made!*  
*Update status if decision is revisited or deprecated.*
