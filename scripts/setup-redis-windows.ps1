# PowerShell script to download and run Redis for Windows manually
# This script helps you set up Redis manually without Docker or WSL

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Redis for Windows - Manual Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Redis is already running
$redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
if ($redisProcess) {
    Write-Host "Redis is already running (PID: $($redisProcess.Id))" -ForegroundColor Green
    Write-Host "You can start Celery now!" -ForegroundColor Green
    exit 0
}

# Define paths
$redisDir = "$env:USERPROFILE\redis-windows"
$redisZip = "$env:TEMP\redis-windows.zip"
$redisUrl = "https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"

# Check if Redis is already downloaded
if (Test-Path "$redisDir\redis-server.exe") {
    Write-Host "Redis found at: $redisDir" -ForegroundColor Green
    Write-Host ""
    Write-Host "Starting Redis server..." -ForegroundColor Yellow
    
    # Start Redis server in a new window
    Start-Process -FilePath "$redisDir\redis-server.exe" -WindowStyle Normal
    
    Write-Host ""
    Write-Host "Redis server started!" -ForegroundColor Green
    Write-Host "A new window opened with Redis running." -ForegroundColor Green
    Write-Host "Keep that window open while using Celery." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Now you can start Celery:" -ForegroundColor Cyan
    Write-Host "  cd backend" -ForegroundColor White
    Write-Host "  celery -A core worker --loglevel=info" -ForegroundColor White
    exit 0
}

# Download Redis
Write-Host "Step 1: Downloading Redis for Windows..." -ForegroundColor Yellow
Write-Host "URL: $redisUrl" -ForegroundColor Gray

try {
    Invoke-WebRequest -Uri $redisUrl -OutFile $redisZip -UseBasicParsing
    Write-Host "[OK] Download complete" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Download failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative: Download manually from:" -ForegroundColor Yellow
    Write-Host "  https://github.com/microsoftarchive/redis/releases" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Extract and run redis-server.exe from the extracted folder." -ForegroundColor Yellow
    exit 1
}

# Extract Redis
Write-Host ""
Write-Host "Step 2: Extracting Redis..." -ForegroundColor Yellow

if (Test-Path $redisDir) {
    Remove-Item -Path $redisDir -Recurse -Force
}

New-Item -ItemType Directory -Path $redisDir -Force | Out-Null
Expand-Archive -Path $redisZip -DestinationPath $redisDir -Force
Write-Host "[OK] Extraction complete" -ForegroundColor Green

# Clean up zip file
Remove-Item -Path $redisZip -Force

# Start Redis
Write-Host ""
Write-Host "Step 3: Starting Redis server..." -ForegroundColor Yellow
Write-Host "Redis location: $redisDir" -ForegroundColor Gray

Start-Process -FilePath "$redisDir\redis-server.exe" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  [OK] Redis is now running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "A new window opened with Redis running." -ForegroundColor Yellow
Write-Host "Keep that window open while using Celery." -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Keep the Redis window open" -ForegroundColor White
Write-Host "  2. Open a new terminal" -ForegroundColor White
Write-Host "  3. Run: cd backend" -ForegroundColor White
Write-Host "  4. Run: celery -A core worker --loglevel=info" -ForegroundColor White
Write-Host ""
Write-Host "To stop Redis: Close the Redis window or press Ctrl+C" -ForegroundColor Gray
Write-Host ""
