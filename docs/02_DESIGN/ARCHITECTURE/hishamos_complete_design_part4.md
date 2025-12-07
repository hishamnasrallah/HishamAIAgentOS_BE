---
title: "HishamOS - التصميم الكامل (الجزء 4/5)"
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

# HishamOS - التصميم الكامل (الجزء 4/5)
## Database + Integration + Security

---

# 10. قاعدة البيانات Database Design

## 10.1 Database Schema - PostgreSQL

### الجداول الرئيسية Core Tables

#### 1. users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    department VARCHAR(100),
    role_id UUID REFERENCES roles(id),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    two_factor_enabled BOOLEAN DEFAULT false,
    two_factor_secret VARCHAR(255),
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

#### 2. roles
```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '[]',
    is_system_role BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default roles
INSERT INTO roles (name, description, permissions, is_system_role) VALUES
('admin', 'System Administrator', '["*"]', true),
('ceo', 'Chief Executive Officer', '["view_all", "create_workflow", "approve_workflow"]', true),
('cto', 'Chief Technology Officer', '["view_tech", "create_workflow", "manage_agents"]', true),
('developer', 'Software Developer', '["view_own", "create_task", "use_coding_agent"]', true),
('legal', 'Legal Team', '["view_legal", "create_legal_task", "use_legal_agent"]', true);
```

#### 3. agents
```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    capabilities JSONB NOT NULL DEFAULT '[]',
    system_prompt TEXT NOT NULL,
    model_config JSONB NOT NULL,
    preferred_platform VARCHAR(50) NOT NULL,
    fallback_platforms JSONB DEFAULT '[]',
    constraints JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    enable_self_review BOOLEAN DEFAULT true,
    enable_streaming BOOLEAN DEFAULT false,
    timeout_seconds INTEGER DEFAULT 300,
    retry_policy JSONB,
    department VARCHAR(100),
    tags JSONB DEFAULT '[]',
    version INTEGER DEFAULT 1,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agents_department ON agents(department);
CREATE INDEX idx_agents_active ON agents(is_active);
```

#### 4. agent_metrics
```sql
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    total_executions INTEGER DEFAULT 0,
    successful_executions INTEGER DEFAULT 0,
    failed_executions INTEGER DEFAULT 0,
    average_quality_score DECIMAL(3,2) DEFAULT 0,
    average_response_time DECIMAL(10,2) DEFAULT 0,
    average_cost DECIMAL(10,4) DEFAULT 0,
    total_tokens_used BIGINT DEFAULT 0,
    last_execution_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_agent_metrics_agent ON agent_metrics(agent_id);
```

#### 5. command_templates
```sql
CREATE TABLE command_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    command_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    agent_ids JSONB NOT NULL DEFAULT '[]',
    template TEXT NOT NULL,
    parameters JSONB NOT NULL DEFAULT '[]',
    output_schema JSONB,
    quality_metrics JSONB DEFAULT '[]',
    examples JSONB DEFAULT '[]',
    estimated_duration_minutes INTEGER,
    difficulty_level VARCHAR(20),
    tags JSONB DEFAULT '[]',
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_commands_category ON command_templates(category);
CREATE INDEX idx_commands_active ON command_templates(is_active);
```

#### 6. workflows
```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    department VARCHAR(100),
    trigger_type VARCHAR(50) NOT NULL,
    schedule_cron VARCHAR(100),
    status VARCHAR(50) DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    tags JSONB DEFAULT '[]',
    estimated_duration_minutes INTEGER,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflows_department ON workflows(department);
CREATE INDEX idx_workflows_status ON workflows(status);
```

#### 7. workflow_steps
```sql
CREATE TABLE workflow_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    agent_id UUID REFERENCES agents(id),
    command_template_id UUID REFERENCES command_templates(id),
    input_mapping JSONB NOT NULL DEFAULT '{}',
    output_mapping JSONB NOT NULL DEFAULT '{}',
    timeout_seconds INTEGER DEFAULT 300,
    retry_policy JSONB,
    dependencies JSONB DEFAULT '[]',
    parallel BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(workflow_id, step_order)
);

CREATE INDEX idx_workflow_steps_workflow ON workflow_steps(workflow_id);
```

