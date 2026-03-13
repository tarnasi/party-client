# Publishing `pm-party-client` to PyPI & GitHub

A step-by-step guide to publishing the package to PyPI and setting up the GitHub repository.

---

## 1. Prerequisites

| Tool | Install |
|------|---------|
| Python 3.10+ | Already installed |
| `build` | `pip install build` |
| `twine` | `pip install twine` |
| PyPI account | Register at https://pypi.org/account/register/ |
| TestPyPI account (optional) | Register at https://test.pypi.org/account/register/ |
| GitHub account | https://github.com |

---

## 2. PyPI API Token Setup

### 2a. Create a PyPI API token

1. Log in to https://pypi.org
2. Go to **Account Settings** → **API tokens**
3. Click **Add API token**
4. Set scope to **Entire account** (for first upload) or a specific project (after first upload)
5. Copy the token — it starts with `pypi-`

### 2b. Configure `~/.pypirc`

Create or edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

> **Security:** Set file permissions: `chmod 600 ~/.pypirc`

---

## 3. Build the Package

```bash
cd /path/to/pm-party-client

# Install build tools
pip install build twine

# Build source distribution + wheel
python -m build
```

This creates:

```
dist/
├── pm_party_client-0.1.0.tar.gz    # Source distribution
└── pm_party_client-0.1.0-py3-none-any.whl  # Wheel
```

---

## 4. Test Upload (Optional but Recommended)

Upload to TestPyPI first to verify everything looks correct:

```bash
twine upload --repository testpypi dist/*
```

Test install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pm-party-client
```

> The `--extra-index-url` is needed so dependencies (PyJWT, cryptography, httpx) resolve from real PyPI.

---

## 5. Upload to PyPI (Production)

```bash
twine upload dist/*
```

After upload, the package is live at:

```
https://pypi.org/project/pm-party-client/
```

Anyone can now install it:

```bash
pip install pm-party-client
```

---

## 6. Version Bumps (Future Releases)

1. Update `version` in **two** places:
   - `pyproject.toml` → `version = "0.2.0"`
   - `src/pm_party_client/__init__.py` → `__version__ = "0.2.0"`

2. Clean old build artifacts:
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

3. Build and upload:
   ```bash
   python -m build
   twine upload dist/*
   ```

### Versioning strategy

| Version | When |
|---------|------|
| `0.1.x` | Bug fixes, no API changes |
| `0.2.0` | New features, backward compatible |
| `1.0.0` | Stable, production-ready, public API locked |
| `1.1.0` | New features after 1.0 |
| `2.0.0` | Breaking changes |

---

## 7. GitHub Repository Setup

### 7a. Create the repo

1. Go to https://github.com/new
2. **Repository name:** `pm-party-client`
3. **Description:** `Python SDK for Project Manager third-party authentication — Ed25519 asymmetric keys, JWT signing, and GraphQL client with sync/async support.`
4. **Visibility:** Public (for PyPI packages) or Private
5. Click **Create repository**

### 7b. Push the code

```bash
cd /path/to/pm-party-client

git init
git add .
git commit -m "feat: initial release v0.1.0"
git branch -M main
git remote add origin git@github.com:YOUR_ORG/pm-party-client.git
git push -u origin main
```

### 7c. Add a `.gitignore`

Create `.gitignore` in the repo root:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
.eggs/

# Virtual environment
.venv/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Test / Coverage
.pytest_cache/
htmlcov/
.coverage
```

### 7d. GitHub Repository Settings

**About section** (sidebar on repo page → gear icon):

- **Description:** `Python SDK for Project Manager third-party authentication — Ed25519 + JWT + GraphQL`
- **Website:** `https://pypi.org/project/pm-party-client/`
- **Topics:** `python`, `sdk`, `graphql`, `jwt`, `ed25519`, `authentication`, `api-client`

### 7e. Create a GitHub Release

1. Go to **Releases** → **Create a new release**
2. **Tag:** `v0.1.0`
3. **Release title:** `v0.1.0 — Initial Release`
4. **Description:**

```markdown
## pm-party-client v0.1.0

Initial release of the Project Manager third-party authentication SDK.

### Features
- Ed25519 asymmetric key JWT authentication
- Sync (`PartyClient`) and async (`AsyncPartyClient`) GraphQL clients
- Automatic token generation with configurable lifetime (max 1 hour)
- Private key loading from file path or string
- Typed exception hierarchy for error handling
- Context manager support (`with` / `async with`)

### Install
```bash
pip install pm-party-client
```

### Quick Start
```python
from pm_party_client import PartyClient

client = PartyClient(
    url="https://pm.example.com/graphql",
    app_id="your-app-id",
    private_key_path="private_key.pem",
)
result = client.query("query { getParties { app_id app_name status } }")
```
```

5. Attach the built files from `dist/` (optional)
6. Click **Publish release**

---

## 8. Optional: Automate Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for trusted publishing
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install build tools
        run: pip install build

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

> **Trusted Publishing** (recommended): Instead of using API tokens, configure trusted publishing on PyPI:
> 1. Go to PyPI → your project → **Publishing**
> 2. Add a **new trusted publisher** with your GitHub repo, workflow name, and environment
> 3. No secrets needed — GitHub OIDC handles authentication

---

## 9. Checklist

- [ ] PyPI account created
- [ ] API token generated and saved to `~/.pypirc`
- [ ] Package builds successfully (`python -m build`)
- [ ] TestPyPI upload verified
- [ ] Production PyPI upload done
- [ ] GitHub repo created with description and topics
- [ ] `.gitignore` added
- [ ] Code pushed to `main`
- [ ] GitHub release `v0.1.0` created
- [ ] (Optional) GitHub Actions CI/CD configured
- [ ] Verify `pip install pm-party-client` works from a clean environment
