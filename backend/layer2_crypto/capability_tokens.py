"""
Capability Token Service — cryptographic authority separation.

Instead of FHE (which is broken by version incompatibilities and
kills performance), we use short-lived JWT capability tokens that
encode exactly which tools this session is allowed to call.

The LLM cannot forge these. The sandbox checks the token before
executing any tool call. This is the differentiator vs Lakera.

Token payload:
  sub:      session/user id
  scope:    list of allowed tool names
  exp:      short TTL (default 5 minutes)
  jti:      unique token id (for revocation)
  iat:      issued-at
"""

from __future__ import annotations
import uuid
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Optional

from jose import jwt, JWTError
from backend.gateway.config import settings
from backend.utils.logging import get_logger

logger = get_logger(__name__)

# All tools that exist in the system — anything not in this list
# is rejected outright regardless of what the LLM tries to call.
# FIX: Added "calculator", "fetch_stock_price", and "get_current_time" which
# are used by FinancialAdvisorAgent and GeneralAgent but were absent from KNOWN_TOOLS.
# Without these, CapabilityTokenService.get_default_scope() always produced an empty
# effective_scope for those agents, and their tools were invoked with zero token coverage.
KNOWN_TOOLS = {
    "read_file", "write_file", "delete_file",
    "search_web", "send_email", "read_crm",
    "log_ticket", "query_database", "execute_code",
    "read_calendar", "create_task",
    # Agent-specific low-risk tools
    "calculator", "fetch_stock_price", "get_current_time",
}

# Risk tiers: high-risk tools require explicit scope grant
HIGH_RISK_TOOLS = {"delete_file", "send_email", "execute_code", "query_database"}

TOKEN_TTL_SECONDS = 300  # 5 minutes


class CapabilityTokenService:

    def issue_token(
        self,
        session_id: str,
        allowed_tools: List[str],
        ttl_seconds: int = TOKEN_TTL_SECONDS,
    ) -> str:
        """Issue a signed JWT token scoped to the given tools."""
        # Sanitise — only grant tools that actually exist
        safe_tools = [t for t in allowed_tools if t in KNOWN_TOOLS]

        payload = {
            "sub": session_id,
            "scope": safe_tools,
            "jti": str(uuid.uuid4()),
            "iat": int(datetime.utcnow().timestamp()),
            "exp": datetime.utcnow() + timedelta(seconds=ttl_seconds),
        }
        token = jwt.encode(payload, settings.secret_key, algorithm="HS256")
        logger.info("Capability token issued for %s, scope=%s", session_id, safe_tools)
        return token

    def verify_tool_call(self, token: str, tool_name: str) -> tuple[bool, str]:
        """
        Returns (allowed, reason).
        Call this before executing any tool.
        """
        if not token:
            return False, "No capability token provided"

        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        except JWTError as e:
            return False, f"Invalid capability token: {e}"

        scope: List[str] = payload.get("scope", [])

        if tool_name not in KNOWN_TOOLS:
            return False, f"Unknown tool: {tool_name}"

        if tool_name not in scope:
            return False, f"Tool '{tool_name}' not in session scope {scope}"

        return True, "Authorised"

    def sign_tool_call(self, tool_name: str, params: dict) -> str:
        """HMAC-sign a tool call for audit trail integrity."""
        payload = json.dumps({"tool": tool_name, "params": params}, sort_keys=True)
        return hmac.new(
            settings.secret_key.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

    def get_default_scope(self, risk_score: float) -> List[str]:
        """
        Returns a safe default tool scope based on session risk.
        High-risk sessions get minimal scope.
        """
        if risk_score >= 0.50:
            # Suspicious session: read-only, no external actions
            return ["read_file", "search_web", "read_crm"]
        elif risk_score >= 0.25:
            # Moderate risk: no destructive tools
            return [t for t in KNOWN_TOOLS if t not in HIGH_RISK_TOOLS]
        else:
            # Clean session: full scope
            return list(KNOWN_TOOLS)


# Simulated FHE wrapper — keeps the concept in the demo without the crashes
class SimulatedFHEEngine:
    """
    Placeholder for FHE. Returns a clearly-labelled simulated result.
    In the demo, this shows the concept without the concrete-ml version hell.
    Replace with real FHEEngine when concrete-ml stabilises.
    """

    def run_encrypted_inference(self, features) -> dict:
        import numpy as np
        # Simulate: sum of first 4 feature values determines classification
        score = float(np.sum(features[:4])) / (float(np.sum(np.abs(features))) + 1e-8)
        label = "injection" if score > 0.5 else "benign"
        return {
            "label": label,
            "score": round(score, 4),
            "mode": "fhe_simulated",
            "note": "FHE simulation — real FHE pending concrete-ml compatibility fix",
        }

    def is_ready(self) -> bool:
        return True