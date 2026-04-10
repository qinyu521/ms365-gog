# SharePoint 列表 / 文档库模块（sharepoint.md）

> 覆盖 SharePoint Online 的核心操作：站点浏览、文档库读写、列表 CRUD、权限管理、搜索。
> 触发词：SharePoint、站点、文档库、列表、SP列表、团队网站、发布页面、intranet

---

## 基础概念速查

```
租户
└── 站点集（Site Collection）        e.g. https://company.sharepoint.com/sites/project-alpha
    ├── 文档库（Document Library）    类似 OneDrive，但归团队/站点所有
    │   └── 文件夹 / 文件
    ├── 列表（List）                  结构化数据表，类似轻量数据库
    │   └── 列表项（List Item）
    └── 页面（Pages）                 Intranet 新闻/Wiki 页面
```

**端点规律**：所有 SharePoint 操作通过 Graph API 的 `/sites/{site-id}/` 前缀访问。

---

## 1. 站点（Site）操作

### 查找站点（按关键词搜索）
```python
resp = requests.get(
    f"{MS_GRAPH}/sites",
    headers=headers,
    params={"search": "project"}  # 搜索站点名称/URL
)
sites = resp.json().get("value", [])
for s in sites:
    print(f"{s['displayName']:30s}  {s['webUrl']}")
    # s["id"] 格式："{hostname},{site-guid},{web-guid}"
```

### 按 URL 精确获取站点 ID
```python
# hostname 和 path 分开传
hostname = "company.sharepoint.com"
site_path = "/sites/project-alpha"
resp = requests.get(
    f"{MS_GRAPH}/sites/{hostname}:{site_path}",
    headers=headers
)
site = resp.json()
SITE_ID = site["id"]   # 保存备用
```

### 列出我关注的站点
```python
resp = requests.get(f"{MS_GRAPH}/me/followedSites", headers=headers)
```

### 列出站点下所有列表（含文档库）
```python
resp = requests.get(
    f"{MS_GRAPH}/sites/{SITE_ID}/lists",
    headers=headers,
    params={"$select": "id,name,displayName,list,webUrl"}
)
lists = resp.json().get("value", [])
# list["list"]["template"]: "documentLibrary" | "genericList" | "tasks" etc.
doc_libs = [l for l in lists if l.get("list", {}).get("template") == "documentLibrary"]
generic_lists = [l for l in lists if l.get("list", {}).get("template") == "genericList"]
```

---

## 2. 文档库（Document Library）

> 文档库本质上是带版本控制和权限的 OneDrive Drive，Graph API 通过 `/sites/{site}/drives/` 访问。

### 获取站点的所有文档库（Drive）
```python
resp = requests.get(f"{MS_GRAPH}/sites/{SITE_ID}/drives", headers=headers, timeout=30)
drives = resp.json().get("value", [])
# 找到目标文档库，找不到则取第一个，都没有则报错
lib = next((d for d in drives if d["name"] == "Documents"), None)
if lib is None:
    lib = drives[0] if drives else None
if lib is None:
    raise ValueError("该站点没有文档库，请先在 SharePoint 中创建")
DRIVE_ID = lib["id"]
```

### 浏览文档库根目录
```python
resp = requests.get(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/root/children",
    headers=headers,
    params={"$select": "name,size,lastModifiedDateTime,webUrl,folder,file,createdBy"}
)
items = resp.json().get("value", [])
```

### 按路径访问子文件夹
```python
folder_path = "2025年/Q2资料/合同"
resp = requests.get(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/root:/{folder_path}:/children",
    headers=headers
)
```

### 上传文件到文档库
```python
# 小文件（< 4MB）
with open("report.docx", "rb") as f:
    data = f.read()

resp = requests.put(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/root:/2025年/report.docx:/content",
    headers={**headers, "Content-Type": "application/octet-stream"},
    data=data,
    timeout=60
)
resp.raise_for_status()  # 非 2xx 立即抛 HTTPError
print(resp.json().get("webUrl", "（上传成功，无链接）"))
```

