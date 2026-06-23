#!/usr/bin/env python3
"""Validate the FitHub WeChat Mini Program scaffold."""

from __future__ import annotations

import argparse
import json
import re
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


def read_config_api_base() -> str:
    config_text = (MINIAPP_ROOT / "config.js").read_text(encoding="utf-8")
    match = re.search(r"apiBase\s*:\s*[\"']([^\"']+)[\"']", config_text)
    return match.group(1).strip() if match else ""


def check_production_config() -> int:
    project_config = json.loads((MINIAPP_ROOT / "project.config.json").read_text(encoding="utf-8"))
    appid = str(project_config.get("appid") or "").strip()
    if not appid or appid == "touristappid":
        return fail("Production mini program must use a real AppID, not touristappid.")
    if not appid.startswith("wx"):
        return fail("Production mini program AppID should start with wx.")

    api_base = read_config_api_base()
    if not api_base:
        return fail("wechat-miniprogram/config.js must define apiBase.")
    if not api_base.startswith("https://"):
        return fail("Production apiBase must use HTTPS.")
    if "onrender.com" in api_base or "pages.dev" in api_base:
        return fail("Production apiBase must use your approved custom backend domain, not Render or Pages.")
    if not api_base.rstrip("/").endswith("/api"):
        return fail("Production apiBase should point to the /api root.")

    publish_js = (MINIAPP_ROOT / "pages" / "publish" / "index.js").read_text(encoding="utf-8")
    media_js = (MINIAPP_ROOT / "utils" / "media.js").read_text(encoding="utf-8")
    if "/media/upload-file" not in publish_js or "wx.uploadFile" not in (MINIAPP_ROOT / "utils" / "api.js").read_text(encoding="utf-8"):
        return fail("Production media publishing must use wx.uploadFile and /media/upload-file.")
    if "fileToDataUrl" in publish_js or "encoding: \"base64\"" in media_js or "encoding: 'base64'" in media_js:
        return fail("Production mini program must not publish media through base64 JSON uploads.")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the FitHub WeChat Mini Program scaffold.")
    parser.add_argument(
        "--production",
        action="store_true",
        help="Also enforce pre-review production settings such as real AppID and approved HTTPS API domain.",
    )
    args = parser.parse_args()

    if not MINIAPP_ROOT.exists():
        return fail("wechat-miniprogram directory does not exist.")
    for check in [check_json_files, check_pages, check_js_files]:
        result = check()
        if result:
            return result
    if args.production:
        result = check_production_config()
        if result:
            return result
    print("WeChat Mini Program scaffold check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
