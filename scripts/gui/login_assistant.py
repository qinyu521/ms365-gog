#!/usr/bin/env python3
"""
ms365-gog GUI 登录助手
跨平台桌面窗口（Windows / macOS / Linux），替代命令行登录流程。
依赖：仅 Python 标准库（tkinter 内置）+ msal
用法：python scripts/gui/login_assistant.py
"""

import sys
import os
import json
import threading
import subprocess
import importlib
from pathlib import Path

# ── 将项目根目录加入 path，以便 import scripts.auth ──────────────────────────
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))


def _ensure_msal():
    try:
        import msal  # noqa
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "msal", "--break-system-packages", "-q"]
        )
        importlib.invalidate_caches()


def _ensure_tkinter():
    try:
        import tkinter  # noqa
    except ImportError:
        msg = (
            "未找到 tkinter 模块。\n\n"
            "请按以下方式安装：\n"
            "  macOS:  brew install python-tk\n"
            "  Ubuntu: sudo apt install python3-tk\n"
            "  其他 Linux: 参考发行版文档"
        )
        print(msg)
        sys.exit(1)


# ── 常量（与 auth.py 保持一致）──────────────────────────────────────────────
CLIENT_ID       = "14d82eec-204b-4c2f-b7e8-296a70dab67e"
TENANT_ID       = "common"
AUTHORITY       = f"https://login.microsoftonline.com/{TENANT_ID}"
TOKEN_CACHE_DIR = Path.home() / ".openclaw"
TOKEN_CACHE_PATH = TOKEN_CACHE_DIR / "ms365_token_cache.json"
SCOPES = [
    "User.Read", "Mail.ReadWrite", "Mail.Send",
    "Calendars.ReadWrite", "Files.ReadWrite.All",
    "Chat.ReadWrite", "ChannelMessage.Send", "Tasks.ReadWrite", "offline_access"
]


def build_app(cache):
    import msal
    return msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)


def load_cache():
    import msal
    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE_PATH.exists():
        try:
            cache.deserialize(TOKEN_CACHE_PATH.read_text())
        except Exception:
            TOKEN_CACHE_PATH.unlink(missing_ok=True)
    return cache


def save_cache(cache):
    import stat
    TOKEN_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE_PATH.write_text(cache.serialize())
    TOKEN_CACHE_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)


# ── GUI ───────────────────────────────────────────────────────────────────────

