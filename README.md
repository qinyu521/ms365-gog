# ms365-gog · Microsoft 365 全家桶集成 Skill

> 让 OpenClaw 拥有与 Google Workspace 集成（gog）同等体验的 **Microsoft 365 原生操作能力**，无需配置 Azure 开发者账号，一行命令登录即用。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://github.com/qinyu521/ms365-gog)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🗺️ 功能一览

| 模块 | 功能 | 个人账号 | 企业账号 |
|------|------|:-------:|:-------:|
| **Outlook 邮件** | 收件箱读取、搜索、发送、回复、附件、标记已读 | ✅ | ✅ |
| **Outlook 日历** | 事件查看/创建/修改、Teams 会议链接生成、空闲查询 | ✅ | ✅ |
| **OneDrive 文件** | 浏览、上传（含大文件分块）、下载、分享链接 | ✅ | ✅ |
| **Teams 消息** | 聊天/频道消息发送、自适应卡片、回复 Thread | ⚠️ 部分 | ✅ |
| **Word / Excel** | 读取、编辑回传（python-docx / openpyxl）、在线协作链接 | ✅ | ✅ |
| **Microsoft To Do** | 任务列表、创建/完成/子任务 | ✅ | ✅ |
| **Planner** | 看板列表、创建任务、进度更新 | ❌ | ✅ |
| **SharePoint** | 站点浏览、文档库读写、List CRUD、全文搜索、权限管理 | ❌ | ✅ |
| **Webhook / 实时通知** | 长轮询、Graph Webhook、Delta Query 增量同步 | ✅ | ✅ |
| **企业版扩展** | 多账号切换、共享邮箱、SSO、审计日志、批量 API | ❌ | ✅ |
| **中国区世纪互联** | 端点自动切换（需企业自注册 Azure App） | ❌ | ✅ |

---

## ⚡ 快速开始

### 前置要求

