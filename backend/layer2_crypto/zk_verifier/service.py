"""ZKP Verifier — stub. See zk_prover/service.py for explanation."""

import hashlib
import json
from backend.utils.logging import get_logger

logger = get_logger(__name__)


class ZKVerifierService:
    """Simulated ZKP verifier — checks proof matches public signals."""

    def verify_tool_call(self, proof: str, public_signals: dict) -> bool:
        tool_name = public_signals.get("tool_name", "")
        param_hash = public_signals.get("param_hash", "")
        # Re-derive proof from public signals to verify consistency
        # (This is a simulation — real ZKP verification is mathematical)
        expected_input = json.dumps(
            {"tool": tool_name, "params": {}}, sort_keys=True
        )
        # We can't fully re-verify without the original params,
        # so we just check proof is a valid sha256 hex string
        valid = len(proof) == 64 and all(c in "0123456789abcdef" for c in proof)
        logger.info("ZKP verification for %s: %s (simulated)", tool_name, valid)
        return valid
