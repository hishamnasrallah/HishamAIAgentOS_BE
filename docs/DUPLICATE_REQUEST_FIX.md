# Duplicate Request Fix

## Issue

The OpenAI Python library has **built-in automatic retry logic** that retries requests on certain errors. This can cause:

1. **Multiple API calls for the same request** - especially on rate limit errors
2. **Unnecessary API usage** - wasting credits/tokens
3. **Faster rate limit exhaustion** - retries count against rate limits

## Root Cause

When calling `client.chat.completions.create()` for streaming:
- OpenAI library defaults to `max_retries=2` (retries 2 more times after initial request)
- It automatically retries on network errors, 5xx errors, and some 429 errors
- This happens **before** our error handling code can catch it

**Evidence from logs:**
```
File "...openai\_base_client.py", line 1484, in _request
    return await self._retry_request(
File "...openai\_base_client.py", line 1530, in _retry_request
    return await self._request(
```

## Solution

**Disable automatic retries** in the OpenAI client initialization:
- Set `max_retries=0` when creating `AsyncOpenAI` client
- This prevents the library from retrying automatically
- We handle errors explicitly in our code

## Changes Made

### 1. OpenRouterAdapter (`openrouter_adapter.py`)
```python
self.client = openai.AsyncOpenAI(
    api_key=self.api_key,
    base_url=base_url,
    http_client=http_client,
    max_retries=0  # Disable automatic retries
)
```

### 2. OpenAIAdapter (`openai_adapter.py`)
```python
self.client = openai.AsyncOpenAI(
    api_key=self.api_key,
    http_client=http_client,
    max_retries=0  # Disable automatic retries - we handle retries via _retry_with_backoff
)
```

**Note**: For non-streaming requests in OpenAIAdapter, we already have `_retry_with_backoff()` which handles retries explicitly with better error handling.

### 3. Added Request Tracking
- Added request ID logging to track potential duplicates
- Logs request details to help identify if same request is sent twice

## Result

**Before:**
- ❌ OpenAI library retries automatically (default: 2 retries)
- ❌ Rate limit errors trigger retries before our code catches them
- ❌ Multiple API calls for same request
- ❌ Faster rate limit exhaustion

**After:**
- ✅ No automatic retries from OpenAI library
- ✅ Errors are caught immediately by our error handling
- ✅ Single API call per request
- ✅ Better control over retry logic

## Why This is Safe

1. **For streaming**: Retries don't make sense anyway - you can't retry a stream
2. **For non-streaming**: OpenAIAdapter already has `_retry_with_backoff()` for explicit retry control
3. **For rate limits**: We want to catch 429 errors immediately, not retry them
4. **For other errors**: We can add explicit retry logic if needed (with better error handling)

## Testing

After this fix:
1. Check logs - should see only **one** "Starting OpenRouter streaming request" per user message
2. Rate limit errors should be caught immediately (no retries)
3. API usage should be accurate (no duplicate calls)

## Files Modified

1. `backend/apps/integrations/adapters/openrouter_adapter.py`
   - Set `max_retries=0` in client initialization
   - Added request ID logging

2. `backend/apps/integrations/adapters/openai_adapter.py`
   - Set `max_retries=0` in client initialization for consistency

