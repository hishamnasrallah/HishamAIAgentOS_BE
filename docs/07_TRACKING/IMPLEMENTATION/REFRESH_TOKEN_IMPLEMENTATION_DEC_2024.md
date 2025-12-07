---
title: "Refresh Token Implementation - December 2024"
description: "Implemented a comprehensive refresh token mechanism in the frontend to handle JWT token expiration and automatic token refresh."

category: "Core"
language: "en"
original_language: "en"

purpose: |
  Documentation file for core category.

target_audience:
  primary:
    - Project Manager
    - CTO / Technical Lead
  secondary:
    - All

applicable_phases:
  primary:
    - Development

tags:
  - core
  - implementation

status: "active"
priority: "medium"
difficulty: "intermediate"
completeness: "100%"
quality_status: "draft"

estimated_read_time: "10 minutes"

version: "1.0"
last_updated: "2025-12-06"
last_reviewed: "2025-12-06"
review_frequency: "quarterly"

author: "Development Team"
maintainer: "Development Team"

related: []
see_also: []
depends_on: []
prerequisite_for: []

aliases: []

changelog:
  - version: "1.0"
    date: "2025-12-06"
    changes: "Initial version after reorganization"
    author: "Documentation Reorganization Script"
---

# Refresh Token Implementation - December 2024

## Overview

Implemented a comprehensive refresh token mechanism in the frontend to handle JWT token expiration and automatic token refresh.

## Problem Statement

The previous implementation had a basic refresh token mechanism that only worked reactively (when a 401 error occurred). There was no:
- Proactive token refresh before expiration
- Token expiration checking
- Automatic refresh interval
- Proper handling of concurrent requests during refresh

## Solution Implemented

### 1. Enhanced API Interceptor (`frontend/src/services/api.ts`)

**Features:**
- **Request Queue**: When multiple requests fail with 401 simultaneously, they are queued and processed after token refresh
- **Single Refresh**: Only one refresh request is made even if multiple 401 errors occur
- **Infinite Loop Prevention**: Refresh endpoint calls are excluded from interceptor logic
- **Automatic Retry**: Failed requests are automatically retried with the new token

**Key Implementation:**
```typescript
// Queue system for concurrent 401 errors
let isRefreshing = false
let failedQueue: Array<{ resolve, reject }> = []

// Refresh token function
const refreshToken = async (): Promise<string | null> => {
  // Uses axios directly to bypass interceptor
  // Prevents infinite refresh loops
}
```

### 2. Token Refresh Utility (`frontend/src/utils/tokenRefresh.ts`)

**New utility functions:**
- `isTokenExpiringSoon(token, bufferMinutes)`: Checks if token expires within specified minutes
- `isTokenExpired(token)`: Checks if token is already expired
- `refreshAccessToken()`: Refreshes access token using refresh token
- `getValidAccessToken()`: Gets valid token, refreshing if necessary
- `setupTokenRefreshInterval()`: Sets up automatic token refresh every minute

**Features:**
- Proactive token refresh (refreshes 5 minutes before expiration)
- Token expiration checking
- Automatic refresh interval
- Clean error handling

### 3. Enhanced Auth Store (`frontend/src/stores/authStore.ts`)

**Updated `checkAuth` method:**
- Checks if token is missing and refreshes if refresh token exists
- Proactively refreshes tokens expiring within 5 minutes
- Handles 401 errors by attempting token refresh
- Updates store state with new tokens

### 4. Automatic Token Refresh in App (`frontend/src/App.tsx`)

**Added:**
- `useEffect` hook that sets up automatic token refresh interval on app mount
- Checks token expiration every minute
- Refreshes tokens proactively before expiration
- Cleans up interval on unmount

### 5. Auth API Enhancement (`frontend/src/services/api.ts`)

**Added `refreshToken` method:**
```typescript
refreshToken: () => {
  const refreshToken = localStorage.getItem('refresh_token')
  return axios.post(`${API_BASE_URL}/auth/token/refresh/`, { refresh: refreshToken })
}
```

## How It Works

### Reactive Refresh (401 Error Handling)

1. API request fails with 401 Unauthorized
2. Interceptor catches the error
3. Checks if refresh is already in progress
   - If yes: Queue the request
   - If no: Start refresh process
