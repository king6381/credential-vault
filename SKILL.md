---
name: credential-vault
description: "GPG AES-256 encrypted credential management. Use when the user needs to securely store, retrieve, or manage passwords, API tokens, and secrets. Supports init/add/get/list/remove operations. Requires GPG (gnupg) installed on the system. Triggers: password management, secret storage, credential encryption, token vault, secure credentials, 凭证管理, 密码加密, 安全存储."
---

# Credential Vault

GPG AES-256 encrypted credential manager — one file, all secrets, zero plaintext in final storage.

## Dependencies

- **Python 3.8+**
- **GPG (gnupg)** — pre-installed on most Linux/macOS; Windows needs [Gpg4win](https://gpg4win.org)
- Check: `gpg --version` (the `init` command will verify this automatically)

## Security Model

- **At rest**: credentials stored as AES-256 encrypted `.gpg` file (permissions 600)
- **In transit**: temporary plaintext file exists briefly during encrypt/decrypt operations
  - Permissions set to 600 (owner-only) via `mkstemp` + `fchmod`
  - Securely deleted after use (zero-overwrite + unlink)
  - Duration: milliseconds (only during GPG subprocess execution)
- **Master password**: passed to GPG via `--passphrase-fd` (stdin pipe), never in command-line arguments
- **Environment variable**: `CRED_MASTER_PASS` — set in `~/.bashrc` with `chmod 600`

## Quick Start

```bash
# Initialize (first time) — checks GPG availability
python3 SKILL_DIR/scripts/cred_manager.py init

# Add credentials
python3 SKILL_DIR/scripts/cred_manager.py add myservice

# Use in scripts
export CRED_MASTER_PASS="your_password"
```

Replace `SKILL_DIR` with the actual skill directory path.

## Core Operations

### Initialize

```bash
python3 scripts/cred_manager.py init
```

Creates encrypted `credentials.json.gpg` (permissions 600) in the same directory. Verifies GPG is installed first. User sets master password interactively (minimum 8 chars recommended).

### Add / Update Credentials

```bash
python3 scripts/cred_manager.py add <service_name>
# Interactive: enter key=value pairs, empty line to finish
```

Or programmatically:

```python
from cred_manager import add_credential
add_credential('github', {'user': 'octocat', 'token': 'ghp_xxx'})
```

### Retrieve Credentials

**Python:**
```python
from cred_manager import get_credential, get_service

token = get_credential('github', 'token')    # single field
config = get_service('github')               # full dict
```

**Shell:**
```bash
export CRED_MASTER_PASS="your_password"
source scripts/cred_helper.sh
TOKEN=$(cred_get github token)
```

**CLI:**
```bash
python3 scripts/cred_manager.py get github token
python3 scripts/cred_manager.py get github        # full service
python3 scripts/cred_manager.py list               # all services
```

### Remove

```bash
python3 scripts/cred_manager.py remove <service_name>
```

## Master Password

Priority: environment variable `CRED_MASTER_PASS` → interactive prompt.

Recommend adding to `~/.bashrc`:
```bash
export CRED_MASTER_PASS="your_password"
chmod 600 ~/.bashrc
```

## Integration Pattern

When a user's script has hardcoded passwords, refactor to:

```python
import sys, os
sys.path.insert(0, os.path.expanduser('path/to/credential-vault/scripts'))
from cred_manager import get_credential

password = get_credential('myservice', 'pass')
```

## Limitations

- Temporary plaintext file briefly exists on disk during encrypt/save operations (mitigated by 600 permissions + secure delete)
- Master password in environment variable is visible to same-user processes (`/proc/*/environ`)
- No key rotation mechanism — manual re-encrypt required
- Single-user design — not suitable for enterprise multi-tenant scenarios
