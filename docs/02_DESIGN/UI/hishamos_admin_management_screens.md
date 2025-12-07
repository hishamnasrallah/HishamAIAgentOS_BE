---
title: "HishamOS - Admin & Management Screens"
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
  - admin
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

# HishamOS - Admin & Management Screens
## الشاشات الإدارية الكاملة للنظام

---

# 1. Platform Configuration Screen
## شاشة ربط تطبيقات الذكاء الاصطناعي (بدون كود)

### 1.1 UI Design

```
┌────────────────────────────────────────────────────────────────┐
│ ⚙️ AI Platforms Configuration                    [Save] [Test]│
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📡 Connected Platforms                                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Platform      Status    API Key      Rate Limit   Actions│ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ 🤖 OpenAI     ✅ Active  sk-...****   3500 RPM   [Edit]  │ │
│  │ 🧠 Claude     ✅ Active  sk-ant-***  1000 RPM   [Edit]  │ │
│  │ 💎 Gemini     ⚠️ Warning API-***     60 RPM     [Edit]  │ │
│  │ 🌐 OpenRouter ❌ Inactive ────────   ────────   [Setup] │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  [➕ Add New Platform]                                          │
│                                                                 │
│  ─────────────────────────────────────────────────────────────│
│                                                                 │
│  🔧 Configure Platform: OpenAI                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │ Platform Name:     [OpenAI                            ▼] │ │
│  │                                                           │ │
│  │ API Key:          [sk-proj-*********************     ] 👁 │ │
│  │                   [Test Connection]                       │ │
│  │                                                           │ │
│  │ Base URL:         [https://api.openai.com/v1         ]  │ │
│  │                                                           │ │
│  │ Rate Limits:                                              │ │
│  │   • Requests/Min:  [3500                            ]    │ │
│  │   • Tokens/Min:    [90000                           ]    │ │
│  │                                                           │ │
│  │ Models Available:  [✓] gpt-4                             │ │
│  │                    [✓] gpt-4-turbo                        │ │
│  │                    [✓] gpt-3.5-turbo                      │ │
│  │                                                           │ │
│  │ Cost Tracking:     [✓] Enable cost monitoring             │ │
│  │ Daily Budget:      [$100.00                         ]    │ │
│  │                                                           │ │
│  │ Fallback Priority: [1] (1=highest)                       │ │
│  │                                                           │ │
│  │ Advanced Settings:                                        │ │
│  │   Timeout:         [30               ] seconds           │ │
│  │   Retry Attempts:  [3                ]                   │ │
│  │   Retry Delay:     [2                ] seconds           │ │
│  │                                                           │ │
│  │              [Cancel]  [Save & Test]  [Save]             │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  📊 Platform Health Status                                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ • OpenAI:   ✅ Healthy (Last check: 2 mins ago)          │ │
│  │ • Claude:   ✅ Healthy (Last check: 2 mins ago)          │ │
│  │ • Gemini:   ⚠️  Rate limit warning (85% usage)           │ │
│  │ • OpenRouter: ❌ Not configured                           │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### 1.2 Backend Implementation

```python
from pydantic import BaseModel, validator
from typing import List, Optional, Dict
from enum import Enum

