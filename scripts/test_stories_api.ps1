$body = @{
    email = 'admin@hishamos.com'
    password = 'Amman123'
} | ConvertTo-Json

Write-Host "Logging in..."
$loginResponse = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/auth/login/' -Method Post -Body $body -ContentType 'application/json'

$headers = @{
    Authorization = "Bearer $($loginResponse.access)"
}

Write-Host "`n=== Test 1: /api/v1/projects/stories/ (expected path) ==="
try {
    $test1 = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/projects/stories/' -Headers $headers
    Write-Host "✅ WORKS at /api/v1/projects/stories/"
    $test1 | ConvertTo-Json -Depth 2
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Response.StatusCode.value__)"
}

Write-Host "`n=== Test 2: /stories/ (root level) ==="
try {
    $test2 = Invoke-RestMethod -Uri 'http://localhost:8000/stories/' -Headers $headers
    Write-Host "✅ WORKS at /stories/"
    $test2 | ConvertTo-Json -Depth 2
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Response.StatusCode.value__)"
}

Write-Host "`n=== Test 3: /api/v1/stories/ ==="
try {
    $test3 = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/stories/' -Headers $headers
    Write-Host "✅ WORKS at /api/v1/stories/"
    $test3 | ConvertTo-Json -Depth 2
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Response.StatusCode.value__)"
}

Write-Host "`n=== Test 4: /api/v1/stories/?project=cb3dd7f3-a16c-4c59-a81e-a6484b45149c ==="
try {
    $test4 = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/stories/?project=cb3dd7f3-a16c-4c59-a81e-a6484b45149c' -Headers $headers
    Write-Host "✅ WORKS with filter!"
    Write-Host "Count: $($test4.count)"
    $test4.results | ForEach-Object { Write-Host "  - $($_.title) (Project: $($_.project))" }
} catch {
    Write-Host "❌ FAILED: $($_.Exception.Response.StatusCode.value__)"
}
