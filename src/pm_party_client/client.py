from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from pm_party_client.auth import TokenManager
from pm_party_client.exceptions import PMAuthError, PMConnectionError, PMGraphQLError


def _load_key(private_key: str | None, private_key_path: str | None) -> str:
    """Resolve private key from string or file path."""
    if private_key:
        return private_key
    if private_key_path:
        path = Path(private_key_path)
        if not path.is_file():
            raise PMAuthError(f"Private key file not found: {private_key_path}")
        return path.read_text()
    raise PMAuthError("Provide either 'private_key' or 'private_key_path'")


class PartyClient:
    """Synchronous GraphQL client for PM third-party authentication."""

    def __init__(
        self,
        url: str,
        app_id: str,
        *,
        private_key: str | None = None,
        private_key_path: str | None = None,
        token_lifetime: int = 600,
        timeout: float = 30.0,
    ):
        key_pem = _load_key(private_key, private_key_path)
        self._url = url
        self._token_mgr = TokenManager(app_id, key_pem, token_lifetime)
        self._http = httpx.Client(timeout=timeout)

    # -- public API ----------------------------------------------------------

    def query(
        self,
        query: str,
        *,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self.execute(query, variables=variables, operation_name=operation_name, headers=headers)

    def mutate(
        self,
        query: str,
        *,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self.execute(query, variables=variables, operation_name=operation_name, headers=headers)

    def execute(
        self,
        query: str,
        *,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        token = self._token_mgr.generate_token()

        req_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if headers:
            req_headers.update(headers)

        body: dict[str, Any] = {"query": query}
        if variables is not None:
            body["variables"] = variables
        if operation_name is not None:
            body["operationName"] = operation_name

        try:
            resp = self._http.post(self._url, json=body, headers=req_headers)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise PMConnectionError(f"HTTP {exc.response.status_code}: {exc.response.text}") from exc
        except httpx.HTTPError as exc:
            raise PMConnectionError(f"Connection error: {exc}") from exc

        data = resp.json()

        if "errors" in data and data["errors"]:
            msgs = "; ".join(e.get("message", "") for e in data["errors"])
            raise PMGraphQLError(f"GraphQL errors: {msgs}", errors=data["errors"])

        return data.get("data", {})

    def close(self) -> None:
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class AsyncPartyClient:
    """Async GraphQL client for PM third-party authentication."""

    def __init__(
        self,
        url: str,
        app_id: str,
        *,
        private_key: str | None = None,
        private_key_path: str | None = None,
        token_lifetime: int = 600,
        timeout: float = 30.0,
    ):
        key_pem = _load_key(private_key, private_key_path)
        self._url = url
        self._token_mgr = TokenManager(app_id, key_pem, token_lifetime)
        self._http = httpx.AsyncClient(timeout=timeout)

    # -- public API ----------------------------------------------------------

    async def query(
        self,
        query: str,
        *,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return await self.execute(query, variables=variables, operation_name=operation_name, headers=headers)

    async def mutate(
        self,
        query: str,
        *,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return await self.execute(query, variables=variables, operation_name=operation_name, headers=headers)

    async def execute(
        self,
        query: str,
        *,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        token = self._token_mgr.generate_token()

        req_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if headers:
            req_headers.update(headers)

        body: dict[str, Any] = {"query": query}
        if variables is not None:
            body["variables"] = variables
        if operation_name is not None:
            body["operationName"] = operation_name

        try:
            resp = await self._http.post(self._url, json=body, headers=req_headers)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise PMConnectionError(f"HTTP {exc.response.status_code}: {exc.response.text}") from exc
        except httpx.HTTPError as exc:
            raise PMConnectionError(f"Connection error: {exc}") from exc

        data = resp.json()

        if "errors" in data and data["errors"]:
            msgs = "; ".join(e.get("message", "") for e in data["errors"])
            raise PMGraphQLError(f"GraphQL errors: {msgs}", errors=data["errors"])

        return data.get("data", {})

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.close()
