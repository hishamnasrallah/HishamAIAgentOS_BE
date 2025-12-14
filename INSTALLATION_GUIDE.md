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
  AI platform setup, Redis & Celery configuration, and verification steps.

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
  - celery
  - redis
  - ai-platforms

status: active
priority: critical
difficulty: beginner
completeness: 100%

estimated_read_time: 30 minutes

version: 2.0
last_updated: 2024-12-14
last_reviewed: 2024-12-14
review_frequency: quarterly
next_review_date: 2025-03-14

author: Development Team
maintainer: Development Team
reviewer: Technical Lead

related:
  - docs/04_DEPLOYMENT/DEPLOYMENT_INFRASTRUCTURE_SUMMARY.md
  - docs/SETUP_COMMANDS_GUIDE.md
see_also:
  - frontend/INSTALLATION_GUIDE.md
  - infrastructure/INSTALLATION_GUIDE.md
depends_on: []
prerequisite_for: []

aliases:
  - "Setup Guide"
  - "Backend Setup"

changelog:
  - version: "2.0"
    date: "2024-12-14"
    changes: "Added comprehensive AI platform setup, Redis & Celery configuration, conversation management setup"
    author: "Development Team"
  - version: "1.0"
    date: "2024-12-06"
    changes: "Updated for standalone repository"
    author: "Development Team"
---

# HishamOS Backend - Complete Installation Guide

