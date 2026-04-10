# 企业版配置指南

## 目录

- [为什么需要自注册 Azure App](#为什么需要自注册-azure-app)
- [注册 Azure App（全球版）](#注册-azure-app全球版)
- [替换默认 Client ID](#替换默认-client-id)
- [中国区世纪互联](#中国区世纪互联)
- [多账号切换](#多账号切换)
- [共享邮箱访问](#共享邮箱访问)
- [Azure AD 条件访问（MFA）](#azure-ad-条件访问mfa)

---

## 为什么需要自注册 Azure App

默认情况下，本 Skill 使用 Microsoft Graph Explorer 的公共 Client ID。这对个人用户完全够用，但企业用户建议自行注册 App，原因如下：

| 对比项 | 公共 Client ID（默认） | 企业自注册 App |
|--------|----------------------|--------------|
| 限流配额 | 与所有使用该 ID 的人共享 | 独占配额 |
| 被微软撤销风险 | 存在 | 完全受你控制 |
| 管理员同意 | 需每用户单独授权 | IT 可一键全员授权 |
| 条件访问兼容性 | 可能被 CA 策略拦截 | 可精确配置豁免策略 |
| 审计日志 | 无 | Azure AD 登录日志 |

---

## 注册 Azure App（全球版）

**需要**：Azure AD 租户的全局管理员权限，或应用管理员权限。

### 步骤 1：创建应用注册

1. 登录 [Azure Portal](https://portal.azure.com)
2. 搜索并进入 **Azure Active Directory → 应用注册**
3. 点击 **新建注册**
4. 填写：
   - **名称**：`ms365-gog`（或你喜欢的名字）
   - **支持的账户类型**：选"**任何组织目录中的账户**"（如需支持个人账号则选第三项）
   - **重定向 URI**：类型选 **公共客户端/本机**，值填 `http://localhost`
5. 点击 **注册**

### 步骤 2：记录应用信息

注册完成后，在应用概述页面记录：

- **应用程序（客户端）ID**：形如 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **目录（租户）ID**：同样格式的 GUID

### 步骤 3：添加 API 权限

1. 左侧菜单 → **API 权限** → **添加权限**
2. 选择 **Microsoft Graph → 委托的权限**
3. 搜索并添加以下权限：

```
User.Read
Mail.ReadWrite
Mail.Send
Calendars.ReadWrite
Files.ReadWrite.All
Chat.ReadWrite
ChannelMessage.Send
Tasks.ReadWrite
offline_access
```

4. 点击 **代表 [你的组织] 授予管理员同意**（重要：这样员工登录时不会弹出授权页面）

### 步骤 4：配置为公共客户端

1. 左侧菜单 → **身份验证**
2. 滚动到底部，找到 **高级设置**
3. 将 **允许公共客户端流** 切换为 **是**
4. 点击保存

---

## 替换默认 Client ID

编辑 `scripts/auth.py`，修改文件顶部的常量：

```python
# 替换这两行
CLIENT_ID = "你的应用程序客户端ID"
TENANT_ID = "你的目录租户ID"   # 或 "common"（允许任意租户）
```

修改后重新打包并安装 Skill：

```bash
python scripts/package.py
# 然后在 OpenClaw 中更新安装 dist/ms365-gog.skill
```

---

## 中国区世纪互联

中国区 M365 由世纪互联运营，认证端点和 API 端点与全球版完全不同。

### 前置要求

- 世纪互联 M365 租户的管理员账号
- 在 [Azure 中国区门户](https://portal.azure.cn) 注册应用（步骤同上，但使用 `.cn` 域名的门户）

### 注册中国区 App

1. 登录 [Azure 中国区 Portal](https://portal.azure.cn)
2. 同全球版步骤注册应用，但 API 权限搜索时需选择**世纪互联版的 Microsoft Graph**
3. 记录 Client ID 和 Tenant ID

### 配置中国区端点

编辑 `scripts/auth.py`，在文件顶部添加：

```python
import os

# 检测是否使用中国区
USE_CHINA_CLOUD = os.environ.get("MS365_CHINA", "false").lower() == "true"

if USE_CHINA_CLOUD:
    CLIENT_ID  = os.environ["MS365_CHINA_CLIENT_ID"]
    TENANT_ID  = os.environ.get("MS365_CHINA_TENANT_ID", "common")
    AUTHORITY  = f"https://login.chinacloudapi.cn/{TENANT_ID}"
    MS_GRAPH   = "https://microsoftgraph.chinacloudapi.cn/v1.0"
    SCOPES = [
        "https://microsoftgraph.chinacloudapi.cn/User.Read",
        "https://microsoftgraph.chinacloudapi.cn/Mail.ReadWrite",
        "https://microsoftgraph.chinacloudapi.cn/Mail.Send",
        "https://microsoftgraph.chinacloudapi.cn/Calendars.ReadWrite",
        "https://microsoftgraph.chinacloudapi.cn/Files.ReadWrite.All",
        "offline_access",
    ]
else:
    CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"
    TENANT_ID = "common"
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    MS_GRAPH  = "https://graph.microsoft.com/v1.0"
    # ... 原有 SCOPES 不变
```

### 使用中国区模式

```bash
export MS365_CHINA=true
export MS365_CHINA_CLIENT_ID="你的中国区App Client ID"
export MS365_CHINA_TENANT_ID="你的租户ID"

python scripts/auth.py --action login
```

---

## 多账号切换

适合同时需要管理主账号和共享邮箱，或兼顾个人与企业账号的用户。

在 `scripts/auth.py` 中，`get_access_token()` 函数支持传入账号别名：

```python
# 登录第二个账号（别名为 "work"）
python scripts/auth.py --action login --alias work

# 使用指定账号
from scripts.auth import get_access_token
token = get_access_token(alias="work")
```

不同别名的 Token 缓存文件相互隔离，存储在：
```
~/.openclaw/ms365_work.json
~/.openclaw/ms365_personal.json
```

---

## 共享邮箱访问

访问 `info@company.com` 这类共享邮箱：

```python
SHARED_MAILBOX = "info@company.com"

# 读取共享邮箱（需 Mail.ReadWrite.Shared 权限或管理员委托访问权）
resp = requests.get(
    f"https://graph.microsoft.com/v1.0/users/{SHARED_MAILBOX}/messages",
    headers=headers,
    params={"$top": 10, "$orderby": "receivedDateTime desc"},
    timeout=30
)
```

**权限要求**：需要 IT 管理员在 Exchange 中为你的账号授予对该邮箱的"完全访问"权限。

---

## Azure AD 条件访问（MFA）

如果你的企业启用了 MFA 策略，登录时会在浏览器中要求额外验证。`scripts/auth.py` 已内置处理逻辑：

```python
# auth.py 中的 MFA 处理（已内置，无需修改）
if result.get("error") == "interaction_required":
    claims = result.get("claims")
    if claims:
        flow = app.initiate_device_flow(scopes=SCOPES, claims_challenge=claims)
        print(f"⚠️  需要额外验证（MFA）")
        print(f"请访问: {flow['verification_uri']}  输入: {flow['user_code']}")
        result = app.acquire_token_by_device_flow(flow)
```

完成 MFA 验证后，Token 中会包含 MFA 声明，后续操作无需再次验证（直到 Token 过期）。

---

## 更多问题

- [常见问题排查](TROUBLESHOOTING.md)
- [提交 Issue](https://github.com/your-username/ms365-gog/issues)
