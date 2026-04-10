# 企业版功能模块（enterprise.md）

> 适用于 **ms365-gog 企业版（¥299/月）**，覆盖多账号、SSO、审计日志、Conditional Access 适配。

---

## 1. 多账号切换

企业用户常需同时管理多个 M365 账号（如个人 + 公司、主账号 + 共享邮箱）。

### Token 缓存隔离

```python
# scripts/auth_enterprise.py 扩展
from pathlib import Path
import hashlib

def get_cache_path(account_alias: str) -> Path:
    """每个账号独立缓存文件，alias 可以是邮箱或自定义名称"""
    safe = hashlib.md5(account_alias.encode()).hexdigest()[:8]
    return Path.home() / ".openclaw" / f"ms365_{safe}.json"

# 使用示例
# get_access_token(account="work@company.com")
# get_access_token(account="personal@outlook.com")
```

### 列出已登录账号
```python
import glob, json, msal
from pathlib import Path

cache_dir = Path.home() / ".openclaw"
accounts = []
for cache_file in cache_dir.glob("ms365_*.json"):
    cache = msal.SerializableTokenCache()
    cache.deserialize(cache_file.read_text())
    # 从缓存中提取账号信息
    data = json.loads(cache_file.read_text())
    for acct in data.get("Account", {}).values():
        accounts.append({
            "alias": acct.get("username"),
            "cache_file": str(cache_file),
            "home_account_id": acct.get("home_account_id")
        })
print(accounts)
```

### 切换当前账号
```bash
python scripts/auth.py --action login --account work@company.com
python scripts/auth.py --action switch --account personal@outlook.com
python scripts/auth.py --action list   # 列出所有已登录账号
```

---

## 2. Azure AD SSO（企业直连）

对于有 Azure AD 的企业，可以用企业自己注册的 App，获得更高权限和更好的安全审计。

### 需要企业 IT 提供的信息
| 参数            | 说明                                   |
|---------------|--------------------------------------|
| `CLIENT_ID`   | Azure 应用注册的应用（客户端）ID           |
| `TENANT_ID`   | 企业 Azure AD 租户 ID                  |
| `CLIENT_SECRET` | （仅服务端使用，桌面端用证书更安全）         |

### 企业 App 配置（IT 管理员操作）
```
1. Azure Portal → 应用注册 → 新建注册
2. 重定向 URI：设为 http://localhost（Device Code Flow 不需要）
3. API 权限 → 添加以下 Microsoft Graph 权限（委托权限）：
   Mail.ReadWrite / Mail.Send / Calendars.ReadWrite /
   Files.ReadWrite.All / Chat.ReadWrite / ChannelMessage.Send
4. 授予管理员同意（避免每个用户单独授权）
```

### 代码切换到企业 App
```python
# 只需修改 auth.py 中的常量
CLIENT_ID = "你的企业应用CLIENT_ID"
TENANT_ID = "你的企业租户ID"  # 如 "contoso.onmicrosoft.com" 或 GUID
# 其他代码完全不变
```

---

## 3. 共享邮箱 / 资源邮箱访问

企业常见场景：访问 `info@company.com` 这类共享邮箱。

```python
SHARED_MAILBOX = "info@company.com"

# 读取共享邮箱
resp = requests.get(
    f"{MS_GRAPH}/users/{SHARED_MAILBOX}/messages",
    headers=headers,
    params={"$top": 10, "$orderby": "receivedDateTime desc"}
)

# 以共享邮箱身份发送邮件
payload = {
    "message": {
        "subject": "自动回复",
        "body": {"contentType": "Text", "content": "感谢您的来信，我们将在1个工作日内回复。"},
        "toRecipients": [{"emailAddress": {"address": "customer@example.com"}}]
    },
    "saveToSentItems": True
}
requests.post(f"{MS_GRAPH}/users/{SHARED_MAILBOX}/sendMail", headers=headers, json=payload)
```

> **权限要求**：需要 `Mail.ReadWrite.Shared` 或管理员授予对该邮箱的完全访问权。

---

## 4. 审计日志

企业版需记录所有 API 操作，便于合规审查。

```python
# scripts/audit_logger.py
import json, logging
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG = Path.home() / ".openclaw" / "audit.jsonl"

def log_action(action: str, resource: str, result: str, user: str = ""):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "user": user,
        "action": action,       # "send_mail" | "delete_file" | "create_event" etc.
        "resource": resource,   # email subject / file name / event title
        "result": result        # "success" | "failed" | "cancelled"
    }
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

### 查看最近操作记录
```bash
tail -20 ~/.openclaw/audit.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    r = json.loads(line)
    print(f\"{r['ts'][:19]}  {r['action']:20s}  {r['result']:8s}  {r['resource'][:40]}\")
"
```

---

## 5. Conditional Access 适配

企业 Azure AD 可能启用了条件访问策略（如：要求 MFA、只允许特定设备）。

**症状**：登录后立即返回 `AADSTS53003` 或 `AADSTS50076` 错误。

**处理方式**：
```python
# auth.py 中捕获 Claims Challenge
if result.get("error") == "interaction_required":
    claims = result.get("claims")
    if claims:
        # 重新发起带 claims 的设备码流
        flow = app.initiate_device_flow(scopes=SCOPES, claims_challenge=claims)
        print(f"⚠️  需要额外验证（MFA 或设备合规性检查）")
        print(f"请访问: {flow['verification_uri']}  输入: {flow['user_code']}")
        result = app.acquire_token_by_device_flow(flow)
```

---

## 6. 批量 API（降低请求数，提高速率限制利用率）

企业用户批量处理邮件/文件时，使用 `$batch` 减少 API 调用次数。

```python
# 一次请求同时获取邮件 + 日历 + OneDrive 根目录
batch_payload = {
    "requests": [
        {"id": "1", "method": "GET", "url": "/me/messages?$top=5"},
        {"id": "2", "method": "GET", "url": "/me/calendar/events?$top=5"},
        {"id": "3", "method": "GET", "url": "/me/drive/root/children?$top=5"}
    ]
}
resp = requests.post(
    "https://graph.microsoft.com/v1.0/$batch",
    headers=headers,
    json=batch_payload
)
responses = {r["id"]: r["body"] for r in resp.json()["responses"]}
emails   = responses["1"].get("value", [])
events   = responses["2"].get("value", [])
files    = responses["3"].get("value", [])
```

> 单批最多 20 个请求，各子请求独立计入速率限制。
