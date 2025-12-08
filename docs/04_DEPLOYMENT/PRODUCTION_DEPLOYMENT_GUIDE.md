# Production Deployment Guide

**Version:** 2.0  
**Last Updated:** December 8, 2024  
**Monitoring:** See `MONITORING_GUIDE.md` for complete monitoring documentation

---

## 📋 Pre-Deployment Checklist

### Infrastructure
- [ ] Kubernetes cluster provisioned (v1.24+)
- [ ] Container registry configured (GitHub Container Registry, Docker Hub, etc.)
- [ ] DNS configured and pointing to load balancer
- [ ] SSL certificates obtained (Let's Encrypt, cert-manager)
- [ ] Database (PostgreSQL) provisioned
- [ ] Redis provisioned
- [ ] Storage volumes configured
- [ ] Monitoring stack deployed (Prometheus, Grafana)
- [ ] Logging stack deployed (Loki, Promtail)
- [ ] Prometheus configured to scrape `/api/v1/monitoring/prometheus/metrics/`
- [ ] Grafana dashboards imported (see `infrastructure/monitoring/grafana-dashboards/`)
- [ ] JSON logging enabled (`USE_JSON_LOGGING=true` in production)
- [ ] Database performance views migration applied

### Security
- [ ] All secrets updated in Kubernetes secrets
- [ ] API keys rotated
- [ ] Security headers configured
- [ ] Rate limiting configured
- [ ] CORS origins restricted
- [ ] Firewall rules configured
- [ ] Backup strategy in place

### Application
- [ ] All tests passing
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] Static files collected
- [ ] Docker images built and pushed
- [ ] Health checks configured

---

## 🚀 Deployment Steps

### 1. Build and Push Docker Images

```bash
# Set registry
export REGISTRY=ghcr.io
export IMAGE_NAME=your-org/hishamos

# Build backend
docker build -f infrastructure/docker/Dockerfile.backend.prod \
  -t $REGISTRY/$IMAGE_NAME-backend:latest \
  -t $REGISTRY/$IMAGE_NAME-backend:v1.0.0 \
  ./backend

# Build frontend
docker build -f infrastructure/docker/Dockerfile.frontend.prod \
  -t $REGISTRY/$IMAGE_NAME-frontend:latest \
  -t $REGISTRY/$IMAGE_NAME-frontend:v1.0.0 \
  ./frontend

# Build Celery worker
docker build -f infrastructure/docker/Dockerfile.celery.prod \
  -t $REGISTRY/$IMAGE_NAME-celery:latest \
  -t $REGISTRY/$IMAGE_NAME-celery:v1.0.0 \
  ./backend

# Push images
docker push $REGISTRY/$IMAGE_NAME-backend:latest
docker push $REGISTRY/$IMAGE_NAME-backend:v1.0.0
docker push $REGISTRY/$IMAGE_NAME-frontend:latest
docker push $REGISTRY/$IMAGE_NAME-frontend:v1.0.0
docker push $REGISTRY/$IMAGE_NAME-celery:latest
docker push $REGISTRY/$IMAGE_NAME-celery:v1.0.0
```

### 2. Update Kubernetes Manifests

```bash
# Update image tags in deployment files
sed -i "s|hishamos/backend:latest|$REGISTRY/$IMAGE_NAME-backend:v1.0.0|g" \
  infrastructure/kubernetes/backend-deployment.yaml

sed -i "s|hishamos/frontend:latest|$REGISTRY/$IMAGE_NAME-frontend:v1.0.0|g" \
  infrastructure/kubernetes/frontend-deployment.yaml

sed -i "s|hishamos/celery:latest|$REGISTRY/$IMAGE_NAME-celery:v1.0.0|g" \
  infrastructure/kubernetes/celery-deployment.yaml
```

### 3. Configure Secrets

```bash
# Generate Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update secrets.yaml with:
# - Django SECRET_KEY
# - Database credentials
# - Redis password
# - AI platform API keys
# - Email credentials
# - JWT signing key
```

### 4. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f infrastructure/kubernetes/namespace.yaml

# Create configmap and secrets
kubectl apply -f infrastructure/kubernetes/configmap.yaml
kubectl apply -f infrastructure/kubernetes/secrets.yaml

# Deploy database
kubectl apply -f infrastructure/kubernetes/postgres-deployment.yaml

# Deploy Redis
kubectl apply -f infrastructure/kubernetes/redis-deployment.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n hishamos --timeout=300s

# Deploy backend
kubectl apply -f infrastructure/kubernetes/backend-deployment.yaml

# Deploy Celery
kubectl apply -f infrastructure/kubernetes/celery-deployment.yaml

# Deploy frontend
kubectl apply -f infrastructure/kubernetes/frontend-deployment.yaml

# Deploy ingress
kubectl apply -f infrastructure/kubernetes/ingress.yaml

# Deploy HPA
kubectl apply -f infrastructure/kubernetes/hpa.yaml
```

### 5. Run Database Migrations

```bash
# Run migrations (including performance views)
kubectl exec -n hishamos deployment/backend -- \
  python manage.py migrate --noinput

# Verify performance views created
kubectl exec -it -n hishamos deployment/postgres -- \
  psql -U hishamos -c "\dv" | grep -E "(agent_performance|command_usage|daily_system|user_activity|workflow_performance)"

# Create superuser (if needed)
kubectl exec -it -n hishamos deployment/backend -- \
  python manage.py createsuperuser

# Collect static files
kubectl exec -n hishamos deployment/backend -- \
  python manage.py collectstatic --noinput
