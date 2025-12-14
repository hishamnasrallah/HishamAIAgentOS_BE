# Update Code Block Languages

## Overview

This command updates language detection for existing code blocks without re-extracting them. Useful after improving language inference logic.

## Advantages

✅ **Faster** - Only updates language field, doesn't re-extract from messages  
✅ **Non-destructive** - Preserves all existing content, tokens, and metadata  
✅ **Safe** - Has `--dry-run` mode to preview changes before applying  
✅ **Targeted** - Only processes conversations that have code blocks  

## Usage

### Option 1: Dry Run (Preview Changes)

```bash
python manage.py update_code_block_languages --all --dry-run
```

Shows what would be updated without making any changes.

### Option 2: Update Single Conversation

```bash
python manage.py update_code_block_languages <conversation_id>
```

### Option 3: Update All Conversations

```bash
python manage.py update_code_block_languages --all
```

## Example Output

```
Processing: New Chat (23edfa07-22a3-46ff-b5fe-154220855ddd)
  Found 3 code blocks
  ✅ Fixed: text → python
     Preview: class User(models.Model): email = models.EmailField(unique=True)...
  ✅ Fixed: text → python
     Preview: class User(models.Model): email = models.EmailField(unique=True)...
  ✅ Fixed: text → python
     Preview: class User(models.Model): email = models.EmailField(unique=True)...
  💾 Saved 3 language updates

======================================================================
✅ Language Update Complete!
  Conversations processed: 1
  Total blocks processed: 3
  Language fixes applied: 3
======================================================================
```

## When to Use

- After improving language inference logic (like we just did)
- To fix blocks incorrectly labeled as `"language": "text"`
- To ensure consistency across all conversations

## Comparison with `re_extract_code_context`

| Feature | `update_code_block_languages` | `re_extract_code_context` |
|---------|------------------------------|---------------------------|
| Speed | ⚡ Fast (language only) | 🐌 Slower (full re-extraction) |
| Preserves | ✅ All existing data | ⚠️ Re-extracts everything |
| Use case | Fix language labels | Full re-extraction needed |

