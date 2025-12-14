# Agent-API Integration - Direct API Calling

**Document Type:** Integration Documentation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** ../04_BACKEND/03_SERVICES_IMPLEMENTATION.md, ../03_ARCHITECTURE/05_INTEGRATION_ARCHITECTURE.md  
**File Size:** 493 lines

---

## 📋 Purpose

This document describes how agents integrate with HishamOS APIs through the AgentAPICaller service.

---

## 🔗 Integration Architecture

### Integration Flow

```
Agent Execution
    │
    ▼
AgentAPICaller (initialized with user context)
    │
    ├──> Authenticate (JWT token generation)
    │
    ├──> Authorize (permission checks)
    │
    ├──> Make API Request (HTTP client)
    │
    ├──> Handle Response
    │
    └──> Return Result to Agent
```

---

## 🔧 Integration Implementation

### Step 1: Agent Context Setup

**In Workflow Executor:**
```python
# Create AgentAPICaller instance
api_caller = AgentAPICaller(user=request.user)

# Add to agent context
context = {
    'api_caller': api_caller,
    'user_id': str(request.user.id),
    ...
}
```

---

### Step 2: Agent Usage

**Agent receives context and uses API caller:**
```python
# In agent execution
api_caller = context.get('api_caller')

if api_caller:
    # Call API directly
    story_data = await api_caller.create_story(
        project_id=project_id,
        title="User login story",
        description="As a user..."
    )
```

---

### Step 3: API Call Execution

**AgentAPICaller makes authenticated request:**
```python
async def create_story(self, project_id, title, description, **kwargs):
    data = {
        'project': project_id,
        'title': title,
        'description': description,
        **kwargs
    }
    return await self.call('POST', f'/projects/{project_id}/stories/', data=data)
```

---

## 🔐 Authentication Integration

### Authentication Flow

1. AgentAPICaller initialized with user
2. JWT token generated via `jwt_service.generate_token(user)`
3. Token included in API request headers
4. Backend validates token
5. Request processed with user context

---

## 🔄 Error Handling Integration

### Error Flow

```
API Call
    │
    ├──> Success → Return data to agent
    │
    └──> Error → Catch exception
            │
            ├──> Retry (if retriable)
            │
            └──> Return error to agent
```

---

## 🔗 Related Documentation

- **Services:** `../04_BACKEND/03_SERVICES_IMPLEMENTATION.md`
- **Integration Architecture:** `../03_ARCHITECTURE/05_INTEGRATION_ARCHITECTURE.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

