---
title: Replit Deployment Guide
description: Quick guide for deploying HishamOS Backend on Replit

category: Deployment
subcategory: Cloud Hosting
language: en
original_language: en

purpose: |
  Quick reference guide for deploying HishamOS backend on Replit platform,
  including CSRF configuration and environment setup.

target_audience:
  primary:
    - Developer
  secondary:
    - DevOps

applicable_phases:
  primary:
    - Deployment
  secondary: []

tags:
  - deployment
  - replit
  - cloud
  - django

status: active
priority: medium
difficulty: beginner
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
  - backend/RENDER_DEPLOYMENT_GUIDE.md
see_also: []
depends_on:
  - backend/INSTALLATION_GUIDE.md
prerequisite_for: []

aliases:
  - "Replit Setup"

changelog:
  - version: "1.0"
    date: "2024-12-06"
    changes: "Initial Replit deployment guide"
    author: "Development Team"
---

# HishamOS Backend - Replit Deployment Guide

Quick guide for deploying HishamOS Backend on Replit.

---

## 📋 Prerequisites

- **Replit Account:** Sign up at [replit.com](https://replit.com)
- **GitHub Repository:** Your backend code on GitHub (optional, can import directly)

---

## 🚀 Quick Setup

### Step 1: Create Repl

1. Go to [Replit](https://replit.com)
2. Click **"Create Repl"**
3. Select **"Import from GitHub"** (or start from scratch)
4. Select your `hishamos-backend` repository
5. Choose **"Python"** as the language

### Step 2: Configure Environment Variables

In Replit, go to **Secrets** tab (lock icon) and add:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=core.settings.production
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-repl-name.replit.dev,your-repl-name.repl.co
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=https://your-repl-name.replit.dev,https://your-repl-name.repl.co
```

**Note:** CSRF_TRUSTED_ORIGINS is already configured in settings to include Replit domains automatically.

### Step 3: Install Dependencies

In Replit Shell:

```bash
pip install -r requirements/production.txt
```

### Step 4: Run Migrations

```bash
python manage.py migrate
```

### Step 5: Create Admin User

```bash
python manage.py setup_admin_user
```

### Step 6: Load Initial Data

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

### Step 7: Start Server

In Replit, click **"Run"** button, or manually:

```bash
daphne core.asgi:application --bind 0.0.0.0 --port 8000
```

**Note:** Replit will automatically assign a port. Check the console for the actual port.

---

## ✅ CSRF Configuration

**CSRF_TRUSTED_ORIGINS** is already configured in:
- `core/settings/base.py`
- `core/settings/production.py`
- `core/settings/development.py`

It includes:
- `https://*.replit.dev`
- `https://*.repl.co`
- Localhost ports for development

**No additional configuration needed!**

---

## 🔧 Replit-Specific Settings

### Port Configuration

Replit assigns ports dynamically. Your app should use the port from environment:

```python
# In your start command, use:
daphne core.asgi:application --bind 0.0.0.0 --port $PORT
```

Or let Replit handle it automatically.

### Database

Replit supports SQLite by default. For PostgreSQL:
1. Use Replit Database (PostgreSQL) addon
2. Or use external database service

### Static Files

Replit handles static files automatically. Ensure:

```bash
python manage.py collectstatic --noinput
```

Runs during deployment.

---

## 🐛 Troubleshooting

### Issue: CSRF Error

**Error:** `CSRF verification failed`

**Solution:**
- CSRF_TRUSTED_ORIGINS is already configured
- Ensure your Replit URL is in ALLOWED_HOSTS
- Check that CSRF_COOKIE_SECURE matches your protocol (https for Replit)

### Issue: Port Already in Use

**Error:** `Address already in use`

**Solution:**
- Use `$PORT` environment variable
- Or let Replit assign port automatically

### Issue: Database Locked

**Error:** `database is locked` (SQLite)

**Solution:**
- SQLite may have issues with concurrent access
- Consider using PostgreSQL for production
- Or ensure only one process accesses database

---

## 📚 Additional Resources

- **Replit Documentation:** https://docs.replit.com
- **Backend Installation Guide:** `INSTALLATION_GUIDE.md`
- **Render Deployment Guide:** `RENDER_DEPLOYMENT_GUIDE.md`

---

**Last Updated:** December 6, 2024  
**Version:** 1.0  
**Maintained By:** Development Team

