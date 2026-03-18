#!/usr/bin/env python3
"""
🔐 凭证加密管理模块 v1.1.0

GPG AES-256 对称加密，所有密码/Token 集中管理。

依赖: Python 3.8+, GPG (gnupg)

用法:
    from cred_manager import get_credential, add_credential

    # 获取凭证
    password = get_credential('yizhan', 'pass')
    token = get_credential('github', 'token')

    # 获取完整服务配置
    config = get_service('yizhan')

    # 添加/更新凭证
    add_credential('my_service', {'user': 'xxx', 'pass': 'yyy'})

首次使用:
    python3 cred_manager.py init
"""

import subprocess
import json
import os
import sys
import getpass
import tempfile
import stat

# ═══════════════════════════════════════════════════════════
# 配置 — 修改这两项适配你的环境
# ═══════════════════════════════════════════════════════════

# 加密文件路径（放在你觉得安全的地方）
CRED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credentials.json.gpg')

# 主密码：从环境变量读取，不硬编码
# 设置方式: export CRED_MASTER_PASS="你的主密码"
MASTER_PASS = os.environ.get('CRED_MASTER_PASS', '')

# ═══════════════════════════════════════════════════════════

_cache = None


def _get_master_pass():
    """获取主密码，优先环境变量，否则交互输入"""
    if MASTER_PASS:
        return MASTER_PASS
    return getpass.getpass('🔑 输入主密码: ')


