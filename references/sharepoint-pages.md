# SharePoint 页面模块（sharepoint-pages.md）

> 覆盖 SharePoint Online 的新闻页面、Wiki 页面的创建、编辑、发布和管理。
> 触发词：SharePoint页面、新闻、公告、Intranet、发布文章、创建页面、Wiki

---

## 核心概念

```
站点（Site）
└── Pages 文档库（系统库，通常无法重命名）
    ├── 新闻页面（News Post）     — 有时效性，出现在新闻 Web Part 中
    ├── 网站页面（Site Page）     — 长期存在的 Wiki / 文档页
    └── 模板页面（Page Template） — 可复用的页面布局
```

SharePoint 页面通过 Graph API 的 **Site Pages** 端点管理，底层是 `SitePage` 资源。

---

## 1. 列出站点页面

```python
MS_GRAPH = "https://graph.microsoft.com/v1.0"

# 列出所有页面（含草稿）
resp = requests.get(
    f"{MS_GRAPH}/sites/{SITE_ID}/pages",
    headers=headers,
    params={
        "$select": "id,title,webUrl,publishingState,createdDateTime,lastModifiedDateTime,createdBy",
        "$orderby": "lastModifiedDateTime desc",
        "$top": 20
    },
    timeout=30
)
resp.raise_for_status()
pages = resp.json().get("value", [])

for page in pages:
    state = page.get("publishingState", {}).get("level", "unknown")
    icon = "🟢" if state == "published" else "📝"
    print(f"{icon} {page['title']:40s} {state:12s} {page['lastModifiedDateTime'][:10]}")
```

### 只看已发布页面

```python
resp = requests.get(
    f"{MS_GRAPH}/sites/{SITE_ID}/pages",
    headers=headers,
    params={"$filter": "publishingState/level eq 'published'"},
    timeout=30
)
```

---

## 2. 读取页面内容

```python
page_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# 获取页面完整内容（含 Web Parts）
resp = requests.get(
    f"{MS_GRAPH}/sites/{SITE_ID}/pages/{page_id}/microsoft.graph.sitePage?$expand=canvasLayout",
    headers=headers,
    timeout=30
)
resp.raise_for_status()
page = resp.json()

title    = page.get("title")
web_url  = page.get("webUrl")
layout   = page.get("canvasLayout", {})

# 提取文本内容（遍历所有 Web Part）
def extract_text_from_layout(layout: dict) -> str:
    texts = []
    for section in layout.get("horizontalSections", []):
        for column in section.get("columns", []):
            for webpart in column.get("webparts", []):
                inner = webpart.get("innerHtml", "")
                if inner:
                    # 简单去除 HTML 标签
                    import re
                    texts.append(re.sub(r"<[^>]+>", "", inner).strip())
    return "\n\n".join(t for t in texts if t)

content = extract_text_from_layout(layout)
print(f"📄 {title}\n{'-'*40}\n{content[:500]}...")
```

---

## 3. 创建新页面

### 3.1 创建基础网站页面（Site Page）

