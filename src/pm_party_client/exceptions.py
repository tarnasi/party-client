class PMClientError(Exception):
    """Base exception for all pm-party-client errors."""


class PMAuthError(PMClientError):
    """Raised when authentication fails (bad key, expired token, etc.)."""


class PMConnectionError(PMClientError):
    """Raised when the HTTP connection to the PM backend fails."""


class PMGraphQLError(PMClientError):
    """Raised when the GraphQL response contains errors."""

    def __init__(self, message: str, errors: list[dict]):
        super().__init__(message)
        self.errors = errors