def _gpg_decrypt(password: str, input_file: str) -> str:
    """
    GPG 解密，通过 --passphrase-fd 从 stdin 传入密码。
    避免密码出现在命令行参数中（ps aux 可见）。
    """
    proc = subprocess.Popen(
        ['gpg', '--batch', '--yes', '--passphrase-fd', '0',
         '--decrypt', input_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate(input=password.encode('utf-8'))
    if proc.returncode != 0:
        raise RuntimeError(f"解密失败（密码错误？）: {stderr.decode()}")
    return stdout.decode('utf-8')


def _gpg_encrypt(password: str, input_file: str, output_file: str):
    """
    GPG 加密，通过 --passphrase-fd 从 stdin 传入密码。
    避免密码出现在命令行参数中。
    """
    proc = subprocess.Popen(
        ['gpg', '--batch', '--yes', '--passphrase-fd', '0',
         '--symmetric', '--cipher-algo', 'AES256',
         '-o', output_file, input_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    _, stderr = proc.communicate(input=password.encode('utf-8'))
    if proc.returncode != 0:
        raise RuntimeError(f"加密失败: {stderr.decode()}")


def _secure_write_temp(data: str) -> str:
    """
    安全地写入临时文件：
    1. 创建时设置 600 权限（仅 owner 可读写）
    2. 使用 mkstemp 而非 NamedTemporaryFile（更可控）
    返回临时文件路径，调用方负责删除。
    """
    fd, tmp_path = tempfile.mkstemp(suffix='.json', prefix='cred_')
    try:
        os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)  # 600
        os.write(fd, data.encode('utf-8'))
    finally:
        os.close(fd)
    return tmp_path


def _secure_delete(path: str):
    """安全删除临时文件：先覆写再删除"""
    try:
        size = os.path.getsize(path)
        with open(path, 'wb') as f:
            f.write(b'\x00' * size)  # 零覆写
            f.flush()
            os.fsync(f.fileno())
        os.unlink(path)
    except OSError:
        # 最坏情况：至少尝试删除
        try:
            os.unlink(path)
        except OSError:
            pass


def _load_credentials():
    """解密并加载凭证（带内存缓存）"""
    global _cache
    if _cache is not None:
        return _cache

    if not os.path.exists(CRED_FILE):
        raise FileNotFoundError(f"加密凭证文件不存在: {CRED_FILE}\n请先运行: python3 cred_manager.py init")

    password = _get_master_pass()
    plaintext = _gpg_decrypt(password, CRED_FILE)
    _cache = json.loads(plaintext)
    return _cache


def _save_credentials(creds: dict):
    """加密并保存凭证（临时文件权限 600 + 安全删除）"""
    password = _get_master_pass()
    json_str = json.dumps(creds, indent=2, ensure_ascii=False)

    tmp_path = _secure_write_temp(json_str)
    try:
        _gpg_encrypt(password, tmp_path, CRED_FILE)
        global _cache
        _cache = creds
    finally:
        _secure_delete(tmp_path)


def get_credential(service: str, key: str) -> str:
    """获取指定服务的指定字段"""
    creds = _load_credentials()
    if service not in creds:
        raise KeyError(f"未找到服务: {service}，可用: {list(creds.keys())}")
    if key not in creds[service]:
        raise KeyError(f"服务 {service} 中未找到字段: {key}，可用: {list(creds[service].keys())}")
    return creds[service][key]


def get_service(service: str) -> dict:
    """获取指定服务的完整配置"""
    creds = _load_credentials()
    if service not in creds:
        raise KeyError(f"未找到服务: {service}")
    return creds[service]


def list_services() -> list:
    """列出所有服务名"""
    creds = _load_credentials()
    return list(creds.keys())


def add_credential(service: str, data: dict):
    """添加或更新凭证"""
    try:
        creds = _load_credentials()
    except FileNotFoundError:
        creds = {}
    creds[service] = data
    _save_credentials(creds)
    print(f"✅ 已保存: {service} ({', '.join(data.keys())})")


def remove_credential(service: str):
    """删除一个服务的凭证"""
    creds = _load_credentials()
    if service not in creds:
        raise KeyError(f"未找到服务: {service}")
    del creds[service]
    _save_credentials(creds)
    print(f"🗑️ 已删除: {service}")


def init_credentials():
    """首次初始化：设置主密码，创建空的加密文件"""
    if os.path.exists(CRED_FILE):
        print(f"⚠️  加密文件已存在: {CRED_FILE}")
        confirm = input("覆盖？(y/N): ")
        if confirm.lower() != 'y':
            return

    print("🔐 初始化凭证管理系统")
    print("=" * 40)

    password = getpass.getpass("设置主密码: ")
    password2 = getpass.getpass("确认主密码: ")
    if password != password2:
        print("❌ 两次密码不一致")
        return

    if len(password) < 8:
        print("⚠️  警告: 主密码少于 8 位，建议使用更强的密码")

    json_str = json.dumps({})
    tmp_path = _secure_write_temp(json_str)
    try:
        _gpg_encrypt(password, tmp_path, CRED_FILE)
    finally:
        _secure_delete(tmp_path)

    # 设置 .gpg 文件权限为 600
    os.chmod(CRED_FILE, stat.S_IRUSR | stat.S_IWUSR)

    print(f"✅ 凭证文件已创建: {CRED_FILE}")
    print()
    print("📌 下一步:")
    print(f'  1. 设置环境变量 (二选一):')
    print(f'     方式A: export CRED_MASTER_PASS="你的密码" (当前终端)')
    print(f'     方式B: 写入 ~/.bashrc 并 chmod 600 ~/.bashrc')
    print(f'  2. 添加凭证: python3 cred_manager.py add 服务名')
    print(f'  3. 查看凭证: python3 cred_manager.py list')
    print()
    print("⚠️  安全提示:")
    print("  • 主密码请牢记，丢失无法恢复")
    print("  • .gpg 文件请定期备份到安全位置")
    print("  • 不要将 .gpg 文件和主密码存放在同一处")


# ═══════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════

def _cli():
    usage = """
🔐 凭证加密管理工具 v1.1.0

命令:
  python3 cred_manager.py init                 首次初始化
  python3 cred_manager.py list                 列出所有服务
  python3 cred_manager.py get <服务> [字段]     查看凭证
  python3 cred_manager.py add <服务>            交互式添加
  python3 cred_manager.py remove <服务>         删除服务

环境变量:
  CRED_MASTER_PASS    主密码（不设置则交互输入）

依赖:
  Python 3.8+, GPG (gnupg) — Linux/macOS 通常预装
  检查: gpg --version
"""

    if len(sys.argv) < 2:
        print(usage)
        return

    cmd = sys.argv[1]

    if cmd == 'init':
        # 检查 GPG 是否可用
        try:
            subprocess.run(['gpg', '--version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("❌ 未找到 GPG。请先安装:")
            print("   Linux (Debian/Ubuntu): sudo apt install gnupg")
            print("   Linux (RHEL/CentOS):   sudo yum install gnupg2")
            print("   macOS:                 brew install gnupg")
            print("   Windows:               https://gpg4win.org")
            return
        init_credentials()

    elif cmd == 'list':
        services = list_services()
        print(f"📋 已存储 {len(services)} 个服务:")
        for s in services:
            svc = get_service(s)
            print(f"  • {s} ({', '.join(svc.keys())})")

    elif cmd == 'get':
        if len(sys.argv) == 3:
            print(json.dumps(get_service(sys.argv[2]), indent=2, ensure_ascii=False))
        elif len(sys.argv) == 4:
            print(get_credential(sys.argv[2], sys.argv[3]))
        else:
            print("用法: python3 cred_manager.py get <服务> [字段]")

    elif cmd == 'add':
        if len(sys.argv) < 3:
            print("用法: python3 cred_manager.py add <服务名>")
            return
        service = sys.argv[2]
        print(f"添加凭证: {service}")
        print("输入字段 (格式: key=value)，空行结束:")
        data = {}
        while True:
            line = input("  > ").strip()
            if not line:
                break
            if '=' not in line:
                print("  格式错误，用 key=value")
                continue
            k, v = line.split('=', 1)
            data[k.strip()] = v.strip()
        if data:
            add_credential(service, data)

    elif cmd == 'remove':
        if len(sys.argv) < 3:
            print("用法: python3 cred_manager.py remove <服务名>")
            return
        remove_credential(sys.argv[2])

    else:
        print(usage)


if __name__ == '__main__':
    _cli()
