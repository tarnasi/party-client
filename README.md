# pm-party-client

A lightweight Python SDK for third-party applications to authenticate and communicate with the **Project Manager** API using **Ed25519** asymmetric key authentication (JWT / EdDSA).

| | |
|---|---|
| **Version** | 0.2.0 |
| **Python** | 3.10+ |
| **Auth** | Ed25519 + JWT (EdDSA) |
| **Transport** | httpx (sync & async) |
| **License** | MIT |

## Installation

```bash
pip install pm-party-client
```

## Quick Start

```python
from pm_party_client import PartyClient

client = PartyClient(
    url="https://pm.example.com/graphql",
    app_id="your-app-id",
    private_key_path="path/to/private_key.pem",
)

# Test connectivity first
health = client.health()
print(health)
# {'status': 200, 'message': 'connected', 'party': {'app_id': '...', 'app_name': '...'}}

# Execute a query
result = client.query("""
    query {
        getParties {
            app_id
            app_name
            status
        }
    }
""")
print(result)

client.close()
```

---

## Configuration

### Constructor parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `url` | `str` | **Yes** | — | PM GraphQL endpoint URL |
| `app_id` | `str` | **Yes** | — | App ID assigned by Project Manager |
| `private_key` | `str` | * | — | Ed25519 private key as PEM string |
| `private_key_path` | `str` | * | — | Path to Ed25519 private key `.pem` file |
| `token_lifetime` | `int` | No | `600` | JWT lifetime in seconds (1–3600) |
| `timeout` | `float` | No | `30.0` | HTTP request timeout in seconds |

> \* Provide **either** `private_key` or `private_key_path`, not both.

### Using a key file

```python
client = PartyClient(
    url="https://pm.example.com/graphql",
    app_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    private_key_path="/secure/location/private_key.pem",
)
```

### Using a key string

```python
client = PartyClient(
    url="https://pm.example.com/graphql",
    app_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    private_key="-----BEGIN PRIVATE KEY-----\nMC4CAQ...\n-----END PRIVATE KEY-----",
)
```

### Custom token lifetime

```python
client = PartyClient(
    url="https://pm.example.com/graphql",
    app_id="a1b2c3d4-...",
    private_key_path="key.pem",
    token_lifetime=300,  # 5 minutes (max 3600)
)
```

---

## API Reference

### `health()` → `dict`

Test connectivity and authentication against the PM backend. Calls `GET /api/v1/party/health` with a signed JWT. Use this to verify your credentials before making real API calls.

```python
result = client.health()
```

**Returns:**

```python
{
    "status": 200,
    "message": "connected",
    "party": {
        "app_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "app_name": "My Application"
    }
}
```

**Raises:** `PMAuthError` (bad credentials), `PMConnectionError` (network issues)

---

### `query(query, *, variables=None, operation_name=None, headers=None)` → `dict`

Execute a GraphQL query.

```python
result = client.query("""
    query GetParty($appId: String!) {
        getParty(appId: $appId) {
            app_name
            status
        }
    }
""", variables={"appId": "some-app-id"})
```

---

### `mutate(query, *, variables=None, operation_name=None, headers=None)` → `dict`

Execute a GraphQL mutation.

```python
result = client.mutate("""
    mutation CreateParty($input: CreatePartyInput!) {
        createParty(input: $input) {
            success
            message
            app_id
        }
    }
""", variables={"input": {"app_name": "New Service"}})
```

---

### `execute(query, *, variables=None, operation_name=None, headers=None)` → `dict`

Low-level method used by `query()` and `mutate()`. Accepts an optional `operation_name` and custom `headers`.

```python
result = client.execute(
    query="query { getParties { app_id } }",
    headers={"X-Request-Id": "abc-123"},
)
```

---

### `close()`

Close the underlying HTTP connection. Also supports context manager usage:

```python
with PartyClient(url=..., app_id=..., private_key=...) as client:
    result = client.query("query { getParties { app_id } }")
# Connection closed automatically
```

---

## Async Support

`AsyncPartyClient` has the same API, all methods are `async`:

```python
from pm_party_client import AsyncPartyClient

async with AsyncPartyClient(
    url="https://pm.example.com/graphql",
    app_id="a1b2c3d4-...",
    private_key_path="key.pem",
) as client:
    # Health check
    health = await client.health()

    # Query
    result = await client.query("query { getParties { app_id app_name } }")

    # Mutation
    result = await client.mutate(
        "mutation RevokeParty($appId: String!) { revokeParty(appId: $appId) { success message } }",
        variables={"appId": "some-app-id"},
    )
```

---

## Error Handling

All exceptions inherit from `PMClientError`:

| Exception | When raised |
|---|---|
| `PMAuthError` | Bad private key, missing credentials, JWT signing failure, 401 from server |
| `PMConnectionError` | Network timeout, DNS failure, HTTP 4xx/5xx (non-401) |
| `PMGraphQLError` | GraphQL response contains `errors` array (access via `.errors`) |
| `PMClientError` | Base class for all the above |

```python
from pm_party_client.exceptions import (
    PMClientError,
    PMAuthError,
    PMGraphQLError,
    PMConnectionError,
)

try:
    result = client.query("query { getParties { app_id } }")
except PMAuthError as e:
    print(f"Authentication failed: {e}")
except PMGraphQLError as e:
    print(f"GraphQL errors: {e.errors}")  # list of error dicts
except PMConnectionError as e:
    print(f"Connection failed: {e}")
except PMClientError as e:
    print(f"Client error: {e}")
```

---

## How It Works

1. You generate an **Ed25519 key pair** and register the **public key** with Project Manager.
2. The client loads your **private key** and creates a short-lived **JWT** (signed with EdDSA) for each request.
3. The JWT is sent as `Authorization: Bearer <token>` — Project Manager verifies it against your stored public key.
4. Tokens are **never stored** — a fresh token is generated per request.

### Generate a key pair

```bash
# Generate private key
openssl genpkey -algorithm Ed25519 -out private_key.pem

# Extract public key (upload this to Project Manager)
openssl pkey -in private_key.pem -pubout -out public_key.pem
```

---

## Dependencies

| Package | Version |
|---|---|
| `PyJWT` | >= 2.8.0 |
| `cryptography` | >= 42.0.0 |
| `httpx` | >= 0.25.0 |

## License

MIT
