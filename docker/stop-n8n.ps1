# stop-n8n.ps1
# Stops n8n (data is preserved in n8n-data folder)

Set-Location "d:\ai client\docker"

Write-Host "`nStopping n8n..." -ForegroundColor Yellow
docker compose down

Write-Host "✅ n8n stopped. Your workflows and credentials are saved in .\n8n-data\" -ForegroundColor Green
