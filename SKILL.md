---
name: credential-vault
description: "GPG AES-256 encrypted credential management. Use when the user needs to securely store, retrieve, or manage passwords, API tokens, and secrets. Supports init/add/get/list/remove operations. Triggers: password management, secret storage, credential encryption, token vault, secure credentials, 凭证管理, 密码加密, 安全存储."
---

# Credential Vault

GPG AES-256 encrypted credential manager — one file, all secrets, zero plaintext.

## Quick Start

```bash
# Initialize (first time)
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

Creates encrypted `credentials.json.gpg` in the same directory. User sets master password interactively.

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

## Security Notes

- Encrypted file: `credentials.json.gpg` (AES-256)
- Plaintext never touches disk (temp file deleted immediately after encryption)
- Add to `.gitignore`: `*.gpg`, `*.json`, `__pycache__/`
- Dependencies: Python 3.8+, GPG (pre-installed on Linux/macOS)
