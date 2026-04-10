#!/usr/bin/env python3
"""
打包 ms365-gog 为 .skill 文件
用法：python scripts/package.py
输出：dist/ms365-gog.skill
"""

import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILL_DIR = ROOT  # SKILL.md 在根目录
DIST_DIR = ROOT / "dist"
OUTPUT = DIST_DIR / "ms365-gog.skill"

# 打包时包含的文件/目录
INCLUDE = [
    "SKILL.md",
    "scripts/auth.py",
    "references/mail.md",
    "references/calendar.md",
    "references/onedrive.md",
    "references/teams.md",
    "references/office-docs.md",
    "references/tasks.md",
    "references/webhook.md",
    "references/enterprise.md",
    "references/sharepoint.md",
    "references/china-cloud.md",
]

# 排除这些文件（不进入 .skill 包）
EXCLUDE_SUFFIXES = {".pyc", ".DS_Store"}
EXCLUDE_DIRS = {"__pycache__", ".git", "dist", "docs", ".github"}


def main():
    DIST_DIR.mkdir(exist_ok=True)

    missing = [f for f in INCLUDE if not (SKILL_DIR / f).exists()]
    if missing:
        print(f"❌ 以下文件不存在，请检查：")
        for f in missing:
            print(f"   {f}")
        sys.exit(1)

    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel_path in INCLUDE:
            full_path = SKILL_DIR / rel_path
            zf.write(full_path, rel_path)
            print(f"  ✓ {rel_path}")

    size_kb = OUTPUT.stat().st_size // 1024
    print(f"\n✅ 打包完成：{OUTPUT}  ({size_kb} KB)")
    print(f"   包含 {len(INCLUDE)} 个文件")
    print(f"\n安装方式：")
    print(f"  OpenClaw → 设置 → Skills → 安装本地 Skill → 选择 dist/ms365-gog.skill")


if __name__ == "__main__":
    main()
