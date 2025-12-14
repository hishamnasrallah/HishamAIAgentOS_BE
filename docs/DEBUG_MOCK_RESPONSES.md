# Debug: Mock Responses Instead of Real AI

## Quick Test

Run this script to test the OpenRouter adapter:

```bash
cd backend
python scripts/test-openrouter-adapter.py
```

This will:
1. Initialize the adapter registry
2. Check if OpenRouter adapter is loaded
3. Test with a real API request
4. Show any errors

## What to Look For

### ✅ Success Output:
```
✓ Registry initialized
  Adapters available: ['openrouter', 'mock']
✓ OpenRouter adapter found
✓ Response received!
  Content: OK...
```

### ❌ Problem Output:
```
✗ OpenRouter adapter NOT found in registry
  Available adapters: ['mock']
```

## Common Issues

### Issue 1: Adapter Not Initializing

**Symptom:** Test script shows only `['mock']` in adapters

**Cause:** OpenRouter platform not enabled or adapter initialization failed

**Fix:**
1. Check platform status:
```python
from apps.integrations.models import AIPlatform
platform = AIPlatform.objects.get(platform_name='openrouter')
print(f"Enabled: {platform.is_enabled}, Status: {platform.status}")
```

2. If not enabled, enable it:
```python
platform.is_enabled = True
platform.status = 'active'
platform.save()
```

3. Restart Django

### Issue 2: API Key Error

**Symptom:** Test script shows "Failed to initialize openrouter adapter"

**Fix:**
1. Re-run setup command:
```bash
python manage.py setup_openrouter --api-key YOUR_KEY --update
```

2. Verify API key is valid at https://openrouter.ai/keys

### Issue 3: Import Error

**Symptom:** "No module named 'openai'" or similar

**Fix:**
```bash
pip install openai
```

### Issue 4: Adapter Registry Not Loading

**Symptom:** No "Initialized adapter" messages in Django logs

**Check Django startup logs** - you should see:
```
INFO apps.integrations.services.adapter_registry: Initialized adapter for openrouter
INFO apps.integrations.services.adapter_registry: Registry initialized with 2 adapters
```

If you don't see these messages, the registry isn't being initialized. This happens because:
- The registry only initializes when first accessed (lazy loading)
- It might be failing silently

## Enable Verbose Logging

Add to `backend/core/settings/development.py`:

```python
LOGGING['loggers']['apps.integrations'] = {
    'level': 'DEBUG',
    'handlers': ['console', 'file'],
}
```

Then restart Django and check logs for:
- "Initialized adapter for openrouter"
- "Failed to initialize openrouter adapter"
- Any import or API key errors

## Manual Verification

### Check Registry Status:
```python
from apps.integrations.services import get_registry
import asyncio

async def check():
    registry = await get_registry()
    print("Adapters:", list(registry.get_all_adapters().keys()))
    openrouter = registry.get_adapter('openrouter')
    print("OpenRouter adapter:", openrouter is not None)

asyncio.run(check())
```

### Check Agent Configuration:
```python
from apps.agents.models import Agent
agent = Agent.objects.get(agent_id='mistral-7b-assistant')
print(f"Platform: {agent.preferred_platform}")
print(f"Model: {agent.model_name}")
```

## Still Not Working?

1. **Check Django logs** for any ERROR messages when sending a chat message
2. **Run test script** to isolate the issue
3. **Verify API key** is valid and not expired
4. **Check network** - can Django reach openrouter.ai?
5. **Try direct API call** to verify OpenRouter is working:

```python
import httpx
async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer YOUR_API_KEY"},
        json={
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [{"role": "user", "content": "Hello"}]
        }
    )
    print(response.json())
```

