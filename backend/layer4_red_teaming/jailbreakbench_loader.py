"""
JailbreakBench loader — reads adversarial prompt datasets from parquet files.
Used by the red team attack runner.
"""

from __future__ import annotations
import os
from typing import List
from backend.utils.logging import get_logger

logger = get_logger(__name__)


class JailbreakBenchLoader:
    def __init__(self, dataset_path: str = "data/attacks"):
        self.path = dataset_path

    def load_attacks(self, category: str = "all") -> List[dict]:
        """Return attack prompts from the JailbreakBench dataset."""
        try:
            import pandas as pd
        except ImportError:
            logger.error("pandas not installed")
            return []

        attacks = []
        for fname in ["train.parquet", "test.parquet"]:
            fpath = os.path.join(self.path, fname)
            if not os.path.exists(fpath):
                logger.warning("Dataset not found: %s", fpath)
                continue
            try:
                df = pd.read_parquet(fpath)
                for _, row in df.iterrows():
                    label = int(row.get("label", 0))
                    if category == "attacks" and label != 1:
                        continue
                    if category == "benign" and label != 0:
                        continue
                    attacks.append({
                        "id": f"JBB_{len(attacks):04d}",
                        "category": "jailbreakbench" if label == 1 else "legitimate",
                        "prompt": str(row.get("text", row.get("prompt", ""))),
                        "label": label,
                    })
                logger.info("Loaded %d entries from %s", len(attacks), fname)
            except Exception as e:
                logger.error("Error loading %s: %s", fname, e)

        return attacks
