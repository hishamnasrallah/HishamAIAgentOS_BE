# HishamOS - Monorepo Structure Guide

**Purpose:** This document explains how to separate Frontend and Backend into different GitHub repositories while maintaining development workflow.

**Last Updated:** December 2024  
**Version:** 1.0

---

## 📋 Overview

HishamOS is structured as a monorepo containing both Frontend (React) and Backend (Django) in a single repository. This guide explains how to:

1. **Separate Frontend and Backend** into different GitHub repositories
2. **Maintain development workflow** without conflicts
3. **Deploy independently** while keeping integration

---

## 🏗️ Current Structure

```
hishamAiAgentOS/
├── backend/                    # Django backend
│   ├── apps/                   # Django applications
│   ├── core/                   # Django settings
│   ├── requirements/           # Python dependencies
│   └── manage.py              # Django CLI
├── frontend/                   # React frontend
│   ├── src/                    # React source code
│   ├── public/                 # Static assets
│   └── package.json           # Node dependencies
├── docs/                       # Documentation
└── infrastructure/             # Docker & deployment
```

---

## 🔀 Separation Strategy

### Option 1: Separate Repositories (Recommended for Production)

#### Repository Structure

**Backend Repository:** `hishamOS-backend`
```
hishamOS-backend/
├── apps/                       # Django applications
├── core/                       # Django settings
├── requirements/               # Python dependencies
├── manage.py                   # Django CLI
├── .env.example               # Environment template
├── .gitignore                 # Backend-specific ignores
├── README.md                   # Backend documentation
└── docker-compose.yml         # Backend Docker config
```

**Frontend Repository:** `hishamOS-frontend`
```
hishamOS-frontend/
├── src/                        # React source code
├── public/                     # Static assets
├── package.json               # Node dependencies
├── .env.example              # Frontend environment template
├── .gitignore                # Frontend-specific ignores
├── README.md                  # Frontend documentation
└── Dockerfile                 # Frontend Docker config
```

#### Benefits

- ✅ **Independent Versioning:** Each repository has its own version tags
- ✅ **Separate CI/CD:** Different pipelines for frontend and backend
- ✅ **Team Isolation:** Frontend and backend teams work independently
- ✅ **Smaller Repositories:** Faster clones and operations
- ✅ **Independent Deployments:** Deploy frontend and backend separately

#### Challenges

- ⚠️ **API Contract:** Need to maintain API documentation
- ⚠️ **Integration Testing:** Requires coordination
- ⚠️ **Version Synchronization:** Need to track compatible versions

---

### Option 2: Monorepo with Submodules (Alternative)

Keep monorepo but use Git submodules for separation:

```
hishamOS/
├── backend/                    # Git submodule
├── frontend/                   # Git submodule
└── .gitmodules                # Submodule configuration
```

**Not Recommended:** Adds complexity without significant benefits.

---

## 🚀 Migration Steps

### Step 1: Create Backend Repository

```bash
# 1. Create new repository on GitHub: hishamOS-backend

# 2. Clone current monorepo
git clone <current-repo-url> hishamOS-backend-temp
cd hishamOS-backend-temp

# 3. Create backend-only branch
git subtree push --prefix=backend origin backend-only

# 4. Create new repository
mkdir hishamOS-backend
cd hishamOS-backend
git init

# 5. Add backend as remote
git remote add origin <backend-repo-url>
git remote add monorepo <current-repo-url>

# 6. Pull backend subtree
git pull monorepo backend-only

# 7. Update .gitignore for backend-only
# Remove frontend-specific ignores
# Add backend-specific ignores

# 8. Push to new repository
git push -u origin main
```

### Step 2: Create Frontend Repository

```bash
# 1. Create new repository on GitHub: hishamOS-frontend

# 2. Create frontend-only branch
cd hishamOS-backend-temp
git subtree push --prefix=frontend origin frontend-only

# 3. Create new repository
mkdir hishamOS-frontend
cd hishamOS-frontend
git init

# 4. Add frontend as remote
git remote add origin <frontend-repo-url>
git remote add monorepo <current-repo-url>

# 5. Pull frontend subtree
git pull monorepo frontend-only

# 6. Update .gitignore for frontend-only
# Remove backend-specific ignores
# Add frontend-specific ignores

# 7. Push to new repository
git push -u origin main
```

### Step 3: Update Configuration Files

#### Backend `.gitignore`
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media
/staticfiles

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

#### Frontend `.gitignore`
```gitignore
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Production
build/
dist/

# Environment
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

---

## 🔗 Integration Strategy

### API Documentation

**Backend Repository:** Maintain OpenAPI/Swagger documentation
- File: `docs/API.md` or `docs/openapi.yaml`
- Update on every API change
- Version API endpoints

**Frontend Repository:** Reference API documentation
- File: `docs/API_INTEGRATION.md`
- Link to backend API docs
- Document expected request/response formats

### Environment Variables

**Backend `.env.example`:**
```env
# Database
DATABASE_URL=sqlite:///db.sqlite3

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# AI Platforms
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```

**Frontend `.env.example`:**
```env
# API
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# App
VITE_APP_NAME=HishamOS
VITE_APP_VERSION=1.0.0
```

### Docker Compose (Separate)

**Backend `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///db.sqlite3
    volumes:
      - ./db.sqlite3:/app/db.sqlite3
