# Redis Setup for Windows - Celery Configuration

This guide explains how to set up Redis on Windows for Celery to work properly.

## 🚀 Quickest Solution

**If you have Docker Desktop installed** (see Option 2 below if not):

Your project already has a `docker-compose.yml` with Redis configured! 

**Start Redis only**:
```powershell
cd backend
docker compose up -d redis
```

**Verify it's running**:
```powershell
docker ps | findstr redis
```

**Check logs**:
```powershell
docker compose logs redis
```

**Stop Redis**:
```powershell
docker compose stop redis
```

That's it! Now start Celery:
```powershell
celery -A core worker --loglevel=info
```

---

## If You Don't Have Docker

See `REDIS_SETUP_WINDOWS_QUICK.md` for the easiest alternatives:

1. **Memurai** (Recommended - Native Windows, easiest setup)
2. **Docker Desktop** (Install Docker first, then use above)
3. **WSL** (If you have Windows Subsystem for Linux)
4. **Redis for Windows** (Direct download)

---

## Detailed Alternative Solutions

### Option 1: Docker (Recommended - Easiest)

If you have Docker Desktop installed:

```bash
# Start Redis in a Docker container
docker run -d --name redis-hishamos -p 6379:6379 redis:7-alpine

# Verify it's running
docker ps

# Check Redis logs
docker logs redis-hishamos
```

**To stop Redis:**
```bash
docker stop redis-hishamos
```

**To start Redis again:**
```bash
docker start redis-hishamos
```

**To remove the container:**
```bash
docker rm -f redis-hishamos
```

### Option 2: WSL (Windows Subsystem for Linux)

If you have WSL installed:

```bash
# Open WSL terminal
wsl

# Install Redis
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo service redis-server start

# Verify it's running
redis-cli ping
# Should return: PONG
```

**To start Redis on boot:**
```bash
sudo systemctl enable redis-server
```

### Option 3: Memurai (Native Windows Redis)

Memurai is a Redis-compatible server for Windows:

1. **Download Memurai**: https://www.memurai.com/get-memurai
2. **Install** the MSI package
3. **Start the service**:
   ```powershell
   # Open PowerShell as Administrator
   Start-Service Memurai
   ```

4. **Verify it's running**:
   ```powershell
   Get-Service Memurai
   ```

Memurai runs on port 6379 by default, same as Redis.

### Option 4: Use Cloud Redis (For Production)

For production environments, consider:
- **Redis Cloud**: https://redis.com/cloud/
- **Azure Cache for Redis**: https://azure.microsoft.com/en-us/services/cache/
- **AWS ElastiCache**: https://aws.amazon.com/elasticache/

Update your `.env` file:
```env
CELERY_BROKER_URL=redis://your-redis-url:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-url:6379/1
```

## Verify Redis is Running

### Using redis-cli (if installed)

```bash
redis-cli ping
```

Should return: `PONG`

### Using Python

```bash
python
```

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.ping()
# Should return: True
```

### Using telnet

```bash
telnet localhost 6379
```

If connected, Redis is running. Press Ctrl+C to exit.

### Using PowerShell

```powershell
Test-NetConnection -ComputerName localhost -Port 6379
```

Look for `TcpTestSucceeded : True`

## After Starting Redis

1. **Verify Celery can connect**:
   ```bash
   cd backend
   celery -A core worker --loglevel=info
   ```

   You should see:
   ```
   -------------- celery@HOSTNAME v5.3.6 (emerald-rush)
   ...
   [tasks]
     . apps.agents.tasks.execute_agent_task_sync
     ...
   ```

   No connection errors!

2. **Test Celery task**:
   ```bash
   python manage.py shell
   ```

   ```python
   from core.celery import debug_task
   result = debug_task.delay()
   print(result.get())
   ```

## Troubleshooting

### Error: "Error 10061 - Connection Refused"

**Cause**: Redis is not running or not accessible on port 6379.

**Solutions**:
1. Start Redis using one of the options above
2. Check if another service is using port 6379:
   ```powershell
   netstat -ano | findstr :6379
   ```
3. Check Windows Firewall isn't blocking the connection

### Error: "Address already in use"

**Cause**: Another Redis instance is already running on port 6379.

**Solutions**:
1. Find and stop the other instance
2. Change Redis port in your `.env`:
   ```env
   CELERY_BROKER_URL=redis://localhost:6380/0
   CELERY_RESULT_BACKEND=redis://localhost:6380/1
   ```

### Celery Still Can't Connect

1. **Check Redis is actually running**:
   ```powershell
   # For Docker
   docker ps | findstr redis
   
   # For Memurai
   Get-Service Memurai
   ```

2. **Check Celery configuration**:
   ```bash
   python manage.py shell
   ```
   ```python
   from django.conf import settings
   print(settings.CELERY_BROKER_URL)
   print(settings.CELERY_RESULT_BACKEND)
   ```

3. **Test Redis connection manually**:
   ```python
   import redis
   r = redis.Redis.from_url('redis://localhost:6379/0')
   r.ping()
   ```

## Development Without Redis (Not Recommended)

If you absolutely cannot run Redis, you can use in-memory broker for development:

**Warning**: Tasks will be lost on restart and won't persist across workers.

Create `backend/core/celery_dev.py`:

```python
from celery import Celery
from kombu import Queue

app = Celery('hishamos')
app.conf.task_always_eager = True  # Execute tasks synchronously
app.conf.task_eager_propagates = True
```

Then use:
```bash
CELERY_ALWAYS_EAGER=True celery -A core worker
```

**Better**: Just install Docker and use the Docker option above.

## Recommended Setup for Development

**Best Practice**: Use Docker for Redis

1. **Install Docker Desktop**: https://www.docker.com/products/docker-desktop

2. **Create a docker-compose.yml** in project root:
   ```yaml
   version: '3.8'
   
   services:
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
       volumes:
         - redis-data:/data
       command: redis-server --appendonly yes
   
   volumes:
     redis-data:
   ```

3. **Start Redis**:
   ```bash
   docker-compose up -d redis
   ```

4. **Start Celery**:
   ```bash
   celery -A core worker --loglevel=info
   ```

## Configuration Files

Your Redis configuration is in `backend/core/settings/base.py`:

```python
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/1')
```

You can override these in your `.env` file if needed.

## Next Steps

Once Redis is running:

1. ✅ Start Celery worker: `celery -A core worker --loglevel=info`
2. ✅ (Optional) Start Celery beat for scheduled tasks: `celery -A core beat --loglevel=info`
3. ✅ Test your tasks work properly
4. ✅ Continue with OpenRouter setup if needed

## Additional Resources

- **Redis Documentation**: https://redis.io/docs/
- **Celery with Redis**: https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html
- **Docker Redis**: https://hub.docker.com/_/redis
- **Memurai Docs**: https://docs.memurai.com/

