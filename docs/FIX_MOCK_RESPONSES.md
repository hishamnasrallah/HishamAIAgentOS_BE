# Fix: Chat Showing Mock Responses Instead of Real AI

If you're seeing mock responses in the chat interface, follow these steps to fix it.

## Quick Diagnosis

Run this command to check your setup:

```bash
cd backend
python scripts/check-ai-setup.py
```

This will show you what's missing.

## Common Issues and Fixes

### Issue 1: OpenRouter Platform Not Set Up

**Symptom:** `check-ai-setup.py` shows "OpenRouter platform NOT FOUND"

**Fix:**
1. Get your OpenRouter API key from https://openrouter.ai/keys
2. Run the setup command:

```bash
cd backend
python manage.py setup_openrouter --api-key YOUR_OPENROUTER_API_KEY
```

### Issue 2: Django Not Restarted After Setup

**Symptom:** Setup completed but still getting mock responses

**Fix:**
1. **Restart Django server** - This is critical! The adapter registry only initializes on startup.
2. Stop your Django server (Ctrl+C)
3. Start it again:

```bash
python manage.py runserver
```

### Issue 3: Using Wrong Agent

**Symptom:** Using an agent that's not configured for OpenRouter

**Fix:**
1. When creating a new chat, make sure to select **"Mistral 7B Assistant"** agent
2. This agent is specifically configured to use OpenRouter

### Issue 4: Agent's Preferred Platform Not Set Correctly

**Symptom:** Agent exists but preferred_platform is not 'openrouter'

**Fix:**
```bash
python manage.py setup_openrouter --api-key YOUR_KEY --update
```

Or manually update in Django shell:
```python
from apps.agents.models import Agent
agent = Agent.objects.get(agent_id='mistral-7b-assistant')
agent.preferred_platform = 'openrouter'
agent.save()
```

## Step-by-Step Complete Fix

### Step 1: Run Setup Command

```bash
cd backend
python manage.py setup_openrouter --api-key sk-or-v1-YOUR_ACTUAL_KEY
```

You should see:
```
✓ Created OpenRouter platform: OpenRouter
✓ Created agent: Mistral 7B Assistant
```

### Step 2: Restart Django Server

**IMPORTANT:** You must restart Django for the adapter registry to pick up the new platform.

```bash
# Stop Django (Ctrl+C)
# Then start again:
python manage.py runserver
```

### Step 3: Verify Setup

```bash
python scripts/check-ai-setup.py
```

Should show:
- ✓ OpenRouter platform found
- ✓ Mistral agent found
- Platform: openrouter

### Step 4: Test in Chat

1. Go to Chat interface in frontend
2. Click "New Chat"
3. Select **"Mistral 7B Assistant"** from agent list
4. Send a message - should get real AI response, not mock

## How It Works

1. **Adapter Registry** loads all enabled AI platforms from database when Django starts
2. **BaseAgent** tries the agent's `preferred_platform` first (e.g., 'openrouter')
3. If that fails, it tries `fallback_platforms`
4. If all real platforms fail, it falls back to `mock`

## Verification Checklist

- [ ] OpenRouter platform exists in database (`is_enabled=True`, `status='active'`)
- [ ] OpenRouter API key is set correctly
- [ ] Mistral 7B Assistant agent exists
- [ ] Agent's `preferred_platform` = 'openrouter'
- [ ] Django server restarted after setup
- [ ] Using "Mistral 7B Assistant" agent in chat conversation

## Still Not Working?

### Check Django Logs

Look for adapter initialization messages:
```
INFO: Initialized adapter for openrouter
INFO: Registry initialized with 2 adapters
```

If you see errors, check:
- API key is valid
- OpenRouter service is accessible
- Platform status is 'active'

### Check Agent Configuration

```python
from apps.agents.models import Agent
agent = Agent.objects.get(agent_id='mistral-7b-assistant')
print(f"Platform: {agent.preferred_platform}")
print(f"Model: {agent.model_name}")
print(f"Status: {agent.status}")
```

### Test Adapter Directly

```python
from apps.integrations.services import get_registry
registry = await get_registry()
adapter = registry.get_adapter('openrouter')
if adapter:
    print("OpenRouter adapter is available!")
else:
    print("OpenRouter adapter NOT found in registry")
```

## Summary

The most common issue is **forgetting to restart Django** after running the setup command. The adapter registry only loads platforms when Django starts, so a restart is required.

After restart, the chat will use real AI when:
- You select the "Mistral 7B Assistant" agent
- The OpenRouter platform is enabled and configured
- The adapter registry has loaded the OpenRouter adapter

