# HishamOS - AI Agent Operating System

Enterprise-grade AI Agent Operating System built with Django, FastAPI, React, and multiple AI platforms.

## 🏗️ Project Structure

```
hishamAiAgentOS/
├── backend/                    # Django + FastAPI backend
│   ├── apps/                   # Django applications
│   │   ├── authentication/     # User auth, JWT, RBAC
│   │   ├── agents/             # AI agent management
│   │   ├── commands/           # Command library (350+)
│   │   ├── workflows/          # Workflow orchestration
│   │   ├── projects/           # Project & sprint management
│   │   ├── integrations/       # AI platform integrations
│   │   ├── results/            # Standardized output layer
│   │   └── monitoring/         # System monitoring & logs
│   ├── core/                   # Django settings
│   │   └── settings/           # Split settings (base, dev, prod, test)
│   ├── requirements/           # Python dependencies
│   ├── static/                 # Static files
│   ├── logs/                   # Application logs
│   └── manage.py               # Django CLI
├── hishamAIAgentOS_frontend/   # React frontend (future)
├── infrastructure/             # Docker & deployment
│   └── docker/                 # Dockerfiles
├── docs/                       # Documentation
├── .venv/                      # Python virtual environment
├── manage.py                   # Root Django CLI (proxy to backend)
├── requirements.txt            # Root requirements (points to backend)
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (3.13 recommended)
- Node.js 18+ (for frontend)
- SQLite (default, included with Python) or PostgreSQL 16+ (production)
- Redis 7+ (optional, for Celery & caching)

### 1. Clone & Setup

```bash
git clone <repository-url>
cd hishamAiAgentOS

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements/development.txt
```

### 2. Database Setup

```bash
# Navigate to backend directory
cd backend

# Run migrations (SQLite is default - no database setup needed)
python manage.py migrate

# Create admin user automatically
python manage.py setup_admin_user

# Collect static files
python manage.py collectstatic --noinput
```

**Default Admin Credentials:**
- Email: `admin@hishamos.com`
- Password: `Amman123`

**Note:** SQLite is used by default. No database installation required!

### 3. Run Development Server

**⚠️ IMPORTANT: For WebSocket support, you MUST use Daphne (ASGI server), not runserver!**

```bash
# Start Django server with WebSocket support (from backend directory)
cd backend
daphne core.asgi:application --bind 0.0.0.0 --port 8000

