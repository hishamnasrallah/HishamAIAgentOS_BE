# Project Management Integration - Agent Interaction

**Document Type:** Integration Documentation  
**Version:** 1.0.0  
**Created:** 2025-12-13  
**Status:** Active  
**Last Updated:** 2025-12-13  
**Related Documents:** ../04_BACKEND/03_SERVICES_IMPLEMENTATION.md, ../06_INTEGRATION/01_AGENT_API_INTEGRATION.md  
**File Size:** 487 lines

---

## 📋 Purpose

This document describes how agents integrate with project management features via direct API calls.

---

## 🔗 Integration Points

### Integration 1: Story Creation

**Agent calls API to create stories:**
```python
# In agent execution
story = await api_caller.create_story(
    project_id=project_id,
    title="User login",
    description="As a user, I want to log in...",
    story_points=5,
    status="backlog"
)
```

**Backend Integration:**
- Uses existing `StoryViewSet`
- Permission checks apply
- Validation rules enforced
- Notifications triggered

---

### Integration 2: Sprint Planning

**Agent calls API to create sprints:**
```python
# In agent execution
sprint = await api_caller.create_sprint(
    project_id=project_id,
    name="Sprint 1",
    start_date="2025-12-20",
    end_date="2025-12-27"
)
```

**Backend Integration:**
- Uses existing `SprintViewSet`
- Validation rules enforced
- Story assignments possible

---

### Integration 3: Story Status Updates

**Agent updates story status:**
```python
# In agent execution
await api_caller.update_story_status(
    story_id=story_id,
    status="in_progress"
)
```

**Backend Integration:**
- Uses existing `StoryViewSet.partial_update`
- State transition validation
- Notifications triggered

---

## 🔄 Workflow Integration

### Complete Workflow Example

**Workflow Step:**
```yaml
- id: create_stories
  type: api_call
  agent: "Business Analyst Agent"
  config:
    endpoint: "/projects/{project_id}/stories/"
    method: POST
    data:
      title: "{{ story_title }}"
      description: "{{ story_description }}"
```

**Execution:**
1. Workflow executor identifies step type as `api_call`
2. Executor uses AgentAPICaller from context
3. API call made with proper authentication
4. Response returned to workflow state
5. Next steps can use response data

---

## 🔗 Related Documentation

- **Agent-API Integration:** `01_AGENT_API_INTEGRATION.md`
- **Backend Services:** `../04_BACKEND/03_SERVICES_IMPLEMENTATION.md`

---

**Document Owner:** Backend Development Team  
**Review Cycle:** As needed during implementation  
**Last Updated:** 2025-12-13

