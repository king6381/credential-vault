---
name: credential-vault
description: "GPG AES-256 encrypted credential management. Requires: GPG (gnupg) installed, CRED_MASTER_PASS env var for non-interactive use. Use when the user needs to securely store, retrieve, or manage passwords, API tokens, and secrets. Supports init/add/get/list/remove operations. Triggers: password management, secret storage, credential encryption, token vault, secure credentials, 凭证管理, 密码加密, 安全存储."
---

# Credential Vault

GPG AES-256 encrypted credential manager — one file, all secrets.

## Dependencies

- **Python 3.8+**
- **GPG (gnupg)** — pre-installed on most Linux/macOS; Windows needs [Gpg4win](https://gpg4win.org)
- Check: `gpg --version` (the `init` command verifies this automatically)

## Required Environment Variables

| Variable | Purpose | Required? |
|----------|---------|-----------|
| `CRED_MASTER_PASS` | Master password for encrypt/decrypt | Required for non-interactive use; if unset, prompts interactively |

## Security Model

### How it works
1. All credentials stored as AES-256 encrypted `.gpg` file (permissions 600)
2. Master password passed to GPG via `--passphrase-fd` (stdin pipe) — **never** in command-line arguments
3. Shell helper also uses `--passphrase-fd 0` (echo pipe) — **not** `--passphrase`

### Temporary plaintext on disk
During save/encrypt operations, plaintext JSON briefly exists as a temporary file:
- Created with `mkstemp` + `fchmod 600` (owner-only read/write)
- Exists for milliseconds (only during GPG subprocess execution)
- Securely deleted: zero-overwrite → fsync → unlink
- **Risk**: on some systems, temp file contents may be recoverable from disk. For higher security, use a tmpfs/ramfs mount or a dedicated secrets manager.

### Master password storage
The `CRED_MASTER_PASS` environment variable is readable by same-user processes via `/proc/*/environ` on Linux.

**Recommended approaches (from most to least secure):**
1. **gpg-agent / pinentry** — enter password interactively each time (most secure)
2. **Runtime injection** — set via a secrets manager or session-scoped `read -s` prompt
3. **Environment variable** — `export CRED_MASTER_PASS="..."` in current shell (convenient but less secure)

**Avoid:** persisting the master password in plaintext files (e.g., `~/.bashrc`). If you must, ensure `chmod 600` and understand the trade-off.

## Quick Start

```bash
# Initialize (first time) — checks GPG availability
python3 SKILL_DIR/scripts/cred_manager.py init

# Add credentials (interactive)
python3 SKILL_DIR/scripts/cred_manager.py add myservice

# Non-interactive use
export CRED_MASTER_PASS="your_password"
```

Replace `SKILL_DIR` with the actual skill directory path.

## Core Operations

### Initialize

```bash
python3 scripts/cred_manager.py init
```

Verifies GPG is installed, creates encrypted `credentials.json.gpg` (permissions 600). Warns if password < 8 chars.

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
python3 scripts/cred_manager.py list
```

### Remove

```bash
python3 scripts/cred_manager.py remove <service_name>
```

## Integration Pattern

When a user's script has hardcoded passwords, refactor to:

```python
import sys, os
sys.path.insert(0, os.path.expanduser('path/to/credential-vault/scripts'))
from cred_manager import get_credential

password = get_credential('myservice', 'pass')
```

## Known Limitations

1. **Temporary plaintext on disk** — briefly exists during encrypt operations (mitigated by 600 permissions + secure delete, but not zero-risk)
2. **Environment variable visibility** — `CRED_MASTER_PASS` readable by same-user processes on Linux
3. **No key rotation** — manual re-encrypt required to change master password
4. **Single-user design** — not for enterprise multi-tenant use
5. **No tamper detection** — `.gpg` file integrity not independently verified

For higher security requirements, consider: OS keyring, `pass`, HashiCorp Vault, or cloud KMS.
