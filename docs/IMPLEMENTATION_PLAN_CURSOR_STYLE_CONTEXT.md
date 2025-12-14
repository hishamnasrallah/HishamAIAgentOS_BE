# Implementation Plan: Cursor-Style Context Management

## Overview
This plan implements Cursor-style context management features to handle large codebases and improve code-related conversations in our AI agent system.

## Goals
1. **Extract and preserve code blocks** from messages
2. **Track file references** discussed in conversations
3. **Smart token budget allocation** for optimal context distribution
4. **Integrate code context** into conversation summarization
5. **Improve context relevance** for code-related queries

## Implementation Phases

### Phase 1: Database Schema Updates
**Files to modify:**
- `backend/apps/chat/models.py`

**Changes:**
- Add `referenced_files` JSONField to Conversation model
- Add `referenced_code_blocks` JSONField to Conversation model
- Add `code_context_metadata` JSONField for tracking code-related metadata

**Migration:**
- Create migration `0007_add_code_context_tracking_fields.py`

---

### Phase 2: Code Extraction Service
**New file:**
- `backend/apps/chat/services/code_context_extractor.py`

**Functions:**
- `extract_code_blocks(message_content: str) -> List[Dict]`
- `extract_file_references(message_content: str) -> List[str]`
- `update_conversation_code_context(conversation: Conversation, message: Message)`
- `get_code_context_for_conversation(conversation: Conversation) -> Dict`

**Features:**
- Extract markdown code blocks (```language\ncode```)
- Extract inline code references
- Extract file paths (e.g., `app/models.py`, `src/components/Button.tsx`)
- Extract function/class references
- Store with metadata (language, line ranges if available)

---

### Phase 3: Token Budget Management
**New file:**
- `backend/apps/chat/services/token_budget_manager.py`

**Functions:**
- `calculate_token_budget(total_limit: int, context: Dict) -> Dict[str, int]`
- `estimate_tokens(text: str) -> int`
- `prioritize_context_items(items: List[Dict], budget: int) -> List[Dict]`

**Budget Allocation Strategy:**
```
Default (with summary):
- Summary: 10% (if exists)
- Code blocks: 30%
- Recent messages: 40%
- System prompt: 20%

Without summary:
- Code blocks: 35%
- Recent messages: 45%
- System prompt: 20%
```

**Priority Rules:**
1. Current file context > referenced files
2. Recent code blocks > older code blocks
3. Larger code blocks > smaller ones (up to limit)
4. Recent messages prioritized by recency

---

### Phase 4: ConversationManager Integration
**File to modify:**
- `backend/apps/integrations/services/conversation_manager.py`

**Changes:**
- Update `get_optimal_messages_to_send()` to:
  - Use token budget manager
  - Include code blocks in context
  - Prioritize code context when relevant
  - Respect token limits intelligently

**New method:**
- `build_enriched_context(platform_config, conversation_history, conversation_context, current_message, code_context) -> List[Dict]`

---

### Phase 5: ConversationSummarizer Enhancement
**File to modify:**
- `backend/apps/chat/services/conversation_summarizer.py`

**Changes:**
- Include code blocks in summary generation
- Preserve important code references in summary
- Update `_format_messages_for_summary()` to include code context

---

### Phase 6: ChatConsumer Integration
**File to modify:**
- `backend/apps/chat/consumers.py`

**Changes:**
- Extract code blocks and file references on message save
- Update conversation code context
- Pass code context to ConversationManager

---

### Phase 7: API & Admin Updates
**Files to modify:**
- `backend/apps/chat/serializers.py`
- `backend/apps/chat/admin.py`

**Changes:**
- Add new fields to serializers
- Display code context in admin interface
- Add read-only fields for code tracking

---

### Phase 8: Testing & Validation
**Test cases:**
1. Code block extraction from markdown
2. File reference detection
3. Token budget allocation
4. Code context in summarization
5. Integration with existing conversation flow

---

## Implementation Details

### Code Block Extraction Patterns

```python
# Markdown code blocks
pattern = r'```(\w+)?\n([\s\S]*?)```'

# Inline code references
pattern = r'`([^`]+)`'

# File paths (common patterns)
patterns = [
    r'([a-zA-Z0-9_\-\./]+\.(py|js|ts|tsx|jsx|java|cpp|c|h|hpp|go|rs|rb|php|swift|kt))',
    r'([a-zA-Z0-9_\-\./]+/.*)',
]
```

### Code Context Storage Format

```python
{
    "referenced_files": [
        "app/models.py",
        "frontend/src/components/Chat.tsx"
    ],
    "code_blocks": [
        {
            "id": "msg-uuid-1-block-0",
            "message_id": "msg-uuid-1",
            "language": "python",
            "content": "class User:\n    ...",
            "line_count": 10,
            "extracted_at": "2025-12-14T10:00:00Z",
            "tokens": 150
        }
    ],
    "metadata": {
        "total_code_blocks": 5,
        "total_code_tokens": 750,
        "last_updated": "2025-12-14T10:00:00Z"
    }
}
```

### Token Budget Calculation Example

```python
# Example: 8192 token limit (GPT-3.5)
budget = {
    "summary": 800,        # 10% if summary exists
    "code_blocks": 2457,   # 30%
    "recent_messages": 3277, # 40%
    "system_prompt": 1638  # 20%
}

# Prioritize code blocks
code_blocks = [
    {"content": "...", "tokens": 500, "priority": 1.0},
    {"content": "...", "tokens": 300, "priority": 0.8},
]
# Fill budget starting with highest priority
```

---

## Files to Create/Modify Summary

### New Files:
1. `backend/apps/chat/services/code_context_extractor.py`
2. `backend/apps/chat/services/token_budget_manager.py`
3. `backend/apps/chat/migrations/0007_add_code_context_tracking_fields.py`

### Modified Files:
1. `backend/apps/chat/models.py` - Add fields
2. `backend/apps/integrations/services/conversation_manager.py` - Integration
3. `backend/apps/chat/services/conversation_summarizer.py` - Code in summaries
4. `backend/apps/chat/consumers.py` - Extract on message
5. `backend/apps/chat/serializers.py` - API fields
6. `backend/apps/chat/admin.py` - Admin display

---

## Testing Checklist

- [ ] Code blocks extracted from markdown
- [ ] File paths detected correctly
- [ ] Token budget calculated accurately
- [ ] Code context included in API requests
- [ ] Summarization preserves code references
- [ ] Admin displays code context
- [ ] No performance degradation
- [ ] Handles edge cases (malformed code, large files)

---

## Performance Considerations

1. **Code extraction**: Should be fast (regex-based)
2. **Token counting**: Use approximation, not exact count
3. **Storage**: JSONField efficient for code blocks
4. **Query**: Index on `referenced_files` if needed later

---

## Future Enhancements (Phase 2)

1. **Vector embeddings** for semantic code search
2. **AST parsing** for better code understanding
3. **Symbol resolution** (function/class linking)
4. **File content retrieval** from repository
5. **Codebase indexing** service