```python
payload = {
    "@odata.type": "#microsoft.graph.sitePage",
    "title": "2025年Q3项目进展报告",
    "name": "q3-progress-2025.aspx",          # URL 文件名，需唯一
    "pageLayout": "article",                    # article | home | microsoftReserved
    "promotionKind": "page",                    # page（普通页面）| newsPost（新闻）
    "showComments": True,
    "showRecommendedPages": True,
    "titleArea": {
        "enableGradientEffect": True,
        "imageWebUrl": "",                      # 可选封面图 URL
        "layout": "colorBlock",                 # plain | colorBlock | overlap | FullWidthImage
        "showAuthor": True,
        "showPublishedDate": True,
        "showTextBlockAboveTitle": False,
        "title": "2025年Q3项目进展报告",
        "textAboveTitle": ""
    },
    "canvasLayout": {
        "horizontalSections": [
            {
                "layout": "oneColumn",          # oneColumn | twoColumns | threeColumns | oneThirdLeftColumn
                "id": "1",
                "emphasis": "none",             # none | netural | soft | strong
                "columns": [
                    {
                        "id": "1",
                        "width": 12,
                        "webparts": [
                            {
                                "@odata.type": "#microsoft.graph.textWebPart",
                                "innerHtml": "<h2>项目概况</h2><p>本季度各项目按计划推进，总体完成率达到 <strong>87%</strong>。</p><ul><li>Alpha 项目：完成核心功能开发</li><li>Beta 项目：进入用户测试阶段</li><li>Gamma 项目：需求评审完成</li></ul>"
                            }
                        ]
                    }
                ]
            },
            {
                "layout": "twoColumns",
                "id": "2",
                "emphasis": "soft",
                "columns": [
                    {
                        "id": "1",
                        "width": 6,
                        "webparts": [
                            {
                                "@odata.type": "#microsoft.graph.textWebPart",
                                "innerHtml": "<h3>🎯 本季度成果</h3><p>完成里程碑 12 个，上线功能 38 项。</p>"
                            }
                        ]
                    },
                    {
                        "id": "2",
                        "width": 6,
                        "webparts": [
                            {
                                "@odata.type": "#microsoft.graph.textWebPart",
                                "innerHtml": "<h3>📅 下季度计划</h3><p>重点推进 Delta 项目，目标完成率 90%+。</p>"
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

resp = requests.post(
    f"{MS_GRAPH}/sites/{SITE_ID}/pages",
    headers=headers,
    json=payload,
    timeout=30
)
resp.raise_for_status()
new_page = resp.json()
print(f"✅ 页面已创建（草稿）：{new_page['webUrl']}")
print(f"   页面 ID：{new_page['id']}")
```

### 3.2 创建新闻帖子（News Post）

```python
news_payload = {
    "@odata.type": "#microsoft.graph.sitePage",
    "title": "重要公告：新版 OA 系统将于下周上线",
    "name": "oa-launch-announcement.aspx",
    "pageLayout": "article",
    "promotionKind": "newsPost",               # ← 关键：设为新闻类型
    "showComments": True,
    "titleArea": {
        "layout": "colorBlock",
        "showAuthor": True,
        "showPublishedDate": True,
        "title": "重要公告：新版 OA 系统将于下周上线"
    },
    "canvasLayout": {
        "horizontalSections": [{
            "layout": "oneColumn",
            "id": "1",
            "columns": [{
                "id": "1",
                "width": 12,
                "webparts": [{
                    "@odata.type": "#microsoft.graph.textWebPart",
                    "innerHtml": """
                        <p>经过三个月的开发和测试，新版 OA 系统将于 <strong>2025年7月7日（周一）</strong> 正式上线。</p>
                        <h3>主要变化</h3>
                        <ul>
                            <li>全新 UI 设计，支持暗色模式</li>
                            <li>移动端体验大幅优化</li>
                            <li>审批流程提速 60%</li>
                        </ul>
                        <h3>培训安排</h3>
                        <p>本周四下午3点在 B座301 进行使用培训，欢迎参加。</p>
                    """
                }]
            }]
        }]
    }
}

resp = requests.post(
    f"{MS_GRAPH}/sites/{SITE_ID}/pages",
    headers=headers,
    json=news_payload,
    timeout=30
)
resp.raise_for_status()
```

---

## 4. 编辑页面内容

```python
# 更新页面标题和内容（PATCH 请求）
page_id = "xxx"
update_payload = {
    "title": "2025年Q3项目进展报告（已更新）",
    "canvasLayout": {
        "horizontalSections": [
            {
                "layout": "oneColumn",
                "id": "1",
                "columns": [{
                    "id": "1",
                    "width": 12,
                    "webparts": [{
                        "@odata.type": "#microsoft.graph.textWebPart",
                        "innerHtml": "<h2>更新说明</h2><p>根据评审意见，数据已更新至 6 月 30 日。</p>"
                    }]
                }]
            }
        ]
    }
}

resp = requests.patch(
    f"{MS_GRAPH}/sites/{SITE_ID}/pages/{page_id}/microsoft.graph.sitePage",
    headers=headers,
    json=update_payload,
    timeout=30
)
resp.raise_for_status()
print("✅ 页面内容已更新（仍为草稿，需重新发布）")
```

