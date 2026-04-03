"""Key Manager — only used when FHE_ENABLED=true in .env."""

from backend.utils.logging import get_logger

logger = get_logger(__name__)


class KeyManager:
    """Stub key manager. Wire to real service when FHE_ENABLED=true."""

    def get_public_key(self) -> bytes:
        raise NotImplementedError("Real key manager requires FHE_ENABLED=true and the key-manager docker service.")

    def decrypt_output(self, enc_output_b64: str, request_id: str) -> list:
        raise NotImplementedError("Real decryption requires FHE_ENABLED=true.")

    def rotate_keys(self) -> dict:
        raise NotImplementedError("Real key rotation requires FHE_ENABLED=true.")

    def sign_tool_call(self, payload: dict) -> str:
        import hmac, hashlib, json
        from backend.gateway.config import settings
        key = settings.secret_key.encode()
        msg = json.dumps(payload, sort_keys=True).encode()
        return hmac.new(key, msg, hashlib.sha256).hexdigest()
