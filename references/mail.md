# Outlook 邮件模块（mail.md）

## 常用操作速查

### 读取收件箱（最新10封）
```python
import requests
resp = requests.get(
    f"{MS_GRAPH}/me/messages",
    headers=headers,
    params={"$top": 10, "$orderby": "receivedDateTime desc",
            "$select": "subject,from,receivedDateTime,bodyPreview,isRead"}
)
emails = resp.json().get("value", [])
```

### 搜索邮件
```python
resp = requests.get(
    f"{MS_GRAPH}/me/messages",
    headers=headers,
    params={"$search": f'"{关键词}"', "$top": 5}
)
```

### 发送邮件
```python
payload = {
    "message": {
        "subject": "主题",
        "body": {"contentType": "HTML", "content": "<p>正文</p>"},
        "toRecipients": [{"emailAddress": {"address": "to@example.com"}}],
        "ccRecipients": [],  # 可选
        "attachments": []    # 可选，见下方附件说明
    },
    "saveToSentItems": True
}
resp = requests.post(f"{MS_GRAPH}/me/sendMail", headers=headers, json=payload)
# 成功返回 202，无响应体
```

### 回复邮件
```python
requests.post(
    f"{MS_GRAPH}/me/messages/{message_id}/reply",
    headers=headers,
    json={"message": {}, "comment": "回复内容"}
)
```

### 标记已读 / 未读
```python
requests.patch(
    f"{MS_GRAPH}/me/messages/{message_id}",
    headers=headers,
    json={"isRead": True}
)
```

### 移动到文件夹
```python
requests.post(
    f"{MS_GRAPH}/me/messages/{message_id}/move",
    headers=headers,
    json={"destinationId": "deleteditems"}  # 或 "inbox", "sentitems", 自定义文件夹ID
)
```

### 添加附件（Base64）
```python
import base64
with open("file.pdf", "rb") as f:
    content = base64.b64encode(f.read()).decode()

attachment = {
    "@odata.type": "#microsoft.graph.fileAttachment",
    "name": "file.pdf",
    "contentType": "application/pdf",
    "contentBytes": content
}
# 将 attachment 加入 payload["message"]["attachments"] 列表
```

## 输出格式建议
- 列出邮件时：显示 发件人、主题、时间、摘要（前100字）、是否已读
- 发送前：展示预览（收件人、主题、正文前200字），请用户确认
