# RectitudeAI - LLM Security Gateway

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Multi-layer defense system for LLM applications with runtime security, prompt injection detection, and behavioral anomaly monitoring.

## 👥 Team

- **Ayush Tandon** (S24CSEU0134) - Backend Architecture & ML
- **Vartika Manish** (S24CSEU0169) - Security & Cryptography

## 🎯 Project Overview

RectitudeAI is a production-grade security gateway for LLM applications that addresses critical vulnerabilities in autonomous AI systems including:

- Prompt injection attacks
- Data breaches
- Unauthorized tool execution
- Multi-turn jailbreak attempts

### Current Status: Phase 2 In Progress 🔄

**Implemented:**
- ✅ FastAPI backend with async support
- ✅ JWT authentication
- ✅ Rate limiting with Redis
- ✅ LLM integration (OpenAI/Anthropic/Ollama)
- ✅ Structured logging
- ✅ Health checks and monitoring
- ✅ Prompt injection & harmful intent classifier (`michellejieli/NSFW_text_classifier`)

**Coming Soon (Phase 2-5):**
- 🔜 Perplexity-based anomaly detection
- 🔜 Policy engine with risk aggregation
- 🔜 Cryptographic tool signing
- 🔜 Red team engine
- 🔜 Behavioral anomaly detection

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Redis (for rate limiting)
- OpenAI/Anthropic API key OR Ollama installed locally

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/TheAyushTandon/RectitudeAI-PromptGuard.git
cd RectitudeAI-PromptGuard

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Start Redis (if not already running)
# Option A: Docker
docker run -d -p 6379:6379 redis:alpine

# Option B: System service
redis-server

# 6. Run the application
uvicorn app.main:app --reload --port 8000
```

### First Request

```bash
# 1. Login to get JWT token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "demo_password_123"
  }'

# Response will include: {"access_token": "eyJ...", ...}

# 2. Make inference request
curl -X POST http://localhost:8000/v1/inference \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "user_id": "user_123",
    "prompt": "Explain quantum computing in simple terms",
    "max_tokens": 500,
    "temperature": 0.7
  }'
```

## 📁 Project Structure

```
rectitude-ai/
├── backend/
│   ├── gateway/                 # Main entry, Config, Auth, LLM
│   ├── api/                     # Health, Audit routes
│   ├── layer1_intent_security/  # Intent & Injection classification
│   ├── layer2_crypto/           # ZKP & FHE Engine (Vartika)
│   ├── layer3_behavior_monitor/ # Agent Stability Index (ASI)
│   ├── layer4_red_teaming/      # Automated attack runners
│   └── layer5_orchestration/    # LangGraph governance
├── frontend/                    # Dashboard (MINE)
│   ├── app/
│   ├── components/
│   └── services/
└── datasets/                    # Security datasets (JailbreakBench)
```

## 🔧 Configuration

### Environment Variables

Key settings in `.env`:

```env
# LLM Provider (choose one)
LLM_PROVIDER=openai        # or anthropic, ollama

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Security
SECRET_KEY=your-secret-key-here
JWT_EXPIRATION_MINUTES=60

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

### Supported LLM Providers

1. **OpenAI** (gpt-4, gpt-3.5-turbo)
2. **Anthropic** (claude-3-sonnet, claude-3-opus)
3. **Ollama** (llama2, mistral, mixtral - local)

## 📊 API Documentation

Interactive API documentation available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/login` | POST | User login | No |
| `/v1/inference` | POST | LLM inference | Yes |
| `/v1/models` | GET | List models | Yes |
| `/health/` | GET | Health check | No |

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_endpoints.py -v

# Run specific test
pytest tests/test_api/test_endpoints.py::TestAuthEndpoints::test_login_success -v
```

**Current Test Coverage:** >80%

## 🏗️ Development Roadmap

### Phase 1: Core Gateway ✅ (Weeks 1-3)
- FastAPI server
- JWT authentication
- Rate limiting
- LLM integration

### Phase 2: Detection Layer 🔄 (Weeks 4-7)
- Injection classifier
- Perplexity detector
- Policy engine

### Phase 3: Cryptographic Layer (Weeks 8-10)
- Document hashing
- Tool call signing
- Sandbox validation

### Phase 4: Red Team Engine (Weeks 11-12)
- Adversarial prompt generator
- Attack runner
- ASR metrics

### Phase 5: Behavioral Analysis (Weeks 13-14)
- Multi-turn detection
- Session profiling
- Anomaly scoring

## 🔒 Security Features

### Phase 1 & 2 (Current)
- ✅ JWT-based authentication
- ✅ Token expiration & refresh
- ✅ Rate limiting (100 req/min default)
- ✅ Request logging & audit trail
- ✅ CORS protection
- ✅ Input validation
- ✅ Harmful intent & prompt injection detection (`michellejieli/NSFW_text_classifier`)

### Phase 3+ (Planned)
- 🔜 Statistical anomaly detection
- 🔜 Risk-based policy enforcement
- 🔜 HMAC tool call signing
- 🔜 Continuous red team testing
- 🔜 Behavioral profiling

## 📈 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Response Time | <500ms | ~300ms |
| Throughput | >1000 req/s | ~800 req/s |
| Detection Rate | >90% | N/A (Phase 2) |
| False Positives | <5% | N/A (Phase 2) |

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all functions
- Run `black` for formatting
- Run `flake8` for linting

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

- **Ayush Tandon**: s24cseu0134@bennett.edu.in
- **Vartika Manish**: s24cseu0169@bennett.edu.in

## 🙏 Acknowledgments

- OWASP Top 10 for LLM Applications
- JailbreakBench dataset
- FastAPI framework
- OpenAI & Anthropic for LLM APIs

## 📚 Resources

- [Documentation](docs/)
- [Architecture Design](docs/ARCHITECTURE.md)
- [API Reference](http://localhost:8000/docs)
- [Contributing Guide](CONTRIBUTING.md)

---

**Status**: Phase 2 In Progress | **Next Milestone**: Tool Signing (Phase 3)

Built by Ayush & Vartika
