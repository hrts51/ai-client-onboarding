# start-n8n.ps1
# Starts n8n via Docker Compose

$dockerDir = "d:\ai client\docker"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Starting n8n via Docker" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start n8n
Set-Location $dockerDir
docker compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ n8n started successfully!" -ForegroundColor Green
    Write-Host "`n  Open in browser: http://localhost:5678" -ForegroundColor Yellow
    Write-Host "  First time? Create your admin account at the URL above.`n" -ForegroundColor Gray
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:5678"
} else {
    Write-Host "`n❌ Failed to start n8n. Check the error above." -ForegroundColor Red
}
