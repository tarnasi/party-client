import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from pm_party_client.auth import TokenManager
from pm_party_client.exceptions import PMAuthError


def _generate_test_keypair() -> tuple[str, str]:
    """Generate a throwaway Ed25519 key pair for tests."""
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    priv_pem = priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    pub_pem = pub.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return pub_pem, priv_pem


class TestTokenManager:
    def test_generate_token_contains_required_claims(self):
        pub_pem, priv_pem = _generate_test_keypair()
        mgr = TokenManager(app_id="test-app", private_key_pem=priv_pem, token_lifetime=300)

        token = mgr.generate_token()

        # Verify with public key
        payload = jwt.decode(token, pub_pem, algorithms=["EdDSA"])
        assert payload["app_id"] == "test-app"
        assert "iat" in payload
        assert "exp" in payload
        assert payload["exp"] - payload["iat"] == 300

    def test_token_lifetime_bounds(self):
        _, priv_pem = _generate_test_keypair()

        with pytest.raises(ValueError):
            TokenManager(app_id="x", private_key_pem=priv_pem, token_lifetime=0)

        with pytest.raises(ValueError):
            TokenManager(app_id="x", private_key_pem=priv_pem, token_lifetime=7200)

    def test_bad_private_key_raises(self):
        with pytest.raises(PMAuthError):
            TokenManager(app_id="x", private_key_pem="not-a-key")

    def test_default_lifetime_is_600(self):
        pub_pem, priv_pem = _generate_test_keypair()
        mgr = TokenManager(app_id="test", private_key_pem=priv_pem)

        token = mgr.generate_token()
        payload = jwt.decode(token, pub_pem, algorithms=["EdDSA"])
        assert payload["exp"] - payload["iat"] == 600