```

**Frontend `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Docker Compose (Combined - Optional)

For local development, create a combined `docker-compose.yml` in a separate repository or locally:

```yaml
version: '3.8'

services:
  backend:
    build: ./hishamOS-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///db.sqlite3
    volumes:
      - ./hishamOS-backend/db.sqlite3:/app/db.sqlite3

  frontend:
    build: ./hishamOS-frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
```

---

## 📝 Development Workflow

### Backend Development

```bash
# Clone backend repository
git clone <backend-repo-url>
cd hishamOS-backend

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements/base.txt

# Run migrations
python manage.py migrate

# Create admin user (automatic via management command)
python manage.py setup_admin_user

# Run development server
python manage.py runserver
```

### Frontend Development

```bash
# Clone frontend repository
git clone <frontend-repo-url>
cd hishamOS-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Integration Testing

1. **Start Backend:**
   ```bash
   cd hishamOS-backend
   python manage.py runserver
   ```

2. **Start Frontend:**
   ```bash
   cd hishamOS-frontend
   npm run dev
   ```

3. **Test Integration:**
   - Frontend should connect to backend API
   - WebSocket connections should work
   - All API endpoints should be accessible

---

## 🔄 Version Synchronization

### Versioning Strategy

**Backend:** `v1.0.0`, `v1.1.0`, `v2.0.0`  
**Frontend:** `v1.0.0`, `v1.1.0`, `v2.0.0`

### Compatibility Matrix

Maintain a compatibility matrix in both repositories:

**Backend `COMPATIBILITY.md`:**
```markdown
| Backend Version | Frontend Version | Status |
|----------------|------------------|--------|
| v1.0.0         | v1.0.0           | ✅ Compatible |
| v1.1.0         | v1.0.0           | ⚠️ Partial (new features not available) |
| v1.1.0         | v1.1.0           | ✅ Compatible |
```

**Frontend `COMPATIBILITY.md`:**
```markdown
| Frontend Version | Backend Version | Status |
|------------------|------------------|--------|
| v1.0.0           | v1.0.0           | ✅ Compatible |
| v1.1.0           | v1.0.0           | ⚠️ Partial (new features require backend v1.1.0+) |
| v1.1.0           | v1.1.0           | ✅ Compatible |
```

---

## 🚢 Deployment Strategy

### Independent Deployment

**Backend Deployment:**
- Deploy to: AWS, GCP, Azure, or any Python hosting
- Database: PostgreSQL (production) or SQLite (development)
- Environment: Set `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`

**Frontend Deployment:**
- Deploy to: Vercel, Netlify, AWS S3, or any static hosting
- Build: `npm run build`
- Environment: Set `VITE_API_BASE_URL` to production backend URL

### Combined Deployment (Optional)

Use Docker Compose for combined deployment:
- Single server with both services
- Nginx as reverse proxy
- Shared network for communication

---

## 📚 Documentation

### Backend Documentation

- **API Documentation:** OpenAPI/Swagger at `/api/docs/`
- **Installation Guide:** `INSTALLATION_GUIDE.md`
- **Development Guide:** `docs/how_to_develop/`
- **API Reference:** `docs/API.md`

### Frontend Documentation

- **Component Documentation:** Storybook or similar
- **Installation Guide:** `INSTALLATION_GUIDE.md`
- **Development Guide:** `docs/DEVELOPMENT.md`
- **API Integration:** `docs/API_INTEGRATION.md`

---

## ✅ Checklist

### Before Separation

- [ ] Document all API endpoints
- [ ] Create API versioning strategy
- [ ] Set up CI/CD pipelines
- [ ] Create environment variable templates
- [ ] Update all documentation
- [ ] Test local development workflow

### After Separation

- [ ] Backend repository created and pushed
- [ ] Frontend repository created and pushed
- [ ] Both repositories have README.md
- [ ] Both repositories have .gitignore
- [ ] Both repositories have installation guides
- [ ] API documentation is up-to-date
- [ ] Compatibility matrix is created
- [ ] CI/CD pipelines are working
- [ ] Local development workflow tested

---

## 🆘 Troubleshooting

### Issue: Frontend can't connect to Backend

**Solution:**
1. Check `VITE_API_BASE_URL` in frontend `.env`
2. Check `CORS_ALLOWED_ORIGINS` in backend `.env`
3. Verify backend is running on correct port
4. Check network connectivity

### Issue: API version mismatch

**Solution:**
1. Check compatibility matrix
2. Update frontend or backend to compatible versions
3. Review API documentation for breaking changes

### Issue: Missing dependencies

**Solution:**
1. Backend: Run `pip install -r requirements/base.txt`
2. Frontend: Run `npm install`
3. Check for version conflicts

---

## 📞 Support

For issues or questions:
- **Backend Issues:** Create issue in `hishamOS-backend` repository
- **Frontend Issues:** Create issue in `hishamOS-frontend` repository
- **Integration Issues:** Create issue in both repositories

---

**Last Updated:** December 2024  
**Maintained By:** HishamOS Development Team

