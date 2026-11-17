# check-setup.ps1
# Run this script at any time to verify your installation status

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  AI Client Onboarding - Setup Checker" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$allGood = $true

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js: NOT FOUND" -ForegroundColor Red
    $allGood = $false
}

# Check npm
try {
    $npmVersion = npm --version 2>&1
    Write-Host "✅ npm: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm: NOT FOUND" -ForegroundColor Red
    $allGood = $false
}

# Check Python 3.11
try {
    $py311 = py -3.11 --version 2>&1
    Write-Host "✅ Python 3.11: $py311" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3.11: NOT FOUND — Download from python.org/downloads/release/python-3119/" -ForegroundColor Red
    $allGood = $false
}

# Check Docker
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker: NOT FOUND — Download from docker.com/products/docker-desktop" -ForegroundColor Red
    $allGood = $false
}

# Check n8n container
try {
    $n8nContainer = docker ps --filter "name=n8n" --format "{{.Status}}" 2>&1
    if ($n8nContainer -like "Up*") {
        Write-Host "✅ n8n container: $n8nContainer" -ForegroundColor Green
    } else {
        Write-Host "⚠️  n8n container: Not running — run start-n8n.ps1" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  n8n container: Could not check (Docker may not be running)" -ForegroundColor Yellow
}

# Check Ollama
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama: NOT FOUND — Download from ollama.com/download/windows" -ForegroundColor Red
    $allGood = $false
}

# Check Ollama API (only if Ollama is installed)
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -ErrorAction Stop
    $models = $response.models | ForEach-Object { $_.name }
    if ($models) {
        Write-Host "✅ Ollama API: Running — Models: $($models -join ', ')" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Ollama API: Running — No models pulled yet. Run: ollama pull mistral" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Ollama API: Not responding (Ollama may not be running)" -ForegroundColor Yellow
}

# Check GPU
Write-Host "`n--- GPU Info ---" -ForegroundColor Cyan
try {
    $gpu = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -like "*NVIDIA*" -or $_.Name -like "*AMD*" }
    if ($gpu) {
        Write-Host "✅ GPU: $($gpu.Name)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No NVIDIA/AMD GPU detected" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not query GPU info" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "  All checks passed! Ready to build." -ForegroundColor Green
} else {
    Write-Host "  Some items need attention (see above)." -ForegroundColor Yellow
}
Write-Host "========================================`n" -ForegroundColor Cyan
