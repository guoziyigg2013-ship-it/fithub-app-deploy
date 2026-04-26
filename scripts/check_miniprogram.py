#!/usr/bin/env python3
"""Validate the FitHub WeChat Mini Program scaffold."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MINIAPP_ROOT = ROOT / "wechat-miniprogram"


def fail(message: str) -> int:
    print(f"[miniapp check] {message}", file=sys.stderr)
    return 1


def check_json_files() -> int:
    for path in MINIAPP_ROOT.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return fail(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return 0


def check_pages() -> int:
    app_json = json.loads((MINIAPP_ROOT / "app.json").read_text(encoding="utf-8"))
    pages = app_json.get("pages") or []
    if not pages:
        return fail("app.json must define at least one page.")
    for page in pages:
        base = MINIAPP_ROOT / page
        for suffix in [".js", ".json", ".wxml", ".wxss"]:
            if not base.with_suffix(suffix).exists():
                return fail(f"Missing page file: {base.with_suffix(suffix).relative_to(ROOT)}")
    return 0


def check_js_files() -> int:
    for path in MINIAPP_ROOT.rglob("*.js"):
        result = subprocess.run(["node", "--check", str(path)], cwd=ROOT)
        if result.returncode != 0:
            return fail(f"JavaScript syntax check failed: {path.relative_to(ROOT)}")
    return 0


def main() -> int:
    if not MINIAPP_ROOT.exists():
        return fail("wechat-miniprogram directory does not exist.")
    for check in [check_json_files, check_pages, check_js_files]:
        result = check()
        if result:
            return result
    print("WeChat Mini Program scaffold check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