#### 8. workflow_executions
```sql
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    workflow_id UUID REFERENCES workflows(id),
    state VARCHAR(50) NOT NULL,
    current_step INTEGER,
    context JSONB NOT NULL DEFAULT '{}',
    results JSONB DEFAULT '{}',
    errors JSONB DEFAULT '{}',
    total_steps INTEGER NOT NULL,
    completed_steps INTEGER DEFAULT 0,
    failed_steps INTEGER DEFAULT 0,
    triggered_by UUID REFERENCES users(id),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_executions_workflow ON workflow_executions(workflow_id);
CREATE INDEX idx_executions_state ON workflow_executions(state);
CREATE INDEX idx_executions_user ON workflow_executions(triggered_by);
```

#### 9. task_results
```sql
CREATE TABLE task_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(100) UNIQUE NOT NULL,
    execution_id UUID REFERENCES workflow_executions(id),
    agent_id UUID REFERENCES agents(id),
    command_id UUID REFERENCES command_templates(id),
    
    -- Output Layer fields
    summary TEXT,
    results JSONB NOT NULL,
    self_critique TEXT,
    improvements JSONB DEFAULT '[]',
    alternatives JSONB DEFAULT '[]',
    action_items JSONB DEFAULT '[]',
    
    -- Metrics
    quality_score DECIMAL(3,2),
    confidence_score DECIMAL(3,2),
    duration_seconds DECIMAL(10,2),
    tokens_used INTEGER,
    cost DECIMAL(10,4),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_results_execution ON task_results(execution_id);
CREATE INDEX idx_results_agent ON task_results(agent_id);
```

#### 10. notifications
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    channels JSONB NOT NULL DEFAULT '[]',
    recipients JSONB NOT NULL DEFAULT '[]',
    data JSONB DEFAULT '{}',
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_created ON notifications(created_at);
```

#### 11. audit_logs
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at);
```

#### 12. api_keys
```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    scopes JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
```

#### 13. platform_credentials
```sql
CREATE TABLE platform_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) UNIQUE NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    additional_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 10.2 Views للتقارير

```sql
-- View: Agent Performance Summary
CREATE VIEW agent_performance_summary AS
SELECT 
    a.id,
    a.name,
    a.department,
    am.total_executions,
    am.successful_executions,
    am.failed_executions,
    ROUND((am.successful_executions::DECIMAL / NULLIF(am.total_executions, 0)) * 100, 2) as success_rate,
    am.average_quality_score,
    am.average_response_time,
    am.average_cost,
    am.total_tokens_used
FROM agents a
LEFT JOIN agent_metrics am ON a.id = am.agent_id;

-- View: Workflow Execution Stats
CREATE VIEW workflow_execution_stats AS
SELECT 
    w.id,
    w.name,
    w.department,
    COUNT(we.id) as total_executions,
    COUNT(CASE WHEN we.state = 'completed' THEN 1 END) as completed,
    COUNT(CASE WHEN we.state = 'failed' THEN 1 END) as failed,
    AVG(EXTRACT(EPOCH FROM (we.completed_at - we.started_at))) as avg_duration_seconds
FROM workflows w
LEFT JOIN workflow_executions we ON w.id = we.workflow_id
GROUP BY w.id, w.name, w.department;
```

---

# 11. التكامل مع المنصات Integration Layer

## 11.1 AI Platform Adapters - التفاصيل الكاملة

### OpenAI Adapter

```python
from openai import AsyncOpenAI
from typing import Dict, AsyncIterator
import os