### 下载文件
```python
# 先获取下载 URL
item_resp = requests.get(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/root:/路径/file.xlsx",
    headers=headers,
    timeout=30
)
item_resp.raise_for_status()
download_url = item_resp.json().get("@microsoft.graph.downloadUrl")
if not download_url:
    raise ValueError("文件不存在或无下载权限")

# 直接下载（该 URL 临时有效，无需 Auth header）
content = requests.get(download_url, timeout=120).content
with open("local_file.xlsx", "wb") as f:
    f.write(content)
```

### 创建文件夹
```python
requests.post(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/root/children",
    headers=headers,
    json={
        "name": "新项目文件夹",
        "folder": {},
        "@microsoft.graph.conflictBehavior": "rename"  # fail | replace | rename
    }
)
```

### 复制 / 移动文件
```python
# 复制（异步操作，返回 Monitor URL）
resp = requests.post(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/items/{item_id}/copy",
    headers=headers,
    json={
        "parentReference": {"driveId": DRIVE_ID, "id": target_folder_id},
        "name": "副本_report.docx"
    }
)
monitor_url = resp.headers.get("Location")  # 轮询此URL查看进度

# 移动（同步）
requests.patch(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/items/{item_id}",
    headers=headers,
    json={"parentReference": {"id": target_folder_id}}
)
```

### 获取文件版本历史
```python
resp = requests.get(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/items/{item_id}/versions",
    headers=headers
)
versions = resp.json().get("value", [])
# 还原到指定版本
requests.post(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/items/{item_id}/versions/{version_id}/restoreVersion",
    headers=headers
)
```

### 生成分享链接
```python
resp = requests.post(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/items/{item_id}/createLink",
    headers=headers,
    json={
        "type": "view",           # view | edit | embed
        "scope": "organization",  # anonymous | organization | users
        "expirationDateTime": "2025-12-31T23:59:00Z"  # 可选，设置过期
    }
)
share_link = resp.json()["link"]["webUrl"]
```

---

## 3. 列表（List）CRUD

> SharePoint List 是企业最常用的轻量数据库，用于管理项目跟踪、审批流程、资产登记等。

### 获取列表字段定义（Column Schema）
```python
LIST_ID = "xxx-list-id"
resp = requests.get(
    f"{MS_GRAPH}/sites/{SITE_ID}/lists/{LIST_ID}/columns",
    headers=headers
)
columns = resp.json().get("value", [])
for col in columns:
    col_type = next((k for k in ['text','number','choice','dateTime','boolean','lookup','personOrGroup']
                     if k in col), '?')
    print(f"{col['name']:20s} {col['displayName']:20s} {col_type}")
```

### 读取列表项
```python
resp = requests.get(
    f"{MS_GRAPH}/sites/{SITE_ID}/lists/{LIST_ID}/items",
    headers=headers,
    params={
        "$expand": "fields",           # 必须展开 fields 才能读取字段值
        # ⚠️ 注意：Graph API 不支持同时使用 $expand=fields 和 $filter=fields/xxx
        # 需要过滤时用客户端过滤（见下方示例）或 SharePoint REST API
        "$orderby": "createdDateTime desc",
        "$top": 50,
        "$select": "id,createdDateTime,fields"
    },
    timeout=30
)
items = resp.json().get("value", [])

# 客户端过滤（替代 $filter=fields/Status eq '进行中'）
items = [i for i in items if i["fields"].get("Status") == "进行中"]

for item in items:
    fields = item["fields"]
    print(f"{fields.get('Title')}  |  {fields.get('Status')}  |  {fields.get('DueDate')}")
```

