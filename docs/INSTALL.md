# 详细安装指南

## 目录

- [系统要求](#系统要求)
- [方式一：下载 .skill 文件安装](#方式一下载-skill-文件安装)
- [方式二：从源码构建安装](#方式二从源码构建安装)
- [首次登录](#首次登录)
- [验证安装](#验证安装)
- [更新 Skill](#更新-skill)
- [卸载](#卸载)

---

## 系统要求

| 要求 | 最低版本 | 说明 |
|------|---------|------|
| OpenClaw | 任意支持 Skill 的版本 | 桌面版或命令行版均可 |
| Python | 3.9+ | 用于 OAuth 登录脚本 |
| 操作系统 | Windows 10 / macOS 11 / Ubuntu 20.04 | 其他 Linux 发行版理论上也支持 |
| 网络 | 可访问 `login.microsoftonline.com` | 中国大陆需特殊网络环境（见下方说明） |

### Python 安装检查

```bash
python3 --version
# 输出应为 Python 3.9.x 或以上
```

如未安装 Python，请前往 [python.org](https://www.python.org/downloads/) 下载安装。

---

## 方式一：下载 .skill 文件安装

这是最简单的安装方式，适合大多数用户。

### 步骤 1：下载 .skill 文件

前往 [GitHub Releases 页面](https://github.com/your-username/ms365-gog/releases/latest)，下载最新版本的 `ms365-gog.skill` 文件。

### 步骤 2：在 OpenClaw 中安装

**桌面版 OpenClaw：**

1. 打开 OpenClaw 应用
2. 点击右上角 **设置（齿轮图标）**
3. 选择 **Skills** 标签页
4. 点击 **安装本地 Skill**
5. 选择下载的 `ms365-gog.skill` 文件
6. 确认安装

**命令行版 OpenClaw：**

```bash
openclaw skill install ./ms365-gog.skill
```

### 步骤 3：确认安装成功

在 OpenClaw 中输入：

```
你安装了哪些 Skill？
```

输出中应包含 `ms365-gog`。

---

## 方式二：从源码构建安装

适合开发者或需要修改 Skill 内容的用户。

### 步骤 1：克隆仓库

```bash
git clone https://github.com/your-username/ms365-gog.git
cd ms365-gog
```

### 步骤 2：（可选）修改 Skill 内容

根据需要编辑 `SKILL.md` 或 `references/` 下的文件。

### 步骤 3：打包为 .skill 文件

```bash
python scripts/package.py
# 输出：dist/ms365-gog.skill
```

### 步骤 4：安装到 OpenClaw

同方式一的步骤 2，选择 `dist/ms365-gog.skill` 文件。

---

## 首次登录

安装完成后，需要完成一次 Microsoft 365 的 OAuth 授权。

### 在 OpenClaw 中触发登录

直接对 OpenClaw 说：

```
帮我登录 Microsoft 365
```

或：

```
连接我的 Outlook 账号
```

### 登录流程

OpenClaw 会显示如下提示：

```
══════════════════════════════════════════════════
🔑 Microsoft 365 一键登录
══════════════════════════════════════════════════
1. 打开浏览器，访问：https://microsoft.com/devicelogin
2. 输入一次性代码：ABCD-1234
3. 使用你的微软账号登录（个人/企业均可）
══════════════════════════════════════════════════
等待登录完成...
```

按照提示操作：

1. **打开浏览器**，访问 `https://microsoft.com/devicelogin`
2. **输入显示的一次性代码**（每次登录都不同，约 15 分钟有效）
3. **选择或输入你的微软账号**
4. **授权权限**：页面会列出本 Skill 需要的权限，确认后点击"接受"
5. 回到 OpenClaw，等待显示登录成功

```
✅ 登录成功！欢迎，张三 (zhangsan@company.com)
```

### 授权的权限说明

登录时会申请以下权限，均为最小必要范围：

| 权限 | 用途 |
|------|------|
| `User.Read` | 读取你的账号基本信息 |
| `Mail.ReadWrite` / `Mail.Send` | 读取和发送邮件 |
| `Calendars.ReadWrite` | 读取和创建日历事件 |
| `Files.ReadWrite.All` | 读写 OneDrive 和 SharePoint 文件 |
| `Chat.ReadWrite` / `ChannelMessage.Send` | 发送 Teams 消息 |
| `Tasks.ReadWrite` | 管理 To Do 任务 |
| `offline_access` | 后台自动刷新 Token，无需频繁重新登录 |

### Token 有效期

| 类型 | 有效期 | 说明 |
|------|--------|------|
| Access Token | 60 分钟 | 自动刷新，无感知 |
| Refresh Token | 90 天 | 每次使用后自动续期 |

**90 天内只需登录一次。** 如果超过 90 天未使用，或主动退出登录，需要重新完成上述流程。

---

## 验证安装

登录成功后，可以尝试以下命令验证各模块是否正常：

```
# 验证邮件
帮我看看最新的 5 封邮件

# 验证日历
今天有什么日程？

# 验证文件
列出我 OneDrive 根目录下的文件

# 验证 Teams（需企业账号）
列出我的 Teams 聊天会话
```

---

## 更新 Skill

### 自动检查更新

在 OpenClaw 中输入：

```
检查 ms365-gog 是否有新版本
```

### 手动更新

1. 前往 [Releases 页面](https://github.com/your-username/ms365-gog/releases/latest) 下载最新 `.skill` 文件
2. 在 OpenClaw → 设置 → Skills 中，找到 `ms365-gog`，选择 **更新**，选择新下载的文件

**更新不会清除已登录的账号信息**，无需重新登录。

---

## 卸载

### 方法一：通过 OpenClaw 界面卸载

OpenClaw → 设置 → Skills → 找到 `ms365-gog` → 卸载

### 方法二：清除所有数据（含登录信息）

```bash
# 卸载 Skill
openclaw skill uninstall ms365-gog

# 清除 Token 缓存（可选，如需完全清除登录信息）
rm ~/.openclaw/ms365_token_cache.json
```

---

## 中国大陆用户注意

全球版 Microsoft 365 的认证服务器 `login.microsoftonline.com` 在中国大陆可能无法直接访问。

**如果你使用的是世纪互联运营的中国区 Microsoft 365**，请参见 [中国区配置指南](ENTERPRISE.md#中国区世纪互联)。

**如果你使用全球版 Microsoft 365 但网络受限**，登录时需要确保浏览器和 Python 环境可以访问微软认证服务器。
