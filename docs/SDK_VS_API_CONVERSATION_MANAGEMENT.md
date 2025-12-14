# SDK-Level vs API-Level Conversation Management

## Important Distinction

Even when an API is **stateless**, the SDK might provide **session management** features. This is a crucial nuance!

## Two Levels of State Management

### 1. API-Level (Server-Side State)
**The HTTP API itself maintains conversation state on the server**

**Example:** OpenAI Assistants API
```python
# Server remembers conversation
thread_id = "thread_abc123"
response = client.threads.messages.create(
    thread_id=thread_id,
    content="New message"  # Server has context from thread_id
)
# ✅ Only sends new message - server maintains full history
```

**Benefits:**
- ✅ True server-side state
- ✅ Minimal token usage (only new message)
- ✅ Server handles context management

---

### 2. SDK-Level (Client-Side Wrapper)
**The SDK provides a wrapper that manages state client-side, but API is still stateless**

**Example:** Anthropic Claude SDK with session_id
```python
# SDK manages session internally
session_id = "session_abc123"
response = claude_client.messages.create(
    messages=[{"role": "user", "content": "New message"}],
    session_id=session_id  # SDK uses this internally
)
# ⚠️ SDK still sends full history to API (API is stateless)
# But SDK provides convenient session abstraction
```

**How it works:**
1. SDK stores conversation history client-side (in memory or cache)
2. When you send a new message with `session_id`, SDK retrieves history
3. SDK automatically prepends full history before sending to API
4. API receives full history (still stateless)
5. SDK returns response

**Benefits:**
- ✅ Convenient session abstraction
- ✅ SDK handles history management
- ⚠️ Still sends full history to API (no token savings)
- ⚠️ Client-side state (lost if SDK instance dies)

---

## Current Implementation Status

### What We're Using:

**OpenAI Adapter:**
- Using: `openai.AsyncOpenAI` SDK
- SDK features: Can use conversation management wrappers
- API: Stateless (Chat Completions)
- Current: We manually manage history (send full history)
- **Opportunity**: Could leverage SDK conversation helpers if available

**OpenRouter Adapter:**
- Using: `openai.AsyncOpenAI` SDK (OpenRouter-compatible)
- SDK features: Same as OpenAI SDK
- API: Stateless
- Current: We manually manage history
- **Opportunity**: Same as OpenAI

**Anthropic Claude Adapter:**
- Need to check: What SDK are we using?
- SDK features: Claude SDK has `session_id` support
- API: Stateless
- **Opportunity**: Could use Claude SDK session management

---

## Should We Use SDK-Level Session Management?

### Pros:
1. ✅ **Convenience**: SDK handles history retrieval/prepending
2. ✅ **Less code**: Don't need to manually manage sliding windows
3. ✅ **Abstraction**: Cleaner API (just pass session_id)

### Cons:
1. ⚠️ **Still stateless**: No token savings (SDK sends full history internally)
2. ⚠️ **Client-side state**: State lost if SDK instance/process dies
3. ⚠️ **Less control**: Can't customize history management (e.g., sliding window size)
4. ⚠️ **Dependency**: Tied to SDK implementation

### Our Current Approach:
- ✅ **More control**: We manage history ourselves
- ✅ **Persistent state**: History stored in database, survives restarts
- ✅ **Customizable**: Can adjust sliding window size per conversation
- ✅ **Provider-agnostic**: Works same way for all providers

---

## Recommendation

**Keep our current approach (manual history management)** because:

1. **Database persistence**: Our conversations are stored in DB, not SDK memory
2. **Cross-provider consistency**: Same approach works for all providers
3. **Customization**: We can optimize sliding window per conversation
4. **Control**: We control exactly what gets sent

**BUT** we could add SDK-level session support as an **optional feature**:
- For providers with SDK session management
- As a convenience layer on top of our database storage
- Users could opt-in to use SDK sessions instead of our sliding window

---

## Example: How SDK Session Would Work

```python
# Current approach (what we do now):
history = get_conversation_history_from_db()  # Our DB
messages = history[-20:] + [new_message]  # Sliding window
response = client.chat.completions.create(messages=messages)
# ✅ Full control, persistent in DB

# Alternative SDK approach (could add as option):
session = client.sessions.create(session_id=conversation_id)
response = session.chat(new_message)  # SDK manages history
# ⚠️ Less control, state in SDK memory/cache
```

---

## Answer to Your Question

**Q: "Some stateless APIs have SDK-level solutions, right?"**

**A: YES, but it's important to understand:**

1. **SDK session management** = Client-side convenience wrapper
   - SDK manages history in memory/cache
   - Still sends full history to API
   - **No token savings** (API is still stateless)
   - More convenient API, but less control

2. **API session management** = True server-side state
   - Server maintains conversation state
   - Only send new messages
   - **Huge token savings** (95%+ reduction)
   - True stateful conversations

3. **Our approach** = Best of both worlds
   - Database persistence (better than SDK memory)
   - Full control over history management
   - Can optimize per conversation
   - Works consistently across all providers

**We could leverage SDK sessions as an optional convenience feature, but our current database-backed approach is more robust for production use.**
