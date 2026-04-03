"""
Embedding Monitor — upgrade path for ASI.

Currently the ASICalculator uses bag-of-words cosine similarity.
When you want higher-quality semantic drift detection, swap this in:

    pip install sentence-transformers

Then replace _cosine_sim_simple in asi_calculator.py with this class.
"""

from __future__ import annotations
from typing import Optional
from backend.utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingMonitor:
    """
    Semantic drift monitor using sentence-transformers.
    Upgrade from the BoW similarity in ASICalculator.
    """

    def __init__(self):
        self._model = None

    def _load(self):
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("EmbeddingMonitor loaded sentence-transformers")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )

    def compute_similarity(self, prompt_a: str, prompt_b: str) -> float:
        """Cosine similarity between two prompts using sentence embeddings."""
        self._load()
        if self._model is None:
            # Fallback to BoW
            from backend.layer3_behavior_monitor.asi_calculator import _cosine_sim_simple
            return _cosine_sim_simple(prompt_a, prompt_b)

        import numpy as np
        emb = self._model.encode([prompt_a, prompt_b])
        a, b = emb[0], emb[1]
        cosine = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
        return max(0.0, cosine)
