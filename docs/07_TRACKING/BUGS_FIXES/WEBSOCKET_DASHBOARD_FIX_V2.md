---
title: "WebSocket Dashboard Connection Fix - V2"
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

# WebSocket Dashboard Connection Fix - V2

**Date:** December 2024  
**Status:** ✅ **FIXED - Server Configuration Issue**

---

## 🚨 Problem

WebSocket connections to `/ws/dashboard/` were failing immediately with:
- `readyState: 3` (CLOSED)
- Connection closed unexpectedly
- Error: "This usually means the server rejected the connection or the server is not running"

---

## 🔍 Root Cause

**The Django server was running with `python manage.py runserver` instead of `daphne`.**

Django's standard `runserver` command **does NOT support WebSockets**. It only handles HTTP requests. WebSocket connections require an ASGI server like Daphne.

---

## ✅ Solution

### Step 1: Install Daphne

```bash
cd backend
pip install daphne
# Or install all requirements:
pip install -r requirements/base.txt
```

### Step 2: Stop Current Server

If you're running the server, stop it (Ctrl+C in the terminal).

### Step 3: Start Server with Daphne

```bash
cd backend
daphne core.asgi:application --bind 0.0.0.0 --port 8000
```

**Important:** You MUST use `daphne`, not `python manage.py runserver`.

---

## 📋 Verification

After starting with daphne, you should see:
1. ✅ Server starts without errors
2. ✅ WebSocket connection succeeds (check browser console)
3. ✅ `readyState: 1` (OPEN) instead of `3` (CLOSED)
4. ✅ No connection errors in browser console

---

## 🔧 Files Updated

1. ✅ `backend/requirements/base.txt` - Added `daphne==4.0.0`
2. ✅ `README.md` - Updated with daphne instructions
3. ✅ `docker-compose.yml` - Changed to use daphne
4. ✅ `infrastructure/docker/Dockerfile.backend` - Changed CMD to use daphne
5. ✅ `backend/apps/monitoring/consumers.py` - Enhanced error handling and logging
6. ✅ `backend/core/middleware.py` - Improved JWT authentication error handling
7. ✅ `frontend/src/hooks/useWebSocket.ts` - Enhanced error logging

---

## 📝 Quick Reference

| Command | WebSocket Support | Status |
|---------|------------------|--------|
| `python manage.py runserver` | ❌ NO | Use for HTTP only |
| `daphne core.asgi:application` | ✅ YES | **REQUIRED for WebSockets** |

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'daphne'"
**Fix:** `pip install daphne`

### Error: "Connection still fails after using daphne"
**Check:**
1. Server is actually running with daphne (check terminal output)
2. Port 8000 is not blocked
3. JWT token is valid and not expired
4. Backend logs show connection attempts

### Error: "ASGI application not found"
**Fix:** Make sure you're in the `backend` directory when running daphne

---

## ✅ Next Steps

1. **Stop current server** (if running with runserver)
2. **Install daphne:** `pip install daphne`
3. **Start with daphne:** `daphne core.asgi:application --bind 0.0.0.0 --port 8000`
4. **Test WebSocket connection** in browser
5. **Check backend logs** for connection messages

---

**Last Updated:** December 2024  
**Status:** ✅ **FIXED - Must use daphne for WebSocket support**

