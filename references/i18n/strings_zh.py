# 界面文本 — 中文（默认）

MS365_STRINGS = {
    "lang":      "zh-CN",
    "lang_name": "简体中文",

    # 登录流程
    "login_title":         "Microsoft 365 一键登录",
    "login_step1":         "1. 打开浏览器，访问：{url}",
    "login_step2":         "2. 输入一次性代码：{code}",
    "login_step3":         "3. 使用你的微软账号登录（个人/企业均可）",
    "login_waiting":       "等待登录完成...",
    "login_success":       "✅ 登录成功！欢迎，{name} ({email})",
    "login_failed":        "❌ 登录失败：{error}",
    "login_mfa_prompt":    "⚠️  需要额外验证（MFA），请再次访问上方链接完成验证",
    "login_required":      "未登录，请先说「帮我登录 Microsoft 365」",
    "login_refresh_fail":  "Token 刷新失败，请重新登录",
    "logout_success":      "✅ 已退出登录，Token 缓存已清除",
    "logout_not_logged_in":"ℹ️  当前未登录",
    "status_logged_in":    "已登录 | {name} | {email}",
    "status_not_logged_in":"未登录",

    # 通用操作
    "op_success":          "✅ 已完成：{summary}",
    "op_failed":           "❌ 操作失败：{error}",
    "op_confirm_delete":   "⚠️  确认删除「{name}」？此操作不可恢复。（回复「确认」继续）",
    "op_confirm_send":     "📤 即将发送给：{to}\n主题：{subject}\n正文预览：{preview}\n\n确认发送？（回复「确认」继续）",
    "op_cancelled":        "已取消",
    "op_uploading":        "正在上传...（{size}）",
    "op_downloading":      "正在下载：{name}",

    # 邮件
    "mail_no_new":         "📭 暂无新邮件",
    "mail_new_count":      "📬 有 {count} 封新邮件",
    "mail_from":           "发件人",
    "mail_subject":        "主题",
    "mail_date":           "时间",
    "mail_preview":        "摘要",
    "mail_unread":         "未读",
    "mail_sent":           "✅ 邮件已发送",
    "mail_attachment":     "附件",

    # 日历
    "cal_no_events":       "📅 今日无日程",
    "cal_event_created":   "✅ 日历事件已创建：{title}",
    "cal_meeting_link":    "Teams 会议链接：{url}",
    "cal_busy":            "忙碌",
    "cal_free":            "空闲",

    # 文件
    "file_uploaded":       "✅ {name} 已上传到 {path}",
    "file_downloaded":     "✅ {name} 已下载（{size}）",
    "file_not_found":      "❌ 文件不存在：{path}",
    "file_share_link":     "🔗 分享链接：{url}（有效期至 {expiry}）",
    "drive_empty":         "文件夹为空",

    # Teams
    "teams_sent":          "✅ 消息已发送至 {target}",
    "teams_enterprise_only": "⚠️  Teams API 需要企业账号，个人 Outlook.com 账号不支持此功能",

    # 任务
    "task_created":        "✅ 任务已创建：{title}（截止 {due}）",
    "task_completed":      "✅ 任务「{title}」已标记完成",
    "task_no_due":         "无截止日期",

    # SharePoint
    "sp_site_not_found":   "❌ 找不到站点：{site}",
    "sp_page_created":     "✅ 页面已创建（草稿）：{url}",
    "sp_page_published":   "✅ 页面已发布，所有人可见：{url}",
    "sp_list_item_created":"✅ 已创建列表项 ID：{id}",
    "sp_no_doc_lib":       "❌ 该站点没有文档库",

    # Power Automate
    "flow_triggered":      "⚡ 已触发流「{name}」，正在处理...",
    "flow_result":         "流执行结果：{result}",
    "flow_url_missing":    "❌ 未配置流的触发 URL，请设置环境变量：{env_var}",

    # 甘特图
    "gantt_exported":      "✅ 甘特图已导出：{path}（{count} 个任务）",
    "gantt_no_due":        "⚠️  {count} 个任务无截止日期，已在甘特图中跳过",
    "gantt_uploaded":      "📤 已上传到 OneDrive：{url}",

    # 规则
    "rule_created":        "✅ 规则已创建：{name}",
    "rule_disabled":       "⏸️  规则已禁用：{name}",
    "rule_deleted":        "✅ 规则已删除：{name}",

    # 错误
    "err_401":             "❌ 认证失败（401），请重新登录",
    "err_403":             "❌ 权限不足（403），请检查账号权限或重新登录授权",
    "err_404":             "❌ 资源不存在（404）：{resource}",
    "err_429":             "⏳ 请求过于频繁（429），{wait} 秒后重试",
    "err_500":             "❌ 微软服务出现问题（{code}），请稍后重试",
    "err_timeout":         "❌ 请求超时，请检查网络连接后重试",
    "err_generic":         "❌ 发生错误：{error}",
}
