# AI Client Onboarding — Full Setup Guide

## Project Structure

```
d:\ai client\
├── docs\                        ← Guides and documentation
├── scripts\                     ← Helper scripts
├── docker\
│   ├── docker-compose.yml       ← n8n Docker config
│   ├── .env                     ← Environment variables
│   ├── n8n-data\                ← n8n data (auto-created, don't delete)
│   ├── start-n8n.ps1            ← Start n8n
│   └── stop-n8n.ps1             ← Stop n8n
├── n8n-workflows\
│   └── onboarding-workflow.json ← Import this into n8n
└── fine-tuning\
    ├── data\                    ← Training data
    ├── output\                  ← Fine-tuned model output
    └── training_data.jsonl      ← Sample training examples
```

---

## Phase 1 — Install Infrastructure

### Step 1: Install Docker Desktop

Docker runs n8n in a container — free, no limits, data saved locally.

1. Go to: **https://www.docker.com/products/docker-desktop/**
2. Click **"Download Docker Desktop"** (Windows)
3. Run the installer
   - Keep default options
   - When asked, choose **WSL 2** backend (recommended)
4. Restart your computer when prompted
5. After restart, Docker Desktop opens automatically in the system tray
6. Verify in PowerShell:
   ```powershell
   docker --version
   docker compose version
   ```

> **Note:** Docker Desktop is free for personal use and small teams.

---

### Step 2: Install Ollama

Ollama runs Mistral AI locally on your RTX 3060.

1. Go to: **https://ollama.com/download/windows**
2. Download and run **OllamaSetup.exe** (no admin rights needed)
3. Ollama will appear in your system tray after install
4. Verify in PowerShell:
   ```powershell
   ollama --version
   ```

---

### Step 3: Install Python 3.11

Python 3.14 (already installed) does **not** support PyTorch or PEFT.
You need Python 3.11.9 alongside it for the fine-tuning phase.

1. Go to: **https://www.python.org/downloads/release/python-3119/**
2. Download **Windows installer (64-bit)**
3. Run installer:
   - ✅ Check **"Add Python 3.11 to PATH"**
   - Click **"Customize installation"** → keep all defaults → Install
4. Verify in a **new** PowerShell window:
   ```powershell
   py -3.11 --version
   # Should print: Python 3.11.9
   ```

---

## Phase 2 — Start n8n with Docker

### Step 4: Start n8n

```powershell
cd "d:\ai client\docker"
docker compose up -d
```

Or just double-click `start-n8n.ps1`.

- First run downloads the n8n image (~500MB), takes 2-3 minutes
- After that, starts in seconds
- Open: **http://localhost:5678**
- Create your admin account (local only, no cloud signup needed)

**Stop n8n:**
```powershell
cd "d:\ai client\docker"
docker compose down
```

Your workflows and credentials are saved in `docker\n8n-data\` and persist across restarts.

---

## Phase 3 — Pull and Run Mistral

### Step 5: Pull Mistral 7B

```powershell
ollama pull mistral
```

Downloads ~4.1GB (4-bit quantized). Your RTX 3060 6GB handles this perfectly.

### Step 6: Test it

```powershell
ollama run mistral "Summarize this in one sentence: A new client named John from TechCorp wants a web app."
```

You should see a response in 2-5 seconds with GPU acceleration.

### Step 7: Verify the API

n8n talks to Ollama via its REST API. Test it:
```powershell
Invoke-RestMethod -Uri "http://localhost:11434/api/tags"
```

---

## Phase 4 — Import Workflow into n8n

### Step 8: Import the workflow

1. Open **http://localhost:5678**
2. Click **"Add workflow"** → **"Import from file"**
3. Select: `d:\ai client\n8n-workflows\onboarding-workflow.json`
4. The workflow loads with all 7 nodes

### Step 9: Configure credentials

You need to add credentials for 3 services:

#### Google Sheets + Gmail (OAuth2)
1. Go to: https://console.cloud.google.com/
2. Create a project → Enable **Google Sheets API** and **Gmail API**
3. Create **OAuth 2.0 credentials** (Desktop app type)
4. In n8n: Settings → Credentials → Add → Google OAuth2
5. Paste Client ID and Secret → Authorize

#### Slack
1. Go to: https://api.slack.com/apps → Create app → "From scratch"
2. Add **Bot Token Scopes**: `chat:write`, `channels:read`
3. Install app to your workspace
4. Copy the **Bot User OAuth Token**
5. In n8n: Settings → Credentials → Add → Slack API → paste token

### Step 10: Update placeholders in the workflow

In the **"Save to Google Sheets"** node:
- Replace `YOUR_GOOGLE_SHEET_ID` with your actual sheet ID
  (it's the long string in the Google Sheets URL)

In the **"Slack Team Notification"** node:
- Replace `YOUR_SLACK_CHANNEL_ID` with your channel ID
  (right-click channel in Slack → View channel details → copy ID)

---

## Phase 5 — Test the Full Flow

### Step 11: Activate and test

1. In n8n, toggle the workflow to **Active**
2. Copy the webhook URL shown on the **Webhook Trigger** node
3. Run this test in PowerShell (replace the URL):

```powershell
$body = @{
    name        = "Test Client"
    email       = "test@example.com"
    company     = "Test Company"
    phone       = "+91 98765 43210"
    projectType = "Web Application"
    budget      = "$10,000 - $25,000"
    timeline    = "3 months"
    description = "We need a customer portal with login, dashboard, and reporting features."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5678/webhook/client-onboarding" `
                  -Method POST `
                  -Body $body `
                  -ContentType "application/json"
```

**Expected result:**
- ✅ Mistral analyzes the client info
- ✅ Row added to Google Sheets
- ✅ Welcome email sent to test@example.com
- ✅ Slack message posted to your channel
- ✅ JSON response with clientId returned

---

## Phase 6 — LoRA Fine-tuning (after Phase 5 works)

```powershell
# Set up Python 3.11 environment
cd "d:\ai client\scripts"
.\setup-python-env.ps1
```

Then run the fine-tuning notebook. See `fine-tuning\README.md`.

---

## Quick Reference

| What | Command |
|------|---------|
| Start n8n | `cd "d:\ai client\docker" && docker compose up -d` |
| Stop n8n | `cd "d:\ai client\docker" && docker compose down` |
| n8n UI | http://localhost:5678 |
| Ollama API | http://localhost:11434 |
| Pull Mistral | `ollama pull mistral` |
| Chat with Mistral | `ollama run mistral` |
| Check all services | `d:\ai client\scripts\check-setup.ps1` |
