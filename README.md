# 🛡️ 雷神之盾 · 凭证保险箱 (Credential Vault)

<p align="center">
  <strong>⚡ 雷神之盾系列 — 安全工具第一弹 ⚡</strong><br>
  <em>GPG AES-256 加密 · 一个文件管所有密码 · 告别明文裸奔</em>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.8+-green.svg" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/加密-AES--256-red.svg" alt="Encryption"></a>
  <a href="#"><img src="https://img.shields.io/badge/系列-雷神之盾-gold.svg" alt="Shield Series"></a>
</p>

---

## 🎯 这是什么

你有没有遇到过这些情况？

- 脚本里到处写 `password = "abc123"` 😱
- `.env` 文件忘记加 `.gitignore`，密码推到了 GitHub 🤦
- 十几个服务的密码分散在各种文件里，找都找不到 🤯
- 想改个密码，要改八个地方 😤

**凭证保险箱**帮你一步解决：所有密码、Token、密钥，**加密存在一个文件里**，用的时候一行代码取出来。

## ✨ 特性

- 🔐 **军事级加密** — GPG AES-256，和银行同级别
- 📦 **一个文件** — 所有凭证集中管理，备份只需复制一个 `.gpg` 文件
- 🐍 **Python + Shell 双接口** — 脚本里一行代码调用
- 🖥️ **完整 CLI** — 命令行交互式管理，不用写代码
- 🔑 **环境变量** — 主密码不硬编码，安全到底
- 🤖 **OpenClaw 技能** — AI 代理也能安全管理你的密码
- 📂 **零依赖** — 只需 Python 3.8 + GPG（系统自带）

## 🚀 三步上手

### 第一步：初始化

```bash
cd credential-vault/scripts
python3 cred_manager.py init
```

系统会让你设置主密码（**请牢记！**），然后生成加密文件。

### 第二步：存入密码

```bash
python3 cred_manager.py add github
# 交互输入：
#   > user=king6381
#   > token=ghp_xxxxxxxxx
#   > email=king@example.com
#   > （空行结束）
# ✅ 已保存: github (user, token, email)
```

### 第三步：使用密码

**Python 脚本里：**
```python
from cred_manager import get_credential

# 取一个字段
token = get_credential('github', 'token')

# 取整个服务配置
config = get_service('github')
# → {'user': 'king6381', 'token': 'ghp_xxx', 'email': '...'}
```

**Shell 脚本里：**
```bash
export CRED_MASTER_PASS="你的主密码"
source cred_helper.sh

TOKEN=$(cred_get github token)
echo "我的 Token 是: $TOKEN"
```

**命令行直接查：**
```bash
export CRED_MASTER_PASS="你的主密码"

python3 cred_manager.py list               # 列出所有服务
python3 cred_manager.py get github         # 查看完整配置
python3 cred_manager.py get github token   # 只取 token
python3 cred_manager.py remove old_service # 删除服务
```

## 📖 完整命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `init` | 首次初始化，设置主密码 | `python3 cred_manager.py init` |
| `list` | 列出所有已存储的服务 | `python3 cred_manager.py list` |
| `add` | 交互式添加凭证 | `python3 cred_manager.py add nas` |
| `get` | 查看凭证 | `python3 cred_manager.py get nas pass` |
| `remove` | 删除一个服务 | `python3 cred_manager.py remove old` |

## 🔒 安全建议

### ✅ 推荐做法

1. **主密码用环境变量**，不要写在脚本里
   ```bash
   # 加到 ~/.bashrc 或 ~/.zshrc
   export CRED_MASTER_PASS="你的强密码"
   chmod 600 ~/.bashrc
   ```

2. **`.gitignore` 排除敏感文件**
   ```
   *.gpg
   *.json
   __pycache__/
   ```

3. **定期备份** `.gpg` 文件到安全位置

4. **定期更换**主密码和服务密码

### ❌ 千万别做

- ❌ 把 `.gpg` 文件和主密码放在同一个地方
- ❌ 用弱密码当主密码（如 `123456`）
- ❌ 把主密码提交到 Git
- ❌ 在公共电脑上不清除环境变量

## 🏗️ 项目结构

```
credential-vault/
├── SKILL.md              ← OpenClaw 技能描述
├── scripts/
│   ├── cred_manager.py   ← 🐍 Python 核心模块 + CLI
│   └── cred_helper.sh    ← 🐚 Shell 辅助脚本
├── LICENSE               ← MIT 开源协议
└── .gitignore            ← Git 忽略规则
```

## 💡 实战场景

### 场景 1：管理多台服务器密码

```bash
python3 cred_manager.py add nas
# > url=http://192.168.1.100
# > user=admin
# > pass=super_secret

python3 cred_manager.py add vps
# > host=8.8.8.8
# > user=root
# > key_path=/home/me/.ssh/id_rsa
```

### 场景 2：API Token 集中管理

```python
from cred_manager import get_credential

# 股票数据
tushare_token = get_credential('tushare', 'token')

# GitHub 自动化
gh_token = get_credential('github', 'token')

# AI 接口
api_key = get_credential('openai', 'key')
```

### 场景 3：团队共享（加密传输）

```bash
# 导出加密文件给队友
cp credentials.json.gpg /shared/drive/

# 队友拿到后设置主密码即可使用
export CRED_MASTER_PASS="团队约定的密码"
python3 cred_manager.py list
```

## 🛡️ 关于雷神之盾

**雷神之盾**是一个安全工具系列，专注于为个人开发者和小团队提供简单、实用、可靠的安全解决方案。

| 工具 | 状态 | 说明 |
|------|------|------|
| 🔐 **凭证保险箱** | ✅ 已发布 | 密码/Token 加密管理 |
| 🔑 更多工具 | 🔜 开发中 | 敬请期待... |

> *姊妹品牌：[⚡ 雷神之锤 (Mjölnir)](https://github.com/king6381) — A股智能量化分析系统*

## 🤝 贡献

欢迎提 Issue 和 PR！这是一个开源项目，任何改进建议都欢迎。

## 📄 开源协议

[MIT License](LICENSE) — 自由使用，随便改。

---

<p align="center">
  <strong>🛡️ 雷神之盾 — 安全，从不裸奔开始</strong><br>
  <em>"The shield that guards the realms of code."</em>
</p>
