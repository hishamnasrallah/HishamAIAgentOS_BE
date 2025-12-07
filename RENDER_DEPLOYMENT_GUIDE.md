---
title: Render.com Deployment Guide
description: Complete guide for deploying HishamOS Backend on Render.com

category: Deployment
subcategory: Cloud Hosting
language: en
original_language: en

purpose: |
  Step-by-step guide for deploying HishamOS backend on Render.com, including
  database setup, environment configuration, and post-deployment data loading.

target_audience:
  primary:
    - DevOps
    - Developer
  secondary:
    - Technical Lead

applicable_phases:
  primary:
    - Deployment
  secondary: []

tags:
  - deployment
  - render
  - cloud
  - production
  - django
  - postgresql

status: active
priority: high
difficulty: intermediate
completeness: 100%

estimated_read_time: 20 minutes

version: 1.0
last_updated: 2024-12-06
last_reviewed: 2024-12-06
review_frequency: quarterly
next_review_date: 2025-03-06

author: DevOps Team
maintainer: DevOps Team
reviewer: Technical Lead

related:
  - backend/INSTALLATION_GUIDE.md
see_also:
  - infrastructure/INSTALLATION_GUIDE.md
depends_on:
  - backend/INSTALLATION_GUIDE.md
prerequisite_for: []

aliases:
  - "Render Setup"
  - "Cloud Deployment"

changelog:
  - version: "1.0"
    date: "2024-12-06"
    changes: "Initial deployment guide for Render.com"
    author: "DevOps Team"
---

# HishamOS Backend - Render.com Deployment Guide

Complete guide for deploying HishamOS Backend on Render.com cloud platform.

---

## 📋 Prerequisites

