# AI Provider Conversation Management

## Overview

This document describes the unified conversation management system for handling conversation context across different AI providers. The system dynamically adapts to each provider's capabilities to minimize token costs while maintaining conversation context.

## Problem Statement

Different AI providers handle conversation context differently:
- **Stateless providers** (OpenAI Chat Completions, Anthropic Claude, OpenRouter): Must send full message history with each request
- **Stateful providers** (Google Gemini with conversation_id): Can maintain context server-side using conversation/thread IDs

Sending full history for every request:
- Increases token costs significantly
- Hits token limits faster
- Slows down responses

## Solution Architecture

### 1. Unified Conversation Manager

The `ConversationManager` service (`apps/integrations/services/conversation_manager.py`) provides:
- Provider capability detection
- Optimal message selection based on provider strategy
- Conversation ID extraction from provider responses
- Context storage and retrieval

### 2. Platform Configuration

Each `AIPlatform` model instance stores conversation management capabilities:
- `conversation_strategy`: How the provider manages context (stateless, thread_id, conversation_id, etc.)
- `conversation_id_field`: Field name for conversation ID in API requests
- `returns_conversation_id`: Whether provider returns conversation IDs in responses
- `conversation_id_path`: JSON path to conversation ID in response

### 3. Conversation Context Storage

The `Conversation` model stores provider-specific context:
- `ai_provider_context`: JSON field storing thread_id, conversation_id, session_id, etc.
- `max_recent_messages`: Sliding window size for stateless providers (default: 20)

## Supported Providers

### OpenAI
- **Strategy**: `stateless` (Chat Completions API)
- **Notes**: Must send full message history. Assistants API (thread_id) requires separate setup.
- **Configuration**: Default - no special setup needed

### Anthropic Claude
- **Strategy**: `stateless`
- **Notes**: Must send full message history with each request
- **Configuration**: Default - no special setup needed

### Google Gemini
- **Strategy**: `conversation_id`
- **Conversation ID Field**: `conversation_id`
- **Returns ID**: Yes
- **Notes**: Supports conversation state via `conversation_id` parameter
- **Configuration**: Will extract and store conversation IDs automatically

### OpenRouter
- **Strategy**: `stateless`
- **Notes**: Must send full message history. Does not support conversationId parameter.
- **Configuration**: Default - no special setup needed

### DeepSeek
- **Strategy**: `stateless` (default, may change with research)
- **Notes**: Research needed on conversation management capabilities

### Grok (xAI)
- **Strategy**: `stateless` (default, may change with research)
- **Notes**: Research needed on conversation management capabilities

## How It Works

### 1. Initial Message

1. User sends first message in conversation
2. System sends message to provider (stateless providers receive just the message)
3. Provider responds
4. If provider supports conversation IDs and returns one, it's extracted and stored in `ai_provider_context`

### 2. Subsequent Messages (Stateful Providers)

1. System checks `ai_provider_context` for conversation ID
2. If ID exists, only new message is sent (provider maintains context)
3. Provider responds with context intact
4. Token costs are minimized (only new message + response)

### 3. Subsequent Messages (Stateless Providers)

1. System retrieves recent messages (sliding window of `max_recent_messages`)
2. Sends recent history + new message to provider
3. Provider responds
4. Token costs depend on sliding window size (default: 20 messages)

## Configuration

### Step 1: Run Configuration Command

```bash
cd backend
python manage.py configure_conversation_management
```

This command configures all platforms with their conversation management strategies based on current research.

### Step 2: Create Migrations

```bash
python manage.py makemigrations integrations chat
python manage.py migrate
```

This creates:
- New fields in `AIPlatform` model for conversation capabilities
- Updated `Conversation` model with `ai_provider_context` JSON field

## Usage Example

### Stateless Provider (OpenRouter)

```python
# ConversationManager automatically uses sliding window
messages = ConversationManager.get_optimal_messages_to_send(
    platform_config=openrouter_platform,
    conversation_history=history,  # Full history from DB
    conversation_context={},
    current_message="New message"
)
# Returns: Last 20 messages + new message (sliding window)
```

### Stateful Provider (Gemini)

```python
# If conversation_id exists, only new message sent
messages = ConversationManager.get_optimal_messages_to_send(
    platform_config=gemini_platform,
    conversation_history=history,
    conversation_context={'ai_provider_context': {'conversation_id': 'abc123'}},
    current_message="New message"
)
# Returns: Only new message (provider maintains context)
```

## Future Enhancements

1. **OpenAI Assistants API**: Support for thread_id based conversations
2. **Provider Research**: Deep research on DeepSeek, Grok conversation capabilities
3. **Conversation Summarization**: For very long conversations, summarize old messages
4. **Adaptive Window Sizing**: Adjust sliding window based on token usage
5. **Multi-Provider Context**: Support switching providers mid-conversation

## Testing

To test conversation management:

1. Configure platforms: `python manage.py configure_conversation_management`
2. Run migrations: `python manage.py migrate`
3. Create a conversation in the chat interface
4. Send multiple messages
5. Check `ai_provider_context` field in `Conversation` model
6. For stateful providers, verify only new messages are sent (check logs)

## Notes

- The system automatically handles provider-specific differences
- Conversation IDs are extracted and stored automatically when available
- Falls back to sliding window for stateless providers
- No code changes needed in adapters beyond implementing `extract_conversation_id()`

## Related Files

- `backend/apps/integrations/services/conversation_manager.py`: Core conversation management logic
- `backend/apps/integrations/models.py`: AIPlatform model with conversation capabilities
- `backend/apps/chat/models.py`: Conversation model with context storage
- `backend/apps/agents/engine/conversational_agent.py`: Agent-level conversation handling
- `backend/apps/integrations/adapters/base.py`: Base adapter with conversation ID extraction
- `backend/apps/integrations/management/commands/configure_conversation_management.py`: Configuration command
