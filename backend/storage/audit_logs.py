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
        self._load_from_disk()

    def _load_from_disk(self):
        """Loads the last MAX_IN_MEMORY entries from the log file into cache."""
        if not os.path.exists(self.path):
            return
        
        try:
            with open(self.path, "r") as f:
                # For very large files, we should seek to the end, but for JSONL we can handle reading
                all_lines = f.readlines()
                last_lines = all_lines[-MAX_IN_MEMORY:]
                for line in last_lines:
                    try:
                        self._cache.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            logger.info("Loaded %d historical logs into dashboard cache", len(self._cache))
        except Exception as e:
            logger.error("Failed to load audit logs from disk: %s", e)

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
        """Returns aggregated stats based on the full cache."""
        total = len(self._cache)
        if total == 0:
            return {
                "total_requests": 0,
                "blocked": 0,
                "escalated": 0,
                "allowed": 0,
                "block_rate": 0,
                "avg_risk_score": 0.0,
            }

        blocked = sum(1 for l in self._cache if l.get("decision") == "block")
        escalated = sum(1 for l in self._cache if l.get("decision") == "escalate")
        avg_score = sum(l.get("risk_score", 0.0) for l in self._cache) / total
        avg_latency = sum(l.get("latency", 0.0) for l in self._cache) / total
        
        return {
            "total_requests": total,
            "blocked": blocked,
            "escalated": escalated,
            "allowed": total - blocked - escalated,
            "block_rate": round(blocked / total, 4),
            "avg_risk_score": round(avg_score, 4),
            "avg_latency_ms": round(avg_latency, 2),
        }

    def save_settings(self, settings_dict: dict):
        """Persists dynamic dashboard settings to a JSON file."""
        config_path = "logs/dynamic_settings.json"
        try:
            with open(config_path, "w") as f:
                json.dump(settings_dict, f, indent=4)
            logger.info("Saved dynamic settings to %s", config_path)
        except Exception as e:
            logger.error("Failed to save dynamic settings: %s", e)

    def load_settings(self) -> Optional[dict]:
        """Loads persisted dashboard settings."""
        config_path = "logs/dynamic_settings.json"
        if not os.path.exists(config_path):
            return None
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to load dynamic settings: %s", e)
            return None
