# Deployment Guide

## Architecture

```
Internet
    │
    ▼
Railway.app (n8n)
    │
    ▼ calls
ngrok tunnel → your laptop → Ollama → Mistral 7B
```

---

## Step 1 — Install ngrok

1. Go to **https://ngrok.com** → Sign up (free)
2. Download ngrok for Windows
3. Extract `ngrok.exe` to `C:\ngrok\`
4. Add `C:\ngrok` to your PATH
5. Get your auth token from https://dashboard.ngrok.com/get-started/your-authtoken
6. Run:
   ```powershell
   ngrok config add-authtoken YOUR_TOKEN_HERE
   ```

## Step 2 — Expose Ollama via ngrok

```powershell
# Make sure Ollama is running first
ollama serve

# In a new terminal, expose port 11434
ngrok http 11434
```

ngrok will show a URL like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:11434
```

Copy that URL — this is your public Ollama endpoint.

## Step 3 — Deploy n8n to Railway

1. Go to **https://railway.app** → Sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `ai-client-onboarding` repo
4. Railway will detect the `docker/docker-compose.yml`
5. Add these environment variables in Railway:
   ```
   N8N_HOST=0.0.0.0
   N8N_PORT=5678
   N8N_PROTOCOL=https
   N8N_ENCRYPTION_KEY=your-random-32-char-key
   WEBHOOK_URL=https://YOUR-RAILWAY-URL.railway.app/
   GENERIC_TIMEZONE=Asia/Kolkata
   ```
6. Click Deploy
7. Railway gives you a public URL like `https://n8n-production-xxxx.up.railway.app`

## Step 4 — Update Workflow

In your deployed n8n:
1. Import the workflow JSON
2. In the **Mistral AI Processing** node, change the URL from:
   ```
   http://host.docker.internal:11434/api/generate
   ```
   to:
   ```
   https://abc123.ngrok-free.app/api/generate
   ```
3. Reconfigure all credentials (Google, Gmail, Slack)
4. Publish

## Step 5 — Test

```powershell
# Replace with your Railway n8n URL
$response = Invoke-RestMethod `
    -Uri "https://YOUR-RAILWAY-URL.railway.app/webhook/client-onboarding" `
    -Method POST `
    -Body '{"name":"Test","email":"test@test.com","company":"Test Co","projectType":"Web App","budget":"$5000","timeline":"1 month","description":"Test"}' `
    -ContentType "application/json"
Write-Host $response
```

## Important Notes

- ngrok free tier URL changes every time you restart it
- For a permanent URL, upgrade to ngrok paid ($8/month) or use a VPS
- Railway free tier gives $5 credit — enough for ~1 month of n8n
- Keep your laptop on and Ollama running for AI processing to work

## Alternative: Keep Local + Use ngrok for n8n too

If you just want a shareable demo URL without Railway:

```powershell
# Expose local n8n to internet
ngrok http 5678
```

This gives you a public URL for your local n8n — simpler but requires your laptop to be on.
