#!/usr/bin/env python3
"""Switch FitHub repository configs to the approved production API and Mini Program AppID."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import urllib.parse
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MINIAPP_ROOT = ROOT / "wechat-miniprogram"
DISALLOWED_PRODUCTION_HOST_PARTS = ("onrender.com", "pages.dev", "trycloudflare.com", "localhost", "127.0.0.1")


def normalize_api_origin(value: str) -> str:
    raw = str(value or "").strip().rstrip("/")
    parsed = urllib.parse.urlparse(raw)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host:
        raise ValueError("API 域名必须是完整 HTTPS 地址，例如 https://api.example.com")
    if any(part in host for part in DISALLOWED_PRODUCTION_HOST_PARTS):
        raise ValueError(f"API 域名不能使用临时域名：{host}")
    if parsed.path and parsed.path != "/":
        raise ValueError("API Origin 只填写域名根路径，不要带 /api；脚本会自动生成小程序 apiBase。")
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, "", "", "", ""))


def normalize_api_base(api_origin: str, api_base: str = "") -> str:
    if not api_base:
        return api_origin.rstrip("/") + "/api"
    raw = str(api_base or "").strip().rstrip("/")
    parsed = urllib.parse.urlparse(raw)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host:
        raise ValueError("小程序 apiBase 必须是完整 HTTPS 地址。")
    if any(part in host for part in DISALLOWED_PRODUCTION_HOST_PARTS):
        raise ValueError(f"小程序 apiBase 不能使用临时域名：{host}")
    if not raw.endswith("/api"):
        raise ValueError("小程序 apiBase 必须指向 /api 根路径。")
    return raw


def normalize_appid(value: str) -> str:
    appid = str(value or "").strip()
    if not appid or appid == "touristappid":
        raise ValueError("小程序 AppID 不能是 touristappid。")
    if not re.fullmatch(r"wx[a-zA-Z0-9]{8,}", appid):
        raise ValueError("小程序 AppID 应以 wx 开头，并使用微信公众平台提供的真实 AppID。")
    return appid


def replace_js_string_property(text: str, key: str, value: str) -> str:
    pattern = rf"({re.escape(key)}\s*:\s*)[\"'][^\"']*[\"']"
    updated, count = re.subn(pattern, rf'\1"{value}"', text, count=1)
    if count != 1:
        raise ValueError(f"没有在 JS 配置中找到 {key} 字段。")
    return updated


def planned_change(path: Path, before: str, after: str, *, root: Path) -> str:
    if before == after:
        return f"{path.relative_to(root)} unchanged\n"
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=str(path.relative_to(root)) + " (before)",
            tofile=str(path.relative_to(root)) + " (after)",
        )
    )


def configure(root: Path, api_origin: str, miniapp_appid: str, *, api_base: str = "", dry_run: bool = False) -> list[str]:
    root = Path(root)
    miniapp_root = root / "wechat-miniprogram"
    api_origin = normalize_api_origin(api_origin)
    api_base = normalize_api_base(api_origin, api_base)
    miniapp_appid = normalize_appid(miniapp_appid)

    web_config_path = root / "config.js"
    mini_config_path = miniapp_root / "config.js"
    project_config_path = miniapp_root / "project.config.json"

    web_before = web_config_path.read_text(encoding="utf-8")
    mini_before = mini_config_path.read_text(encoding="utf-8")
    project_before = project_config_path.read_text(encoding="utf-8")

    web_after = replace_js_string_property(web_before, "apiOrigin", api_origin)
    mini_after = replace_js_string_property(mini_before, "apiBase", api_base)
    project_config = json.loads(project_before)
    project_config["appid"] = miniapp_appid
    project_after = json.dumps(project_config, ensure_ascii=False, indent=2) + "\n"

    previews = [
        planned_change(web_config_path, web_before, web_after, root=root),
        planned_change(mini_config_path, mini_before, mini_after, root=root),
        planned_change(project_config_path, project_before, project_after, root=root),
    ]
    if not dry_run:
        web_config_path.write_text(web_after, encoding="utf-8")
        mini_config_path.write_text(mini_after, encoding="utf-8")
        project_config_path.write_text(project_after, encoding="utf-8")
    return previews


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure FitHub production API domain and WeChat Mini Program AppID.")
    parser.add_argument("--api-origin", required=True, help="Approved backend origin, for example https://api.example.com")
    parser.add_argument("--miniapp-appid", required=True, help="Real WeChat Mini Program AppID, for example wx123...")
    parser.add_argument("--api-base", default="", help="Optional Mini Program API base. Defaults to <api-origin>/api.")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing files.")
    args = parser.parse_args()

    try:
        previews = configure(
            ROOT,
            args.api_origin,
            args.miniapp_appid,
            api_base=args.api_base,
            dry_run=args.dry_run,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Production config failed: {exc}", file=sys.stderr)
        return 1

    action = "would update" if args.dry_run else "updated"
    print(f"FitHub production config {action}:")
    for preview in previews:
        print(preview, end="" if preview.endswith("\n") else "\n")
    print("\nNext: run npm run check:production after the backend domain is live.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
