# Research Gaps - AI Provider Conversation Management

## Overview

This document identifies gaps between our implementation and confirmed provider capabilities. Some providers' conversation management features are unclear from public documentation and require verification through API testing.

## Confirmed Capabilities ✅

### OpenAI Chat Completions API
- **Status**: ✅ Confirmed
- **Strategy**: Stateless
- **Notes**: Must send full message history. Assistants API (v2) supports thread_id but requires separate implementation.

### OpenRouter
- **Status**: ✅ Confirmed  
- **Strategy**: Stateless
- **Notes**: Explicitly documented as stateless. Does not support conversationId parameter.

## Research Gaps ⚠️

### Anthropic Claude Messages API
- **Current Configuration**: Stateless
- **Research Gap**: Some sources suggest Claude may support conversation_id for threading, but official documentation is unclear.
- **Action Needed**: 
  1. Test Claude Messages API with conversation_id parameter
  2. Check if responses return conversation identifiers
  3. Verify if context is maintained server-side

**Testing Steps**:
```python
# Test 1: Send initial message
response1 = claude_client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "Hello"}]
)
# Check response for conversation_id or similar field

# Test 2: Send follow-up with conversation_id (if supported)
response2 = claude_client.messages.create(
    model="claude-3-sonnet-20240229",
    conversation_id=response1.conversation_id,  # If exists
    messages=[{"role": "user", "content": "What did I just say?"}]
)
# Verify if context is maintained
```

### Google Gemini API
- **Current Configuration**: Stateless (updated from conversation_id)
- **Research Gap**: 
  - Official Gemini API documentation unclear on conversation state support
  - Some sources mention `startConversation()` but this may be SDK-specific
  - Need to verify API-level conversation management

**Testing Steps**:
```python
# Test 1: Check if Gemini API supports conversation state
# Look for conversation_id in request/response
# Test with official Google AI SDK and raw API calls

# Test 2: Verify if Gemini maintains context between requests
# without sending full history
```

### DeepSeek
- **Current Configuration**: Stateless (default)
- **Research Gap**: No documentation found on conversation management
- **Action Needed**: 
  1. Review DeepSeek API documentation
  2. Test API for conversation_id/session_id support
  3. Check response headers/metadata for conversation identifiers

### Grok (xAI)
- **Current Configuration**: Stateless (default)
- **Research Gap**: Limited public documentation available
- **Action Needed**:
  1. Review xAI API documentation
  2. Test for conversation/session management features
  3. Check if Grok maintains context server-side

## Implementation Gaps 🔧

### OpenAI Assistants API Support
- **Status**: Not Implemented
- **Current**: Only Chat Completions API supported
- **Gap**: Assistants API (v2) supports thread-based conversations with persistent context
- **Action Needed**:
  1. Implement Assistants API adapter (separate from Chat Completions)
  2. Add thread creation and management
  3. Support thread_id in conversation context
  4. Configure platform with `assistant_thread` strategy

**Implementation Plan**:
```python
# New platform: 'openai-assistants'
# Strategy: 'assistant_thread'
# conversation_id_field: 'thread_id'
# Requires: assistant_id + thread_id
```

## Verification Checklist

For each provider, verify:

- [ ] **API Documentation Review**
  - [ ] Read official API documentation
  - [ ] Check for conversation/thread/session parameters
  - [ ] Review response structure for identifiers

- [ ] **API Testing**
  - [ ] Send initial message and check response for IDs
  - [ ] Send follow-up message with ID (if supported)
  - [ ] Verify context is maintained without sending history
  - [ ] Test error handling for invalid IDs

- [ ] **Adapter Implementation**
  - [ ] Update adapter to extract conversation IDs
  - [ ] Implement ID passing in requests
  - [ ] Handle provider-specific ID field names

- [ ] **Configuration Update**
  - [ ] Update `configure_conversation_management.py`
  - [ ] Set correct `conversation_strategy`
  - [ ] Configure `conversation_id_field` and `conversation_id_path`
  - [ ] Set `returns_conversation_id = True` if confirmed

## Recommended Next Steps

1. **Immediate** (High Priority):
   - ✅ Fix OpenRouter configuration (already done - stateless confirmed)
   - Test Anthropic Claude Messages API for conversation_id support
   - Test Google Gemini API for conversation state support

2. **Short Term**:
   - Review DeepSeek and Grok official documentation
   - Create test scripts for each provider
   - Document findings in this file

3. **Long Term**:
   - Implement OpenAI Assistants API support
   - Create automated tests for conversation management
   - Build provider capability detection system

## Testing Script Template

```python
"""
Template for testing provider conversation management capabilities.
"""

async def test_provider_conversation_management(adapter, platform_config):
    """Test if provider supports conversation state management."""
    
    # Test 1: Initial message
    request1 = CompletionRequest(
        prompt="My name is Alice. Remember this.",
        messages=[{"role": "user", "content": "My name is Alice. Remember this."}]
    )
    response1 = await adapter.generate_completion(request1)
    
    # Extract conversation ID if present
    conversation_id = adapter.extract_conversation_id(response1.raw_response, response1.metadata)
    
    if conversation_id:
        print(f"✓ Provider supports conversation IDs: {conversation_id}")
        
        # Test 2: Follow-up with ID
        request2 = CompletionRequest(
            prompt="What is my name?",
            conversation_id=conversation_id,
            messages=[{"role": "user", "content": "What is my name?"}]  # Only new message
        )
        response2 = await adapter.generate_completion(request2)
        
        if "Alice" in response2.content:
            print("✓ Provider maintains context via conversation ID")
            return True, conversation_id
        else:
            print("✗ Provider does not maintain context despite ID")
            return False, None
    else:
        print("✗ Provider does not return conversation IDs (stateless)")
        return False, None
```

## Notes

- Always verify with official API documentation first
- API capabilities may change - keep documentation updated
- Some providers may have undocumented features - test empirically
- Error handling is critical - providers may reject unknown parameters
