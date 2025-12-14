# Step-by-Step Testing Guide: Conversation Context & Code Extraction

This guide helps you verify that conversation history, code context extraction, and summarization are working correctly.

## Prerequisites

1. **Django server running**: `python manage.py runserver`
2. **Celery worker running** (for summarization): `celery -A core worker -l info`
3. **Django Admin access**: http://localhost:8000/admin/
4. **Frontend chat interface**: http://localhost:3000 (or your frontend URL)

## Test 1: Basic Conversation History

### Steps:
1. Open your chat interface
2. Start a new conversation with an agent (e.g., "Mistral 7B Assistant")
3. Send message 1: `"Hello, can you help me with Python?"`
4. Wait for AI response
5. Send message 2: `"What is a list comprehension?"`
6. Wait for AI response
7. Send message 3: `"Can you give me an example?"`

### Expected Results:
- ✅ All 3 messages should be saved in the database
- ✅ AI should reference previous messages in its responses
- ✅ In Django Admin → Conversations → [Your Conversation] → Messages tab, you should see 6 messages (3 user + 3 assistant)

### Check Logs:
Look for these log entries:
```
[ChatConsumer] Context: conversation_history=3 messages
[ConversationalAgent] prepare_prompt: history_count=3
[ConversationManager] get_optimal_messages_to_send: history_count=3
[ConversationManager] Stateless enriched context: X messages total
```

### Verify in Django Admin:
1. Go to: `/admin/chat/conversation/`
2. Click on your conversation
3. Check "Total Messages" field
4. Scroll to "Messages" section at bottom - should show all 6 messages

---

## Test 2: Code Block Extraction

### Steps:
1. Continue the conversation from Test 1 (or start new)
2. Send a message with a code block:
   ```
   Here's my Django model:
   
   ```python
   class User(models.Model):
       email = models.EmailField(unique=True)
       username = models.CharField(max_length=150)
       created_at = models.DateTimeField(auto_now_add=True)
   ```
   ```
3. Wait for AI response

### Expected Results:
- ✅ Code block should be extracted and stored
- ✅ Language should be detected as "python"
- ✅ AI should understand the code context

### Check Logs:
Look for:
```
[ChatConsumer] Code extraction result: 1 blocks, 0 files from message
[ChatConsumer] Extracted code context: 1 blocks, 0 files
```

### Verify in Django Admin:
1. Go to: `/admin/chat/conversation/` → [Your Conversation]
2. Scroll to "Code Context Tracking" section
3. Check:
   - **Referenced code blocks**: Should show 1 block with `"language": "python"`
   - **Code context metadata**: Should show `"total_blocks": 1, "total_code_tokens": X`

---

## Test 3: Unformatted Code Detection

### Steps:
1. Send a message with unformatted code (no markdown backticks):
   ```
   Here's my Django model: python class User(models.Model): email = models.EmailField(unique=True) username = models.CharField(max_length=150)
   ```
2. Wait for AI response

### Expected Results:
- ✅ Code should still be extracted (fallback detection)
- ✅ Language should be detected as "python"
- ✅ Warning log if backticks found but extraction failed

### Check Logs:
Look for:
```
[ChatConsumer] Code extraction result: 1 blocks, 0 files from message
```
(May also see warning if backticks present but extraction failed)

### Verify in Django Admin:
- **Referenced code blocks**: Should show block with `"type": "unformatted_code"`

---

## Test 4: File Reference Extraction

### Steps:
1. Send a message mentioning file paths:
   ```
   I'm working on src/components/UserProfile.ts and backend/apps/users/models.py
   ```
2. Wait for AI response

### Expected Results:
- ✅ File paths should be extracted
- ✅ Files should be stored in `referenced_files` field

### Check Logs:
Look for:
```
[ChatConsumer] Code extraction result: 0 blocks, 2 files from message
```

### Verify in Django Admin:
- **Referenced files**: Should show `["src/components/UserProfile.ts", "backend/apps/users/models.py"]`
- **Code context metadata**: Should show `"unique_files_count": 2`

---

## Test 5: Conversation History in API Request