class OpenAIAdapter(AIAdapter):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.pricing = {
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
            'gpt-4-turbo-preview': {'input': 0.01, 'output': 0.03},
            'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
        }
        self.rate_limiter = RateLimiter(rpm=3500, tpm=90000)
    
    async def execute(self, prompt: str, config: Dict) -> AIResponse:
        """تنفيذ prompt على OpenAI"""
        # Wait for rate limit
        await self.rate_limiter.acquire()
        
        start = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": config.get('system_prompt', '')},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.get('temperature', 0.7),
                max_tokens=config.get('max_tokens', 4000),
                top_p=config.get('top_p', 1.0),
                frequency_penalty=config.get('frequency_penalty', 0.0),
                presence_penalty=config.get('presence_penalty', 0.0),
            )
            
            duration = time.time() - start
            
            return AIResponse(
                content=response.choices[0].message.content,
                tokens=response.usage.total_tokens,
                cost=self.get_cost(response.usage.total_tokens, response.model),
                model=response.model,
                finish_reason=response.choices[0].finish_reason,
                duration=duration
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise AIProviderError(f"OpenAI failed: {e}")
    
    async def stream(self, prompt: str, config: Dict) -> AsyncIterator[str]:
        """Streaming response"""
        await self.rate_limiter.acquire()
        
        stream = await self.client.chat.completions.create(
            model=config.get('model', 'gpt-4'),
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            **config
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def health_check(self) -> bool:
        """فحص صحة الاتصال"""
        try:
            await self.client.models.list()
            return True
        except:
            return False
```

### Claude Adapter

```python
from anthropic import AsyncAnthropic

class ClaudeAdapter(AIAdapter):
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
        self.pricing = {
            'claude-3-opus': {'input': 0.015, 'output': 0.075},
            'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
            'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
        }
        self.rate_limiter = RateLimiter(rpm=1000, tpm=40000)
    
    async def execute(self, prompt: str, config: Dict) -> AIResponse:
        await self.rate_limiter.acquire()
        
        start = time.time()
        
        try:
            response = await self.client.messages.create(
                model=config.get('model', 'claude-3-sonnet-20240229'),
                max_tokens=config.get('max_tokens', 4000),
                temperature=config.get('temperature', 0.7),
                system=config.get('system_prompt', ''),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            duration = time.time() - start
            
            return AIResponse(
                content=response.content[0].text,
                tokens=response.usage.input_tokens + response.usage.output_tokens,
                cost=self.get_cost(
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                    response.model
                ),
                model=response.model,
                finish_reason=response.stop_reason,
                duration=duration
            )
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise AIProviderError(f"Claude failed: {e}")
    
    def get_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """حساب التكلفة بناءً على input/output منفصلين"""
        pricing = self.pricing.get(model, self.pricing['claude-3-sonnet'])
        cost = (input_tokens / 1000 * pricing['input']) + \
               (output_tokens / 1000 * pricing['output'])
        return round(cost, 4)
```

### Gemini Adapter

```python
import google.generativeai as genai

class GeminiAdapter(AIAdapter):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.pricing = {
            'gemini-pro': {'input': 0.00025, 'output': 0.0005},
            'gemini-pro-vision': {'input': 0.00025, 'output': 0.0005},
        }
        self.rate_limiter = RateLimiter(rpm=60, tpm=32000)
    
    async def execute(self, prompt: str, config: Dict) -> AIResponse:
        await self.rate_limiter.acquire()
        
        start = time.time()
        
        try:
            model = genai.GenerativeModel(
                config.get('model', 'gemini-pro')
            )
            
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=config.get('temperature', 0.7),
                    max_output_tokens=config.get('max_tokens', 4000),
                )
            )
            
            duration = time.time() - start
            
            # Gemini doesn't provide exact token counts yet
            estimated_tokens = len(response.text.split()) * 1.3
            
            return AIResponse(
                content=response.text,
                tokens=int(estimated_tokens),
                cost=self.get_cost(int(estimated_tokens), config.get('model')),
                model=config.get('model', 'gemini-pro'),
                finish_reason='stop',
                duration=duration
            )
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise AIProviderError(f"Gemini failed: {e}")
```

## 11.2 Rate Limiter

```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    """
    معدل محدد للطلبات
    """
    def __init__(self, rpm: int, tpm: int):
        self.rpm = rpm  # Requests per minute
        self.tpm = tpm  # Tokens per minute
        
        self.request_timestamps = []
        self.token_usage = []
        self.lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 0):
        """انتظار حتى يكون الطلب مسموحاً"""
        async with self.lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            
            # Clean old timestamps
            self.request_timestamps = [
                ts for ts in self.request_timestamps if ts > minute_ago
            ]
            self.token_usage = [
                (ts, t) for ts, t in self.token_usage if ts > minute_ago
            ]
            
            # Check RPM limit
            if len(self.request_timestamps) >= self.rpm:
                wait_time = 60 - (now - self.request_timestamps[0]).total_seconds()
                await asyncio.sleep(wait_time)
            
            # Check TPM limit
            current_tokens = sum(t for _, t in self.token_usage)
            if current_tokens + tokens > self.tpm:
                wait_time = 60 - (now - self.token_usage[0][0]).total_seconds()
                await asyncio.sleep(wait_time)
            
            # Record this request
            self.request_timestamps.append(now)
            if tokens > 0:
                self.token_usage.append((now, tokens))
