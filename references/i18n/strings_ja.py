# インターフェーステキスト — 日本語

MS365_STRINGS = {
    "lang":      "ja-JP",
    "lang_name": "日本語",

    # 認証
    "login_title":         "Microsoft 365 ワンクリックサインイン",
    "login_step1":         "1. ブラウザで次のURLを開いてください：{url}",
    "login_step2":         "2. ワンタイムコードを入力してください：{code}",
    "login_step3":         "3. Microsoftアカウントでサインイン（個人・法人どちらも可）",
    "login_waiting":       "サインイン完了を待っています...",
    "login_success":       "✅ サインイン成功！ようこそ、{name}（{email}）",
    "login_failed":        "❌ サインイン失敗：{error}",
    "login_mfa_prompt":    "⚠️  追加認証（MFA）が必要です。上記のURLにもう一度アクセスしてください。",
    "login_required":      "サインインしていません。まず「Microsoft 365にサインインして」とお伝えください。",
    "login_refresh_fail":  "トークンの更新に失敗しました。再度サインインしてください。",
    "logout_success":      "✅ サインアウトしました。トークンキャッシュを削除しました。",
    "logout_not_logged_in":"ℹ️  現在サインインしていません。",
    "status_logged_in":    "サインイン済み | {name} | {email}",
    "status_not_logged_in":"未サインイン",

    # 汎用
    "op_success":          "✅ 完了：{summary}",
    "op_failed":           "❌ 操作に失敗しました：{error}",
    "op_confirm_delete":   "⚠️  「{name}」を削除しますか？この操作は元に戻せません。（「確認」と返答して続行）",
    "op_confirm_send":     "📤 送信先：{to}\n件名：{subject}\n本文プレビュー：{preview}\n\n送信しますか？（「確認」と返答）",
    "op_cancelled":        "キャンセルしました。",
    "op_uploading":        "アップロード中...（{size}）",
    "op_downloading":      "ダウンロード中：{name}",

    # メール
    "mail_no_new":         "📭 新しいメールはありません。",
    "mail_new_count":      "📬 新着メールが {count} 件あります",
    "mail_from":           "送信者",
    "mail_subject":        "件名",
    "mail_date":           "日時",
    "mail_preview":        "プレビュー",
    "mail_unread":         "未読",
    "mail_sent":           "✅ メールを送信しました。",
    "mail_attachment":     "添付ファイル",

    # カレンダー
    "cal_no_events":       "📅 本日の予定はありません。",
    "cal_event_created":   "✅ 予定を作成しました：{title}",
    "cal_meeting_link":    "Teams会議リンク：{url}",
    "cal_busy":            "予定あり",
    "cal_free":            "空き",

    # ファイル
    "file_uploaded":       "✅ {name} を {path} にアップロードしました",
    "file_downloaded":     "✅ {name} をダウンロードしました（{size}）",
    "file_not_found":      "❌ ファイルが見つかりません：{path}",
    "file_share_link":     "🔗 共有リンク：{url}（有効期限：{expiry}）",
    "drive_empty":         "このフォルダは空です。",

    # Teams
    "teams_sent":          "✅ {target} にメッセージを送信しました",
    "teams_enterprise_only": "⚠️  Teams APIは法人アカウントが必要です。個人のOutlook.comアカウントはサポートされていません。",

    # タスク
    "task_created":        "✅ タスクを作成しました：{title}（期限：{due}）",
    "task_completed":      "✅ タスク「{title}」を完了にしました。",
    "task_no_due":         "期限なし",

    # SharePoint
    "sp_site_not_found":   "❌ サイトが見つかりません：{site}",
    "sp_page_created":     "✅ ページを作成しました（下書き）：{url}",
    "sp_page_published":   "✅ ページを公開しました：{url}",
    "sp_list_item_created":"✅ リストアイテムを作成しました。ID：{id}",
    "sp_no_doc_lib":       "❌ このサイトにドキュメントライブラリがありません。",

    # Power Automate
    "flow_triggered":      "⚡ フロー「{name}」をトリガーしました。処理中...",
    "flow_result":         "フロー実行結果：{result}",
    "flow_url_missing":    "❌ フローのトリガーURLが設定されていません。環境変数を設定してください：{env_var}",

    # ガントチャート
    "gantt_exported":      "✅ ガントチャートをエクスポートしました：{path}（{count} タスク）",
    "gantt_no_due":        "⚠️  {count} 件のタスクに期限がないためスキップしました。",
    "gantt_uploaded":      "📤 OneDriveにアップロードしました：{url}",

    # ルール
    "rule_created":        "✅ ルールを作成しました：{name}",
    "rule_disabled":       "⏸️  ルールを無効にしました：{name}",
    "rule_deleted":        "✅ ルールを削除しました：{name}",

    # エラー
    "err_401":             "❌ 認証エラー（401）。再度サインインしてください。",
    "err_403":             "❌ アクセス権限がありません（403）。アカウントの権限を確認するか、再度認証してください。",
    "err_404":             "❌ リソースが見つかりません（404）：{resource}",
    "err_429":             "⏳ リクエスト制限に達しました（429）。{wait} 秒後に再試行します...",
    "err_500":             "❌ Microsoftサービスエラー（{code}）。しばらく経ってから再試行してください。",
    "err_timeout":         "❌ リクエストがタイムアウトしました。ネットワーク接続を確認してください。",
    "err_generic":         "❌ エラーが発生しました：{error}",
}
