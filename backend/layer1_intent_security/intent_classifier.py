"""
Tier-2 ML intent classifier.
Hybrid model combining NSFW detection and Toxicity detection.
- NSFW: michellejieli/NSFW_text_classifier
- Toxicity: unitary/toxic-bert
"""

from __future__ import annotations
from backend.models.security import SecurityDecision
from backend.utils.logging import get_logger

try:
    import torch
    from transformers import pipeline
    _ML_AVAILABLE = True
except ImportError:
    _ML_AVAILABLE = False

logger = get_logger(__name__)

# Models to use for hybrid detection
NSFW_MODEL = "michellejieli/NSFW_text_classifier"
TOXIC_MODEL = "unitary/toxic-bert"

THRESHOLD_BLOCK = 0.70
THRESHOLD_ESCALATE = 0.40


class IntentClassifier:
    """Hybrid intent classifier (NSFW + Toxicity). Lazy-loaded for performance."""

    def __init__(self):
        self._nsfw_pipeline = None
        self._toxic_pipeline = None
        self._device = "cuda" if (_ML_AVAILABLE and torch.cuda.is_available()) else "cpu"
        self._loaded = False

    def _load(self):
        """Pre-warm the models. Called during FastAPI startup lifespan."""
        if self._loaded:
            return
        if not _ML_AVAILABLE:
            logger.warning("IntentClassifier: torch/transformers not installed, running in passthrough mode")
            return

        try:
            logger.info("IntentClassifier: Loading NSFW model %s on %s...", NSFW_MODEL, self._device)
            # Use pipeline for simplicity as per reference, but specify device
            device_idx = 0 if self._device == "cuda" else -1
            self._nsfw_pipeline = pipeline("text-classification", model=NSFW_MODEL, device=device_idx)
            
            logger.info("IntentClassifier: Loading Toxicity model %s on %s...", TOXIC_MODEL, self._device)
            self._toxic_pipeline = pipeline("text-classification", model=TOXIC_MODEL, device=device_idx)
            
            self._loaded = True
            logger.info("IntentClassifier: Hybrid models loaded successfully.")
        except Exception as e:
            logger.error("Failed to load IntentClassifier models: %s", e)

    async def classify(self, prompt: str) -> SecurityDecision:
        """Run the hybrid classification."""
        self._load()

        if not self._loaded or not self._nsfw_pipeline or not self._toxic_pipeline:
            return SecurityDecision(
                decision="allow",
                risk_score=0.0,
                reason="Classifier unavailable — passthrough",
                metadata={"classifier": "intent_ml"},
            )

        try:
            # NSFW check
            nsfw_res = self._nsfw_pipeline(prompt)[0]
            # label can be 'SFW' or 'NSFW'
            nsfw_score = nsfw_res['score'] if nsfw_res['label'] == 'NSFW' else (1.0 - nsfw_res['score'])
            
            # Toxicity check
            toxic_res = self._toxic_pipeline(prompt)[0]
            # toxic-bert has 'toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate' or 'neutral'
            # Reference logic used 'neutral' vs others
            is_toxic = toxic_res['label'] != 'neutral'
            toxic_score = toxic_res['score'] if is_toxic else (1.0 - toxic_res['score'])

            risk_score = max(nsfw_score, toxic_score)
            
            if risk_score >= THRESHOLD_BLOCK:
                decision, reason = "block", f"Harmful intent detected (NSFW/Toxicity max score: {risk_score:.2%})"
            elif risk_score >= THRESHOLD_ESCALATE:
                decision, reason = "escalate", f"Moderate harmful signal (NSFW/Toxicity: {risk_score:.2%})"
            else:
                decision, reason = "allow", "Harmful intent check passed"

            return SecurityDecision(
                decision=decision,
                risk_score=round(risk_score, 4),
                reason=reason,
                metadata={
                    "classifier": "intent_ml",
                    "nsfw_score": round(nsfw_score, 4),
                    "toxic_score": round(toxic_score, 4),
                },
            )
        except Exception as e:
            logger.error("IntentClassifier classification error: %s", e)
            return SecurityDecision(
                decision="allow",
                risk_score=0.0,
                reason=f"Classification error: {str(e)}",
                metadata={"classifier": "intent_ml"},
            )