- **Render Account:** Sign up at [render.com](https://render.com) (free tier available)
- **GitHub Repository:** Your backend code pushed to GitHub
- **Environment Variables:** API keys for OpenAI, Anthropic, Google AI (optional)

---

## 🚀 Quick Start

1. **Create PostgreSQL Database** on Render
2. **Create Web Service** connected to your GitHub repo
3. **Set Environment Variables**
4. **Deploy and run migrations**
5. **Load initial data**

---

## 📦 Step-by-Step Deployment

### Step 1: Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name:** `hishamos-db`
   - **Database:** `hishamos_db`
   - **User:** `hishamos_user`
   - **Plan:** Free (for development)
4. Click **"Create Database"**
5. **Copy the Internal Database URL** (you'll need it later)

**Note:** The Internal Database URL is only accessible from other Render services. For external access, use the External Database URL.

### Step 2: Create Web Service

1. Go to Render Dashboard → **"New +"** → **"Web Service"**
2. **Connect Repository:**
   - Connect your GitHub account
   - Select your `hishamos-backend` repository
   - Select the branch (usually `main` or `master`)

3. **Configure Service:**
   - **Name:** `hishamos-backend`
   - **Environment:** `Python 3`
   - **Region:** Choose closest to your users
   - **Branch:** `main` (or your default branch)
   - **Root Directory:** `backend` (if your repo has backend folder) or leave empty if repo root is backend

4. **Build & Start:**
   - **Build Command:**
     ```bash
     pip install -r requirements/production.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command:**
     ```bash
     daphne core.asgi:application --bind 0.0.0.0 --port $PORT
     ```

5. **Plan:** Free (for development/testing)

6. Click **"Create Web Service"**

### Step 3: Configure Environment Variables

In your Web Service → **Environment** tab, add:

**Required Variables:**

```env
DJANGO_SECRET_KEY=<generate-a-secret-key>
DJANGO_SETTINGS_MODULE=core.settings.production
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=<from-postgresql-service-internal-url>
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:5173
```

**Optional (AI Platform Keys):**

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

**How to Set Variables:**

1. Go to your Web Service → **Environment** tab
2. Click **"Add Environment Variable"**
3. For `DATABASE_URL`, you can:
   - Manually copy from PostgreSQL service
   - Or use Render's database linking (see below)

**Link Database Automatically:**

1. In Web Service → **Environment** tab
2. Click **"Link Database"**
3. Select your `hishamos-db` PostgreSQL service
4. Render will automatically add `DATABASE_URL`

**Generate Django Secret Key:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 4: First Deployment

1. Click **"Save Changes"** in your Web Service
2. Render will automatically start building and deploying
3. Watch the **Logs** tab for build progress
4. Wait for deployment to complete (usually 3-5 minutes)

### Step 5: Run Migrations

After first successful deployment:

1. Go to your Web Service → **Shell** tab
2. Or use Render CLI:
   ```bash
   render shell
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

### Step 6: Create Admin User

In the same shell:

```bash
python manage.py setup_admin_user
```

This creates:
- Email: `admin@hishamos.com`
- Password: `Amman123`
- Username: `admin`

**Change password in production:**
```bash
python manage.py setup_admin_user --email your-email@example.com --password YourSecurePassword123
```

### Step 7: Load Initial Data

**Important:** Run these commands in order:

```bash
# Step 1: Create default AI agents (15+ agents)
python scripts/create_default_agents.py

# Step 2: Load command templates (350+ commands)
python manage.py create_commands

# Step 3: Link commands to agents
python manage.py link_commands_to_agents

# Step 4: Create sample workflows (optional)
python manage.py create_sample_workflows
```

**Verify Data Loaded:**

```bash
python manage.py shell
```

```python
from apps.agents.models import Agent
from apps.commands.models import CommandTemplate, CommandCategory
from apps.workflows.models import Workflow

print(f"Agents: {Agent.objects.count()}")
print(f"Command Categories: {CommandCategory.objects.count()}")
print(f"Command Templates: {CommandTemplate.objects.count()}")
print(f"Workflows: {Workflow.objects.count()}")
```

**Expected Results:**
- Agents: 15+
- Command Categories: 12
- Command Templates: 350+
- Workflows: 0+ (if you ran create_sample_workflows)

---

## ✅ Verification

### 1. Check Health Endpoint

```bash
curl https://your-app-name.onrender.com/api/v1/monitoring/dashboard/health/
```

Expected:
```json
{"status": "healthy"}
```

### 2. Check Admin Panel

Visit: `https://your-app-name.onrender.com/admin/`

Login with:
- Email: `admin@hishamos.com`
- Password: `Amman123`

### 3. Check API Documentation

Visit: `https://your-app-name.onrender.com/api/docs/`

Should see Swagger UI with all API endpoints.

### 4. Test API Endpoints

```bash
# Get auth token
curl -X POST https://your-app-name.onrender.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@hishamos.com", "password": "Amman123"}'

# Use token to access protected endpoint
curl https://your-app-name.onrender.com/api/v1/agents/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🔧 Configuration Files

### render.yaml (Optional)

If you prefer configuration as code, use `render.yaml`:

```yaml
services:
  - type: web
    name: hishamos-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements/production.txt && python manage.py collectstatic --noinput
    startCommand: daphne core.asgi:application --bind 0.0.0.0 --port $PORT
    envVars:
      - key: DJANGO_SECRET_KEY
        sync: false
      - key: DJANGO_SETTINGS_MODULE
        value: core.settings.production
      - key: DATABASE_URL
        fromDatabase:
          name: hishamos-db
          property: connectionString

databases:
  - name: hishamos-db
    plan: free
    databaseName: hishamos_db
    user: hishamos_user
```

**To use render.yaml:**

1. Push `render.yaml` to your repository
2. In Render Dashboard → **"New +"** → **"Blueprint"**
3. Connect repository and select `render.yaml`
4. Render will create services automatically

### Procfile

For Heroku-style deployment (Render also supports this):

```
web: daphne core.asgi:application --bind 0.0.0.0 --port $PORT
```

### runtime.txt

Specify Python version:

```
python-3.13.0
```

---

## 🐛 Troubleshooting

### Issue: Build Fails

**Error:** Build command fails

**Solutions:**
1. Check build logs in Render dashboard
2. Verify `requirements/production.txt` exists
3. Ensure Python version is compatible
4. Check for missing dependencies

### Issue: Application Crashes on Startup

**Error:** Service fails to start

**Solutions:**
1. Check application logs
2. Verify all environment variables are set
3. Check database connection string
4. Verify `DJANGO_SETTINGS_MODULE` is correct
5. Check for logging errors (see below)

### Issue: Logging Error (File Not Found)

**Error:** `FileNotFoundError: /opt/render/project/src/logs/django.log`

**Solution:**
This is fixed in `core/settings/production.py` - it uses console logging only. If you still see this:
1. Ensure `DJANGO_SETTINGS_MODULE=core.settings.production`
2. Check that production settings override logging configuration

### Issue: Database Connection Fails

**Error:** `django.db.utils.OperationalError: could not connect to server`

**Solutions:**
1. Verify `DATABASE_URL` is correct
2. Use Internal Database URL (not External) for Render services
3. Check PostgreSQL service is running
4. Verify database user has proper permissions
5. Check firewall/network settings

### Issue: Static Files Not Loading

**Error:** 404 for static files

**Solutions:**
1. Ensure `collectstatic` runs in build command
2. Check `STATIC_ROOT` in settings
3. Verify static files are collected in build
4. Check `STATIC_URL` configuration

### Issue: CORS Errors

**Error:** CORS policy blocking requests

**Solutions:**
1. Set `CORS_ALLOWED_ORIGINS` in environment variables
2. Include your frontend domain
3. For development, you can temporarily set:
   ```env
   CORS_ALLOW_ALL_ORIGINS=True
   ```
   (Not recommended for production)

### Issue: WebSocket Not Working

**Note:** Render's free tier may have limitations with WebSockets. Consider:
1. Using paid plan for WebSocket support
2. Using alternative service (Railway, Fly.io) for WebSocket features
3. Implementing polling as fallback

---

## 📊 Monitoring

### View Logs

1. Go to your Web Service → **Logs** tab
2. View real-time logs
3. Filter by level (INFO, WARNING, ERROR)

### Metrics

Render provides basic metrics:
- Request count
- Response times
- Error rates

For advanced monitoring, integrate:
- Sentry (error tracking)
- Prometheus (metrics)
- Custom monitoring endpoints

---

## 🔄 Updating Deployment

### Automatic Deploys

Render automatically deploys when you push to your connected branch.

### Manual Deploy

1. Go to Web Service → **Manual Deploy**
2. Select branch/commit
3. Click **"Deploy"**

### Rollback

1. Go to Web Service → **Deploys** tab
2. Find previous successful deployment
3. Click **"Rollback"**

---

## 🔐 Security Best Practices

1. **Never commit secrets:**
   - Use environment variables only
   - Add `.env` to `.gitignore`

2. **Use strong secret keys:**
   - Generate unique `DJANGO_SECRET_KEY`
   - Rotate keys periodically

3. **Enable HTTPS:**
   - Render provides SSL automatically
   - Ensure `SECURE_SSL_REDIRECT=True` in production

4. **Restrict CORS:**
   - Only allow your frontend domain
   - Don't use `CORS_ALLOW_ALL_ORIGINS` in production

5. **Database Security:**
   - Use strong database passwords
   - Limit database access
   - Regular backups

---

## 💰 Cost Considerations

**Free Tier Limits:**
- 750 hours/month (enough for 24/7 operation)
- Service sleeps after 15 minutes of inactivity
- 512 MB RAM
- Limited CPU

**Upgrade to Paid:**
- Always-on service (no sleep)
- More RAM and CPU
- Better WebSocket support
- Priority support

---

## 📚 Additional Resources

- **Render Documentation:** https://render.com/docs
- **Django Deployment:** https://docs.djangoproject.com/en/stable/howto/deployment/
- **Backend Installation Guide:** `INSTALLATION_GUIDE.md`

---

## 🎯 Post-Deployment Checklist

- [ ] Database migrations run successfully
- [ ] Admin user created
- [ ] Default agents loaded (15+)
- [ ] Command templates loaded (350+)
- [ ] Commands linked to agents
- [ ] Health endpoint returns 200
- [ ] Admin panel accessible
- [ ] API documentation accessible
- [ ] CORS configured correctly
- [ ] Environment variables set
- [ ] SSL/HTTPS working
- [ ] Logs accessible

---

**Last Updated:** December 6, 2024  
**Version:** 1.0  
**Maintained By:** DevOps Team

