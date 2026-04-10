# Outlook 日历模块（calendar.md）

## 常用操作速查

### 查看即将到来的事件
```python
from datetime import datetime, timezone, timedelta
now = datetime.now(timezone.utc).isoformat()
end = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

resp = requests.get(
    f"{MS_GRAPH}/me/calendarView",
    headers=headers,
    params={
        "startDateTime": now,
        "endDateTime": end,
        "$orderby": "start/dateTime",
        "$select": "subject,start,end,location,organizer,isOnlineMeeting,onlineMeetingUrl"
    }
)
events = resp.json().get("value", [])
```

### 创建日历事件
```python
payload = {
    "subject": "会议主题",
    "start": {"dateTime": "2025-06-01T10:00:00", "timeZone": "Asia/Shanghai"},
    "end":   {"dateTime": "2025-06-01T11:00:00", "timeZone": "Asia/Shanghai"},
    "location": {"displayName": "线上 / 北京办公室"},
    "attendees": [
        {
            "emailAddress": {"address": "colleague@example.com", "name": "同事"},
            "type": "required"
        }
    ],
    "isOnlineMeeting": True,  # 自动生成 Teams 会议链接
    "onlineMeetingProvider": "teamsForBusiness",
    "body": {"contentType": "HTML", "content": "<p>会议议程</p>"},
    "reminderMinutesBeforeStart": 15
}
resp = requests.post(f"{MS_GRAPH}/me/events", headers=headers, json=payload)
event = resp.json()
print(event.get("onlineMeeting", {}).get("joinUrl"))  # Teams 会议链接
```

### 更新事件
```python
requests.patch(f"{MS_GRAPH}/me/events/{event_id}", headers=headers, json={"subject": "新主题"})
```

### 删除事件（需用户确认后执行）
```python
requests.delete(f"{MS_GRAPH}/me/events/{event_id}", headers=headers)
```

### 查看空闲/忙碌时间
```python
payload = {
    "schedules": ["user@example.com"],
    "startTime": {"dateTime": "2025-06-01T08:00:00", "timeZone": "Asia/Shanghai"},
    "endTime":   {"dateTime": "2025-06-01T18:00:00", "timeZone": "Asia/Shanghai"},
    "availabilityViewInterval": 30  # 分钟粒度
}
resp = requests.post(f"{MS_GRAPH}/me/calendar/getSchedule", headers=headers, json=payload)
```

## 输出格式建议
- 展示事件：📅 日期时间 | 主题 | 地点 | 参与人数
- 在线会议：附上 Teams 加入链接
- 时区：始终显示本地时间（Asia/Shanghai）
