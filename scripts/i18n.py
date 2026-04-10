"""
ms365-gog 多语言支持模块
用法：
    from scripts.i18n import t, set_lang
    set_lang("ja")  # 切换到日语
    print(t("login_success", name="田中", email="tanaka@co.jp"))
"""

import os
import importlib.util
from pathlib import Path

_STRINGS: dict = {}
_LANG: str = "zh"

_LANG_FILES = {
    "zh": "strings_zh",
    "zh-cn": "strings_zh",
    "en": "strings_en",
    "en-us": "strings_en",
    "ja": "strings_ja",
    "ja-jp": "strings_ja",
}

_I18N_DIR = Path(__file__).parent.parent / "references" / "i18n"


def _load_lang(lang_key: str) -> dict:
    module_name = _LANG_FILES.get(lang_key.lower())
    if not module_name:
        print(f"[i18n] 不支持的语言 '{lang_key}'，回退到中文")
        module_name = "strings_zh"

    path = _I18N_DIR / f"{module_name}.py"
    if not path.exists():
        raise FileNotFoundError(f"找不到语言文件：{path}")

    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MS365_STRINGS


def set_lang(lang: str):
    """切换界面语言。支持：zh / en / ja"""
    global _STRINGS, _LANG
    _STRINGS = _load_lang(lang)
    _LANG = lang
    print(f"[i18n] 界面语言切换为：{_STRINGS.get('lang_name', lang)}")


def t(key: str, **kwargs) -> str:
    """
    获取翻译字符串，支持 {变量} 插值。
    未找到 key 时回退到 key 本身，不抛异常。
    """
    if not _STRINGS:
        # 延迟初始化：从环境变量或默认值加载
        _auto_init()

    template = _STRINGS.get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template  # 插值失败时返回原模板
    return template


def _auto_init():
    """根据环境变量或系统语言自动选择语言"""
    global _STRINGS, _LANG

    # 优先读取环境变量
    env_lang = os.environ.get("MS365_LANG", "").lower()
    if env_lang:
        _STRINGS = _load_lang(env_lang)
        _LANG = env_lang
        return

    # 其次读取系统语言（简单检测）
    import locale
    sys_lang = locale.getdefaultlocale()[0] or "zh_CN"
    if sys_lang.startswith("ja"):
        _STRINGS = _load_lang("ja")
        _LANG = "ja"
    elif sys_lang.lower().startswith("en"):
        _STRINGS = _load_lang("en")
        _LANG = "en"
    else:
        _STRINGS = _load_lang("zh")
        _LANG = "zh"


def current_lang() -> str:
    return _STRINGS.get("lang", _LANG) if _STRINGS else "zh-CN"


def available_langs() -> list[str]:
    return list(_LANG_FILES.keys())
