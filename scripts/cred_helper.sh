#!/bin/bash
# 🔐 凭证管理 Shell 辅助工具
#
# 用法:
#   source cred_helper.sh
#   cred_get yizhan pass     → 输出密码
#   cred_get github token    → 输出 token
#
# 前置:
#   export CRED_MASTER_PASS="你的主密码"

CRED_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRED_FILE="$CRED_DIR/credentials.json.gpg"

cred_get() {
    local service="$1"
    local key="$2"

    if [ -z "$service" ] || [ -z "$key" ]; then
        echo "用法: cred_get <服务> <字段>" >&2
        return 1
    fi

    if [ ! -f "$CRED_FILE" ]; then
        echo "ERROR: 加密凭证文件不存在: $CRED_FILE" >&2
        echo "请先运行: python3 cred_manager.py init" >&2
        return 1
    fi

    if [ -z "$CRED_MASTER_PASS" ]; then
        echo "ERROR: 请设置环境变量 CRED_MASTER_PASS" >&2
        return 1
    fi

    gpg --batch --yes --passphrase "$CRED_MASTER_PASS" --decrypt "$CRED_FILE" 2>/dev/null | \
        python3 -c "import sys,json; d=json.load(sys.stdin); print(d['$service']['$key'])" 2>/dev/null
}

cred_list() {
    if [ ! -f "$CRED_FILE" ]; then
        echo "ERROR: 加密凭证文件不存在" >&2
        return 1
    fi

    if [ -z "$CRED_MASTER_PASS" ]; then
        echo "ERROR: 请设置环境变量 CRED_MASTER_PASS" >&2
        return 1
    fi

    gpg --batch --yes --passphrase "$CRED_MASTER_PASS" --decrypt "$CRED_FILE" 2>/dev/null | \
        python3 -c "import sys,json; [print(f'  • {k}') for k in json.load(sys.stdin).keys()]"
}

echo "🔐 凭证工具已加载 (cred_get / cred_list)"