Complete installation and setup guide for HishamOS Backend (Django REST API) with AI platforms, Redis, and Celery.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Step-by-Step Installation](#step-by-step-installation)
4. [Redis Setup (Multiple Methods)](#redis-setup-multiple-methods)
5. [Celery Setup & Configuration](#celery-setup--configuration)
6. [AI Platform Setup](#ai-platform-setup)
7. [Running the Application](#running-the-application)
8. [Verification](#verification)
9. [Troubleshooting](#troubleshooting)

---

## 📋 Prerequisites

### Required Software

- **Python 3.11+** (3.13 recommended)
- **pip** (Python package manager)
- **Git** (version control)
- **SQLite** (default, included with Python)

### Required for Full Functionality

- **Redis 7+** (for caching and Celery task queue)
- **Celery** (for asynchronous task processing)

### Optional (for production)

- **PostgreSQL 16+** (production database)
- **Docker** (containerized deployment)

---

## 🚀 Quick Start

For a quick setup with all essential components:

```bash
# 1. Clone repository
git clone https://github.com/your-org/hishamos-backend.git
cd hishamos-backend/backend

# 2. Create virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements/development.txt

# 4. Setup environment
# Copy .env.example to .env and configure

# 5. Run migrations
python manage.py migrate

# 6. Create admin user
python manage.py setup_admin_user

# 7. Setup AI platforms (see AI Platform Setup section)
python manage.py setup_all_platforms

# 8. Configure conversation management
python manage.py configure_conversation_management
python manage.py configure_provider_documentation

# 9. Setup Redis (see Redis Setup section)

# 10. Start Celery (see Celery Setup section)

# 11. Run server
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
cd hishamos-backend/backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate
```

**Note:** The virtual environment should be activated before proceeding. You'll see `(.venv)` in your terminal prompt.

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

Create a `.env` file in the backend root directory (same level as `manage.py`):

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

# CORS - Allows all origins by default for flexibility
CORS_ALLOW_ALL_ORIGINS=true
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Redis (for Celery and caching)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Optional: AI Platform API Keys (can also be set via setup commands)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
OPENROUTER_API_KEY=
```

**Generate Django Secret Key:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Note:** The backend is configured to accept requests from any IP address by default:
- `ALLOWED_HOSTS = ['*']` (if not specified in `.env`)
- `CORS_ALLOW_ALL_ORIGINS = True` (allows requests from any origin)
- CSRF protection is disabled for API endpoints (uses JWT/API keys instead)

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
   
   # Windows
   # Download from: https://www.postgresql.org/download/windows/
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

---

## 🔴 Redis Setup (Multiple Methods)

Redis is **REQUIRED** for Celery (asynchronous task processing) and caching. Choose the method that works best for your environment.

### Understanding Redis

**What is Redis?**
- Redis is an in-memory data store used as a message broker for Celery
- It acts as a queue system for asynchronous tasks
- Also used for caching frequently accessed data
- Provides fast read/write operations

**Why Do We Need Redis?**
1. **Celery Message Broker**: Celery uses Redis to queue tasks that need to run asynchronously (e.g., AI agent execution)
2. **Task Result Backend**: Stores results of completed tasks
3. **Caching**: Speeds up repeated database queries
4. **Session Storage**: Can store user session data
5. **Real-time Features**: Supports pub/sub for real-time notifications

**How Redis Works:**
- **Producer** (Django/Celery): Sends tasks to Redis queue
- **Redis Queue**: Stores tasks waiting to be processed
- **Consumer** (Celery Worker): Picks up tasks from queue and executes them
- **Result Storage**: Completed task results stored back in Redis

---

### Method 1: Docker (Recommended - Easiest)

**Best for:** All platforms, easiest setup

#### Prerequisites
- Docker Desktop installed: https://www.docker.com/products/docker-desktop

#### Setup

```bash
# Start Redis container
docker run -d --name redis-hishamos -p 6379:6379 redis:7-alpine

# Verify it's running
docker ps | findstr redis  # Windows
docker ps | grep redis     # Linux/Mac

# Check logs
docker logs redis-hishamos
```

**Start Redis:**
```bash
docker start redis-hishamos
```

**Stop Redis:**
```bash
docker stop redis-hishamos
```

**Remove Container:**
```bash
docker rm -f redis-hishamos
```

**Using docker-compose** (if you have docker-compose.yml):
```bash
docker-compose up -d redis
```

**Advantages:**
- ✅ Works on all platforms
- ✅ Easy to start/stop
- ✅ Isolated from system
- ✅ No system installation needed

---

### Method 2: Windows Native - Memurai (Recommended for Windows)

**Best for:** Windows users who want native Windows service

#### What is Memurai?
- Memurai is a Redis-compatible server for Windows
- Runs as a Windows service
- Starts automatically with Windows
- No Docker required

#### Setup

1. **Download Memurai:**
   - Visit: https://www.memurai.com/get-memurai
   - Download the MSI installer

2. **Install:**
   - Run the MSI installer
   - Follow installation wizard
   - Service installs automatically

3. **Verify Service:**
   ```powershell
   # Check if service is running
   Get-Service Memurai
   
   # Start service (if not running)
   Start-Service Memurai
   
   # Stop service
   Stop-Service Memurai
   ```

4. **Test Connection:**
   ```powershell
   python
   ```
   ```python
   import redis
   r = redis.Redis(host='localhost', port=6379, db=0)
   r.ping()  # Should return: True
   ```

**Advantages:**
- ✅ Native Windows service
- ✅ Starts automatically
- ✅ No Docker needed
- ✅ Easy to manage via Windows Services

---

### Method 3: Windows - Direct Download

**Best for:** Windows users without Docker, quick testing

#### Setup

1. **Download Redis:**
   - Visit: https://github.com/microsoftarchive/redis/releases
   - Download `Redis-x64-*.zip` (latest version)

2. **Extract:**
   ```powershell
   # Extract to C:\redis (or your preferred location)
   Expand-Archive -Path Redis-x64-*.zip -DestinationPath C:\redis
   ```

3. **Run Redis:**
   ```powershell
   cd C:\redis
   .\redis-server.exe
   ```
   
   **Keep this window open!** Redis runs in foreground.

4. **Test Connection:**
   ```powershell
   # In a new terminal
   cd C:\redis
   .\redis-cli.exe ping
   # Should return: PONG
   ```

**Advantages:**
- ✅ No installation needed
- ✅ Works immediately
- ✅ Good for testing

**Disadvantages:**
- ❌ Must keep window open
- ❌ Doesn't start automatically
- ❌ Manual management required

---

### Method 4: Windows - Automated Script

**Best for:** Windows users, automated setup

We provide a PowerShell script:

```powershell
cd backend
.\scripts\setup-redis-windows.ps1
```

This script:
1. Downloads Redis automatically
2. Extracts to `%USERPROFILE%\redis-windows`
3. Starts Redis server in a new window

**Keep the Redis window open** while you develop!

---

### Method 5: Linux/macOS - Package Manager

**Best for:** Linux and macOS users

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server

# Enable on boot
sudo systemctl enable redis-server

# Verify
redis-cli ping  # Should return: PONG
```

#### macOS (Homebrew):
```bash
brew install redis

# Start Redis
brew services start redis

# Or run manually
redis-server

# Verify
redis-cli ping  # Should return: PONG
```

#### macOS (MacPorts):
```bash
sudo port install redis

# Start Redis
redis-server

# Verify
redis-cli ping
```

---

### Method 6: WSL (Windows Subsystem for Linux)

**Best for:** Windows users with WSL installed

```bash
# Open WSL terminal
wsl

# Install Redis
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo service redis-server start

# Verify
redis-cli ping  # Should return: PONG

# Enable on boot
sudo systemctl enable redis-server
```

---

### Verifying Redis is Running

**Method 1: Using redis-cli:**
```bash
redis-cli ping
# Should return: PONG
```

**Method 2: Using Python:**
```bash
python
```
```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()  # Should return: True
print("Redis is running!")
```

**Method 3: Using PowerShell (Windows):**
```powershell
Test-NetConnection -ComputerName localhost -Port 6379
# Look for: TcpTestSucceeded : True
```

**Method 4: Check Process:**
```powershell
# Windows
Get-Process -Name "redis-server" -ErrorAction SilentlyContinue

# Linux/Mac
ps aux | grep redis
```

---

## ⚙️ Celery Setup & Configuration

### Understanding Celery

**What is Celery?**
- Celery is a distributed task queue system
- Allows Django to run tasks asynchronously (in the background)
- Tasks don't block the main application thread
- Perfect for long-running operations like AI agent execution

**Why Do We Need Celery?**
1. **Async Task Processing**: Execute AI agent tasks without blocking HTTP requests
2. **Background Jobs**: Process tasks while user continues using the app
3. **Scalability**: Can run multiple workers to handle more tasks
4. **Reliability**: Tasks are queued and persisted (won't be lost if server restarts)
5. **Scheduling**: Can schedule tasks to run at specific times (Celery Beat)

**How Celery Works:**
```
User Request → Django View → Queue Task to Redis → Return Response Immediately
                                              ↓
                                    Celery Worker picks up task
                                              ↓
                                    Execute task (AI agent, etc.)
                                              ↓
                                    Store result in Redis
                                              ↓
                                    (Optional) Send notification
```

**Components:**
- **Celery Worker**: Process that executes tasks (you run this)
- **Redis**: Message broker (queue for tasks)
- **Django**: Produces tasks and stores them in Redis
- **Task**: A function that runs asynchronously

---

### Step 1: Install Celery (Already Included)

Celery is included in `requirements/base.txt`. No additional installation needed.

Verify installation:
```bash
celery --version
```

---

### Step 2: Start Celery Worker

**Important:** Redis must be running before starting Celery!

#### Windows (Recommended Settings)

**Use solo pool** (single process) - Windows-friendly:

```powershell
cd backend
celery -A core worker --loglevel=info --pool=solo --concurrency=1
```

**Why solo pool?**
- Windows doesn't handle multiprocessing well
- Solo pool uses single process (avoids MemoryError)
- Perfect for development

**Using provided script:**
```powershell
cd backend
.\scripts\start-celery-windows.ps1
```

#### Linux/macOS (Production Settings)

**Use prefork pool** (multiple processes) - Better performance:

```bash
cd backend
celery -A core worker --loglevel=info --concurrency=4
```

**Why prefork pool?**
- Better performance with multiple workers
- Can handle multiple tasks concurrently
- Standard for production

#### Development Settings (All Platforms)

```bash
# Basic worker
celery -A core worker --loglevel=info

# With specific pool (Windows)
celery -A core worker --loglevel=info --pool=solo

# With concurrency control
celery -A core worker --loglevel=info --concurrency=2

# With task events (for monitoring)
celery -A core worker --loglevel=info --pool=solo --events
```

---

### Step 3: Start Celery Beat (Optional - For Scheduled Tasks)

Celery Beat schedules periodic tasks (like cleanup jobs, scheduled reports).

```bash
# Start Celery Beat
celery -A core beat --loglevel=info
```

**Note:** This is optional and only needed if you have scheduled tasks.

---

### Celery Command Options Explained

| Option | Description | Example |
|--------|-------------|---------|
| `-A core` | Celery app instance | Points to `core/celery.py` |
| `worker` | Run as worker (task executor) | Processes tasks from queue |
| `beat` | Run as beat (scheduler) | Schedules periodic tasks |
| `--loglevel=info` | Logging level | `debug`, `info`, `warning`, `error` |
| `--pool=solo` | Worker pool type | `solo` (single process) or `prefork` (multiple) |
| `--concurrency=1` | Number of concurrent tasks | 1-4 for development, 8+ for production |
| `--events` | Enable task events | For monitoring tools |

---

### Running Celery in Development

**Terminal 1 - Django Server:**
```bash
cd backend
python manage.py runserver
# OR
daphne core.asgi:application --bind 0.0.0.0 --port 8000
```

**Terminal 2 - Redis:**
```bash
# If using Docker
docker start redis-hishamos

# If using Memurai (Windows)
# Service runs automatically

# If using direct Redis
redis-server
```

**Terminal 3 - Celery Worker:**
```bash
cd backend
celery -A core worker --loglevel=info --pool=solo --concurrency=1
```

**Terminal 4 - Celery Beat (Optional):**
```bash
cd backend
celery -A core beat --loglevel=info
```

---

### Testing Celery

**Test Task Execution:**

```bash
python manage.py shell
```

```python
from core.celery import debug_task

# Execute task asynchronously
result = debug_task.delay()

# Get result (blocks until task completes)
print(result.get())  # Should print task result

# Check task status
print(result.status)  # Should be: SUCCESS
```

**Expected Output:**
- Celery worker terminal should show task execution logs
- Task completes successfully
- Result returned correctly

---

### Celery Configuration

Celery is configured in `core/celery.py` and uses settings from `core/settings/base.py`:

**Key Settings:**
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'      # Task queue
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'  # Result storage
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

**Override in `.env`:**
```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

---

### Celery Troubleshooting

**Error: "Cannot connect to Redis"**
- **Solution:** Make sure Redis is running (see Redis Setup above)
- **Verify:** `redis-cli ping` should return `PONG`

**Error: "MemoryError" on Windows**
- **Solution:** Use `--pool=solo` flag
- **Command:** `celery -A core worker --pool=solo --concurrency=1`

**Tasks Not Executing:**
- **Check:** Redis is running
- **Check:** Celery worker is running and connected
- **Check:** Logs for errors
- **Verify:** Tasks are being queued (check Django logs)

**Tasks Stuck in Queue:**
- **Check:** Worker is running
- **Check:** Worker can connect to Redis
- **Restart:** Both Redis and Celery worker

---

## 🤖 AI Platform Setup

HishamOS supports multiple AI platforms. Set them up using management commands.

### Understanding AI Platforms

**What are AI Platforms?**
- Integration points with AI providers (OpenAI, Anthropic, Google, etc.)
- Each platform has different models, capabilities, and pricing
- Configured with API keys and conversation management settings
- Agents use platforms to execute AI tasks

**What Gets Configured:**
- API credentials (encrypted)
- Default models
- Conversation management strategy
- Cost optimization settings
- Provider documentation

---

### Quick Setup: All Platforms

**Interactive Setup** (prompts for API keys):
```bash
python manage.py setup_all_platforms
```

**Batch Setup** (with API keys):
```bash
python manage.py setup_all_platforms \
  --openai-key YOUR_OPENAI_KEY \
  --anthropic-key YOUR_ANTHROPIC_KEY \
  --gemini-key YOUR_GEMINI_KEY \
  --openrouter-key YOUR_OPENROUTER_KEY \
  --update
```

---

### Individual Platform Setup

#### 1. OpenAI (GPT-4, GPT-3.5)

```bash
python manage.py setup_openai --api-key YOUR_OPENAI_API_KEY
```

**Options:**
- `--api-key` (required): Your OpenAI API key
- `--update`: Update existing platform
- `--create-agents`: Create default agents (default: True)

**Creates:**
- OpenAI platform configuration
- GPT-4 Assistant agent
- GPT-3.5 Assistant agent
- Full conversation management configuration

**Models Available:**
- `gpt-4-turbo` - Most capable model
- `gpt-4` - Standard GPT-4
- `gpt-3.5-turbo` - Fast and cost-effective

---

#### 2. Anthropic (Claude Opus, Sonnet, Haiku)

```bash
python manage.py setup_anthropic --api-key YOUR_ANTHROPIC_API_KEY
```

**Options:**
- `--api-key` (required): Your Anthropic API key
- `--update`: Update existing platform
- `--create-agents`: Create default agents (default: True)

**Creates:**
- Anthropic Claude platform configuration
- Claude Opus Assistant agent
- Claude Sonnet Assistant agent
- Claude Haiku Assistant agent
- Full conversation management configuration

**Models Available:**
- `claude-3-opus` - Most powerful
- `claude-3-sonnet` - Balanced performance
- `claude-3-haiku` - Fast and efficient

---

#### 3. Google Gemini

```bash
python manage.py setup_gemini --api-key YOUR_GEMINI_API_KEY
```

**Options:**
- `--api-key` (required): Your Google Gemini API key
- `--update`: Update existing platform
- `--create-agents`: Create default agents (default: True)

**Creates:**
- Google Gemini platform configuration
- Gemini Pro Assistant agent
- Gemini Vision Assistant agent
- Full conversation management configuration (with testing notes)

**Models Available:**
- `gemini-pro` - Standard model
- `gemini-pro-vision` - With image analysis

**Note:** Conversation state support needs API testing. Currently defaults to stateless.

---

#### 4. OpenRouter (Multiple Models)

```bash
python manage.py setup_openrouter \
  --api-key YOUR_OPENROUTER_API_KEY \
  --site-url http://localhost:3000 \
  --site-name HishamOS
```

**Options:**
- `--api-key` (required): Your OpenRouter API key
- `--site-url`: Your site URL for rankings (default: http://localhost:3000)
- `--site-name`: Your site name (default: HishamOS)
- `--update`: Update existing platform

**Creates:**
- OpenRouter platform configuration
- Mistral 7B Assistant agent (free model)
- Full conversation management configuration

**Models Available:**
- Access to multiple AI models through OpenRouter
- Free models available (e.g., `mistralai/mistral-7b-instruct:free`)

---

### After Platform Setup

**1. Configure Conversation Management:**
```bash
python manage.py configure_conversation_management
```

This command:
- Sets conversation strategy for each platform
- Configures identifier extraction paths
- Sets up conversation ID field mappings

**2. Configure Provider Documentation:**
```bash
python manage.py configure_provider_documentation
```

This command:
- Populates comprehensive provider documentation
- Adds architecture details
- Includes cost optimization notes
- Documents identifier extraction methods

**3. Verify Setup:**
```bash
python manage.py shell
```

```python
from apps.integrations.models import AIPlatform
from apps.agents.models import Agent

# Check platforms
platforms = AIPlatform.objects.filter(is_enabled=True)
for p in platforms:
    print(f"{p.display_name}: {p.platform_name}")
    print(f"  Strategy: {p.conversation_strategy}")
    print(f"  API Stateful: {p.api_stateful}")
    print(f"  Has Docs: {bool(p.provider_notes)}")

# Check agents
agents = Agent.objects.filter(status='active')
for a in agents:
    print(f"{a.name}: {a.preferred_platform} / {a.model_name}")
```

---

## 🏃 Running the Application

### Development Mode

**Terminal Setup:**

You'll need **multiple terminals** for full functionality:

**Terminal 1 - Django Server:**
```bash
cd backend
python manage.py runserver
# OR with WebSocket support:
daphne core.asgi:application --bind 0.0.0.0 --port 8000
```

**Terminal 2 - Redis:**
```bash
# If using Docker
docker start redis-hishamos

# If using direct Redis
redis-server

# If using Memurai (Windows)
# Service runs automatically - no terminal needed
```

**Terminal 3 - Celery Worker:**
```bash
cd backend
celery -A core worker --loglevel=info --pool=solo --concurrency=1
```

**Terminal 4 - Celery Beat (Optional):**
```bash
cd backend
celery -A core beat --loglevel=info
```

**⚠️ IMPORTANT:** 
- Use Daphne for WebSocket support (chat, real-time updates, dashboard)
- Use `0.0.0.0` to allow access from any IP address (localhost, external IP, network)
- Redis must be running before Celery
- Celery worker must be running for async tasks to execute

---

### Production Mode

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn (HTTP)
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Run with Daphne (WebSocket)
daphne core.asgi:application --bind 0.0.0.0 --port 8000

# Celery Worker (Production)
celery -A core worker --loglevel=info --concurrency=8

# Celery Beat (Production)
celery -A core beat --loglevel=info
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

### 4. Check Redis Connection

```bash
python manage.py shell
```

```python
import redis
from django.conf import settings

# Test Redis connection
r = redis.Redis.from_url(settings.CELERY_BROKER_URL)
print(r.ping())  # Should return: True
print("Redis is connected!")
```

### 5. Check Celery Connection

```bash
python manage.py shell
```

```python
from core.celery import debug_task

# Test Celery task
result = debug_task.delay()
print(result.get())  # Should return task result
print(result.status)  # Should be: SUCCESS
print("Celery is working!")
```

### 6. Check AI Platforms

```bash
python manage.py shell
```

```python
from apps.integrations.models import AIPlatform
from apps.agents.models import Agent

# Check platforms
print(f"Platforms: {AIPlatform.objects.filter(is_enabled=True).count()}")
for p in AIPlatform.objects.filter(is_enabled=True):
    print(f"  - {p.display_name}: {p.platform_name}")

# Check agents
print(f"Agents: {Agent.objects.filter(status='active').count()}")
for a in Agent.objects.filter(status='active'):
    print(f"  - {a.name}: {a.preferred_platform}")
```

### 7. Check Database

```bash
python manage.py shell
```

```python
from apps.authentication.models import User
from apps.agents.models import Agent
from apps.commands.models import CommandTemplate

# Check data
print(f"Users: {User.objects.count()}")
print(f"Agents: {Agent.objects.count()}")
print(f"Commands: {CommandTemplate.objects.count()}")
```

---

## 🐛 Troubleshooting

### Issue: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
pip install -r requirements/development.txt
```

---

### Issue: Database Migration Errors

**Error:** `django.db.utils.OperationalError: no such table`

**Solution:**
```bash
# For SQLite (development)
rm db.sqlite3
python manage.py migrate
python manage.py setup_admin_user

# For PostgreSQL (production)
python manage.py migrate
```

---

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

---

### Issue: Redis Connection Failed

**Error:** `Error 10061 - Connection Refused` or `Cannot connect to Redis`

**Solutions:**

1. **Check Redis is running:**
   ```powershell
   # Windows - Check process
   Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
   
   # Docker - Check container
   docker ps | findstr redis
   
   # Memurai - Check service
   Get-Service Memurai
   ```

2. **Start Redis:**
   ```bash
   # Docker
   docker start redis-hishamos
   
   # Direct
   redis-server
   
   # Memurai (Windows)
   Start-Service Memurai
   ```

3. **Test Connection:**
   ```python
   import redis
   r = redis.Redis(host='localhost', port=6379, db=0)
   r.ping()  # Should return: True
   ```

4. **Check Port:**
   ```powershell
   netstat -ano | findstr :6379
   ```

---

### Issue: Celery MemoryError (Windows)

**Error:** `MemoryError` or `Fatal process out of memory`

**Solution:**
Use solo pool instead of default prefork:
```bash
celery -A core worker --loglevel=info --pool=solo --concurrency=1
```

**Why?**
- Windows doesn't handle multiprocessing well
- Solo pool uses single process
- Prevents memory issues

---

### Issue: Celery Tasks Not Executing

**Symptoms:**
- Tasks are queued but never complete
- No logs in Celery worker

**Solutions:**

1. **Check Celery Worker is Running:**
   ```bash
   # Should see worker logs
   celery -A core worker --loglevel=info
   ```

2. **Check Redis Connection:**
   ```python
   from django.conf import settings
   import redis
   r = redis.Redis.from_url(settings.CELERY_BROKER_URL)
   r.ping()  # Should return: True
   ```

3. **Clear Redis:**
   ```bash
   # Clear all Celery data
   redis-cli FLUSHDB
   ```

4. **Restart Everything:**
   ```bash
   # Stop Celery (Ctrl+C)
   # Stop Redis
   # Start Redis
   # Start Celery
   ```

---

### Issue: CORS Errors

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**
1. **Default Configuration:** CORS should work automatically (allows all origins)
2. **Check `.env`:** `CORS_ALLOW_ALL_ORIGINS=true` (or not set, defaults to true)
3. **Restart server** after changes

**Note:** The backend accepts requests from any origin by default.

---

### Issue: AI Platform Not Working

**Error:** Mock responses or platform errors

**Solutions:**

1. **Check Platform is Enabled:**
   ```python
   from apps.integrations.models import AIPlatform
   platform = AIPlatform.objects.get(platform_name='openai')
   print(platform.is_enabled)  # Should be: True
   ```

2. **Check API Key:**
   ```python
   platform = AIPlatform.objects.get(platform_name='openai')
   print(platform.has_api_key())  # Should be: True
   ```

3. **Reconfigure Platform:**
   ```bash
   python manage.py setup_openai --api-key YOUR_KEY --update
   ```

4. **Check Adapter:**
   ```bash
   python scripts/check-ai-setup.py
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
│   │   ├── adapters/        # AI platform adapters
│   │   └── services/        # Conversation management
│   ├── chat/                # Chat interface with AI agents
│   ├── results/             # Standardized output layer
│   ├── monitoring/          # System monitoring & logs
│   ├── docs/                # Documentation viewer
│   └── core/                # Core utilities
├── core/                    # Django settings
│   ├── settings/            # Split settings (base, dev, prod, test)
│   └── celery.py            # Celery configuration
├── docs/                    # Documentation
├── requirements/            # Python dependencies
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── scripts/                 # Utility scripts
│   ├── setup-redis-windows.ps1
│   ├── start-celery-windows.ps1
│   └── check-ai-setup.py
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

### AI Platforms

```bash
# Setup platforms
python manage.py setup_openai --api-key KEY
python manage.py setup_anthropic --api-key KEY
python manage.py setup_gemini --api-key KEY
python manage.py setup_openrouter --api-key KEY
python manage.py setup_all_platforms

# Configure conversation management
python manage.py configure_conversation_management
python manage.py configure_provider_documentation
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
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery message broker | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result storage | `redis://localhost:6379/1` |
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |
| `GOOGLE_API_KEY` | Google Gemini API key | Optional |
| `OPENROUTER_API_KEY` | OpenRouter API key | Optional |

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
3. Set environment variables (including Redis URL)
4. Deploy and run migrations
5. Setup AI platforms
6. Load initial data

**Important:** After deployment, run these commands via Render Shell:

```bash
# Run migrations
python manage.py migrate

# Create admin user
python manage.py setup_admin_user

# Setup AI platforms
python manage.py setup_all_platforms

# Configure conversation management
python manage.py configure_conversation_management
python manage.py configure_provider_documentation

# Load initial data
python scripts/create_default_agents.py
python manage.py create_commands
python manage.py link_commands_to_agents
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

## 📖 Additional Resources

- **API Documentation:** http://localhost:8000/api/docs/
- **Setup Commands Guide:** `docs/SETUP_COMMANDS_GUIDE.md`
- **Redis Setup:** `docs/REDIS_MANUAL_SETUP.md`
- **Celery Setup:** `docs/CELERY_WINDOWS_SETUP.md`
- **Development Guide:** `docs/05_DEVELOPMENT/MASTER_DEVELOPMENT_GUIDE.md`

---

## 🎯 Next Steps

After installation:

1. ✅ **Setup Redis** (see Redis Setup section)
2. ✅ **Start Celery Worker** (see Celery Setup section)
3. ✅ **Configure AI Platforms** (see AI Platform Setup section)
4. ✅ **Load initial data** (commands, agents, workflows)
5. ✅ **Connect frontend** repository
6. ✅ **Review documentation** in `docs/` directory

---

**Last Updated:** December 14, 2024  
**Version:** 2.0  
**Maintained By:** Development Team
