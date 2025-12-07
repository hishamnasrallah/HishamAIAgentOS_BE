---
title: Backend Installation Guide
description: Complete installation and setup guide for HishamOS Backend (Django REST API)

category: Development
subcategory: Setup
language: en
original_language: en

purpose: |
  This guide provides step-by-step instructions for installing and setting up the HishamOS backend
  as a standalone repository. Includes prerequisites, environment setup, database configuration,
  and verification steps.

target_audience:
  primary:
    - Developer
  secondary:
    - DevOps
    - Technical Lead

applicable_phases:
  primary:
    - Development
    - Deployment
  secondary: []

tags:
  - installation
  - setup
  - django
  - backend
  - api
  - python
  - database
  - environment

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

author: Development Team
maintainer: Development Team
reviewer: Technical Lead

related:
  - docs/04_DEPLOYMENT/DEPLOYMENT_INFRASTRUCTURE_SUMMARY.md
see_also:
  - frontend/INSTALLATION_GUIDE.md
  - infrastructure/INSTALLATION_GUIDE.md
depends_on: []
prerequisite_for: []

aliases:
  - "Setup Guide"
  - "Backend Setup"

changelog:
  - version: "1.0"
    date: "2024-12-06"
    changes: "Updated for standalone repository"
    author: "Development Team"
---

# HishamOS Backend - Installation Guide

Complete installation and setup guide for HishamOS Backend (Django REST API).

---

## 📋 Prerequisites

### Required Software

- **Python 3.11+** (3.13 recommended)
- **pip** (Python package manager)
- **Git** (version control)
- **SQLite** (default, included with Python)

### Optional (for production)

- **PostgreSQL 16+** (production database)
- **Redis 7+** (for caching and Celery)
- **Docker** (containerized deployment)

---

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/your-org/hishamos-backend.git
cd hishamos-backend

# 2. Create virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements/development.txt

# 4. Setup environment
# Copy .env.example to .env and configure

# 5. Run migrations
python manage.py migrate

# 6. Create admin user
python manage.py setup_admin_user

# 7. Run server
python manage.py runserver
# OR with WebSocket support:
daphne core.asgi:application --bind 0.0.0.0 --port 8000
```

**Default Admin Credentials:**
- Email: `admin@hishamos.com`
- Password: `Amman123`

**Access URLs:**
- API: http://localhost:8000/api/v1/
- Admin Panel: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/docs/

---

## 📦 Step-by-Step Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/hishamos-backend.git
cd hishamos-backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

**Note:** The virtual environment should be activated before proceeding.

### Step 3: Install Dependencies

```bash
# For development (recommended)
pip install -r requirements/development.txt

# For production
pip install -r requirements/production.txt

# Base only
pip install -r requirements/base.txt
```

**Requirements structure:**
- `requirements/base.txt` - Core dependencies
- `requirements/development.txt` - Base + development tools
- `requirements/production.txt` - Base + production tools

### Step 4: Environment Configuration

Create a `.env` file in the root directory (same level as `manage.py`):

```bash
# Copy example if exists
cp .env.example .env

# Or create manually
```

**Minimum `.env` configuration:**

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
DJANGO_DEBUG=True
# ALLOWED_HOSTS - Accepts all hosts by default (*)
# Can be restricted via: DJANGO_ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite - Default)
DATABASE_URL=sqlite:///db.sqlite3

# CORS - Allows all origins by default for flexibility
# Can be restricted via: CORS_ALLOW_ALL_ORIGINS=false
# Then specify: CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
CORS_ALLOW_ALL_ORIGINS=true
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Optional: AI Platform API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```

**Note:** The backend is configured to accept requests from any IP address by default:
- `ALLOWED_HOSTS = ['*']` (if not specified in `.env`)
- `CORS_ALLOW_ALL_ORIGINS = True` (allows requests from any origin)
- CSRF protection is disabled for API endpoints (uses JWT/API keys instead)

This allows you to:
- Access the backend from any IP (localhost, external IP, cloud platforms)
- Connect from Postman, frontend, or any other client
- Deploy without needing to modify settings for each environment

To restrict access later, set environment variables as shown above.

**Generate Django Secret Key:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 5: Database Setup

#### Option A: SQLite (Default - Development)

SQLite is configured by default. No additional setup required.

```bash
# Run migrations
python manage.py migrate
```

#### Option B: PostgreSQL (Production)

1. **Install PostgreSQL:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. **Create Database:**
   ```bash
   sudo -u postgres psql
   
   CREATE DATABASE hishamos_db;
   CREATE USER hishamos_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE hishamos_db TO hishamos_user;
   \q
   ```