```

## 11.3 Unified AI Service مع Fallback

```python
class UnifiedAIService:
    """
    خدمة موحدة مع دعم Fallback و Cost Tracking
    """
    def __init__(self):
        self.adapters = {
            'openai': OpenAIAdapter(os.getenv('OPENAI_API_KEY')),
            'claude': ClaudeAdapter(os.getenv('CLAUDE_API_KEY')),
            'gemini': GeminiAdapter(os.getenv('GEMINI_API_KEY')),
        }
        
        # Cost tracking
        self.total_cost = 0.0
        self.cost_by_platform = {}
        
        # Health status
        self.platform_health = {}
    
    async def execute(
        self,
        platform: str,
        prompt: str,
        config: Dict,
        allow_fallback: bool = True
    ) -> AIResponse:
        """
        تنفيذ مع fallback تلقائي
        """
        adapter = self.adapters.get(platform)
        if not adapter:
            raise ValueError(f"Unknown platform: {platform}")
        
        try:
            response = await adapter.execute(prompt, config)
            
            # Track cost
            self._track_cost(platform, response.cost)
            
            return response
            
        except AIProviderError as e:
            logger.warning(f"Platform {platform} failed: {e}")
            
            # Mark platform as unhealthy
            self.platform_health[platform] = False
            
            if allow_fallback:
                return await self._fallback_execute(
                    platform, prompt, config, e
                )
            else:
                raise
    
    async def _fallback_execute(
        self,
        failed_platform: str,
        prompt: str,
        config: Dict,
        original_error: Exception
    ) -> AIResponse:
        """
        محاولة على منصات بديلة
        """
        fallback_order = ['openai', 'claude', 'gemini']
        fallback_platforms = [
            p for p in fallback_order 
            if p != failed_platform and self.platform_health.get(p, True)
        ]
        
        for platform in fallback_platforms:
            try:
                logger.info(f"Trying fallback: {platform}")
                return await self.adapters[platform].execute(prompt, config)
            except Exception as e:
                logger.error(f"Fallback {platform} failed: {e}")
                self.platform_health[platform] = False
                continue
        
        # All failed
        raise Exception(f"All platforms failed. Original: {original_error}")
    
    def _track_cost(self, platform: str, cost: float):
        """تتبع التكاليف"""
        self.total_cost += cost
        self.cost_by_platform[platform] = \
            self.cost_by_platform.get(platform, 0.0) + cost
    
    async def health_check_all(self):
        """فحص صحة جميع المنصات"""
        for platform, adapter in self.adapters.items():
            try:
                is_healthy = await adapter.health_check()
                self.platform_health[platform] = is_healthy
            except:
                self.platform_health[platform] = False
