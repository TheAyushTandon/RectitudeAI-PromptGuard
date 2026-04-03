# Proposal: Agentic Security Orchestration Framework (Phase 5)

## 1. Objective
Transform the RectitudeAI security pipeline from a serial, static filtering process into a dynamic, agentic intelligence team using **CrewAI**. This shift aims to reduce average computation time for benign queries while providing deeper, context-aware analysis for complex security threats.

---

## 2. Core Architecture: The "Security Crew"
The system transitions from running every detector on every prompt to a **Hub-and-Spoke** model.

### 2.1 The Dispatcher (Manager Agent)
- **Model**: Fast, lightweight Semantic Router or Tiny-BERT.
- **Role**: Primary triage. It performs a "first-glance" analysis of the incoming prompt.
- **Workflow**: 
    - **Benign Path**: If the prompt is common/harmless (e.g., "Hello", "What's the weather?"), it bypasses heavy security agents and proceeds directly to the LLM.
    - **Suspect Path**: If the prompt contains specific patterns (code, Base64, aggressive instructions), it recruits specialized agents.

---

## 3. Specialized Security Agents
Each agent is assigned a specific "Security Persona" and has the authority to flag or block prompts within their domain.

| Agent | Role | Tools Used (Existing Models) |
| :--- | :--- | :--- |
| **Injection Specialist** | Protects against Jailbreaks & Prompt Injections. | `Deepset Injection Model` |
| **Harmful Intent Auditor** | Detects dangerous instructions (weapons, toxicity). | `Toxic-BERT` + `NSFW Classifier` |
| **Obfuscation Analyst** | Decodes Base64, Hex, and hidden payloads. | `GPT-2 Perplexity Detector` |
| **Privacy Officer** | Scans for PII (Personally Identifiable Information). | `Presidio` or custom RegEx tools. |

---

## 4. Implementation Details (The "Tools")
Existing models will be wrapped as **CrewAI Tools**. This allows agents to "consult" the models only when necessary.

```python
# Example Tool Wrapper
from crewai.tools import tool

@tool("intent_check")
def check_intent_logic(prompt: str):
    """Analyzes the prompt for harmful or restricted instructions."""
    # Existing Layer 1 Logic is called here
    return IntentClassifier().classify(prompt)
```

---

## 5. Key Advantages
1. **Adaptive Computation**: Benign prompts use ~90% less processing power by avoiding the full security stack.
2. **Contextual Reasoning**: Agents can "discuss" a prompt. For example, the Obfuscation Analyst might decode a string and then pass the *decoded* result to the Intent Auditor for a second check.
3. **Easier Scaling**: Adding a new security layer (like Layer 3: Behavioral) simply means adding a new Agent to the Crew, without breaking the existing pipeline.

---

## 6. Development Roadmap
- **Step 1**: Initialize Layer 5 with CrewAI dependencies.
- **Step 2**: Define the "Dispatcher" logic and routing thresholds.
- **Step 3**: Wrap Layer 1 & Layer 2 models as Agent Tools.
- **Step 4**: Implement the "Final Gatekeeper" to aggregate Agent results.

---
**Status**: Planned / Conceptual
**Assigned**: Future Milestone (Layer 5 Orchestration)
