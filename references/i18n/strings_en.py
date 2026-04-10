# Interface strings — English

MS365_STRINGS = {
    "lang":      "en-US",
    "lang_name": "English",

    # Auth
    "login_title":         "Microsoft 365 Sign-In",
    "login_step1":         "1. Open your browser and visit: {url}",
    "login_step2":         "2. Enter the one-time code: {code}",
    "login_step3":         "3. Sign in with your Microsoft account (personal or work)",
    "login_waiting":       "Waiting for sign-in...",
    "login_success":       "✅ Signed in successfully! Welcome, {name} ({email})",
    "login_failed":        "❌ Sign-in failed: {error}",
    "login_mfa_prompt":    "⚠️  Additional verification required (MFA). Please visit the link above again.",
    "login_required":      "Not signed in. Please say 'Sign me in to Microsoft 365' first.",
    "login_refresh_fail":  "Token refresh failed. Please sign in again.",
    "logout_success":      "✅ Signed out. Token cache cleared.",
    "logout_not_logged_in":"ℹ️  Not currently signed in.",
    "status_logged_in":    "Signed in | {name} | {email}",
    "status_not_logged_in":"Not signed in",

    # General
    "op_success":          "✅ Done: {summary}",
    "op_failed":           "❌ Operation failed: {error}",
    "op_confirm_delete":   "⚠️  Confirm delete '{name}'? This cannot be undone. (Reply 'confirm' to proceed)",
    "op_confirm_send":     "📤 Sending to: {to}\nSubject: {subject}\nPreview: {preview}\n\nConfirm send? (Reply 'confirm')",
    "op_cancelled":        "Cancelled.",
    "op_uploading":        "Uploading... ({size})",
    "op_downloading":      "Downloading: {name}",

    # Mail
    "mail_no_new":         "📭 No new emails.",
    "mail_new_count":      "📬 {count} new email(s)",
    "mail_from":           "From",
    "mail_subject":        "Subject",
    "mail_date":           "Date",
    "mail_preview":        "Preview",
    "mail_unread":         "Unread",
    "mail_sent":           "✅ Email sent.",
    "mail_attachment":     "Attachment",

    # Calendar
    "cal_no_events":       "📅 No events today.",
    "cal_event_created":   "✅ Calendar event created: {title}",
    "cal_meeting_link":    "Teams meeting link: {url}",
    "cal_busy":            "Busy",
    "cal_free":            "Free",

    # Files
    "file_uploaded":       "✅ {name} uploaded to {path}",
    "file_downloaded":     "✅ {name} downloaded ({size})",
    "file_not_found":      "❌ File not found: {path}",
    "file_share_link":     "🔗 Share link: {url} (expires {expiry})",
    "drive_empty":         "This folder is empty.",

    # Teams
    "teams_sent":          "✅ Message sent to {target}",
    "teams_enterprise_only": "⚠️  Teams API requires a work account. Personal Outlook.com accounts are not supported.",

    # Tasks
    "task_created":        "✅ Task created: {title} (due {due})",
    "task_completed":      "✅ Task '{title}' marked as complete.",
    "task_no_due":         "No due date",

    # SharePoint
    "sp_site_not_found":   "❌ Site not found: {site}",
    "sp_page_created":     "✅ Page created (draft): {url}",
    "sp_page_published":   "✅ Page published and visible to all: {url}",
    "sp_list_item_created":"✅ List item created. ID: {id}",
    "sp_no_doc_lib":       "❌ This site has no document library.",

    # Power Automate
    "flow_triggered":      "⚡ Flow '{name}' triggered. Processing...",
    "flow_result":         "Flow result: {result}",
    "flow_url_missing":    "❌ Flow trigger URL not configured. Please set environment variable: {env_var}",

    # Gantt
    "gantt_exported":      "✅ Gantt chart exported: {path} ({count} tasks)",
    "gantt_no_due":        "⚠️  {count} task(s) have no due date and were skipped.",
    "gantt_uploaded":      "📤 Uploaded to OneDrive: {url}",

    # Rules
    "rule_created":        "✅ Rule created: {name}",
    "rule_disabled":       "⏸️  Rule disabled: {name}",
    "rule_deleted":        "✅ Rule deleted: {name}",

    # Errors
    "err_401":             "❌ Authentication error (401). Please sign in again.",
    "err_403":             "❌ Permission denied (403). Check your account permissions or re-authorize.",
    "err_404":             "❌ Resource not found (404): {resource}",
    "err_429":             "⏳ Rate limited (429). Retrying in {wait} seconds...",
    "err_500":             "❌ Microsoft service error ({code}). Please try again later.",
    "err_timeout":         "❌ Request timed out. Check your network connection.",
    "err_generic":         "❌ Error: {error}",
}
