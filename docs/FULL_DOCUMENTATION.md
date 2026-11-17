# AI Client Onboarding Automation — Full Documentation

**Project:** AI-Powered Automatic Client Onboarding Automation  
**Author:** Ankit Kumar  
**GitHub:** https://github.com/hrts51/ai-client-onboarding  
**Stack:** n8n · Mistral 7B · Ollama · Docker · Python 3.11 · PEFT · Google Workspace · Slack

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Project Structure](#4-project-structure)
5. [Installation & Setup](#5-installation--setup)
6. [Workflow Explanation](#6-workflow-explanation)
7. [AI Model — Mistral 7B](#7-ai-model--mistral-7b)
8. [LoRA Fine-tuning](#8-lora-fine-tuning)
9. [Deployment](#9-deployment)
10. [API Reference](#10-api-reference)
11. [Troubleshooting](#11-troubleshooting)
12. [Interview Q&A](#12-interview-qa)

---

## 1. Project Overview

This project automates the complete client onboarding process using AI-powered workflow automation. The system eliminates repetitive manual tasks including:

- Reading and summarizing client submissions
- Creating client records in spreadsheets
- Sending welcome emails
- Notifying the internal team

**Key Innovation:** Instead of using expensive cloud AI APIs (OpenAI, Anthropic), this system runs Mistral 7B locally on a consumer GPU via Ollama, reducing recurring AI costs to zero.

### What Happens When a Client Submits the Form

```
Client submits Google Form
         ↓ (within 60 seconds)
n8n detects new response
         ↓
Client data extracted and validated
         ↓
Mistral 7B analyzes client (locally, free)
         ↓ (parallel execution)
┌────────────────────────────────────────┐
│  Google Sheets ← client record saved  │
│  Gmail ← welcome email sent           │
│  Slack ← team notified                │
└────────────────────────────────────────┘
         ↓
Done — total time under 30 seconds
```

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                          │
│                                                         │
│  Google Form → Google Sheets (Form Responses)           │
└─────────────────────────┬───────────────────────────────┘
                          │ polls every 60s
┌─────────────────────────▼───────────────────────────────┐
│              n8n (Docker Container)                     │
│              Port: 5678                                 │
│                                                         │
│  Node 1: Google Sheets Trigger                          │
│  Node 2: Extract & Validate Data (JavaScript)           │
│  Node 3: HTTP Request → Ollama API                      │
│  Node 4: Merge AI Analysis (JavaScript)                 │
│  Node 5: Save to Google Sheets                          │
│  Node 6: Gmail — Send Welcome Email                     │
│  Node 7: Slack — Team Notification                      │
└──────────────┬──────────────────────────────────────────┘
               │ host.docker.internal:11434
┌──────────────▼──────────────────────────────────────────┐
│              Ollama (Windows Host)                      │
│              Port: 11434                                │
│                                                         │
│  Model: mistral:latest (Q4_K_M, 4.4GB)                 │
│  Hardware: RTX 3060 Laptop GPU (6GB VRAM)               │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

| Step | Input | Output |
|------|-------|--------|
| Form Trigger | New Google Sheet row | Raw form data JSON |
| Extract & Validate | Raw form data | Structured client object |
| Mistral AI | Client data prompt | AI analysis text |
| Merge Analysis | Client data + AI text | Complete client record |
| Google Sheets | Complete record | New row appended |
| Gmail | Client email + data | HTML welcome email sent |
| Slack | Client data + AI analysis | Channel notification |

---

## 3. Technology Stack

### Core Infrastructure
| Technology | Version | Purpose |
|---|---|---|
| n8n | 2.47.7 | Workflow automation engine |
| Docker Desktop | 29.9.3 | Container runtime for n8n |
| Docker Compose | 5.7.0 | Container orchestration |

### AI & ML
| Technology | Version | Purpose |
|---|---|---|
| Mistral 7B Instruct v0.2 | Q4_K_M | Local language model |
| Ollama | 0.40.16 | Local LLM deployment |
| Python | 3.11.9 | Fine-tuning runtime |
| PyTorch | 2.5.1+cu121 | Deep learning framework |
| Hugging Face Transformers | 4.40.0 | Model loading & training |
| PEFT | 0.10.0 | LoRA fine-tuning framework |
| BitsAndBytes | 0.43.1 | 4-bit quantization |
| Datasets | 2.19.0 | Training data handling |
| Accelerate | 0.29.3 | Distributed training utility |

### Integrations
| Technology | Purpose |
|---|---|
| Google Forms | Client data collection |
| Google Sheets API | Data storage & trigger |
| Google Drive API | Required by Sheets API |
| Gmail API | Automated email sending |
| Slack API | Team notifications |

### Hardware
| Component | Spec |
|---|---|
| CPU | AMD Ryzen 7 5800H |
| GPU | NVIDIA RTX 3060 Laptop (6GB VRAM) |
| RAM | 16GB |
| OS | Windows 11 |

---

## 4. Project Structure

```
ai-client-onboarding/
│
├── docker/
│   ├── docker-compose.yml              # n8n Docker configuration
│   ├── .env                            # Environment variables
│   ├── n8n-data/                       # n8n persistent data (gitignored)
│   ├── start-n8n.ps1                   # Start n8n script
│   └── stop-n8n.ps1                    # Stop n8n script
│
├── n8n-workflows/
│   ├── onboarding-workflow.json        # Webhook-based workflow
│   └── onboarding-workflow-googleform.json  # Google Form workflow (active)
│
├── fine-tuning/
│   ├── train.py                        # LoRA fine-tuning script
│   ├── merge_and_export.py             # Merge LoRA weights script
│   ├── training_data.jsonl             # Training examples (5 samples)
│   ├── requirements.txt                # Python dependencies
│   ├── venv/                           # Python virtual environment (gitignored)
│   ├── output/                         # Fine-tuned model output (gitignored)
│   └── README.md                       # Fine-tuning guide
│
├── scripts/
│   ├── check-setup.ps1                 # Verify all installations
│   ├── setup-python-env.ps1            # Set up Python ML environment
│   └── start-services.ps1             # Start all services
│
├── docs/
│   ├── index.html                      # HTML project documentation
│   ├── SETUP_GUIDE.md                  # Setup guide
│   ├── FULL_DOCUMENTATION.md           # This file
│   └── INTERVIEW_QA.md                 # Interview preparation
│
├── .gitignore
└── README.md
```

---

## 5. Installation & Setup

### Prerequisites

1. **Docker Desktop** — https://www.docker.com/products/docker-desktop/
2. **Ollama** — https://ollama.com/download/windows
3. **Python 3.11.9** — https://www.python.org/downloads/release/python-3119/

### Step 1: Clone Repository
```bash
git clone https://github.com/hrts51/ai-client-onboarding.git
cd ai-client-onboarding
```

### Step 2: Pull Mistral Model
```powershell
ollama pull mistral
# Downloads ~4.4GB — Mistral 7B Q4_K_M quantized
```

### Step 3: Start n8n
```powershell
cd docker
docker compose up -d
# First run downloads n8n image (~500MB)
# Subsequent starts take 3-5 seconds
```

### Step 4: Configure n8n
1. Open http://localhost:5678
2. Create local admin account
3. Import workflow: **Add workflow → Import from file**
   - Select `n8n-workflows/onboarding-workflow-googleform.json`
4. Add credentials:
   - Google Sheets OAuth2 (Client ID + Secret from Google Cloud Console)
   - Gmail OAuth2 (same credentials)
   - Slack API (Bot User OAuth Token)
5. Update node settings:
   - Google Sheets nodes: set your Sheet ID
   - Slack node: set your channel ID
6. Click Publish

### Step 5: Set Up Google Form
1. Create form at https://forms.google.com
2. Add fields: Full Name, Email, Company, Phone, Project Type, Budget, Timeline, Description
3. Link to Google Sheets: Responses tab → Sheets icon → Create new spreadsheet
4. Share the form URL with clients

### Step 6: Test
```powershell
$body = @{
    name="Test Client"; email="your@email.com"; company="Test Co"
    projectType="Web App"; budget='$10,000'; timeline="3 months"
    description="Need a customer portal"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5678/webhook/client-onboarding" `
    -Method POST -Body $body -ContentType "application/json"
```

---

## 6. Workflow Explanation

### Node 1: Google Sheets Trigger
- **Type:** Polling trigger
- **Interval:** Every 1 minute
- **Source:** Google Sheet linked to the onboarding form
- **Action:** Fires when a new row is detected

### Node 2: Extract & Validate Data
- **Type:** JavaScript Code node
- **Input:** Raw Google Sheets row
- **Logic:** Maps column names to standard fields, validates required fields (name, email)
- **Output:** Structured client data object

```javascript
const clientData = {
  name: body['Full Name'],
  email: body['Email Address'],
  company: body['Company Name'],
  phone: body['Phone Number'],
  projectType: body['Project Type'],
  budget: body['Budget Range'],
  timeline: body['Expected Timeline'],
  description: body['Project Description'],
  submittedAt: body['Timestamp']
};
```

### Node 3: Mistral AI Processing
- **Type:** HTTP Request
- **URL:** `http://host.docker.internal:11434/api/generate`
- **Method:** POST
- **Model:** mistral
- **Timeout:** 60 seconds
- **Prompt:** Structured prompt asking for client profile, requirements, priority, and notes

### Node 4: Merge AI Analysis
- **Type:** JavaScript Code node
- **Logic:** Combines client data with Mistral response, generates unique Client ID
- **Client ID format:** `CLT-` + base36 timestamp (e.g., `CLT-MWK9KQK6`)

### Node 5: Save to Google Sheets
- **Type:** Google Sheets node
- **Operation:** Append Row
- **Columns:** 13 fields including AI analysis

### Node 6: Email Client (Welcome)
- **Type:** Gmail node
- **To:** Client's email from form
- **Content:** Branded HTML email with reference ID, submission summary, next steps

### Node 7: Slack Team Notification
- **Type:** Slack node
- **Channel:** #onboarding-alerts
- **Content:** Full client details + complete AI analysis

---

## 7. AI Model — Mistral 7B

### Model Details
- **Name:** Mistral 7B Instruct v0.2
- **Parameters:** 7.2 billion
- **Format:** GGUF (Q4_K_M quantization)
- **Size on disk:** 4.4 GB
- **VRAM usage:** ~4.2 GB
- **Context length:** 32,768 tokens

### Why Mistral?
- Best open-source model at 7B scale for instruction following
- Fits in 6GB VRAM with 4-bit quantization
- Fast inference — 15-25 tokens/second on RTX 3060
- Apache 2.0 license — commercial use allowed

### Quantization
4-bit NF4 (NormalFloat 4-bit) quantization reduces model size from ~14GB (float16) to ~4.4GB while maintaining ~95% of original quality. Applied using BitsAndBytes during loading.

### Prompt Template
```
You are an AI assistant for a professional services company.
A new client has submitted an onboarding form.
Analyze their information and provide:
1. A brief client profile summary (2-3 sentences)
2. Key project requirements extracted from their description
3. Suggested priority level (High/Medium/Low)
4. Any important notes or concerns

Client Information:
- Name: {name}
- Company: {company}
- Project Type: {projectType}
- Budget: {budget}
- Timeline: {timeline}
- Description: {description}

Respond in a structured format.
```

---

## 8. LoRA Fine-tuning

### What is LoRA?
Low-Rank Adaptation adds small trainable adapter matrices to frozen base model layers. Instead of training 7 billion parameters, only ~4-8 million adapter parameters are trained.

### Configuration
```python
LoraConfig(
    r=16,               # Rank — higher = more capacity
    lora_alpha=32,      # Scaling factor (2x rank)
    lora_dropout=0.05,
    target_modules=["q_proj","k_proj","v_proj","o_proj",
                    "gate_proj","up_proj","down_proj"],
    task_type=TaskType.CAUSAL_LM
)
```

### Training Setup
```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)
```

### Training Arguments
```python
TrainingArguments(
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,  # Effective batch size = 4
    learning_rate=2e-4,
    fp16=True,
    warmup_steps=10
)
```

### Run Fine-tuning
```powershell
cd fine-tuning
.\venv\Scripts\Activate.ps1
python train.py
```

### Output
Fine-tuned LoRA weights saved to: `fine-tuning/output/mistral-onboarding-lora/`

---

## 9. Deployment

### Local Deployment
- n8n: Docker on localhost:5678
- Ollama: Windows host on localhost:11434
- Access: Local network

### Demo Access via ngrok
To share a public URL for demos:
```powershell
# Expose n8n publicly
ngrok http 5678
# Share the generated URL e.g. https://xxxx.ngrok-free.app
```

---

## 10. API Reference

### Webhook Endpoint (Local)
```
POST http://localhost:5678/webhook/client-onboarding
Content-Type: application/json

{
  "name": "string (required)",
  "email": "string (required)",
  "company": "string",
  "phone": "string",
  "projectType": "string",
  "budget": "string",
  "timeline": "string",
  "description": "string"
}
```

### Response
```json
{
  "success": true,
  "clientId": "CLT-XXXXXXXX",
  "message": "Onboarding received successfully."
}
```

### Ollama API (Direct)
```
POST http://localhost:11434/api/generate
Content-Type: application/json

{
  "model": "mistral",
  "prompt": "Your prompt here",
  "stream": false
}
```

---

## 11. Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `channel_not_found` (Slack) | Bot not in channel | Add bot to channel via Slack |
| `host.docker.internal` unreachable | Ollama not running | Run `ollama serve` |
| Google Sheets 403 | Drive API disabled | Enable at console.cloud.google.com |
| `Values to Send` empty | Sheets mapping not saved | Re-add column mappings manually |
| CUDA out of memory | Batch size too large | Reduce batch size to 1 |
| `channel_not_found` after update | Old channel ID cached | Delete and recreate Slack credential |

---

## 12. Interview Q&A

See `docs/INTERVIEW_QA.md` for complete interview preparation with 20+ questions and answers.
