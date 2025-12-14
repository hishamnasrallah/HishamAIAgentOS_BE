# Testing Guide: Cursor-Style Context Management

## 🧪 Test Scenario: Verify Code Context Extraction & Summarization

This guide walks you through testing the conversation context management features to ensure everything is working correctly.

---

## Test 1: Code Block Extraction (Basic)

### Messages to Send:

**Message 1:**
```
I'm working on a Python project. Here's my user model:

```python
class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
```
```

**Message 2:**
```
Can you help me add password hashing to this model?
```

### ✅ What to Check:

1. **Check Logs** (should see):
   ```
   [ChatConsumer] Extracted code context: 1 blocks, 0 files
   ```

2. **Check Django Admin**:
   - Go to: `/admin/chat/conversation/`
   - Open the conversation
   - Check "Code Context Tracking" section
   - Should see:
     - `referenced_code_blocks`: Contains the Python code block
     - `code_context_metadata`: Shows token counts, block count

3. **Check Database**:
   ```python
   # In Django shell: python manage.py shell
   from apps.chat.models import Conversation
   conv = Conversation.objects.last()
   print(conv.referenced_code_blocks)  # Should show the code block
   print(conv.code_context_metadata)   # Should show metadata
   ```

---

## Test 2: File Reference Detection

### Messages to Send:

**Message 1:**
```
I'm working on the authentication system. The files involved are:
- backend/apps/authentication/models.py
- frontend/src/components/Login.tsx
- backend/apps/authentication/views.py
```

**Message 2:**
```
Can you review the Login component in frontend/src/components/Login.tsx?
```

### ✅ What to Check:

1. **Check Logs**:
   ```
   [ChatConsumer] Extracted code context: 0 blocks, 3 files
   ```

2. **Check Admin Panel**:
   - `referenced_files`: Should contain:
     ```json
     [
       "backend/apps/authentication/models.py",
       "frontend/src/components/Login.tsx",
       "backend/apps/authentication/views.py"
     ]
     ```

3. **Check AI Response**:
   - The AI should acknowledge the file paths
   - Context about these files should be included in future messages

---

## Test 3: Mixed Code Blocks & File References

### Messages to Send:

**Message 1:**
```
Here's my authentication view in backend/apps/authentication/views.py:

```python
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=401)
```

And here's the frontend component in frontend/src/components/Login.tsx:
```typescript
import React, { useState } from 'react';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        // Login logic here
    };
    
    return <form onSubmit={handleSubmit}>...</form>;
};
```
```

**Message 2:**
```
How can I connect these two pieces together?
```

### ✅ What to Check:

1. **Check Logs**:
   ```
   [ChatConsumer] Extracted code context: 2 blocks, 2 files
   ```

2. **Check Admin Panel**:
   - `referenced_code_blocks`: Should have 2 entries (Python + TypeScript)
   - `referenced_files`: Should have both file paths
   - `code_context_metadata.total_blocks`: Should be 2

3. **Verify in Next Message**:
   - Send another message asking about the code
   - AI should remember both code blocks and file references

---

## Test 4: Context Inclusion in AI Requests

### Messages to Send:

**Message 1:**
```
Here's my model:

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
```
```

**Message 2:**
```
I want to add a discount field to this model.
```

**Message 3:**
```
Wait, actually I also need a description field. Can you update the model again?
```

### ✅ What to Check:

1. **Check Logs** (for message 3):
   ```
   [ConversationManager] Stateless enriched context: X messages total (summary=no, code_blocks=1, files=0)
   [ConversationManager] Including 1/1 code blocks
   ```

2. **Check AI Response**:
   - AI should remember the Product model from message 1
   - Should understand you want both discount AND description fields
   - Should reference the original model structure

3. **Verify Token Budget**:
   - Check logs for token allocation:
   ```
   [ConversationManager] Including conversation summary in messages
   [TokenBudgetManager] Calculated budget for 8192 tokens: {...}
   ```

---

## Test 5: Conversation Summarization Trigger

### Messages to Send:

Send **35+ messages** (the default threshold is 30 messages).

**Pattern:**
1. Message 1: "Let's build a todo app"
2. Messages 2-10: Discuss features, requirements
3. Messages 11-20: Share code snippets
4. Messages 21-30: Ask questions about implementation
5. Messages 31-35: Continue conversation

### ✅ What to Check:

1. **Check Logs** (after message 30):
   ```
   [ConversationSummarizer] Should summarize: message_count=30, ...
   [ChatConsumer] Triggered async summarization for conversation ...
   ```

2. **Check Celery Task**:
   ```
   [summarize_conversation_task] Successfully summarized conversation ...
   ```

3. **Check Admin Panel** (after summarization):
   - `conversation_summary`: Should have a summary text
   - `summary_metadata`: Should show:
     - `last_summarized_at`: Timestamp
     - `messages_summarized_count`: Number of messages summarized
     - `summary_version`: 1

4. **Check Next Message**:
   - Send message 36: "Can you remind me what we discussed about authentication?"
   - AI should reference the summary and provide context
   - Check logs:
     ```
     [ConversationManager] Including conversation summary in messages
     ```

---

## Test 6: Token Budget Allocation

### Messages to Send:

**Message 1:**
```
Here's a large code file:

