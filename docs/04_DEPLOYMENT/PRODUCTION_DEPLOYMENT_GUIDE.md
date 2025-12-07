---
title: "HishamOS Production Deployment Guide"
description: "**Last Updated:** December 6, 2024"

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Project Manager
    - CTO / Technical Lead
  secondary:
    - All

applicable_phases:
  primary:
    - Development

tags:
  - deployment
  - core
  - guide

status: "active"
priority: "medium"
difficulty: "intermediate"
completeness: "100%"
quality_status: "draft"

estimated_read_time: "10 minutes"

version: "1.0"
last_updated: "2025-12-06"
last_reviewed: "2025-12-06"
review_frequency: "quarterly"

author: "Development Team"
maintainer: "Development Team"

related: []
see_also: []
depends_on: []
prerequisite_for: []

aliases: []

changelog:
  - version: "1.0"
    date: "2025-12-06"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---

# HishamOS Production Deployment Guide

**Last Updated:** December 6, 2024  
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Security Hardening](#security-hardening)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)
11. [Production Checklist](#production-checklist)

---

## Overview

This guide covers deploying HishamOS to production using either Docker Compose or Kubernetes. Both methods are fully supported and production-ready.

### Architecture

- **Backend:** Django + Daphne (ASGI) for WebSocket support
- **Frontend:** React + Vite, served via Nginx
- **Database:** PostgreSQL 16
- **Cache/Queue:** Redis 7
- **Task Queue:** Celery with Redis broker
- **Web Server:** Nginx (reverse proxy)

---

## Prerequisites

### Required

- Docker 20.10+ and Docker Compose 2.0+ (for Docker deployment)
- OR Kubernetes 1.24+ with kubectl (for Kubernetes deployment)
- PostgreSQL 16+ (or use containerized version)
- Redis 7+ (or use containerized version)
- Domain name with DNS configured
- SSL/TLS certificates (Let's Encrypt recommended)

### Recommended

- Container registry (Docker Hub, AWS ECR, GCR, etc.)
- CI/CD pipeline (GitHub Actions, GitLab CI, etc.)
- Monitoring solution (Prometheus + Grafana)
- Log aggregation (ELK, Loki, etc.)
- Backup solution

---

## Docker Deployment

### Quick Start

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd hishamAiAgentOS
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your production values
   ```

3. **Build and start services:**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Run migrations:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
   ```

6. **Load initial data:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python manage.py create_commands
   docker-compose -f docker-compose.prod.yml exec backend python manage.py link_commands_to_agents
   ```

### Production Configuration

**File:** `docker-compose.prod.yml`

**Key Features:**
- Multi-stage Docker builds for optimized images
- Resource limits and reservations
- Health checks for all services
- Persistent volumes for data
- Internal networking (no exposed ports except frontend)
- Automatic restarts

**Services:**
- `postgres`: Database (no external ports)
- `redis`: Cache/Queue (no external ports)
- `backend`: Django application
- `celery`: Background workers
- `celery-beat`: Scheduled tasks
- `frontend`: Nginx serving React app

### Scaling

```bash
# Scale backend
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Scale Celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery=4
```

### Updates

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

---

## Kubernetes Deployment

See `infrastructure/kubernetes/README.md` for detailed Kubernetes deployment instructions.

### Quick Start

```bash
# Build and push images
docker build -f infrastructure/docker/Dockerfile.backend.prod -t your-registry/hishamos/backend:latest ./backend
docker build -f infrastructure/docker/Dockerfile.frontend.prod -t your-registry/hishamos/frontend:latest ./frontend
docker push your-registry/hishamos/backend:latest
docker push your-registry/hishamos/frontend:latest

# Update image references in deployment files
# Deploy
kubectl apply -f infrastructure/kubernetes/
```

---

## Environment Configuration

### Required Environment Variables

Create `.env` file or Kubernetes secrets with:

```bash
# Django
DJANGO_SECRET_KEY=<generate-with-django-utils>
DEBUG=False
DJANGO_SETTINGS_MODULE=core.settings.production

# Database
POSTGRES_DB=hishamos
POSTGRES_USER=hishamos
POSTGRES_PASSWORD=<strong-password>
DATABASE_URL=postgresql://hishamos:<password>@postgres:5432/hishamos

# Redis
REDIS_PASSWORD=<strong-password>
REDIS_URL=redis://:<password>@redis:6379/0

# JWT
JWT_SECRET_KEY=<generate-random-key>

# AI Platform API Keys (optional, can be set via admin UI)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=

# Email (for password reset, notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-password>
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@hishamos.com

# Frontend URL
FRONTEND_URL=https://yourdomain.com

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Generate Django Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Database Setup

### Initial Setup

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Or with Kubernetes
kubectl exec -it deployment/backend -n hishamos -- python manage.py migrate
```

### Load Initial Data

```bash
# Load command library
docker-compose -f docker-compose.prod.yml exec backend python manage.py create_commands

# Link commands to agents
docker-compose -f docker-compose.prod.yml exec backend python manage.py link_commands_to_agents

# Create default agents (if not already created)
docker-compose -f docker-compose.prod.yml exec backend python manage.py create_default_agents
```

### Database Backup

```bash
# Manual backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U hishamos hishamos > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U hishamos hishamos < backup.sql
```

### Automated Backups

Set up cron job or Kubernetes CronJob:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: hishamos
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:16-alpine
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgres -U $POSTGRES_USER $POSTGRES_DB | \
              gzip > /backups/backup_$(date +%Y%m%d_%H%M%S).sql.gz
            env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: hishamos-secrets
                  key: POSTGRES_USER
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: hishamos-secrets
                  key: POSTGRES_PASSWORD
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

---

## Security Hardening

### 1. Secrets Management

- **Never commit secrets to git**
- Use environment variables or secret management (Vault, AWS Secrets Manager)
- Rotate secrets regularly
- Use strong, unique passwords

### 2. SSL/TLS

- Use Let's Encrypt for free SSL certificates
- Configure automatic renewal
- Force HTTPS redirects
- Use HSTS headers

### 3. Firewall

- Only expose necessary ports (80, 443)
- Use internal networking for database/Redis
- Configure security groups/network policies

### 4. Django Security Settings

Ensure `core/settings/production.py` has:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 5. API Rate Limiting

Configure in Django settings:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

---

## Monitoring & Logging

### Health Checks

All services include health check endpoints:

- Backend: `GET /api/v1/monitoring/health/`
- Frontend: `GET /health`

### Logging

**Docker:**
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f celery

# Logs are stored in volumes
docker-compose -f docker-compose.prod.yml exec backend tail -f /app/logs/django.log
```

**Kubernetes:**
```bash
kubectl logs -f deployment/backend -n hishamos
kubectl logs -f deployment/celery-worker -n hishamos
```

### Metrics

- Prometheus metrics available at `/metrics` (if configured)
- Django admin provides usage statistics
- Analytics dashboard in admin UI

---

## Backup & Recovery

### Database Backup Strategy

1. **Daily automated backups** (retain 30 days)
2. **Weekly full backups** (retain 12 weeks)
3. **Monthly archives** (retain 12 months)
4. **Test restore procedures** monthly

### Backup Locations

- Primary: Local storage
- Secondary: Cloud storage (S3, GCS, Azure Blob)
- Offsite: Different region/cloud provider

### Recovery Procedure

1. Stop services
2. Restore database from backup
3. Verify data integrity
4. Restart services
5. Test functionality

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check database is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check connection
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell

# Verify credentials
docker-compose -f docker-compose.prod.yml exec backend env | grep DATABASE
```

#### 2. Migrations Failing

```bash
# Check migration status
docker-compose -f docker-compose.prod.yml exec backend python manage.py showmigrations

# Fake migration (if needed)
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate --fake
```

#### 3. Static Files Not Loading

```bash
# Collect static files
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# Check permissions
docker-compose -f docker-compose.prod.yml exec backend ls -la /app/staticfiles
```

#### 4. Celery Not Processing Tasks

```bash
# Check Celery status
docker-compose -f docker-compose.prod.yml exec celery celery -A core inspect active

# Check Redis connection
docker-compose -f docker-compose.prod.yml exec celery celery -A core inspect stats
```

#### 5. High Memory Usage

```bash
# Check resource usage
docker stats

# Scale down if needed
docker-compose -f docker-compose.prod.yml up -d --scale backend=2
```

---

## Production Checklist

### Pre-Deployment

- [ ] All secrets configured and secure
- [ ] Database migrations tested
- [ ] SSL/TLS certificates configured
- [ ] Domain DNS configured
- [ ] Firewall rules configured
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] Error tracking configured (Sentry)
- [ ] Load testing completed
- [ ] Security audit completed

### Deployment

- [ ] Build and push Docker images
- [ ] Deploy infrastructure (Docker/K8s)
- [ ] Run database migrations
- [ ] Load initial data (commands, agents)
- [ ] Create admin user
- [ ] Configure AI platform API keys
- [ ] Verify all services healthy
- [ ] Test API endpoints
- [ ] Test frontend functionality
- [ ] Test WebSocket connections
- [ ] Verify SSL/TLS working

### Post-Deployment

- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify backups running
- [ ] Test disaster recovery
- [ ] Document any issues
- [ ] Update runbooks
- [ ] Schedule regular maintenance

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)

---

**Last Updated:** December 6, 2024  
**Maintained By:** HishamOS Development Team

