# HishamOS Monitoring Guide

**Version:** 1.0  
**Last Updated:** December 8, 2024  
**Status:** ✅ Complete

---

## 📊 Overview

HishamOS includes comprehensive monitoring capabilities with:
- **Structured JSON Logging** - For log aggregation and analysis
- **Prometheus Metrics** - For metrics collection and alerting
- **Grafana Dashboards** - For visualization and analytics
- **Database Performance Views** - For optimized analytics queries
- **Health Checks** - For system health monitoring

---

## 📝 Structured JSON Logging

### Overview

HishamOS supports structured JSON logging for production environments, enabling easy log aggregation and analysis with tools like Loki, ELK, or CloudWatch.

### Configuration

**Location:** `backend/core/settings/base.py`

**Environment Variable:**
```bash
USE_JSON_LOGGING=true  # Enable JSON logging
```

**Production:** JSON logging is enabled by default in `production.py`

### Log Format

JSON logs include:
- `timestamp` - ISO 8601 UTC timestamp
- `level` - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `logger` - Logger name
- `message` - Log message
- `module` - Python module name
- `function` - Function name
- `line` - Line number
- `process_id` - Process ID
- `thread_id` - Thread ID
- `exception` - Exception details (if present)
- `request_id` - Request ID (if available)
- `user_id` - User ID (if available)
- `ip_address` - Client IP (if available)
- `path` - Request path (if available)
- `method` - HTTP method (if available)

### Example Log Entry

```json
{
  "timestamp": "2024-12-08T10:30:45.123Z",
  "level": "INFO",
  "logger": "apps.agents.services.execution_engine",
  "message": "Agent execution completed",
  "module": "execution_engine",
  "function": "execute_agent",
  "line": 245,
  "process_id": 12345,
  "thread_id": 67890,
  "agent_id": "code-generator",
  "execution_time": 2.5,
  "tokens_used": 1500,
  "cost": 0.0025
}
```

### Log Files

- **Standard Log:** `logs/django.log` (verbose format)
- **JSON Log:** `logs/django.json.log` (JSON format, when enabled)

### Integration

**Loki:**
```yaml
# promtail-config.yaml
scrape_configs:
  - job_name: hishamos
    static_configs:
      - targets:
          - localhost
        labels:
          job: hishamos
          __path__: /app/logs/django.json.log
```

**CloudWatch:**
- Use CloudWatch Logs Agent to ship JSON logs
- Configure log group: `/aws/ecs/hishamos`

**ELK Stack:**
- Use Filebeat to collect JSON logs
- Configure Logstash to parse JSON format

---

## 📈 Prometheus Metrics

### Overview

HishamOS exposes Prometheus metrics at `/api/v1/monitoring/prometheus/metrics/`

### Available Metrics

#### Agent Metrics

- `hishamos_agent_executions_total` - Total agent executions (labels: `agent_id`, `status`)
- `hishamos_agent_execution_duration_seconds` - Execution duration histogram (labels: `agent_id`)
- `hishamos_agent_tokens_total` - Total tokens used (labels: `agent_id`, `platform`)
- `hishamos_agent_cost_total` - Total cost (labels: `agent_id`, `platform`)

#### Command Metrics

- `hishamos_command_executions_total` - Total command executions (labels: `command_id`, `status`)
- `hishamos_command_execution_duration_seconds` - Execution duration histogram (labels: `command_id`)

#### Workflow Metrics

- `hishamos_workflow_executions_total` - Total workflow executions (labels: `workflow_id`, `status`)
- `hishamos_workflow_execution_duration_seconds` - Execution duration histogram (labels: `workflow_id`)

#### API Metrics

- `hishamos_api_requests_total` - Total API requests (labels: `method`, `endpoint`, `status_code`)
- `hishamos_api_request_duration_seconds` - Request duration histogram (labels: `method`, `endpoint`)

#### System Metrics

- `hishamos_active_users` - Number of active users (gauge)
- `hishamos_system_health` - System health status (gauge, labels: `component`)
- `hishamos_database_connections` - Active database connections (gauge)
- `hishamos_cache_hits_total` - Cache hits (counter, labels: `cache_type`)
- `hishamos_cache_misses_total` - Cache misses (counter, labels: `cache_type`)
- `hishamos_errors_total` - Total errors (counter, labels: `error_type`, `component`)

### Prometheus Configuration

