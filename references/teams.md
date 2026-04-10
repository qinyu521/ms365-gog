# Teams 消息模块（teams.md）

> ⚠️ Teams API 大部分功能仅支持企业（AAD）账号，个人 MSA 账号调用会返回 403。

## 常用操作速查

### 列出我的聊天会话
```python
resp = requests.get(f"{MS_GRAPH}/me/chats", headers=headers,
                    params={"$expand": "members", "$top": 20})
chats = resp.json().get("value", [])
# chat["chatType"]: "oneOnOne" | "group" | "meeting"
```

### 发送个人聊天消息
```python
# 先找到 chatId（可从 chats 列表或用户的 userId 构造）
requests.post(
    f"{MS_GRAPH}/me/chats/{chat_id}/messages",
    headers=headers,
    json={
        "body": {
            "contentType": "html",  # 或 "text"
            "content": "<b>重要通知</b>：会议改为线上，请点击链接加入。"
        }
    }
)
```

### 列出 Teams 频道列表
```python
# 先获取用户所在的团队
teams_resp = requests.get(f"{MS_GRAPH}/me/joinedTeams", headers=headers)
teams = teams_resp.json().get("value", [])

# 获取某团队的频道
channels_resp = requests.get(
    f"{MS_GRAPH}/teams/{team_id}/channels", headers=headers
)
```

### 发送频道消息
```python
requests.post(
    f"{MS_GRAPH}/teams/{team_id}/channels/{channel_id}/messages",
    headers=headers,
    json={
        "body": {
            "contentType": "html",
            "content": "<p>@团队 本周五下午3点项目评审，请准备演示材料。</p>"
        },
        "importance": "high"  # "normal" | "high" | "urgent"
    }
)
```

### 回复频道消息（Thread）
```python
requests.post(
    f"{MS_GRAPH}/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies",
    headers=headers,
    json={"body": {"contentType": "text", "content": "收到，准时参加！"}}
)
```

### 发送自适应卡片（富媒体通知）
```python
card_payload = {
    "body": {
        "contentType": "html",
        "content": "<attachment id=\"card1\"></attachment>"
    },
    "attachments": [{
        "id": "card1",
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": json.dumps({
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {"type": "TextBlock", "text": "📢 通知标题", "weight": "Bolder", "size": "Medium"},
                {"type": "TextBlock", "text": "通知正文内容", "wrap": True}
            ],
            "actions": [
                {"type": "Action.OpenUrl", "title": "查看详情", "url": "https://example.com"}
            ]
        })
    }]
}
```

## 输出格式建议
- 发送前展示预览：💬 发送到：[会话名称] | 内容摘要
- 成功后：✅ 消息已发送至 [频道/聊天名称]
