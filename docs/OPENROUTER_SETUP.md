# OpenRouter Integration Setup Guide

This guide explains how to set up and use OpenRouter with Mistral 7B Instruct (free) in HishamOS.

## Overview

OpenRouter provides access to multiple AI models through an OpenAI-compatible API. We've integrated it to support the free Mistral 7B Instruct model for testing and development.

## Features

- ✅ OpenAI-compatible API adapter
- ✅ Support for Mistral 7B Instruct (free)
- ✅ Streaming completions
- ✅ Cost tracking (free models = $0)
- ✅ Automatic fallback to mock if API fails

## Setup Instructions

### 1. Get Your OpenRouter API Key

1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Sign up or log in
3. Go to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Copy the API key

### 2. Run the Setup Command

```bash
cd backend
python manage.py setup_openrouter --api-key YOUR_OPENROUTER_API_KEY
```

**Optional parameters:**
- `--site-url`: Your site URL for OpenRouter rankings (default: http://localhost:3000)
- `--site-name`: Your site name (default: HishamOS)
- `--update`: Update existing OpenRouter platform if it already exists

**Example:**
```bash
python manage.py setup_openrouter \
  --api-key sk-or-v1-abc123... \
  --site-url https://myapp.com \
  --site-name "My HishamOS Instance"
```

### 3. Restart Services

After running the setup command, restart your Django server and Celery workers:

```bash
# Restart Django
python manage.py runserver

# Restart Celery (if running)
celery -A core worker --loglevel=info
```

## What Gets Created

### 1. OpenRouter AI Platform

- **Platform Name**: `openrouter`
- **Display Name**: OpenRouter
- **API URL**: `https://openrouter.ai/api/v1`
- **Default Model**: `mistralai/mistral-7b-instruct:free`
- **Status**: Active and enabled

### 2. Test Agent

- **Agent ID**: `mistral-7b-assistant`
- **Name**: Mistral 7B Assistant
- **Platform**: OpenRouter
- **Model**: `mistralai/mistral-7b-instruct:free`
- **Capabilities**: Code Generation, Code Review, Requirements Analysis, Documentation, Research

## Usage

### In Chat

1. Go to the Chat interface
2. Select the "Mistral 7B Assistant" agent (or any agent configured to use OpenRouter)
3. Start chatting - responses will come from real AI, not mock

### In Workflows

1. Create or edit a workflow
2. Set the agent field to `mistral-7b-assistant` (or the agent's name/ID)
3. Execute the workflow - it will use real AI

### Programmatically

```python
from apps.agents.models import Agent
from apps.agents.services.execution_engine import ExecutionEngine

# Get the agent
agent = Agent.objects.get(agent_id='mistral-7b-assistant')

# Execute
engine = ExecutionEngine()
result = await engine.execute(
    agent=agent,
    input_data={'prompt': 'Hello, how are you?'},
    user=request.user
)
```

## Model Information

### Mistral 7B Instruct (Free)

- **Model ID**: `mistralai/mistral-7b-instruct:free`
- **Context Length**: 32,768 tokens
- **Cost**: $0 (free)
- **Provider**: Mistral AI via OpenRouter

### Available Models

The OpenRouter adapter supports these models (you can add more in `openrouter_adapter.py`):

- `mistral-7b-instruct-free` → `mistralai/mistral-7b-instruct:free`
- `mistral-7b-instruct` → `mistralai/mistral-7b-instruct:free`

## Configuration

### Updating API Key

```python
from apps.integrations.models import AIPlatform

platform = AIPlatform.objects.get(platform_name='openrouter')
platform.set_api_key('your-new-api-key')
platform.save()
```

### Changing Default Model

```python
platform = AIPlatform.objects.get(platform_name='openrouter')
platform.default_model = 'mistralai/mistral-7b-instruct:free'
platform.save()
```

### Adding More Models

Edit `backend/apps/integrations/adapters/openrouter_adapter.py`:

```python
MODELS = {
    'mistral-7b-instruct-free': 'mistralai/mistral-7b-instruct:free',
    'mistral-7b-instruct': 'mistralai/mistral-7b-instruct:free',
    'your-model-name': 'provider/model-id',  # Add here
}
```

## Troubleshooting

### Agent Not Using Real AI

1. **Check platform status**: Ensure OpenRouter platform is `active` and `is_enabled=True`
2. **Verify API key**: Check that the API key is set correctly
3. **Check agent configuration**: Ensure agent's `preferred_platform` is `openrouter`
4. **Restart services**: Restart Django and Celery workers

### API Errors

- **401 Unauthorized**: Invalid API key - update it using the setup command
- **429 Rate Limit**: Too many requests - wait or upgrade your OpenRouter plan
- **500 Server Error**: OpenRouter service issue - check [OpenRouter Status](https://openrouter.ai/status)

### Mock Responses Still Appearing

1. Check that OpenRouter platform exists and is enabled
2. Verify the agent's preferred platform is set to `openrouter`
3. Check Django logs for adapter initialization errors
4. Ensure the adapter registry is initialized (restart Django)

## Architecture

### Adapter Structure

```
OpenRouterAdapter (extends BaseAIAdapter)
├── Uses OpenAI-compatible client
├── Custom base URL: https://openrouter.ai/api/v1
├── Supports streaming
└── Cost calculation (free models = $0)
```

### Integration Points

1. **Adapter Registry**: `backend/apps/integrations/services/adapter_registry.py`
2. **Base Agent**: `backend/apps/agents/engine/base_agent.py`
3. **Execution Engine**: `backend/apps/agents/services/execution_engine.py`
4. **Chat Consumer**: `backend/apps/chat/consumers.py`

## API Reference

### OpenRouter API

- **Base URL**: `https://openrouter.ai/api/v1`
- **Documentation**: https://openrouter.ai/docs
- **Models**: https://openrouter.ai/models

### Headers

OpenRouter supports optional headers:
- `HTTP-Referer`: Your site URL (stored in `organization_id`)
- `X-Title`: Your site name (from `display_name`)

These are automatically included in requests.

## Security Notes

- API keys are encrypted in the database
- Use environment variables for production API keys
- Never commit API keys to version control
- Rotate API keys regularly

## Next Steps

1. ✅ Set up OpenRouter platform
2. ✅ Create test agent
3. ✅ Test in chat interface
4. ✅ Use in workflows
5. ✅ Monitor usage and costs (free models = $0)

## Support

- **OpenRouter Docs**: https://openrouter.ai/docs
- **OpenRouter Discord**: https://discord.gg/openrouter
- **HishamOS Issues**: Report issues in the project repository



