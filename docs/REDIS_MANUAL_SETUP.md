# Manual Redis Setup for Windows

This guide helps you download and run Redis manually on Windows without Docker or WSL.

## Option 1: Automated Script (Easiest)

We've created a PowerShell script to automate the download and setup:

```powershell
cd backend
.\scripts\setup-redis-windows.ps1
```

This script will:
1. Download Redis for Windows
2. Extract it to `%USERPROFILE%\redis-windows`
3. Start Redis server in a new window

**Keep the Redis window open** while you run Celery!

---

## Option 2: Manual Download

### Step 1: Download Redis

1. Go to: https://github.com/microsoftarchive/redis/releases
2. Download the latest `Redis-x64-*.zip` file (e.g., `Redis-x64-3.0.504.zip`)

### Step 2: Extract Redis

1. Create a folder: `C:\redis` (or anywhere you prefer)
2. Extract the ZIP file contents to this folder
3. You should see `redis-server.exe` in the folder

### Step 3: Run Redis

**Option A: Run in PowerShell** (recommended for testing):
```powershell
cd C:\redis
.\redis-server.exe
```

**Option B: Run in Command Prompt**:
```cmd
cd C:\redis
redis-server.exe
```

**Option C: Create a shortcut**:
1. Right-click `redis-server.exe`
2. Create shortcut
3. Double-click to run

**Keep the Redis window/tab open!** Redis runs in the foreground.

### Step 4: Verify Redis is Running

Open a **new** PowerShell/Command Prompt window and test:

```powershell
# If you have redis-cli in the same folder
cd C:\redis
.\redis-cli.exe ping
```

Should return: `PONG`

Or test from Python:
```powershell
python
```

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()
# Should return: True
```

### Step 5: Start Celery

In a **new** terminal window (keep Redis running):

```powershell
cd backend
celery -A core worker --loglevel=info
```

You should see Celery start without connection errors!

---

## Running Redis as a Background Service (Advanced)

If you want Redis to run in the background without keeping a window open:

### Using NSSM (Non-Sucking Service Manager)

1. **Download NSSM**: https://nssm.cc/download
2. **Extract** NSSM to a folder (e.g., `C:\nssm`)
3. **Install Redis as service**:
   ```powershell
   # Run PowerShell as Administrator
   cd C:\nssm\win64
   .\nssm.exe install Redis "C:\redis\redis-server.exe"
   ```
4. **Start the service**:
   ```powershell
   Start-Service Redis
   ```
5. **Verify**:
   ```powershell
   Get-Service Redis
   ```

Now Redis will start automatically with Windows and run in the background!

---

## Quick Commands

### Start Redis Manually
```powershell
cd C:\redis
.\redis-server.exe
```

### Stop Redis
- Close the Redis window, or
- Press `Ctrl+C` in the Redis window

### Test Redis Connection
```powershell
cd C:\redis
.\redis-cli.exe ping
# Should return: PONG
```

### Start Celery (after Redis is running)
```powershell
cd backend
celery -A core worker --loglevel=info
```

---

## Troubleshooting

### "Redis is already running"
If you see this error, Redis might already be running. Check:
```powershell
Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
```

If it's running, you can start Celery directly. If you want to stop it:
```powershell
Stop-Process -Name "redis-server" -Force
```

### "Port 6379 is already in use"
Another process is using port 6379. Find and stop it:
```powershell
netstat -ano | findstr :6379
# Note the PID (last column)
taskkill /PID <PID> /F
```

### "redis-server.exe not found"
Make sure you extracted the ZIP file and are running from the correct folder. Check:
```powershell
Test-Path C:\redis\redis-server.exe
```

### Celery Still Can't Connect

1. **Verify Redis is running**:
   ```powershell
   Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
   ```

2. **Test connection**:
   ```powershell
   python
   ```
   ```python
   import redis
   r = redis.Redis(host='localhost', port=6379, db=0)
   r.ping()  # Should return True
   ```

3. **Check Celery config**:
   ```powershell
   python manage.py shell
   ```
   ```python
   from django.conf import settings
   print(settings.CELERY_BROKER_URL)
   # Should be: redis://localhost:6379/0
   ```

---

## Recommended Setup for Development

1. **Download Redis** to a permanent location (e.g., `C:\redis`)
2. **Create a desktop shortcut** to `redis-server.exe` for easy starting
3. **Start Redis** before running Celery
4. **Keep Redis window open** while developing

For production, consider using:
- Docker (with docker-compose)
- Memurai (Windows service)
- Cloud Redis (Redis Cloud, Azure Cache, etc.)

---

## Next Steps

Once Redis is running:

✅ Start Celery: `celery -A core worker --loglevel=info`
✅ (Optional) Start Celery Beat: `celery -A core beat --loglevel=info`
✅ Test your tasks
✅ Continue with OpenRouter setup if needed


