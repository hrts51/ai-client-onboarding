"""
LoRA Fine-tuning Script for Mistral 7B
Project: AI Client Onboarding Automation

This script fine-tunes Mistral 7B Instruct v0.2 using LoRA (Low-Rank Adaptation)
on client onboarding data to produce more consistent, domain-specific responses.

Requirements:
- Python 3.11
- NVIDIA GPU with 6GB+ VRAM (RTX 3060 or better)
- CUDA 12.1
- Run: pip install -r requirements.txt first

Usage:
    python train.py
"""

import os
import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from tqdm import tqdm

# ─── Configuration ───────────────────────────────────────────────────────────

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
DATA_PATH  = "training_data.jsonl"
OUTPUT_DIR = "output/mistral-onboarding-lora"

LORA_CONFIG = {
    "r": 16,                    # LoRA rank
    "lora_alpha": 32,           # LoRA alpha
    "lora_dropout": 0.05,       # Dropout
    "target_modules": [         # Modules to apply LoRA to
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
}

TRAINING_CONFIG = {
    "num_train_epochs": 3,
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 4,
    "learning_rate": 2e-4,
    "max_seq_length": 1024,
    "warmup_steps": 10,
    "logging_steps": 5,
    "save_steps": 50,
    "fp16": True,               # Use FP16 for 6GB VRAM
}

# ─── Load Training Data ───────────────────────────────────────────────────────

def load_training_data(path):
    """Load JSONL training data and format as Mistral instruct prompts."""
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line.strip())
            # Format as Mistral instruct template
            prompt = f"<s>[INST] {item['instruction']}\n\n{item['input']} [/INST] {item['output']}</s>"
            data.append({"text": prompt})
    print(f"Loaded {len(data)} training examples")
    return Dataset.from_list(data)

# ─── Load Model ──────────────────────────────────────────────────────────────

def load_model_and_tokenizer():
    """Load Mistral 7B in 4-bit quantization for 6GB VRAM."""
    print(f"Loading model: {MODEL_NAME}")
    print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB" if torch.cuda.is_available() else "")

    # 4-bit quantization config (fits in 6GB VRAM)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    model = prepare_model_for_kbit_training(model)
    return model, tokenizer

# ─── Apply LoRA ───────────────────────────────────────────────────────────────

def apply_lora(model):
    """Apply LoRA adapters to the model."""
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_CONFIG["r"],
        lora_alpha=LORA_CONFIG["lora_alpha"],
        lora_dropout=LORA_CONFIG["lora_dropout"],
        target_modules=LORA_CONFIG["target_modules"],
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model

# ─── Tokenize Dataset ─────────────────────────────────────────────────────────

def tokenize_dataset(dataset, tokenizer, max_length=1024):
    """Tokenize the training data."""
    def tokenize(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_tensors="pt",
        )
    return dataset.map(tokenize, batched=True, remove_columns=["text"])

# ─── Train ────────────────────────────────────────────────────────────────────

def train(model, tokenizer, dataset):
    """Run the fine-tuning training loop."""
    from transformers import Trainer, DataCollatorForLanguageModeling

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=TRAINING_CONFIG["num_train_epochs"],
        per_device_train_batch_size=TRAINING_CONFIG["per_device_train_batch_size"],
        gradient_accumulation_steps=TRAINING_CONFIG["gradient_accumulation_steps"],
        learning_rate=TRAINING_CONFIG["learning_rate"],
        fp16=TRAINING_CONFIG["fp16"],
        warmup_steps=TRAINING_CONFIG["warmup_steps"],
        logging_steps=TRAINING_CONFIG["logging_steps"],
        save_steps=TRAINING_CONFIG["save_steps"],
        save_total_limit=2,
        report_to="none",
        dataloader_pin_memory=False,
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
    )

    print("\nStarting fine-tuning...")
    trainer.train()
    print(f"\nTraining complete. Model saved to: {OUTPUT_DIR}")

# ─── Export for Ollama ────────────────────────────────────────────────────────

def create_modelfile():
    """Create an Ollama Modelfile to serve the fine-tuned model."""
    modelfile = f"""FROM mistral
ADAPTER {os.path.abspath(OUTPUT_DIR)}

SYSTEM You are an expert AI assistant specialized in client onboarding for professional services companies. You analyze client submissions and provide structured assessments including client profiles, project requirements, priority levels, and important notes.
"""
    with open(os.path.join(OUTPUT_DIR, "Modelfile"), "w") as f:
        f.write(modelfile)
    print(f"Modelfile created at: {OUTPUT_DIR}/Modelfile")
    print("\nTo serve in Ollama, run:")
    print(f"  ollama create onboarding-mistral -f {OUTPUT_DIR}/Modelfile")
    print("  ollama run onboarding-mistral")

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Mistral 7B LoRA Fine-tuning — Client Onboarding")
    print("=" * 60)

    # Check GPU
    if not torch.cuda.is_available():
        print("WARNING: No GPU detected. Training on CPU will be very slow.")
        print("Recommended: NVIDIA RTX 3060 or better with CUDA 12.1")
    else:
        print(f"GPU detected: {torch.cuda.get_device_name(0)}")

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data
    dataset = load_training_data(DATA_PATH)

    # Load model
    model, tokenizer = load_model_and_tokenizer()

    # Apply LoRA
    model = apply_lora(model)

    # Tokenize
    tokenized_dataset = tokenize_dataset(dataset, tokenizer)

    # Train
    train(model, tokenizer, tokenized_dataset)

    # Create Ollama Modelfile
    create_modelfile()

    print("\nDone! Fine-tuned model is ready.")
