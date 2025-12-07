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

### Export and Prepare Fixtures for Deployment (Recommended)

**One-command solution for deployment-ready fixtures:**

```bash
# Export and prepare fixtures in one step (excludes users, cleans references)
python initial_data/scripts/prepare_and_export.py
```

This will:
1. Export all data (excluding users)
2. Clean all user references in fixtures
3. Save deployment-ready fixtures to `initial_data/fixtures/deployment/`

### Export All Data from Database

```bash
# From backend directory
python manage.py export_initial_data

# Export for deployment (excludes users automatically)
python manage.py export_initial_data --prepare-for-deployment

# Or with custom output directory
python manage.py export_initial_data --output initial_data/fixtures/

# Export specific apps only
python manage.py export_initial_data --apps agents commands
```

### Prepare Existing Fixtures for Deployment

If you already have fixtures and want to make them deployment-ready:

```bash
# Clean user references from existing fixtures
python initial_data/scripts/prepare_fixtures.py
```

This will:
- Remove `authentication.json` (user data)
- Clean all user references (set to `null` or empty lists)
- Save cleaned fixtures to `initial_data/fixtures/deployment/`

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

### Using Deployment Fixtures (Recommended - One Command)

```bash
# Load deployment-ready fixtures (prepared, no conflicts)
python initial_data/scripts/load_deployment_fixtures.py
```

This script:
- Loads all fixtures from `initial_data/fixtures/deployment/`
- Loads fixtures in the correct order automatically
- Shows progress and summary
- No user conflicts (already cleaned)

**To prepare deployment fixtures first:**
```bash
python initial_data/scripts/prepare_and_export.py
```

### Using Safe Loading Script

```bash
# Automatically handles user conflicts
python initial_data/scripts/load_fixtures_safe.py
```

This script:
- Checks if users exist in the database
- Automatically skips `authentication.json` if users are found
- Loads all other fixtures in the correct order
- Shows a summary of loaded fixtures

### Using Django's loaddata

```bash
# Load all fixtures (⚠️ May fail if users exist)
python manage.py loaddata initial_data/fixtures/*.json

# Load specific fixtures in order
python manage.py loaddata \
    initial_data/fixtures/integrations.json \
    initial_data/fixtures/agents.json \
    initial_data/fixtures/commands.json

# Load with verbosity
python manage.py loaddata initial_data/fixtures/*.json --verbosity 2
```

### Order Matters!

When importing, load fixtures in this order:

1. **Authentication** (`authentication.json`) - Users (⚠️ Skip if you have existing users)
2. **Integrations** (`integrations.json`) - AI platforms
3. **Agents** (`agents.json`) - Agent definitions
4. **Commands** (`commands.json`) - Command templates (depends on agents)
5. **Projects** (`projects.json`) - Projects and related data (depends on users)
6. **Workflows** (`workflows.json`) - Workflows (depends on users)
7. **Other** - Monitoring, chat, results (optional)

**⚠️ Important:** If you already have users in your database:
- **Skip** `authentication.json` when loading
- Projects and workflows may reference users that don't exist
- Either edit fixture files to use your existing user IDs, or skip those fixtures

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

**Option A: Fresh Database (No existing users)**

```bash
# 1. Run migrations
python manage.py migrate

# 2. Create admin user first
python manage.py setup_admin_user

# 3. Load fixtures (skip authentication.json if it conflicts)
python manage.py loaddata initial_data/fixtures/integrations.json
python manage.py loaddata initial_data/fixtures/agents.json
python manage.py loaddata initial_data/fixtures/commands.json
# Skip projects/workflows if they reference users that don't match

# 4. Create default agents (if not in fixtures)
python scripts/create_default_agents.py
```

**Option B: Existing Database (Has users)**

```bash
# 1. Export without users first (if not already done)
python manage.py export_initial_data --exclude-users

# 2. Load fixtures (skip authentication.json)
python manage.py loaddata initial_data/fixtures/integrations.json
python manage.py loaddata initial_data/fixtures/agents.json
python manage.py loaddata initial_data/fixtures/commands.json

# 3. For projects/workflows: Either skip them or edit fixture files to use your user IDs
```

---

## 🛠️ Troubleshooting

**For detailed troubleshooting guide, see:** [`FIXTURE_LOADING_GUIDE.md`](FIXTURE_LOADING_GUIDE.md)

### Issue: Foreign Key Constraints

**Error:** `IntegrityError: FOREIGN KEY constraint failed`

**Solution:** 
- Load fixtures in the correct order (see "Order Matters!" section above)
- Ensure all referenced objects exist (e.g., users before projects, agents before commands)
- If loading into existing database, ensure referenced IDs match existing records

### Issue: Duplicate Key Errors (Users)

**Error:** `IntegrityError: UNIQUE constraint failed: users.username` or `users.email`

**Cause:** Fixture contains users that already exist in your database.

**Solution 1: Exclude users when exporting (Recommended)**
```bash
# Export without user data
python manage.py export_initial_data --exclude-users

# Then load fixtures (skip authentication.json)
python manage.py loaddata initial_data/fixtures/integrations.json
python manage.py loaddata initial_data/fixtures/agents.json
# ... etc
```

**Solution 2: Clear database first (⚠️ Deletes all data)**
```bash
python manage.py flush --noinput
python manage.py migrate
python manage.py setup_admin_user
python manage.py loaddata initial_data/fixtures/*.json
```

**Solution 3: Edit fixture to use existing user IDs**
- Open the fixture file (e.g., `projects.json`)
- Find references to user IDs
- Replace with your existing user IDs
- Save and reload

### Issue: Duplicate Key Errors (Other Models)

**Error:** `IntegrityError: UNIQUE constraint failed: agents.agent_id`

**Solution:** 
- Clear existing data before loading:
  ```bash
  python manage.py flush --noinput
  python manage.py migrate
  python manage.py loaddata initial_data/fixtures/*.json
  ```
- Or skip the conflicting fixture and create data manually

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

