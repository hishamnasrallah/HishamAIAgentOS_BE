# AI Provider Conversation Identifier Reference

## Overview

This document lists the exact field names and mechanisms each AI provider uses for conversation/thread/session management. This is critical for implementing proper conversation context management.

## Provider-Specific Identifiers

### 1. OpenAI

#### Chat Completions API (Current Implementation)
- **Status**: ⚠️ Stateless (no conversation ID support)
- **Conversation Strategy**: `stateless`
- **Field Name**: N/A (stateless)
- **Notes**: 
  - Standard Chat Completions API requires full message history
  - No built-in conversation/thread management
  - Must send full history with each request

#### Assistants API (v2) - NOT CURRENTLY IMPLEMENTED
- **Status**: ✅ Stateful (thread-based)
- **Conversation Strategy**: `assistant_thread`
- **Field Names**:
  - Request: `thread_id` (required parameter)
  - Response: `thread.id` (in thread object)
  - Also requires: `assistant_id`
- **API Endpoints**:
  - Create thread: `POST /v1/threads`
  - Create message: `POST /v1/threads/{thread_id}/messages`
  - Run: `POST /v1/threads/{thread_id}/runs`
- **Documentation**: https://platform.openai.com/docs/api-reference/assistants
- **Notes**: 
  - Different API from Chat Completions
  - Requires separate adapter implementation
  - Threads maintain context automatically

#### Conversations API (NEW - Needs Verification)
- **Status**: ⚠️ Research Needed
- **Possible Field Names**: `conversation_id`, `item_id`
- **Documentation**: Some sources mention `GET /v1/conversations/{conversation_id}/items/{item_id}`
- **Notes**: May be a newer API - needs verification with official docs

---

### 2. Anthropic Claude

#### Messages API (Current Implementation)
- **Status**: ✅ Stateless (confirmed)
- **Conversation Strategy**: `stateless`
- **Field Name**: N/A (stateless)
- **API Endpoint**: `POST /v1/messages`
- **Documentation**: https://docs.anthropic.com/en/api/messages
- **Notes**: 
  - Must send full message history with each request
  - API does not maintain conversation state
  - No conversation_id or session_id parameter

#### Claude SDK Session Management (SDK-Level)
- **Status**: ✅ SDK provides session abstraction (but API still stateless)
- **Field Name**: `session_id` (SDK-level)
- **How it works**:
  - SDK manages conversation history client-side (in memory/cache)
  - When you pass `session_id`, SDK retrieves and prepends history
  - SDK still sends full history to API (API is stateless)
  - More convenient API, but no token savings
- **Notes**: 
  - This is a convenience wrapper - underlying API is still stateless
  - SDK stores history client-side (lost if SDK instance dies)
  - Could be useful as optional convenience feature
  - Our database-backed approach is more robust for production

---

### 3. Google Gemini

#### Chat/GenerateContent API
- **Status**: ⚠️ RESEARCH NEEDED - Unclear
- **Possible Field Names**: 
  - `conversation_id` (unverified)
  - `session_id` (unverified)
- **API Documentation**: https://ai.google.dev/docs
- **Notes**: 
  - Documentation mentions "stateful mode" but unclear on API parameters
  - Some sources suggest conversation management but details unclear
  - Conversational Analytics API may have different capabilities
  - **REQUIRES ACTUAL API TESTING**

#### Possible Stateful Mode
- **Status**: ⚠️ Research Needed
- **Field Name**: Unknown (may be `conversation_id` or similar)
- **Notes**: Need to test API to confirm if conversation state is supported

---

### 4. OpenRouter

#### Chat Completions API (Current Implementation)
- **Status**: ✅ Stateless (confirmed)
- **Conversation Strategy**: `stateless`
- **Field Name**: N/A (stateless)
- **API Endpoint**: `POST /api/v1/chat/completions`
- **Documentation**: https://openrouter.ai/docs
- **Notes**: 
  - Explicitly documented as stateless
  - Does NOT support `conversationId` parameter (tested - causes errors)
  - Must send full message history
  - Uses OpenAI-compatible API format

---

### 5. DeepSeek

