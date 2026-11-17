# LoRA Fine-tuning — Mistral 7B for Client Onboarding

This module fine-tunes Mistral 7B Instruct v0.2 using LoRA on client onboarding data.

## Requirements

- NVIDIA GPU with 6GB+ VRAM (RTX 3060 or better)
- CUDA 12.1
- Python 3.11

## Setup

```powershell
# Create and activate virtual environment
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1

# Install PyTorch with CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install remaining dependencies
pip install -r requirements.txt
```

## Training Data

`training_data.jsonl` contains 5 onboarding examples in this format:

```json
{
  "instruction": "Analyze this client onboarding submission...",
  "input": "Name: John Smith\nCompany: ...",
  "output": "**Client Profile:**\n..."
}
```

Add more examples to improve model quality. 50-100 examples gives significantly better results.

## Run Training

```powershell
python train.py
```

Training takes approximately 20-40 minutes on an RTX 3060.

## Serve Fine-tuned Model

After training completes:

```powershell
ollama create onboarding-mistral -f output/mistral-onboarding-lora/Modelfile
ollama run onboarding-mistral "Analyze this client..."
```

Then update the n8n workflow's Mistral node URL to use `onboarding-mistral` instead of `mistral`.

## LoRA Configuration

| Parameter | Value |
|---|---|
| Rank (r) | 16 |
| Alpha | 32 |
| Dropout | 0.05 |
| Target modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
| Quantization | 4-bit NF4 |
| Epochs | 3 |
| Learning rate | 2e-4 |
