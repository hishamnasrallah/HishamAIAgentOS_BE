# AI Platform Setup Commands Guide

Complete guide for setting up all AI platforms and agents in HishamOS.

---

## Quick Start

### Set Up All Platforms (Interactive)
```bash
python manage.py setup_all_platforms
```

### Set Up All Platforms (With API Keys)
```bash
python manage.py setup_all_platforms \
  --openai-key YOUR_OPENAI_KEY \
  --anthropic-key YOUR_ANTHROPIC_KEY \
  --gemini-key YOUR_GEMINI_KEY \
  --openrouter-key YOUR_OPENROUTER_KEY \
  --update
```

---

## Individual Platform Setup

### 1. OpenAI (GPT-4, GPT-3.5)

```bash
python manage.py setup_openai --api-key YOUR_OPENAI_API_KEY
```

**Options:**
- `--api-key` (required): Your OpenAI API key
- `--update`: Update existing platform
- `--create-agents`: Create default agents (default: True)

**Creates Agents:**
- `gpt-4-assistant` - GPT-4 Turbo
- `gpt-35-assistant` - GPT-3.5 Turbo

**Configuration:**
- Conversation Strategy: Stateless
- Models: gpt-4-turbo, gpt-3.5-turbo
- Full metadata extraction configured

---

### 2. Anthropic (Claude Opus, Sonnet, Haiku)

```bash
python manage.py setup_anthropic --api-key YOUR_ANTHROPIC_API_KEY
```

**Options:**
- `--api-key` (required): Your Anthropic API key
- `--update`: Update existing platform
- `--create-agents`: Create default agents (default: True)

**Creates Agents:**
- `claude-opus-assistant` - Claude Opus
- `claude-sonnet-assistant` - Claude Sonnet
- `claude-haiku-assistant` - Claude Haiku

**Configuration:**
- Conversation Strategy: Stateless
- SDK Session Support: Yes (convenience wrapper, no token savings)
- Models: claude-3-opus, claude-3-sonnet, claude-3-haiku
- Full metadata extraction configured

---

### 3. Google Gemini

```bash
python manage.py setup_gemini --api-key YOUR_GEMINI_API_KEY
```

**Options:**
- `--api-key` (required): Your Google Gemini API key
- `--update`: Update existing platform
- `--create-agents`: Create default agents (default: True)

**Creates Agents:**
- `gemini-pro-assistant` - Gemini Pro
- `gemini-vision-assistant` - Gemini Pro Vision

**Configuration:**
- Conversation Strategy: Stateless (default, needs API testing)
- Possible conversation_id support (needs verification)
- Models: gemini-pro, gemini-pro-vision
- Full metadata extraction configured

**Note:** Conversation state support needs API testing. Currently defaults to stateless.

---

### 4. OpenRouter (Multiple Models)

```bash
python manage.py setup_openrouter \
  --api-key YOUR_OPENROUTER_API_KEY \
  --site-url http://localhost:3000 \
  --site-name HishamOS
```

**Options:**
- `--api-key` (required): Your OpenRouter API key
- `--site-url`: Your site URL for OpenRouter rankings (default: http://localhost:3000)
- `--site-name`: Your site name (default: HishamOS)
- `--update`: Update existing platform

**Creates Agent:**
- `mistral-7b-assistant` - Mistral 7B Instruct (free)

**Configuration:**
- Conversation Strategy: Stateless (confirmed)
- Models: mistralai/mistral-7b-instruct:free
- Full metadata extraction configured

---

## Configuration Commands

After setting up platforms, run these commands to configure conversation management:

### 1. Configure Conversation Management
```bash
python manage.py configure_conversation_management
```
Sets conversation strategy and identifier extraction paths for all platforms.

### 2. Configure Provider Documentation
```bash
python manage.py configure_provider_documentation
```
Populates comprehensive documentation for all platforms including:
- Architecture details
- Identifier information
- Cost optimization notes
- Implementation details

---

## What Gets Created

### Platform Configuration
Each platform setup creates an `AIPlatform` record with:
- ✅ Basic configuration (API URL, model, timeout, etc.)
- ✅ **Comprehensive conversation management fields:**
  - `conversation_strategy` - How provider manages context
  - `api_stateful` - Whether API is stateful
  - `sdk_session_support` - SDK session features
  - `supported_identifiers` - List of ID types
  - `metadata_fields` - All metadata fields
  - `identifier_extraction_paths` - Extraction paths
  - `provider_notes` - Complete documentation
  - `cost_optimization_notes` - Cost strategies

### Agent Configuration
Each platform setup creates `Agent` records with:
- ✅ Agent ID, name, description
- ✅ Capabilities
- ✅ System prompts
- ✅ Model configuration
- ✅ Platform preferences

---

## Complete Setup Workflow

```bash
# Step 1: Set up platforms (choose one method)

# Method A: Interactive
python manage.py setup_all_platforms

# Method B: All at once with keys
python manage.py setup_all_platforms \
  --openai-key KEY \
  --anthropic-key KEY \
  --gemini-key KEY \
  --openrouter-key KEY \
  --update

# Method C: Individual platforms
python manage.py setup_openai --api-key KEY
python manage.py setup_anthropic --api-key KEY
python manage.py setup_gemini --api-key KEY
python manage.py setup_openrouter --api-key KEY

# Step 2: Configure conversation management
python manage.py configure_conversation_management

# Step 3: Configure provider documentation
python manage.py configure_provider_documentation

# Step 4: Restart services
# Restart Django server and Celery workers
```

---

## Verification

After setup, verify platforms:

```python
# In Django shell
from apps.integrations.models import AIPlatform
from apps.agents.models import Agent

# Check platforms
platforms = AIPlatform.objects.filter(is_enabled=True)
for p in platforms:
    print(f"{p.display_name}: {p.platform_name}")
    print(f"  Conversation Strategy: {p.conversation_strategy}")
    print(f"  API Stateful: {p.api_stateful}")
    print(f"  Has Documentation: {bool(p.provider_notes)}")

# Check agents
agents = Agent.objects.filter(status='active')
for a in agents:
    print(f"{a.name}: {a.agent_id}")
    print(f"  Platform: {a.preferred_platform}")
    print(f"  Model: {a.model_name}")
```

---

## Troubleshooting

### Platform Already Exists
Use `--update` flag to update existing platform:
```bash
python manage.py setup_openai --api-key KEY --update
```

### Skip Existing Platforms
```bash
python manage.py setup_all_platforms --skip-existing
```

### Platform Not Working
1. Check API key is correct
2. Restart Django server and Celery workers
3. Verify platform is enabled: `is_enabled=True`
4. Check logs for adapter initialization errors

---

## Summary

All setup commands now include:
- ✅ Complete conversation management configuration
- ✅ Comprehensive provider documentation
- ✅ Cost optimization notes
- ✅ Identifier extraction paths
- ✅ Metadata field definitions
- ✅ Agent creation with proper configuration

**Everything is ready to use immediately after setup!**