---

## 5. 发布页面

```python
# 发布草稿（让页面对所有人可见）
resp = requests.post(
    f"{MS_GRAPH}/sites/{SITE_ID}/pages/{page_id}/microsoft.graph.sitePage/publish",
    headers=headers,
    timeout=30
)
# 成功返回 204 No Content
if resp.status_code == 204:
    print("✅ 页面已发布，现在对站点所有成员可见")
else:
    resp.raise_for_status()
```

---

## 6. 复制页面（从模板创建）

```python
# 复制现有页面作为新页面的基础
resp = requests.post(
    f"{MS_GRAPH}/sites/{SITE_ID}/pages/{template_page_id}/microsoft.graph.sitePage/copy",
    headers=headers,
    json={},  # 空 body 即可
    timeout=30
)
resp.raise_for_status()
copied_page = resp.json()
print(f"✅ 页面已复制：{copied_page['webUrl']}")
# 然后用 PATCH 修改标题和内容
```

---

## 7. 删除页面（需用户确认）

```python
resp = requests.delete(
    f"{MS_GRAPH}/sites/{SITE_ID}/pages/{page_id}",
    headers=headers,
    timeout=30
)
# 成功返回 204
if resp.status_code == 204:
    print("✅ 页面已删除")
```

---

## 8. 辅助函数：构建富文本内容

```python
def make_html_content(sections: list[dict]) -> str:
    """
    将结构化内容转换为页面 innerHtml。
    sections 格式：[{"type": "heading|paragraph|list|table", "content": ...}]
    """
    parts = []
    for sec in sections:
        t = sec.get("type", "paragraph")
        c = sec.get("content", "")
        if t == "heading":
            level = sec.get("level", 2)
            parts.append(f"<h{level}>{c}</h{level}>")
        elif t == "paragraph":
            parts.append(f"<p>{c}</p>")
        elif t == "list":
            items = "".join(f"<li>{item}</li>" for item in c)
            ordered = sec.get("ordered", False)
            tag = "ol" if ordered else "ul"
            parts.append(f"<{tag}>{items}</{tag}>")
        elif t == "table":
            rows = c  # list of lists
            thead = "".join(f"<th>{cell}</th>" for cell in rows[0])
            tbody = "".join(
                "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
                for row in rows[1:]
            )
            parts.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>")
        elif t == "divider":
            parts.append("<hr/>")
    return "\n".join(parts)

# 使用示例
html = make_html_content([
    {"type": "heading", "level": 2, "content": "季度总结"},
    {"type": "paragraph", "content": "本季度共完成 <strong>38</strong> 个功能点。"},
    {"type": "list", "content": ["Alpha 项目按时交付", "Beta 项目延期 2 周", "Gamma 项目提前完成"]},
    {"type": "divider"},
    {"type": "table", "content": [
        ["项目", "状态", "完成率"],
        ["Alpha", "已完成", "100%"],
        ["Beta",  "进行中", "78%"],
    ]}
])
```

---

## 注意事项

1. **页面名称唯一**：`name` 字段（文件名）在站点内必须唯一，重复会返回 409；建议加时间戳后缀
2. **草稿 vs 发布**：创建/编辑后默认为草稿状态，必须单独调用 `/publish` 才对外可见
3. **权限要求**：创建/编辑页面需要 `Sites.ReadWrite.All`，发布需要 `Sites.Manage.All`
4. **中文文件名**：`name` 字段建议使用英文+连字符，避免 URL 编码问题
5. **图片嵌入**：图片需先上传到文档库，再用绝对 URL 引用；不支持 base64 内嵌图
