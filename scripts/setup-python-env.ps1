# setup-python-env.ps1
# Creates a Python 3.11 virtual environment and installs all ML dependencies
# Run this AFTER installing Python 3.11

Write-Host "`n Setting up Python 3.11 environment for fine-tuning...`n" -ForegroundColor Cyan

$envPath = "d:\ai client\fine-tuning\venv"

# Check Python 3.11
try {
    $py311 = py -3.11 --version 2>&1
    Write-Host "✅ Found: $py311" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3.11 not found. Install it from:" -ForegroundColor Red
    Write-Host "   https://www.python.org/downloads/release/python-3119/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment at: $envPath" -ForegroundColor Yellow
py -3.11 -m venv $envPath

# Activate it
$activateScript = "$envPath\Scripts\Activate.ps1"
& $activateScript

Write-Host "✅ Virtual environment created and activated`n" -ForegroundColor Green

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install PyTorch with CUDA 12.1 support (for RTX 3060)
Write-Host "`nInstalling PyTorch 2.3 with CUDA 12.1 support..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes (downloading ~2.5GB)..." -ForegroundColor Gray
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install ML libraries
Write-Host "`nInstalling Transformers, PEFT, BitsAndBytes..." -ForegroundColor Yellow
pip install transformers==4.40.0
pip install peft==0.10.0
pip install bitsandbytes==0.43.1
pip install datasets==2.19.0
pip install accelerate==0.29.3
pip install scipy
pip install sentencepiece
pip install protobuf

# Install utilities
Write-Host "`nInstalling utilities..." -ForegroundColor Yellow
pip install tqdm
pip install wandb
pip install tensorboard

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Python environment ready!" -ForegroundColor Green
Write-Host "  Location: $envPath" -ForegroundColor White
Write-Host "`n  To activate later, run:" -ForegroundColor White
Write-Host "  $activateScript" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

# Verify PyTorch + CUDA
Write-Host "Verifying PyTorch CUDA support..." -ForegroundColor Yellow
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU only\"}')"