3. **Update `.env`:**
   ```env
   DATABASE_URL=postgresql://hishamos_user:your_password@localhost:5432/hishamos_db
   ```

4. **Install PostgreSQL adapter:**
   ```bash
   pip install psycopg2-binary
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

### Step 6: Create Admin User

**Automatic Setup (Recommended):**

```bash
python manage.py setup_admin_user
```

Creates default admin:
- Email: `admin@hishamos.com`
- Password: `Amman123`
- Username: `admin`
- Role: `admin`

**Custom Credentials:**

```bash
python manage.py setup_admin_user \
    --email your-email@example.com \
    --password YourPassword123 \
    --username your-username
```

**Manual Setup:**

```bash
python manage.py createsuperuser
```

### Step 7: Load Initial Data (Recommended)

After running migrations, load initial data to populate the database with essential records.

**Important:** Execute these commands in order, as some depend on previous data.

```bash
# Step 1: Create default AI agents (Required for commands to work properly)
# Note: This is a Python script, not a management command
python scripts/create_default_agents.py

# Step 2: Load command templates (350+ commands across 12 categories)
python manage.py create_commands

# Step 3: Link commands to recommended agents based on capabilities
python manage.py link_commands_to_agents

# Step 4: Create sample workflows (optional, for testing)
python manage.py create_sample_workflows
```

**What Each Command Does:**

- **`create_default_agents`** - Creates 15+ default AI agents (Business Analyst, Coding Agent, QA Agent, DevOps Agent, etc.)
- **`create_commands`** - Loads 350+ command templates across 12 categories (Requirements, Code Generation, Testing, etc.)
- **`link_commands_to_agents`** - Links commands to their recommended agents based on capabilities
- **`create_sample_workflows`** - Creates example workflows for testing the workflow execution system

**Verify Data Loaded:**

```bash
python manage.py shell
```

```python
from apps.agents.models import Agent
from apps.commands.models import CommandTemplate, CommandCategory
from apps.workflows.models import Workflow

# Check agents
print(f"Agents: {Agent.objects.count()}")

# Check commands
print(f"Command Categories: {CommandCategory.objects.count()}")
print(f"Command Templates: {CommandTemplate.objects.count()}")

# Check workflows
print(f"Workflows: {Workflow.objects.count()}")
```

**Expected Results:**
- Agents: 15+ agents
- Command Categories: 12 categories
- Command Templates: 350+ commands
- Workflows: 0+ (only if you ran `create_sample_workflows`)

**Alternative: Manual Setup via Django Admin**

If scripts don't work, you can create data manually:
- Visit: http://localhost:8000/admin/
- Create agents, commands, and workflows via the admin interface

### Step 7.5: Export Database Data as Fixtures (Optional)

If you want to export all your current database data to JSON fixtures for backup, migration, or setting up new environments:

**🚀 Quick Export for Deployment (Recommended):**

```bash
# One command to export and prepare deployment-ready fixtures
python initial_data/scripts/prepare_and_export.py
```

This creates deployment-ready fixtures in `initial_data/fixtures/deployment/` that:
- Exclude user data (no conflicts)
- Have all user references cleaned (set to null)
- Can be loaded directly without manual intervention

**Manual Export Options:**

```bash
# Export all data to initial_data/fixtures/
python manage.py export_initial_data

# Export for deployment (excludes users, ready for prepare script)
python manage.py export_initial_data --prepare-for-deployment

# Export with custom output directory
python manage.py export_initial_data --output initial_data/fixtures/backup_2024-12-06/

# Export only specific apps
python manage.py export_initial_data --apps agents commands

# Export without user data (for templates)
python manage.py export_initial_data --exclude-users

