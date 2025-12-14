# PowerShell script to start Celery worker with Windows-friendly settings
# Windows has issues with prefork pool, so we use solo pool or reduce concurrency

Write-Host "Starting Celery worker for Windows..." -ForegroundColor Cyan
Write-Host ""

# Check if Redis is running
$redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
if (-not $redisProcess) {
    Write-Host "[ERROR] Redis is not running!" -ForegroundColor Red
    Write-Host "Please start Redis first using: .\scripts\setup-redis-windows.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Redis is running (PID: $($redisProcess.Id))" -ForegroundColor Green
Write-Host ""

# Change to backend directory (scripts folder is in backend/scripts, so go up one level)
$backendDir = Split-Path -Parent $PSScriptRoot
Set-Location -Path $backendDir

# Start Celery with Windows-friendly settings
# Using solo pool (single process) instead of prefork to avoid memory issues
Write-Host "Starting Celery worker with solo pool (Windows-friendly)..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

celery -A core worker --loglevel=info --pool=solo --concurrency=1

