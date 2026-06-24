#!/usr/bin/env python3
"""Validate the current Tencent Cloud trial environment.

This gate is intentionally different from the formal prelaunch gate:
- Trial gate proves the current fixed trial URL, CloudBase API, and feature
  inventory are safe for ongoing testers.
- Formal prelaunch gate still blocks on real WeChat AppID, legal domains, and
  Tencent COS/CDN before review or broad production launch.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import deploy_smoke
import prelaunch_gate
import production_write_acceptance


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FRONTEND = "https://zhangxin-zhinan-d4fwtsmr9a834d58-1401297280.tcloudbaseapp.com/fithub/"
DEFAULT_BACKEND = "https://fithub-api-274271-9-1401297280.sh.run.tcloudbase.com"


def phase(name: str, label: str, ready: bool, detail: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "label": label,
        "ready": bool(ready),
        "detail": detail,
        "payload": payload or {},
    }


def normalize_url(value: str) -> str:
    raw = str(value or "").strip()
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"Expected an HTTPS URL, got {value!r}")
    return raw.rstrip("/")


def phase_frontend(frontend_url: str, backend_url: str) -> dict[str, Any]:
    frontend_url = normalize_url(frontend_url) + "/"
    backend_url = normalize_url(backend_url)
    payload: dict[str, Any] = {"frontendUrl": frontend_url, "expectedApiOrigin": backend_url}
    try:
        code, html, shell_elapsed = deploy_smoke.fetch_text_with_retries(frontend_url, attempts=2, timeout=20)
        deploy_smoke.ensure(code == 200, f"前端返回 {code}")
        deploy_smoke.ensure("FitHub" in html or "探索" in html, "前端不像 FitHub 页面")
        config_url = urllib.parse.urljoin(frontend_url, "config.js")
        code, config_js, config_elapsed = deploy_smoke.fetch_text_with_retries(config_url, attempts=2, timeout=20)
        deploy_smoke.ensure(code == 200, f"config.js 返回 {code}")
        actual_api_origin = deploy_smoke.validate_frontend_api_origin(config_js, backend_url)
        payload.update(
            {
                "frontendElapsedSeconds": round(shell_elapsed, 3),
                "configElapsedSeconds": round(config_elapsed, 3),
                "actualApiOrigin": actual_api_origin,
            }
        )
        return phase("trial-fixed-frontend", "腾讯云固定试运行入口", True, f"前端可用，API 指向 {actual_api_origin}", payload)
    except Exception as exc:
        payload["error"] = str(exc)
        return phase("trial-fixed-frontend", "腾讯云固定试运行入口", False, str(exc), payload)


def phase_backend(backend_url: str, *, min_real_profiles: int, require_cos_media: bool) -> dict[str, Any]:
    backend_url = normalize_url(backend_url)
    payload: dict[str, Any] = {"backendUrl": backend_url}
    try:
        code, health, health_elapsed = deploy_smoke.fetch_text_with_retries(f"{backend_url}/healthz", attempts=2, timeout=20)
        deploy_smoke.ensure(code == 200, f"healthz 返回 {code}")
        deploy_smoke.ensure(str(health or "").strip(), "healthz 响应为空")
        code, storage, storage_elapsed = deploy_smoke.fetch_json(f"{backend_url}/api/storage/status?remote=1", attempts=2, timeout=30)
        deploy_smoke.ensure(code == 200, f"storage status 返回 {code}")
        deploy_smoke.validate_storage_status(
            storage,
            allow_local_storage=False,
            min_real_profiles=min_real_profiles,
            require_cos_media=require_cos_media,
        )
        code, bootstrap, bootstrap_elapsed = deploy_smoke.fetch_json(f"{backend_url}/api/bootstrap", attempts=2, timeout=30)
        deploy_smoke.ensure(code == 200, f"bootstrap 返回 {code}")
        deploy_smoke.ensure(isinstance(bootstrap.get("profiles"), list), "bootstrap 缺少 profiles")
        payload.update(
            {
                "health": str(health or "").strip()[:120],
                "storage": {
                    "loadedFrom": (storage.get("storage") or {}).get("loadedFrom"),
                    "remoteWritable": (storage.get("storage") or {}).get("remoteWritable"),
                    "mediaProvider": (storage.get("media") or {}).get("storageProvider"),
                    "metrics": storage.get("metrics") or {},
                },
                "elapsedSeconds": {
                    "healthz": round(health_elapsed, 3),
                    "storage": round(storage_elapsed, 3),
                    "bootstrap": round(bootstrap_elapsed, 3),
                },
            }
        )
        return phase("trial-cloudbase-api", "CloudBase API 与持久化", True, "CloudBase 可读写，bootstrap 正常", payload)
    except Exception as exc:
        payload["error"] = str(exc)
        return phase("trial-cloudbase-api", "CloudBase API 与持久化", False, str(exc), payload)


def phase_feature_inventory(root: Path) -> dict[str, Any]:
    phases = prelaunch_gate.build_feature_phases(root)
    blockers = [item for item in phases if not item.get("ready")]
    detail = "核心功能库存已通过" if not blockers else "; ".join(str(item.get("detail") or item.get("label")) for item in blockers[:3])
    return phase(
        "trial-feature-inventory",
        "试运行核心功能库存",
        not blockers,
        detail,
        {"phases": phases, "blockerCount": len(blockers)},
    )


def phase_write_acceptance(backend_url: str, *, min_real_profiles: int) -> dict[str, Any]:
    try:
        result = production_write_acceptance.run_acceptance(
            backend_url=backend_url,
            min_real_profiles=min_real_profiles,
        )
        return phase(
            "trial-write-acceptance",
            "线上写入闭环",
            True,
            "注册、关注、动态、私信、预约写入通过",
            result._asdict(),
        )
    except Exception as exc:
        return phase("trial-write-acceptance", "线上写入闭环", False, str(exc), {"error": str(exc)})


def formal_pending_items(root: Path) -> list[str]:
    configs = {}
    try:
        configs = prelaunch_gate.tencent_launch_gate.domestic_migration_status.read_configs(root)
    except Exception:
        pass
    items: list[str] = []
    if configs.get("miniappAppId") in {"", "touristappid", None}:
        items.append("替换真实微信小程序 AppID，并在云端配置 AppSecret")
    items.append("在微信后台配置 request/uploadFile/downloadFile 合法域名")
    items.append("正式提审前把媒体下载域名切到腾讯云 COS/CDN 或备案自定义域名")
    items.append("如需正式公开运营，绑定并备案 app/api/media 自定义域名")
    return items


def build_report(
    *,
    root: Path = ROOT,
    frontend_url: str = DEFAULT_FRONTEND,
    backend_url: str = DEFAULT_BACKEND,
    min_real_profiles: int = 0,
    require_cos_media: bool = False,
    run_write: bool = False,
) -> dict[str, Any]:
    root = Path(root)
    phases = [
        phase_frontend(frontend_url, backend_url),
        phase_backend(backend_url, min_real_profiles=min_real_profiles, require_cos_media=require_cos_media),
        phase_feature_inventory(root),
    ]
    if run_write:
        phases.append(phase_write_acceptance(backend_url, min_real_profiles=min_real_profiles))
    blockers = [item for item in phases if not item["ready"]]
    return {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "ready" if not blockers else "blocked",
        "ready": not blockers,
        "blockerCount": len(blockers),
        "frontendUrl": normalize_url(frontend_url) + "/",
        "backendUrl": normalize_url(backend_url),
        "phases": phases,
        "formalPrelaunchPending": formal_pending_items(root),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# FitHub 腾讯云试运行门禁",
        "",
        f"- 生成时间：{report['generatedAt']}",
        f"- 状态：{report['status']}",
        f"- 前端：{report['frontendUrl']}",
        f"- API：{report['backendUrl']}",
        f"- 阻断阶段数：{report['blockerCount']}",
        "",
    ]
    for item in report["phases"]:
        mark = "OK" if item["ready"] else "BLOCKED"
        lines.append(f"- [{mark}] {item['label']}：{item['detail']}")
    lines.append("")
    if report["ready"]:
        lines.append("结论：腾讯云固定试运行入口可继续给测试用户使用。")
    else:
        lines.append("结论：试运行门禁未通过，先不要扩大测试。")
    pending = list(report.get("formalPrelaunchPending") or [])
    if pending:
        lines.extend(["", "正式提审前仍需完成："])
        for index, item in enumerate(pending, start=1):
            lines.append(f"{index}. {item}")
    lines.append("")
    return "\n".join(lines)


def report_stem(report: dict[str, Any]) -> str:
    timestamp = str(report.get("generatedAt") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    safe_timestamp = timestamp.replace("-", "").replace(":", "").replace("T", "-").replace("Z", "Z")
    return f"fithub-trial-gate-{safe_timestamp}"


def write_outputs(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = report_stem(report)
    markdown_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"markdown": str(markdown_path), "json": str(json_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the FitHub Tencent Cloud trial gate.")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--frontend-url", default=DEFAULT_FRONTEND)
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND)
    parser.add_argument("--min-real-profiles", type=int, default=0)
    parser.add_argument("--require-cos-media", action="store_true")
    parser.add_argument("--run-write", action="store_true", help="Also run production write-path acceptance.")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--soft-fail", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = build_report(
            root=Path(args.root),
            frontend_url=args.frontend_url,
            backend_url=args.backend_url,
            min_real_profiles=args.min_real_profiles,
            require_cos_media=args.require_cos_media,
            run_write=args.run_write,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FitHub trial gate failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report), end="")
    if args.output_dir:
        paths = write_outputs(report, Path(args.output_dir))
        print(f"\n报告已写入：{paths['markdown']}")
        print(f"JSON 已写入：{paths['json']}")
    if args.soft_fail:
        return 0
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
