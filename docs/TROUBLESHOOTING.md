# 常见问题排查

## 目录

- [登录相关](#登录相关)
- [权限错误（403）](#权限错误403)
- [Token 过期（401）](#token-过期401)
- [Teams 功能不可用](#teams-功能不可用)
- [SharePoint 列表筛选无效](#sharepoint-列表筛选无效)
- [中国区账号无法登录](#中国区账号无法登录)
- [Python 相关错误](#python-相关错误)

---

## 登录相关

### 问题：浏览器打开后提示"该代码已过期"

**原因**：设备码默认有效期约 15 分钟，超时后失效。

**解决**：重新对 OpenClaw 说"帮我登录 Microsoft 365"，获取新的一次性代码。

---

### 问题：登录成功但 OpenClaw 没有反应

**原因**：网络超时或 Python 进程意外退出。

**解决**：

```bash
# 检查登录状态
python scripts/auth.py --action status

# 如显示 NOT_LOGGED_IN，重新登录
python scripts/auth.py --action login
```

---

### 问题：`ModuleNotFoundError: No module named 'msal'`

**解决**：

```bash
pip install msal --break-system-packages
# 或
pip3 install msal
```

---

### 问题：登录后提示"AADSTS50076: 需要多重身份验证"

**原因**：你的企业启用了条件访问策略（MFA）。

**解决**：登录页面会自动跳转到 MFA 验证步骤，完成手机/邮件验证码验证后即可。如果反复出现，联系 IT 管理员确认是否允许 Device Code Flow。

---

### 问题：Token 缓存文件损坏导致每次都要重新登录

**解决**：删除损坏的缓存文件，重新登录。

```bash
rm ~/.openclaw/ms365_token_cache.json
# 然后重新登录
```

---

## 权限错误（403）

### 问题：调用某功能时提示 403 Forbidden

**原因 1**：初次登录时未授予该功能所需的权限。

**解决**：退出登录后重新登录，在授权页面确认接受所有权限。

```bash
python scripts/auth.py --action logout
python scripts/auth.py --action login
```

**原因 2**：企业 IT 管理员未为该应用授予管理员同意。

**解决**：联系 IT 管理员在 Azure Portal 为 App 授予管理员同意，或参考 [企业版指南](ENTERPRISE.md) 使用企业自注册的 App。

---

### 问题：Teams 功能返回 403

**原因**：Teams API 大部分功能仅支持企业（Azure AD）账号，个人 Outlook.com 账号无法使用。

**解决**：确认你使用的是企业 Microsoft 365 账号（邮箱格式通常为 `user@company.com` 而非 `@outlook.com`）。

---

## Token 过期（401）

### 问题：使用一段时间后出现 401 Unauthorized

**原因**：Refresh Token 超过 90 天未使用已失效。

**解决**：

```bash
python scripts/auth.py --action logout
python scripts/auth.py --action login
```

或直接对 OpenClaw 说"帮我重新登录 Microsoft 365"。

---

## Teams 功能不可用

### 问题：无法列出 Teams 聊天或频道

**检查步骤**：

1. 确认使用的是企业（AAD）账号而非个人账号
2. 确认账号有 Microsoft Teams 许可证

```bash
# 验证账号类型
python scripts/auth.py --action status
# 企业账号输出的邮箱不应以 @outlook.com / @hotmail.com 结尾
```

---

## SharePoint 列表筛选无效

### 问题：使用 `$filter=fields/xxx` 筛选列表项报错 400

**原因**：Graph API 不支持同时使用 `$expand=fields` 和 `$filter=fields/...`，这是微软的 API 限制。

**解决**：改用客户端筛选：

```python
# 先获取全部数据
items = get_all_items(site_id, list_id, headers)
# 再在本地筛选
items = [i for i in items if i["fields"].get("Status") == "进行中"]
```

或使用 SharePoint REST API（支持服务端筛选）：

```python
SP_SITE = "https://company.sharepoint.com/sites/your-site"
url = f"{SP_SITE}/_api/lists/getbytitle('列表名')/items"
params = {"$filter": "Status eq '进行中'", "$select": "Title,Status,DueDate"}
headers_sp = {**headers, "Accept": "application/json;odata=verbose"}
resp = requests.get(url, headers=headers_sp, timeout=30)
```

---

## 中国区账号无法登录

### 问题：中国区世纪互联账号登录失败

**原因**：中国区 M365 使用不同的认证端点（`login.chinacloudapi.cn`），且需要企业自注册的 Azure App。

**解决**：参见 [企业版指南 → 中国区配置](ENTERPRISE.md#中国区世纪互联)。

---

## Python 相关错误

### 问题：`ssl.SSLError` 或 `certificate verify failed`

**原因**：Python SSL 证书库不完整（常见于 macOS）。

**解决**：

```bash
# macOS
/Applications/Python\ 3.x/Install\ Certificates.command

# 或安装 certifi
pip install certifi --break-system-packages
```

---

### 问题：`pip install` 提示权限不足

**解决**：

```bash
# 方式 1：加 --user 标志
pip install msal --user

# 方式 2：使用虚拟环境
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install msal
```

---

## 仍未解决？

- 查看 [GitHub Issues](https://github.com/your-username/ms365-gog/issues) 搜索类似问题
- 提交新 Issue 时请附上：
  - 操作系统版本
  - Python 版本（`python3 --version`）
  - 错误的完整信息（截图或粘贴文本）
  - 账号类型（个人 / 企业，是否中国区）