#### API Documentation
- **Status**: ⚠️ RESEARCH NEEDED
- **Field Names**: Unknown
- **API Documentation**: Need to locate official docs
- **Notes**: 
  - No official documentation found in search
  - Defaulting to stateless until verified
  - **REQUIRES API TESTING**

---

### 6. Grok (xAI)

#### API Documentation
- **Status**: ⚠️ RESEARCH NEEDED
- **Field Names**: Unknown
- **API Documentation**: Limited public documentation
- **Notes**: 
  - Limited public information available
  - Defaulting to stateless until verified
  - **REQUIRES API TESTING**

---

## Current Configuration Status

Based on research:

| Provider | Strategy | Field Name | Confirmed | Notes |
|----------|----------|------------|-----------|-------|
| OpenAI Chat | `stateless` | N/A | ✅ Yes | Standard Chat Completions API |
| OpenAI Assistants | `assistant_thread` | `thread_id` | ✅ Yes | Separate API, not implemented |
| Anthropic Claude | `stateless` | N/A | ✅ Yes | Messages API confirmed stateless |
| Google Gemini | `stateless` | Unknown | ⚠️ No | Needs API testing |
| OpenRouter | `stateless` | N/A | ✅ Yes | Confirmed stateless |
| DeepSeek | `stateless` | Unknown | ⚠️ No | No docs found |
| Grok | `stateless` | Unknown | ⚠️ No | Limited docs |

---

## Implementation Notes

### Key Findings:

1. **OpenAI**: Two different APIs
   - Chat Completions: Stateless (current implementation)
   - Assistants API: Uses `thread_id` (not implemented, different API)

2. **Anthropic Claude**: Confirmed stateless
   - SDK has `session_id` but API does not
   - Must send full history

3. **Google Gemini**: Unclear
   - May support stateful mode but documentation unclear
   - Needs actual API testing

4. **OpenRouter**: Confirmed stateless
   - Does not support conversationId parameter

5. **DeepSeek & Grok**: Unknown
   - Defaulting to stateless until verified

---

## Testing Requirements

### Google Gemini Testing Needed:
```python
# Test 1: Check if conversation_id parameter is accepted
response = gemini_client.generate_content(
    model="gemini-pro",
    contents=[{"role": "user", "parts": [{"text": "Hello"}]}],
    # Try with: conversation_id="test-id"
)

# Test 2: Check response for conversation identifiers
# Look in response.metadata, response.conversation, etc.
```

### DeepSeek Testing Needed:
- Locate official API documentation
- Test API endpoints for conversation management
- Check response structure for identifiers

### Grok Testing Needed:
- Review xAI API documentation (if available)
- Test API for conversation management features
- Check response for identifiers

---

## Configuration Mapping

For the `configure_conversation_management.py` command:

```python
'openai': {
    'conversation_strategy': 'stateless',
    'conversation_id_field': None,
    'returns_conversation_id': False,
    # Note: Assistants API uses thread_id but is separate API
},
'openai-assistants': {  # Separate platform for Assistants API
    'conversation_strategy': 'assistant_thread',
    'conversation_id_field': 'thread_id',
    'returns_conversation_id': True,
    'conversation_id_path': 'thread.id',
},
'anthropic': {
    'conversation_strategy': 'stateless',
    'conversation_id_field': None,
    'returns_conversation_id': False,
},
'google': {
    'conversation_strategy': 'stateless',  # Until verified
    'conversation_id_field': None,  # Unknown - needs testing
    'returns_conversation_id': False,  # Unknown - needs testing
},
'openrouter': {
    'conversation_strategy': 'stateless',
    'conversation_id_field': None,
    'returns_conversation_id': False,
},
```

---

## Next Steps

1. **Immediate**: Update configuration to reflect confirmed findings
2. **Short-term**: Test Google Gemini API for conversation state support
3. **Long-term**: 
   - Implement OpenAI Assistants API support
   - Locate and test DeepSeek API
   - Locate and test Grok API
   - Create automated tests for conversation management

---

## References

- OpenAI Chat Completions: https://platform.openai.com/docs/api-reference/chat
- OpenAI Assistants: https://platform.openai.com/docs/api-reference/assistants
- Anthropic Messages API: https://docs.anthropic.com/en/api/messages
- Google Gemini: https://ai.google.dev/docs
- OpenRouter: https://openrouter.ai/docs
