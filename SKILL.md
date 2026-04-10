---
name: ms365-gog
description: >
  Microsoft 365 全家桶集成 Skill，为 OpenClaw 提供与 Google Workspace 集成（gog）同等体验的 M365 能力。
  覆盖：一键 OAuth 登录、Outlook 邮件/日历/任务、OneDrive 文件读写、Teams 消息、Word/Excel 在线文档编辑。
  当用户提到以下任何场景时必须触发本 Skill：
  - "帮我发邮件/看邮件/回邮件"（Outlook）
  - "查日历/加会议/Teams 会议"
  - "OneDrive 上传/下载/读取文件"
  - "发 Teams 消息/通知"
  - "读 Word/Excel 文档"、"编辑 Office 文档"
  - "连接 Microsoft 365"、"登录微软账号"、"M365 集成"
  即使用户未明确说"ms365-gog"，只要涉及微软办公生态，都应优先查阅本 Skill。
compatibility:
  required_tools:
    - bash
  optional_tools:
    - web_fetch
  python_packages:
    - msal>=1.28.0          # Microsoft Authentication Library
    - msgraph-sdk>=1.4.0    # Microsoft Graph SDK
    - O365>=2.0.35          # 简化封装层（备用）
---

# Microsoft 365 全家桶集成 Skill（ms365-gog）

## 概览

本 Skill 让 OpenClaw 用户**无需手动配置 Azure 开发者账号**，即可通过标准 OAuth 2.0 Device Code Flow 登录 Microsoft 365，并操作 Outlook、OneDrive、Teams、Word/Excel 等服务。

```
用户意图
  └─► [身份验证] OAuth 设备码流 → Token 缓存
        ├─► [邮件]     Outlook Mail API      → references/mail.md
        ├─► [日历]     Outlook Calendar API  → references/calendar.md
        ├─► [文件]     OneDrive Files API    → references/onedrive.md
        ├─► [消息]     Teams Chat/Channel    → references/teams.md
        └─► [文档]     Word / Excel          → references/office-docs.md
```

---

## 第一步：身份验证（所有功能的前置条件）

> **每次执行 M365 操作前，先检查 Token 是否有效，再调用相应模块。**

### 1.1 安装依赖

```bash
pip install msal msgraph-sdk --break-system-packages -q
```

### 1.2 Token 管理脚本

在工作目录运行 `scripts/auth.py`，它会：
1. 使用公共客户端 Device Code Flow（用户只需在浏览器输入一次性代码）
2. 将 Token 缓存到 `~/.openclaw/ms365_token_cache.json`
3. 自动刷新（access token 60 min，refresh token 90 天）

```bash
python scripts/auth.py --action login   # 首次登录
python scripts/auth.py --action status  # 检查登录状态
python scripts/auth.py --action logout  # 清除 Token
```

**重要**：若 `status` 返回 `NOT_LOGGED_IN`，必须先执行 `login` 再继续。

### 1.3 获取 Access Token（代码片段）

```python
from scripts.auth import get_access_token
token = get_access_token()  # 自动刷新；未登录则抛出 AuthRequiredError
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
MS_GRAPH = "https://graph.microsoft.com/v1.0"
```

### 1.4 权限范围（Scopes）

本 Skill 申请最小必要权限：

| 功能        | Scope                                          |
|-----------|------------------------------------------------|
| 邮件读写    | `Mail.ReadWrite`, `Mail.Send`                  |
| 日历       | `Calendars.ReadWrite`                          |
| OneDrive  | `Files.ReadWrite.All`                          |
| Teams     | `Chat.ReadWrite`, `ChannelMessage.Send`        |
| Office 文档 | `Files.ReadWrite.All`（通过 OneDrive 接口访问） |
| 用户信息    | `User.Read` (默认)                             |

---

## 第二步：选择功能模块

根据用户意图，读取对应的参考文档：

