# Duplicate Message Prevention Fix

## Issue

Users reported:
1. **Error messages appearing twice** - "The AI service is currently rate-limited..." shown twice
2. **AI responding that model was sent twice** - When sending Django model, AI said it received the same model twice

This indicated that:
- Messages were being sent/processed twice
- Conversation history might include duplicate messages

## Root Causes

1. **Frontend**: No protection against double-clicking or multiple rapid sends
2. **Backend**: No duplicate message detection
3. **No processing state tracking**: Could process same message multiple times if sent quickly

## Solution

### Frontend Changes (`useChatWebSocket.ts` & `ChatPage.tsx`)

1. **Added `isProcessing` state**:
   - Tracks if a message is currently being processed
   - Prevents sending new messages while one is processing

2. **Enhanced `sendMessage` function**:
   - Checks `isProcessing` before sending
   - Sets `isProcessing = true` immediately when sending
   - Returns early if already processing

3. **Reset `isProcessing` on completion**:
   - Set to `false` when `message_complete` received
   - Set to `false` on errors
   - Set to `false` on timeout

4. **UI disabled state**:
   - `ChatInput` disabled when `isProcessing` is true
   - Shows "Waiting for response..." placeholder

### Backend Changes (`consumers.py`)

1. **Added processing state tracking**:
   - `self.processing_message = False` - Tracks if processing a message
   - `self.last_message_hash = None` - Tracks last message hash to detect exact duplicates

2. **Duplicate detection**:
   - Checks if `processing_message` is True before processing
   - Creates hash of message content (changes every 5 seconds to allow retries)
   - Rejects exact duplicate messages sent within 5 seconds

3. **State management**:
   - Sets `processing_message = True` when starting to process
   - Resets to `False` on:
     - Successful completion
     - Any error (rate limit, API error, permission error, etc.)
     - Message save failures

## Code Changes

### Frontend

```typescript
// Added state
const [isProcessing, setIsProcessing] = useState(false);

// Enhanced sendMessage
const sendMessage = useCallback((content: string, attachments: string[] = []) => {
    if (isProcessing) {
        console.warn('Cannot send message: already processing');
        return;
    }
    setIsProcessing(true);
    // ... send message
}, [isProcessing]);

// Reset on completion
case 'message_complete':
    setIsProcessing(false);
    // ...

// Reset on chunk (first chunk indicates processing started)
case 'message_chunk':
    setIsProcessing(true);
    // ...
```

### Backend

```python
# In connect()
self.processing_message = False
self.last_message_hash = None

# In handle_user_message()
if self.processing_message:
    logger.warning("Ignoring duplicate message - already processing")
    return

# Create hash and check for exact duplicates
message_hash = hashlib.md5(f"{content}{time.time()//5}".encode()).hexdigest()
if message_hash == self.last_message_hash:
    logger.warning("Ignoring duplicate message (same content)")
    return

# Set processing
self.processing_message = True
self.last_message_hash = message_hash

# Reset on completion/error
self.processing_message = False
```

## Result

**Before:**
- ❌ Messages could be sent twice (double-click, rapid sends)
- ❌ Backend processed duplicates
- ❌ Error messages appeared twice
- ❌ AI received duplicate messages in history

**After:**
- ✅ Frontend prevents sending while processing
- ✅ Backend rejects duplicate messages
- ✅ Single error message per request
- ✅ No duplicate messages in conversation history

## Testing

1. **Test double-click prevention**:
   - Click send button rapidly multiple times
   - Should only send one message

2. **Test duplicate message rejection**:
   - Send same message twice quickly
   - Second should be rejected with error message

3. **Test error handling**:
   - Trigger rate limit error
   - Should see only one error message
   - Should be able to send new message after error

## Files Modified

1. `frontend/src/hooks/useChatWebSocket.ts`
   - Added `isProcessing` state
   - Enhanced `sendMessage` with duplicate prevention
   - Reset `isProcessing` on completion/error

2. `frontend/src/pages/chat/ChatPage.tsx`
   - Use `isProcessing` for input disabled state

3. `backend/apps/chat/consumers.py`
   - Added `processing_message` and `last_message_hash` tracking
   - Added duplicate message detection
   - Reset processing state on all completion/error paths

