# 任务管理模块（tasks.md）

> 覆盖 **Microsoft To Do**（个人任务）和 **Microsoft Planner**（团队任务看板）。
> 触发词：任务、待办、To Do、Planner、看板、deadline、提醒事项

---

## Microsoft To Do（个人任务）

### 列出任务列表（任务夹）

```python
resp = requests.get(f"{MS_GRAPH}/me/todo/lists", headers=headers)
task_lists = resp.json().get("value", [])
# 每项含：id, displayName, isOwner, isShared
for lst in task_lists:
    print(f"{lst['displayName']}  (id: {lst['id']})")
```

### 列出指定任务夹中的任务

```python
list_id = "AQMkAD..."  # 从上方获取
resp = requests.get(
    f"{MS_GRAPH}/me/todo/lists/{list_id}/tasks",
    headers=headers,
    params={
        "$filter": "status ne 'completed'",  # 只看未完成
        "$orderby": "importance desc,dueDateTime/dateTime asc",
        "$select": "title,status,importance,dueDateTime,reminderDateTime,body"
    }
)
tasks = resp.json().get("value", [])
```

### 创建新任务

```python
payload = {
    "title": "准备Q3汇报PPT",
    "importance": "high",          # "low" | "normal" | "high"
    "status": "notStarted",
    "dueDateTime": {
        "dateTime": "2025-06-30T18:00:00.000000",
        "timeZone": "Asia/Shanghai"
    },
    "reminderDateTime": {
        "dateTime": "2025-06-30T09:00:00.000000",
        "timeZone": "Asia/Shanghai"
    },
    "isReminderOn": True,
    "body": {
        "content": "需要包含：财务数据、用户增长、下季度OKR",
        "contentType": "text"
    }
}
resp = requests.post(
    f"{MS_GRAPH}/me/todo/lists/{list_id}/tasks",
    headers=headers,
    json=payload
)
task = resp.json()
print(f"✅ 任务已创建：{task['title']}  ID: {task['id']}")
```

### 更新任务（标记完成 / 修改截止日期）

```python
# 标记完成
requests.patch(
    f"{MS_GRAPH}/me/todo/lists/{list_id}/tasks/{task_id}",
    headers=headers,
    json={"status": "completed"}
)

# 修改截止日期
requests.patch(
    f"{MS_GRAPH}/me/todo/lists/{list_id}/tasks/{task_id}",
    headers=headers,
    json={"dueDateTime": {"dateTime": "2025-07-15T18:00:00", "timeZone": "Asia/Shanghai"}}
)
```

### 添加任务步骤（子任务）

```python
requests.post(
    f"{MS_GRAPH}/me/todo/lists/{list_id}/tasks/{task_id}/checklistItems",
    headers=headers,
    json={"displayName": "收集各部门数据", "isChecked": False}
)
```

### 创建新任务夹

```python
resp = requests.post(
    f"{MS_GRAPH}/me/todo/lists",
    headers=headers,
    json={"displayName": "项目跟踪 - 2025H2"}
)
```

---

## Microsoft Planner（团队任务 / 看板）

> ⚠️ Planner 仅支持企业（AAD）账号，需要对应 Microsoft 365 Group。

### 获取我参与的计划（Plan）

```python
resp = requests.get(f"{MS_GRAPH}/me/planner/plans", headers=headers)
plans = resp.json().get("value", [])
```

### 列出计划中的任务

```python
plan_id = "xxx"
resp = requests.get(
    f"{MS_GRAPH}/planner/plans/{plan_id}/tasks",
    headers=headers
)
tasks = resp.json().get("value", [])
# 含：title, assigneePriority, percentComplete, bucketId, dueDateTime, assignments
```

### 获取看板列（Bucket）

```python
resp = requests.get(f"{MS_GRAPH}/planner/plans/{plan_id}/buckets", headers=headers)
buckets = resp.json().get("value", [])
# buckets: 待办 / 进行中 / 已完成 等自定义列名
```

### 创建 Planner 任务

```python
payload = {
    "planId": plan_id,
    "bucketId": bucket_id,       # 分配到哪一列
    "title": "设计新版登录页",
    "dueDateTime": "2025-07-01T15:00:00Z",
    "assignments": {
        "user-object-id": {      # 指派给某用户（需 AAD Object ID）
            "@odata.type": "#microsoft.graph.plannerAssignment",
            "orderHint": " !"
        }
    }
}
resp = requests.post(f"{MS_GRAPH}/planner/tasks", headers=headers, json=payload)
```

### 更新任务进度

```python
import requests  # 必须用 requests 库才能读响应头

# 先获取 ETag（Planner 所有更新操作必须携带，否则返回 412）
task_resp = requests.get(
    f"{MS_GRAPH}/planner/tasks/{task_id}",
    headers=headers,
    timeout=30
)
task_resp.raise_for_status()
etag = task_resp.headers["ETag"]  # 不用 .get()，缺少 ETag 应报错而非静默

requests.patch(
    f"{MS_GRAPH}/planner/tasks/{task_id}",
    headers={**headers, "If-Match": etag},
    json={"percentComplete": 50},   # 0 / 50 / 100
    timeout=30
).raise_for_status()
```

---

## 输出格式建议

**To Do 任务列表展示：**
```
📋 工作任务（5项未完成）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 [高] 准备Q3汇报PPT          截止 6/30
🟡 [中] 回复客户邮件            截止 6/25
🟢 [低] 整理文档归档            无截止日期
```

**Planner 看板展示：**
```
📊 产品迭代 Sprint 12
┌─ 待办(3) ──┬─ 进行中(2) ──┬─ 已完成(5) ─┐
│ 设计登录页  │ API 开发      │ 需求评审    │
│ 写测试用例  │ UI走查        │ ...         │
└────────────┴──────────────┴─────────────┘
```