### 创建列表项
```python
# 字段名使用 SharePoint 内部列名（可从 columns 接口获取）
resp = requests.post(
    f"{MS_GRAPH}/sites/{SITE_ID}/lists/{LIST_ID}/items",
    headers=headers,
    json={
        "fields": {
            "Title": "第三方审计报告审阅",
            "Status": "待处理",
            # ⚠️ 人员字段（Person column）不能直接用邮箱，需 LoginName 格式
            # 先查用户：user = requests.get(f"{MS_GRAPH}/users/email@co.com", headers=headers).json()
            # 再填：[{"loginName": f"i:0#.f|membership|{user['userPrincipalName']}"}]
            "AssignedTo": [{"loginName": "i:0#.f|membership|user@company.com"}],
            "Priority": "高",
            "DueDate": "2025-07-15",
            "Description": "需在Q3结束前完成SOC2审计报告审阅"
        }
    },
    timeout=30
)
resp.raise_for_status()
new_item = resp.json()
print(f"✅ 已创建列表项 ID: {new_item['id']}")
```

### 更新列表项
```python
requests.patch(
    f"{MS_GRAPH}/sites/{SITE_ID}/lists/{LIST_ID}/items/{item_id}/fields",
    headers=headers,
    json={"Status": "已完成", "CompletedDate": "2025-06-28"}
)
```

### 删除列表项（需用户确认）
```python
requests.delete(
    f"{MS_GRAPH}/sites/{SITE_ID}/lists/{LIST_ID}/items/{item_id}",
    headers=headers
)
# 204 = 成功
```

### 批量读取（处理分页）
```python
def get_all_items(site_id, list_id, headers, filter_expr=None):
    """自动处理分页，返回全部列表项"""
    url = f"{MS_GRAPH}/sites/{site_id}/lists/{list_id}/items"
    params = {"$expand": "fields", "$top": 200}
    if filter_expr:
        params["$filter"] = filter_expr
    
    all_items = []
    while url:
        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()
        all_items.extend(data.get("value", []))
        url = data.get("@odata.nextLink")  # 有则继续翻页
        params = {}  # nextLink 已包含所有参数
    return all_items
```

---

## 4. 全文搜索

### 搜索站点内所有内容（文件 + 列表项）
```python
resp = requests.post(
    f"{MS_GRAPH}/search/query",
    headers=headers,
    json={
        "requests": [{
            "entityTypes": ["driveItem", "listItem", "site"],
            "query": {"queryString": "合同 AND 2025"},
            "from": 0,
            "size": 10,
            "fields": ["title", "webUrl", "lastModifiedDateTime", "author"],
            "contentSources": [f"/sites/{SITE_ID}"]  # 限定站点范围
        }]
    }
)
hits = resp.json()["value"][0].get("hitsContainers", [])
for container in hits:
    for hit in container.get("hits", []):
        r = hit["resource"]
        print(f"{r.get('name') or r.get('subject')}  →  {r.get('webUrl')}")
```

### 跨租户全局搜索
```python
# 去掉 contentSources 限制，搜索范围扩展到全租户
payload = {
    "requests": [{
        "entityTypes": ["driveItem"],
        "query": {"queryString": "Q2财务报告"},
        "from": 0,
        "size": 10
    }]
}
resp = requests.post(f"{MS_GRAPH}/search/query", headers=headers,
                     json=payload, timeout=30)
resp.raise_for_status()
hits = resp.json()["value"][0].get("hitsContainers", [])
for container in hits:
    for hit in container.get("hits", []):
        r = hit["resource"]
        print(f"{r.get('name')}  →  {r.get('webUrl')}")
```

---

## 5. 权限管理

### 查看文件/文件夹现有权限
```python
resp = requests.get(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/items/{item_id}/permissions",
    headers=headers
)
perms = resp.json().get("value", [])
for p in perms:
    roles = p.get("roles", [])
    granted = p.get("grantedToV2", {})
    user = granted.get("user", {}).get("displayName", "（继承）")
    print(f"{user:30s} → {roles}")
```

