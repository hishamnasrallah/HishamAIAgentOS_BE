# Command Library Initialization Guide

This guide shows you all the commands and files needed to initialize the command library data.

## 📁 Initial Data Files

### Fixture File (JSON)
- **Location:** `backend/initial_data/fixtures/commands.json`
- **Contains:** Pre-exported command categories and templates
- **Usage:** Load using `python manage.py load_initial_data`

## 🔧 Management Commands

### Option 1: Load from Fixtures (Fastest - Recommended)

If you have the fixture file, use this method:

```bash
cd backend
python manage.py load_initial_data
```

This will load all fixtures including commands, agents, workflows, etc. in the correct order.

**Note:** Make sure you have:
- Run migrations: `python manage.py migrate`
- Created admin user: `python manage.py setup_admin_user`

---

### Option 2: Create Commands Programmatically (Step by Step)

If you want to create commands from scratch or expand the library, use these commands in order:

#### Step 1: Create Base Commands (Creates categories + initial commands)

```bash
cd backend
python manage.py create_commands
```

**What it does:**
- Creates all 12 command categories
- Creates initial set of commands (typically ~148-229 commands)
- Links commands to categories

#### Step 2: Expand to 250 Commands (Optional)

```bash
python manage.py add_commands_to_250
```

**What it does:**
- Adds 21 more commands to reach 250 total
- Distributes across various categories

#### Step 3: Expand to 325 Commands (Optional - Full Library)

```bash
python manage.py add_remaining_96_commands
```

**What it does:**
- Adds remaining 96 commands to reach 325 total
- Completes the full command library

#### Step 4: Link Commands to Agents (Recommended)

```bash
python manage.py link_commands_to_agents
```

**What it does:**
- Links commands to recommended agents based on capabilities
- Matches commands with appropriate agents (coding-agent, code-reviewer, etc.)

---

## ✅ Verification Commands

### Check Command Library Status

```bash
python manage.py verify_commands
```

**Shows:**
- Total commands count
- Commands by category
- Commands with/without agents
- Recent commands
- Statistics

### Test Command Endpoints

```bash
python manage.py test_command_endpoints
```

**Tests:**
- Command list endpoint
- Command detail endpoint
- Command preview endpoint
- Command execution endpoint

### Verify System

```bash
python manage.py verify_system
```

**Verifies:**
- All system components
- Database integrity
- Command relationships

---

## 📋 Complete Initialization Sequence

### For Fresh Installation:

```bash
cd backend

# 1. Run migrations
python manage.py migrate

# 2. Create admin user
python manage.py setup_admin_user

# 3. Load all initial data (including commands)
python manage.py load_initial_data

# OR if you prefer to create commands programmatically:

# 3a. Create base commands
python manage.py create_commands

# 3b. Link to agents
python manage.py link_commands_to_agents

# 3c. (Optional) Expand to 250
python manage.py add_commands_to_250

# 3d. (Optional) Expand to 325
python manage.py add_remaining_96_commands

# 4. Verify everything
python manage.py verify_commands
```

---

## 📊 Expected Results

After initialization, you should have:

- ✅ **12 Command Categories**
  - Requirements Engineering
  - Code Generation
  - Code Review
  - Testing & QA
  - DevOps & Deployment
  - Documentation
  - Project Management
  - Design & Architecture
  - Legal & Compliance
  - Business Analysis
  - UX/UI Design
  - Research & Analysis

- ✅ **148-325 Commands** (depending on which commands you ran)
  - All linked to categories
  - Many linked to recommended agents
  - With templates, parameters, and metadata

- ✅ **Command Executions** table ready for tracking

---

## 🔍 Troubleshooting

### If commands.json fixture fails to load:

1. Check that agents are loaded first:
   ```bash
   python manage.py loaddata initial_data/fixtures/agents.json
   ```

2. Then load commands:
   ```bash
   python manage.py loaddata initial_data/fixtures/commands.json
   ```

### If you get foreign key errors:

Make sure to load in this order:
1. `authentication.json` (users)
2. `integrations.json` (AI platforms)
3. `agents.json` (agents)
4. `commands.json` (commands)
5. `projects.json`
6. `workflows.json`

### If commands are created but not linked to agents:

Run the linking command:
```bash
python manage.py link_commands_to_agents
```

---

## 📝 Management Command Files

All command management files are located in:
- `backend/apps/commands/management/commands/`

**Available Commands:**
1. `create_commands.py` - Base command creation
2. `add_commands_to_250.py` - Expand to 250 commands
3. `add_remaining_96_commands.py` - Expand to 325 commands
4. `link_commands_to_agents.py` - Link commands to agents
5. `verify_commands.py` - Verify command library
6. `test_command_endpoints.py` - Test API endpoints
7. `test_commands.py` - Test command functionality
8. `verify_system.py` - System-wide verification

---

## 🎯 Quick Start (Recommended)

For fastest setup, use the fixture file:

```bash
cd backend
python manage.py migrate
python manage.py setup_admin_user
python manage.py load_initial_data
python manage.py verify_commands
```

This will give you a fully initialized system with all commands, agents, workflows, and other data!