# Include audit logs and metrics
python manage.py export_initial_data --include-audit --include-metrics
```

**Prepare Existing Fixtures:**

```bash
# Clean user references from existing fixtures
python initial_data/scripts/prepare_fixtures.py
```

**Import Data from Fixtures:**

**⚠️ Important:** If you already have a user in your database (e.g., created via `setup_admin_user`), you need to handle user conflicts.

**Option 1: Use Deployment-Ready Fixtures (Recommended)**

```bash
# Load deployment-ready fixtures (no user conflicts, all references cleaned)
python manage.py loaddata initial_data/fixtures/deployment/*.json
```

These fixtures are prepared using:
```bash
python initial_data/scripts/prepare_and_export.py
```

**Option 1B: Use Safe Loading Script**

```bash
# Automatically skips authentication.json if users exist
python initial_data/scripts/load_fixtures_safe.py
```

This script will:
- Check if users exist in the database
- Automatically skip `authentication.json` if users are found
- Load all other fixtures in the correct order
- Show a summary of what was loaded

**Option 1B: Load without user data manually**

```bash
# First, export fixtures without users (if not already done)
python manage.py export_initial_data --exclude-users

# Then load fixtures in correct order (skip authentication.json if it contains users)
python manage.py loaddata initial_data/fixtures/integrations.json
python manage.py loaddata initial_data/fixtures/agents.json
python manage.py loaddata initial_data/fixtures/commands.json
python manage.py loaddata initial_data/fixtures/projects.json
python manage.py loaddata initial_data/fixtures/workflows.json
```

**Option 2: Clear database first (⚠️ Deletes all existing data)**

```bash
# WARNING: This will delete ALL existing data!
python manage.py flush --noinput
python manage.py migrate

# Then create admin user
python manage.py setup_admin_user

# Then load fixtures (SKIP authentication.json to avoid user conflicts)
python manage.py loaddata initial_data/fixtures/integrations.json
python manage.py loaddata initial_data/fixtures/agents.json
python manage.py loaddata initial_data/fixtures/commands.json
python manage.py loaddata initial_data/fixtures/projects.json
python manage.py loaddata initial_data/fixtures/workflows.json
# Skip: initial_data/fixtures/authentication.json (user already exists)
```

**⚠️ Important:** After `setup_admin_user`, skip `authentication.json` because it contains a user with the same username "admin".

**Option 3: Load fixtures manually, skipping conflicts**

If you have existing users and want to keep them:

```bash
# Load fixtures one by one, skipping authentication.json if it causes conflicts
python manage.py loaddata initial_data/fixtures/integrations.json
python manage.py loaddata initial_data/fixtures/agents.json
python manage.py loaddata initial_data/fixtures/commands.json

# For projects/workflows that reference users, you may need to:
# 1. Edit the fixture files to use your existing user IDs, OR
# 2. Skip those fixtures and create projects/workflows manually
```

**Troubleshooting Fixture Loading:**

**Error: `UNIQUE constraint failed: users.username`**
- **Cause:** Fixture contains a user that already exists
- **Solution:** 
  - Use `--exclude-users` when exporting: `python manage.py export_initial_data --exclude-users`
  - Or skip `authentication.json` when loading: Don't load `initial_data/fixtures/authentication.json`

**Error: `No fixture named 'core' found`**
- **Cause:** `core.json` doesn't exist (not all apps export fixtures)
- **Solution:** Skip it, it's optional. Only load fixtures that exist.

**Error: `Foreign key constraint failed`**
- **Cause:** Fixture references users/agents that don't exist
- **Solution:**
  1. Load fixtures in correct order (integrations → agents → commands → projects → workflows)
  2. Ensure users exist before loading projects/workflows
  3. Or edit fixture files to use existing user/agent IDs

**For more details, see:** 
- `initial_data/README.md` - Complete fixture documentation
- `initial_data/FIXTURE_LOADING_GUIDE.md` - Troubleshooting guide for fixture loading issues

### Step 8: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## 🏃 Running the Application

### Development Mode

**Option 1: Standard Django Server (HTTP only)**

```bash
# Run on localhost only
python manage.py runserver

# Run on all interfaces (accessible from any IP)
python manage.py runserver 0.0.0.0:8000
```

**Option 2: Daphne ASGI Server (WebSocket support)**

```bash
# Run on all interfaces (accessible from any IP)
daphne core.asgi:application --bind 0.0.0.0 --port 8000
```

**⚠️ IMPORTANT:** 
- Use Daphne for WebSocket support (chat, real-time updates, dashboard)
- Use `0.0.0.0` to allow access from any IP address (localhost, external IP, network)
- The backend is configured to accept requests from any origin by default

### Production Mode

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn (HTTP)
gunicorn core.wsgi:application --bind 0.0.0.0:8000

# Run with Daphne (WebSocket)
daphne core.asgi:application --bind 0.0.0.0 --port 8000
```

---

## ✅ Verification

### 1. Check API Health

```bash
curl http://localhost:8000/api/v1/monitoring/dashboard/health/
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Check Admin Panel

- Visit: http://localhost:8000/admin/
- Login with: `admin@hishamos.com` / `Amman123`
- Should see Django admin interface

### 3. Check API Documentation

- Visit: http://localhost:8000/api/docs/
- Should see Swagger UI with all API endpoints

### 4. Check Database

```bash
python manage.py shell
```

```python
from apps.authentication.models import User
User.objects.count()  # Should return at least 1 (admin user)
```

---

## 📚 Project Structure

```
backend/
├── apps/                    # Django applications
│   ├── authentication/      # User auth, JWT, RBAC
│   ├── agents/              # AI agent management
│   ├── commands/            # Command library (350+)
│   ├── workflows/           # Workflow orchestration
│   ├── projects/            # Project & sprint management
│   ├── integrations/        # AI platform integrations
│   ├── results/             # Standardized output layer
│   ├── monitoring/          # System monitoring & logs
│   ├── docs/                # Documentation viewer
│   └── core/                # Core utilities
├── core/                    # Django settings
│   └── settings/            # Split settings (base, dev, prod, test)
├── docs/                    # Documentation (included in this repo)
├── requirements/            # Python dependencies
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── scripts/                 # Utility scripts
├── manage.py                # Django CLI
└── .env                     # Environment variables (create this)
```

---

## 🛠️ Development Commands

### Database

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
python manage.py dbshell
```

### Users

```bash
python manage.py createsuperuser
python manage.py changepassword <username>
python manage.py setup_admin_user
```

### Development

```bash
python manage.py runserver
python manage.py check
python manage.py test
python manage.py shell
```

### Static Files

```bash
python manage.py collectstatic
python manage.py findstatic <file>
```

---

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available environment variables.

**Key variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | Required |
| `DJANGO_DEBUG` | Debug mode | `False` |
| `DJANGO_ALLOWED_HOSTS` | Allowed hostnames/IPs | `['*']` (all hosts) |
| `DATABASE_URL` | Database connection | `sqlite:///db.sqlite3` |
| `CORS_ALLOW_ALL_ORIGINS` | Allow all CORS origins | `True` |
| `CORS_ALLOWED_ORIGINS` | Specific CORS origins (if `CORS_ALLOW_ALL_ORIGINS=false`) | `[]` |
| `CSRF_TRUSTED_ORIGINS` | CSRF trusted origins | Comprehensive list (see settings) |
| `REDIS_URL` | Redis connection | Optional |
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |

### Settings Files

Settings are split by environment:

- `core/settings/base.py` - Base settings
- `core/settings/development.py` - Development settings
- `core/settings/production.py` - Production settings
- `core/settings/test.py` - Test settings

Default: `development.py` (can be changed via `DJANGO_SETTINGS_MODULE`)

---

## 🐳 Docker Installation (Alternative)

See `infrastructure/INSTALLATION_GUIDE.md` for Docker setup instructions.

**Quick Docker setup:**

```bash
# From infrastructure directory
docker-compose -f docker-compose.yml up --build
```

---

## ☁️ Cloud Deployment

### Render.com Deployment

For detailed step-by-step guide on deploying to Render.com, see:
- **[RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)** - Complete Render deployment guide

**Quick Render Setup:**

1. Create PostgreSQL database on Render
2. Create Web Service connected to GitHub
3. Set environment variables
4. Deploy and run migrations
5. Load initial data (see Step 7 above)

**Important:** After deployment, run these commands via Render Shell:

```bash
# Run migrations
python manage.py migrate

# Create admin user
python manage.py setup_admin_user

# Load initial data
python scripts/create_default_agents.py
python manage.py create_commands
python manage.py link_commands_to_agents
python manage.py create_sample_workflows
```

---

## 🔗 Integration with Frontend

This backend repository works independently, but integrates with:

- **Frontend Repository:** `hishamos-frontend`
- **Infrastructure Repository:** `hishamos-infrastructure`

**Configuration:**

1. **Default Configuration (No setup needed):**
   - Backend accepts requests from any origin by default
   - No CORS configuration required
   - Frontend can connect from any domain/IP

2. **Optional: Restrict CORS (if needed):**
   ```env
   CORS_ALLOW_ALL_ORIGINS=false
   CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,https://yourdomain.com
   ```

3. **Frontend Configuration:**
   - Frontend should point to: `http://localhost:8000/api/v1/` (development)
   - Or: `https://your-backend-domain.com/api/v1/` (production)
   - No CORS errors will occur due to default permissive settings

---

## 🐛 Troubleshooting

### Issue: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
pip install -r requirements/development.txt
```

### Issue: Database Migration Errors

**Error:** `django.db.utils.OperationalError: no such table`

**Solution:**
```bash
rm db.sqlite3
python manage.py migrate
python manage.py setup_admin_user
```

### Issue: Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Use different port
python manage.py runserver 8001
```

### Issue: CORS Errors

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**
1. **Default Configuration:** CORS should work automatically (allows all origins)
2. **If restricted:** Check `CORS_ALLOW_ALL_ORIGINS` in `.env` (should be `true` or not set)
3. **If using specific origins:** Ensure frontend URL is in `CORS_ALLOWED_ORIGINS`
4. Restart server after changes

**Note:** The backend is configured to accept requests from any origin by default. If you're seeing CORS errors, check:
- `CORS_ALLOW_ALL_ORIGINS=true` (or not set, defaults to true)
- Server is running and accessible
- Frontend is pointing to correct backend URL

---

## 📖 Additional Resources

- **API Documentation:** http://localhost:8000/api/docs/
- **Development Guide:** `docs/05_DEVELOPMENT/MASTER_DEVELOPMENT_GUIDE.md`
- **Documentation Maintenance:** `docs/05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md`

---

## 🚀 Deployment on Render.com

### Prerequisites

1. **Render Account:** Sign up at [render.com](https://render.com)
2. **GitHub Repository:** Push your backend code to GitHub
3. **PostgreSQL Database:** Create a PostgreSQL database on Render

### Step 1: Create PostgreSQL Database

1. Go to Render Dashboard → New → PostgreSQL
2. Name: `hishamos-db`
3. Database: `hishamos_db`
4. User: `hishamos_user`
5. Copy the **Internal Database URL**

### Step 2: Create Web Service

1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configure:
   - **Name:** `hishamos-backend`
   - **Environment:** `Python 3`
   - **Build Command:** 
     ```bash
     pip install -r requirements/production.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command:**
     ```bash
     daphne core.asgi:application --bind 0.0.0.0 --port $PORT
     ```

### Step 3: Set Environment Variables

In Render Dashboard → Environment:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=core.settings.production
DJANGO_DEBUG=False
# ALLOWED_HOSTS - Accepts all hosts by default (*)
# Can be restricted: DJANGO_ALLOWED_HOSTS=your-app.onrender.com
# Leave unset to allow all hosts
DATABASE_URL=<from PostgreSQL service>
# CORS - Allows all origins by default
# Can be restricted: CORS_ALLOW_ALL_ORIGINS=false
# Then specify: CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
# Leave unset to allow all origins
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
```

**Important:** The backend accepts requests from any IP/origin by default. You don't need to set `DJANGO_ALLOWED_HOSTS` or `CORS_ALLOWED_ORIGINS` unless you want to restrict access.

### Step 4: Run Migrations and Load Initial Data

After first deployment, run these commands via Render Shell:

1. **Open Render Shell:**
   - Go to your service → Shell tab
   - Or use: `render shell`

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Create admin user:**
   ```bash
   python manage.py setup_admin_user
   ```

4. **Load initial data:**
   ```bash
   # Create default agents
   python scripts/create_default_agents.py
   
   # Load command templates
   python manage.py create_commands
   
   # Link commands to agents
   python manage.py link_commands_to_agents
   
   # Optional: Create sample workflows
   python manage.py create_sample_workflows
   ```

### Step 5: Verify Deployment

1. **Check health endpoint:**
   ```
   https://your-app.onrender.com/api/v1/monitoring/dashboard/health/
   ```

2. **Check admin panel:**
   ```
   https://your-app.onrender.com/admin/
   ```

3. **Check API docs:**
   ```
   https://your-app.onrender.com/api/docs/
   ```

### Troubleshooting Render Deployment

**Issue: Build fails**
- Check build logs in Render dashboard
- Verify `requirements/production.txt` exists
- Ensure Python version is compatible

**Issue: Application crashes on startup**
- Check logs for errors
- Verify all environment variables are set
- Check database connection string

**Issue: Static files not loading**
- Ensure `collectstatic` runs in build command
- Check `STATIC_ROOT` in settings

**Issue: Database connection fails**
- Verify `DATABASE_URL` is correct
- Check PostgreSQL service is running
- Ensure database user has proper permissions

---

## 🎯 Next Steps

After installation:

1. **Configure AI Platform API Keys** in `.env` (or Render environment variables)
2. **Load initial data** (commands, agents, workflows)
3. **Connect frontend** repository
4. **Review documentation** in `docs/` directory

---

**Last Updated:** December 6, 2024  
**Version:** 1.0  
**Maintained By:** Development Team