```python
# ... (paste a large code block, 100+ lines)
```
```

**Message 2-10:**
```
Ask various questions about the code
```

### ✅ What to Check:

1. **Check Logs**:
   ```
   [TokenBudgetManager] Calculated budget for 8192 tokens: {
     'summary': 800,
     'code_blocks': 2457,
     'recent_messages': 3277,
     'system_prompt': 1638
   }
   [TokenBudgetManager] Selected 5/10 code blocks using 2457/2457 tokens
   ```

2. **Verify Priority**:
   - Most recent code blocks should be included
   - Older code blocks may be excluded if over budget

---

## Test 7: Code Context in Summary

### Messages to Send:

Send **30+ messages** with code blocks in early messages, then ask about the code in later messages.

**Example:**
- Messages 1-15: Include code blocks
- Messages 16-30: Discussion without code
- Message 31: "What was that function we discussed earlier?"

### ✅ What to Check:

1. **Check Summary** (after summarization):
   - Summary should mention the code discussed
   - Should preserve important code references

2. **Check AI Response** (message 31):
   - AI should be able to reference the code from the summary
   - Should maintain context across the conversation

---

## 🔍 Verification Checklist

### For Each Test:

- [ ] **Code Extraction**: Logs show code blocks extracted
- [ ] **File Detection**: Logs show file references extracted
- [ ] **Admin Panel**: Fields populated correctly
- [ ] **AI Context**: AI remembers code/file references
- [ ] **Token Budget**: Logs show proper allocation
- [ ] **Summarization**: Triggers at threshold (30 messages)
- [ ] **Summary Usage**: Summary included in later messages

---

## 📊 Expected Log Output

### Normal Operation:
```
[ChatConsumer] Extracted code context: 2 blocks, 1 files
[ConversationManager] Stateless enriched context: 5 messages total (summary=no, code_blocks=2, files=1)
[ConversationManager] Including 2/2 code blocks
[ConversationManager] Including 3/3 recent messages
```

### With Summary:
```
[ChatConsumer] Triggered async summarization for conversation abc-123
[ConversationManager] Including conversation summary in messages
[ConversationManager] Stateless enriched context: 4 messages total (summary=yes, code_blocks=1, files=0)
```

### Token Budget:
```
[TokenBudgetManager] Calculated budget for 8192 tokens: {...}
[TokenBudgetManager] Selected 3/5 code blocks using 1500/2457 tokens
[TokenBudgetManager] Selected 8/10 messages using 3200/3277 tokens
```

---

## 🐛 Troubleshooting

### Code Blocks Not Extracted?

1. **Check Message Format**:
   - Ensure code blocks use proper markdown: ` ```language\ncode``` `
   - Check logs for extraction errors

2. **Check Async Issues**:
   - Verify no "SynchronousOnlyOperation" errors
   - Check database connection

### Files Not Detected?

1. **Check Format**:
   - File paths should look like: `path/to/file.py`
   - Relative paths work: `./file.py`, `../parent/file.py`

2. **Check Logs**:
   - Look for false positive filtering messages

### Summarization Not Triggering?

1. **Check Threshold**:
   - Default is 30 messages
   - Check `conversation.summarize_at_message_count`

2. **Check Celery**:
   - Ensure Celery worker is running
   - Check Celery logs for task execution

### Summary Not Used?

1. **Check Summary Exists**:
   - Verify `conversation.conversation_summary` has content

2. **Check Logs**:
   - Look for "Including conversation summary" messages

---

## 📝 Quick Test Script

### Minimal Test (2 Messages):

```python
# Message 1
"""
Check my code:

```python
def hello():
    print("Hello World")
```
"""

# Message 2
"What does this function do?"
```

**Expected Result:**
- Code block extracted
- AI remembers the function in response to message 2

---

## ✅ Success Criteria

Your implementation is working correctly if:

1. ✅ Code blocks are extracted and stored
2. ✅ File references are detected
3. ✅ Code context is included in AI requests
4. ✅ Token budget is allocated properly
5. ✅ Summarization triggers at threshold
6. ✅ Summary is used in later messages
7. ✅ AI maintains context across long conversations

---

## 🎯 Advanced Test: Full Workflow

### Complete Scenario:

1. **Start Conversation**: "Let's build a REST API"
2. **Share Code**: Post authentication code (message 2)
3. **Discuss**: Ask questions about the code (messages 3-10)
4. **Add More Code**: Share model definitions (messages 11-15)
5. **Continue Discussion**: More questions (messages 16-29)
6. **Trigger Summary**: Send message 30 (should trigger summarization)
7. **Verify Context**: Ask about code from message 2 (message 31)
8. **Check Summary Usage**: AI should remember everything

### Expected Behavior:

- Messages 2-15: Code blocks extracted
- Message 30: Summarization triggered
- Message 31: AI uses summary + recent messages + code blocks
- AI maintains full context despite 30+ messages

---

## 📚 Related Documentation

- `IMPLEMENTATION_SUMMARY_CURSOR_STYLE.md` - Implementation details
- `CURSOR_STYLE_CONTEXT_MANAGEMENT.md` - Architecture explanation
- `AGENT_RECORDS_UPDATE_GUIDE.md` - Setup guide

