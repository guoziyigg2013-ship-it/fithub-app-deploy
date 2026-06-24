#!/usr/bin/env python3
"""Run the FitHub Tencent Cloud launch gate and summarize blockers."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import domestic_migration_status
import production_readiness
import tencent_domain_readiness
import wechat_domain_manifest


ROOT = Path(__file__).resolve().parent.parent
TENCENT_ENV = ROOT / "deploy" / "tencent-cloud" / ".env.production"


def phase(name: str, label: str, ready: bool, detail: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "label": label,
        "ready": bool(ready),
        "detail": detail,
        "payload": payload or {},
    }


def first_blocker_details(items: list[dict[str, Any]]) -> str:
    blockers = [item for item in items if not item.get("ok")]
    if not blockers:
        return "已通过"
    return "; ".join(str(item.get("detail") or item.get("label") or "blocked") for item in blockers[:3])


def configured_api_origin(root: Path) -> str:
    try:
        return domestic_migration_status.read_configs(root)["webApiOrigin"]
    except Exception:
        return ""


def static_url_validation(api_origin: str, web_origin: str, media_origin: str = "") -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for key, label, value in (
        ("api_origin", "API 固定域名", api_origin),
        ("web_origin", "用户访问固定域名", web_origin),
        ("media_origin", "媒体固定域名", media_origin),
    ):
        if key == "media_origin" and not value:
            items.append({"key": key, "label": label, "ok": False, "detail": "建议配置 media.yourdomain.com 作为 COS/CDN 下载域名。"})
            continue
        failures: list[str] = []
        production_readiness.validate_https_custom_url(label, value, failures)
        items.append({"key": key, "label": label, "ok": not failures, "detail": value if not failures else "; ".join(failures)})
    return items


def build_gate(
    *,
    root: Path = ROOT,
    env_file: Path = TENCENT_ENV,
    api_origin: str = "",
    web_origin: str = "",
    media_origin: str = "",
    expected_ip: str = "",
    check_domain_network: bool = False,
    check_acme: bool = False,
    check_tls: bool = False,
    check_live: bool = False,
    require_cos_media: bool = True,
) -> dict[str, Any]:
    root = Path(root)
    env_file = Path(env_file)
    configs = domestic_migration_status.read_configs(root)
    api_origin = (api_origin or configs.get("webApiOrigin") or "").rstrip("/")
    web_origin = web_origin.rstrip("/")
    media_origin = media_origin.rstrip("/")

    phases: list[dict[str, Any]] = []

    domestic_report = domestic_migration_status.build_report(
        root=root,
        env_file=env_file,
        backend_url=api_origin,
        check_live=check_live,
        require_cos_media=require_cos_media,
    )
    phases.append(
        phase(
            "domestic-migration",
            "国内生产配置",
            bool(domestic_report["ready"]),
            first_blocker_details(list(domestic_report["items"])),
            domestic_report,
        )
    )

    wechat_report = wechat_domain_manifest.build_manifest(
        root=root,
        env_file=env_file,
        require_cos_media=require_cos_media,
    )
    phases.append(
        phase(
            "wechat-domains",
            "微信小程序合法域名",
            bool(wechat_report["ready"]),
            first_blocker_details(list(wechat_report["items"])),
            wechat_report,
        )
    )

    url_items = static_url_validation(api_origin, web_origin, media_origin)
    phases.append(
        phase(
            "fixed-domains",
            "固定域名输入",
            all(bool(item["ok"]) for item in url_items),
            first_blocker_details(url_items),
            {"items": url_items, "apiOrigin": api_origin, "webOrigin": web_origin, "mediaOrigin": media_origin},
        )
    )

    if check_domain_network:
        try:
            domain_report = tencent_domain_readiness.build_report(
                api_origin=api_origin,
                web_origin=web_origin,
                media_origin=media_origin,
                expected_ip=expected_ip,
                check_acme=check_acme,
                check_tls=check_tls,
            )
        except ValueError as exc:
            domain_report = {"ready": False, "status": "blocked", "blockerCount": 1, "domains": [], "error": str(exc)}
        detail = "已通过" if domain_report.get("ready") else domain_report.get("error") or f"{domain_report.get('blockerCount', 0)} 个域名阻断项"
        phases.append(
            phase(
                "domain-network",
                "DNS/ACME/TLS",
                bool(domain_report.get("ready")),
                str(detail),
                domain_report,
            )
        )

    blockers = [item for item in phases if not item["ready"]]
    return {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "ready" if not blockers else "blocked",
        "ready": not blockers,
        "blockerCount": len(blockers),
        "urls": {
            "apiOrigin": api_origin,
            "webOrigin": web_origin,
            "mediaOrigin": media_origin,
            "configuredMiniappApiBase": configs.get("miniappApiBase", ""),
            "miniappAppId": configs.get("miniappAppId", ""),
        },
        "phases": phases,
        "nextSteps": domestic_report.get("nextSteps") or [],
    }


def print_markdown(report: dict[str, Any]) -> None:
    print("# FitHub 腾讯云国内上线总控门禁")
    print("")
    print(f"- 生成时间：{report['generatedAt']}")
    print(f"- API：{report['urls']['apiOrigin'] or '缺失'}")
    print(f"- Web：{report['urls']['webOrigin'] or '缺失'}")
    print(f"- Media：{report['urls']['mediaOrigin'] or '缺失'}")
    print(f"- 小程序 AppID：{report['urls']['miniappAppId'] or '缺失'}")
    print("")
    for item in report["phases"]:
        mark = "OK" if item["ready"] else "BLOCKED"
        print(f"- [{mark}] {item['label']}：{item['detail']}")
    print("")
    if report["ready"]:
        print("结论：总控门禁通过，可以进入最终发布验收。")
    else:
        print(f"结论：还有 {report['blockerCount']} 个阶段未通过，不要提交小程序审核或切给正式用户。")
        next_steps = list(report.get("nextSteps") or [])
        if next_steps:
            print("")
            print("下一步建议：")
            for index, step in enumerate(next_steps, start=1):
                print(f"{index}. {step}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the FitHub Tencent Cloud launch gate.")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--env-file", default=str(TENCENT_ENV))
    parser.add_argument("--api-origin", default="", help="Production API origin, e.g. https://api.example.cn")
    parser.add_argument("--web-origin", default="", help="Production web origin, e.g. https://app.example.cn")
    parser.add_argument("--media-origin", default="", help="Production media origin, e.g. https://media.example.cn")
    parser.add_argument("--expected-ip", default="", help="Tencent Cloud public IP expected in DNS.")
    parser.add_argument("--check-domain-network", action="store_true", help="Also run DNS/TCP/TLS network checks.")
    parser.add_argument("--check-acme", action="store_true", help="Require port 80 for ACME HTTP-01.")
    parser.add_argument("--check-tls", action="store_true", help="Require port 443 and valid TLS.")
    parser.add_argument("--check-live", action="store_true", help="Also validate live backend storage.")
    parser.add_argument("--allow-non-cos-media", action="store_true", help="Do not require Tencent COS media storage.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = build_gate(
            root=Path(args.root),
            env_file=Path(args.env_file),
            api_origin=args.api_origin,
            web_origin=args.web_origin,
            media_origin=args.media_origin,
            expected_ip=args.expected_ip,
            check_domain_network=args.check_domain_network,
            check_acme=args.check_acme,
            check_tls=args.check_tls,
            check_live=args.check_live,
            require_cos_media=not args.allow_non_cos_media,
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FitHub Tencent launch gate failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_markdown(report)
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
