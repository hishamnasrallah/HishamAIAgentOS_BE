---
title: "HishamOS - حلول الفجوات (الجزء 2)"
description: "Documentation file"

category: "Core"
language: "ar"
original_language: "ar"

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
  - core

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

# HishamOS - حلول الفجوات (الجزء 2)
## النقاط 5-10

---

# 5. Secrets Management

## 5.1 HashiCorp Vault Integration

```python
import hvac
from typing import Dict, Optional
from cryptography.fernet import Fernet

class SecretsManager:
    """
    إدارة Secrets بشكل آمن
    """
    def __init__(
        self,
        vault_url: str,
        vault_token: Optional[str] = None
    ):
        self.client = hvac.Client(
            url=vault_url,
            token=vault_token or os.getenv('VAULT_TOKEN')
        )
        
        # Fallback to local encryption if Vault unavailable
        self.fernet = Fernet(os.getenv('ENCRYPTION_KEY').encode())
        self.use_vault = self.client.is_authenticated()
    
    async def store_secret(
        self,
        path: str,
        secret_data: Dict,
        metadata: Optional[Dict] = None
    ):
        """
        تخزين secret
        """
        if self.use_vault:
            # Store in Vault
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secret_data,
                metadata=metadata
            )
        else:
            # Fallback: Encrypt and store in database
            encrypted = self._encrypt_local(secret_data)
            await self.db.secrets.create({
                'path': path,
                'data': encrypted,
                'metadata': metadata
            })
    
    async def get_secret(self, path: str) -> Dict:
        """
        الحصول على secret
        """
        if self.use_vault:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path
            )
            return response['data']['data']
        else:
            # Fallback: Get from database and decrypt
            secret_record = await self.db.secrets.find_one({'path': path})
            if secret_record:
                return self._decrypt_local(secret_record['data'])
            raise SecretNotFoundError(f"Secret not found: {path}")
    
    async def rotate_secret(
        self,
        path: str,
        new_value: Dict,
        notify: bool = True
    ):
        """
        تدوير Secret
        """
        # Store old version
        old_secret = await self.get_secret(path)
        await self.store_secret(
            f"{path}/versions/backup",
            old_secret,
            metadata={'rotated_at': datetime.utcnow()}
        )
        
        # Store new version
        await self.store_secret(path, new_value)
        
        # Notify services if needed
        if notify:
            await self._notify_secret_rotation(path)
    
    async def get_ai_api_key(self, platform: str) -> str:
        """
        الحصول على AI API Key بشكل آمن
        """
        secret_path = f"ai/platforms/{platform}"
        secret = await self.get_secret(secret_path)
        return secret.get('api_key')
    
    async def store_ai_api_key(
        self,
        platform: str,
        api_key: str,
        additional_config: Optional[Dict] = None
    ):
        """
        تخزين AI API Key
        """
        secret_data = {
            'api_key': api_key,
            'platform': platform,
            'created_at': datetime.utcnow().isoformat()
        }
        
        if additional_config:
            secret_data.update(additional_config)
        
        await self.store_secret(
            f"ai/platforms/{platform}",
            secret_data,
            metadata={'platform': platform}
        )
    
    def _encrypt_local(self, data: Dict) -> str:
        """
        تشفير محلي كـ fallback
        """
        json_data = json.dumps(data)
        return self.fernet.encrypt(json_data.encode()).decode()
    
    def _decrypt_local(self, encrypted: str) -> Dict:
        """
        فك تشفير محلي
        """
        decrypted = self.fernet.decrypt(encrypted.encode()).decode()
        return json.loads(decrypted)

class PlatformCredentialsManager:
    """
    إدارة credentials للمنصات المختلفة
    """
    def __init__(self, secrets_manager: SecretsManager):
        self.secrets = secrets_manager
        self.credentials_cache = {}
    
    async def get_platform_credentials(
        self,
        platform: str
    ) -> Dict:
        """
        الحصول على credentials مع caching آمن
        """
        # Check cache first (memory only, not persisted)
        if platform in self.credentials_cache:
            return self.credentials_cache[platform]
        
        # Get from secrets manager
        api_key = await self.secrets.get_ai_api_key(platform)
        
        # Cache for performance (cleared on restart)
        self.credentials_cache[platform] = {
            'api_key': api_key,
            'cached_at': datetime.utcnow()
        }
        
        return self.credentials_cache[platform]
    
    async def rotate_platform_key(
        self,
        platform: str,
        new_key: str
    ):
        """
        تدوير API Key لمنصة
        """
        await self.secrets.rotate_secret(
            f"ai/platforms/{platform}",
            {'api_key': new_key}
        )
        
        # Clear cache
        if platform in self.credentials_cache:
            del self.credentials_cache[platform]
```