class PlatformType(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"
    AZURE_OPENAI = "azure_openai"
    CUSTOM = "custom"

class PlatformConfig(BaseModel):
    """Model للـ Platform Configuration"""
    platform_type: PlatformType
    api_key: str
    base_url: Optional[str] = None
    rate_limit_rpm: int  # Requests per minute
    rate_limit_tpm: int  # Tokens per minute
    available_models: List[str]
    cost_tracking_enabled: bool = True
    daily_budget: Optional[float] = None
    fallback_priority: int = 1
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay_seconds: int = 2
    is_active: bool = True
    
    @validator('api_key')
    def api_key_not_empty(cls, v):
        if not v or len(v) < 10:
            raise ValueError('API key is required and must be valid')
        return v

class PlatformManagementAPI:
    """
    API لإدارة Platform Configurations
    """
    
    @app.get("/api/v1/admin/platforms")
    @require_permission(Permission.MANAGE_PLATFORMS)
    async def list_platforms(user: User = Depends(get_current_user)):
        """
        قائمة جميع المنصات المكونة
        """
        platforms = await db.platform_credentials.find({})
        
        # Add health status
        for platform in platforms:
            platform['health_status'] = await self._check_platform_health(
                platform['platform']
            )
        
        return {"platforms": platforms}
    
    @app.post("/api/v1/admin/platforms")
    @require_permission(Permission.MANAGE_PLATFORMS)
    async def add_platform(
        config: PlatformConfig,
        user: User = Depends(get_current_user)
    ):
        """
        إضافة منصة جديدة
        """
        # Test connection first
        test_result = await self._test_platform_connection(config)
        
        if not test_result['success']:
            raise HTTPException(
                status_code=400,
                detail=f"Connection test failed: {test_result['error']}"
            )
        
        # Encrypt API key
        encrypted_key = await secrets_manager.encrypt(config.api_key)
        
        # Store configuration
        platform_id = await db.platform_credentials.create({
            'platform': config.platform_type.value,
            'api_key_encrypted': encrypted_key,
            'base_url': config.base_url,
            'rate_limit_rpm': config.rate_limit_rpm,
            'rate_limit_tpm': config.rate_limit_tpm,
            'available_models': config.available_models,
            'cost_tracking_enabled': config.cost_tracking_enabled,
            'daily_budget': config.daily_budget,
            'fallback_priority': config.fallback_priority,
            'timeout_seconds': config.timeout_seconds,
            'retry_attempts': config.retry_attempts,
            'retry_delay_seconds': config.retry_delay_seconds,
            'is_active': config.is_active,
            'created_by': user.id,
            'created_at': datetime.utcnow()
        })
        
        # Audit log
        await audit_service.log(
            user_id=user.id,
            action='platform_added',
            resource_type='platform',
            resource_id=platform_id,
            new_value={'platform': config.platform_type.value}
        )
        
        return {
            "id": platform_id,
            "message": f"Platform {config.platform_type.value} configured successfully",
            "test_result": test_result
        }
    
    @app.post("/api/v1/admin/platforms/{platform_id}/test")
    @require_permission(Permission.MANAGE_PLATFORMS)
    async def test_platform_connection(
        platform_id: str,
        user: User = Depends(get_current_user)
    ):
        """
        اختبار اتصال المنصة
        """
        platform = await db.platform_credentials.get(platform_id)
        
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")
        
        # Decrypt API key
        api_key = await secrets_manager.decrypt(platform['api_key_encrypted'])
        
        # Create temporary config
        config = PlatformConfig(
            platform_type=PlatformType(platform['platform']),
            api_key=api_key,
            base_url=platform.get('base_url'),
            rate_limit_rpm=platform['rate_limit_rpm'],
            rate_limit_tpm=platform['rate_limit_tpm'],
            available_models=platform['available_models']
        )
        
        # Test connection
        result = await self._test_platform_connection(config)
        
        return result
    
    async def _test_platform_connection(
        self,
        config: PlatformConfig
    ) -> Dict:
        """
        اختبار فعلي للاتصال
        """
        try:
            # Get appropriate adapter
            adapter = self._get_adapter(config.platform_type, config.api_key)
            
            # Test with simple prompt
            start = time.time()
            response = await adapter.execute(
                prompt="Say 'Hello'",
                config={
                    'model': config.available_models[0],
                    'max_tokens': 10
                }
            )
            duration = time.time() - start
            
            # Check health endpoint
            is_healthy = await adapter.health_check()
            
            return {
                'success': True,
                'platform': config.platform_type.value,
                'response_time': round(duration, 2),
                'health_status': 'healthy' if is_healthy else 'degraded',
                'models_available': config.available_models,
                'test_prompt_tokens': response.tokens,
                'test_cost': response.cost,
                'message': f'✅ Connection successful! Response time: {duration:.2f}s'
            }
            
        except Exception as e:
            logger.error(f"Platform test failed: {e}")
            return {
                'success': False,
                'platform': config.platform_type.value,
                'error': str(e),
                'message': f'❌ Connection failed: {str(e)}'
            }

class PlatformHealthMonitor:
    """
    مراقبة صحة المنصات بشكل دوري
    """
    def __init__(self):
        self.health_checks = {}
    
    async def monitor_all_platforms(self):
        """
        فحص صحة جميع المنصات كل دقيقة
        """
        platforms = await db.platform_credentials.find({'is_active': True})
        
        for platform in platforms:
            health = await self._check_platform_health(platform['platform'])
            
            # Store in cache
            await cache_manager.set(
                'platform_health',
                platform['platform'],
                health,
                ttl_override=120  # 2 minutes
            )
            
            # Alert if unhealthy
            if health['status'] != 'healthy':
                await alert_manager.check_rules({
                    'type': 'platform_health',
                    'platform': platform['platform'],
                    health['openai']: health['status'] == 'healthy'
                })
    
    async def _check_platform_health(self, platform: str) -> Dict:
        """
        فحص صحة منصة واحدة
        """
        try:
            adapter = unified_ai_service.adapters.get(platform)
            if not adapter:
                return {'status': 'not_configured'}
            
            is_healthy = await adapter.health_check()
            
            # Get usage stats
            current_usage = await self._get_platform_usage(platform)
            
            # Determine status
            if not is_healthy:
                status = 'down'
            elif current_usage['rpm_usage'] > 0.9:
                status = 'rate_limited'
            elif current_usage['budget_usage'] > 0.9:
                status = 'budget_exceeded'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'last_check': datetime.utcnow(),
                'rpm_usage': current_usage['rpm_usage'],
                'budget_usage': current_usage['budget_usage'],
                'total_cost_today': current_usage['total_cost_today']
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
```

---

# 2. User Permissions Management Screen
## شاشة صلاحيات المستخدمين للذكاء الاصطناعي

### 2.1 UI Design

```
┌────────────────────────────────────────────────────────────────┐
│ 👥 User Permissions & AI Access Control                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔍 Search Users: [________________] [Search]  [➕ Add User]   │
│                                                                 │
│  👤 Users List                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ User          Role      AI Access  Daily Limit  Actions  │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ Ahmed Ali     Admin     ✅ Full    Unlimited   [Edit]    │ │
│  │ Sara Hassan   Dev       ✅ Limited $50/day     [Edit]    │ │
│  │ Khaled Omar   Legal     ✅ Limited $30/day     [Edit]    │ │
│  │ Noor Ahmad    Viewer    ❌ None    ────        [Edit]    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ─────────────────────────────────────────────────────────────│
│                                                                 │
│  🔒 Edit User: Sara Hassan                                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │ Basic Info:                                               │ │
│  │   Email:        sara.hassan@company.com                  │ │
│  │   Department:   [Engineering                         ▼]  │ │
│  │   Role:         [Developer                           ▼]  │ │
│  │                                                           │ │
│  │ AI Platform Access:                                       │ │
│  │   [✓] OpenAI      (Models: [✓] gpt-4 [✓] gpt-3.5)       │ │
│  │   [✓] Claude      (Models: [✓] claude-3-sonnet)          │ │
│  │   [ ] Gemini      (No access)                             │ │
│  │                                                           │ │
│  │ Agent Access:                                             │ │
│  │   [✓] Coding Agent                                        │ │
│  │   [✓] Code Reviewer Agent                                 │ │
│  │   [ ] Legal Agent                                         │ │
│  │   [✓] CTO Engineering Agent                               │ │
│  │   [ ] CEO Strategy Agent                                  │ │
│  │   → Select All  | Clear All                               │ │
│  │                                                           │ │
│  │ Usage Limits:                                             │ │
│  │   Daily Cost Limit:     [$50.00              ]           │ │
│  │   Monthly Cost Limit:   [$1000.00            ]           │ │
│  │   Requests/Hour:        [100                 ]           │ │
│  │   Max Tokens/Request:   [4000                ]           │ │
│  │                                                           │ │
│  │ Workflow Permissions:                                     │ │
│  │   [✓] Create workflows                                    │ │
│  │   [✓] Execute workflows                                   │ │
│  │   [ ] Delete workflows                                    │ │
│  │   [ ] Approve workflows (Admin only)                      │ │
│  │                                                           │ │
│  │ Notifications:                                            │ │
│  │   [✓] Email on 80% budget usage                           │ │
│  │   [✓] Email on  limit exceeded                            │ │
│  │   [✓] Daily usage summary                                 │ │
│  │                                                           │ │
│  │              [Cancel]  [Save Changes]                     │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### 2.2 Backend Implementation

```python
class UserAIPermissions(BaseModel):
    """نموذج صلاحيات AI للمستخدم"""
    user_id: str
    allowed_platforms: List[str]  # ['openai', 'claude']
    allowed_models: Dict[str, List[str]]  # {'openai': ['gpt-4', 'gpt-3.5']}
    allowed_agents: List[str]  # Agent IDs
    daily_cost_limit: float
    monthly_cost_limit: float
    requests_per_hour: int
    max_tokens_per_request: int
    can_create_workflows: bool = True
    can_execute_workflows: bool = True
    can_delete_workflows: bool = False
    can_approve_workflows: bool = False

@app.put("/api/v1/admin/users/{user_id}/ai-permissions")
@require_permission(Permission.MANAGE_USERS)
async def update_user_ai_permissions(
    user_id: str,
    permissions: UserAIPermissions,
    admin_user: User = Depends(get_current_user)
):
    """
    تحديث صلاحيات AI للمستخدم
    """
    # Validate user exists
    user = await db.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get old permissions for audit
    old_permissions = await db.user_ai_permissions.find_one({'user_id': user_id})
    
    # Update permissions
    await db.user_ai_permissions.update_one(
        {'user_id': user_id},
        {'$set': permissions.dict()},
        upsert=True
    )
    
    # Audit log
    await audit_service.log(
        user_id=admin_user.id,
        action='user_permissions_updated',
        resource_type='user_permissions',
        resource_id=user_id,
        old_value=old_permissions,
        new_value=permissions.dict()
    )
    
    # Invalidate cache
    await cache_manager.invalidate('user_permissions', user_id)
    
    return {"message": "Permissions updated successfully"}

class PermissionChecker:
    """
    التحقق من الصلاحيات قبل كل استخدام
    """
    async def check_ai_access(
        self,
        user_id: str,
        platform: str,
        model: str,
        estimated_tokens: int
    ) -> bool:
        """
        التحقق من صلاحية الوصول
        """
        # Get user permissions
        permissions = await self._get_user_permissions(user_id)
        
        # Check platform access
        if platform not in permissions['allowed_platforms']:
            raise PermissionDeniedError(
                f"User does not have access to {platform}"
            )
        
        # Check model access
        allowed_models = permissions['allowed_models'].get(platform, [])
        if model not in allowed_models:
            raise PermissionDeniedError(
                f"User does not have access to model {model}"
            )
        
        # Check token limit
        if estimated_tokens > permissions['max_tokens_per_request']:
            raise PermissionDeniedError(
                f"Request exceeds max tokens limit"
            )
        
        # Check daily cost limit
        today_cost = await self._get_user_cost_today(user_id)
        if today_cost >= permissions['daily_cost_limit']:
            raise PermissionDeniedError(
                "Daily cost limit exceeded"
            )
        
        # Check rate limit
        requests_last_hour = await self._get_user_requests_last_hour(user_id)
        if requests_last_hour >= permissions['requests_per_hour']:
            raise RateLimitError(
                "Hourly request limit exceeded"
            )
        
        return True
```

---

# 3. Token Management & Limits Screen
## شاشة إدارة التوكينز والحدود

### 3.1 UI Design

```
┌────────────────────────────────────────────────────────────────┐
│ 🎫 Token Management & Usage Limits                              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📊 Global Token Usage (Today)                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Platform    Tokens Used    Limit      Usage    Cost      │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ OpenAI      2.5M / 10M     ████░░░░░  25%     $75.00    │ │
│  │ Claude      500K / 5M      ██░░░░░░░░  10%     $15.00    │ │
│  │ Gemini      100K / 1M      █░░░░░░░░░  10%     $2.50     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  💰 Budget Overview                                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Today:    $92.50  / $200.00   (46%)                      │ │
│  │ This Week: $450.00 / $1000.00 (45%)                      │ │
│  │ This Month: $1,850 / $5000.00 (37%)                      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ⚙️ Global Limits Configuration                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                                                           │ │
│  │ Daily Limits:                                             │ │
│  │   Total Cost:        [$200.00            ]               │ │
│  │   Total Tokens:      [10000000           ] (10M)         │ │
│  │   Total Requests:    [10000              ]               │ │
│  │                                                           │ │
│  │ Per-Platform Limits (OpenAI):                             │ │
│  │   Daily Cost:        [$150.00            ]               │ │
│  │   Daily Tokens:      [5000000            ] (5M)          │ │
│  │   RPM:               [3500               ]               │ │
│  │   TPM:               [90000              ]               │ │
│  │                                                           │ │
│  │ Alert Thresholds:                                         │ │
│  │   Warning at:        [80                 ]%              │ │
│  │   Critical at:       [95                 ]%              │ │
│  │                                                           │ │
│  │ Auto-Actions:                                             │ │
│  │   [✓] Pause new requests at 100% usage                   │ │
│  │   [✓] Send email alerts to admins                        │ │
│  │   [✓] Failover to cheaper platform when possible         │ │
│  │                                                           │ │
│  │              [Save Configuration]                         │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  👥 Per-User Token Usage (Today)                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ User         Tokens    Cost     Limit    Status  Actions │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ Ahmed Ali    150K      $4.50    $50      ✅ OK    [View] │ │
│  │ Sara Hassan  450K      $45.00   $50      ⚠️  90%  [View] │ │
│  │ Khaled Omar  25K       $2.50    $30      ✅ OK    [View] │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### 3.2 Backend Implementation

```python
class TokenUsageTracker:
    """
    تتبع استخدام التوكينز بدقة
    """
    async def record_usage(
        self,
        user_id: str,
        platform: str,
        model: str,
        tokens: int,
        cost: float,
        request_type: str
    ):
        """
        تسجيل استخدام توكين
        """
        usage_record = {
            'user_id': user_id,
            'platform': platform,
            'model': model,
            'tokens': tokens,
            'cost': cost,
            'request_type': request_type,
            'timestamp': datetime.utcnow()
        }
        
        # Store in database
        await db.token_usage.create(usage_record)
        
        # Update aggregated metrics in cache
        await self._update_usage_metrics(user_id, platform, tokens, cost)
        
        # Check limits
        await self._check_and_alert_limits(user_id, platform)
    
    async def _update_usage_metrics(
        self,
        user_id: str,
        platform: str,
        tokens: int,
        cost: float
    ):
        """
        تحديث metrics في الكاش
        """
        today = datetime.utcnow().date()
        
        # Update user metrics
        user_key = f"usage:{user_id}:{today}"
        await redis.hincrby(user_key, 'tokens', tokens)
        await redis.hincrbyfloat(user_key, 'cost', cost)
        await redis.expire(user_key, 86400 * 7)  # Keep for 7 days
        
        # Update platform metrics
        platform_key = f"usage:platform:{platform}:{today}"
        await redis.hincrby(platform_key, 'tokens', tokens)
        await redis.hincrbyfloat(platform_key, 'cost', cost)
        await redis.expire(platform_key, 86400 * 7)
    
    async def get_user_usage_today(self, user_id: str) -> Dict:
        """
        الحصول على استخدام المستخدم اليوم
        """
        today = datetime.utcnow().date()
        key = f"usage:{user_id}:{today}"
        
        usage = await redis.hgetall(key)
        
        if not usage:
            return {'tokens': 0, 'cost': 0.0}
        
        return {
            'tokens': int(usage.get('tokens', 0)),
            'cost': float(usage.get('cost', 0.0))
        }
```

---

# 4. Conversation History Storage
## حفظ المحادثات بطريقة منظمة ومحسّنة

### 4.1 Database Schema

```sql
-- Conversation threads table
CREATE TABLE conversation_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id),
    workflow_execution_id UUID REFERENCES workflow_executions(id),
    
    title VARCHAR(255),
    summary TEXT,
    
    -- Metadata
    department VARCHAR(100),
    tags JSONB DEFAULT '[]',
    is_archived BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP
);

