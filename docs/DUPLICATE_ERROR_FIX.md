# Duplicate Error Message Fix

## Issue

Users were seeing error messages **twice** in the UI when errors occurred (especially rate limit errors).

## Root Cause

The backend was sending error messages **twice**:

1. **First**: Via `send_error()` which sends `{"type": "error", "message": "..."}`
2. **Second**: Via `message_complete` which sends `{"type": "message_complete", "status": "error", "error": "..."}`

Both messages triggered the frontend's `onError` callback, causing **two toast notifications** for the same error.

## Solution

**Removed duplicate `send_error()` calls** when we're already sending the error via `message_complete`.

**Strategy**:
- For errors that happen during message processing: Send error via `message_complete` only
- For errors that happen outside message processing (e.g., invalid JSON, unknown message type): Keep `send_error()` since there's no `message_complete` response

## Changes Made

### Removed `send_error()` from these locations:

1. **Rate limit errors** (2 places):
   ```python
   # BEFORE: Both send_error() and message_complete
   await self.send_error(user_message)
   await self.send(text_data=json.dumps({'type': 'message_complete', 'error': user_message, ...}))
   
   # AFTER: Only message_complete
   await self.send(text_data=json.dumps({'type': 'message_complete', 'error': user_message, ...}))
   ```

2. **API errors** (2 places):
   - During streaming error handling
   - During fallback error handling

3. **Permission errors**:
   - Both in initial handling and fallback

4. **General errors**:
   - Final exception handler

### Kept `send_error()` for these (no message_complete response):

- Invalid JSON errors
- Unknown message type errors
- Empty message content
- Duplicate message detection
- Message save failures (before processing starts)

## Result

**Before:**
- ❌ Error message sent twice (`send_error` + `message_complete`)
- ❌ Two toast notifications shown to user
- ❌ Confusing duplicate error messages

**After:**
- ✅ Error message sent once (via `message_complete` only)
- ✅ Single toast notification
- ✅ Clean error handling

## Why This Works

`message_complete` with `status: 'error'` is the standard way to signal completion with an error during message processing. It:
- Signals completion (frontend can accept new messages)
- Includes error information
- Is handled by the same frontend logic

The separate `error` message type is for errors that occur outside the normal message processing flow (e.g., validation errors, connection errors).

## Files Modified

- `backend/apps/chat/consumers.py`
  - Removed duplicate `send_error()` calls
  - All errors during message processing now sent via `message_complete` only

