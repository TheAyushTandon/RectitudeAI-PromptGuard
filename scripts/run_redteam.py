#!/usr/bin/env python3
"""
Red Team Runner — CLI tool to run the attack suite.

Usage:
    python scripts/run_redteam.py           # regex tier only (fast)
    python scripts/run_redteam.py --full    # includes ML classifiers (slow, needs models)

Output: logs/vulnerability_report.json
"""

import sys
import asyncio
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.layer4_red_teaming.attack_runner import AttackRunner

if __name__ == "__main__":
    use_full = "--full" in sys.argv
    runner = AttackRunner()

    print("\nRectitudeAI Red Team Runner")
    print("─" * 40)
    if use_full:
        print("Mode: Full pipeline (regex + ML classifiers)")
        print("Note: ML models must be downloaded. This may take a while.")
    else:
        print("Mode: Tier-1 regex prefilter only (fast)")
        print("Tip: use --full to include ML classifiers")
    print()

    asyncio.run(runner.run_async(use_full_pipeline=use_full))
