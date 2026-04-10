#!/usr/bin/env python3
"""
ms365-gog 认证模块
使用 MSAL Device Code Flow，无需 Azure 开发者配置
"""

import os
import sys
import json
import stat
import argparse
from pathlib import Path

# ── 公共客户端配置 ──────────────────────────────────────────────────────────
# 使用 Microsoft Graph Explorer 的公共 Client ID（无需自行注册 Azure App）
# ⚠️ 风险：此 ID 为第三方公共客户端，微软可能限流或收回权限
# 企业版用户建议在 Azure Portal 注册自己的 App 并替换此 ID（见 references/enterprise.md）
CLIENT_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"  # Microsoft Graph Explorer 公共客户端
TENANT_ID = "common"  # 支持个人账号 + 企业账号

SCOPES = [
    "User.Read",
    "Mail.ReadWrite",
    "Mail.Send",
    "Calendars.ReadWrite",
    "Files.ReadWrite.All",
    "Chat.ReadWrite",
    "ChannelMessage.Send",
    "Tasks.ReadWrite",
    "offline_access",  # 获取 refresh token
]

TOKEN_CACHE_PATH = Path.home() / ".openclaw" / "ms365_token_cache.json"


class AuthRequiredError(Exception):
    pass


def _get_app():
    try:
        import msal
    except ImportError:
        print("正在安装 msal...", file=sys.stderr)
        import subprocess
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "msal", "--break-system-packages", "-q"]
        )
        import importlib
        importlib.invalidate_caches()
        import msal  # noqa: F811 (re-import after install)

    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE_PATH.exists():
        try:
            cache.deserialize(TOKEN_CACHE_PATH.read_text())
        except Exception:
            # 缓存文件损坏，清除后重新登录
            TOKEN_CACHE_PATH.unlink(missing_ok=True)

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        token_cache=cache,
    )
    return app, cache


def _save_cache(cache):
    TOKEN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE_PATH.write_text(cache.serialize())
    TOKEN_CACHE_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)  # chmod 600


def get_access_token(force_refresh: bool = False) -> str:
    """获取有效的 Access Token，自动刷新。未登录则抛出 AuthRequiredError。"""
    app, cache = _get_app()

    accounts = app.get_accounts()
    if not accounts:
        raise AuthRequiredError("未登录，请先运行: python scripts/auth.py --action login")

    result = app.acquire_token_silent(SCOPES, account=accounts[0], force_refresh=force_refresh)

    if result and "access_token" in result:
        _save_cache(cache)
        return result["access_token"]

    raise AuthRequiredError("Token 刷新失败，请重新登录: python scripts/auth.py --action login")


def cmd_login():
    app, cache = _get_app()
    flow = app.initiate_device_flow(scopes=SCOPES)

    if "user_code" not in flow:
        print(f"❌ 无法启动设备码流: {flow.get('error_description')}")
        sys.exit(1)

    print("\n" + "="*50)
    print("🔑 Microsoft 365 一键登录")
    print("="*50)
    print(f"1. 打开浏览器，访问: {flow['verification_uri']}")
    print(f"2. 输入一次性代码: {flow['user_code']}")
    print(f"3. 使用你的微软账号登录（个人/企业均可）")
    print("="*50)
    print("等待登录完成...\n")

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        _save_cache(cache)
        # 获取用户信息
        import urllib.request
        req = urllib.request.Request(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {result['access_token']}"}
        )
        try:
            with urllib.request.urlopen(req) as resp:
                user = json.loads(resp.read())
            print(f"✅ 登录成功！欢迎，{user.get('displayName', '')} ({user.get('mail') or user.get('userPrincipalName', '')})")
        except Exception:
            print("✅ 登录成功！")
    else:
        print(f"❌ 登录失败: {result.get('error_description', result.get('error'))}")
        sys.exit(1)


def cmd_status():
    try:
        token = get_access_token()
        import urllib.request
        req = urllib.request.Request(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req) as resp:
            user = json.loads(resp.read())
        print(f"LOGGED_IN | {user.get('displayName')} | {user.get('mail') or user.get('userPrincipalName')}")
    except AuthRequiredError:
        print("NOT_LOGGED_IN")
    except Exception as e:
        print(f"ERROR | {e}")


def cmd_logout():
    if TOKEN_CACHE_PATH.exists():
        TOKEN_CACHE_PATH.unlink()
        print("✅ 已退出登录，Token 缓存已清除")
    else:
        print("ℹ️  当前未登录")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ms365-gog 身份验证")
    parser.add_argument("--action", choices=["login", "status", "logout"], required=True)
    parser.add_argument("--cloud", choices=["global", "china"], default="global",
                        help="微软云区域（中国用 china）")
    args = parser.parse_args()

    if args.cloud == "china":
        # 中国区需要不同端点，暂提示用户
        print("⚠️  中国区 M365 支持正在开发中，请参见 references/china-cloud.md")
        sys.exit(1)

    if args.action == "login":
        cmd_login()
    elif args.action == "status":
        cmd_status()
    elif args.action == "logout":
        cmd_logout()
