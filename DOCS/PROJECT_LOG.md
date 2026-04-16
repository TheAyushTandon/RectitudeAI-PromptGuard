# Rectitude.AI - Project Tree & Feature Map (FORKED: Vartika222)

This document serves as the live source of truth for the forked project structure.
This repository is the **High-Fidelity Feature Lead** containing full RL and Crypto implementations.

> [!TIP]
> **Credit Saving Entry Point**: For a detailed, explainable map of the codebase, see [CODEBASE_MAP.md](file:///d:/PROJECTS/Rectitude.AI%20new/CODEBASE_MAP.md).

## 📂 Project Structure

```text
Rectitude.AI/ (Fork: Vartika222)
├── .agents/                    # Agent skills and workflows
│   └── skills/
│       └── project_management.md # SKILL: Ensures tree logs are updated
├── backend/                    # Core Backend Services (FastAPI)
│   ├── api/                    # API Endpoints (FastAPI)
│   ├── gateway/                # JWT Auth, Rate Limiting (Redis)
│   ├── layer1_intent_security/ # Prompt Injection, NSFW, Perplexity Anomaly
│   ├── layer2_crypto/          # capability_tokens, fhe_engine, zk_prover/verifier
│   ├── layer3_behavior_monitor/ # Embedding Monitor, Boundary Violations, ASI
│   ├── layer4_red_teaming/     # Attack Runner, RL Policy Updater
│   ├── layer5_orchestration/   # LangGraph, n8n, Observability
│   ├── models/                 # LLM Integration (OpenAI, Anthropic, Ollama)
│   ├── storage/                # Data storage and persistence
│   └── utils/                  # Helper utilities and logging
├── data/                       # Dataset storage
├── DOCS/                       # Documentation and Research (NEW)
│   ├── FEATURE_SHOWCASE.md     # Feature list and benchmarks
│   └── TECHNICAL_RATIONALE.md  # Detailed "Why this stack" analysis
├── scripts/                    # Automation and deployment scripts
│   └── unified_evaluator.py    # Master Security Evaluation Suite
├── tests/                      # Unit and integration tests
├── .env.example                # Environment variables template
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Service orchestration
├── results_and_analysis_report.txt # Milestone 3 Research Report
├── frontend/                   # Next.js 14 Frontend (NEW ✅)
│   ├── src/
│   │   ├── app/                # Next.js App Router pages (/, /chat, /agents, /dashboard, /settings)
│   │   ├── components/         # UI components (sidebar, chat, dashboard, agents, hero)
│   │   ├── hooks/              # useChat.ts, useAuth.ts
│   │   ├── store/              # Zustand stores (chatStore, authStore)
│   │   ├── api/                # Axios client with JWT interceptor
│   │   └── lib/                # utils (cn helper)
│   ├── public/                 # logo.svg, mask.svg
│   └── .env.local              # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
└── README.md                   # Project overview
```

## ✅ Feature Breakdown & Technical Details

### 1. **Core Infrastructure**
- **FastAPI Gateway**: Fully operational with JWT and Redis-based rate limiting.
- **Async LLM Integration**: Multi-provider support (OpenAI, Anthropic, Ollama).

### 2. **AI Security Layers**
- **Layer 1: Intent Security**: DeBERTa v3-based hybrid classification.
- **Layer 2: Crypto Integrity**: ZK-verified callbacks and capability tokens.
- **Layer 3: Behavior Monitor**: Agent Stability Index (ASI) tracking multi-turn drift.
- **Layer 4: Red Teaming**: RL-based adaptive policy updates (PPO).

## 📝 Modification Log

| Date | User Request | Changes Made |
| :--- | :--- | :--- |
| 2026-04-04 | Pull forked repo | Switched from main to `Vartika222/RectitudeAI-PromptGuard`. |
| 2026-04-04 | Workspace Reset | Cleared all incorrect files and re-cloned the correct fork. |
| 2026-04-04 | Remove frontend | Entirely deleted the `frontend/` directory. |
| 2026-04-04 | Project Management | Restored `.agents` and updated `PROJECT_LOG.md` for the fork. |
| 2026-04-04 | Milestone 3 | Completed security evaluation (Phase 1-4). Created `results_and_analysis_report.txt` and `TECHNICAL_RATIONALE.md`. |
| 2026-04-09 | Multi-Agent Build | Implemented 4 specialized agents (HR, Email, Code, Finance), 5 tools, and Integrated them into a secure Orchestrator pipeline with Capability Tokens and ASI monitoring. Upgraded all technical documentation. |
| 2026-04-10 | Credit Optimization | Created `CODEBASE_MAP.md` with Mermaid architecture and layered deep-dives to save context tokens. Updated Project Management skill. |
| 2026-04-10 | Security & Precision | Merged 8 verified bug fixes (Regex precision, Finance agent auth, ASI ghost drift, Orchestrator latency). System is now frontend-ready. |

| 2026-04-11 | Frontend Build | Bootstrapped full Next.js 14 + TypeScript + Tailwind + shadcn/ui frontend. 6 routes: `/` (landing), `/chat` (interactive security-protected chat), `/agents` (Agents Access + JWT showcase), `/dashboard` (live ASI gauge + audit log), `/settings`. Animated collapsible sidebar, framer-motion hero, 5-layer security badge system. Build: ✅ 0 TypeScript errors. |
| 2026-04-16 | Project Hardening | Integrated elite Agent Skill suite (`security-auditor`, `backend-architect`, `python-pro`, `fastapi-pro`, `lint-and-validate`, `systematic-debugging`). Implemented the **GSD (Get Shit Done)** workflow based on `subagent-driven-development`. System updated to Phase 5.5 (Agent-Optimized). |

---
*Last Updated: 2026-04-11 04:20:00*
