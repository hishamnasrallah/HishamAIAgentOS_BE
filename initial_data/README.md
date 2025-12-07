---
title: Initial Data - Database Fixtures
description: Database fixtures and export/import tools for HishamOS initial data

category: Development
subcategory: Database
language: en
original_language: en

purpose: |
  This directory contains database fixtures and tools for exporting/importing
  initial data from/to the HishamOS database. Useful for setting up new
  environments, backups, and data migration.

target_audience:
  primary:
    - Developer
    - DevOps
  secondary:
    - Technical Lead

applicable_phases:
  primary:
    - Development
    - Deployment
  secondary:
    - Testing

tags:
  - database
  - fixtures
  - initial-data
  - backup
  - export
  - import

status: active
priority: high
difficulty: intermediate
completeness: 100%

estimated_read_time: 10 minutes

version: 1.0
last_updated: 2024-12-06
last_reviewed: 2024-12-06
review_frequency: quarterly
next_review_date: 2025-03-06

author: Development Team
maintainer: Development Team
reviewer: Technical Lead

related:
  - backend/INSTALLATION_GUIDE.md
see_also: []
depends_on: []
prerequisite_for: []

aliases:
  - "Database Fixtures"
  - "Initial Data"

changelog:
  - version: "1.0"
    date: "2024-12-06"
    changes: "Initial initial data directory and tools"
    author: "Development Team"
---

# Initial Data - Database Fixtures

This directory contains database fixtures and tools for exporting/importing initial data from/to the HishamOS database.

---

## 📁 Directory Structure

```
initial_data/
├── README.md                          # This file
├── __init__.py                        # Package initialization
├── fixtures/                          # Exported fixture files (JSON)
│   ├── agents.json
│   ├── commands.json
│   ├── projects.json
│   ├── workflows.json
│   ├── integrations.json
│   └── ...
└── scripts/                           # Helper scripts
    └── export_all_data.py            # Export script
```

---

## 🚀 Quick Start

### Export All Data from Database

```bash
# From backend directory
python manage.py export_initial_data

# Or with custom output directory
python manage.py export_initial_data --output initial_data/fixtures/

# Export specific apps only
python manage.py export_initial_data --apps agents commands
```

### Import Data from Fixtures

```bash
# Import all fixtures
python manage.py loaddata initial_data/fixtures/*.json

# Import specific fixture
python manage.py loaddata initial_data/fixtures/agents.json
```

---

## 📋 What Gets Exported

The export command exports data from the following Django apps:

### Core Models
- **Authentication**: Users, API Keys
- **Agents**: Agent definitions, Agent executions
- **Commands**: Command categories, Command templates
- **Projects**: Projects, Sprints, Epics, User Stories, Tasks
- **Workflows**: Workflows, Workflow executions, Workflow steps
- **Integrations**: AI Platforms, Platform usage
- **Core**: System settings, Feature flags
- **Monitoring**: System metrics, Health checks, Audit logs
- **Chat**: Conversations, Messages
- **Results**: Results, Result feedback

### Excluded Models
- **Audit logs** (by default, use `--include-audit` to include)
- **System metrics** (by default, use `--include-metrics` to include)
- **Execution histories** (by default, use `--include-histories` to include)

---

## 🔧 Management Command

### Export Command

```bash
python manage.py export_initial_data [options]
```

#### Options

- `--output DIR` - Output directory for fixtures (default: `initial_data/fixtures/`)
- `--apps APP1 APP2` - Export only specific apps
- `--format FORMAT` - Output format: `json` (default), `xml`
- `--indent N` - JSON indentation level (default: 2)
- `--exclude-empty` - Skip empty fixtures (default: True)
- `--include-audit` - Include audit logs
- `--include-metrics` - Include system metrics
- `--include-histories` - Include execution histories
- `--exclude-users` - Exclude user data (useful for templates)

#### Examples

```bash
# Export all data
python manage.py export_initial_data

# Export only agents and commands
python manage.py export_initial_data --apps agents commands

# Export with audit logs
python manage.py export_initial_data --include-audit

# Export without user data (for templates)
python manage.py export_initial_data --exclude-users
```

---

## 📦 Importing Fixtures

### Using Django's loaddata

```bash
# Load all fixtures
python manage.py loaddata initial_data/fixtures/*.json

# Load specific fixtures in order
python manage.py loaddata \
    initial_data/fixtures/core.json \
    initial_data/fixtures/integrations.json \
    initial_data/fixtures/agents.json \
    initial_data/fixtures/commands.json

# Load with verbosity
python manage.py loaddata initial_data/fixtures/*.json --verbosity 2
```

### Order Matters!

When importing, load fixtures in this order:

1. **Core** (`core.json`) - System settings, feature flags
2. **Integrations** (`integrations.json`) - AI platforms
3. **Agents** (`agents.json`) - Agent definitions
4. **Commands** (`commands.json`) - Command templates (depends on agents)
5. **Projects** (`projects.json`) - Projects and related data
6. **Workflows** (`workflows.json`) - Workflows
7. **Other** - Monitoring, chat, results (optional)

---

## 🔒 Security Considerations

### Sensitive Data

**⚠️ Important:** Fixtures may contain sensitive data:

- **API Keys** - Encrypted in database, but exported in fixtures
- **User Passwords** - Hashed, but still sensitive
- **User Data** - Personal information

### Best Practices

1. **Never commit fixtures with real data** to version control
2. **Use `.gitignore`** to exclude fixture files:
   ```
   initial_data/fixtures/*.json
   !initial_data/fixtures/.gitkeep
   ```
3. **Create template fixtures** without sensitive data:
   ```bash
   python manage.py export_initial_data --exclude-users --output initial_data/fixtures/templates/
   ```
4. **Encrypt fixtures** if storing sensitive data

---

## 📝 Example Workflow

### 1. Export Current Database

```bash
# Export all data from current database
python manage.py export_initial_data --output initial_data/fixtures/backup_2024-12-06/
```

### 2. Create Template Fixtures

```bash
# Export without sensitive data for templates
python manage.py export_initial_data \
    --exclude-users \
    --output initial_data/fixtures/templates/
```

### 3. Set Up New Environment

```bash
# 1. Run migrations
python manage.py migrate

# 2. Load template fixtures
python manage.py loaddata initial_data/fixtures/templates/*.json

# 3. Create admin user
python manage.py setup_admin_user

# 4. Create default agents (if not in fixtures)
python scripts/create_default_agents.py
```

---

## 🛠️ Troubleshooting

### Issue: Foreign Key Constraints

**Error:** `IntegrityError: FOREIGN KEY constraint failed`

**Solution:** Load fixtures in the correct order (see "Order Matters!" section above).

### Issue: Duplicate Key Errors

**Error:** `IntegrityError: UNIQUE constraint failed`

**Solution:** 
- Clear existing data before loading:
  ```bash
  python manage.py flush --noinput
  python manage.py migrate
  python manage.py loaddata initial_data/fixtures/*.json
  ```

### Issue: Encrypted API Keys

**Note:** API keys are encrypted in the database. If you're importing fixtures with encrypted keys:
- Ensure the `ENCRYPTION_KEY` environment variable matches
- Or re-enter API keys manually after import

---

## 📚 Related Documentation

- **Installation Guide**: `../INSTALLATION_GUIDE.md`
- **Django Fixtures**: https://docs.djangoproject.com/en/stable/topics/serialization/
- **Management Commands**: https://docs.djangoproject.com/en/stable/howto/custom-management-commands/

---

**Last Updated:** December 6, 2024  
**Version:** 1.0  
**Maintained By:** Development Team

