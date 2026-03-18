# 🛡️ 雷神之盾 · 凭证保险箱 — 使用指南

> 本文档面向中文用户，手把手教你从零开始使用凭证保险箱。

---

## 📋 目录

1. [环境准备](#1-环境准备)
2. [安装](#2-安装)
3. [初始化](#3-初始化)
4. [日常使用](#4-日常使用)
5. [在脚本中调用](#5-在脚本中调用)
6. [常见问题](#6-常见问题)

---

## 1. 环境准备

### 检查 Python

```bash
python3 --version
# 需要 3.8 或更高版本
```

### 检查 GPG

```bash
gpg --version
# Linux / macOS 通常自带
# Windows 用户请安装 Gpg4win: https://gpg4win.org
```

如果都有，直接跳到下一步 ✅

## 2. 安装

### 方式一：克隆仓库

```bash
git clone https://github.com/king6381/credential-vault.git
cd credential-vault/scripts
```

### 方式二：直接下载

下载 `scripts/cred_manager.py` 和 `scripts/cred_helper.sh` 两个文件放到同一个目录即可。

## 3. 初始化

```bash
python3 cred_manager.py init
```

输出：
```
🔐 初始化凭证管理系统
========================================
设置主密码: （输入密码，屏幕不显示）
确认主密码: （再输入一次）
✅ 凭证文件已创建: ./credentials.json.gpg

📌 下一步:
  1. 设置环境变量: export CRED_MASTER_PASS="你的密码"
  2. 添加凭证: python3 cred_manager.py add 服务名
  3. 查看凭证: python3 cred_manager.py list
```

### ⚡ 设置环境变量（重要！）

把主密码设为环境变量，这样每次使用不用重复输入：

```bash
# Linux / macOS — 加到 ~/.bashrc 或 ~/.zshrc
echo 'export CRED_MASTER_PASS="你的主密码"' >> ~/.bashrc
source ~/.bashrc

# 安全起见，设置文件权限
chmod 600 ~/.bashrc
```

## 4. 日常使用

### 添加凭证

```bash
python3 cred_manager.py add 服务名
```

**示例：添加 NAS 登录信息**
```
$ python3 cred_manager.py add nas
添加凭证: nas
输入字段 (格式: key=value)，空行结束:
  > url=http://192.168.110.44
  > user=admin
  > pass=my_nas_password
  >
✅ 已保存: nas (url, user, pass)
```

**示例：添加 GitHub Token**
```
$ python3 cred_manager.py add github
添加凭证: github
输入字段 (格式: key=value)，空行结束:
  > user=king6381
  > email=king6381@hotmail.com
  > token=ghp_xxxxxxxxxxxx
  >
✅ 已保存: github (user, email, token)
```

### 查看凭证

```bash
# 列出所有服务
python3 cred_manager.py list
# 📋 已存储 2 个服务:
#   • nas (url, user, pass)
#   • github (user, email, token)

# 查看某个服务的完整配置
python3 cred_manager.py get nas
# {
#   "url": "http://192.168.110.44",
#   "user": "admin",
#   "pass": "my_nas_password"
# }

# 只取一个字段
python3 cred_manager.py get nas pass
# my_nas_password
```

### 删除凭证

```bash
python3 cred_manager.py remove 旧服务
# 🗑️ 已删除: 旧服务
```

### 修改凭证

直接用 `add` 覆盖即可（同名服务会被替换）：

```bash
python3 cred_manager.py add nas
# 重新输入新的 key=value
```

## 5. 在脚本中调用

### Python 脚本

```python
# 方式一：直接导入（cred_manager.py 在同目录或 PYTHONPATH 中）
from cred_manager import get_credential, get_service

# 取单个字段
password = get_credential('nas', 'pass')
token = get_credential('github', 'token')

# 取完整配置
nas_config = get_service('nas')
print(nas_config['url'])  # http://192.168.110.44

# 方式二：cred_manager.py 在其他目录
import sys
sys.path.insert(0, '/path/to/credential-vault/scripts')
from cred_manager import get_credential
```

### Shell 脚本

```bash
#!/bin/bash
# 确保已设置 CRED_MASTER_PASS 环境变量

source /path/to/credential-vault/scripts/cred_helper.sh

# 获取凭证
NAS_PASS=$(cred_get nas pass)
GH_TOKEN=$(cred_get github token)

# 使用
curl -u "admin:$NAS_PASS" http://192.168.110.44/api/...
```

### 实战：改造一个有硬编码密码的脚本

**改造前（危险 ❌）：**
```python
import requests

url = "http://192.168.110.44"
user = "admin"
password = "abc123"  # 😱 明文密码！

r = requests.get(url, auth=(user, password))
```

**改造后（安全 ✅）：**
```python
import requests
from cred_manager import get_credential

url = get_credential('nas', 'url')
user = get_credential('nas', 'user')
password = get_credential('nas', 'pass')

r = requests.get(url, auth=(user, password))
```

## 6. 常见问题

### Q: 忘记主密码怎么办？

**没有办法恢复。** GPG 加密是单向的，没有密码就无法解密。所以：
- 请把主密码记在安全的地方（比如密码管理器）
- 定期备份 `.gpg` 文件

### Q: 换了电脑怎么办？

只需要复制 `credentials.json.gpg` 文件到新电脑，然后设置相同的主密码环境变量即可。

### Q: 支持 Windows 吗？

支持，但需要先安装 [Gpg4win](https://gpg4win.org)。Python 和 Shell 脚本在 Windows 上都能运行（Shell 脚本需要 Git Bash 或 WSL）。

### Q: 多人共享凭证安全吗？

可以共享 `.gpg` 文件 + 口头约定主密码。但更推荐每人维护自己的凭证文件，只共享不敏感的配置。

### Q: 和 1Password / Bitwarden 有什么区别？

凭证保险箱专注于**开发者场景**：
- 无需联网，纯本地加密
- 脚本一行代码调用，适合自动化
- 零依赖，GPG + Python 够用
- 免费开源

如果你需要浏览器插件、手机 App、团队管理等功能，推荐用专业的密码管理器。

---

<p align="center">
  🛡️ <strong>雷神之盾 · 凭证保险箱</strong><br>
  <em>密码安全，从不裸奔开始。</em>
</p>
