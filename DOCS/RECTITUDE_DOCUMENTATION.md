# 🔬 Rectitude.AI — The Security Layer for the Generative Intelligence Era

> **Rectitude.AI** is a high-performance, multi-layered security gateway designed to protect Large Language Model (LLM) applications from adversarial attacks, data exfiltration, and behavioral drift. 

By implementing a **"Defense-in-Depth"** strategy, Rectitude.AI ensures that LLMs operate within safe, authorized boundaries, even when acting autonomously as agents.

---

## 🛡️ The 5-Layer Security Sandwich
Rectitude.AI processes every request through a tiered pipeline where each layer specializes in a different threat vector.

### Layer 1: Intent & Prompt Security (The Shield)
Evaluates "what the user is trying to do" before it reaches the model.
- **Hybrid Detection**: Combines deterministic regex prefiltering with transformer-based ML classifiers (`DeBERTa-v3`).
- **Injection Prevention**: Detects prompt injection patterns (e.g., "Ignore previous instructions") and indirect injection.
- **NSFW & Harm Filter**: Scans for toxicity, sexually explicit content, and harmful intent logic.

### Layer 2: Cryptographic Integrity (The Vault)
Uses cryptographic primitives to ensure agents only do what they are authorized to do.
- **Capability Tokens**: Short-lived, HMAC-signed JWTs that encode a specific "tool scope" (e.g., `read-only` vs `write-access`).
- **Tool Call Verification**: Every agent must present a valid token to the sandbox before a tool (like File System or Email) is executed.
- **Integrity Checks**: Prevents man-in-the-middle tampering of instructions between the orchestrator and the agent.

### Layer 3: Behavioral Monitoring & ASI (The Watcher)
Detects "slow-burn" attacks that happen over many turns.
- **Agent Stability Index (ASI)**: A proprietary metric tracking session health.
- **Drift Detection**: Analyzes semantic consistency, tool usage patterns, and boundary violations across a sliding window of 10+ turns.
- **Persona Persistence**: Ensures the agent hasn't been "steered" into a different, malicious persona by the user.

### Layer 4: Adaptive Policy & Red Teaming (The Trainer)
Keeps the system ahead of new threats through simulation.
- **Automated Red Teaming**: Uses an RL-driven agent to probe the system with adversarial prompts from the `JailbreakBench`.
- **Policy Auto-Update**: If a novel attack is detected, the system automatically updates its internal scoring thresholds via a Reinforcement Learning policy updater.

### Layer 5: Orchestration & Governance (The Brain)
Ensures seamless coordination across the entire pipeline.
- **Intelligent Routing**: Classifies user intent and routes to specialized, sandboxed agents (HR, Email, Finance, Code).
- **Output Mediation**: Scans model responses in real-time to redact PII (SSNs, Phone Numbers) and secrets (API Keys) before they reach the user.

---

## 🚀 Key Innovations

### 1. The Agent Stability Index (ASI)
Unlike standard gateways that check one prompt at a time, Rectitude.AI remembers. If a user starts clean but gradually steers an agent towards a jailbreak, the **ASI score** will drop. When it hits the critical threshold, the session is quarantined.

### 2. Scoped Capability Tokens
Agents are never "trusted" by default. They are issued tokens based on the current session's risk score.
- **Low Risk**: Full tool access (write, delete, send).
- **High Risk**: Read-only access (search, read-only CRM).

### 3. RL-Based Policy Fusion
Our policy engine doesn't just use fixed rules. It fuses regex, ML, and behavioral signals into a single score. If a regex is too strict (false positive), the ML classifier can "vote" to pull it back, ensuring usability isn't sacrificed for security.

---

## 🏗️ Technical Stack
Rectitude.AI is built using a modern, scalable infrastructure:
- **Backend**: Python (FastAPI), Async architecture.
- **Intelligence**: Ollama (Llama2/Mistral), OpenAI (GPT-4), Anthropic (Claude 3.5).
- **ML Classifiers**: HuggingFace Transformers, PyTorch.
- **State Store**: Redis (Rate limiting and ASI tracking).
- **Persistence**: Hybrid SQLite/PostgreSQL for audit logs.

---

## 👥 Use Cases
*   **Enterprise Chatbots**: Safely integrate LLMs with internal HR and Finance databases.
*   **Autonomous Agents**: Prevent "Agent Hijacking" where an LLM is tricked into deleting cloud resources.
*   **Customer Support**: Ensure agents don't leak PII or violate company policy during long interactions.
*   **Shadow AI Protection**: Act as a central security proxy for all internal AI usage.

---
**Rectitude.AI**: *Security that doesn't just block—it monitors, detects, and adapts.*
