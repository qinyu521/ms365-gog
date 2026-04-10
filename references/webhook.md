# Webhook 实时通知模块（webhook.md）

> 当用户需要**实时感知** M365 变化（新邮件、日历提醒、文件变更、Teams 消息）时使用本模块。
> 触发词：实时通知、新邮件提醒、监听、订阅变更、自动触发

---

## 核心概念

Graph API 的 Webhook 叫做 **Change Notifications（变更通知）**：
1. 你的服务注册一个 HTTPS 端点（Notification URL）
2. 微软在资源发生变化时 POST 通知到该端点
3. 支持资源：邮件、日历、联系人、OneDrive、Teams 消息、用户等

**OpenClaw 本地场景**（无公网服务器）：使用 **长轮询** 或 **ngrok 临时隧道** 代替真实 Webhook。

---

## 方案一：长轮询（本地推荐，简单可靠）

适合 OpenClaw 本地运行，无需公网端点。

```python
# scripts/poller.py - 定期轮询检查新邮件
import time, requests
from scripts.auth import get_access_token

def poll_new_emails(interval_seconds: int = 60, callback=None):
    """每隔 interval_seconds 检查新邮件"""
    last_check = None

    while True:
        # ✅ 每轮重新获取 token，自动处理 60 分钟过期刷新
        headers = {"Authorization": f"Bearer {get_access_token()}"}

        params = {"$top": 10, "$orderby": "receivedDateTime desc",
                  "$select": "id,subject,from,receivedDateTime,isRead"}
        if last_check:
            params["$filter"] = f"receivedDateTime gt {last_check}"

        try:
            resp = requests.get(
                "https://graph.microsoft.com/v1.0/me/messages",
                headers=headers, params=params, timeout=30
            )
            resp.raise_for_status()
            emails = resp.json().get("value", [])
        except Exception as e:
            print(f"⚠️  轮询出错: {e}，60秒后重试")
            time.sleep(60)
            continue

        if emails:
            for email in emails:
                print(f"📧 新邮件: {email['subject']} from {email['from']['emailAddress']['address']}")
                if callback:
                    callback(email)

        from datetime import datetime, timezone
        last_check = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        time.sleep(interval_seconds)

# 启动：python scripts/poller.py
if __name__ == "__main__":
    poll_new_emails(interval_seconds=30)
```

---

## 方案二：Graph API Webhook（需公网 HTTPS 端点）

### 2.1 用 ngrok 建临时公网端点（开发/测试用）

```bash
# 安装 ngrok 后
ngrok http 8000
# 获得类似 https://xxxx.ngrok.io 的地址
```

### 2.2 启动本地接收服务

```python
# scripts/webhook_server.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Graph 首次验证：返回 validationToken
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(self.path).query)
        if token := qs.get("validationToken"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(token[0].encode())
            return

        # 处理真实通知
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        for notification in body.get("value", []):
            resource = notification.get("resource")
            change_type = notification.get("changeType")
            print(f"🔔 变更通知: {change_type} → {resource}")
            # 在这里触发具体处理逻辑

        self.send_response(202)
        self.end_headers()

    def log_message(self, format, *args):
        pass  # 静默日志

HTTPServer(("0.0.0.0", 8000), WebhookHandler).serve_forever()
```

### 2.3 注册 Webhook 订阅

```python
import requests
from datetime import datetime, timezone, timedelta

NOTIFICATION_URL = "https://xxxx.ngrok.io/webhook"  # 你的公网地址

# 订阅新邮件通知
payload = {
    "changeType": "created",           # created | updated | deleted
    "notificationUrl": NOTIFICATION_URL,
    "resource": "/me/messages",         # 监听资源
    "expirationDateTime": (            # 最长 4230 分钟（约3天）
        datetime.now(timezone.utc) + timedelta(hours=72)
    ).isoformat(),
    "clientState": "ms365-gog-secret"  # 用于验证通知来源
}
resp = requests.post(
    "https://graph.microsoft.com/v1.0/subscriptions",
    headers=headers, json=payload
)
subscription = resp.json()
subscription_id = subscription["id"]
print(f"✅ 订阅成功，ID: {subscription_id}")
```

### 2.4 支持的资源类型

| 监听资源                                         | changeType         | 说明             |
|------------------------------------------------|--------------------|----------------|
| `/me/messages`                                  | created            | 新邮件           |
| `/me/mailFolders('Inbox')/messages`             | created,updated    | 收件箱变更        |
| `/me/events`                                    | created,updated,deleted | 日历变更    |
| `/me/drive/root`                                | updated            | OneDrive 文件变更 |
| `/me/chats/getAllMessages`                       | created            | 所有 Teams 消息  |
| `/teams/{id}/channels/{id}/messages`            | created            | 指定频道消息      |

### 2.5 续期订阅（在过期前调用）

```python
new_expiry = (datetime.now(timezone.utc) + timedelta(hours=72)).isoformat()
requests.patch(
    f"https://graph.microsoft.com/v1.0/subscriptions/{subscription_id}",
    headers=headers,
    json={"expirationDateTime": new_expiry}
)
```

### 2.6 删除订阅

```python
requests.delete(
    f"https://graph.microsoft.com/v1.0/subscriptions/{subscription_id}",
    headers=headers
)
```

---

## 方案三：Delta Query（增量同步，适合离线再上线场景）

```python
# 首次：获取完整列表 + deltaLink
resp = requests.get(
    "https://graph.microsoft.com/v1.0/me/messages/delta",
    headers=headers,
    params={"$select": "subject,from,receivedDateTime"}
)
data = resp.json()
messages = data.get("value", [])

# 保存 deltaLink（下次从这里继续）
delta_link = data.get("@odata.deltaLink")

# 下次调用：只返回变化的邮件（新增/修改/删除）
resp2 = requests.get(delta_link, headers=headers)
changes = resp2.json().get("value", [])
# changes 中 "@removed" 字段存在表示该邮件已删除
```

---

## 推荐使用场景

| 场景                    | 推荐方案             |
|-----------------------|------------------|
| 本地 OpenClaw 实时监控    | 方案一（长轮询）      |
| 服务器部署 / 企业自动化    | 方案二（真实 Webhook）|
| 离线恢复 / 批量同步       | 方案三（Delta Query）|
