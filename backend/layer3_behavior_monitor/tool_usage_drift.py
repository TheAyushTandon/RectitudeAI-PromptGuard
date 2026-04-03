"""
Tool Usage Drift detector.
Logic is currently baked into ASICalculator.t_tool.
This class is an upgrade path if you want chi-squared testing.
"""

from typing import List
from collections import Counter


class ToolUsageDrift:
    def check_drift(self, tool_history: List[str]) -> float:
        """
        Returns drift score 0–1.
        High score = unusual tool usage pattern.
        Currently: penalise new tools appearing in second half of window.
        """
        if len(tool_history) < 4:
            return 0.0
        half = len(tool_history) // 2
        first_half = set(t for t in tool_history[:half] if t)
        second_half = set(t for t in tool_history[half:] if t)
        new_tools = second_half - first_half
        return min(len(new_tools) * 0.25, 1.0)
