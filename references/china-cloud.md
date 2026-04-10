# 中国区 Microsoft 365 适配（china-cloud.md）

> 中国区 M365 由**世纪互联**运营，与全球版完全隔离，端点、认证地址、数据均不同。
> 使用 `--cloud china` 参数时读取本文档。

---

## 关键差异对照表

| 项目              | 全球版                                       | 中国区（世纪互联）                              |
|-----------------|---------------------------------------------|----------------------------------------------|
| 登录端点          | `login.microsoftonline.com`                 | `login.chinacloudapi.cn`                     |
| Graph API        | `graph.microsoft.com`                       | `microsoftgraph.chinacloudapi.cn`            |
| 账号格式          | `user@company.com`                          | `user@company.partner.onmschina.cn`          |
| 公共客户端 ID     | 全球 Graph Explorer ID                       | 需企业自行在中国区 Azure 注册应用              |
| Teams 可用性      | 全球 Teams                                  | Teams（世纪互联版）功能有删减                  |
| SharePoint       | `tenant.sharepoint.com`                     | `tenant.sharepoint.cn`                       |

---

## 配置修改

### auth.py 中国区配置

```python
# 检测到 --cloud china 时使用以下常量
CHINA_AUTHORITY   = "https://login.chinacloudapi.cn/common"
CHINA_GRAPH_URL   = "https://microsoftgraph.chinacloudapi.cn/v1.0"
CHINA_SCOPES      = [
    "https://microsoftgraph.chinacloudapi.cn/User.Read",
    "https://microsoftgraph.chinacloudapi.cn/Mail.ReadWrite",
    "https://microsoftgraph.chinacloudapi.cn/Mail.Send",
    "https://microsoftgraph.chinacloudapi.cn/Calendars.ReadWrite",
    "https://microsoftgraph.chinacloudapi.cn/Files.ReadWrite.All",
    "offline_access",
]

# ⚠️ 中国区必须使用企业自注册的 App（无公共客户端可用）
CHINA_CLIENT_ID = os.environ.get("MS365_CHINA_CLIENT_ID", "")
if not CHINA_CLIENT_ID:
    raise ValueError(
        "中国区需要企业自己的 Azure 应用 Client ID。\n"
        "请设置环境变量：export MS365_CHINA_CLIENT_ID=your-client-id\n"
        "或联系 IT 管理员在 Azure 中国区门户注册应用。"
    )
```

### 完整中国区 auth 初始化

```python
import msal

app = msal.PublicClientApplication(
    client_id=CHINA_CLIENT_ID,
    authority=CHINA_AUTHORITY,
    token_cache=cache,
)

# 启动设备码流
flow = app.initiate_device_flow(scopes=CHINA_SCOPES)
print(f"请访问: {flow['verification_uri']}")
print(f"输入代码: {flow['user_code']}")
result = app.acquire_token_by_device_flow(flow)
```

### 所有 API 请求替换端点

```python
# 将全局变量 MS_GRAPH 替换为：
MS_GRAPH = "https://microsoftgraph.chinacloudapi.cn/v1.0"
# 其余 API 调用代码完全相同，无需修改
```

---

## 企业 IT 操作步骤（中国区 Azure 注册应用）

```
1. 登录 Azure 中国区门户：https://portal.azure.cn
2. Azure Active Directory → 应用注册 → 新建注册
3. 支持的账户类型：选"任何组织目录中的账户"
4. 重定向 URI：http://localhost（Device Code Flow）
5. 记录"应用程序（客户端）ID"和"目录（租户）ID"
6. API 权限 → 添加 Microsoft Graph（世纪互联版）权限
7. 授予管理员同意
```

---

## 中国区已知限制

| 功能                     | 状态                              |
|------------------------|----------------------------------|
| Teams 消息 API           | ✅ 支持（部分功能滞后全球版 3-6 个月） |
| Outlook 邮件/日历         | ✅ 完整支持                        |
| OneDrive                | ✅ 完整支持                        |
| SharePoint              | ✅ 完整支持                        |
| 自适应卡片（Teams）        | ⚠️ 版本落后，部分属性不支持          |
| Viva / Loop             | ❌ 中国区暂不可用                   |
| Copilot for M365        | ⚠️ 2024年起逐步开放，功能受限        |

---

## 快速验证连接

```bash
# 设置环境变量后执行
export MS365_CHINA_CLIENT_ID="你的Client ID"
python scripts/auth.py --action login --cloud china
python scripts/auth.py --action status --cloud china
```

成功登录后，状态输出示例：
```
LOGGED_IN | 张三 | zhangsan@company.partner.onmschina.cn | [中国区]
```
