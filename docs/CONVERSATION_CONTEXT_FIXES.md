# Conversation Context Fixes & Improvements

## Issues Identified

1. **Model Name Not Recognized**: OpenRouter model names like `mistralai/mistral-7b-instruct:free` weren't being recognized by `TokenBudgetManager`, causing it to default to 4096 tokens instead of 8192.

2. **Model Name Not Passed**: The `model_name` wasn't being passed in the agent context metadata, so `ConversationManager` couldn't calculate the correct token limit.

3. **Insufficient Logging**: Limited logging made it difficult to diagnose why conversation history wasn't being included in API requests.

## Fixes Applied

### 1. Improved Model Name Detection (`token_budget_manager.py`)

- **Enhanced `get_model_token_limit()`** to handle OpenRouter model name format:
  - Removes provider prefix (e.g., `mistralai/`)
  - Removes tag suffix (e.g., `:free`)
  - Added support for Mistral and Llama models
  - Increased default limit from 4096 to 8192 tokens

**Example:**
- Input: `mistralai/mistral-7b-instruct:free`
- Normalized: `mistral-7b-instruct`
- Matched to: `mistral-7b-instruct` → 8192 tokens

### 2. Pass Model Name in Context (`consumers.py`)

- Added `model_name` to agent context metadata so `ConversationManager` can use it for token limit calculation.

**Change:**
```python
metadata={
    'conversation_id': str(conversation.id),
    'conversation_context': conversation_context,
    'platform_config': platform_config,
    'model_name': agent_model.model_name,  # ← Added
    'total_message_count': len(history)
}
```

### 3. Enhanced Logging (`conversation_manager.py`)

- Added detailed logging for:
  - Token budget calculation (with all parameters)
  - Message processing (count, estimates)
  - Token estimates for debugging
  - Warnings when history is skipped due to budget

**New Log Output:**
```
[ConversationManager] Token budget calculated: {...} (total_limit=8192, has_summary=False, has_code=True)
[ConversationManager] Processing 3 recent messages from history (total history: 6, max_recent: 20)
[ConversationManager] Estimated tokens for 3 messages: 150 (budget: 3686)
[ConversationManager] Including 3/3 recent messages (budget: 3686 tokens, estimated: 150 tokens)
```

## Testing Steps

### Step 1: Verify Model Name Detection

Run this in Django shell:
```python
from apps.chat.services.token_budget_manager import TokenBudgetManager

# Test various model name formats
models = [
    'mistralai/mistral-7b-instruct:free',
    'mistral-7b-instruct',
    'gpt-3.5-turbo',
    'unknown-model'
]

for model in models:
    limit = TokenBudgetManager.get_model_token_limit(model)
    print(f"{model:40} → {limit} tokens")
```

**Expected Output:**
```
mistralai/mistral-7b-instruct:free        → 8192 tokens
mistral-7b-instruct                        → 8192 tokens
gpt-3.5-turbo                              → 16385 tokens
unknown-model                               → 8192 tokens (default)
```

### Step 2: Test Conversation History Inclusion

1. Start a conversation with at least 3 message pairs (6 total messages)
2. Send a new message
3. Check server logs for:

```
[ConversationManager] Token budget calculated: {...}
[ConversationManager] Processing X recent messages from history
[ConversationManager] Including X/Y recent messages (budget: Z tokens)
[ConversationManager] Stateless enriched context: X messages total
```

4. Verify API request includes history:
   - Look for: `Starting OpenRouter streaming request: model=..., messages=X`
   - `X` should be **more than 2** (system + current message)

### Step 3: Check Token Budget Allocation

With a conversation that has:
- No summary
- 1 code block
- 6 messages (3 pairs)

Expected budget allocation (for 8192 token limit):
- System prompt: ~20% = ~1638 tokens
- Code blocks: ~35% = ~2867 tokens
- Recent messages: ~45% = ~3686 tokens

Check logs for:
```
[ConversationManager] Token budget calculated: {
  'system_prompt': 1638,
  'code_blocks': 2867,
  'recent_messages': 3686
}
```

### Step 4: Verify Code Context Inclusion

1. Send a message with a code block
2. Send another message: "Can you explain this code?"
3. Check logs for:
   ```
   [ConversationManager] Including X/Y code blocks
   [ConversationalAgent] Message 1/X: role=system, content_preview=Code blocks referenced...
   ```

## Common Issues & Solutions

### Issue: Still seeing `messages=2` in API request

**Possible Causes:**
1. Token budget too restrictive (check logs for `recent_messages budget is 0`)
2. All messages exceed budget (check token estimates in logs)
3. Agent doesn't have `CONVERSATION` capability

**Solutions:**
1. Check token budget logs - if `recent_messages` is 0, the allocation might be wrong
2. Verify agent capabilities:
   ```python
   python manage.py shell
   from apps.agents.models import Agent
   agent = Agent.objects.get(name="Mistral 7B Assistant")
   print(agent.capabilities)  # Should include 'CONVERSATION'
   ```
3. If missing, run: `python manage.py fix_agent_capabilities --agent-id <id>`

### Issue: Rate Limit Errors (429)

**Symptom:**
```
OpenRouter API error: Error code: 429 - {'error': {'message': 'Provider returned error', ...}}
```

**Solutions:**
1. **Wait**: Free tier has strict rate limits - wait 1-2 minutes
2. **Switch Model**: Use a different agent/model
3. **Add API Key**: Add your own OpenRouter API key:
   - Go to: `/admin/integrations/aiplatform/`
   - Edit "OpenRouter" platform
   - Add your API key in "API Key" field
   - Get key from: https://openrouter.ai/settings/keys

### Issue: Model Name Not Recognized

**Check:**
```python
from apps.chat.services.token_budget_manager import TokenBudgetManager
limit = TokenBudgetManager.get_model_token_limit('mistralai/mistral-7b-instruct:free')
print(f"Limit: {limit}")  # Should be 8192, not 4096
```

If it returns 4096, the model name normalization might need adjustment.

## Next Steps

1. **Test the fixes**: Follow the testing steps above
2. **Monitor logs**: Watch for the new detailed logging output
3. **Verify API requests**: Confirm that conversation history is included
4. **Adjust if needed**: If token budget is still too restrictive, you can adjust percentages in `TokenBudgetManager.DEFAULT_ALLOCATION`

## Files Modified

1. `backend/apps/chat/services/token_budget_manager.py`
   - Enhanced `get_model_token_limit()` for OpenRouter model names
   - Increased default limit to 8192

2. `backend/apps/chat/consumers.py`
   - Added `model_name` to agent context metadata

3. `backend/apps/integrations/services/conversation_manager.py`
   - Enhanced logging for debugging token budget and message selection

## Related Documentation

- `TESTING_CONVERSATION_CONTEXT.md` - Comprehensive testing guide
- `IMPLEMENTATION_PLAN_CURSOR_STYLE_CONTEXT.md` - Implementation details

