---
title: Documentation Standards and Guidelines
description: Comprehensive standards and guidelines for creating and updating documentation in HishamOS. All new documents MUST follow these standards.

category: Core
subcategory: Standards
language: en
original_language: en

purpose: |
  This document establishes the mandatory standards for all documentation in HishamOS. It ensures consistency, discoverability, and maintainability across all documentation files.

target_audience:
  primary:
    - Technical Writer
    - Developer
  secondary:
    - AI Agent
    - Project Manager
    - CTO / Technical Lead

applicable_phases:
  primary:
    - All
  secondary: []

tags:
  - documentation
  - standards
  - guidelines
  - metadata
  - yaml
  - frontmatter
  - writing
  - quality
  - consistency
  - discoverability

status: active
priority: critical
difficulty: beginner
completeness: 100%

estimated_read_time: 15 minutes

version: 1.0
last_updated: 2024-12-06
last_reviewed: 2024-12-06
review_frequency: quarterly
next_review_date: 2025-03-06

author: Documentation Team
maintainer: Documentation Team
reviewer: Technical Lead

related:
  - 05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md
  - 05_DEVELOPMENT/MASTER_DEVELOPMENT_GUIDE.md
see_also:
  - DOCUMENTATION_WRITING_GUIDELINES.md
depends_on: []
prerequisite_for:
  - 05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md

aliases:
  - "Documentation Guidelines"
  - "Doc Standards"
  - "Writing Standards"

changelog:
  - version: "1.0"
    date: "2024-12-06"
    changes: "Initial version after documentation reorganization"
    author: "Documentation Team"
---

# Documentation Standards and Guidelines

**⚠️ MANDATORY:** All new and updated documentation MUST follow these standards.

---

## 📋 Quick Reference

### Creating a New Document

1. **Choose the right location** based on category
2. **Copy the template** from `01_CORE/DOCUMENTATION_WRITING_GUIDELINES.md`
3. **Fill ALL mandatory metadata fields**
4. **Write content** following structure guidelines
5. **Verify YAML** frontmatter is valid
6. **Test links** before saving

### Updating an Existing Document

1. **Read the document** fully
2. **Increment version** (1.0 → 1.1)
3. **Update last_updated** date
4. **Add changelog entry**
5. **Update content** as needed
6. **Update related/depends_on** if structure changed

---

## ✅ Mandatory Metadata Fields

Every document MUST include:

### Required Fields

- ✅ `title` - Clear, descriptive title
- ✅ `description` - 2-3 sentence summary
- ✅ `category` - One of: Core, Design, Testing, Development, Deployment, Planning, Tracking, Commands, Phases
- ✅ `language` - ar, en, or both
- ✅ `purpose` - 1-2 paragraph explanation
- ✅ `target_audience` - Primary (1-2 roles) + Secondary (multiple)
- ✅ `applicable_phases` - Primary + Secondary phases
- ✅ `tags` - Minimum 10 comprehensive tags
- ✅ `status` - active, draft, or deprecated
- ✅ `version` - Semantic versioning (e.g., 1.0)
- ✅ `last_updated` - Date in YYYY-MM-DD format
- ✅ `author` - Author name/team
- ✅ `changelog` - Array of version history

### Recommended Fields

- ⭐ `subcategory` - More specific categorization
- ⭐ `related` - Links to related documents
- ⭐ `see_also` - Additional references
- ⭐ `depends_on` - Prerequisite documents
- ⭐ `prerequisite_for` - Documents that depend on this
- ⭐ `aliases` - Alternative names for search
- ⭐ `keywords` - Search keywords
- ⭐ `estimated_read_time` - Reading time estimate

---

## 📝 Metadata Examples

### Example 1: Development Guide

```yaml
---
title: "API Development Guide"
description: "Complete guide for developing REST API endpoints in HishamOS backend. Includes authentication, serialization, and testing."

category: Development
subcategory: API
language: en

purpose: |
  This guide provides step-by-step instructions for developing new API endpoints,
  including authentication, request validation, error handling, and testing.

target_audience:
  primary:
    - Developer
  secondary:
    - Technical Lead
    - QA / Tester

applicable_phases:
  primary:
    - Development
  secondary:
    - Testing

tags:
  - api
  - development
  - backend
  - django
  - rest
  - endpoints
  - authentication
  - serialization
  - testing
  - guide

status: active
priority: high
difficulty: intermediate
completeness: 100%

version: 1.0
last_updated: 2024-12-06
author: Development Team
changelog:
  - version: "1.0"
    date: "2024-12-06"
    changes: "Initial version"
    author: "Development Team"
---
```

### Example 2: Testing Checklist

