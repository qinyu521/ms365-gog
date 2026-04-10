# Outlook 规则管理模块（mail-rules.md）

> 覆盖 Outlook 收件箱规则（Inbox Rules）的查看、创建、修改和删除。
> 触发词：邮件规则、收件箱规则、自动分类、自动转发、自动删除、Rule、过滤邮件

---

## 核心概念

收件箱规则 = **条件（Conditions）** + **动作（Actions）**

当新邮件匹配条件时，自动执行动作：移动到文件夹、标记已读、转发、删除等。

---

## 1. 列出所有规则

```python
MS_GRAPH = "https://graph.microsoft.com/v1.0"

resp = requests.get(
    f"{MS_GRAPH}/me/mailFolders/inbox/messageRules",
    headers=headers,
    timeout=30
)
resp.raise_for_status()
rules = resp.json().get("value", [])

for rule in rules:
    enabled = "✅" if rule.get("isEnabled") else "⏸️"
    print(f"{enabled} [{rule['sequence']:02d}] {rule['displayName']:35s}  优先级:{rule['sequence']}")
    cond = rule.get("conditions", {})
    acts  = rule.get("actions", {})
    if cond.get("subjectContains"):
        print(f"     条件: 主题包含 {cond['subjectContains']}")
    if cond.get("senderContains"):
        print(f"     条件: 发件人包含 {cond['senderContains']}")
    if acts.get("moveToFolder"):
        print(f"     动作: 移动到 {acts['moveToFolder']}")
    if acts.get("delete"):
        print(f"     动作: 删除")
```

---

## 2. 读取单条规则详情

```python
rule_id = "AQAAAxxxxxxx"
resp = requests.get(
    f"{MS_GRAPH}/me/mailFolders/inbox/messageRules/{rule_id}",
    headers=headers,
    timeout=30
)
resp.raise_for_status()
rule = resp.json()
import json
print(json.dumps(rule, ensure_ascii=False, indent=2))
```

---

## 3. 创建规则

### 3.1 自动移动到指定文件夹

```python
# 先获取目标文件夹 ID
folders_resp = requests.get(
    f"{MS_GRAPH}/me/mailFolders",
    headers=headers,
    params={"$select": "id,displayName"},
    timeout=30
)
folders = {f["displayName"]: f["id"] for f in folders_resp.json().get("value", [])}
# 如果文件夹不存在，先创建
if "供应商邮件" not in folders:
    new_folder = requests.post(
        f"{MS_GRAPH}/me/mailFolders",
        headers=headers,
        json={"displayName": "供应商邮件"},
        timeout=30
    ).json()
    target_folder_id = new_folder["id"]
else:
    target_folder_id = folders["供应商邮件"]

# 创建规则
rule_payload = {
    "displayName": "供应商邮件 → 归类到供应商文件夹",
    "sequence": 10,              # 执行优先级，数字越小越先执行
    "isEnabled": True,
    "conditions": {
        "senderContains": ["supplier@", "vendor@", "procurement@"],   # 发件人含任一字符串
        "subjectContains": [],
        "bodyContains": [],
        "importance": "any",
        "hasAttachments": None                                         # None = 不限制
    },
    "actions": {
        "moveToFolder": target_folder_id,
        "markAsRead": True,
        "stopProcessingRules": True   # 匹配后不再继续执行其他规则
    }
}

resp = requests.post(
    f"{MS_GRAPH}/me/mailFolders/inbox/messageRules",
    headers=headers,
    json=rule_payload,
    timeout=30
)
resp.raise_for_status()
new_rule = resp.json()
print(f"✅ 规则已创建：{new_rule['displayName']}  ID: {new_rule['id']}")
```

### 3.2 自动标记重要邮件

```python
vip_rule = {
    "displayName": "VIP 邮件 → 标红 + 重要标记",
    "sequence": 1,               # 最高优先级
    "isEnabled": True,
    "conditions": {
        "fromAddresses": [
            {"emailAddress": {"address": "ceo@company.com"}},
            {"emailAddress": {"address": "cto@company.com"}}
        ]
    },
    "actions": {
        "markImportance": "high",
        "markAsRead": False,
        "forwardTo": [],
        "stopProcessingRules": False
    }
}
```

### 3.3 自动转发规则

```python
forward_rule = {
    "displayName": "客服邮件 → 自动转发给客服团队",
    "sequence": 20,
    "isEnabled": True,
    "conditions": {
        "sentToAddresses": [
            {"emailAddress": {"address": "support@company.com"}}
        ]
    },
    "actions": {
        "forwardTo": [
            {"emailAddress": {"address": "cs-team@company.com", "name": "客服团队"}}
        ],
        "stopProcessingRules": True
    }
}
```

### 3.4 自动删除垃圾邮件

```python
spam_rule = {
    "displayName": "营销垃圾邮件 → 自动删除",
    "sequence": 5,
    "isEnabled": True,
    "conditions": {
        "subjectContains": ["恭喜您中奖", "限时优惠", "免费领取", "点击领取"],
        "bodyContains": ["退订", "unsubscribe"]
    },
    "actions": {
        "delete": True,
        "stopProcessingRules": True
    }
}
```

### 3.5 完整条件字段参考

