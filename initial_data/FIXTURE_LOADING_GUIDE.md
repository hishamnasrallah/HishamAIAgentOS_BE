# Fixture Loading Guide - حل مشاكل تحميل البيانات

This guide helps you resolve common issues when loading fixtures into a database that already has data.

---

## 🚨 Common Issues

### Issue 1: User Already Exists

**Error:**
```
IntegrityError: UNIQUE constraint failed: users.username
```

**Cause:** The fixture contains a user that already exists in your database (e.g., created via `setup_admin_user`).

**Solutions:**

#### Solution A: Skip User Data (Recommended)

```bash
# 1. Export fixtures without users
python manage.py export_initial_data --exclude-users

# 2. Load fixtures (skip authentication.json)
python manage.py loaddata initial_data/fixtures/integrations.json
python manage.py loaddata initial_data/fixtures/agents.json
python manage.py loaddata initial_data/fixtures/commands.json
python manage.py loaddata initial_data/fixtures/projects.json
python manage.py loaddata initial_data/fixtures/workflows.json
```

#### Solution B: Clear Database First (⚠️ Deletes All Data)

```bash
# WARNING: This deletes ALL existing data!
python manage.py flush --noinput
python manage.py migrate
python manage.py setup_admin_user

# ⚠️ IMPORTANT: Skip authentication.json because setup_admin_user already created "admin" user
python manage.py loaddata initial_data/fixtures/integrations.json
python manage.py loaddata initial_data/fixtures/agents.json
python manage.py loaddata initial_data/fixtures/commands.json
python manage.py loaddata initial_data/fixtures/projects.json
python manage.py loaddata initial_data/fixtures/workflows.json
# DO NOT load: initial_data/fixtures/authentication.json
```

#### Solution C: Edit Fixture Files

1. Open `initial_data/fixtures/authentication.json`
2. Find the user entry
3. Either:
   - Delete the user entry, OR
   - Change the username/email to something unique

---

### Issue 2: Foreign Key References Missing Users

**Error:**
```
IntegrityError: The row in table 'projects' has an invalid foreign key: 
projects.owner_id contains a value 'xxx' that does not have a corresponding value in users.id
```

**Cause:** Projects/workflows reference user IDs that don't exist in your database.

**Solutions:**

#### Solution A: Edit Fixture to Use Your User ID

1. Get your user ID:
   ```bash
   python manage.py shell
   ```
   ```python
   from apps.authentication.models import User
   user = User.objects.first()
   print(user.id)  # Copy this UUID
   ```

2. Edit the fixture file (e.g., `projects.json`):
   - Find all `"owner_id": "xxx"` entries
   - Replace with your user ID: `"owner_id": "your-user-id-here"`
   - Save the file

3. Load the fixture:
   ```bash
   python manage.py loaddata initial_data/fixtures/projects.json
   ```

#### Solution B: Skip Projects/Workflows

```bash
# Load only non-user-dependent fixtures
python manage.py loaddata initial_data/fixtures/integrations.json
python manage.py loaddata initial_data/fixtures/agents.json
python manage.py loaddata initial_data/fixtures/commands.json

# Skip projects.json and workflows.json
# Create projects/workflows manually via admin or API
```

---

### Issue 3: Foreign Key References Missing Agents

**Error:**
```
IntegrityError: The row in table 'command_templates' has an invalid foreign key: 
command_templates.recommended_agent_id contains a value 'xxx' that does not have a corresponding value in agents.id
```

**Cause:** Commands reference agent IDs that don't exist.

**Solutions:**

#### Solution A: Load Agents First

```bash
# 1. Load agents first
python manage.py loaddata initial_data/fixtures/agents.json

# 2. Then load commands
python manage.py loaddata initial_data/fixtures/commands.json
```

#### Solution B: Create Agents First

```bash
# 1. Create default agents
python scripts/create_default_agents.py

# 2. Then load commands
python manage.py loaddata initial_data/fixtures/commands.json
```

#### Solution C: Edit Fixture to Remove Agent References

1. Open `initial_data/fixtures/commands.json`
2. Find entries with `"recommended_agent_id": "xxx"`
3. Change to `"recommended_agent_id": null`
4. Save and reload

---

### Issue 4: Fixture File Not Found

**Error:**
```
CommandError: No fixture named 'core' found.
```

**Cause:** Not all apps export fixtures. Some apps (like `core`) may not have fixtures.

**Solution:** Skip missing fixtures. Only load fixtures that exist:

```bash
# Check which fixtures exist
ls initial_data/fixtures/

# Load only existing fixtures
python manage.py loaddata initial_data/fixtures/integrations.json
python manage.py loaddata initial_data/fixtures/agents.json
# ... etc
```

---

## 📋 Recommended Loading Order

When loading fixtures, follow this order:

1. **Integrations** (`integrations.json`) - No dependencies
2. **Agents** (`agents.json`) - No dependencies (or create via script)
3. **Commands** (`commands.json`) - Depends on agents
4. **Projects** (`projects.json`) - Depends on users
5. **Workflows** (`workflows.json`) - Depends on users
6. **Other** - Chat, results, monitoring (optional)

**⚠️ Skip `authentication.json` if you have existing users!**

---

## 🔧 Complete Workflow for Existing Database

If you have an existing database with users:

```bash
# Step 1: Export without users (if not already done)
python manage.py export_initial_data --exclude-users

# Step 2: Load fixtures in order (skip authentication.json)
python manage.py loaddata initial_data/fixtures/integrations.json
python manage.py loaddata initial_data/fixtures/agents.json
python manage.py loaddata initial_data/fixtures/commands.json

# Step 3: For projects/workflows, either:
# Option A: Edit fixture files to use your user IDs
# Option B: Skip them and create manually
# Option C: Use the link_commands_to_agents command instead
python manage.py link_commands_to_agents
```

---

## 💡 Best Practices

1. **Always export without users** when creating templates:
   ```bash
   python manage.py export_initial_data --exclude-users
   ```

2. **Load fixtures one by one** to identify issues early:
   ```bash
   python manage.py loaddata initial_data/fixtures/integrations.json
   # Check for errors, then continue...
   ```

3. **Use scripts instead of fixtures** when possible:
   ```bash
   python scripts/create_default_agents.py
   python manage.py create_commands
   python manage.py link_commands_to_agents
   ```

4. **Keep fixture files small** - Export only what you need:
   ```bash
   python manage.py export_initial_data --apps agents commands
   ```

---

## 🆘 Still Having Issues?

1. **Check fixture file format:**
   ```bash
   # Validate JSON
   python -m json.tool initial_data/fixtures/agents.json > /dev/null
   ```

2. **Check database state:**
   ```bash
   python manage.py shell
   ```
   ```python
   from apps.authentication.models import User
   from apps.agents.models import Agent
   print(f"Users: {User.objects.count()}")
   print(f"Agents: {Agent.objects.count()}")
   ```

3. **Clear and start fresh:**
   ```bash
   python manage.py flush --noinput
   python manage.py migrate
   python manage.py setup_admin_user
   # Then load fixtures
   ```

---

**Last Updated:** December 7, 2024  
**For more help, see:** `initial_data/README.md`

