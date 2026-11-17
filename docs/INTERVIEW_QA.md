# Interview Q&A — AI Client Onboarding Automation

## Basic Project Questions

**Q: Tell me about your project in one minute.**
> I built an AI-powered client onboarding automation system. When a client fills a Google Form, the system automatically processes their information using a locally hosted Mistral 7B language model, saves the data to Google Sheets, sends them a welcome email, and notifies the internal team on Slack — all in under 30 seconds with zero manual work. The key technical contribution is replacing expensive cloud AI APIs with a locally fine-tuned Mistral model running on my RTX 3060 GPU, which brings recurring AI processing costs to zero.

**Q: Why did you choose n8n over Zapier or Make.com?**
> n8n is open-source and self-hostable, which means no per-execution charges. Zapier charges based on workflow runs — for a production system handling hundreds of clients, that becomes expensive quickly. n8n gave me full control over the workflow logic, allowed custom JavaScript nodes, and integrated easily with a locally hosted AI model, which wouldn't be possible with Zapier.

**Q: Why Mistral instead of OpenAI GPT?**
> Two reasons — cost and control. OpenAI charges per token, so every client submission costs money. Mistral 7B runs locally on my GPU via Ollama, making AI processing completely free. Additionally, I can fine-tune Mistral on my own data, which isn't possible with GPT-4. For a production system, this reduces operational costs significantly.

**Q: What does the system actually do with AI?**
> For every client submission, Mistral analyzes the data and generates four things: a client profile summary, a list of extracted project requirements, a suggested priority level (High/Medium/Low) based on budget and timeline, and any important notes or concerns. This saves the account manager from manually reading and categorizing every submission.

---

## Technical Questions

**Q: How does n8n connect to your local Mistral model?**
> n8n runs inside a Docker container. Docker Desktop on Windows provides a special hostname called `host.docker.internal` that resolves to the Windows host machine. Ollama serves Mistral as a REST API on port 11434. So the n8n HTTP Request node calls `http://host.docker.internal:11434/api/generate` with the client data as a prompt, and receives the AI analysis as a JSON response.

**Q: What is Ollama and why did you use it?**
> Ollama is an open-source tool that makes running large language models locally as simple as running a Docker container. It handles model downloading, GPU acceleration, quantization, and exposes a REST API compatible with OpenAI's format. Without Ollama, running Mistral would require manually setting up CUDA, writing inference code, and managing memory — Ollama handles all of that automatically.

**Q: Explain 4-bit quantization.**
> Quantization reduces the precision of model weights from 32-bit or 16-bit floating point to 4-bit integers. This compresses Mistral 7B from ~14GB down to ~4.4GB, allowing it to fit in a 6GB VRAM GPU like the RTX 3060. The quality loss is minimal — 4-bit quantized Mistral performs nearly identically to the full precision version for text generation tasks.

**Q: What is LoRA fine-tuning? Why did you use it?**
> LoRA stands for Low-Rank Adaptation. Instead of retraining all 7 billion parameters of Mistral, LoRA adds small trainable adapter matrices to specific layers and only trains those. This reduces trainable parameters from 7 billion to roughly 4-8 million, making fine-tuning feasible on consumer hardware. I used it to teach Mistral the specific format and style of onboarding analysis our system needs.

**Q: What is PEFT?**
> PEFT stands for Parameter-Efficient Fine-Tuning. It's a Hugging Face library that implements techniques like LoRA, allowing fine-tuning of large models with minimal computational resources. It handles applying LoRA adapters to the right model layers, managing trainable vs frozen parameters, and saving/loading the adapter weights separately from the base model.

**Q: What is BitsAndBytes?**
> BitsAndBytes is a library that enables 4-bit and 8-bit quantization during model loading and training. I used it with the NF4 (NormalFloat 4-bit) quantization type, which is specifically designed for neural network weights and preserves model quality better than standard integer quantization.

**Q: How does the Google Form trigger work in n8n?**
> Google Forms automatically writes responses to a linked Google Sheet. n8n's Google Sheets Trigger node polls that sheet every minute for new rows. When it detects a new row, it fires the workflow with that row's data. This is a polling-based trigger — a more efficient alternative would be a Google Apps Script webhook that pushes to n8n instantly.

**Q: What happens if Mistral takes too long to respond?**
> Currently the HTTP Request node has a 60-second timeout. If Mistral doesn't respond within 60 seconds, the workflow fails. An improvement would be adding an error handling branch with retry logic, and sending a fallback notification to Slack if AI processing fails while still saving the raw client data.