### Steps:
1. Continue conversation with at least 3 message pairs (6 total messages)
2. Send a new message
3. Check server logs for the API request

### Expected Results:
- ✅ API request should include conversation history
- ✅ For stateless providers (OpenRouter), should see multiple messages in request

### Check Logs:
Look for detailed ConversationManager logs:
```
[ConversationManager] Building enriched context: history_count=6, code_blocks=X, has_summary=no
[ConversationManager] Token budget calculated: {...}
[ConversationManager] Including X/Y recent messages (budget: Y tokens)
[ConversationManager] Stateless enriched context: X messages total
```

### Verify API Request:
In logs, find the OpenRouter request:
```
Starting OpenRouter streaming request: model=..., messages=X
```
- `messages=X` should be **more than 2** if history exists
- Should include system message (if summary/code blocks exist)
- Should include recent conversation history
- Should include current message

---

## Test 6: Code Context in API Request

### Steps:
1. Send a message with code block (from Test 2)
2. Send another message that references that code: `"Can you explain this model?"`
3. Check logs

### Expected Results:
- ✅ Code block should be included in API request as system message
- ✅ AI should have context about the code

### Check Logs:
Look for:
```
[ConversationManager] Including X/Y code blocks
[ConversationalAgent] Message 1/X: role=system, content_length=Y, content_preview=Code blocks referenced...
```

### Verify:
- System message should contain code blocks
- AI response should reference the code you sent

---

## Test 7: Conversation Summarization Trigger

### Steps:
1. Create a long conversation (30+ messages)
   - Or manually set `summarize_at_message_count = 5` in Django Admin for testing
2. Send messages until threshold is reached
3. Check Celery logs

### Expected Results:
- ✅ Summarization task should be triggered
- ✅ Summary should be generated and stored
- ✅ Future messages should use summary instead of full history

### Check Logs:
Look for:
```
[ChatConsumer] Triggered async summarization for conversation ...
[summarize_conversation_task] Starting summarization for conversation ...
[ConversationSummarizer] Generated summary: ...
```

### Verify in Django Admin:
- **Conversation summary**: Should contain AI-generated summary
- **Summary metadata**: Should show:
  ```json
  {
    "last_summarized_at": "2025-12-14T...",
    "messages_summarized_count": 30,
    "summary_version": 1,
    "summary_tokens": 150
  }
  ```

---

## Test 8: Summary in API Request

### Steps:
1. Continue conversation after summarization (from Test 7)
2. Send a new message
3. Check logs

### Expected Results:
- ✅ Summary should be included in API request as system message
- ✅ Recent messages should still be included
- ✅ Older messages should be replaced by summary

### Check Logs:
Look for:
```
[ConversationManager] Building enriched context: has_summary=yes
[ConversationManager] Including conversation summary
[ConversationManager] Token budget calculated: {..., "summary": 200, ...}
```

### Verify:
- System message should start with "Previous conversation summary:"
- AI should maintain context from summarized conversation

---

## Test 9: Token Budget Management

### Steps:
1. Create conversation with:
   - Summary (if available)
   - Multiple code blocks
   - Long conversation history
2. Send a new message
3. Check token budget logs

### Expected Results:
- ✅ Token budget should be calculated correctly
- ✅ Messages should fit within model's token limit
- ✅ Priority: Summary > Code blocks > Recent messages

### Check Logs:
Look for:
```
[ConversationManager] Token budget calculated: {
  "system": 200,
  "summary": 200,
  "code_blocks": 1000,
  "recent_messages": 2000,
  "total": 8192
}
[ConversationManager] Including X/Y recent messages (budget: 2000 tokens)
```

### Verify:
- Total should not exceed model's token limit
- Budget allocation should be reasonable

---

## Test 10: Rate Limit Handling

### Steps:
1. If you see `RateLimitError: 429` in logs:
   - Wait 1-2 minutes
   - Try again
   - Or switch to a different model/agent

### Expected Results:
- ✅ Error should be logged clearly
- ✅ User should see error message in chat
- ✅ System should handle gracefully