**Location:** `infrastructure/monitoring/prometheus-config.yaml`

**Scrape Configuration:**
```yaml
scrape_configs:
  - job_name: 'backend'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - hishamos
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: backend
      - source_labels: [__meta_kubernetes_pod_ip]
        action: replace
        target_label: __address__
        replacement: $1:8000
    metrics_path: '/api/v1/monitoring/prometheus/metrics/'
```

### Recording Metrics

**In Code:**
```python
from apps.monitoring.prometheus_metrics import (
    record_agent_execution,
    record_api_request,
    record_error,
    set_system_health
)

# Record agent execution
record_agent_execution(
    agent_id='code-generator',
    status='completed',
    duration=2.5,
    tokens=1500,
    cost=0.0025,
    platform='openai'
)

# Record API request
record_api_request(
    method='POST',
    endpoint='/api/v1/agents/execute/',
    status_code=200,
    duration=0.5
)

# Record error
record_error(
    error_type='ValidationError',
    component='agents'
)

# Set system health
set_system_health('database', healthy=True)
```

### Alert Rules

**Location:** `infrastructure/monitoring/alert-rules.yaml`

**Example Alerts:**
- High error rate (> 5% of requests)
- Slow API responses (P95 > 2 seconds)
- High agent failure rate (> 10%)
- System component unhealthy
- High cost threshold exceeded

---

## 📊 Grafana Dashboards

### Available Dashboards

**Location:** `infrastructure/monitoring/grafana-dashboards/`

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

### Importing Dashboards

**Method 1: Via Grafana UI**
1. Open Grafana → Dashboards → Import
2. Upload JSON file or paste JSON content
3. Select Prometheus data source
4. Click "Import"

**Method 2: Via API**
```bash
curl -X POST \
  http://grafana:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -d @infrastructure/monitoring/grafana-dashboards/system-overview.json
```

**Method 3: Via ConfigMap (Kubernetes)**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards
  namespace: monitoring
data:
  system-overview.json: |
    { ... dashboard JSON ... }
```

### Dashboard Access

- **URL:** `http://grafana:3000`
- **Default Credentials:** `admin/admin` (change on first login)
- **Data Source:** Prometheus (configured automatically)

---

## 🗄️ Database Performance Views

### Overview

Optimized database views for analytics and reporting without impacting application performance.

### Available Views

**Location:** `backend/apps/monitoring/migrations/0002_performance_views.py`

1. **agent_performance_summary**
   - Agent execution statistics
   - Success rates
   - Average execution times
   - Total tokens and cost

2. **command_usage_statistics**
   - Command execution counts
   - Success/failure rates
   - Average execution times
   - Total tokens and cost

3. **daily_system_metrics**
   - Daily aggregated metrics (last 30 days)
   - Total executions
   - Success/failure counts
   - Total tokens and cost
   - Average execution times

4. **user_activity_summary**
   - User activity across agents, commands, workflows
   - Total tokens used
   - Total cost
   - Last activity timestamp

5. **workflow_performance_summary**
   - Workflow execution statistics
   - Success rates
   - Average execution times
   - Running executions count

### Usage

**Query Example:**
```sql
-- Get top performing agents
SELECT 
    agent_name,
    total_executions,
    success_rate,
    avg_execution_time
FROM agent_performance_summary
ORDER BY success_rate DESC
LIMIT 10;

-- Get daily metrics
SELECT 
    date,
    total_agent_executions,
    successful_executions,
    total_cost
FROM daily_system_metrics
ORDER BY date DESC
LIMIT 7;

-- Get user activity
SELECT 
    email,
    agent_executions_count,
    command_executions_count,
    total_cost
FROM user_activity_summary
ORDER BY total_cost DESC;
```

### Migration

**Apply Views:**
```bash
python manage.py migrate monitoring
```

**Rollback:**
```bash
python manage.py migrate monitoring 0001
```

---

## 🏥 Health Checks

### Endpoints

**System Health:**
```
GET /api/v1/monitoring/dashboard/health/
```

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "database": {"status": "healthy", "response_time_ms": 5},
    "cache": {"status": "healthy", "response_time_ms": 2},
    "celery": {"status": "healthy"},
    "websocket": {"status": "healthy"}
  },
  "timestamp": "2024-12-08T10:30:45Z"
}
```

**Health Check (Prometheus):**
```
GET /api/v1/monitoring/health/
```

### Kubernetes Health Probes

**Liveness Probe:**
```yaml
livenessProbe:
  httpGet:
    path: /api/v1/monitoring/health/
    port: 8000
  initialDelaySeconds: 40
  periodSeconds: 30
  timeoutSeconds: 10
