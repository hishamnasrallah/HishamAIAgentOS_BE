# Operations Runbook

**Version:** 1.0  
**Last Updated:** December 8, 2024

---

## 🚨 Incident Response

### Severity Levels

- **P0 - Critical:** System down, data loss, security breach
- **P1 - High:** Major feature broken, significant performance degradation
- **P2 - Medium:** Minor feature broken, moderate performance issues
- **P3 - Low:** Cosmetic issues, minor bugs

### Response Procedures

#### P0 - Critical Incident

1. **Immediate Actions:**
   - Assess impact
   - Notify team via Slack/email
   - Check monitoring dashboards
   - Review recent deployments

2. **Investigation:**
   ```bash
   # Check pod status
   kubectl get pods -n hishamos
   
   # Check logs
   kubectl logs -f deployment/backend -n hishamos
   
   # Check metrics
   # Access Grafana dashboards
   ```

3. **Resolution:**
   - Fix root cause
   - Deploy hotfix if needed
   - Verify fix
   - Monitor for 1 hour

4. **Post-Incident:**
   - Document incident
   - Root cause analysis
   - Update runbook
   - Team retrospective

---

## 🔧 Common Operations

### Restart Services

```bash
# Restart backend
kubectl rollout restart deployment/backend -n hishamos

# Restart frontend
kubectl rollout restart deployment/frontend -n hishamos

# Restart Celery
kubectl rollout restart deployment/celery -n hishamos
```

### Scale Services

```bash
# Scale backend
kubectl scale deployment/backend --replicas=5 -n hishamos

# Scale Celery workers
kubectl scale deployment/celery --replicas=3 -n hishamos
```

### View Logs

```bash
# Backend logs (standard format)
kubectl logs -f deployment/backend -n hishamos

# Backend JSON logs (structured)
kubectl exec -it deployment/backend -n hishamos -- \
  tail -f /app/logs/django.json.log | jq .

# Celery logs
kubectl logs -f deployment/celery -n hishamos

# All pods logs
kubectl logs -f -l app=backend -n hishamos

# Search logs (JSON format)
kubectl exec -it deployment/backend -n hishamos -- \
  grep -h "ERROR" /app/logs/django.json.log | jq .
```

### Database Operations

```bash
# Access database shell
kubectl exec -it -n hishamos deployment/postgres -- psql -U hishamos

# Run migrations
kubectl exec -n hishamos deployment/backend -- \
  python manage.py migrate

# Create backup
kubectl exec -n hishamos deployment/postgres -- \
  pg_dump -U hishamos hishamos > backup.sql
```

---

## 🔄 Deployment Procedures

### Standard Deployment

1. **Pre-Deployment:**
   - Run tests: `pytest`
   - Review changes
   - Update version tag

2. **Deployment:**
   - Push code to main branch
   - CI/CD pipeline builds and deploys
   - Monitor deployment status

3. **Post-Deployment:**
   - Verify health endpoints
   - Check error rates
   - Monitor for 30 minutes

### Hotfix Deployment

1. Create hotfix branch
2. Make fix
3. Test locally
4. Deploy to staging
5. Verify fix
6. Deploy to production
7. Monitor closely

---

## 📊 Monitoring & Alerts

**For complete monitoring documentation, see `MONITORING_GUIDE.md`**

### Key Dashboards

1. **System Overview** (`system-overview.json`)
   - Agent execution rate
   - API request rate
   - System health status
   - Active users
   - Total cost
   - Error rate

2. **Agent Performance** (`agent-performance.json`)
   - Agent execution duration (P50, P95)
   - Agent success rate
   - Tokens used by agent
   - Cost by platform

3. **API Performance** (`api-performance.json`)
   - API request rate by endpoint
   - API response time (P95)
   - API error rate
   - HTTP status codes

### Metrics Endpoint

```bash
# Prometheus metrics
curl http://backend:8000/api/v1/monitoring/prometheus/metrics/
```

### Alert Channels

- **Slack:** Webhook configured via `ALERTING_SLACK_WEBHOOK_URL`
- **Email:** Recipients via `ALERTING_EMAIL_RECIPIENTS`
- **SMS:** Twilio via `TWILIO_*` settings
- **Webhook:** Custom webhook URLs

### Database Performance Views

```sql
-- Query agent performance
SELECT * FROM agent_performance_summary ORDER BY success_rate DESC LIMIT 10;

-- Query daily metrics
SELECT * FROM daily_system_metrics ORDER BY date DESC LIMIT 7;
```

---

## 🔐 Security Operations

### Secret Rotation

```bash
# Update secret in Kubernetes
kubectl create secret generic hishamos-secrets \
  --from-literal=SECRET_KEY='new-secret-key' \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secrets
kubectl rollout restart deployment/backend -n hishamos
```

### Security Audit

1. Review access logs
2. Check for suspicious activity
3. Verify security headers
4. Review API key usage
5. Check for vulnerabilities

---

## 💾 Backup & Recovery

### Database Backup

```bash
# Automated backup (daily)
kubectl create job --from=cronjob/postgres-backup postgres-backup-manual -n hishamos

# Manual backup
kubectl exec -n hishamos deployment/postgres -- \
  pg_dump -U hishamos hishamos > backup-$(date +%Y%m%d).sql
```

### Restore from Backup

```bash
# Restore database
kubectl exec -i -n hishamos deployment/postgres -- \
  psql -U hishamos hishamos < backup-20241208.sql
```

---

## 🐛 Troubleshooting Guide

### High Error Rate

1. Check application logs
2. Review recent deployments
3. Check database connectivity
4. Verify external API availability
5. Check resource limits

### Slow Response Times

1. Check database query performance
2. Review cache hit rates
3. Check resource usage
4. Review recent code changes
5. Check for N+1 queries

### Database Issues

1. Check database pod status
2. Review connection pool settings
3. Check for long-running queries
4. Review database logs
5. Check disk space

---

## 📞 Escalation

### On-Call Rotation

- **Primary:** [Team Member 1]
- **Secondary:** [Team Member 2]
- **Escalation:** [Tech Lead]

### Escalation Path

1. **Level 1:** On-call engineer
2. **Level 2:** Team lead
3. **Level 3:** CTO/Engineering Manager

---

**Last Updated:** December 8, 2024

