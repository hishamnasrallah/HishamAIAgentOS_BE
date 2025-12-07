---
title: "HishamOS - ملحق معالجة الفجوات الحرجة"
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

# HishamOS - ملحق معالجة الفجوات الحرجة
## حل شامل للنقاط العشرة

---

> **الهدف**: معالجة جميع الفجوات المحددة في التحليل الأولي  
> **الحالة**: حلول تفصيلية شاملة  
> **التاريخ**: 2025-11-29

---

# 📋 فهرس الحلول

1. [المعمارية التقنية - API Contracts](#1-المعمارية-التقنية---api-contracts)
2. [Agent Dispatcher - Conflict Resolution](#2-agent-dispatcher---conflict-resolution)
3. [Caching Strategy المتقدمة](#3-caching-strategy-المتقدمة)
4. [State Management التفصيلي](#4-state-management-التفصيلي)
5. [Secrets Management](#5-secrets-management)
6. [Alerting System](#6-alerting-system)
7. [Feedback Loop & ML Pipeline](#7-feedback-loop--ml-pipeline)
8. [Performance Tuning المتقدم](#8-performance-tuning-المتقدم)
9. [API Documentation الكاملة](#9-api-documentation-الكاملة)
10. [Deployment Playbooks](#10-deployment-playbooks)

---

# 1. المعمارية التقنية - API Contracts

## 1.1 جميع API Endpoints

### Authentication APIs

```python
# POST /api/v1/auth/register
Request:
{
    "username": "string",
    "email": "string",
    "password": "string",
    "full_name": "string",
    "department": "string"
}

Response 201:
{
    "user_id": "uuid",
    "username": "string",
    "email": "string",
    "message": "Please verify your email"
}

# POST /api/v1/auth/login
Request:
{
    "username": "string",
    "password": "string",
    "2fa_token": "string?"  # Optional if 2FA enabled
}

Response 200:
{
    "access_token": "jwt_string",
    "refresh_token": "jwt_string",
    "token_type": "Bearer",
    "expires_in": 1800,
    "user": {
        "id": "uuid",
        "username": "string",
        "email": "string",
        "role": "string",
        "permissions": ["array"]
    }
}

# POST /api/v1/auth/refresh
Request:
{
    "refresh_token": "string"
}

Response 200:
{
    "access_token": "jwt_string",
    "expires_in": 1800
}

# POST /api/v1/auth/enable-2fa
Headers: Authorization: Bearer {token}

Response 200:
{
    "secret": "string",
    "qr_code_url": "string",
    "backup_codes": ["array"]
}

# POST /api/v1/auth/verify-2fa
Request:
{
    "token": "string"
}

Response 200:
{
    "verified": true,
    "message": "2FA enabled successfully"
}
```

### Agents APIs

```python
# GET /api/v1/agents
Headers: Authorization: Bearer {token}
Query Params:
  - department: string?
  - is_active: boolean?
  - page: int? (default: 1)
  - limit: int? (default: 20)

Response 200:
{
    "agents": [
        {
            "id": "uuid",
            "agent_id": "string",
            "name": "string",
            "description": "string",
            "capabilities": ["array"],
            "department": "string",
            "is_active": boolean,
            "metrics": {
                "total_executions": int,
                "success_rate": float,
                "average_quality_score": float,
                "average_response_time": float
            }
        }
    ],
    "pagination": {
        "page": int,
        "limit": int,
        "total": int,
        "pages": int
    }
}

# GET /api/v1/agents/{agent_id}
Response 200:
{
    "id": "uuid",
    "agent_id": "string",
    "name": "string",
    "description": "string",
    "capabilities": ["array"],
    "system_prompt": "string",
    "model_config": {
        "model": "string",
        "temperature": float,
        "max_tokens": int
    },
    "preferred_platform": "string",
    "fallback_platforms": ["array"],
    "is_active": boolean,
    "metrics": {
        "total_executions": int,
        "successful_executions": int,
        "failed_executions": int,
        "average_quality_score": float,
        "average_response_time": float,
        "average_cost": float,
        "last_execution_at": "datetime"
    }
}

# POST /api/v1/agents
Headers: Authorization: Bearer {token}
Permissions: manage_agents

Request:
{
    "name": "string",
    "description": "string",
    "capabilities": ["array"],
    "system_prompt": "string",
    "model_config": {
        "model": "string",
        "temperature": float,
        "max_tokens": int
    },
    "preferred_platform": "string",
    "department": "string"
}

Response 201:
{
    "id": "uuid",
    "agent_id": "string",
    "message": "Agent created successfully"
}

# PUT /api/v1/agents/{agent_id}
# PATCH /api/v1/agents/{agent_id}/toggle-active
# DELETE /api/v1/agents/{agent_id}
```

### Workflows APIs

```python
# GET /api/v1/workflows
Query Params:
  - department: string?
  - status: string?
  - search: string?
  - page: int?
  - limit: int?

Response 200:
{
    "workflows": [
        {
            "id": "uuid",
            "workflow_id": "string",
            "name": "string",
            "description": "string",
            "department": "string",
            "status": "string",
            "total_steps": int,
            "estimated_duration_minutes": int,
            "created_by": "string",
            "created_at": "datetime"
        }
    ],
    "pagination": {...}
}

# POST /api/v1/workflows
Request:
{
    "name": "string",
    "description": "string",
    "department": "string",
    "trigger_type": "manual|scheduled|event",
    "schedule_cron": "string?",
    "steps": [
        {
            "order": int,
            "name": "string",
            "agent_id": "uuid",
            "command_template_id": "uuid",
            "input_mapping": {},
            "output_mapping": {},
            "timeout_seconds": int,
            "dependencies": ["uuid"],
            "parallel": boolean
        }
    ]
}

Response 201:
{
    "id": "uuid",
    "workflow_id": "string",
    "message": "Workflow created successfully"
}

# POST /api/v1/workflows/{workflow_id}/execute
Request:
{
    "input_data": {
        "key": "value"
    },
    "priority": "high|medium|low"
}

Response 202:
{
    "execution_id": "uuid",
    "status": "queued",
    "message": "Workflow execution started",
    "estimated_completion": "datetime"
}

# GET /api/v1/workflows/executions/{execution_id}
Response 200:
{
    "execution_id": "uuid",
    "workflow_id": "uuid",
    "state": "running|completed|failed",
    "progress": {
        "total_steps": int,
        "completed_steps": int,
        "failed_steps": int,
        "current_step": int,
        "percentage": float
    },
    "started_at": "datetime",
    "completed_at": "datetime?",
    "results": {},
    "errors": {}
}

# WebSocket /api/v1/workflows/executions/{execution_id}/stream
# Real-time updates for workflow execution
```

### Commands APIs

```python
# GET /api/v1/commands
Query Params:
  - category: string?
  - agent_id: uuid?
  - search: string?

Response 200:
{
    "commands": [
        {
            "id": "uuid",
            "command_id": "string",
            "name": "string",
            "description": "string",
            "category": "string",
            "agent_ids": ["uuid"],
            "estimated_duration_minutes": int,
            "difficulty_level": "string"
        }
    ]
}

# GET /api/v1/commands/{command_id}
# POST /api/v1/commands
# PUT /api/v1/commands/{command_id}
```

### Results APIs

```python
# GET /api/v1/results
Query Params:
  - execution_id: uuid?
  - agent_id: uuid?
  - date_from: date?
  - date_to: date?

Response 200:
{
    "results": [
        {
            "task_id": "uuid",
            "execution_id": "uuid",
            "agent_id": "uuid",
            "summary": "string",
            "quality_score": float,
            "confidence_score": float,
            "created_at": "datetime"
        }
    ]
}

# GET /api/v1/results/{task_id}
Response 200:
{
    "task_id": "uuid",
    "execution_id": "uuid",
    "agent_id": "uuid",
    "command_id": "uuid",
    "summary": "string",
    "results": {},
    "self_critique": "string",
    "improvements": ["array"],
    "alternatives": ["array"],
    "action_items": [
        {
            "title": "string",
            "description": "string",
            "priority": "string",
            "assigned_to": "uuid?",
            "due_date": "datetime?"
        }
    ],
    "quality_score": float,
    "confidence_score": float,
    "duration_seconds": float,
    "tokens_used": int,
    "cost": float,
    "created_at": "datetime"
}

# POST /api/v1/results/{task_id}/feedback
Request:
{
    "rating": int,  # 1-5
    "feedback": "string",
    "issues": ["array"]
}

Response 200:
{
    "message": "Feedback recorded"
}
```

### Analytics & Metrics APIs

```python
# GET /api/v1/analytics/overview
Response 200:
{
    "total_workflows_today": int,
    "total_workflows_completed": int,
    "active_agents": int,
    "total_cost_today": float,
    "average_quality_score": float,
    "success_rate": float
}

# GET /api/v1/analytics/agents/{agent_id}/performance
Query Params:
  - period: "today|week|month|year"

Response 200:
{
    "agent_id": "uuid",
    "period": "string",
    "metrics": {
        "total_executions": int,
        "success_rate": float,
        "average_quality_score": float,
        "average_response_time": float,
        "total_cost": float,
        "total_tokens": int
    },
    "timeline": [
        {
            "date": "date",
            "executions": int,
            "success_rate": float,
            "quality_score": float
        }
    ]
}

# GET /api/v1/analytics/costs
Query Params:
  - start_date: date
  - end_date: date
  - platform: string?

Response 200:
{
    "total_cost": float,
    "by_platform": {
        "openai": float,
        "claude": float,
        "gemini": float
    },
    "by_agent": {
        "agent_id": float
    },
    "timeline": [
        {
            "date": "date",
            "cost": float
        }
    ]
}
```

---

# 2. Agent Dispatcher - Conflict Resolution

## 2.1 خوارزمية متقدمة مع Conflict Resolution

```python
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class ConflictResolutionStrategy(Enum):
    PRIORITY_BASED = "priority"  # أعلى أولوية
    LOAD_BALANCED = "load_balanced"  # توزيع الحمل
    COST_OPTIMIZED = "cost_optimized"  # الأقل تكلفة
    QUALITY_OPTIMIZED = "quality_optimized"  # الأعلى جودة
    HYBRID = "hybrid"  # مزيج

@dataclass
class AgentCandidate:
    agent: Agent
    score: float
    factors: Dict[str, float]
    current_load: int
    estimated_cost: float
    estimated_duration: float

class AdvancedAgentDispatcher:
    """
    Agent Dispatcher متقدم مع حل التعارضات
    """
    def __init__(
        self,
        conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.HYBRID
    ):
        self.conflict_strategy = conflict_strategy
        self.agent_locks = {}  # لمنع race conditions
        self.agent_queues = {}  # queue لكل agent
    
    async def select_agent(
        self,
        task: Task,
        exclude_agents: List[str] = [],
        required_capabilities: List[AgentCapability] = []
    ) -> Agent:
        """
        اختيار Agent مع معالجة التعارضات
        """
        # 1. Get all capable agents
        candidates = await self._get_candidates(
            task,
            exclude_agents,
            required_capabilities
        )
        
        if not candidates:
            raise NoAgentAvailableError("No capable agents found")
        
        # 2. Score all candidates
        scored_candidates = []
        for agent in candidates:
            score_data = await self._score_agent_comprehensive(agent, task)
            scored_candidates.append(score_data)
        
        # 3. Apply conflict resolution strategy
        selected = await self._resolve_conflicts(
            scored_candidates,
            task
        )
        
        # 4. Reserve agent (prevent concurrent assignments)
        await self._reserve_agent(selected.agent, task)
        
        return selected.agent
    
    async def _score_agent_comprehensive(
        self,
        agent: Agent,
        task: Task
    ) -> AgentCandidate:
        """
        تسجيل شامل للـ Agent
        """
        factors = {}
        
        # 1. Capability Match (30%)
        capability_score = self._calculate_capability_match(agent, task)
        factors['capability'] = capability_score * 0.30
        
        # 2. Historical Performance (25%)
        performance_score = agent.metrics.average_quality_score / 10.0
        factors['performance'] = performance_score * 0.25
        
        # 3. Current Load (20%)
        current_load = await self._get_agent_current_load(agent.id)
        load_score = max(0, 1.0 - (current_load / agent.max_concurrent_tasks))
        factors['load'] = load_score * 0.20
        
        # 4. Cost Efficiency (15%)
        estimated_cost = await self._estimate_task_cost(agent, task)
        cost_score = 1.0 - min(1.0, estimated_cost / self.max_acceptable_cost)
        factors['cost'] = cost_score * 0.15
        
        # 5. Response Time (10%)
        estimated_duration = await self._estimate_task_duration(agent, task)
        time_score = 1.0 - min(1.0, estimated_duration / self.max_acceptable_time)
        factors['speed'] = time_score * 0.10
        
        total_score = sum(factors.values())
        
        return AgentCandidate(
            agent=agent,
            score=total_score,
            factors=factors,
            current_load=current_load,
            estimated_cost=estimated_cost,
            estimated_duration=estimated_duration
        )
    
    async def _resolve_conflicts(
        self,
        candidates: List[AgentCandidate],
        task: Task
    ) -> AgentCandidate:
        """
        حل التعارضات بين Agents متساوية في النقاط
        """
        if self.conflict_strategy == ConflictResolutionStrategy.PRIORITY_BASED:
            # Sort by score, then by priority
            return max(candidates, key=lambda c: (c.score, c.agent.priority))
        
        elif self.conflict_strategy == ConflictResolutionStrategy.LOAD_BALANCED:
            # Prefer agents with lower load
            return min(candidates, key=lambda c: (
                -c.score,  # Higher score first
                c.current_load  # Lower load second
            ))
        
        elif self.conflict_strategy == ConflictResolutionStrategy.COST_OPTIMIZED:
            # Prefer lower cost while maintaining minimum quality
            quality_threshold = 0.7
            qualified = [c for c in candidates if c.score >= quality_threshold]
            if qualified:
                return min(qualified, key=lambda c: c.estimated_cost)
            return max(candidates, key=lambda c: c.score)
        
        elif self.conflict_strategy == ConflictResolutionStrategy.QUALITY_OPTIMIZED:
            # Always pick highest quality
            return max(candidates, key=lambda c: c.score)
        
        else:  # HYBRID
            # Weighted decision based on task priority
            if task.priority == "high":
                # Quality > Speed > Cost
                return max(candidates, key=lambda c: (
                    c.score * 0.6,
                    -c.estimated_duration * 0.3,
                    -c.estimated_cost * 0.1
                ))
            elif task.priority == "low":
                # Cost > Load > Quality
                return min(candidates, key=lambda c: (
                    c.estimated_cost * 0.5,
                    c.current_load * 0.3,
                    -c.score * 0.2
                ))
            else:  # medium
                # Balanced
                return max(candidates, key=lambda c: c.score)
    
    async def _reserve_agent(self, agent: Agent, task: Task):
        """
        حجز Agent لمنع التعيين المتزامن
        """
        async with self.agent_locks.get(agent.id, asyncio.Lock()):
            # Add task to agent's queue
            if agent.id not in self.agent_queues:
                self.agent_queues[agent.id] = []
            
            self.agent_queues[agent.id].append(task.id)
            
            # Update agent load
            await self._update_agent_load(agent.id)
    
    async def release_agent(self, agent_id: str, task_id: str):
        """
        تحرير Agent بعد انتهاء المهمة
        """
        if agent_id in self.agent_queues:
            try:
                self.agent_queues[agent_id].remove(task_id)
            except ValueError:
                pass
            
            await self._update_agent_load(agent_id)
```

## 2.2 Multi-Agent Orchestration

```python
class MultiAgentOrchestrator:
    """
    تنسيق مهام تحتاج عدة Agents
    """
    async def execute_complex_task(
        self,
        task: ComplexTask
    ) -> Dict:
        """
        تنفيذ مهمة معقدة تحتاج عدة agents
        """
        # 1. Break down task into subtasks
        subtasks = await self._decompose_task(task)
        
        # 2. Assign agent to each subtask
        assignments = {}
        for subtask in subtasks:
            agent = await self.dispatcher.select_agent(subtask)
            assignments[subtask.id] = agent
        
        # 3. Execute in parallel where possible
        results = await self._execute_parallel(assignments, subtasks)
        
        # 4. Merge results
        final_result = await self._merge_results(results)
        
        return final_result
    
    async def _execute_parallel(
        self,
        assignments: Dict,
        subtasks: List[Task]
    ) -> Dict:
        """
        تنفيذ متوازي للمهام المستقلة
        """
        # Build dependency graph
        dag = self._build_dependency_graph(subtasks)
        
        results = {}
        
        # Execute level by level
        for level in dag:
            tasks = []
            for subtask in level:
                agent = assignments[subtask.id]
                task_coro = self._execute_subtask(agent, subtask)
                tasks.append(task_coro)
            
            # Execute this level in parallel
            level_results = await asyncio.gather(*tasks)
            
            # Store results
            for subtask, result in zip(level, level_results):
                results[subtask.id] = result
        
        return results
```

---

# 3. Caching Strategy المتقدمة

## 3.1 Multi-Layer Caching

```python
from redis import Redis
from typing import Optional, Any
import hashlib
import json

class CacheLayer(Enum):
    MEMORY = "memory"  # In-process cache
    REDIS = "redis"  # Distributed cache
    DATABASE = "database"  # Persistent cache

@dataclass
class CacheConfig:
    ttl_seconds: int
    layers: List[CacheLayer]
    invalidation_strategy: str  # "ttl" | "manual" | "event"

class AdvancedCacheManager:
    """
    نظام caching متعدد الطبقات
    """
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.memory_cache = {}  # Simple dict للـ in-memory
        
        # Cache configurations for different data types
        self.configs = {
            'agent': CacheConfig(
                ttl_seconds=300,  # 5 minutes
                layers=[CacheLayer.MEMORY, CacheLayer.REDIS],
                invalidation_strategy="manual"
            ),
            'command_template': CacheConfig(
                ttl_seconds=600,  # 10 minutes
                layers=[CacheLayer.MEMORY, CacheLayer.REDIS],
                invalidation_strategy="manual"
            ),
            'workflow_result': CacheConfig(
                ttl_seconds=3600,  # 1 hour
                layers=[CacheLayer.REDIS, CacheLayer.DATABASE],
                invalidation_strategy="ttl"
            ),
            'ai_response': CacheConfig(
                ttl_seconds=7200,  # 2 hours
                layers=[CacheLayer.REDIS],
                invalidation_strategy="ttl"
            ),
            'user_session': CacheConfig(
                ttl_seconds=1800,  # 30 minutes
                layers=[CacheLayer.REDIS],
                invalidation_strategy="ttl"
            ),
            'metrics': CacheConfig(
                ttl_seconds=60,  # 1 minute
                layers=[CacheLayer.MEMORY],
                invalidation_strategy="ttl"
            )
        }
    
    async def get(
        self,
        cache_type: str,
        key: str
    ) -> Optional[Any]:
        """
        الحصول على قيمة من الـ cache
        """
        config = self.configs.get(cache_type)
        if not config:
            return None
        
        # Try each layer in order
        for layer in config.layers:
            if layer == CacheLayer.MEMORY:
                value = self._get_from_memory(cache_type, key)
                if value is not None:
                    return value
            
            elif layer == CacheLayer.REDIS:
                value = await self._get_from_redis(cache_type, key)
                if value is not None:
                    # Populate higher layers
                    await self._populate_higher_layers(
                        cache_type, key, value, layer, config.layers
                    )
                    return value
            
            elif layer == CacheLayer.DATABASE:
                value = await self._get_from_database(cache_type, key)
                if value is not None:
                    await self._populate_higher_layers(
                        cache_type, key, value, layer, config.layers
                    )
                    return value
        
        return None
    
    async def set(
        self,
        cache_type: str,
        key: str,
        value: Any,
        ttl_override: Optional[int] = None
    ):
        """
        حفظ قيمة في الـ cache
        """
        config = self.configs.get(cache_type)
        if not config:
            return
        
        ttl = ttl_override or config.ttl_seconds
        
        # Store in all configured layers
        for layer in config.layers:
            if layer == CacheLayer.MEMORY:
                self._set_in_memory(cache_type, key, value, ttl)
            
            elif layer == CacheLayer.REDIS:
                await self._set_in_redis(cache_type, key, value, ttl)
            
            elif layer == CacheLayer.DATABASE:
                await self._set_in_database(cache_type, key, value)
    
    async def invalidate(
        self,
        cache_type: str,
        key: Optional[str] = None,
        pattern: Optional[str] = None
    ):
        """
        إبطال cache
        """
        if key:
            # Invalidate specific key
            await self._invalidate_key(cache_type, key)
        elif pattern:
            # Invalidate by pattern
            await self._invalidate_pattern(cache_type, pattern)
        else:
            # Invalidate all
            await self._invalidate_all(cache_type)
    
    def _generate_cache_key(
        self,
        cache_type: str,
        key: str
    ) -> str:
        """
        توليد cache key موحد
        """
        return f"hishamos:{cache_type}:{key}"
    
    async def _get_from_redis(
        self,
        cache_type: str,
        key: str
    ) -> Optional[Any]:
        """
        الحصول من Redis
        """
        cache_key = self._generate_cache_key(cache_type, key)
        value = await self.redis.get(cache_key)
        
        if value:
            return json.loads(value)
        return None
    
    async def _set_in_redis(
        self,
        cache_type: str,
        key: str,
        value: Any,
        ttl: int
    ):
        """
        الحفظ في Redis
        """
        cache_key = self._generate_cache_key(cache_type, key)
        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(value, default=str)
        )
```

## 3.2 Smart Caching للـ AI Responses

```python
class AIResponseCache:
    """
    Caching ذكي لاستجابات AI
    """
    def __init__(self, cache_manager: AdvancedCacheManager):
        self.cache = cache_manager
    
    def generate_prompt_hash(self, prompt: str, config: Dict) -> str:
        """
        توليد hash للـ prompt مع الـ config
        """
        # Combine prompt + relevant config
        cache_input = {
            'prompt': prompt,
            'model': config.get('model'),
            'temperature': config.get('temperature'),
            # Ignore irrelevant fields like timestamps
        }
        
        cache_string = json.dumps(cache_input, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()
    
    async def get_cached_response(
        self,
        prompt: str,
        config: Dict
    ) -> Optional[AIResponse]:
        """
        محاولة الحصول على استجابة من الـ cache
        """
        prompt_hash = self.generate_prompt_hash(prompt, config)
        
        cached = await self.cache.get('ai_response', prompt_hash)
        
        if cached:
            logger.info(f"Cache HIT for prompt hash: {prompt_hash[:8]}")
            return AIResponse(**cached)
        
        logger.info(f"Cache MISS for prompt hash: {prompt_hash[:8]}")
        return None
    
    async def cache_response(
        self,
        prompt: str,
        config: Dict,
        response: AIResponse
    ):
        """
        حفظ استجابة في الـ cache
        """
        prompt_hash = self.generate_prompt_hash(prompt, config)
        
        await self.cache.set(
            'ai_response',
            prompt_hash,
            response.dict()
        )
```

---

# 4. State Management التفصيلي

## 4.1 Transaction Management

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class TransactionManager:
    """
    إدارة Transactions للـ workflows
    """
    def __init__(self, db_session):
        self.session = db_session
        self.savepoints = []
    
    @asynccontextmanager
    async def transaction(
        self,
        isolation_level: str = "READ_COMMITTED"
    ) -> AsyncGenerator:
        """
        Transaction context manager
        """
        await self.session.execute(
            f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"
        )
        
        try:
            yield self.session
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
    
    @asynccontextmanager
    async def savepoint(self, name: str) -> AsyncGenerator:
        """
        Savepoint للـ partial rollback
        """
        await self.session.execute(f"SAVEPOINT {name}")
        self.savepoints.append(name)
        
        try:
            yield
        except Exception as e:
            await self.session.execute(f"ROLLBACK TO SAVEPOINT {name}")
            logger.warning(f"Rolled back to savepoint {name}")
            raise
        finally:
            if name in self.savepoints:
                self.savepoints.remove(name)

class WorkflowStateManager:
    """
    إدارة حالة Workflow مع دعم Recovery
    """
    def __init__(
        self,
        db_session,
        cache_manager: AdvancedCacheManager
    ):
        self.db = db_session
        self.cache = cache_manager
        self.transaction_mgr = TransactionManager(db_session)
    
    async def save_state(
        self,
        execution_id: str,
        state: WorkflowState,
        context: Dict,
        checkpoint: bool = False
    ):
        """
        حفظ حالة الـ workflow
        """
        async with self.transaction_mgr.transaction():
            # Update database
            await self.db.workflow_executions.update(
                {'execution_id': execution_id},
                {
                    'state': state.value,
                    'context': context,
                    'updated_at': datetime.utcnow()
                }
            )
            
            # Update cache for fast access
            await self.cache.set(
                'workflow_state',
                execution_id,
                {
                    'state': state.value,
                    'context': context
                },
                ttl_override=300
            )
            
            # Create checkpoint if requested
            if checkpoint:
                await self._create_checkpoint(execution_id, context)
    
    async def _create_checkpoint(
        self,
        execution_id: str,
        context: Dict
    ):
        """
        إنشاء checkpoint للـ recovery
        """
        await self.db.workflow_checkpoints.create({
            'execution_id': execution_id,
            'context_snapshot': context,
            'created_at': datetime.utcnow()
        })
    
    async def recover_from_checkpoint(
        self,
        execution_id: str,
        checkpoint_id: Optional[str] = None
    ) -> Dict:
        """
        استرجاع من checkpoint
        """
        if checkpoint_id:
            checkpoint = await self.db.workflow_checkpoints.get(checkpoint_id)
        else:
            # Get latest checkpoint
            checkpoint = await self.db.workflow_checkpoints.find_one(
                {'execution_id': execution_id},
                sort=[('created_at', -1)]
            )
        
        if not checkpoint:
            raise CheckpointNotFoundError(
                f"No checkpoint found for execution {execution_id}"
            )
        
        return checkpoint['context_snapshot']
    
    async def resume_workflow(
        self,
        execution_id: str,
        from_step: Optional[int] = None
    ):
        """
        استئناف workflow متوقف
        """
        # Get current state
        execution = await self.db.workflow_executions.get(execution_id)
        
        if execution['state'] not in ['paused', 'failed']:
            raise InvalidStateError(
                f"Cannot resume workflow in state: {execution['state']}"
            )
        
        # Recover context
        if from_step is not None:
            # Restore from specific checkpoint
            context = await self.recover_from_checkpoint(execution_id)
        else:
            # Continue from current state
            context = execution['context']
        
        # Update state to running
        await self.save_state(
            execution_id,
            WorkflowState.RUNNING,
            context
        )
        
        # Trigger workflow engine to continue
        await self.workflow_engine.continue_execution(
            execution_id,
            from_step or execution['current_step']
        )
```

---

**سيتم إكمال باقي النقاط في الرسالة التالية بسبب حد الطول...**