class LoginAssistant:
    BRAND_BLUE  = "#0078d4"
    BRAND_LIGHT = "#deecf9"
    BG          = "#f3f2f1"
    CARD_BG     = "#ffffff"
    TEXT_MAIN   = "#201f1e"
    TEXT_MUTED  = "#605e5c"
    GREEN       = "#107c10"
    RED         = "#a4262c"

    def __init__(self, root):
        import tkinter as tk
        from tkinter import ttk, font as tkfont
        self.tk = tk
        self.ttk = ttk
        self.root = root
        self._setup_window()
        self._build_ui()
        self._check_status_bg()

    def _setup_window(self):
        tk = self.tk
        self.root.title("Microsoft 365 登录助手 · ms365-gog")
        self.root.geometry("480x560")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)
        # 居中
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self):
        tk = self.tk
        ttk = self.ttk

        # ── 顶部 Banner ────────────────────────────────────────────────────
        banner = tk.Frame(self.root, bg=self.BRAND_BLUE, height=80)
        banner.pack(fill="x")
        tk.Label(banner, text="☁  Microsoft 365", fg="white", bg=self.BRAND_BLUE,
                 font=("", 18, "bold")).pack(pady=(18, 2))
        tk.Label(banner, text="OpenClaw ms365-gog 登录助手", fg=self.BRAND_LIGHT,
                 bg=self.BRAND_BLUE, font=("", 10)).pack()

        # ── 状态卡片 ────────────────────────────────────────────────────────
        card = tk.Frame(self.root, bg=self.CARD_BG, relief="flat", bd=0)
        card.pack(fill="x", padx=20, pady=(20, 0))

        tk.Label(card, text="当前状态", fg=self.TEXT_MUTED, bg=self.CARD_BG,
                 font=("", 9)).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 2))

        self.status_icon = tk.Label(card, text="⏳", bg=self.CARD_BG, font=("", 22))
        self.status_icon.grid(row=1, column=0, padx=16, pady=4, sticky="w")

        self.status_label = tk.Label(card, text="检查中...", fg=self.TEXT_MUTED,
                                     bg=self.CARD_BG, font=("", 11), wraplength=380, justify="left")
        self.status_label.grid(row=2, column=0, padx=16, pady=(0, 14), sticky="w")
        card.pack_configure(ipady=0)

        # ── 设备码区域（登录时显示）───────────────────────────────────────
        self.code_frame = tk.Frame(self.root, bg=self.BRAND_LIGHT,
                                   relief="flat", bd=0)

        tk.Label(self.code_frame, text="第 1 步：打开浏览器，访问", bg=self.BRAND_LIGHT,
                 fg=self.TEXT_MAIN, font=("", 10)).pack(anchor="w", padx=16, pady=(14, 2))

        url_row = tk.Frame(self.code_frame, bg=self.BRAND_LIGHT)
        url_row.pack(fill="x", padx=16, pady=(0, 8))
        self.url_var = tk.StringVar(value="https://microsoft.com/devicelogin")
        url_entry = tk.Entry(url_row, textvariable=self.url_var, state="readonly",
                             font=("", 11), relief="solid", bd=1, fg=self.BRAND_BLUE,
                             readonlybackground=self.BRAND_LIGHT)
        url_entry.pack(side="left", fill="x", expand=True)
        tk.Button(url_row, text="复制", command=lambda: self._copy(self.url_var.get()),
                  bg=self.BRAND_BLUE, fg="white", relief="flat", padx=8,
                  cursor="hand2").pack(side="left", padx=(6, 0))

        tk.Label(self.code_frame, text="第 2 步：输入一次性验证码", bg=self.BRAND_LIGHT,
                 fg=self.TEXT_MAIN, font=("", 10)).pack(anchor="w", padx=16, pady=(4, 2))

        code_row = tk.Frame(self.code_frame, bg=self.BRAND_LIGHT)
        code_row.pack(fill="x", padx=16, pady=(0, 14))
        self.code_var = tk.StringVar(value="——")
        code_lbl = tk.Label(code_row, textvariable=self.code_var, fg=self.BRAND_BLUE,
                            bg=self.BRAND_LIGHT, font=("Courier", 26, "bold"))
        code_lbl.pack(side="left")
        tk.Button(code_row, text="复制", command=lambda: self._copy(self.code_var.get()),
                  bg=self.BRAND_BLUE, fg="white", relief="flat", padx=8,
                  cursor="hand2").pack(side="left", padx=(14, 0))

        tk.Label(self.code_frame, text="完成后本窗口将自动更新 ✔", bg=self.BRAND_LIGHT,
                 fg=self.TEXT_MUTED, font=("", 9)).pack(anchor="w", padx=16, pady=(0, 12))

        # ── 按钮区 ──────────────────────────────────────────────────────────
        btn_frame = tk.Frame(self.root, bg=self.BG)
        btn_frame.pack(fill="x", padx=20, pady=16)

        self.login_btn = tk.Button(btn_frame, text="登录 Microsoft 365",
                                   command=self._on_login,
                                   bg=self.BRAND_BLUE, fg="white",
                                   font=("", 11, "bold"), relief="flat",
                                   pady=10, cursor="hand2", activebackground="#106ebe")
        self.login_btn.pack(fill="x", pady=(0, 8))

        self.logout_btn = tk.Button(btn_frame, text="退出登录",
                                    command=self._on_logout,
                                    bg="#d13438", fg="white",
                                    font=("", 10), relief="flat",
                                    pady=8, cursor="hand2", state="disabled")
        self.logout_btn.pack(fill="x")

        # ── 语言切换 ────────────────────────────────────────────────────────
        lang_frame = tk.Frame(self.root, bg=self.BG)
        lang_frame.pack(anchor="e", padx=20)
        tk.Label(lang_frame, text="语言 / Language：", bg=self.BG,
                 fg=self.TEXT_MUTED, font=("", 9)).pack(side="left")
        self.lang_var = tk.StringVar(value="中文")
        lang_menu = ttk.Combobox(lang_frame, textvariable=self.lang_var,
                                 values=["中文", "English", "日本語"],
                                 state="readonly", width=9, font=("", 9))
        lang_menu.pack(side="left")
        lang_menu.bind("<<ComboboxSelected>>", self._on_lang_change)

        # ── 底部版本 ─────────────────────────────────────────────────────────
        tk.Label(self.root, text="ms365-gog · MIT License · github.com/your-username/ms365-gog",
                 fg=self.TEXT_MUTED, bg=self.BG, font=("", 8)).pack(side="bottom", pady=10)

    # ── 事件处理 ─────────────────────────────────────────────────────────────

    def _check_status_bg(self):
        threading.Thread(target=self._check_status, daemon=True).start()

    def _check_status(self):
        _ensure_msal()
        cache = load_cache()
        app = build_app(cache)
        accounts = app.get_accounts()
        if not accounts:
            self._set_status("not_logged_in")
            return
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            save_cache(cache)
            self._fetch_user_info(result["access_token"])
        else:
            self._set_status("not_logged_in")

    def _fetch_user_info(self, token: str):
        import urllib.request
        req = urllib.request.Request(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                user = json.loads(resp.read())
            name  = user.get("displayName", "")
            email = user.get("mail") or user.get("userPrincipalName", "")
            self._set_status("logged_in", name=name, email=email)
        except Exception:
            self._set_status("logged_in", name="（未知）", email="")

    def _set_status(self, state: str, **kwargs):
        tk = self.tk
        if state == "logged_in":
            icon  = "✅"
            text  = f"已登录\n{kwargs.get('name', '')}\n{kwargs.get('email', '')}"
            color = self.GREEN
            self.root.after(0, lambda: self.login_btn.config(state="disabled"))
            self.root.after(0, lambda: self.logout_btn.config(state="normal"))
            self.root.after(0, self.code_frame.pack_forget)
        elif state == "not_logged_in":
            icon  = "🔒"
            text  = "未登录\n点击下方按钮开始授权"
            color = self.TEXT_MUTED
            self.root.after(0, lambda: self.login_btn.config(state="normal"))
            self.root.after(0, lambda: self.logout_btn.config(state="disabled"))
            self.root.after(0, self.code_frame.pack_forget)
        elif state == "waiting_code":
            icon  = "⏳"
            text  = "等待浏览器授权...\n完成后此窗口将自动更新"
            color = self.BRAND_BLUE
            self.root.after(0, lambda: self.code_frame.pack(fill="x", padx=20, pady=(10, 0)))
        elif state == "error":
            icon  = "❌"
            text  = f"登录失败\n{kwargs.get('error', '')}"
            color = self.RED
            self.root.after(0, lambda: self.login_btn.config(state="normal"))
            self.root.after(0, self.code_frame.pack_forget)
        else:
            icon, text, color = "⏳", "检查中...", self.TEXT_MUTED

        self.root.after(0, lambda: self.status_icon.config(text=icon))
        self.root.after(0, lambda: self.status_label.config(text=text, fg=color))

    def _on_login(self):
        self.login_btn.config(state="disabled", text="登录中...")
        threading.Thread(target=self._do_login, daemon=True).start()

    def _do_login(self):
        _ensure_msal()
        cache = load_cache()
        app = build_app(cache)
        flow = app.initiate_device_flow(scopes=SCOPES)

        if "user_code" not in flow:
            self._set_status("error", error=flow.get("error_description", "未知错误"))
            self.root.after(0, lambda: self.login_btn.config(state="normal", text="登录 Microsoft 365"))
            return

        # 更新界面显示设备码
        self.root.after(0, lambda: self.url_var.set(flow["verification_uri"]))
        self.root.after(0, lambda: self.code_var.set(flow["user_code"]))
        self._set_status("waiting_code")

        # 尝试自动打开浏览器
        try:
            import webbrowser
            webbrowser.open(flow["verification_uri"])
        except Exception:
            pass

        result = app.acquire_token_by_device_flow(flow)
        self.root.after(0, lambda: self.login_btn.config(text="登录 Microsoft 365"))

        if "access_token" in result:
            save_cache(cache)
            self._fetch_user_info(result["access_token"])
        else:
            error = result.get("error_description", result.get("error", "未知错误"))
            self._set_status("error", error=error)
            self.root.after(0, lambda: self.login_btn.config(state="normal"))

    def _on_logout(self):
        if TOKEN_CACHE_PATH.exists():
            TOKEN_CACHE_PATH.unlink()
        self._set_status("not_logged_in")
        self.root.after(0, lambda: self.login_btn.config(state="normal"))

    def _on_lang_change(self, _event=None):
        lang_map = {"中文": "zh", "English": "en", "日本語": "ja"}
        lang = lang_map.get(self.lang_var.get(), "zh")
        os.environ["MS365_LANG"] = lang
        # 简单提示重启
        self.tk.messagebox.showinfo(
            "语言 / Language",
            {"zh": "语言设置已保存，重启后生效。",
             "en": "Language saved. Restart to apply.",
             "ja": "言語設定を保存しました。再起動後に反映されます。"}.get(lang, "")
        )

    def _copy(self, text: str):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)


def main():
    _ensure_tkinter()
    _ensure_msal()
    import tkinter as tk
    root = tk.Tk()
    try:
        from tkinter import messagebox  # noqa — ensure it's importable
    except ImportError:
        pass
    app = LoginAssistant(root)
    root.mainloop()


if __name__ == "__main__":
    main()
