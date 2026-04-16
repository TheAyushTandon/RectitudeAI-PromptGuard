# Rectitude.AI Deployment Guide (Production Hardened)

This guide provides instructions for deploying the Rectitude.AI platform in a standalone, production-ready environment using a remote Ollama server for private, high-speed inference.

## 🏗️ Architecture
- **Inference Server**: Remote Ollama host running `gemma:2b` or `llama3:8b`.
- **Backend API**: FastAPI (rectitude-api) handling the multi-agent security pipeline.
- **Frontend**: Next.js (rectitude-frontend) providing the dashboard interface.
- **State Store**: Redis for session memory and rate limiting.

## 🔑 API Key Acquisition

Before deploying, you may need keys for the following services (depending on your configuration):

### 1. Large Language Models (LLMs)
*   **Ollama (Local/Remote)**: No API key required. Best for privacy.
*   **Groq (High Speed)**: Get at [console.groq.com](https://console.groq.com/keys). Best for speed/responsiveness.
*   **Anthropic (Claude)**: Get at [console.anthropic.com](https://console.anthropic.com/).
*   **OpenAI (GPT-4)**: Get at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### 2. Search & Tools (Optional)
*   **Tavily (Web Search)**: Recommended for the EmailAgent's `search_web` tool. Get at [tavily.com](https://tavily.com/).
*   **Perplexity**: For specialized security analytics. Get at [perplexity.ai](https://www.perplexity.ai/settings/api).

### 3. Application Security
*   **SECRET_KEY**: Generate a long, random string for JWT signing:
    ```bash
    python -c "import secrets; print(secrets.token_urlsafe(32))"
    ```

### 1. Configure the Remote Ollama Server
On your remote inference machine (with GPU recommended):
1. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
2. Expose the API:
   - Edit the systemd service or set environment variable: `OLLAMA_HOST=0.0.0.0`
   - Restart Ollama.
3. Pull the recommended model: `ollama pull gemma:2b`
4. Ensure the firewall allows port `11434` from the API server's IP.

### 2. Prepare the Application Server
1. Clone the repository: `git clone <repo-url> RectitudeAI`
2. Create your `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Update `.env` with your remote Ollama IP:
   ```env
   OLLAMA_BASE_URL=http://<YOUR_REMOTE_IP>:11434
   DEFAULT_MODEL=gemma:2b
   ```

### 3. Launch the Stack
Initialize the containers:
```bash
docker-compose up -d --build
```

### 4. Verify Health
- **Check Backend**: `curl http://localhost:8000/health`
- **Check Frontend**: Open `http://localhost:3000` in your browser.
- **Check Logs**: `docker-compose logs -f api`

The system will start 3 services:
- **API**: `localhost:8000`
- **Frontend**: `localhost:3000`
- **Redis**: Port `6379`

## 🛡️ Security Features Verified
- **Hardened Audit Agent**: Strictly refuses investment recommendations using regex and persona enforcement.
- **System Prompt Propagation**: All agents use the now-standardized `system_prompt` propagation in the LLM pipeline to prevent persona drift.
- **Private Inference**: All data stays on your remote Ollama server; no cloud API keys required.
- **Sandbox Execution**: CodeExecutionAgent runs in a restricted Python environment.

## 🛠️ Troubleshooting
- **Failed to Fetch**: Ensure the `NEXT_PUBLIC_API_URL` in `docker-compose.yml` (frontend env) is accessible from your browser (typically `http://localhost:8000`).
- **Ollama Connection Error**: Verify `OLLAMA_BASE_URL` is reachable from the `api` container.
- **Persona Drift**: Check `backend/gateway/llm/client.py` to ensure prompts are being formatted with the `### SYSTEM ###` markers.
