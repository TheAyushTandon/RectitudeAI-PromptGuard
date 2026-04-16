"""
Agent Router — classifies user intent and dispatches to the correct agent.

Uses the base LLM (via Ollama) to make a structured classification decision.
Falls back to simple keyword matching if the LLM is unavailable.

Flow:
  1. User prompt arrives (already security-screened by the orchestrator)
  2. Router sends the prompt + agent catalog to the base LLM
  3. LLM returns a JSON classification: {"agent": "agent_name", "reasoning": "..."}
  4. Router looks up the agent in the registry and dispatches

If the LLM is down or returns an invalid response, the router falls back
to keyword-based classification using the agent descriptions.
"""

from __future__ import annotations
import json
import re
from typing import Optional

import httpx

from backend.agents.registry import agent_registry
from backend.gateway.config import settings
from backend.utils.logging import get_logger

logger = get_logger(__name__)

# Classification prompt template
_CLASSIFICATION_PROMPT = """You are a high-precision multi-agent router. Your job is to decide which specialized agent is required for a task.

AVAILABLE AGENTS:
{agent_list}

RULES:
1. If the request is a GREETING (e.g., "hello", "hi", "hey"), return "none".
2. If the request is GENERAL CHAT or off-topic, return "none".
3. ONLY return an agent name if the request matches their specialized description.
4. Respond ONLY with valid JSON: {{"agent": "name", "reasoning": "..."}}

USER_PROMPT: "{user_prompt}"

RESPONSE:
```json
"""
# Keyword fallback patterns for each agent type
_KEYWORD_PATTERNS = {
    "hr_database": [
        r"\b(employee|salary|salaries|department|staff|hr|human\s+resource|payroll|personnel|performance\s+review)\b",
        r"\b(hire|hiring|team\s+member|headcount|who\s+works)\b",
    ],
    "email_agent": [
        r"\b(email|mail|send\s+message|inbox|reply|forward|compose|draft|support\s+ticket)\b",
        r"\b(customer\s+complaint|respond\s+to|write\s+back)\b",
    ],
    "code_exec": [
        r"\b(run\s+code|execute|python|script|debug|analyze\s+logs?|server\s+logs?|diagnose)\b",
        r"\b(code\s+snippet|function|algorithm|program|calculate|compute)\b",
    ],
    "finance_audit": [
        r"\b(budget|invest|stock|portfolio|finance|financial|money|savings?|retirement|expense)\b",
        r"\b(mutual\s+fund|etf|crypto|market|trading|capital|wealth|tax|audit|risk|anomaly)\b",
    ],
    "general_utility": [
        r"\b(time|date|day|today|clock|calendar|month|year)\b",
        r"\b(what\s+time|current\s+time|what\s+day)\b",
    ],
}


class AgentRouter:
    """
    Routes user prompts to the appropriate agent.

    Uses LLM-based classification with keyword-based fallback.
    """

    async def classify(self, prompt: str) -> Optional[str]:
        """
        Classify user intent and return the agent name to handle it.
        """
        # Build the agent catalog for the classification prompt
        agents = agent_registry.list_agents()
        if not agents:
            logger.warning("AgentRouter: no agents registered")
            return None

        agent_list = "\n".join(
            f"  - \"{a['name']}\": {a['description']}"
            for a in agents
        )

        # Attempt LLM-based classification
        agent_name = await self._classify_with_llm(prompt, agent_list)
        if agent_name and agent_name in agent_registry:
            logger.info("AgentRouter (LLM): '%s' → agent '%s'", prompt[:50], agent_name)
            return agent_name

        # Fallback: keyword-based classification
        agent_name = self._classify_with_keywords(prompt)
        if agent_name:
            logger.info("AgentRouter (keyword fallback): '%s' → agent '%s'", prompt[:50], agent_name)
            return agent_name

        logger.info("AgentRouter: no agent matched for '%s'", prompt[:50])
        return None

    async def _classify_with_llm(self, prompt: str, agent_list: str) -> Optional[str]:
        """Use the base LLM to classify intent."""
        from backend.gateway.llm.client import get_llm_client
        
        classification_prompt = _CLASSIFICATION_PROMPT.format(
            agent_list=agent_list,
            user_prompt=prompt[:500],
        )

        try:
            client = get_llm_client()
            llm_response = await client.generate(
                prompt=classification_prompt,
                temperature=0.1
            )
            
            raw_text = llm_response.response.strip()

            # Extract JSON from response
            json_match = re.search(r"\{[^{}]*\}", raw_text, re.DOTALL)
            if not json_match:
                logger.warning("AgentRouter: no JSON in LLM response: %s", raw_text[:100])
                return None

            parsed = json.loads(json_match.group())
            agent_name = parsed.get("agent", "none")

            if agent_name == "none":
                return None

            return agent_name

        except Exception as e:
            logger.warning("AgentRouter LLM classification failed: %s", e)
            return None

    def _classify_with_keywords(self, prompt: str) -> Optional[str]:
        """Keyword-based fallback classification."""
        prompt_lower = prompt.lower()
        best_match = None
        best_score = 0

        for agent_name, patterns in _KEYWORD_PATTERNS.items():
            if agent_name not in agent_registry:
                continue
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, prompt_lower, re.IGNORECASE)
                score += len(matches)
            if score > best_score:
                best_score = score
                best_match = agent_name

        return best_match if best_score > 0 else None


# Module-level singleton
agent_router = AgentRouter()