```

### 6. Verify Deployment

```bash
# Check all pods
kubectl get pods -n hishamos

# Check services
kubectl get svc -n hishamos

# Check ingress
kubectl get ingress -n hishamos

# View logs
kubectl logs -f deployment/backend -n hishamos

# Test health endpoint
curl https://your-domain.com/api/v1/monitoring/health/

# Test Prometheus metrics endpoint
curl https://your-domain.com/api/v1/monitoring/prometheus/metrics/

# Test system health dashboard
curl https://your-domain.com/api/v1/monitoring/dashboard/health/
```

---

## 🔍 Post-Deployment Verification

### Smoke Tests

```bash
# Health check
curl https://your-domain.com/api/v1/monitoring/health/

# API authentication
curl -X POST https://your-domain.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Frontend accessibility
curl https://your-domain.com/
```

### Monitoring Checks

- [ ] Prometheus scraping metrics from `/api/v1/monitoring/prometheus/metrics/`
- [ ] Grafana dashboards showing data (import from `infrastructure/monitoring/grafana-dashboards/`)
- [ ] Alerts configured and working (see `infrastructure/monitoring/alert-rules.yaml`)
- [ ] JSON logs flowing (check `logs/django.json.log` if `USE_JSON_LOGGING=true`)
- [ ] Logs flowing to Loki (if configured)
- [ ] No error rates spiking
- [ ] Response times within targets
- [ ] Database performance views created (run migrations)
- [ ] Health checks responding correctly

**See `MONITORING_GUIDE.md` for detailed monitoring setup and configuration.**

---

## 🔄 Rollback Procedure

If deployment fails:

```bash
# Rollback to previous version
kubectl rollout undo deployment/backend -n hishamos
kubectl rollout undo deployment/frontend -n hishamos
kubectl rollout undo deployment/celery -n hishamos

# Verify rollback
kubectl rollout status deployment/backend -n hishamos
```

---

## 📊 Monitoring & Alerts

**For complete monitoring documentation, see `MONITORING_GUIDE.md`**

### Key Metrics to Monitor

1. **Application Health**
   - Pod status
   - Health check endpoints (`/api/v1/monitoring/dashboard/health/`)
   - Error rates (`hishamos_errors_total`)
   - System health (`hishamos_system_health`)

2. **Performance**
   - API response times (p95 < 200ms) - `hishamos_api_request_duration_seconds`
   - Database query times
   - Cache hit rates (`hishamos_cache_hits_total` / `hishamos_cache_misses_total`)
   - Agent execution times (`hishamos_agent_execution_duration_seconds`)

3. **Resources**
   - CPU usage (via node exporter)
   - Memory usage (via node exporter)
   - Disk usage (via node exporter)
   - Database connections (`hishamos_database_connections`)

4. **Business Metrics**
   - Active users (`hishamos_active_users`)
   - API requests per minute (`hishamos_api_requests_total`)
   - Workflow executions (`hishamos_workflow_executions_total`)
   - Agent executions (`hishamos_agent_executions_total`)
   - Total cost (`hishamos_agent_cost_total`)

### Prometheus Metrics

**Endpoint:** `/api/v1/monitoring/prometheus/metrics/`

**Available Metrics:**
- Agent metrics (executions, duration, tokens, cost)
- Command metrics (executions, duration)
- Workflow metrics (executions, duration)
- API metrics (requests, duration, status codes)
- System metrics (health, users, connections)
- Cache metrics (hits, misses)
- Error metrics

### Grafana Dashboards

**Location:** `infrastructure/monitoring/grafana-dashboards/`

**Available Dashboards:**
1. System Overview
2. Agent Performance
3. API Performance

**Import:** Via Grafana UI or API (see `MONITORING_GUIDE.md`)

### Alert Rules

See `infrastructure/monitoring/alert-rules.yaml` for configured alerts.

**Alert Channels:**
- Email (SMTP)
- Slack (Webhook)
- SMS (Twilio)
- Custom Webhooks

**For complete monitoring documentation, see `MONITORING_GUIDE.md`**

---

## 🔐 Security Post-Deployment

- [ ] Verify security headers in responses
- [ ] Test rate limiting
- [ ] Verify CORS configuration
- [ ] Check SSL/TLS configuration
- [ ] Review access logs
- [ ] Verify secrets are not exposed

---

## 📝 Maintenance

### Regular Tasks

1. **Daily:**
   - Monitor error rates (Grafana dashboard)
   - Check resource usage (Prometheus metrics)
   - Review security alerts
   - Review JSON logs for errors
   - Check Prometheus targets status

2. **Weekly:**
   - Review performance metrics (Grafana dashboards)
   - Check backup status
   - Update dependencies
   - Review database performance views
   - Analyze top error sources

3. **Monthly:**
   - Security audit
   - Performance optimization review
   - Capacity planning
   - Review and tune alert thresholds
   - Clean up old logs (if needed)

---

## 🆘 Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n hishamos

# Check logs
kubectl logs <pod-name> -n hishamos

# Check events
kubectl get events -n hishamos --sort-by='.lastTimestamp'
```

### Database Connection Issues

```bash
# Test database connection
kubectl exec -it -n hishamos deployment/backend -- \
  python manage.py dbshell

# Check database pod
kubectl logs -f deployment/postgres -n hishamos
```

### High Resource Usage

```bash
# Check resource usage
kubectl top pods -n hishamos

# Scale up if needed
kubectl scale deployment/backend --replicas=5 -n hishamos
```

---

**Last Updated:** December 8, 2024
