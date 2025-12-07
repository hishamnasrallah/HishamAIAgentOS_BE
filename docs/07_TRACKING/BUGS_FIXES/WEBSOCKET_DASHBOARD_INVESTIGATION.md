---
title: "WebSocket Dashboard Connection Investigation"
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

# WebSocket Dashboard Connection Investigation

**Date:** December 2024  
**Status:** 🔍 **INVESTIGATING - Connection closes during handshake**

---

## 🚨 Problem Summary

Dashboard WebSocket connection is **accepted by backend** but **immediately closed by browser** before `onopen` event fires.

**Symptoms:**
- Backend logs: ✅ Connection accepted, message sent
- Frontend: ❌ Never receives `onopen`, only `onerror` with `readyState: 3` (CLOSED)
- Protocol/Extensions: Empty (handshake never completed)

---

## 🔍 Key Observations

1. **Chat WebSocket works perfectly** - Same server, same setup
2. **Backend accepts connection** - Logs confirm acceptance
3. **Connection closes ~20ms after acceptance** - Too fast for normal operation
4. **Frontend never sees `onopen`** - Handshake never completes

---

## 🧪 Tests Performed

1. ✅ Fixed dependency array issue (options causing re-renders)
2. ✅ Memoized message handler in DashboardPage
3. ✅ Enhanced error logging
4. ✅ Added delay before sending first message
5. ✅ Simplified connect method to match chat consumer pattern
6. ✅ Removed immediate message sending (test if that's the issue)

---

## 🔧 Current Implementation

### Backend (`DashboardConsumer`)
- Accepts connection
- Joins group
- **Does NOT send immediate message** (testing if this helps)

### Frontend (`useWebSocket`)
- Creates WebSocket connection
- Handles `onopen`, `onerror`, `onclose`, `onmessage`
- Uses refs to prevent re-render issues

---

## 🐛 Possible Root Causes

1. **Browser rejecting connection** - Protocol/extension mismatch
2. **Message sent too early** - Browser closes if message sent before handshake completes
3. **CORS/Origin issue** - Browser rejecting for security reason
4. **Middleware issue** - Something closing connection after accept
5. **Browser bug** - Specific browser behavior with this route

---

## 📋 Next Steps

1. **Test without immediate message** - Current change
2. **Check browser network tab** - See actual WebSocket frames
3. **Compare with chat** - Why does chat work but dashboard doesn't?
4. **Test in different browser** - Rule out browser-specific issue
5. **Check for exceptions** - Backend logs might show hidden errors

---

## 🔍 Debugging Checklist

- [ ] Check browser Network tab for WebSocket frames
- [ ] Verify WebSocket URL is correct
- [ ] Check if CORS headers are set correctly
- [ ] Compare chat vs dashboard routing patterns
- [ ] Test in different browser (Chrome, Firefox, Edge)
- [ ] Check backend logs for any exceptions after accept
- [ ] Verify channel layer is working
- [ ] Test with minimal consumer (no group, no message)

---

**Last Updated:** December 2024  
**Status:** 🔍 **INVESTIGATING - Removed immediate message sending**