4. Refresh token is used to get new access token
5. Queued requests are retried with new token
6. Original failed request is retried with new token

### Proactive Refresh

1. App initializes and sets up refresh interval (every minute)
2. Interval checks if token expires within 5 minutes
3. If yes, automatically refreshes token
4. New token is stored in localStorage
5. Auth store is updated with new token

### Token Expiration Checking

1. `checkAuth` is called (e.g., on app load, route change)
2. Token expiration is checked by decoding JWT
3. If token expires within 5 minutes, refresh is triggered
4. User profile is verified with `/auth/me/` endpoint
5. If 401 occurs, refresh is attempted once more

## Token Lifecycle

1. **Login/Register**: Access token (30 min) and refresh token (30 days) are stored
2. **API Requests**: Access token is sent in Authorization header
3. **Token Expiring Soon**: Proactive refresh (5 min before expiration)
4. **401 Error**: Reactive refresh using refresh token
5. **Refresh Success**: New access token (and possibly new refresh token) stored
6. **Refresh Failure**: Tokens cleared, user redirected to login

## Configuration

### Token Lifetimes (Backend)
- **Access Token**: 30 minutes (configurable via `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Refresh Token**: 30 days (configurable via `JWT_REFRESH_TOKEN_EXPIRE_DAYS`)

### Refresh Settings (Frontend)
- **Proactive Refresh Buffer**: 5 minutes before expiration
- **Refresh Check Interval**: Every 60 seconds (1 minute)

## Files Modified

1. **`frontend/src/services/api.ts`**
   - Enhanced response interceptor with request queue
   - Added `refreshToken` function
   - Added `authAPI.refreshToken` method

2. **`frontend/src/stores/authStore.ts`**
   - Enhanced `checkAuth` with proactive refresh
   - Added token expiration checking
   - Improved error handling

3. **`frontend/src/utils/tokenRefresh.ts`** (NEW)
   - Token expiration utilities
   - Refresh token functions
   - Automatic refresh interval setup

4. **`frontend/src/App.tsx`**
   - Added automatic token refresh interval on mount

## Benefits

1. **Seamless User Experience**: Users don't get logged out unexpectedly
2. **Reduced API Errors**: Proactive refresh prevents 401 errors
3. **Concurrent Request Handling**: Multiple simultaneous requests don't cause multiple refresh attempts
4. **Automatic Management**: Tokens are refreshed automatically without user intervention
5. **Error Recovery**: Failed requests are automatically retried after token refresh

## Testing Recommendations

1. **Token Expiration Test**:
   - Wait for access token to expire (or manually expire it)
   - Make an API request
   - Verify token is automatically refreshed and request succeeds

2. **Proactive Refresh Test**:
   - Set token to expire in 4 minutes
   - Wait 1 minute
   - Verify token is automatically refreshed

3. **Concurrent Requests Test**:
   - Make multiple API requests simultaneously
   - Expire token during requests
   - Verify only one refresh occurs and all requests succeed

4. **Refresh Token Expiration Test**:
   - Use expired refresh token
   - Verify user is redirected to login
   - Verify tokens are cleared

## Security Considerations

1. **Token Storage**: Tokens stored in localStorage (consider httpOnly cookies for production)
2. **Token Rotation**: Backend rotates refresh tokens (`ROTATE_REFRESH_TOKENS: True`)
3. **Token Blacklisting**: Expired refresh tokens are blacklisted (`BLACKLIST_AFTER_ROTATION: True`)
4. **HTTPS Required**: Tokens should only be transmitted over HTTPS in production

## Known Limitations

1. **localStorage Security**: Tokens in localStorage are accessible to XSS attacks
2. **No Token Revocation**: Client-side logout doesn't revoke tokens on server
3. **Single Tab**: Token refresh in one tab doesn't update other tabs

## Future Enhancements

1. **Token Revocation**: Implement token blacklisting on logout
2. **Multi-Tab Sync**: Use BroadcastChannel API to sync tokens across tabs
3. **Secure Storage**: Consider using httpOnly cookies for token storage
4. **Token Refresh Events**: Emit events when tokens are refreshed for UI updates

---

**Date**: December 2024  
**Status**: ✅ Completed  
**Next Steps**: Test thoroughly and consider security enhancements for production