- [OpenClaw](https://openclaw.ai) 已安装（桌面版或命令行版均可）
- Python 3.9 或以上（用于 OAuth 登录脚本）
- 有效的 Microsoft 账号（个人 Outlook.com 或企业 Microsoft 365）

### 安装 Skill

**方式一：下载 .skill 文件安装（推荐）**

1. 前往 [Releases 页面](https://github.com/qinyu521/ms365-gog/releases/latest)
2. 下载 `ms365-gog.skill`
3. 打开 OpenClaw → 设置 → Skills → 安装本地 Skill → 选择下载的文件

**方式二：从源码安装**

```bash
git clone https://github.com/qinyu521/ms365-gog.git
cd ms365-gog

# 打包为 .skill 文件
python scripts/package.py

# 输出：dist/ms365-gog.skill
# 然后在 OpenClaw 中安装该文件
```

### 登录 Microsoft 365

安装 Skill 后，在 OpenClaw 中输入：

```
帮我登录 Microsoft 365
```

OpenClaw 会自动调用本 Skill，引导你完成登录：

```
🔑 Microsoft 365 一键登录
══════════════════════════════════════════════════
1. 打开浏览器，访问：https://microsoft.com/devicelogin
2. 输入一次性代码：ABCD-1234
3. 使用你的微软账号登录（个人/企业均可）
══════════════════════════════════════════════════
等待登录完成...

✅ 登录成功！欢迎，张三 (zhangsan@company.com)
```

登录完成后即可直接使用所有功能，**Token 自动刷新，90 天内无需重新登录**。

---

## 💬 使用示例

登录后，直接用自然语言和 OpenClaw 对话：

```
📧 邮件
"帮我看看今天有没有新邮件"
"把上一封邮件转发给李四，并附上一句简短说明"
"搜索包含'合同'的邮件，最近一个月的"

📅 日历
"明天下午3点和产品团队创建一个项目评审会，在线会议"
"查一下本周五我有哪些日程"
"帮我看看张三明天上午有没有空"

📁 文件
"列出我 OneDrive 根目录下的文件"
"把刚才的报告上传到 OneDrive 的 2025年/Q2 文件夹"
"生成这个文件的共享链接，有效期到年底"

💬 Teams
"在 #产品讨论 频道发消息：本周五 3 点项目评审，请准备材料"
"给王五发一条私信，问他合同审批进度"

📋 任务
"创建一个高优先级任务：准备Q3汇报，截止日期6月30日"
"把'设计稿评审'标记为已完成"

📂 SharePoint
"浏览一下 project-alpha 站点的文档库"
"把这份 Excel 数据批量导入到项目跟踪列表"
"查看合同文件夹的权限设置"
```

---

## 📁 项目结构

```
ms365-gog/
├── SKILL.md                    # Skill 主入口（触发规则 + 功能路由）
├── scripts/
│   └── auth.py                 # OAuth 2.0 Device Code Flow 认证模块
├── references/
│   ├── mail.md                 # Outlook 邮件 API
│   ├── calendar.md             # 日历 / Teams 会议
│   ├── onedrive.md             # OneDrive 文件读写
│   ├── teams.md                # Teams 消息 / 频道
│   ├── office-docs.md          # Word / Excel 编辑
│   ├── tasks.md                # Microsoft To Do / Planner
│   ├── webhook.md              # Webhook / 长轮询 / Delta Query
│   ├── enterprise.md           # 企业版：多账号、SSO、审计
│   ├── sharepoint.md           # SharePoint 站点、列表、文档库
│   └── china-cloud.md          # 中国区世纪互联适配
├── docs/
│   ├── INSTALL.md              # 详细安装指南
│   ├── ENTERPRISE.md           # 企业版配置指南
│   └── TROUBLESHOOTING.md      # 常见问题排查
├── scripts/
│   └── package.py              # 打包为 .skill 文件
├── LICENSE                     # MIT License
├── CONTRIBUTING.md             # 贡献指南
└── README.md                   # 本文档
```

---

## 🔐 安全说明

- **不采集任何数据**：所有 API 调用直接从你的设备发往微软服务器，本 Skill 不经过任何中间服务器
- **Token 本地存储**：登录凭证保存在 `~/.openclaw/ms365_token_cache.json`，权限 600（仅你本人可读写）
- **最小权限原则**：仅申请功能所需的 OAuth Scope，不申请管理员权限
- **公共客户端 ID**：使用 Microsoft Graph Explorer 的公共 Client ID（无密钥），企业用户建议自行注册 Azure App 替换（见 [企业版指南](docs/ENTERPRISE.md)）

---

## 🏢 企业版配置

企业用户通常需要：

- **自注册 Azure App**：避免依赖第三方公共 Client ID，获得更稳定的限流配额
- **Azure AD SSO**：与企业身份体系对接，支持条件访问（MFA）
- **多账号切换**：同时管理主账号 + 共享邮箱
- **中国区世纪互联**：需要不同的端点和自注册 App

详见 → [企业版配置指南](docs/ENTERPRISE.md)

---

## 🌍 语言支持

界面提示和错误信息目前为中文。欢迎提交 PR 添加其他语言支持。

---

## 🤝 贡献

欢迎任何形式的贡献！

- 🐛 [报告 Bug](https://github.com/qinyu521/ms365-gog/issues/new?template=bug_report.md)
- 💡 [提交新功能建议](https://github.com/qinyu521/ms365-gog/issues/new?template=feature_request.md)
- 📖 [改善文档](https://github.com/qinyu521/ms365-gog/pulls)
- 🌐 [添加语言翻译](docs/CONTRIBUTING.md#翻译)

请先阅读 [贡献指南](CONTRIBUTING.md)。

---

## 📋 路线图

- [ ] SharePoint 页面（Page）创建和编辑
- [ ] Outlook 规则（Rules）管理
- [ ] Power Automate 触发器集成
- [ ] 多语言界面（English / 日本語）
- [ ] GUI 登录助手（替代命令行）
- [ ] Planner 甘特图视图导出

---

## 📄 License

[MIT License](LICENSE) © 2025 ms365-gog contributors

## 免责声明

本项目为开源社区项目，**与 Microsoft Corporation 无关联、无赞助、无认可**。

Microsoft 365®、Outlook®、Teams®、OneDrive®、SharePoint®、Microsoft Graph® 均为 [Microsoft Corporation](https://www.microsoft.com) 在美国及其他国家的注册商标或商标。

使用本工具需遵守 [Microsoft 服务协议](https://www.microsoft.com/servicesagreement) 和 [Microsoft Graph API 使用条款](https://learn.microsoft.com/en-us/legal/microsoft-apis/terms-of-use)。
