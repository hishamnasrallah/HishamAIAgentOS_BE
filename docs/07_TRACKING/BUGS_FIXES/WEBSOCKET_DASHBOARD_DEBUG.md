---
title: "WebSocket Dashboard Connection Debug"
description: "**Date:** December 2024"

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

# WebSocket Dashboard Connection Debug

**Date:** December 2024  
**Status:** 🔍 **INVESTIGATING**

---

## 🚨 Problem

Dashboard WebSocket connection fails immediately with `readyState: 3` (CLOSED), while chat WebSocket works fine.

**Error:**
```
[WebSocket] Error: Event {isTrusted: true, type: 'error', ...}
[WebSocket] ReadyState: 3
[WebSocket] URL: ws://localhost:8000/ws/dashboard/?token=...
[WebSocket] Connection closed unexpectedly
```

---

## ✅ What Works

- **Chat WebSocket** (`/ws/chat/<conversation_id>/`) - ✅ Working
- **Server is running with ASGI** (daphne) - ✅ Confirmed (chat works)

---

## 🔍 Investigation

### Differences Between Chat and Dashboard

1. **Routing Pattern:**
   - Chat: `r'ws/chat/(?P<conversation_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$'`
   - Dashboard: `r'ws/dashboard/$'`

2. **Consumer Authentication:**
   - Chat: Rejects unauthenticated users (`await self.close(code=4001)`)
   - Dashboard: Accepts unauthenticated users

3. **URL Construction:**
   - Chat: `ws://localhost:8000/ws/chat/${conversationId}/?token=...`
   - Dashboard: `ws://localhost:8000/ws/dashboard/?token=...`

### Possible Causes

1. **Routing Order Issue:** Monitoring routing is first in the list - should be fine
2. **Middleware Exception:** JWT middleware might be throwing an exception for dashboard route
3. **Consumer Exception:** Dashboard consumer might be failing before `accept()`
4. **Channel Layer Issue:** InMemoryChannelLayer might have issues with dashboard group

---

## 🔧 Fixes Applied

1. ✅ Enhanced error handling in `DashboardConsumer.connect()`
2. ✅ Added detailed logging in JWT middleware
3. ✅ Improved exception handling in middleware chain
4. ✅ Added defensive checks for user authentication

---

## 📋 Next Steps

1. **Check Backend Logs:**
   - Look for `[JWT Middleware]` logs
   - Look for `[DashboardConsumer]` logs
   - Check for any exceptions

2. **Test Connection:**
   - Try connecting to dashboard WebSocket
   - Check if logs show connection attempt
   - Verify if consumer's `connect()` method is called

3. **Compare with Chat:**
   - Verify chat connection logs
   - Compare middleware behavior
   - Check if there's a routing pattern issue

---

## 🐛 Debugging Commands

### Check Backend Logs
```bash
# Look for WebSocket connection attempts
grep -i "dashboard\|websocket\|jwt middleware" backend/logs/*.log
```

### Test WebSocket Connection
```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/ws/dashboard/?token=YOUR_TOKEN')
ws.onopen = () => console.log('Connected')
ws.onerror = (e) => console.error('Error:', e)
ws.onclose = (e) => console.log('Closed:', e.code, e.reason)
```

---

**Last Updated:** December 2024  
**Status:** 🔍 **DEBUGGING IN PROGRESS**

