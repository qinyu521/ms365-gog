# 贡献指南

首先，感谢你考虑为 ms365-gog 做贡献！🎉

无论是修复一个错别字、报告一个 Bug、还是新增一个 API 模块，每一份贡献都很有价值。

## 目录

- [报告 Bug](#报告-bug)
- [提交新功能建议](#提交新功能建议)
- [提交代码（Pull Request）](#提交代码pull-request)
- [添加新的 API 模块](#添加新的-api-模块)
- [改进文档](#改进文档)
- [添加语言翻译](#添加语言翻译)
- [行为准则](#行为准则)

---

## 报告 Bug

**在提交 Issue 前，请先**：

1. 查看 [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) 确认是否有已知解决方案
2. 搜索现有 [Issues](https://github.com/your-username/ms365-gog/issues) 避免重复

**提交 Bug 报告时请包含**：

- 操作系统和版本
- Python 版本（`python3 --version`）
- 账号类型（个人 Outlook.com / 企业 AAD / 中国区）
- 完整的错误信息（截图或文本）
- 复现步骤

---

## 提交新功能建议

欢迎提交功能建议！请在 Issue 中说明：

- **使用场景**：你想解决什么问题？
- **期望行为**：你希望如何与 OpenClaw 对话来触发这个功能？
- **对应的 Microsoft Graph API**（如果你知道的话）

---

## 提交代码（Pull Request）

### 开发环境搭建

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/YOUR-USERNAME/ms365-gog.git
cd ms365-gog

# 2. 安装开发依赖
pip install msal requests --break-system-packages

# 3. 创建功能分支
git checkout -b feature/your-feature-name
```

### 提交规范

提交信息请遵循以下格式：

```
<类型>: <简短描述>

<详细说明（可选）>
```

类型：
- `fix` — 修复 Bug
- `feat` — 新功能
- `docs` — 文档改进
- `refactor` — 代码重构（不改变行为）
- `chore` — 构建脚本、依赖更新等

示例：
```
fix: 修复长轮询中 token 过期导致 401 的问题

长轮询循环中每次迭代都应重新获取 token，
原代码只在初始化时获取一次，60 分钟后会过期。
```

### Pull Request 流程

1. 确保你的改动有对应的 Issue（大的改动建议先开 Issue 讨论）
2. 更新相关文档（`SKILL.md`、`references/`、`docs/`）
3. 在 PR 描述中说明改动内容和测试方式
4. 等待 review，根据反馈进行修改

---

## 添加新的 API 模块

如果你想新增一个 Microsoft Graph API 的功能模块（比如 OneNote、Viva、Power Automate），请：

### 1. 创建参考文档

在 `references/` 目录下创建新文件，例如 `references/onenote.md`。

参考文档结构：

```markdown
# OneNote 模块（onenote.md）

> 功能描述。
> 触发词：OneNote、笔记、记录想法

---

## 常用操作速查

### 列出笔记本
...（代码示例）

## 注意事项
...
```

### 2. 更新主 SKILL.md 路由

在 `SKILL.md` 的功能路由表中添加新模块：

```markdown
| OneNote、笔记、记录 | `references/onenote.md` |
```

### 代码示例规范

- 每个示例必须是**完整可运行**的代码片段
- 包含 `timeout=30` 参数
- 包含 `raise_for_status()` 调用
- 用中文注释说明关键步骤和陷阱
- 对破坏性操作（删除、发送）标注"需用户确认"

---

## 改进文档

文档贡献同样非常欢迎！

- **错别字、语句不通**：直接提 PR，无需开 Issue
- **示例不够清晰**：提 PR 附上改进版本
- **缺少某个场景的说明**：提 Issue 说明后再 PR

文档文件位置：
- `README.md` — 项目主页
- `docs/INSTALL.md` — 安装指南
- `docs/ENTERPRISE.md` — 企业版指南
- `docs/TROUBLESHOOTING.md` — 问题排查
- `references/*.md` — 各 API 模块参考

---

## 添加语言翻译

目前文档为中文，欢迎添加其他语言版本。

翻译文件放在 `docs/i18n/<语言代码>/` 目录下，例如：

```
docs/i18n/en/README.md
docs/i18n/ja/README.md
```

翻译时请保持代码示例不变，仅翻译注释和说明文字。

---

## 行为准则

参与本项目即代表你同意以开放、友好的态度与他人交流：

- 尊重不同经验水平的贡献者
- 接受建设性的批评和建议
- 关注问题本身，而非攻击个人

---

再次感谢你的贡献！如有任何疑问，欢迎在 Issues 中提问。
