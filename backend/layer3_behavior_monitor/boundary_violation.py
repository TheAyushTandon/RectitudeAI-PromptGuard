"""
Boundary Violation Detector.
Detects when a user re-attempts a blocked intent in subsequent turns.
This signal feeds into ASICalculator.b_boundaries.
"""

from typing import List


class BoundaryViolationDetector:
    def detect_violation(self, current_prompt: str, blocked_history: List[str]) -> bool:
        """
        Returns True if current prompt semantically resembles
        a previously blocked prompt — persistence after refusal.
        """
        if not blocked_history:
            return False
        from backend.layer3_behavior_monitor.asi_calculator import _cosine_sim_simple
        for past in blocked_history[-3:]:  # check last 3 blocked prompts
            sim = _cosine_sim_simple(current_prompt, past)
            if sim > 0.55:
                return True
        return False
