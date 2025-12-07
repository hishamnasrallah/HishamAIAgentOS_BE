# Deployment-Ready Fixtures

This directory contains fixtures that are ready for deployment without manual intervention.

## ✅ What Makes These Fixtures Deployment-Ready?

1. **No User Data** - `authentication.json` is excluded to prevent conflicts
2. **Cleaned User References** - All user foreign keys are set to `null` or empty lists
3. **No Conflicts** - Can be loaded directly without errors

## 🚀 Usage

### Load All Deployment Fixtures (One Command)

```bash
# From backend directory - One command to load everything
python initial_data/scripts/load_deployment_fixtures.py
```

This script will:
- Load all fixtures in the correct order
- Show progress for each file
- Display a summary of loaded fixtures

### Load Manually

```bash
# From backend directory
python manage.py loaddata initial_data/fixtures/deployment/*.json
```

### Load Specific Fixtures

```bash
# Load in order
python manage.py loaddata initial_data/fixtures/deployment/integrations.json
python manage.py loaddata initial_data/fixtures/deployment/agents.json
python manage.py loaddata initial_data/fixtures/deployment/commands.json
python manage.py loaddata initial_data/fixtures/deployment/projects.json
python manage.py loaddata initial_data/fixtures/deployment/workflows.json
```

## 📦 How to Create Deployment Fixtures

### Option 1: One-Command Solution (Recommended)

```bash
python initial_data/scripts/prepare_and_export.py
```

This will:
1. Export all data (excluding users)
2. Clean all user references
3. Save to this directory

### Option 2: Manual Steps

```bash
# Step 1: Export without users
python manage.py export_initial_data --exclude-users

# Step 2: Prepare fixtures
python initial_data/scripts/prepare_fixtures.py
```

## ⚠️ Important Notes

- **User References**: All user foreign keys (owner, created_by, assigned_to, etc.) are set to `null`
- **ManyToMany Fields**: User-related ManyToMany fields (like `members`) are set to empty lists
- **After Loading**: You may need to manually assign projects/workflows to users via admin or API

## 🔄 Updating Deployment Fixtures

When you need to update these fixtures:

```bash
# Re-run the preparation script
python initial_data/scripts/prepare_and_export.py
```

This will overwrite existing files in this directory.

---

**Last Updated:** December 7, 2024  
**Maintained By:** Development Team

