#!/usr/bin/env python3
"""Report FitHub mainland China production migration status."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import production_readiness
import tencent_cloud_preflight


ROOT = Path(__file__).resolve().parent.parent
MINIAPP_ROOT = ROOT / "wechat-miniprogram"
TENCENT_ENV = ROOT / "deploy" / "tencent-cloud" / ".env.production"


def status_item(key: str, label: str, ok: bool, detail: str) -> dict[str, object]:
    return {
        "key": key,
        "label": label,
        "ok": bool(ok),
        "detail": detail,
    }


def read_configs(root: Path) -> dict[str, str]:
    miniapp_root = root / "wechat-miniprogram"
    web_config = (root / "config.js").read_text(encoding="utf-8")
    mini_config = (miniapp_root / "config.js").read_text(encoding="utf-8")
    project_config = json.loads((miniapp_root / "project.config.json").read_text(encoding="utf-8"))
    return {
        "webApiOrigin": production_readiness.extract_js_string_property(web_config, "apiOrigin"),
        "miniappApiBase": production_readiness.extract_js_string_property(mini_config, "apiBase"),
        "miniappAppId": str(project_config.get("appid") or "").strip(),
    }


def validate_static_configs(root: Path) -> list[dict[str, object]]:
    config = read_configs(root)
    items: list[dict[str, object]] = []

    failures: list[str] = []
    production_readiness.validate_https_custom_url("Web apiOrigin", config["webApiOrigin"], failures)
    items.append(
        status_item(
            "web_api_origin",
            "Web API 已切国内生产域名",
            not failures,
            config["webApiOrigin"] if not failures else "; ".join(failures),
        )
    )

    failures = []
    production_readiness.validate_https_custom_url("Mini Program apiBase", config["miniappApiBase"], failures, require_api_suffix=True)
    items.append(
        status_item(
            "miniapp_api_base",
            "小程序 API 已切国内生产域名",
            not failures,
            config["miniappApiBase"] if not failures else "; ".join(failures),
        )
    )

    appid = config["miniappAppId"]
    appid_ok = bool(appid and appid != "touristappid" and appid.startswith("wx"))
    items.append(
        status_item(
            "miniapp_appid",
            "小程序 AppID 已替换为真实 AppID",
            appid_ok,
            appid if appid_ok else f"当前 AppID={appid or 'missing'}",
        )
    )
    return items


def validate_tencent_env(env_file: Path, *, require_cos_media: bool) -> list[dict[str, object]]:
    if not env_file.exists():
        return [
            status_item(
                "tencent_env",
                "腾讯云生产环境变量文件已生成",
                False,
                f"缺少 {env_file}。用 npm run init:tencent-env 生成真实服务器环境变量。",
            )
        ]

    values = tencent_cloud_preflight.parse_env_file(env_file)
    failures: list[str] = []
    tencent_cloud_preflight.validate_env(values, failures)
    provider = str(values.get("FITHUB_MEDIA_STORAGE_PROVIDER") or "").strip().lower()
    if require_cos_media and provider != "cos":
        failures.append(f"FITHUB_MEDIA_STORAGE_PROVIDER should be cos for mainland China production, got {provider or 'missing'}.")

    return [
        status_item(
            "tencent_env",
            "腾讯云生产环境变量通过预检",
            not failures,
            "已通过" if not failures else "; ".join(failures),
        )
    ]


def validate_live_backend(backend_url: str, *, require_cos_media: bool) -> list[dict[str, object]]:
    if not backend_url:
        return [
            status_item(
                "live_backend",
                "线上后端健康且可写",
                False,
                "未提供 backend URL。",
            )
        ]
    failures: list[str] = []
    production_readiness.validate_live_backend(backend_url, failures, require_cos_media=require_cos_media)
    return [
        status_item(
            "live_backend",
            "线上后端健康且可写",
            not failures,
            backend_url if not failures else "; ".join(failures),
        )
    ]


def build_next_steps(items: list[dict[str, object]]) -> list[str]:
    blocked_keys = {str(item["key"]) for item in items if not item["ok"]}
    steps: list[str] = []
    if {"web_api_origin", "miniapp_api_base", "miniapp_appid"} & blocked_keys:
        steps.append(
            "执行 npm run cutover:tencent -- --api-origin https://api.yourdomain.com "
            "--web-origin https://app.yourdomain.com --miniapp-appid wx你的真实AppID --apply"
        )
    if "tencent_env" in blocked_keys:
        steps.append(
            "执行 npm run init:tencent-env -- --api-origin https://api.yourdomain.com "
            "--state-provider cloudbase --cloudbase-env-id 你的CloudBase环境ID --cloudbase-api-key 你的CloudBaseAPIKey --write"
        )
    if {"web_api_origin", "miniapp_api_base", "tencent_env"} & blocked_keys:
        steps.append(
            "拿到服务器公网 IP 后执行 npm run check:tencent-domains -- "
            "--api-origin https://api.yourdomain.com --web-origin https://app.yourdomain.com "
            "--media-origin https://media.yourdomain.com --expected-ip 你的服务器公网IP --check-acme"
        )
    if "live_backend" in blocked_keys:
        steps.append(
            "部署完成后执行 npm run check:smoke -- --frontend-url https://app.yourdomain.com/ "
            "--backend-url https://api.yourdomain.com --expect-frontend-api-origin https://api.yourdomain.com --require-cos-media"
        )
    return steps


def build_report(
    *,
    root: Path = ROOT,
    env_file: Path = TENCENT_ENV,
    backend_url: str = "",
    check_live: bool = False,
    require_cos_media: bool = True,
) -> dict[str, object]:
    root = Path(root)
    items = []
    items.extend(validate_static_configs(root))
    items.extend(validate_tencent_env(Path(env_file), require_cos_media=require_cos_media))
    if check_live:
        items.extend(validate_live_backend(backend_url or read_configs(root)["webApiOrigin"], require_cos_media=require_cos_media))
    blockers = [item for item in items if not item["ok"]]
    return {
        "status": "ready" if not blockers else "blocked",
        "ready": not blockers,
        "items": items,
        "blockerCount": len(blockers),
        "nextSteps": build_next_steps(items),
    }


def print_markdown(report: dict[str, object]) -> None:
    title = "FitHub 国内固定域迁移状态"
    print(f"# {title}")
    print("")
    for item in report["items"]:
        mark = "OK" if item["ok"] else "BLOCKED"
        print(f"- [{mark}] {item['label']}: {item['detail']}")
    print("")
    if report["ready"]:
        print("结论：当前配置已满足国内生产切换门槛。")
    else:
        print(f"结论：还有 {report['blockerCount']} 个阻断项，暂时不要提交小程序审核或面向正式用户发布。")
        next_steps = list(report.get("nextSteps") or [])
        if next_steps:
            print("")
            print("下一步建议：")
            for index, step in enumerate(next_steps, start=1):
                print(f"{index}. {step}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Report FitHub mainland China production migration status.")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--env-file", default=str(TENCENT_ENV))
    parser.add_argument("--backend-url", default="")
    parser.add_argument("--check-live", action="store_true")
    parser.add_argument("--allow-non-cos-media", action="store_true", help="Do not require Tencent COS media storage.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = build_report(
            root=Path(args.root),
            env_file=Path(args.env_file),
            backend_url=args.backend_url,
            check_live=args.check_live,
            require_cos_media=not args.allow_non_cos_media,
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FitHub domestic migration status failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_markdown(report)
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