| 用户需求关键词                              | 参考文档                               |
|----------------------------------------|------------------------------------|
| 邮件、Outlook、发邮件、收件箱、回复邮件       | `references/mail.md`               |
| 邮件规则、收件箱规则、自动分类、自动转发        | `references/mail-rules.md`         |
| 日历、会议、约时间、提醒、Teams会议链接        | `references/calendar.md`           |
| 文件、OneDrive、上传、下载、共享、云盘         | `references/onedrive.md`           |
| Teams、消息、频道、群组通知、卡片            | `references/teams.md`              |
| Word、Excel、文档编辑、表格、工作表          | `references/office-docs.md`        |
| 任务、待办、To Do、Planner、看板、deadline  | `references/tasks.md`              |
| 甘特图、Gantt、进度图、时间线、任务时间轴       | `references/planner-gantt.md`      |
| 实时通知、监听、订阅、新邮件提醒、自动触发      | `references/webhook.md`            |
| 多账号、共享邮箱、SSO、企业版、审计、批量API   | `references/enterprise.md`         |
| 世纪互联、中国区、chinacloudapi、.cn账号    | `references/china-cloud.md`        |
| SharePoint、站点、文档库、SP列表、团队网站    | `references/sharepoint.md`         |
| SharePoint页面、新闻、公告、Intranet、Wiki  | `references/sharepoint-pages.md`   |
| Power Automate、Flow、触发流、审批流、工作流  | `references/power-automate.md`     |

> **多模块请求**（如"发邮件+建日历+通知Teams"）按顺序读取多个参考文档，依次执行。

---

## 复合场景示例（常见企业工作流）

### 场景 A：晨间工作汇总
> "帮我总结今天的邮件、日程和待办"
→ 并行读取 `mail.md` + `calendar.md` + `tasks.md`，汇总展示

### 场景 B：发送会议通知
> "给项目组发周五下午3点评审会的邀请，并在Teams通知大家"
→ `calendar.md`（创建事件+生成Teams链接）→ `teams.md`（发频道消息附链接）

### 场景C：文件协作
> "把这份Excel上传到OneDrive，生成共享链接发给张三"
→ `office-docs.md`（本地处理）→ `onedrive.md`（上传+生成链接）→ `mail.md`（发邮件）

### 场景 D：任务自动化
> "监控收件箱，一旦收到含'合同'的邮件就创建任务提醒我处理"
→ `webhook.md`（监听邮件）→ `tasks.md`（创建To Do任务）

### 场景 E：邮件附件自动归档
> "把收到的合同附件自动存到SharePoint文档库，并更新列表记录"
→ `mail.md`（读附件）→ `sharepoint.md`（上传文档库 + 写列表项）

---

## 第三步：错误处理规范

| HTTP 状态码 | 含义         | 处理方式                                |
|-----------|------------|-------------------------------------|
| 401        | Token 过期   | 调用 `get_access_token(force_refresh=True)` 后重试 |
| 403        | 权限不足      | 提示用户重新登录（`auth.py --action login`）并说明缺少的 Scope |
| 429        | 速率限制      | 读取 `Retry-After` 响应头，等待后重试（最多3次） |
| 404        | 资源不存在    | 告知用户资源不存在，提供备选操作                  |
| 5xx        | 微软服务故障   | 等待5秒后重试1次，若仍失败则报告并建议稍后再试          |

---

## 输出格式规范

- **操作成功**：用一句中文确认"✅ 已完成：[操作摘要]"，再附上关键返回数据（邮件ID、文件链接等）
- **需要用户确认**：发送/删除等破坏性操作前，先展示预览并询问确认
- **操作失败**：明确告知失败原因 + 下一步建议，不要只抛出原始错误码

---

## 快速参考：Graph API 基础端点

```
用户信息:     GET  /me
邮件列表:     GET  /me/messages
发送邮件:     POST /me/sendMail
日历事件:     GET  /me/calendar/events
OneDrive根:  GET  /me/drive/root/children
Teams聊天:   GET  /me/chats
```

完整 API 细节见各 `references/` 文件。

---

## 变现提示（面向 Skill 开发者）

| 版本         | 价格       | 核心限制/功能                                        |
|------------|----------|--------------------------------------------------|
| 个人版       | ¥49-99/月  | 单账号、OneDrive 文件 ≤ 100MB、无审计日志               |
| 企业版       | ¥299/月    | 多账号切换、共享邮箱、审计日志、Azure AD SSO、批量 API      |
| 企业版+中国区 | ¥399/月    | 世纪互联适配 + 以上全部功能                              |

**企业版差异化功能**：读取 `references/enterprise.md`
**中国区适配**：读取 `references/china-cloud.md`

---

## 注意事项

1. **Token 安全**：缓存文件 `~/.openclaw/ms365_token_cache.json` 权限应为 `600`，脚本会自动设置
2. **共享设备**：企业环境建议启用加密存储，参见 `references/enterprise.md`
3. **中国区 M365**：端点不同，需设置 `--cloud china`，参见 `references/china-cloud.md`（如有需要可扩展）
4. **个人账号 vs 企业账号**：部分 Teams API 仅支持企业（AAD）账号，个人 MSA 账号调用时会返回 403