## 5.2 Environment Variables Management

```python
# .env.example (Template)
# Copy to .env and fill in actual values

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hishamos
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Encryption
ENCRYPTION_KEY=your-encryption-key-32-chars-min

# Vault (Optional)
VAULT_URL=http://localhost:8200
VAULT_TOKEN=your-vault-token

# AI Platforms (Store in Vault in production)
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...
GEMINI_API_KEY=...
OPENROUTER_API_KEY=...

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=admin

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-app-password

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_BOT_TOKEN=xoxb-...

# Misc
ENVIRONMENT=production|staging|development
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
MAX_CONCURRENT_WORKFLOWS=100
MAX_CONCURRENT_TASKS_PER_AGENT=5
```

---

# 6. Alerting System

## 6.1 Alert Manager

```python
from enum import Enum
from typing import List, Callable
from dataclasses import dataclass

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    SMS = "sms"

@dataclass
class AlertRule:
    name: str
    condition: Callable
    severity: AlertSeverity
    channels: List[AlertChannel]
    cooldown_minutes: int
    message_template: str

class AlertManager:
    """
    نظام تنبيهات متقدم
    """
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alert_history = {}
        self.channels = {
            AlertChannel.EMAIL: EmailAlertChannel(),
            AlertChannel.SLACK: SlackAlertChannel(),
            AlertChannel.PAGERDUTY: PagerDutyAlertChannel(),
        }
        
        self._register_default_rules()
    
    def _register_default_rules(self):
        """
        تسجيل Alert Rules الافتراضية
        """
        # High Error Rate
        self.rules.append(AlertRule(
            name="high_error_rate",
            condition=lambda metrics: metrics['error_rate'] > 0.05,
            severity=AlertSeverity.WARNING,
            channels=[AlertChannel.SLACK],
            cooldown_minutes=15,
            message_template="⚠️ High error rate detected: {error_rate:.2%}"
        ))
        
        # Workflow Failure
        self.rules.append(AlertRule(
            name="workflow_failed",
            condition=lambda event: event['type'] == 'workflow_failed',
            severity=AlertSeverity.ERROR,
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
            cooldown_minutes=0,  # No cooldown, alert every time
            message_template="❌ Workflow failed: {workflow_name} - {error}"
        ))
        
        # High Cost
        self.rules.append(AlertRule(
            name="high_cost",
            condition=lambda metrics: metrics['cost_today'] > 100.0,
            severity=AlertSeverity.WARNING,
            channels=[AlertChannel.EMAIL],
            cooldown_minutes=60,
            message_template="💰 High cost alert: ${cost_today:.2f} today"
        ))
        
        # Platform Down
        self.rules.append(AlertRule(
            name="platform_down",
            condition=lambda health: not health['openai'] or not health['claude'],
            severity=AlertSeverity.CRITICAL,
            channels=[AlertChannel.SLACK, AlertChannel.PAGERDUTY],
            cooldown_minutes=5,
            message_template="🚨 AI Platform DOWN: {platform}"
        ))
        
        # Low Quality Scores
        self.rules.append(AlertRule(
            name="low_quality",
            condition=lambda metrics: metrics['avg_quality_score'] < 6.0,
            severity=AlertSeverity.WARNING,
            channels=[AlertChannel.SLACK],
            cooldown_minutes=30,
            message_template="📉 Low quality scores: {avg_quality_score:.1f}/10"
        ))
        
        # Database Connection Issues
        self.rules.append(AlertRule(
            name="db_connection_pool_exhausted",
            condition=lambda metrics: metrics['db_pool_usage'] > 0.9,
            severity=AlertSeverity.CRITICAL,
            channels=[AlertChannel.SLACK, AlertChannel.EMAIL],
            cooldown_minutes=10,
            message_template="🔴 Database connection pool at {db_pool_usage:.0%}"
        ))
    
    async def check_rules(self, context: Dict):
        """
        فحص جميع القواعد
        """
        for rule in self.rules:
            try:
                if rule.condition(context):
                    await self._trigger_alert(rule, context)
            except Exception as e:
                logger.error(f"Error checking alert rule {rule.name}: {e}")
    
    async def _trigger_alert(
        self,
        rule: AlertRule,
        context: Dict
    ):
        """
        إطلاق تنبيه
        """
        # Check cooldown
        if not self._check_cooldown(rule.name, rule.cooldown_minutes):
            logger.debug(f"Alert {rule.name} in cooldown, skipping")
            return
        
        # Format message
        message = rule.message_template.format(**context)
        
        # Send to all channels
        tasks = []
        for channel in rule.channels:
            if channel in self.channels:
                task = self.channels[channel].send(
                    message=message,
                    severity=rule.severity,
                    context=context
                )
                tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Record in history
        self._record_alert(rule.name)
    
    def _check_cooldown(
        self,
        rule_name: str,
        cooldown_minutes: int
    ) -> bool:
        """
        فحص cooldown period
        """
        if cooldown_minutes == 0:
            return True
        
        if rule_name in self.alert_history:
            last_alert = self.alert_history[rule_name]
            elapsed = (datetime.utcnow() - last_alert).total_seconds() / 60
            return elapsed >= cooldown_minutes
        
        return True
    
    def _record_alert(self, rule_name: str):
        """
        تسجيل تنبيه في التاريخ
        """
        self.alert_history[rule_name] = datetime.utcnow()

class SlackAlertChannel:
    """
    إرسال التنبيهات عبر Slack
    """
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    async def send(
        self,
        message: str,
        severity: AlertSeverity,
        context: Dict
    ):
        """
        إرسال إلى Slack
        """
        color = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9800",
            AlertSeverity.ERROR: "#f44336",
            AlertSeverity.CRITICAL: "#b71c1c"
        }[severity]
        
        payload = {
            "attachments": [{
                "color": color,
                "title": f"{severity.value.upper()} Alert",
                "text": message,
                "fields": [
                    {"title": k, "value": str(v), "short": True}
                    for k, v in context.items()
                ],
                "footer": "HishamOS",
                "ts": int(datetime.utcnow().timestamp())
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook_url, json=payload)
```

