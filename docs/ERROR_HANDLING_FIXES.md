# Error Handling Fixes

## Issues Fixed

### 1. Rate Limit Errors (429) - Poor Error Messages

**Problem:**
- When OpenRouter API returned rate limit errors (429), the error messages were generic
- Users saw: "I'm sorry, I didn't receive a proper response" or cryptic error codes
- No guidance on what to do about rate limits

**Fix:**
- Enhanced error extraction in `OpenRouterAdapter` to pull detailed error messages from API responses
- Added specific handling for `RateLimitError` before catching generic `APIError`
- Extracts error messages from nested response structure (handles OpenRouter's error format)
- Provides user-friendly messages explaining rate limits and suggesting solutions

**Changes:**
- `openrouter_adapter.py`: Both `generate_completion()` and `generate_streaming_completion()`
  - Catch `RateLimitError` first (before `APIError`)
  - Extract detailed error messages from response
  - Provide helpful error message: "Rate limit exceeded: [details]. Please wait a moment and try again, or add your own API key for higher limits."

### 2. Generic API Errors - Missing Details

**Problem:**
- API errors only showed generic messages without error codes or details
- Hard to diagnose issues

**Fix:**
- Enhanced error extraction to get error codes and messages
- Logs include error codes and detailed messages
- Users see more informative error messages

### 3. Error Handling in ChatConsumer

**Problem:**
- Errors during streaming were caught generically
- Rate limit errors weren't handled specially
- Users didn't get helpful guidance

**Fix:**
- Added specific handling for `OpenAIError` (custom exception from adapters)
- Detects rate limit errors by checking error message content
- Provides user-friendly messages explaining the issue
- Sends error type in response so frontend can handle differently if needed

**Changes:**
- `consumers.py`: Enhanced `handle_user_message()` error handling
  - Checks if error is `OpenAIError` (raised by adapters)
  - Detects rate limit errors (checks for "rate limit" or "429" in message)
  - Provides helpful messages for rate limits
  - Falls back to non-streaming execution for other errors

## Error Message Flow

### Before:
```
OpenRouter API → RateLimitError → Generic "Rate limit exceeded" → User sees: "I'm sorry, I didn't receive a proper response"
```

### After:
```
OpenRouter API → RateLimitError → Extract detailed message → "Rate limit exceeded: mistralai/mistral-7b-instruct:free is temporarily rate-limited upstream. Please retry shortly, or add your own key..." → User sees helpful message
```

## Error Handling Details

### Rate Limit Error Handling

1. **In Adapter (`openrouter_adapter.py`)**:
   ```python
   except openai.RateLimitError as e:
       # Extract detailed error from response
       error_message = extract_from_response(e)
       raise OpenAIError("Rate limit exceeded: {details}. Please wait...")
   ```

2. **In Consumer (`consumers.py`)**:
   ```python
   except Exception as stream_error:
       if isinstance(stream_error, OpenAIError):
           if 'rate limit' in str(stream_error).lower():
               # Send helpful message to user
               await self.send_error("The AI service is currently rate-limited...")
   ```

### Error Extraction

The adapter now extracts errors from OpenRouter's response structure:
```json
{
  "error": {
    "message": "Provider returned error",
    "code": 429,
    "metadata": {
      "raw": "mistralai/mistral-7b-instruct:free is temporarily rate-limited upstream..."
    }
  }
}
```

The code extracts:
- `error_code` from `error.code` or `status_code`
- `error_message` from `error.metadata.raw` (most detailed) or `error.message`

## Testing Error Handling

### Test Rate Limit Error:

1. **Trigger rate limit**:
   - Send multiple requests quickly to OpenRouter free tier
   - Or wait for natural rate limit

2. **Check logs**:
   ```
   [OpenRouterAdapter] OpenRouter rate limit exceeded: mistralai/mistral-7b-instruct:free is temporarily rate-limited upstream... (code: 429)
   [ChatConsumer] Rate limit error: Rate limit exceeded: ...
   ```

3. **Check user sees**:
   - Helpful error message in chat
   - Suggestion to wait or add API key
   - Error type: `rate_limit` in response

### Test Generic API Error:

1. **Trigger error** (e.g., invalid API key):
   ```
   [OpenRouterAdapter] OpenRouter API error: Error code: 401 - Invalid API key
   [ChatConsumer] API error: AI service error: Invalid API key
   ```

2. **Check user sees**:
   - Clear error message
   - Error type: `api_error` in response

## Error Response Format

The consumer now sends structured error responses:
```json
{
  "type": "message_complete",
  "message_id": null,
  "status": "error",
  "error": "The AI service is currently rate-limited...",
  "error_type": "rate_limit"  // or "api_error"
}
```

This allows the frontend to:
- Display appropriate UI (e.g., retry button for rate limits)
- Show different messages based on error type
- Handle errors gracefully

## Common Error Scenarios

### 1. Rate Limit (429)
- **Cause**: Free tier limits exceeded
- **User sees**: "The AI service is currently rate-limited. Please wait a moment and try again. You can add your own API key in settings for higher limits."
- **Solution**: Wait 1-2 minutes, or add API key

### 2. Invalid API Key (401)
- **Cause**: API key is invalid or expired
- **User sees**: "AI service error: Invalid API key"
- **Solution**: Update API key in Django Admin

### 3. Model Unavailable
- **Cause**: Model is temporarily unavailable
- **User sees**: "AI service error: Model unavailable"
- **Solution**: Try again later, or use different model

### 4. Network Error
- **Cause**: Connection to API failed
- **User sees**: "AI service error: Connection failed"
- **Solution**: Check internet connection, try again

## Files Modified

1. `backend/apps/integrations/adapters/openrouter_adapter.py`
   - Enhanced `generate_completion()` error handling
   - Enhanced `generate_streaming_completion()` error handling
   - Better error extraction and messages

2. `backend/apps/chat/consumers.py`
   - Enhanced error handling in `handle_user_message()`
   - Specific handling for rate limit errors
   - Better error messages for users

## Next Steps

1. **Test error scenarios**:
   - Rate limit errors
   - API errors
   - Network errors

2. **Monitor logs**:
   - Check error messages are informative
   - Verify users see helpful messages

3. **Frontend updates** (optional):
   - Handle `error_type` field in responses
   - Show retry button for rate limit errors
   - Display error messages appropriately