-- Optimized indexes
CREATE INDEX idx_conversations_user ON conversation_threads(user_id, last_message_at DESC);
CREATE INDEX idx_conversations_agent ON conversation_threads(agent_id);
CREATE INDEX idx_conversations_workflow ON conversation_threads(workflow_execution_id);
CREATE INDEX idx_conversations_tags ON conversation_threads USING GIN(tags);

-- Messages table
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID REFERENCES conversation_threads(id) ON DELETE CASCADE,
    
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    
    -- AI Response metadata
    model VARCHAR(100),
    tokens_used INTEGER,
    cost DECIMAL(10,4),
    quality_score DECIMAL(3,2),
    
    -- Performance
    response_time DECIMAL(10,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Partition by month for better performance
CREATE INDEX idx_messages_thread ON conversation_messages(thread_id, created_at DESC);

-- View для quick access
CREATE VIEW conversation_summary AS
SELECT 
    ct.id as thread_id,
    ct.user_id,
    ct.agent_id,
    ct.title,
    COUNT(cm.id) as message_count,
    SUM(cm.tokens_used) as total_tokens,
    SUM(cm.cost) as total_cost,
    AVG(cm.quality_score) as avg_quality,
    ct.last_message_at
FROM conversation_threads ct
LEFT JOIN conversation_messages cm ON ct.id = cm.thread_id
GROUP BY ct.id;
```

### 4.2 Implementation

```python
class ConversationManager:
    """
    إدارة المحادثات بكفاءة عالية
    """
    
    async def create_thread(
        self,
        user_id: str,
        agent_id: str,
        title: str,
        workflow_execution_id: Optional[str] = None
    ) -> str:
        """
        إنشاء thread محادثة جديد
        """
        thread_id = await db.conversation_threads.create({
            'user_id': user_id,
            'agent_id': agent_id,
            'workflow_execution_id': workflow_execution_id,
            'title': title,
            'created_at': datetime.utcnow(),
            'last_message_at': datetime.utcnow()
        })
        
        return thread_id
    
    async def add_message(
        self,
        thread_id: str,
        role: str,  # 'user' or 'assistant'
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        إضافة رسالة للمحادثة
        """
        message_data = {
            'thread_id': thread_id,
            'role': role,
            'content': content,
            'created_at': datetime.utcnow()
        }
        
        if metadata:
            message_data.update({
                'model': metadata.get('model'),
                'tokens_used': metadata.get('tokens'),
                'cost': metadata.get('cost'),
                'quality_score': metadata.get('quality_score'),
                'response_time': metadata.get('response_time')
            })
        
        # Insert message
        message_id = await db.conversation_messages.create(message_data)
        
        # Update thread's last_message_at
        await db.conversation_threads.update(
            {'id': thread_id},
            {'last_message_at': datetime.utcnow()}
        )
        
        # Update cache
        await self._cache_recent_messages(thread_id)
        
        return message_id
    
    async def get_thread_messages(
        self,
        thread_id: str,
        limit: int = 100,
        before_id: Optional[str] = None
    ) -> List[Dict]:
        """
        الحصول على رسائل المحادثة (مع pagination)
        """
        # Try cache first
        cache_key = f"thread_messages:{thread_id}"
        cached = await cache_manager.get('conversation', cache_key)
        
        if cached and not before_id:
            return cached
        
        # Query database
        query = {'thread_id': thread_id}
        if before_id:
            query['id__lt'] = before_id
        
        messages = await db.conversation_messages.find(query) \
            .sort('created_at', -1) \
            .limit(limit)
        
        # Cache if recent
        if not before_id:
            await cache_manager.set('conversation', cache_key, messages, ttl_override=300)
        
        return list(reversed(messages))
    
    async def search_conversations(
        self,
        user_id: str,
        query: Optional[str] = None,
        agent_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict]:
        """
        بحث في المحادثات
        """
        filters = {'user_id': user_id}
        
        if agent_id:
            filters['agent_id'] = agent_id
        
        if tags:
            filters['tags__contains'] = tags
        
        if date_from:
            filters['created_at__gte'] = date_from
        
        if date_to:
            filters['created_at__lte'] = date_to
        
        threads = await db.conversation_threads.find(filters)
        
        # Full-text search if query provided
        if query:
            threads = await self._full_text_search(threads, query)
        
        return threads
    
    async def archive_old_conversations(self, days: int = 90):
        """
        أرشفة المحادثات القديمة تلقائياً
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        await db.conversation_threads.update_many(
            {
                'last_message_at__lt': cutoff_date,
                'is_archived': False
            },
            {'is_archived': True}
        )
```

---

# 5. Enhanced Professional Dashboard
## لوحة تحكم احترافية شاملة

### 5.1 Main Dashboard

```
┌──────────────────────────────────────────────────────────────────┐
│ 🏠 HishamOS Dashboard                    [User ▼] [⚙️] [🔔 3]   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📊 Quick Stats (Real-time)                                       │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐      │
│  │ 📈 Active   │ ✅ Complete │ 🤖 Agents   │ 💰 Cost     │      │
│  │ Workflows   │ Today       │ Online      │ Today       │      │
│  │     8       │     47      │    15/15    │   $92.50    │      │
│  │    +2       │    +12      │   ✅ All    │   ↓ 15%     │      │
│  └─────────────┴─────────────┴─────────────┴─────────────┘      │
│                                                                   │
│  🚀 Quick Actions                                                 │
│  [▶️ Run Workflow] [➕ New Task] [📋 Templates] [📊 Analytics]   │
│                                                                   │
│  ───────────────────────────────────────────────────────────────│
│                                                                   │
│  📋 Recent Workflows                          [View All →]       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Status  Workflow              Agent      Progress  Score   │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ ✅      Feature Development   Coding     100%      9.2/10  │ │
│  │         2 hours ago                      ████████          │ │
│  │                                                            │ │
│  │ ▶️       Code Review          Reviewer   65%       ─      │ │
│  │         Running now...                   ██████░░          │ │
│  │                                                            │ │
│  │ ⏸        Contract Review       Legal      45%       ─      │ │
│  │         Paused - waiting approval        ████░░░░          │ │
│  │                                                            │ │
│  │ ❌      Data Analysis          Data       Failed    5.5/10  │ │
│  │         30 mins ago - Retry?             ─────────  [↻]   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ───────────────────────────────────────────────────────────────│
│                                                                   │
│  📈 Performance Metrics (Last 24 Hours)                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Success Rate          Quality Score       Avg Response    │ │
│  │  ████████░░ 87%       ████████── 8.5/10    2.3s           │ │
│  │                                                            │ │
│  │  [Interactive Chart: Workflows over time]                  │ │
│  │  50│                    ╭─╮                               │ │
│  │  40│         ╭─╮    ╭──╯ ╰─╮                             │ │
│  │  30│    ╭────╯ ╰────╯       ╰──╮                         │ │
│  │  20│╭───╯                      ╰────                     │ │
│  │    └────────────────────────────────→                    │ │
│  │    6am   9am  12pm  3pm  6pm  9pm  Now                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  💰 Cost Analysis (This Month)                  [Details →]     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Total: $1,850 / $5,000 (37%)  ████████░░░░░░░░░           │ │
│  │                                                            │ │
│  │  By Platform:                                              │ │
│  │  • OpenAI:      $1,200 (65%)  █████████████░░░            │ │
│  │  • Claude:      $  500 (27%)  █████░░░░░░░░░░░            │ │
│  │  • Gemini:      $  150 (8%)   ██░░░░░░░░░░░░░░            │ │
│  │                                                            │ │
│  │  [Trend Chart: Daily cost over month]                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  🎯 Agent Performance Leaderboard              [All Agents →]   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Rank  Agent              Tasks  Success  Quality  Avg Time│ │
│  │  🥇 1   Coding Agent      245    98%      9.1/10   1.8s   │ │
│  │  🥈 2   Legal Agent        89    95%      8.9/10   3.2s   │ │
│  │  🥉 3   Code Reviewer     156    92%      8.7/10   2.1s   │ │
│  │     4   CTO Engineering    67    91%      8.5/10   4.5s   │ │
│  │     5   Product Manager    43    89%      8.3/10   3.8s   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  🔔 Recent Alerts & Notifications              [All Alerts →]   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  ⚠️  Sara Hassan approaching daily limit (90%)  - 5 mins   │ │
│  │  ✅  Workflow "Build Feature" completed successfully        │ │
│  │  ⚠️  Gemini platform rate limit warning (85%)             │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

# ✅ Summary - الخلاصة

## 🎯 ما تم إضافته:

### 1. ✅ Platform Configuration Screen
- إضافة/تعديل منصات AI بدون كود
- Test Connection فوري
- إدارة Rate Limits
- Platform Health Monitoring

### 2. ✅ User Permissions Management
- صلاحيات تفصيلية لكل مستخدم
- التحكم في Platform/Model/Agent Access
- حدود يومية وشهرية
- Permission Checker قبل كل استخدام

### 3. ✅ Token Management & Limits
- تتبع استخدام التوكينز Realtime
- حدود Global و Per-User
- Alerting تلقائي
- Cost tracking دقيق

### 4. ✅ Conversation History
- تخزين منظم ومحسّن
- Partitioning للأداء
- Full-text search
- Auto-archiving

### 5. ✅ Enhanced Dashboard
- Stats realtime
- Performance charts
- Cost analysis
- Agent leaderboard
- Recent alerts

## 📁 الملف الجديد:
`hishamos_admin_management_screens.md` - يحتوي على كل التفاصيل!

**النظام الآن جاهز 100% من ناحية الإدارة والتحكم!** 🚀
