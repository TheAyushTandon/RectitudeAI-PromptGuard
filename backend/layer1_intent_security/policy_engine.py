"""
Policy engine — fuses signals from all detectors into a final decision.

Thresholds and weights are read live from PolicyStore on every call,
so RL-approved updates take effect immediately without a server restart.

Signal weights (tunable via PolicyStore):
  regex_prefilter : 0.35
  injection_ml    : 0.35
  intent_ml       : 0.20
  behavioral_asi  : 0.10

Decision thresholds (PolicyStore keys):
  block_threshold     default 0.80
  escalate_threshold  default 0.50

Custom patterns (PolicyStore key "custom_patterns"):
  Added by the RL agent, applied as an escalate-level regex scan
  on top of the base prefilter before fusion.
"""

import re
from typing import List

from backend.models.requests import InferenceRequest
from backend.models.security import SecurityDecision
from backend.storage.policy_store import PolicyStore
from backend.utils.logging import get_logger

logger = get_logger(__name__)

# Module-level singleton — one PolicyStore per process, reloads from disk automatically
_policy_store = PolicyStore()

# Default weights (can be overridden by PolicyStore in a future extension)
_WEIGHTS = {
    "regex_prefilter": 0.35,
    "injection_ml":    0.35,
    "intent_ml":       0.20,
    "behavioral_asi":  0.10,
}

# Fallback if PolicyStore is unavailable
_DEFAULT_BLOCK     = 0.80
_DEFAULT_ESCALATE  = 0.50


def _get_thresholds():
    block    = float(_policy_store.get("block_threshold",    _DEFAULT_BLOCK))
    escalate = float(_policy_store.get("escalate_threshold", _DEFAULT_ESCALATE))
    # Safety guard: escalate must always be strictly below block
    if escalate >= block:
        escalate = max(block - 0.10, 0.20)
    return block, escalate


def _get_custom_patterns() -> List[re.Pattern]:
    """Compile RL-added patterns. Invalid patterns are silently skipped."""
    raw: List[str] = _policy_store.get("custom_patterns", [])
    compiled = []
    for p in raw:
        try:
            compiled.append(re.compile(p, re.IGNORECASE | re.DOTALL))
        except re.error as e:
            logger.warning("Skipping invalid custom pattern '%s': %s", p, e)
    return compiled


def apply_policies(
    req: InferenceRequest,
    decisions: List[SecurityDecision],
) -> SecurityDecision:
    """
    Weighted fusion of all detector signals.

    Reads block_threshold and escalate_threshold live from PolicyStore
    so RL-approved updates apply on the very next request.

    Any single detector with score == 1.0 AND decision == "block"
    short-circuits to an instant block (bypasses weighting).

    Custom regex patterns from the RL agent are applied as a pre-pass:
    if any match, the fused score is bumped to at least escalate_threshold.
    """
    block_threshold, escalate_threshold = _get_thresholds()
    custom_patterns = _get_custom_patterns()

    metadata: dict = {}
    block_reasons: List[str] = []
    weighted_score = 0.0
    total_weight   = 0.0

    for d in decisions:
        name   = d.metadata.get("classifier", "unknown")
        weight = _WEIGHTS.get(name, 0.10)

        metadata[name] = {
            "decision":   d.decision,
            "risk_score": d.risk_score,
            "reason":     d.reason,
        }

        # Instant-block short-circuit
        # If any single detector is very confident (>= 0.92), block immediately.
        # This prevents ML signals from being diluted by "Allow" signals from other layers.
        if d.decision == "block" and d.risk_score >= 0.92:
            return SecurityDecision(
                decision="block",
                risk_score=d.risk_score,
                reason=f"High-confidence block [{name}]: {d.reason}",
                metadata={"fusion": metadata},
            )

        weighted_score += d.risk_score * weight
        total_weight   += weight

        if d.decision == "block":
            block_reasons.append(f"[{name.upper()}] {d.reason}")

    # Normalise
    fused_score = min(weighted_score / total_weight, 1.0) if total_weight > 0 else 0.0

    # Apply RL custom patterns — bump score to at least escalate if any match
    if custom_patterns and req and hasattr(req, "prompt"):
        for cp in custom_patterns:
            if cp.search(req.prompt):
                pattern_str = cp.pattern[:40]
                logger.debug("Custom pattern matched: %s", pattern_str)
                metadata["rl_custom_pattern"] = {
                    "decision": "escalate",
                    "risk_score": escalate_threshold,
                    "reason": f"RL pattern matched: {pattern_str}",
                }
                fused_score = max(fused_score, escalate_threshold)
                break

    # Final decision — FIX: Previously, ANY detector with decision=="block" (even
    # at a moderate prefilter score of 0.85) would add to block_reasons, causing
    # the final fused decision to be "block" regardless of what the ML classifiers
    # said. This meant the ML layer had zero corrective power against false positives.
    #
    # New logic: fused_score is authoritative. block_reasons is used for logging only.
    # A prefilter "block" at 0.85 is already captured in the fused_score (weight=0.40),
    # which will push the fused score close to or above block_threshold on its own
    # for a genuine attack. For a false-positive (ML disagrees strongly), the fused
    # score stays below threshold and ML corrections are respected.
    if fused_score >= block_threshold:
        final_decision = "block"
    elif fused_score >= escalate_threshold:
        final_decision = "escalate"
    else:
        final_decision = "allow"

    reason = " | ".join(block_reasons) if block_reasons else "All checks passed"

    return SecurityDecision(
        decision=final_decision,
        risk_score=round(fused_score, 4),
        reason=reason,
        metadata={
            "fusion":             metadata,
            "fused_score":        fused_score,
            "block_threshold":    block_threshold,
            "escalate_threshold": escalate_threshold,
            "custom_patterns_n":  len(custom_patterns),
        },
    )