# Conversation Management: Stateful vs Stateless Providers

## Important Clarification

**NOT all providers support conversation/thread/session IDs.** There are two fundamentally different approaches:

### 1. Stateless Providers (No Conversation ID Support)
These providers **do not maintain conversation state** on their servers. They require you to send the full conversation history with each request.

**Examples:**
- ✅ **OpenAI Chat Completions API** - Stateless (confirmed)
- ✅ **Anthropic Claude Messages API** - Stateless (confirmed)
- ✅ **OpenRouter** - Stateless (confirmed, tested)

**How it works:**
- No conversation ID exists
- Must send full message history each time
- Provider doesn't "remember" previous messages
- We use a sliding window approach (send last 20 messages)

### 2. Stateful Providers (Conversation ID Support)
These providers **maintain conversation state** on their servers. You can send just the new message and reference the conversation by ID.

**Examples:**
- ✅ **OpenAI Assistants API** - Uses `thread_id` (different API from Chat Completions)
- ⚠️ **Google Gemini** - May support conversation state (needs testing)
- ⚠️ **DeepSeek** - Unknown (needs research)
- ⚠️ **Grok** - Unknown (needs research)

**How it works:**
- Provider assigns a conversation/thread ID
- Send only new messages with the ID
- Provider maintains full history server-side
- Much more token-efficient

---

## Key Insight: It's NOT Just Implementation Difference

The difference between stateless and stateful providers is **fundamental API design**, not just different field names:

### Stateless Provider Flow:
```
Request 1: Send ["Hello"]
Response 1: "Hi there!"

Request 2: Send ["Hello", "Hi there!", "What's 2+2?"]  ← Must send full history
Response 2: "4"
```

### Stateful Provider Flow:
```
Request 1: Send ["Hello"]
Response 1: "Hi there!" + conversation_id: "abc123"

Request 2: Send ["What's 2+2?"] + conversation_id: "abc123"  ← Only new message
Response 2: "4" (provider remembers "Hello" and "Hi there!" from ID)
```

---

## Current Provider Status

### Confirmed Stateless (No ID Support):
| Provider | API | Conversation ID? | Must Send History? |
|----------|-----|------------------|-------------------|
| OpenAI | Chat Completions | ❌ No | ✅ Yes |
| Anthropic | Messages API | ❌ No | ✅ Yes |
| OpenRouter | Chat Completions | ❌ No | ✅ Yes |

### May Support Conversation IDs (Needs Testing):
| Provider | API | Conversation ID? | Status |
|----------|-----|------------------|--------|
| Google Gemini | GenerateContent | ⚠️ Unknown | Needs API testing |
| DeepSeek | Chat API | ⚠️ Unknown | No docs found |
| Grok (xAI) | Chat API | ⚠️ Unknown | Limited docs |

### Confirmed Stateful (Has ID Support):
| Provider | API | Field Name | Notes |
|----------|-----|------------|-------|
| OpenAI | Assistants API | `thread_id` | Different API, not implemented yet |

---

## Implementation Strategy

Our system handles both approaches:

### For Stateless Providers:
```python
# System automatically sends sliding window of recent messages
messages = [
    {"role": "user", "content": "Message 1"},
    {"role": "assistant", "content": "Response 1"},
    {"role": "user", "content": "Message 2"},
    {"role": "assistant", "content": "Response 2"},
    {"role": "user", "content": "New message"},  # Current message
]
# Send all messages (last 20 in sliding window)
```

### For Stateful Providers:
```python
# System sends only new message if conversation ID exists
if conversation_id:
    messages = [
        {"role": "user", "content": "New message"}  # Only new message
    ]
    params = {
        "messages": messages,
        "conversation_id": conversation_id  # Provider maintains context
    }
else:
    # First message - send it, provider returns conversation_id
    messages = [{"role": "user", "content": "First message"}]
```

---

## Why This Matters

### Token Costs Example:

**Stateless Provider (20 message conversation):**
- Request: ~5,000 tokens (full history)
- Response: ~200 tokens
- Total: ~5,200 tokens per message

**Stateful Provider (same conversation):**
- Request: ~50 tokens (just new message + ID)
- Response: ~200 tokens
- Total: ~250 tokens per message

**Savings: ~95% fewer tokens with stateful provider!**

---

## Answer to Your Question

**Q: Do all providers have a solution to get thread/session/conversation ID, just implemented differently?**

**A: NO** - Not all providers support conversation IDs. The distinction is:

1. **Stateless providers** (most current ones):
   - ❌ No conversation ID support
   - ✅ Solution: Send full history (sliding window)
   - ✅ Our system handles this automatically

2. **Stateful providers** (some exist, need testing):
   - ✅ Support conversation/thread IDs
   - ✅ Solution: Use IDs to maintain context
   - ✅ Our system will automatically use IDs when available

3. **Different APIs from same provider**:
   - OpenAI Chat Completions: Stateless
   - OpenAI Assistants: Stateful (different API entirely)

---

## Conclusion

The difference is **fundamental API architecture**, not just implementation details:
- **Stateless = No server-side memory** → Must send history
- **Stateful = Server-side memory** → Can use IDs

Our unified system handles both approaches automatically, optimizing for each provider's capabilities.
