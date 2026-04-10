# Power Automate 触发器集成模块（power-automate.md）

> 覆盖通过 HTTP 触发器调用 Power Automate 流，以及查询和管理流的状态。
> 触发词：Power Automate、Flow、自动化流程、触发流、审批流、工作流、自动化

---

## 集成架构

OpenClaw 与 Power Automate 有两种集成方式：

```
方式 A（推荐）：HTTP 触发器
  OpenClaw → HTTP POST → Power Automate 即时流 → 任意 M365 操作

方式 B：Graph API 管理
  OpenClaw → Graph API → 查询/启停已有的流
```

方式 A 功能最强，支持双向通信（流可返回结果给 OpenClaw）。

---

## 方式 A：HTTP 触发器调用 Power Automate 流

### A-1 在 Power Automate 中创建 HTTP 触发流

1. 打开 [Power Automate](https://make.powerautomate.com)
2. 新建 → **即时云端流**
3. 触发器选择：**当收到 HTTP 请求时**（When a HTTP request is received）
4. 在触发器中设置请求正文 JSON 架构（可选但推荐）：

```json
{
    "type": "object",
    "properties": {
        "action":  {"type": "string"},
        "payload": {"type": "object"},
        "from":    {"type": "string"}
    }
}
```

5. 保存流后，触发器会生成一个 **HTTP POST URL**（含 SAS Token，复制备用）

### A-2 从 OpenClaw 触发流

```python
import requests, json

FLOW_TRIGGER_URL = "https://prod-xx.westeurope.logic.azure.com:443/workflows/.../triggers/manual/paths/invoke?..."
# ⚠️ 此 URL 含密钥，应存入环境变量：os.environ["FLOW_URL_审批"]

def trigger_flow(flow_url: str, action: str, payload: dict) -> dict:
    """触发 Power Automate 流，返回流的响应（如有）"""
    body = {
        "action": action,
        "payload": payload,
        "from": "OpenClaw ms365-gog"
    }
    resp = requests.post(
        flow_url,
        json=body,
        timeout=60   # 流可能有较长处理时间
    )
    resp.raise_for_status()

    # 如果流配置了"回复 HTTP 请求"动作，可以读取返回值
    if resp.status_code == 200 and resp.content:
        return resp.json()
    return {"status": "accepted", "http_status": resp.status_code}

# 使用示例：触发采购审批流
result = trigger_flow(
    flow_url=os.environ["FLOW_URL_PURCHASE_APPROVAL"],
    action="create_approval",
    payload={
        "amount": 58000,
        "currency": "CNY",
        "item": "服务器采购",
        "requester": "张三",
        "department": "技术部",
        "urgency": "normal"
    }
)
print(f"流已触发：{result}")
```

### A-3 带回调的双向通信

Power Automate 流执行可能需要时间（如等待人工审批），可用回调 URL 通知结果：

```python
import uuid, threading

CALLBACK_RESULTS = {}  # 存储异步回调结果

def trigger_flow_async(flow_url: str, payload: dict, callback_endpoint: str) -> str:
    """触发流并附带回调 URL，返回 correlation_id 用于后续查询"""
    correlation_id = str(uuid.uuid4())
    payload["_callback_url"] = callback_endpoint
    payload["_correlation_id"] = correlation_id

    requests.post(flow_url, json=payload, timeout=30).raise_for_status()
    return correlation_id

# Power Automate 流执行完成后，会 POST 到你的 callback_endpoint：
# {
#   "correlation_id": "xxx",
#   "status": "approved",
#   "approver": "李四",
#   "comment": "金额合理，同意"
# }
```

---

## 常用流模板示例

### 模板 1：邮件触发审批并通知 Teams

在 Power Automate 中配置如下流，从 OpenClaw 传入数据后自动处理：

```
触发器: 当收到 HTTP 请求时
  ↓
动作1: 发起审批（内置审批连接器）
  - 审批者: @{triggerBody()?['payload']?['approver']}
  - 标题: @{triggerBody()?['payload']?['title']}
  ↓
条件: 审批结果 == '批准'
  是: 发送 Teams 消息（"审批通过：..."）
  否: 发送邮件（"审批拒绝：..."）
  ↓
动作2: 回复 HTTP 请求（返回审批结果给 OpenClaw）
  - 状态码: 200
  - 正文: {"result": "@{body('开始并等待审批')?['outcome']}", "approver": "..."}
```

对应的 OpenClaw 调用：
```python
result = trigger_flow(
    flow_url=os.environ["FLOW_URL_APPROVAL"],
    action="request_approval",
    payload={
        "title": "差旅报销申请 - 张三 - ¥3,200",
        "approver": "manager@company.com",
        "amount": 3200,
        "description": "出差上海，参加客户评审会"
    }
)
print(f"审批结果：{result.get('result')}，审批人：{result.get('approver')}")
```

### 模板 2：定时生成报告并发邮件

```python
# 触发"每周报告"流（流内部配置了数据查询 + Excel 写入 + 邮件发送）
trigger_flow(
    flow_url=os.environ["FLOW_URL_WEEKLY_REPORT"],
    action="generate_report",
    payload={
        "report_type": "weekly_sales",
        "week": "2025-W26",
        "recipients": ["boss@company.com", "team@company.com"]
    }
)
print("✅ 报告生成流已触发，邮件将在 2-3 分钟内送达")
```

### 模板 3：跨系统数据同步

```python
# 触发 CRM 同步流（将新客户信息同步到 SharePoint 列表）
trigger_flow(
    flow_url=os.environ["FLOW_URL_CRM_SYNC"],
    action="sync_customer",
    payload={
        "customer_name": "ABC 科技有限公司",
        "contact": "王总",
        "phone": "138xxxxxxxx",
        "source": "展会",
        "assigned_to": "salesperson@company.com"
    }
)
```

---

## 方式 B：Graph API 管理已有的流

> ⚠️ Power Automate 的 Graph API 支持有限，以下为当前可用接口。

### B-1 列出我的流

```python
resp = requests.get(
    "https://graph.microsoft.com/v1.0/me/drives",  # 目前通过 Flow API 访问
    headers=headers,
    timeout=30
)

# 实际使用 Power Platform API（不是 Graph API）
FLOW_API = "https://api.flow.microsoft.com/providers/Microsoft.ProcessSimple"
ENVIRONMENT = "Default-{tenant-id}"  # 从 Power Automate 门户获取环境 ID

flows_resp = requests.get(
    f"{FLOW_API}/environments/{ENVIRONMENT}/flows",
    headers=headers,  # 需要额外的 Flow API scope: https://service.flow.microsoft.com//.default
    params={"api-version": "2016-11-01"},
    timeout=30
)
flows = flows_resp.json().get("value", [])
for flow in flows:
    props = flow.get("properties", {})
    state = props.get("state", "unknown")
    icon = "✅" if state == "Started" else "⏸️"
    print(f"{icon} {props.get('displayName'):40s}  状态: {state}")
```

### B-2 启用/停用流

```python
FLOW_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# 停用流
requests.post(
    f"{FLOW_API}/environments/{ENVIRONMENT}/flows/{FLOW_ID}/stop",
    headers=headers,
    params={"api-version": "2016-11-01"},
    timeout=30
).raise_for_status()
print("⏸️  流已停用")

# 启用流
requests.post(
    f"{FLOW_API}/environments/{ENVIRONMENT}/flows/{FLOW_ID}/start",
    headers=headers,
    params={"api-version": "2016-11-01"},
    timeout=30
).raise_for_status()
print("✅ 流已启用")
```

### B-3 查看流运行历史

```python
resp = requests.get(
    f"{FLOW_API}/environments/{ENVIRONMENT}/flows/{FLOW_ID}/runs",
    headers=headers,
    params={"api-version": "2016-11-01", "$top": 10},
    timeout=30
)
runs = resp.json().get("value", [])
for run in runs:
    props = run.get("properties", {})
    status = props.get("status")
    start = props.get("startTime", "")[:19].replace("T", " ")
    icon = {"Succeeded": "✅", "Failed": "❌", "Running": "⏳"}.get(status, "❓")
    print(f"{icon} {start}  {status}")
```

---

## 环境变量管理（安全存储流 URL）

流的 HTTP 触发 URL 包含密钥，绝对不能硬编码或提交到 Git。

```python
# 推荐：用系统环境变量管理
import os

FLOW_URLS = {
    "审批":    os.environ.get("FLOW_URL_APPROVAL"),
    "周报":    os.environ.get("FLOW_URL_WEEKLY_REPORT"),
    "CRM同步": os.environ.get("FLOW_URL_CRM_SYNC"),
}

def get_flow_url(name: str) -> str:
    url = FLOW_URLS.get(name)
    if not url:
        raise ValueError(
            f"未找到流 '{name}' 的触发 URL。\n"
            f"请设置环境变量：export FLOW_URL_{name.upper().replace(' ', '_')}='你的流URL'"
        )
    return url
```

---

## 输出格式建议

- 触发后立即告知：`⚡ 已触发"[流名称]"，正在处理...`
- 同步流（有返回值）：展示返回的结构化结果
- 异步流（无返回值）：说明预计完成时间和通知方式
- 失败时：显示 HTTP 状态码 + 错误描述，并建议检查流的运行历史

---

## 注意事项

1. **URL 安全**：HTTP 触发 URL 含 SAS Token，泄露等同于密钥泄露，必须用环境变量存储
2. **超时设置**：含人工审批的流可能需要数小时，调用时设置较长 timeout 或改用异步回调
3. **Flow API Scope**：管理流本身需要额外申请 `https://service.flow.microsoft.com//.default` scope，与 Graph API Token 不同
4. **Premium 连接器**：部分 Power Automate 连接器需要 Premium 许可证（如 HTTP 连接器、SAP、Salesforce）
5. **环境隔离**：生产流和测试流应在不同 Power Platform 环境中管理