## 6.2 Prometheus Alerting Rules

```yaml
# prometheus_alerts.yml
groups:
  - name: hishamos_alerts
    interval: 30s
    rules:
      # High Error Rate
      - alert: HighErrorRate
        expr: rate(hishamos_agent_executions_total{status="failed"}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}% for the last 5 minutes"
      
      # Workflow Duration Too Long
      - alert: WorkflowDurationHigh
        expr: histogram_quantile(0.95, rate(hishamos_workflow_duration_seconds_bucket[5m])) > 3600
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Workflow duration is too high"
          description: "95th percentile is {{ $value }} seconds"
      
      # High API Cost
      - alert: HighAPICost
        expr: increase(hishamos_ai_cost_dollars_total[1h]) > 50
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API costs are high"
          description: "Spent ${{ $value }} in the last hour"
      
      # Agent Down
      - alert: AgentDown
        expr: hishamos_active_agents == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "No active agents"
          description: "All agents are down or inactive"
```

---

# 7. Feedback Loop & ML Pipeline

## 7.1 Quality Scoring System

```python
from typing import Dict, List
from sklearn.ensemble import RandomForestRegressor
import numpy as np

class QualityScorer:
    """
    تقييم جودة النتائج
    """
    def __init__(self):
        self.model = None
        self.features = [
            'prompt_length',
            'response_length',
            'tokens_used',
            'response_time',
            'agent_average_score',
            'command_difficulty',
            'has_code',
            'has_examples',
            'has_self_critique'
        ]
    
    def score_output(
        self,
        output: Dict,
        agent: Agent,
        command: CommandTemplate
    ) -> float:
        """
        تسجيل جودة المخرجات (0-10)
        """
        scores = []
        
        # 1. Completeness (30%)
        completeness = self._score_completeness(output, command)
        scores.append(completeness * 0.30)
        
        # 2. Clarity (20%)
        clarity = self._score_clarity(output)
        scores.append(clarity * 0.20)
        
        # 3. Correctness (25%)
        correctness = self._score_correctness(output)
        scores.append(correctness * 0.25)
        
        # 4. Depth (15%)
        depth = self._score_depth(output)
        scores.append(depth * 0.15)
        
        # 5. Formatting (10%)
        formatting = self._score_formatting(output)
        scores.append(formatting * 0.10)
        
        total_score = sum(scores) * 10  # Scale to 0-10
        
        return round(total_score, 2)
    
    def _score_completeness(
        self,
        output: Dict,
        command: CommandTemplate
    ) -> float:
        """
        تقييم الاكتمال
        """
        required_fields = command.output_schema.keys()
        present_fields = [
            f for f in required_fields 
            if f in output and output[f]
        ]
        
        return len(present_fields) / len(required_fields)
    
    def _score_clarity(self, output: Dict) -> float:
        """
        تقييم الوضوح
        """
        text = str(output.get('results', ''))
        
        # Check for clear structure
        has_headings = '##' in text or '###' in text
        has_lists = '-' in text or '*' in text or '1.' in text
        has_examples = 'example' in text.lower()
        
        score = 0.0
        if has_headings: score += 0.4
        if has_lists: score += 0.3
        if has_examples: score += 0.3
        
        return min(1.0, score)
    
    def _score_correctness(self, output: Dict) -> float:
        """
        تقييم الصحة (placeholder - يحتاج ML)
        """
        # This would ideally use ML model trained on user feedback
        # For now, use heuristics
        
        if self.model:
            features = self._extract_features(output)
            prediction = self.model.predict([features])[0]
            return prediction / 10.0
        
        # Fallback: assume high quality if no errors
        return 0.8

class FeedbackCollector:
    """
    جمع feedback من المستخدمين
    """
    async def collect_feedback(
        self,
        task_id: str,
        user_id: str,
        rating: int,  # 1-5
        feedback_text: str,
        issues: List[str] = []
    ):
        """
        جمع feedback
        """
        feedback = {
            'task_id': task_id,
            'user_id': user_id,
            'rating': rating,
            'feedback': feedback_text,
            'issues': issues,
            'created_at': datetime.utcnow()
        }
        
        # Store in database
        await db.task_feedback.create(feedback)
        
        # Trigger ML pipeline for retraining
        await self._trigger_ml_pipeline(task_id, rating)
    
    async def _trigger_ml_pipeline(
        self,
        task_id: str,
        rating: int
    ):
        """
        تشغيل ML pipeline
        """
        # Queue for async processing
        await ml_queue.enqueue(
            'retrain_quality_model',
            task_id=task_id,
            rating=rating
        )

class MLPipeline:
    """
    Machine Learning Pipeline للتحسين المستمر
    """
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
        self.training_data = []
    
    async def retrain_model(self):
        """
        إعادة تدريب النموذج
        """
        # Get feedback data
        feedback_data = await db.task_feedback.find({
            'created_at': {'$gte': datetime.utcnow() - timedelta(days=30)}
        })
        
        if len(feedback_data) < 100:
            logger.info("Not enough data for retraining yet")
            return
        
        # Prepare training data
        X = []
        y = []
        
        for feedback in feedback_data:
            # Get task result
            task = await db.task_results.get(feedback['task_id'])
            
            # Extract features
            features = self._extract_features(task)
            X.append(features)
            
            # Target: user rating scaled to 0-10
            y.append(feedback['rating'] * 2)
        
        # Train model
        self.model.fit(X, y)
        
        # Save model
        await self._save_model()
        
        logger.info(f"Model retrained with {len(X)} samples")
    
    def _extract_features(self, task: Dict) -> List[float]:
        """
        استخراج features للتدريب
        """
        return [
            len(task.get('summary', '')),
            len(str(task.get('results', ''))),
            task.get('tokens_used', 0),
            task.get('duration_seconds', 0),
            task.get('agent', {}).get('average_quality_score', 7.0),
            float('has_code' in str(task.get('results', '')).lower()),
            float(len(task.get('improvements', [])) > 0),
            float(len(task.get('alternatives', [])) > 0),
        ]

class TemplateOptimizer:
    """
    تحسين Command Templates تلقائياً
    """
    async def optimize_template(
        self,
        template_id: str
    ):
        """
        تحسين template بناءً على النتائج
        """
        # Get executions using this template
        executions = await db.task_results.find({
            'command_id': template_id
        }).limit(100)
        
        # Analyze patterns
        high_quality = [e for e in executions if e['quality_score'] >= 8.0]
        low_quality = [e for e in executions if e['quality_score'] < 6.0]
        
        if len(high_quality) < 10:
            logger.info(f"Not enough data to optimize template {template_id}")
            return
        
        # Find common patterns in high quality
        improvements = self._analyze_patterns(high_quality, low_quality)
        
        # Suggest template modifications
        await self._suggest_modifications(template_id, improvements)
    
    def _analyze_patterns(
        self,
        high_quality: List,
        low_quality: List
    ) -> Dict:
        """
        تحليل الأنماط
        """
        improvements = {
            'add_sections': [],
            'remove_sections': [],
            'modify_instructions': []
        }
        
        # Analyze what high quality outputs have
        high_patterns = self._extract_patterns(high_quality)
        low_patterns = self._extract_patterns(low_quality)
        
        # Identify differences
        unique_to_high = set(high_patterns) - set(low_patterns)
        
        for pattern in unique_to_high:
            improvements['add_sections'].append(pattern)
        
        return improvements
```

---

**سيتم إكمال النقاط 8-10 في ملف منفصل...**
