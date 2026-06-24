#!/usr/bin/env python3
"""Build and validate WeChat Mini Program domain settings for FitHub."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import production_readiness
import tencent_cloud_preflight


ROOT = Path(__file__).resolve().parent.parent
MINIAPP_ROOT = ROOT / "wechat-miniprogram"
TENCENT_ENV = ROOT / "deploy" / "tencent-cloud" / ".env.production"


def origin_from_url(raw_url: str) -> str:
    parsed = urllib.parse.urlparse(str(raw_url or "").strip())
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        value = value.strip().rstrip("/")
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


def status_item(key: str, label: str, ok: bool, detail: str) -> dict[str, Any]:
    return {"key": key, "label": label, "ok": bool(ok), "detail": detail}


def read_project_appid(root: Path) -> str:
    project_config = json.loads((root / "wechat-miniprogram" / "project.config.json").read_text(encoding="utf-8"))
    return str(project_config.get("appid") or "").strip()


def read_miniapp_api_base(root: Path) -> str:
    text = (root / "wechat-miniprogram" / "config.js").read_text(encoding="utf-8")
    return production_readiness.extract_js_string_property(text, "apiBase")


def read_env_values(env_file: Path) -> dict[str, str]:
    if not env_file.exists():
        return {}
    return tencent_cloud_preflight.parse_env_file(env_file)


def validate_domain(label: str, value: str) -> list[str]:
    failures: list[str] = []
    production_readiness.validate_https_custom_url(label, value, failures)
    return failures


def build_manifest(
    *,
    root: Path = ROOT,
    env_file: Path = TENCENT_ENV,
    require_cos_media: bool = True,
) -> dict[str, Any]:
    root = Path(root)
    env_file = Path(env_file)
    appid = read_project_appid(root)
    api_base = read_miniapp_api_base(root)
    api_origin = origin_from_url(api_base)
    env_values = read_env_values(env_file)
    media_provider = str(env_values.get("FITHUB_MEDIA_STORAGE_PROVIDER") or "").strip().lower()
    cos_public_origin = origin_from_url(env_values.get("FITHUB_TENCENT_COS_PUBLIC_BASE_URL", ""))
    download_domain = cos_public_origin or api_origin

    request_domains = unique([api_origin])
    upload_domains = unique([api_origin])
    download_domains = unique([download_domain])
    socket_domains: list[str] = []

    items: list[dict[str, Any]] = []
    appid_ok = bool(appid and appid != "touristappid" and appid.startswith("wx"))
    items.append(
        status_item(
            "miniapp_appid",
            "小程序 AppID",
            appid_ok,
            appid if appid_ok else f"当前 AppID={appid or 'missing'}",
        )
    )

    api_failures: list[str] = []
    production_readiness.validate_https_custom_url("Mini Program apiBase", api_base, api_failures, require_api_suffix=True)
    items.append(
        status_item(
            "api_base",
            "小程序 API 根路径",
            not api_failures,
            api_base if not api_failures else "; ".join(api_failures),
        )
    )

    domain_failures: list[str] = []
    for label, domains in (
        ("request 合法域名", request_domains),
        ("uploadFile 合法域名", upload_domains),
        ("downloadFile 合法域名", download_domains),
    ):
        if not domains:
            domain_failures.append(f"{label} 缺少域名。")
        for domain in domains:
            domain_failures.extend(validate_domain(label, domain))
    items.append(
        status_item(
            "wechat_domains",
            "微信后台合法域名",
            not domain_failures,
            "已生成" if not domain_failures else "; ".join(domain_failures),
        )
    )

    cos_ok = bool(media_provider == "cos" and cos_public_origin)
    if require_cos_media:
        items.append(
            status_item(
                "cos_download_domain",
                "媒体 downloadFile 域名使用腾讯 COS/CDN",
                cos_ok,
                cos_public_origin if cos_ok else f"provider={media_provider or 'missing'}, publicBase={cos_public_origin or 'missing'}",
            )
        )

    blockers = [item for item in items if not item["ok"]]
    return {
        "status": "ready" if not blockers else "blocked",
        "ready": not blockers,
        "blockerCount": len(blockers),
        "appid": appid,
        "apiBase": api_base,
        "domains": {
            "request": request_domains,
            "uploadFile": upload_domains,
            "downloadFile": download_domains,
            "socket": socket_domains,
        },
        "media": {
            "provider": media_provider,
            "cosPublicOrigin": cos_public_origin,
        },
        "items": items,
    }


def print_markdown(manifest: dict[str, Any]) -> None:
    print("# FitHub 微信小程序合法域名清单")
    print("")
    print(f"- AppID: {manifest['appid'] or 'missing'}")
    print(f"- apiBase: {manifest['apiBase'] or 'missing'}")
    print("")
    print("## 微信公众平台需要配置")
    print("")
    labels = {
        "request": "request 合法域名",
        "uploadFile": "uploadFile 合法域名",
        "downloadFile": "downloadFile 合法域名",
        "socket": "socket 合法域名",
    }
    for key in ("request", "uploadFile", "downloadFile", "socket"):
        domains = manifest["domains"].get(key) or []
        print(f"### {labels[key]}")
        if domains:
            for domain in domains:
                print(f"- {domain}")
        else:
            print("- 暂无")
        print("")
    print("## 检查结果")
    print("")
    for item in manifest["items"]:
        mark = "OK" if item["ok"] else "BLOCKED"
        print(f"- [{mark}] {item['label']}: {item['detail']}")
    print("")
    if manifest["ready"]:
        print("结论：微信小程序域名配置已满足提审前门槛。")
    else:
        print(f"结论：还有 {manifest['blockerCount']} 个阻断项，暂时不要提交小程序审核。")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and validate WeChat Mini Program legal domains.")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--env-file", default=str(TENCENT_ENV))
    parser.add_argument("--allow-non-cos-media", action="store_true", help="Do not require Tencent COS download domain.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        manifest = build_manifest(
            root=Path(args.root),
            env_file=Path(args.env_file),
            require_cos_media=not args.allow_non_cos_media,
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"WeChat domain manifest failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        print_markdown(manifest)
    return 0 if manifest["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
