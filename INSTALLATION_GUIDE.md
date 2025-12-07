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
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite - Default)
DATABASE_URL=sqlite:///db.sqlite3

# CORS (Frontend URL)
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Optional: AI Platform API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```

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

### Step 7: Load Initial Data (Optional)

```bash
# Load command templates
python manage.py create_commands

# Create default agents
python manage.py create_default_agents

# Create sample workflows (optional)
python manage.py create_sample_workflows
```

### Step 8: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## 🏃 Running the Application

### Development Mode

**Option 1: Standard Django Server (HTTP only)**

```bash
python manage.py runserver
```

**Option 2: Daphne ASGI Server (WebSocket support)**

```bash
daphne core.asgi:application --bind 0.0.0.0 --port 8000
```

**⚠️ IMPORTANT:** Use Daphne for WebSocket support (chat, real-time updates, dashboard).

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
| `DATABASE_URL` | Database connection | `sqlite:///db.sqlite3` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | `[]` |
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

## 🔗 Integration with Frontend

This backend repository works independently, but integrates with:

- **Frontend Repository:** `hishamos-frontend`
- **Infrastructure Repository:** `hishamos-infrastructure`

**Configuration:**

1. Set `CORS_ALLOWED_ORIGINS` in `.env`:
   ```env
   CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

2. Frontend should point to: `http://localhost:8000/api/v1/`

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
1. Check `CORS_ALLOWED_ORIGINS` in `.env`
2. Ensure frontend URL is included
3. Restart server

---

## 📖 Additional Resources

- **API Documentation:** http://localhost:8000/api/docs/
- **Development Guide:** `docs/05_DEVELOPMENT/MASTER_DEVELOPMENT_GUIDE.md`
- **Documentation Maintenance:** `docs/05_DEVELOPMENT/DOCUMENTATION_MAINTENANCE.md`

---

## 🎯 Next Steps

After installation:

1. **Configure AI Platform API Keys** in `.env`
2. **Load initial data** (commands, agents, workflows)
3. **Connect frontend** repository
4. **Review documentation** in `docs/` directory

---

**Last Updated:** December 6, 2024  
**Version:** 1.0  
**Maintained By:** Development Team
