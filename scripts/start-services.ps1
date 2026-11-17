# start-services.ps1
# Starts Ollama (if not running) and n8n in separate windows

Write-Host "`n Starting AI Client Onboarding Services...`n" -ForegroundColor Cyan

# Start Ollama serve (if not already running)
$ollamaRunning = $false
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -ErrorAction Stop
    $ollamaRunning = $true
    Write-Host "✅ Ollama is already running" -ForegroundColor Green
} catch {
    Write-Host "Starting Ollama..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "ollama serve" -WindowStyle Normal
    Start-Sleep -Seconds 3
    Write-Host "✅ Ollama started" -ForegroundColor Green
}

# Start n8n
Write-Host "Starting n8n..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "n8n start" -WindowStyle Normal
Start-Sleep -Seconds 5

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Services started!" -ForegroundColor Green
Write-Host "  n8n UI:      http://localhost:5678" -ForegroundColor White
Write-Host "  Ollama API:  http://localhost:11434" -ForegroundColor White
Write-Host "========================================`n" -ForegroundColor Cyan

# Open n8n in browser
Start-Process "http://localhost:5678"
