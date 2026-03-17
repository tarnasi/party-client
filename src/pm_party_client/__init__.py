"""pm-party-client — Python SDK for Project Manager third-party authentication."""

__version__ = "0.2.0"

from pm_party_client.client import AsyncPartyClient, PartyClient
from pm_party_client.exceptions import (
    PMAuthError,
    PMClientError,
    PMConnectionError,
    PMGraphQLError,
)

__all__ = [
    "PartyClient",
    "AsyncPartyClient",
    "PMClientError",
    "PMAuthError",
    "PMConnectionError",
    "PMGraphQLError",
]