### Check Logs:
Look for:
```
OpenRouter API error: Error code: 429 - {'error': {'message': 'Provider returned error', ...}}
```

### Solutions:
1. **Wait**: Free tier has rate limits - wait a few minutes
2. **Switch Model**: Use a different agent/model
3. **Add API Key**: Add your own OpenRouter API key for higher limits

---

## Troubleshooting

### Issue: Conversation history not included in API request

**Symptoms:**
- Logs show `conversation_history=3 messages` but `messages=2` in API request
- AI doesn't remember previous messages

**Check:**
1. Verify agent has `CONVERSATION` capability:
   ```python
   python manage.py shell
   from apps.agents.models import Agent
   agent = Agent.objects.get(name="Mistral 7B Assistant")
   print(agent.capabilities)  # Should include 'CONVERSATION'
   ```

2. If missing, run:
   ```python
   python manage.py fix_agent_capabilities --agent-id <agent_id>
   ```

3. Check ConversationManager logs for token budget issues:
   - If `recent_messages budget is 0`, token budget may be too restrictive
   - Check `TokenBudgetManager.calculate_token_budget()` output

### Issue: Code blocks not extracted

**Symptoms:**
- `referenced_code_blocks` is empty in Django Admin
- Logs show `Code extraction result: 0 blocks`

**Check:**
1. Verify code has proper markdown formatting: ` ```python ... ``` `
2. Check logs for warnings about malformed code
3. Unformatted code detection should still work (fallback)

### Issue: Rate Limit Errors

**Symptoms:**
- `RateLimitError: 429` in logs
- AI returns "I'm sorry, I didn't receive a proper response"

**Solutions:**
1. Wait 1-2 minutes and retry
2. Switch to a different model/agent
3. Add your own OpenRouter API key in Django Admin:
   - Go to: `/admin/integrations/aiplatform/`
   - Edit "OpenRouter" platform
   - Add your API key in "API Key" field

### Issue: Summarization not triggered

**Symptoms:**
- Conversation has 30+ messages but no summary

**Check:**
1. Verify Celery worker is running: `celery -A core worker -l info`
2. Check Celery logs for errors
3. Manually trigger summarization:
   ```python
   python manage.py shell
   from apps.chat.models import Conversation
   from apps.chat.tasks import summarize_conversation_task
   conv = Conversation.objects.get(id='...')
   summarize_conversation_task.delay(str(conv.id))
   ```

---

## Quick Verification Commands

### Check conversation history:
```python
python manage.py shell
from apps.chat.models import Conversation
conv = Conversation.objects.order_by('-created_at').first()
print(f"Messages: {conv.messages.count()}")
print(f"Summary: {bool(conv.conversation_summary)}")
print(f"Code blocks: {len(conv.referenced_code_blocks or [])}")
print(f"Files: {len(conv.referenced_files or [])}")
```

### Check agent capabilities:
```python
python manage.py shell
from apps.agents.models import Agent
agent = Agent.objects.get(name="Mistral 7B Assistant")
print(f"Capabilities: {agent.capabilities}")
print(f"Platform: {agent.preferred_platform}")
```

### Check code extraction:
```python
python manage.py shell
from apps.chat.models import Message
from apps.chat.services.code_context_extractor import CodeContextExtractor
msg = Message.objects.order_by('-created_at').first()
blocks = CodeContextExtractor.extract_code_blocks(msg.content)
files = CodeContextExtractor.extract_file_references(msg.content)
print(f"Blocks: {len(blocks)}, Files: {len(files)}")
```

---

## Success Criteria

✅ **All tests pass if:**
1. Conversation history is included in API requests (for stateless providers)
2. Code blocks are extracted and stored correctly
3. File references are captured
4. Summarization triggers at threshold
5. Summary is included in future API requests
6. Token budget is managed correctly
7. AI responses show awareness of conversation context

---

## Next Steps

After verifying all tests:
1. Monitor production logs for any issues
2. Adjust token budget percentages if needed (in `TokenBudgetManager`)
3. Tune summarization thresholds (in `Conversation` model)
4. Consider adding more sophisticated code context prioritization

