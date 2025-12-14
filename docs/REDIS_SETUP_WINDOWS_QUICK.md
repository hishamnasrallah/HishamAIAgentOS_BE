# Quick Redis Setup for Windows - No Docker Required

Since you don't have Docker installed, here are the **easiest options** to get Redis running:

## Option 1: Memurai (Recommended - Easiest Native Windows Solution)

Memurai is a Redis-compatible server built for Windows. It's the easiest native solution.

### Steps:

1. **Download Memurai**:
   - Go to: https://www.memurai.com/get-memurai
   - Download the free Developer Edition (Windows MSI installer)

2. **Install Memurai**:
   - Run the downloaded MSI installer
   - Follow the installation wizard (defaults are fine)
   - It will install as a Windows service

3. **Verify it's running**:
   ```powershell
   Get-Service Memurai
   ```
   Should show: `Running`

4. **Test the connection**:
   ```powershell
   # If you have redis-cli installed, test with:
   redis-cli ping
   # Should return: PONG
   ```

5. **Start Celery**:
   ```powershell
   cd backend
   celery -A core worker --loglevel=info
   ```

Memurai runs on port 6379 by default (same as Redis), so your Celery configuration will work automatically!

---

## Option 2: Install Docker Desktop (If you want to use docker-compose)

If you prefer using Docker (recommended for development):

1. **Download Docker Desktop**:
   - Go to: https://www.docker.com/products/docker-desktop
   - Download Docker Desktop for Windows

2. **Install Docker Desktop**:
   - Run the installer
   - Restart your computer when prompted

3. **Start Docker Desktop**:
   - Launch Docker Desktop from Start Menu
   - Wait for it to fully start (whale icon in system tray)

4. **Start Redis**:
   ```powershell
   cd backend
   docker compose up -d redis
   ```

5. **Verify Redis is running**:
   ```powershell
   docker ps
   ```

6. **Start Celery**:
   ```powershell
   celery -A core worker --loglevel=info
   ```

---

## Option 3: WSL (Windows Subsystem for Linux)

If you have WSL installed or want to install it:

1. **Install WSL** (if not installed):
   ```powershell
   # Run PowerShell as Administrator
   wsl --install
   ```
   Restart your computer after installation.

2. **Open WSL terminal**:
   ```powershell
   wsl
   ```

3. **Install Redis in WSL**:
   ```bash
   sudo apt-get update
   sudo apt-get install redis-server
   ```

4. **Start Redis**:
   ```bash
   sudo service redis-server start
   ```

5. **Verify Redis is running**:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

6. **Start Celery** (from Windows PowerShell):
   ```powershell
   cd backend
   celery -A core worker --loglevel=info
   ```

---

## Option 4: Download Redis for Windows (Official Port)

**Note**: This is less maintained but works.

1. **Download Redis for Windows**:
   - Go to: https://github.com/microsoftarchive/redis/releases
   - Download the latest `Redis-x64-*.zip` file

2. **Extract and Run**:
   - Extract the ZIP file
   - Run `redis-server.exe` from the extracted folder
   - Keep the terminal window open (Redis runs in foreground)

3. **Start Celery** (in another terminal):
   ```powershell
   cd backend
   celery -A core worker --loglevel=info
   ```

---

## Quick Test After Setup

Once Redis is running, verify Celery can connect:

```powershell
cd backend
celery -A core worker --loglevel=info
```

You should see:
```
-------------- celery@HOSTNAME v5.3.6 (emerald-rush)
--- ***** -----
...
[tasks]
  . apps.agents.tasks.execute_agent_task_sync
  ...
```

**No connection errors!** ✅

---

## Recommendation

**For quick setup**: Use **Option 1 (Memurai)** - it's the easiest native Windows solution, installs as a service, and works out of the box.

**For development consistency**: Use **Option 2 (Docker Desktop)** - it matches production environments and makes it easy to manage multiple services.

---

## Troubleshooting

### "Connection Refused" Error

1. **Check if Redis/Memurai is running**:
   ```powershell
   # For Memurai
   Get-Service Memurai
   
   # For Docker
   docker ps
   
   # For WSL
   wsl redis-cli ping
   ```

2. **Check if port 6379 is available**:
   ```powershell
   netstat -ano | findstr :6379
   ```

3. **Verify Celery configuration**:
   ```powershell
   python manage.py shell
   ```
   ```python
   from django.conf import settings
   print(settings.CELERY_BROKER_URL)
   # Should be: redis://localhost:6379/0
   ```

### Still Having Issues?

Check the full troubleshooting guide in `REDIS_SETUP_WINDOWS.md`


