# pm-party-client

A lightweight Python SDK for third-party applications to authenticate and query the Project Manager GraphQL API using Ed25519 asymmetric key authentication.

## Installation

```bash
pip install pm-party-client
```

## Quick Start

```python
from pm_party_client import PartyClient

client = PartyClient(
    url="https://your-pm-instance.com/graphql",
    app_id="your-app-id",
    private_key_path="path/to/private_key.pem",  # or use private_key="-----BEGIN PRIVATE KEY-----\n..."
)

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
```

## Configuration

### Using a key file

```python
client = PartyClient(
    url="https://pm.example.com/graphql",
    app_id="a1b2c3d4-...",
    private_key_path="/secure/location/private_key.pem",
)
```

### Using a key string

```python
client = PartyClient(
    url="https://pm.example.com/graphql",
    app_id="a1b2c3d4-...",
    private_key="-----BEGIN PRIVATE KEY-----\nMC4CAQ...\n-----END PRIVATE KEY-----",
)
```

### Token lifetime

Tokens are short-lived by default (10 minutes). You can adjust:

```python
client = PartyClient(
    url="https://pm.example.com/graphql",
    app_id="a1b2c3d4-...",
    private_key_path="key.pem",
    token_lifetime=300,  # 5 minutes (max 3600)
)
```

## Usage

### Query

```python
result = client.query("""
    query GetParty($appId: String!) {
        getParty(appId: $appId) {
            app_name
            status
            public_key
        }
    }
""", variables={"appId": "some-app-id"})
```

### Mutation

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

### Raw execute

```python
result = client.execute(
    query="query { me { id email } }",
    variables={},
    operation_name="GetMe",
)
```

### Custom headers

```python
result = client.query(
    "query { getParties { app_id } }",
    headers={"X-Request-Id": "abc-123"},
)
```

## Async Support

```python
from pm_party_client import AsyncPartyClient

client = AsyncPartyClient(
    url="https://pm.example.com/graphql",
    app_id="a1b2c3d4-...",
    private_key_path="key.pem",
)

result = await client.query("query { getParties { app_id } }")
await client.close()

# Or use as async context manager
async with AsyncPartyClient(url=..., app_id=..., private_key_path=...) as client:
    result = await client.query("query { getParties { app_id } }")
```

## Error Handling

```python
from pm_party_client.exceptions import (
    PMClientError,
    PMAuthError,
    PMGraphQLError,
    PMConnectionError,
)

try:
    result = client.query("query { me { id } }")
except PMAuthError as e:
    print(f"Authentication failed: {e}")
except PMGraphQLError as e:
    print(f"GraphQL errors: {e.errors}")
except PMConnectionError as e:
    print(f"Connection failed: {e}")
except PMClientError as e:
    print(f"Client error: {e}")
```

## Health Check

Test your connection and credentials before making real API calls:

```python
result = client.health()
# {'status': 200, 'message': 'connected', 'party': {'app_id': '...', 'app_name': '...'}}
```

Async:

```python
result = await async_client.health()
```

## Python Version Support

- Python 3.10+

## Dependencies

- `PyJWT >= 2.8.0`
- `cryptography >= 42.0.0`
- `httpx >= 0.25.0`

## License

MIT
