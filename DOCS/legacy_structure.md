# Legacy Structure Overview (Pre-Redesign)

This document captures the core functionality and data structures of the Rectitude.AI frontend before the "Modern UI" redesign.

## Core Components used across routes
- `SessionNavBar`: Sidebar navigation.
- `apiClient`: For backend communication.
- `useChatStore` / `useChat`: State management and logic for chat interactions.

---

## 1. Dashboard (`/dashboard`)
**Primary Purpose**: Real-time security monitoring and session health.

### Key Features:
- **ASI Gauge**: Displays Autonomous Safety Index score (0.00 to 1.00).
- **Security Alerts**: Visual indicator for ASI alerts.
- **Risk Distribution**: Visualization of risk scores for the last few requests.
- **Layer Performance**: Latency monitoring for:
  - T1 (Regex Prefilter)
  - T2 (ML Classifier)
  - T3 (JWT Token Verification)
  - Output Mediator
- **Live Audit Log**: Row-based log of every request, decision (ALLOW/BLOCK/ESCALATE), risk score, and agent used.

---

## 2. Chat (`/chat`)
**Primary Purpose**: Interactive security-wrapped chat interface.

### Key Features:
- **Agent Selection**: Switch between specialized agents (HR, Finance, Code, etc.).
- **Message Bubbles**: Support for user and assistant messages with security metadata (tier reached, blocked status).
- **Thinking Indicator**: Visual feedback during processing.
- **Suggested Prompts**: Quick-start buttons that demonstrate specific security layers.
- **Session ID**: Tracking for multi-turn safety analysis.

---

## 3. Agents (`/agents`)
**Primary Purpose**: Catalog of available agents and their security boundaries.

### List of Agents & Configuration:
- **HR Database Agent**: `query_database`, schema scoping, PII redaction.
- **Email Agent**: `compose_email`, domain whitelist, exfiltration prevention.
- **Code Execution Agent**: `execute_python`, sandboxed environment, import smuggling protection.
- **Financial Advisor Agent**: `calculator`, persona drift detection, ASI monitoring.
- **General Utility Agent**: Fallback for unclassified requests.

### Technical Concept:
- **JWT Capability Tokens**: Explanation of how tokens enforce tool-specific scoping.

---

## 4. Settings (`/settings`)
**Primary Purpose**: User and system configuration.

### Placeholder Sections:
- **Profile**: Preferences.
- **API Keys**: Access token management.
- **Alerts**: ASI threshold configuration.