```

**Readiness Probe:**
```yaml
readinessProbe:
  httpGet:
    path: /api/v1/monitoring/health/
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
```

---

## 🔔 Alerting

### Alert Rules

**Location:** `infrastructure/monitoring/alert-rules.yaml`

**Configured Alerts:**
- High error rate (> 5%)
- Slow API responses (P95 > 2s)
- High agent failure rate (> 10%)
- System component unhealthy
- High cost threshold
- Database connection issues
- Cache unavailability

### Alert Channels

**Supported:**
- Email (SMTP)
- Slack (Webhook)
- SMS (Twilio)
- Webhook (Custom)

**Configuration:**
```python
# settings/base.py
ALERTING_ENABLED = True
ALERTING_EMAIL_RECIPIENTS = ['ops@example.com']
ALERTING_SLACK_WEBHOOK_URL = 'https://hooks.slack.com/...'
TWILIO_ACCOUNT_SID = '...'
TWILIO_AUTH_TOKEN = '...'
TWILIO_FROM_NUMBER = '+1234567890'
```

---

## 📋 Monitoring Checklist

### Setup Checklist

- [ ] Enable JSON logging in production
- [ ] Deploy Prometheus server
- [ ] Configure Prometheus scraping
- [ ] Import Grafana dashboards
- [ ] Configure alert rules
- [ ] Set up alert channels (Email/Slack/SMS)
- [ ] Apply database performance views migration
- [ ] Configure health check probes in Kubernetes
- [ ] Test metrics collection
- [ ] Verify dashboard data
- [ ] Test alert notifications

### Daily Operations

- [ ] Review Grafana dashboards
- [ ] Check error rates
- [ ] Monitor API response times
- [ ] Review agent performance
- [ ] Check system health status
- [ ] Review cost metrics
- [ ] Check alert notifications

### Weekly Operations

- [ ] Review weekly performance trends
- [ ] Analyze top error sources
- [ ] Review user activity patterns
- [ ] Optimize slow queries
- [ ] Review and tune alert thresholds
- [ ] Clean up old logs (if needed)

---

## 🛠️ Troubleshooting

### Metrics Not Appearing

1. **Check Prometheus Configuration:**
   ```bash
   kubectl get configmap prometheus-config -n monitoring -o yaml
   ```

2. **Verify Scrape Targets:**
   - Access Prometheus UI: `http://prometheus:9090/targets`
   - Check if backend target is UP

3. **Check Metrics Endpoint:**
   ```bash
   curl http://backend:8000/api/v1/monitoring/prometheus/metrics/
   ```

### Logs Not Appearing

1. **Check Log Configuration:**
   ```bash
   # Check if JSON logging is enabled
   echo $USE_JSON_LOGGING
   ```

2. **Verify Log Files:**
   ```bash
   kubectl exec -it deployment/backend -n hishamos -- ls -la /app/logs/
   ```

3. **Check Log Format:**
   ```bash
   kubectl exec -it deployment/backend -n hishamos -- \
     tail -n 1 /app/logs/django.json.log | jq .
   ```

### Dashboard Not Loading

1. **Check Data Source:**
   - Grafana → Configuration → Data Sources
   - Verify Prometheus connection

2. **Check Query:**
   - Open dashboard → Edit panel
   - Verify PromQL query syntax

3. **Check Time Range:**
   - Ensure time range includes data
   - Check if metrics are being collected

---

## 📚 Additional Resources

- **Prometheus Documentation:** https://prometheus.io/docs/
- **Grafana Documentation:** https://grafana.com/docs/
- **Loki Documentation:** https://grafana.com/docs/loki/
- **PromQL Guide:** https://prometheus.io/docs/prometheus/latest/querying/basics/

---

## 🔄 Updates

**December 8, 2024:**
- ✅ Added structured JSON logging
- ✅ Implemented Prometheus metrics exporters
- ✅ Created Grafana dashboards
- ✅ Added database performance views
- ✅ Enhanced health check endpoints

---

**Last Updated:** December 8, 2024  
**Maintainer:** DevOps Team