**Q: How did you handle the Docker networking between n8n and Ollama?**
> n8n runs inside a Docker container while Ollama runs directly on Windows. Docker Desktop automatically creates a bridge called `host.docker.internal` that maps to the Windows host's IP. I configured n8n's HTTP Request node to call `host.docker.internal:11434` instead of `localhost:11434` — because inside the container, localhost refers to the container itself, not the host machine.

---

## Architecture Questions

**Q: Draw the system architecture.**
```
Client
  │
  ▼
Google Form
  │ (new response)
  ▼
Google Sheets ◄──── n8n polls every 60 seconds
  │
  ▼
n8n (Docker Container, port 5678)
  │
  ├──► HTTP POST → Ollama API (host.docker.internal:11434)
  │                    │
  │                    ▼
  │              Mistral 7B Q4_K_M
  │              (RTX 3060, 6GB VRAM)
  │                    │
  │              AI Analysis Response
  │                    │
  ◄────────────────────┘
  │
  ├──► Google Sheets API → Append row (13 columns)
  ├──► Gmail API → Send welcome email (HTML)
  └──► Slack API → Post to #onboarding-alerts
```

**Q: What database does n8n use?**
> By default n8n uses SQLite stored in the Docker volume at `./n8n-data`. This stores all workflow definitions, credentials (encrypted with AES-256 using the N8N_ENCRYPTION_KEY), and execution history. For production, this should be replaced with PostgreSQL for better performance and reliability.

**Q: How are credentials stored securely?**
> n8n encrypts all credentials using AES-256 encryption with a key defined in the `N8N_ENCRYPTION_KEY` environment variable in docker-compose.yml. The encrypted credentials are stored in the SQLite database inside the Docker volume. They are never stored in plain text.

---

## Challenges & Problem-Solving Questions

**Q: What was the biggest challenge you faced?**
> The most significant challenge was the Docker networking between n8n and Ollama. n8n runs inside a container and couldn't reach Ollama at localhost because localhost inside the container points to the container itself. I debugged this by running wget inside the n8n container to test connectivity, discovered `host.docker.internal` as the solution, and verified it resolved correctly before updating the workflow.

**Q: You mentioned CUDA out-of-memory errors. How did you handle them?**
> I solved this by using 4-bit quantization with BitsAndBytes. Loading Mistral in full float16 requires ~14GB VRAM, which exceeds the RTX 3060's 6GB. 4-bit quantization reduces this to ~4.4GB. I also set batch size to 1 with gradient accumulation of 4 steps to keep training memory usage within limits.

**Q: Why can't you serve the fine-tuned model in Ollama?**
> Newer versions of Ollama removed support for LoRA adapters directly. The proper workflow is to merge the LoRA adapter weights into the base model and convert to GGUF format for Ollama. The merge requires loading the full float16 model (~14GB) which exceeds my 16GB system RAM when other processes are running. The solution is running the merge on Google Colab (free GPU + 12GB RAM) or a machine with 32GB RAM.

**Q: What would you do differently if you rebuilt this?**
> Three things: First, I'd use Google Apps Script to push form responses to n8n instantly instead of polling every minute. Second, I'd add a PostgreSQL database to n8n instead of SQLite for production reliability. Third, I'd build the fine-tuning dataset with at least 100 examples before training, as 5 examples is too few for meaningful domain adaptation.

---

## Impact & Results Questions

**Q: What is the business impact of this system?**
> Manual client onboarding typically takes 15-30 minutes per client — reading the submission, writing a summary, sending an email, updating a spreadsheet, and notifying the team. This system does all of that in under 30 seconds. For a company onboarding 20 clients per month, that's 5-10 hours of saved administrative work monthly. The AI analysis also ensures consistent quality in how clients are assessed.

**Q: How does this reduce costs compared to existing solutions?**
> A comparable setup using Zapier + OpenAI GPT-4 would cost approximately $20-50/month for Zapier plus $0.03-0.10 per client for GPT-4 processing. Our system costs $0/month — n8n is free self-hosted, Mistral runs locally on existing hardware. At 100 clients/month, that's roughly $30-60/month saved on API costs alone.

---

## Future Improvements

**Q: What would you add next?**
> Four improvements in priority order:
> 1. Instant trigger using Google Apps Script webhook instead of polling
> 2. Serve the fine-tuned Mistral model by merging weights on Google Colab
> 3. Add a client dashboard — a simple web UI showing all onboarding records with status tracking
> 4. Follow-up automation — if no response from client in 3 days, automatically send a follow-up email
