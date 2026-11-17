# AI Client Onboarding Automation

An AI-powered automated client onboarding system built with **n8n**, **Mistral 7B**, and **Google Workspace**. Automates the entire onboarding pipeline from form submission to team notification — with zero recurring AI costs.

---

## 🚀 What It Does

When a client submits the onboarding form, the system automatically:

1. **Triggers** — Google Form submission detected by n8n
2. **Analyzes** — Mistral 7B AI (running locally) processes client information
3. **Stores** — Client data + AI analysis saved to Google Sheets
4. **Emails** — Automated welcome email sent to the client via Gmail
5. **Notifies** — Team notified instantly on Slack

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| n8n | Workflow automation (Docker) |
| Mistral 7B Instruct v0.2 | Local AI processing |
| Ollama | Local LLM deployment |
| Docker | Container for n8n |
| Python 3.11 + PEFT | LoRA fine-tuning |
| Google Forms | Client data collection |
| Google Sheets | Client data storage |
| Gmail | Automated email communication |
| Slack | Team notifications |

---

## 📁 Project Structure

```
ai-client-onboarding/
├── docker/
│   ├── docker-compose.yml        # n8n Docker setup
│   ├── start-n8n.ps1             # Start n8n
│   └── stop-n8n.ps1              # Stop n8n
├── n8n-workflows/
│   ├── onboarding-workflow.json           # Webhook-based workflow
│   └── onboarding-workflow-googleform.json # Google Form workflow
├── fine-tuning/
│   ├── training_data.jsonl       # LoRA training examples
│   ├── train.py                  # Fine-tuning script
│   └── README.md                 # Fine-tuning guide
├── scripts/
│   ├── check-setup.ps1           # Verify all installations
│   ├── setup-python-env.ps1      # Set up Python ML environment
│   └── start-services.ps1        # Start all services
├── docs/
│   ├── SETUP_GUIDE.md            # Full setup guide
│   └── index.html                # Project documentation (HTML)
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites
- Windows 10/11
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/download/windows)
- Python 3.11

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-client-onboarding.git
cd ai-client-onboarding
```

### 2. Pull Mistral model
```bash
ollama pull mistral
```

### 3. Start n8n
```powershell
cd docker
docker compose up -d
```

### 4. Open n8n
Go to **http://localhost:5678** and create your account.

### 5. Import workflow
In n8n: **Add workflow → Import from file** → select `n8n-workflows/onboarding-workflow-googleform.json`

### 6. Configure credentials
- Google Sheets OAuth2
- Gmail OAuth2
- Slack API token

### 7. Test
Submit the Google Form and watch the automation run.

---

## 🤖 AI Processing

Mistral 7B runs **locally on your GPU** via Ollama. No external API calls, no cost per request.

For each client submission, Mistral generates:
- Client profile summary
- Key project requirements
- Priority level (High/Medium/Low)
- Important notes and concerns

---

## 🔧 LoRA Fine-tuning

Fine-tune Mistral specifically for onboarding use cases:

```powershell
cd fine-tuning
# Activate virtual environment
.\venv\Scripts\Activate.ps1
# Run training
python train.py
```

Requirements: NVIDIA GPU with 6GB+ VRAM, Python 3.11, CUDA 12.1

---

## 📊 System Architecture

```
Google Form
     ↓
   n8n (Docker)
     ↓
Mistral 7B (Ollama)
     ↓
  ┌──────────────────────┐
  │  Google Sheets       │
  │  Gmail               │
  │  Slack               │
  └──────────────────────┘
```

---

## 👤 Author

**Ankit Kumar**  
AI-Powered Client Onboarding Automation Project

---

## 📄 License

MIT License — free to use and modify.
