"""
FHE Engine — simulated mode.

Real FHE (concrete-ml) is disabled due to version incompatibilities.
This module provides a SimulatedFHEEngine that demonstrates the concept
correctly in the demo without the 1000x latency penalty.

When concrete-ml stabilises, swap SimulatedFHEEngine for the real
FHEEngine in backend/layer2_crypto/capability_tokens.py.
"""

import numpy as np
from backend.utils.logging import get_logger

logger = get_logger(__name__)


class FHEEngine:
    """
    Real FHE engine — currently non-functional due to concrete-ml
    version incompatibilities. Kept for future use.
    Set FHE_ENABLED=false and FHE_SIMULATED=true in .env.
    """

    def encrypt_features(self, features: np.ndarray) -> str:
        raise NotImplementedError(
            "Real FHE is disabled. Set FHE_ENABLED=false and FHE_SIMULATED=true."
        )

    def run_encrypted_inference(self, features: np.ndarray) -> dict:
        raise NotImplementedError("Real FHE is disabled.")

    def is_ready(self) -> bool:
        return False


class SimulatedFHEEngine:
    """
    Demonstrates FHE concept without the computational overhead.
    Used in demo when FHE_SIMULATED=true.

    Simulates the pipeline:
      1. Feature extraction (already done by features.py)
      2. Quantisation (float → int, as FHE requires integers)
      3. Encrypted classification (simulated)
      4. Decryption of result

    The security concept is real — in true FHE, step 3 happens on
    encrypted data the server cannot read. We show the interface,
    not the cryptographic primitive.
    """

    def quantise(self, features: np.ndarray, n_bits: int = 8) -> np.ndarray:
        """Simulate quantisation-aware step FHE requires."""
        scale = (2 ** n_bits - 1)
        f_min, f_max = features.min(), features.max()
        if f_max == f_min:
            return np.zeros_like(features, dtype=np.int32)
        normalised = (features - f_min) / (f_max - f_min)
        return (normalised * scale).astype(np.int32)

    def run_encrypted_inference(self, features: np.ndarray) -> dict:
        """
        Simulated encrypted inference.
        Returns label + score as if a real FHE circuit ran.
        """
        quantised = self.quantise(features)
        # Simulate: use weighted sum of first 4 features as classifier
        weights = np.array([0.4, 0.3, 0.2, 0.1])
        score = float(np.dot(quantised[:4], weights)) / (255 * weights.sum())
        score = min(max(score, 0.0), 1.0)
        label = "injection" if score > 0.5 else "benign"

        logger.info(
            "SimulatedFHE: label=%s score=%.4f (simulated — not real FHE)",
            label, score,
        )
        return {
            "label": label,
            "score": round(score, 4),
            "mode": "fhe_simulated",
            "quantised_features": quantised[:4].tolist(),
            "note": "Simulated FHE — demonstrates interface, not cryptographic execution",
        }

    def is_ready(self) -> bool:
        return True
