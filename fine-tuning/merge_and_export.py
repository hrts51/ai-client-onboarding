"""
Merge LoRA weights into base model and export for Ollama
Run this after train.py completes
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_MODEL  = "mistralai/Mistral-7B-Instruct-v0.2"
LORA_DIR    = os.path.join(SCRIPT_DIR, "output", "mistral-onboarding-lora")
MERGED_DIR  = os.path.join(SCRIPT_DIR, "output", "mistral-onboarding-merged")

print("=" * 60)
print("  Merging LoRA weights into base model")
print("=" * 60)

# Load base model in float16 (not quantized — needed for merging)
print("\nLoading base model for merging (this takes a few minutes)...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="cpu",   # Merge on CPU to avoid VRAM limits
    trust_remote_code=True,
)

# Load and merge LoRA weights
print("Merging LoRA adapters...")
model = PeftModel.from_pretrained(model, LORA_DIR)
model = model.merge_and_unload()

# Save merged model
print(f"Saving merged model to: {MERGED_DIR}")
os.makedirs(MERGED_DIR, exist_ok=True)
model.save_pretrained(MERGED_DIR)
tokenizer.save_pretrained(MERGED_DIR)

print("\nMerge complete!")
print("\nNext step — convert to GGUF for Ollama:")
print("  pip install llama-cpp-python")
print(f"  python -m llama_cpp.server --model {MERGED_DIR}")
print("\nOr use the merged model directly in n8n via a local API server.")