# OR if you don't need WebSockets (HTTP only):
python manage.py runserver
```

**Note:** The standard `runserver` command does NOT support WebSockets. Use `daphne` for real-time features (chat, agent execution updates, dashboard).

**Access URLs:**
- API Documentation (Swagger): http://localhost:8000/api/docs/
- Admin Panel: http://localhost:8000/admin/
- ReDoc: http://localhost:8000/api/redoc/

## 📦 Phase 1 & 2 Complete

###  Phase 1: Core Backend Infrastructure
- ✅ 18 Django models across 8 apps
- ✅ Complete database schema with migrations
- ✅ Django REST Framework API
- ✅ 18 serializers with validation
- ✅ 18 ModelViewSets with filtering/searching/pagination
- ✅  URL routing for all endpoints
- ✅ Swagger/OpenAPI documentation

### ✅ Phase 2: Authentication & Authorization
- ✅ JWT authentication (login, register, token refresh)
- ✅ Password reset flow
- ✅ User profile management
- ✅ RBAC permissions (Admin, Manager, Developer, Viewer)
- ✅ API key authentication (X-API-Key header)
- ✅ Authentication logging middleware

## 🔐 Authentication

### JWT Authentication

**Register:**
```bash
POST /api/v1/auth/register/
{
  "email": "user@example.com",
  "username": "username",
  "password": "secure_password",
  "password_confirm": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Login:**
```bash
POST /api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "secure_password"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { ... }
}
```

**Use Token:**
```bash
# Add to headers
Authorization: Bearer <access_token>
```

### API Key Authentication

```bash
# Add to headers
X-API-Key: your-api-key-here
```

## 📚 API Endpoints

### Authentication (`/api/v1/auth/`)
- `POST /login/` - Login
- `POST /register/` - Register
- `POST /token/refresh/` - Refresh token
- `POST /logout/` - Logout
- `GET /profile/` - Get profile
- `PUT /profile/` - Update profile
- `POST /change-password/` - Change password
- `POST /password-reset/` - Request password reset
- `POST /password-reset/confirm/` - Confirm password reset
- `GET /users/` - List users (admin)
- `POST /users/` - Create user (admin)
- `GET /api-keys/` - List API keys
- `POST /api-keys/` - Create API key

### Agents (`/api/v1/agents/`)
- `/agents/` - CRUD operations for AI agents
- `/executions/` - Agent execution history

### Commands (`/api/v1commands/`)
- `/categories/` - Command categories
- `/templates/` - Command templates (350+)

### Workflows (`/api/v1/workflows/`)
- `/workflows/` - Workflow definitions
- `/executions/` - Workflow runs
- `/steps/` - Workflow steps

### Projects (`/api/v1/projects/`)
- `/projects/` - Project management
- `/sprints/` - Sprint tracking
- `/stories/` - User stories
- `/tasks/` - Task management

### Integrations (`/api/v1/integrations/`)
- `/platforms/` - AI platform configs
- `/usage/` - Platform usage logs

### Results (`/api/v1/results/`)
- `/results/` - Output results
- `/feedback/` - User feedback

### Monitoring (`/api/v1/monitoring/`)
- `/metrics/` - System metrics
- `/health/` - Health checks
- `/audit/` - Audit logs

## 🛠️ Development

### Project Commands

```bash
# From root directory (uses root manage.py)
python manage.py <command>

# From backend directory
cd backend
python manage.py <command>
```

### Common Commands

```bash
# Database
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# Users
python manage.py createsuperuser
python manage.py changepassword <username>

# Development
python manage.py runserver
python manage.py check
python manage.py test

# Static files
python manage.py collectstatic
python manage.py findstatic <file>

# Shell
python manage.py shell
python manage.py dbshell
```

## 🐳 Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.authentication

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📝 Environment Variables

Create a `.env` file in the root directory (see `.env.example`):

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (production)
POSTGRES_DB=hishamos_db
POSTGRES_USER=hishamos_user
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-here

# AI Platforms
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=...

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🏗️ Tech Stack

### Backend
- **Framework:** Django 5.0.1
- **API:** Django REST Framework 3.14.0
- **Authentication:** JWT (Simple JWT)
- **API Docs:** DRF Spectacular (Swagger/OpenAPI)
- **Async Tasks:** Celery 5.3.6
- **Real-time:** Channels 4.0.0
- **Cache/Broker:** Redis 7
- **Database:** PostgreSQL 16 / SQLite (dev)

### AI Integrations
- **OpenAI:** GPT-4, GPT-3.5
- **Anthropic:** Claude 3
- **Google:** Gemini Pro

### DevOps
- **Containerization:** Docker
- **Orchestration:** Docker Compose

### Frontend (Future)
- **Framework:** React 18 + TypeScript
- **UI:** TailwindCSS + Shadcn/UI
- **State:** Redux Toolkit
- **API Client:** React Query

## 📖 Documentation

- [Implementation Plan](docs/implementation_plan.md)
- [API Documentation](http://localhost:8000/api/docs/)
- [Walkthrough](docs/walkthrough.md)
- [Task Tracker](docs/task.md)

## 🎯 Project Status

- ✅ **Phase 0:** Project Foundation - COMPLETE
- ✅ **Phase 1:** Core Backend Infrastructure - COMPLETE
- ✅ **Phase 2:** Authentication & Authorization - COMPLETE
- ⏳ **Phase 3:** AI Platform Integration Layer - PLANNED
- ⏳ **Phase 4:** Agent Engine Core - PLANNED
- ⏳ **Phase 5-30:** See implementation plan

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## 📄 License

[Add your license here]

## 👤 Contact

[Add your contact information]