```yaml
---
title: "Phase 13-14 Manual Testing Checklist"
description: "Comprehensive manual testing checklist for chat interface and agent management features implemented in phases 13 and 14."

category: Testing
subcategory: Manual Testing
language: en

purpose: |
  This checklist ensures all features from phases 13-14 are thoroughly tested
  before marking the phase as complete.

target_audience:
  primary:
    - QA / Tester
  secondary:
    - Developer
    - Project Manager

applicable_phases:
  primary:
    - Testing
  secondary:
    - Development

tags:
  - testing
  - manual-testing
  - checklist
  - phase-13
  - phase-14
  - chat-interface
  - agent-management
  - qa
  - verification
  - sign-off

status: active
priority: critical
difficulty: beginner
completeness: 100%

version: 1.0
last_updated: 2024-12-06
author: QA Team
changelog:
  - version: "1.0"
    date: "2024-12-06"
    changes: "Initial checklist created"
    author: "QA Team"
---
```

---

## 🎯 Target Audience Roles

Use these standardized role names:

### Primary Roles (choose 1-2):
- `Developer`
- `QA / Tester`
- `Project Manager`
- `Business Analyst`
- `CTO / Technical Lead`
- `Technical Writer`
- `DevOps`
- `Infrastructure`
- `Scrum Master`

### Secondary Roles (can have multiple):
- Any of the above roles
- `General` (only if truly applicable to all)

**Important:** 
- Primary roles should be the main audience (1-2 roles)
- Secondary roles should be those who also benefit but aren't primary
- Be realistic and accurate - don't use "All" unless truly applicable

---

## 🔄 Applicable Phases

Use these standardized phase names:

### Primary Phases:
- `Development`
- `Testing`
- `Planning`
- `Deployment`
- `Business Gathering`
- `QA`
- `All` (only if applicable to all phases)

### Secondary Phases:
- Any of the above
- Can have multiple

---

## 📍 Document Categories and Structure

### Category: Core (`01_CORE/`)
- Status reports
- Indexes
- User guides
- Admin documentation
- Summaries

### Category: Design (`02_DESIGN/`)
- Architecture documents
- UI/UX designs
- Design specifications
- Roadmaps
- Gaps analysis

### Category: Testing (`03_TESTING/`)
- Test checklists
- Test guides
- UAT documentation
- Test execution results
- Testing strategies

### Category: Development (`05_DEVELOPMENT/`)
- Development guides
- Code standards
- Implementation guides
- Verification checklists
- Documentation maintenance

### Category: Deployment (`04_DEPLOYMENT/`)
- Deployment guides
- Infrastructure documentation
- Production setup
- Docker/container guides

### Category: Planning (`06_PLANNING/`)
- Project plans
- Technical architecture
- User stories
- Implementation plans
- BA artifacts

### Category: Tracking (`07_TRACKING/`)
- Status summaries
- Roadmaps
- Blockers
- Changelog
- Comprehensive audit
- Task tracking

### Category: Commands (`08_COMMANDS/`)
- Command library documentation
- Command testing guides
- Command usage examples

### Category: Phases (`09_PHASES/`)
- Phase-specific documentation
- Expected outputs
- Phase implementation plans

---

## 🔍 Tag Guidelines

Tags should be:
- **Comprehensive** - Minimum 10 tags
- **Relevant** - Related to document content
- **Searchable** - Use terms people would search for
- **Standardized** - Use consistent terminology

### Tag Categories:
- **Topic tags**: api, testing, development, deployment
- **Technology tags**: django, react, docker, postgresql
- **Feature tags**: authentication, commands, workflows
- **Role tags**: developer, qa, pm (if role-specific)
- **Type tags**: guide, checklist, reference, tutorial
- **Phase tags**: phase-13, phase-14 (if phase-specific)
- **Status tags**: active, draft, deprecated

---

## ⚠️ Common Mistakes to Avoid

### ❌ Don't:
1. Skip metadata fields
2. Use "All" for target_audience unless truly applicable
3. Use generic tags (fewer than 10)
4. Forget to increment version when updating
5. Skip changelog entries
6. Use incorrect category
7. Forget to update last_updated date
8. Create documents without YAML frontmatter

### ✅ Do:
1. Fill ALL mandatory fields
2. Use specific, accurate roles
3. Include 10+ comprehensive tags
4. Increment version for each update
5. Add changelog entry for every change
6. Use correct category
7. Update dates when modifying
8. Validate YAML syntax before saving

---

## 📚 Reference Documents

### Primary References:
- `01_CORE/DOCUMENTATION_WRITING_GUIDELINES.md` - Complete writing guide
- `05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md` - Maintenance instructions
- `05_DEVELOPMENT/MASTER_DEVELOPMENT_GUIDE.md` - Development guide

### Examples:
- Check existing documentation files for metadata examples
- Review files in same category for consistency

---

## 🚀 Quick Start Checklist

Before creating or updating any document:

- [ ] ✅ Read `01_CORE/DOCUMENTATION_WRITING_GUIDELINES.md`
- [ ] ✅ Understand metadata requirements
- [ ] ✅ Chose correct category and location
- [ ] ✅ Prepared all required metadata
- [ ] ✅ Validated YAML syntax
- [ ] ✅ Checked existing similar documents for format
- [ ] ✅ Prepared content outline
- [ ] ✅ Verified all links work

---

**Last Updated:** December 6, 2024  
**Version:** 1.0  
**Maintained By:** Documentation Team

