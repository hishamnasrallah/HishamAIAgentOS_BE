---
title: "WebSocket Server Requirement - CRITICAL"
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

# WebSocket Server Requirement - CRITICAL

**Date:** December 2024  
**Status:** ⚠️ **IMPORTANT INFORMATION**

---

## 🚨 Critical Issue

WebSocket connections are failing because **Django must be run with an ASGI server**, not the standard `runserver` command.

### The Problem

Django's standard `python manage.py runserver` **does NOT support WebSockets**. It only supports HTTP requests.

**Symptoms:**
- WebSocket connections fail immediately
- `readyState: 3` (CLOSED) immediately after connection attempt
- No error messages in Django console
- Connection closes before `accept()` is called

---

## ✅ Solution

### Use Daphne ASGI Server

Django Channels requires an ASGI server. The project uses **Daphne**.

**Correct Command:**
```bash
cd backend
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

**Or with manage.py:**
```bash
cd backend
python manage.py runserver  # This WON'T work for WebSockets
```

**For WebSockets, you MUST use:**
```bash
cd backend
daphne core.asgi:application --bind 0.0.0.0 --port 8000
```

---

## 📋 Verification

### Check if Server Supports WebSockets

1. **Check Process:**
   ```bash
   # Windows PowerShell
   Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*daphne*"}
   ```

2. **Check Logs:**
   - If using `runserver`: No WebSocket support
   - If using `daphne`: Should see ASGI application loading

3. **Test Connection:**
   - Try connecting to WebSocket
   - Check browser console for connection errors
   - Check backend logs for connection attempts

---

## 🔧 Setup Instructions

### Development

1. **Install Daphne** (already in requirements):
   ```bash
   pip install daphne
   ```

2. **Run Server:**
   ```bash
   cd backend
   daphne core.asgi:application --bind 0.0.0.0 --port 8000
   ```

3. **Or use manage.py with daphne:**
   ```bash
   cd backend
   python manage.py runserver  # This uses runserver (NO WebSocket support)
   # Instead, use:
   daphne core.asgi:application --bind 0.0.0.0 --port 8000
   ```

### Production

Use Daphne or Uvicorn with proper process management (systemd, supervisor, etc.)

---

## 🐛 Common Errors

### Error: "Connection closed unexpectedly"
**Cause:** Server running with `runserver` instead of `daphne`  
**Fix:** Stop server and restart with `daphne`

### Error: "Module not found: daphne"
**Cause:** Daphne not installed  
**Fix:** `pip install daphne`

### Error: "ASGI application not found"
**Cause:** Wrong ASGI application path  
**Fix:** Use `core.asgi:application`

---

## 📝 Quick Reference

| Command | WebSocket Support | Use Case |
|---------|------------------|----------|
| `python manage.py runserver` | ❌ NO | HTTP only |
| `daphne core.asgi:application` | ✅ YES | Development with WebSockets |
| `uvicorn core.asgi:application` | ✅ YES | Alternative ASGI server |

---

## ✅ Verification Checklist

- [ ] Server is running with `daphne` (not `runserver`)
- [ ] Daphne is installed (`pip list | grep daphne`)
- [ ] ASGI application is configured (`core.asgi:application`)
- [ ] Port 8000 is accessible
- [ ] WebSocket URL is correct (`ws://localhost:8000/ws/dashboard/`)
- [ ] JWT token is included in URL
- [ ] Backend logs show connection attempts

---

## 🔧 Files Updated

1. ✅ `backend/requirements/base.txt` - Added `daphne==4.0.0`
2. ✅ `README.md` - Updated with daphne instructions
3. ✅ `docker-compose.yml` - Changed to use daphne
4. ✅ `infrastructure/docker/Dockerfile.backend` - Changed CMD to use daphne

## 📝 Installation

If daphne is not installed:
```bash
pip install daphne
# Or
pip install -r backend/requirements/base.txt
```

---

**Last Updated:** December 2024  
**Status:** ⚠️ **CRITICAL - MUST USE DAPHNE FOR WEBSOCKETS**  
**Fixed By:** AI Agent (Auto)

