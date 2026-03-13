import time

import jwt
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from pm_party_client.exceptions import PMAuthError

# Server-enforced ceiling
_MAX_LIFETIME = 3600


class TokenManager:
    """Handles Ed25519 JWT creation for party authentication."""

    def __init__(self, app_id: str, private_key_pem: str, token_lifetime: int = 600):
        if token_lifetime < 1 or token_lifetime > _MAX_LIFETIME:
            raise ValueError(f"token_lifetime must be between 1 and {_MAX_LIFETIME} seconds")

        self._app_id = app_id
        self._token_lifetime = token_lifetime

        try:
            self._private_key = load_pem_private_key(private_key_pem.encode(), password=None)
        except Exception as exc:
            raise PMAuthError(f"Failed to load Ed25519 private key: {exc}") from exc

    def generate_token(self) -> str:
        """Create a short-lived JWT signed with the Ed25519 private key."""
        now = int(time.time())
        payload = {
            "app_id": self._app_id,
            "iat": now,
            "exp": now + self._token_lifetime,
        }
        try:
            return jwt.encode(payload, self._private_key, algorithm="EdDSA")
        except Exception as exc:
            raise PMAuthError(f"Failed to sign JWT: {exc}") from exc