```

---

# 12. الأمان والصلاحيات Security & Authorization

## 12.1 Authentication System

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import pyotp

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    خدمة المصادقة
    """
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    @staticmethod
    def hash_password(password: str) -> str:
        """تشفير كلمة المرور"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """التحقق من كلمة المرور"""
        return pwd_context.verify(plain, hashed)
    
    @classmethod
    def create_access_token(cls, data: dict) -> str:
        """إنشاء Access Token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def create_refresh_token(cls, data: dict) -> str:
        """إنشاء Refresh Token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=cls.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def verify_token(cls, token: str) -> dict:
        """التحقق من Token"""
        try:
            payload = jwt.decode(
                token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM]
            )
            return payload
        except JWTError:
            raise AuthenticationError("Invalid token")
    
    @staticmethod
    def generate_2fa_secret() -> str:
        """توليد سر للـ 2FA"""
        return pyotp.random_base32()
    
    @staticmethod
    def verify_2fa_token(secret: str, token: str) -> bool:
        """التحقق من رمز 2FA"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
```

## 12.2 Authorization - RBAC System

```python
from enum import Enum
from typing import List, Set

class Permission(Enum):
    # Workflow permissions
    VIEW_WORKFLOWS = "view_workflows"
    CREATE_WORKFLOW = "create_workflow"
    EDIT_WORKFLOW = "edit_workflow"
    DELETE_WORKFLOW = "delete_workflow"
    EXECUTE_WORKFLOW = "execute_workflow"
    
    # Agent permissions
    VIEW_AGENTS = "view_agents"
    MANAGE_AGENTS = "manage_agents"
    
    # Results permissions
    VIEW_OWN_RESULTS = "view_own_results"
    VIEW_ALL_RESULTS = "view_all_results"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_API_KEYS = "manage_api_keys"
    
    # Wildcard
    ALL = "*"

class RBACService:
    """
    خدمة التحكم في الصلاحيات
    """
    @staticmethod
    async def check_permission(
        user_id: str,
        required_permission: Permission
    ) -> bool:
        """
        التحقق من صلاحية المستخدم
        """
        # Get user role
        user = await db.users.get(user_id)
        role = await db.roles.get(user.role_id)
        
        # Check if has wildcard
        if Permission.ALL.value in role.permissions:
            return True
        
        # Check specific permission
        return required_permission.value in role.permissions
    
    @staticmethod
    async def require_permission(permission: Permission):
        """
        Decorator للتحقق من الصلاحية
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Get current user from context
                user_id = get_current_user_id()
                
                has_permission = await RBACService.check_permission(
                    user_id, permission
                )
                
                if not has_permission:
                    raise PermissionDeniedError(
                        f"Missing permission: {permission.value}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
```

## 12.3 Audit Trail

```python
class AuditService:
    """
    خدمة تسجيل جميع الأنشطة
    """
    @staticmethod
    async def log(
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str = None,
        old_value: dict = None,
        new_value: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """
        تسجيل نشاط في Audit Log
        """
        await db.audit_logs.create({
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'old_value': old_value,
            'new_value': new_value,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.utcnow()
        })
    
    @staticmethod
    async def get_user_activity(
        user_id: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[dict]:
        """
        الحصول على نشاط مستخدم
        """
        query = {'user_id': user_id}
        
        if start_date:
            query['created_at__gte'] = start_date
        if end_date:
            query['created_at__lte'] = end_date
        
        return await db.audit_logs.find(query).sort('created_at', -1)
```

---

**نهاية الجزء 4/5**

**الجزء الأخير (5/5)** سيتضمن:
- Monitoring & Metrics System
- Infrastructure & Deployment
- خطة التنفيذ الكاملة (Implementation Plan)
- Testing Strategy
