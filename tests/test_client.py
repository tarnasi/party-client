import pytest
import httpx
import respx

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from pm_party_client import PartyClient, AsyncPartyClient
from pm_party_client.exceptions import PMGraphQLError, PMConnectionError, PMAuthError


def _make_private_key() -> str:
    priv = Ed25519PrivateKey.generate()
    return priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()


FAKE_URL = "https://pm.test/graphql"


class TestPartyClient:
    def test_missing_key_raises(self):
        with pytest.raises(PMAuthError):
            PartyClient(url=FAKE_URL, app_id="x")

    @respx.mock
    def test_query_success(self):
        priv_pem = _make_private_key()

        respx.post(FAKE_URL).respond(
            json={"data": {"getParties": [{"app_id": "123"}]}}
        )

        with PartyClient(url=FAKE_URL, app_id="test", private_key=priv_pem) as client:
            result = client.query("query { getParties { app_id } }")

        assert result == {"getParties": [{"app_id": "123"}]}

    @respx.mock
    def test_graphql_errors_raise(self):
        priv_pem = _make_private_key()

        respx.post(FAKE_URL).respond(
            json={"data": None, "errors": [{"message": "Auth required"}]}
        )

        with PartyClient(url=FAKE_URL, app_id="test", private_key=priv_pem) as client:
            with pytest.raises(PMGraphQLError) as exc_info:
                client.query("query { me { id } }")

        assert len(exc_info.value.errors) == 1

    @respx.mock
    def test_http_error_raises(self):
        priv_pem = _make_private_key()

        respx.post(FAKE_URL).respond(status_code=500, text="Internal Server Error")

        with PartyClient(url=FAKE_URL, app_id="test", private_key=priv_pem) as client:
            with pytest.raises(PMConnectionError):
                client.query("query { me { id } }")


class TestAsyncPartyClient:
    @respx.mock
    @pytest.mark.asyncio
    async def test_async_query_success(self):
        priv_pem = _make_private_key()

        respx.post(FAKE_URL).respond(
            json={"data": {"getParties": [{"app_id": "456"}]}}
        )

        async with AsyncPartyClient(url=FAKE_URL, app_id="test", private_key=priv_pem) as client:
            result = await client.query("query { getParties { app_id } }")

        assert result == {"getParties": [{"app_id": "456"}]}