### 邀请用户访问文件
```python
requests.post(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/items/{item_id}/invite",
    headers=headers,
    json={
        "requireSignIn": True,
        "sendInvitation": True,          # 是否发邮件通知
        "roles": ["read"],               # read | write
        "recipients": [
            {"email": "partner@external.com"}
        ],
        "message": "请查阅此文档并在本周五前反馈意见。"
    }
)
```

### 移除权限
```python
requests.delete(
    f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/items/{item_id}/permissions/{perm_id}",
    headers=headers
)
```

---

## 6. 常见企业场景示例

### 场景：自动归档邮件附件到 SharePoint
```python
# 1. 获取邮件附件
attachments_resp = requests.get(
    f"{MS_GRAPH}/me/messages/{message_id}/attachments",
    headers=headers
)
for att in attachments_resp.json().get("value", []):
    if att["@odata.type"] == "#microsoft.graph.fileAttachment":
        import base64
        content = base64.b64decode(att["contentBytes"])
        filename = att["name"]
        
        # 2. 上传到 SharePoint 文档库
        requests.put(
            f"{MS_GRAPH}/sites/{SITE_ID}/drives/{DRIVE_ID}/root:/邮件附件/{filename}:/content",
            headers={**headers, "Content-Type": att["contentType"]},
            data=content
        )
        print(f"✅ {filename} 已归档到 SharePoint")
```

### 场景：从 Excel 批量导入数据到 SharePoint 列表
```python
import openpyxl, io, requests

# 1. 从 OneDrive 下载 Excel
dl_url = requests.get(
    f"{MS_GRAPH}/me/drive/root:/数据导入.xlsx",
    headers=headers
).json()["@microsoft.graph.downloadUrl"]
wb = openpyxl.load_workbook(io.BytesIO(requests.get(dl_url).content))
ws = wb.active

headers_row = [cell.value for cell in ws[1]]  # 第一行为列名

# 2. 逐行写入 SharePoint 列表
for row in ws.iter_rows(min_row=2, values_only=True):
    fields = dict(zip(headers_row, row))
    fields = {k: str(v) if v is not None else "" for k, v in fields.items()}
    requests.post(
        f"{MS_GRAPH}/sites/{SITE_ID}/lists/{LIST_ID}/items",
        headers=headers,
        json={"fields": fields}
    )
print(f"✅ 已导入 {ws.max_row - 1} 条记录")
```

---

## 输出格式建议

**文档库文件列表：**
```
📁 Documents / 2025年 / Q2资料
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 合同模板v3.docx          128 KB   修改于 06/15  张三
📊 Q2财务汇总.xlsx           2.3 MB   修改于 06/20  李四
📁 审计资料/                  —        含 12 个文件
```

**列表项展示：**
```
📋 项目跟踪列表（共 23 项，8项进行中）
┌────────────────────┬────────┬─────────┬──────────┐
│ 标题               │ 状态   │ 负责人  │ 截止日期 │
├────────────────────┼────────┼─────────┼──────────┤
│ 第三方审计报告审阅  │ 待处理 │ 王五    │ 07/15    │
│ 新官网上线         │ 进行中 │ 赵六    │ 07/30    │
└────────────────────┴────────┴─────────┴──────────┘
```

---

## 注意事项

1. **列名陷阱**：SharePoint 列表字段的"显示名称"和"内部列名"可能不同（尤其中文列名），创建/更新时使用内部列名，先用 `/columns` 接口确认
2. **分页必须处理**：列表项超过 200 条时 Graph API 会返回 `@odata.nextLink`，必须循环翻页
3. **权限继承**：文件默认继承父文件夹权限，单独授权前先调用 `/permissions` 确认
4. **中国区差异**：SharePoint 中国区域名为 `.sharepoint.cn`，参见 `references/china-cloud.md`
5. **大文件上传**：文档库文件 ≥ 4MB 时使用 OneDrive 分块上传接口（参见 `references/onedrive.md`），驱动器 ID 替换为文档库 Drive ID 即可
