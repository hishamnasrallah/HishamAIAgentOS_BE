# Celery Setup for Windows

## Problem

On Windows, Celery by default uses the `prefork` pool, which spawns multiple worker processes. This can cause `MemoryError` issues due to:
- High memory usage from multiple Python processes
- Windows process model differences
- Import overhead being multiplied across processes

## Solution

Use the `solo` pool instead, which runs all tasks in a single process. This is perfect for development on Windows.

## Quick Start

### 1. Clear Redis (if needed)

If you're having issues, clear Redis cache:

```powershell
cd backend
.\scripts\clear-redis.ps1
```

### 2. Start Celery with Windows-Friendly Settings

Use the provided script:

```powershell
cd backend
.\scripts\start-celery-windows.ps1
```

Or manually:

```powershell
cd backend
celery -A core worker --loglevel=info --pool=solo --concurrency=1
```

## Command Options Explained

- `--pool=solo`: Uses a single process instead of spawning multiple workers (Windows-friendly)
- `--concurrency=1`: Ensures only one task runs at a time (safe for development)
- `--loglevel=info`: Shows informative log messages

## Stopping Celery

Press `Ctrl+C` in the terminal where Celery is running.

## Production Note

For production on Linux/Unix, you can use:
```bash
celery -A core worker --loglevel=info --concurrency=4
```

The `prefork` pool works fine on Unix-like systems and provides better performance with multiple workers.

## Troubleshooting

### MemoryError during startup
- Make sure all previous Celery processes are stopped
- Use `--pool=solo` instead of default prefork
- Reduce concurrency if needed

### Cannot connect to Redis
- Make sure Redis is running (check with `Get-Process -Name redis-server`)
- Start Redis using `.\scripts\setup-redis-windows.ps1`

### Tasks not executing
- Check Redis connection
- Verify Celery worker is running and connected
- Check logs for errors

