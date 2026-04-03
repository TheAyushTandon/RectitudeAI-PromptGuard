"""
Tier-2 ML injection classifier.
Uses protectai/deberta-v3-base-prompt-injection-v2 which is trained
specifically on injection patterns, not content moderation.
Lazy-loaded so startup is fast.
"""

from __future__ import annotations
from backend.models.security import SecurityDecision
from backend.utils.logging import get_logger

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    _ML_AVAILABLE = True
except ImportError:
    _ML_AVAILABLE = False

logger = get_logger(__name__)

# Primary model: purpose-built for prompt injection detection
_PRIMARY_MODEL = "protectai/deberta-v3-base-prompt-injection-v2"
# Fallback: the fine-tuned local model you trained
_LOCAL_MODEL = "data/models/injection_classifier"

THRESHOLD_BLOCK = 0.80
THRESHOLD_ESCALATE = 0.50


class InjectionClassifier:
    """DeBERTa-based prompt injection classifier. Lazy-loaded on first use."""

    def __init__(self):
        self._tokenizer = None
        self._model = None
        self._device = "cuda" if (_ML_AVAILABLE and torch.cuda.is_available()) else "cpu"
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        if not _ML_AVAILABLE:
            logger.warning("InjectionClassifier: torch/transformers not installed, running in passthrough mode")
            return
        for model_id in [_LOCAL_MODEL, _PRIMARY_MODEL]:
            try:
                self._tokenizer = AutoTokenizer.from_pretrained(model_id)
                self._model = AutoModelForSequenceClassification.from_pretrained(model_id)
                self._model.eval()
                self._model.to(self._device)
                logger.info("InjectionClassifier loaded from %s on %s", model_id, self._device)
                self._loaded = True
                return
            except Exception as e:
                logger.warning("Could not load %s: %s", model_id, e)
        logger.error("InjectionClassifier: all model sources failed, running in passthrough mode")

    async def classify(self, prompt: str) -> SecurityDecision:
        self._load()

        if not self._loaded or self._model is None:
            return SecurityDecision(
                decision="allow",
                risk_score=0.0,
                reason="Classifier unavailable — passthrough",
                metadata={"classifier": "injection_ml"},
            )

        inputs = self._tokenizer(
            prompt, return_tensors="pt", truncation=True,
            padding=True, max_length=512,
        )
        inputs = {k: v.to(self._device) for k, v in inputs.items()}

        with torch.no_grad():
            logits = self._model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).squeeze()

        # label 1 = injection for both models
        injection_prob = float(probs[1]) if probs.ndim > 0 else float(probs)

        if injection_prob >= THRESHOLD_BLOCK:
            decision, reason = "block", f"Injection probability {injection_prob:.2%}"
        elif injection_prob >= THRESHOLD_ESCALATE:
            decision, reason = "escalate", f"Moderate injection signal {injection_prob:.2%}"
        else:
            decision, reason = "allow", "No injection detected"

        return SecurityDecision(
            decision=decision,
            risk_score=round(injection_prob, 4),
            reason=reason,
            metadata={"classifier": "injection_ml", "model": self._model.config.name_or_path if hasattr(self._model.config, 'name_or_path') else "loaded"},
        )