```python
# conditions 支持的所有字段
conditions_reference = {
    # 字符串匹配（OR 关系，任一匹配即触发）
    "subjectContains":        ["关键词1", "关键词2"],  # 主题包含
    "bodyContains":           ["关键词"],              # 正文包含
    "bodyOrSubjectContains":  ["关键词"],              # 主题或正文包含
    "senderContains":         ["@domain.com"],         # 发件人地址包含
    "recipientContains":      ["team@"],               # 收件人地址包含
    "subjectOrBodyContains":  ["关键词"],

    # 地址匹配
    "fromAddresses": [{"emailAddress": {"address": "boss@co.com"}}],
    "sentToAddresses": [{"emailAddress": {"address": "me@co.com"}}],
    "sentToOrCcAddresses": [...],

    # 其他条件
    "hasAttachments": True,              # 是否有附件
    "importance": "high",                # low | normal | high
    "sensitivity": "private",           # normal | personal | private | confidential
    "isApprovalRequest": False,
    "isAutomaticForward": False,
    "isMeetingRequest": False,
    "isReadReceipt": False,
}

# actions 支持的所有字段
actions_reference = {
    "moveToFolder":        "folder-id",       # 移动到文件夹
    "copyToFolder":        "folder-id",       # 复制到文件夹（原件保留收件箱）
    "delete":              True,              # 移入已删除
    "permanentDelete":     True,              # 永久删除（危险！）
    "markAsRead":          True,
    "markImportance":      "high",           # low | normal | high
    "forwardTo":           [...],            # 转发给
    "forwardAsAttachmentTo": [...],          # 作为附件转发
    "redirectTo":          [...],            # 重定向（原件不保留）
    "assignCategories":    ["蓝色分类"],     # 分配分类标签
    "stopProcessingRules": True,             # 停止后续规则
}
```

---

## 4. 修改规则

```python
# 禁用规则（不删除，只暂停）
requests.patch(
    f"{MS_GRAPH}/me/mailFolders/inbox/messageRules/{rule_id}",
    headers=headers,
    json={"isEnabled": False},
    timeout=30
).raise_for_status()
print("⏸️  规则已禁用")

# 修改规则名称和优先级
requests.patch(
    f"{MS_GRAPH}/me/mailFolders/inbox/messageRules/{rule_id}",
    headers=headers,
    json={
        "displayName": "新规则名称",
        "sequence": 3
    },
    timeout=30
).raise_for_status()

# 追加新的触发关键词
rule = requests.get(
    f"{MS_GRAPH}/me/mailFolders/inbox/messageRules/{rule_id}",
    headers=headers, timeout=30
).json()
existing_keywords = rule["conditions"].get("subjectContains", [])
existing_keywords.append("新关键词")
requests.patch(
    f"{MS_GRAPH}/me/mailFolders/inbox/messageRules/{rule_id}",
    headers=headers,
    json={"conditions": {"subjectContains": existing_keywords}},
    timeout=30
).raise_for_status()
```

---

## 5. 删除规则（需用户确认）

```python
resp = requests.delete(
    f"{MS_GRAPH}/me/mailFolders/inbox/messageRules/{rule_id}",
    headers=headers,
    timeout=30
)
if resp.status_code == 204:
    print("✅ 规则已删除")
```

---

## 6. 实用辅助：列出所有邮件文件夹（含 ID）

创建移动规则时需要文件夹 ID，用此函数查询：

```python
def list_all_folders(headers: dict, parent_id: str = None) -> list[dict]:
    """递归列出所有邮件文件夹"""
    if parent_id:
        url = f"{MS_GRAPH}/me/mailFolders/{parent_id}/childFolders"
    else:
        url = f"{MS_GRAPH}/me/mailFolders"
    resp = requests.get(url, headers=headers,
                        params={"$select": "id,displayName,totalItemCount"},
                        timeout=30)
    resp.raise_for_status()
    folders = resp.json().get("value", [])
    result = []
    for f in folders:
        result.append(f)
        result.extend(list_all_folders(headers, f["id"]))  # 递归子文件夹
    return result

all_folders = list_all_folders(headers)
for f in all_folders:
    print(f"📁 {f['displayName']:30s}  ({f['totalItemCount']} 封)  ID: {f['id']}")
```

---

## 输出格式建议

**规则列表展示：**
```
📋 收件箱规则（共 5 条）
══════════════════════════════════════════════════════════════
✅ [01] VIP 邮件 → 标红                    发件人: ceo@, cto@
✅ [05] 营销垃圾 → 自动删除               主题含: 恭喜, 优惠
⏸️  [10] 供应商邮件 → 归类               发件人含: supplier@
✅ [20] 客服邮件 → 转发                   收件人: support@
✅ [99] 会议邀请 → 移到日历文件夹         类型: 会议请求
```

---

## 注意事项

1. **sequence 顺序**：数字越小优先级越高，同一 sequence 值时行为未定义
2. **规则数量上限**：Outlook 规则上限通常为 256 条（取决于账号设置）
3. **permanentDelete 危险**：永久删除的邮件无法恢复，生产环境慎用，建议改用 `delete`（移入废纸篓）
4. **客户端规则 vs 服务端规则**：Graph API 只管理服务端规则（即使 Outlook 客户端未打开也会执行）；Outlook 客户端规则（仅在客户端运行时执行）无法通过 API 管理
5. **共享邮箱规则**：需要将 URL 中的 `/me/` 替换为 `/users/{mailbox@domain}/`
