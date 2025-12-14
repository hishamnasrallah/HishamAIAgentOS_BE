# PowerShell script to clear Redis cache
# This helps reset Redis if you're having issues

Write-Host "Clearing Redis cache..." -ForegroundColor Yellow

$redisCli = "$env:USERPROFILE\redis-windows\redis-cli.exe"

if (Test-Path $redisCli) {
    # Try to clear all databases
    & $redisCli FLUSHALL
    Write-Host "[OK] Redis cache cleared" -ForegroundColor Green
} else {
    Write-Host "[WARNING] redis-cli.exe not found at: $redisCli" -ForegroundColor Yellow
    Write-Host "If Redis is running, you can manually run:" -ForegroundColor Yellow
    Write-Host "  redis-cli FLUSHALL" -ForegroundColor White
}

