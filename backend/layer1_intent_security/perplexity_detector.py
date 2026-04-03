"""
Perplexity-based obfuscation detector (Tier-2).
High perplexity = unusual / encoded text = potential attack obfuscation.
GPT-2 is small enough to be acceptable in async path.
Lazy-loaded.
"""

from __future__ import annotations
from backend.models.security import SecurityDecision
from backend.utils.logging import get_logger

try:
    import torch
    from transformers import GPT2LMHeadModel, GPT2TokenizerFast
    _ML_AVAILABLE = True
except ImportError:
    _ML_AVAILABLE = False

logger = get_logger(__name__)

_MODEL_ID = "gpt2"   # gpt2 not gpt2-medium — smaller, faster, good enough
# Calibrated on benign chat prompts:
# Normal prompts:   perplexity ~50–300
# Encoded/garbled:  perplexity ~5000+
THRESHOLD_BLOCK     = 8000.0
THRESHOLD_ESCALATE  = 3000.0


class PerplexityDetector:
    """GPT-2 perplexity scorer. Lazy-loaded."""

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._device = "cuda" if (_ML_AVAILABLE and torch.cuda.is_available()) else "cpu"

    def _load(self):
        if self._model is not None:
            return
        if not _ML_AVAILABLE:
            logger.warning("PerplexityDetector: torch/transformers not installed, running in passthrough mode")
            return
        try:
            self._tokenizer = GPT2TokenizerFast.from_pretrained(_MODEL_ID)
            self._model = GPT2LMHeadModel.from_pretrained(_MODEL_ID)
            self._model.eval()
            self._model.to(self._device)
            logger.info("PerplexityDetector loaded (%s) on %s", _MODEL_ID, self._device)
        except Exception as e:
            logger.error("PerplexityDetector load failed: %s", e)

    async def classify(self, prompt: str) -> SecurityDecision:
        self._load()

        if self._model is None or not prompt.strip():
            return SecurityDecision(
                decision="allow", risk_score=0.0,
                reason="Perplexity detector unavailable or empty prompt",
                metadata={"classifier": "perplexity"},
            )

        enc = self._tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=512,
        )
        ids = enc.input_ids.to(self._device)
        n_tokens = ids.shape[1]

        with torch.no_grad():
            loss = self._model(ids, labels=ids).loss
            perplexity = torch.exp(loss).item()

        # Short prompts are naturally high-perplexity — be lenient
        effective_block = THRESHOLD_BLOCK * (2.0 if n_tokens < 5 else 1.0)
        effective_escalate = THRESHOLD_ESCALATE * (1.5 if n_tokens < 10 else 1.0)

        if perplexity >= effective_block:
            decision = "block"
            reason = f"Extreme perplexity {perplexity:.0f} — likely obfuscation"
        elif perplexity >= effective_escalate:
            decision = "escalate"
            reason = f"High perplexity {perplexity:.0f} — possible encoding"
        else:
            decision = "allow"
            reason = f"Normal perplexity {perplexity:.0f}"

        risk_score = min(perplexity / effective_block, 1.0)

        return SecurityDecision(
            decision=decision,
            risk_score=round(risk_score, 4),
            reason=reason,
            metadata={
                "classifier": "perplexity",
                "raw_perplexity": round(perplexity, 2),
                "token_count": n_tokens,
            },
        )