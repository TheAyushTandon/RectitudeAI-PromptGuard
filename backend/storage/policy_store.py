"""
Policy Store — central runtime configuration for thresholds and rules.
Designed to accept updates from the RL policy updater without restarts.
"""

from __future__ import annotations
import json
import os
from typing import Any
from backend.utils.logging import get_logger

logger = get_logger(__name__)

_DEFAULTS = {
    "block_threshold": 0.80,
    "escalate_threshold": 0.50,
    "asi_alert_threshold": 0.45,
    "max_risk_score": 0.85,
    "blocked_intents": ["data_exfiltration", "unauthorized_access", "prompt_injection"],
    "custom_patterns": [],   # RL agent adds patterns here
}

POLICY_FILE = "logs/active_policy.json"


class PolicyStore:
    def __init__(self):
        self._policies = dict(_DEFAULTS)
        self._load_from_disk()

    def _load_from_disk(self):
        if os.path.exists(POLICY_FILE):
            try:
                with open(POLICY_FILE) as f:
                    saved = json.load(f)
                self._policies.update(saved)
                logger.info("PolicyStore loaded from %s", POLICY_FILE)
            except Exception as e:
                logger.warning("Could not load policy file: %s", e)

    def get(self, key: str, default: Any = None) -> Any:
        return self._policies.get(key, default)

    def set(self, key: str, value: Any):
        """Apply a policy update. Called by approved RL updates."""
        self._policies[key] = value
        self._save()
        logger.info("PolicyStore updated: %s = %s", key, value)

    def _save(self):
        os.makedirs(os.path.dirname(POLICY_FILE), exist_ok=True)
        with open(POLICY_FILE, "w") as f:
            json.dump(self._policies, f, indent=2)

    def add_custom_pattern(self, pattern: str):
        patterns = self._policies.get("custom_patterns", [])
        if pattern not in patterns:
            patterns.append(pattern)
            self.set("custom_patterns", patterns)

    def get_all(self) -> dict:
        return dict(self._policies)
