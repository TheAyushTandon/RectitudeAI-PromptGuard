"""
Audit logger — append-only JSON-lines file with in-memory cache for dashboard.
"""

from __future__ import annotations
import json
import os
import uuid
from datetime import datetime
from typing import List, Optional
from backend.utils.logging import get_logger

logger = get_logger(__name__)

LOG_PATH = "logs/audit.jsonl"
MAX_IN_MEMORY = 500


class AuditLogger:
    def __init__(self, log_path: str = LOG_PATH):
        self.path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self._cache: List[dict] = []

    def log_event(self, event: dict):
        entry = {
            "event_id": str(uuid.uuid4())[:12],
            "timestamp": datetime.utcnow().isoformat(),
            **event,
        }
        # Severity inference
        score = event.get("risk_score", 0)
        decision = event.get("decision", "allow")
        if decision == "block" or score >= 0.80:
            entry["severity"] = "critical"
        elif decision == "escalate" or score >= 0.50:
            entry["severity"] = "warning"
        else:
            entry["severity"] = "info"

        try:
            with open(self.path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError as e:
            logger.error("Audit write failed: %s", e)

        self._cache.append(entry)
        if len(self._cache) > MAX_IN_MEMORY:
            self._cache = self._cache[-MAX_IN_MEMORY:]

    def get_logs(
        self,
        limit: int = 50,
        severity: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[dict]:
        logs = list(reversed(self._cache))
        if severity:
            logs = [l for l in logs if l.get("severity") == severity]
        if user_id:
            logs = [l for l in logs if l.get("user_id") == user_id]
        return logs[:limit]

    def get_stats(self) -> dict:
        total = len(self._cache)
        blocked = sum(1 for l in self._cache if l.get("decision") == "block")
        escalated = sum(1 for l in self._cache if l.get("decision") == "escalate")
        avg_score = (
            sum(l.get("risk_score", 0) for l in self._cache) / total
            if total > 0 else 0.0
        )
        return {
            "total_requests": total,
            "blocked": blocked,
            "escalated": escalated,
            "allowed": total - blocked - escalated,
            "block_rate": round(blocked / total, 4) if total else 0,
            "avg_risk_score": round(avg_score, 4),
        }
