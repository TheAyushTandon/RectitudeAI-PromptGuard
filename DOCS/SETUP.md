# Setup Instructions

## Prerequisites

1.  **Python 3.11+**
2.  **Redis** (Used for rate limiting and state management)
3.  **Ollama (Recommended for Local Dev)**:
    *   Download from: [ollama.com](https://ollama.com)
    *   Install and run the application.
    *   Pull the default model: `ollama pull llama3` (or your preferred model).
    *   Ensure Ollama is running at `http://localhost:11434`.
4.  **Node.js & npm** (For the Frontend Dashboard).

## Quick Setup (Recommended)

### Option 1: Using the Run Script
```bash
cd rectitude-ai
./run.sh
```

### Option 2: Frontend Dashboard
```bash
cd rectitude-ai/frontend
npm install
npm run dev
```
Dashboard available at http://localhost:3000

### Option 3: Using Docker
```bash
cd rectitude-ai
docker-compose up -d
```

## Manual Setup

### 1. Environment Setup

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit with your preferred editor
nano .env  # or vim, code, etc.
```

**Required variables:**
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `LLM_PROVIDER` - Choose: openai, anthropic, or ollama
- API keys for your chosen provider

### 3. Start Redis

**Option A - Docker:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**Option B - System Package:**
```bash
# Mac
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Verify
redis-cli ping  # Should return PONG
```

### 4. Run the Application

```bash
uvicorn backend.gateway.main:app --reload --port 8000
```

## Verification

### 1. Health Check
```bash
curl http://localhost:8000/health/
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {...}
}
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_user","password":"demo_password_123"}'
```

### 3. Make Inference Request
```bash
# Save token from login response
TOKEN="your-token-here"

curl -X POST http://localhost:8000/v1/inference \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "user_id": "test",
    "prompt": "Hello, how are you?",
    "max_tokens": 100
  }'
```

## Running Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution:** Make sure you're in the project root directory and PYTHONPATH is set:
```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

### Issue: "Redis connection refused"
**Solution:** Start Redis:
```bash
redis-server
# Or check if it's running
redis-cli ping
```

### Issue: "OpenAI API Error"
**Solution:** Verify your API key in `.env`:
```bash
# Test your key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

### Issue: Port 8000 already in use
**Solution:** Use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

## Development Workflow

### Daily Workflow
```bash
# 1. Activate environment
source venv/bin/activate

# 2. Pull latest changes
git pull origin main

# 3. Install any new dependencies
pip install -r requirements.txt

# 4. Run tests
pytest tests/

# 5. Start development server
uvicorn app.main:app --reload
```

### Before Committing
```bash
# Format code
black app/ tests/

# Lint
flake8 app/ tests/

# Run tests
pytest tests/ -v --cov=app

# Type check (optional)
mypy app/
```

## Next Steps

After setup is complete:

1. **Test the API** using the Swagger docs at http://localhost:8000/docs
2. **Read the roadmap** in `roadmap.md`
3. **Start Phase 2** implementation (injection detection)
4. **Set up CI/CD** with GitHub Actions
5. **Deploy to production** when ready

## Support

If you encounter any issues:

1. Check the logs in `logs/app.log`
2. Review error messages carefully
3. Consult the README.md
4. Contact the team:
   - Ayush: s24cseu0134@bennett.edu.in
   - Vartika: s24cseu0169@bennett.edu.in
