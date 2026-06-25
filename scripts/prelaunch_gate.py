#!/usr/bin/env python3
"""Run the FitHub prelaunch product and production readiness gate."""

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

import tencent_launch_gate


ROOT = Path(__file__).resolve().parent.parent
TENCENT_ENV = ROOT / "deploy" / "tencent-cloud" / ".env.production"


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def check_file(root: Path, relative_path: str, needles: list[str]) -> dict[str, Any]:
    text = read_text(root, relative_path)
    missing = [needle for needle in needles if needle not in text]
    return {
        "file": relative_path,
        "ok": bool(text) and not missing,
        "missing": missing,
    }


def check_exists(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    return {
        "file": relative_path,
        "ok": path.exists(),
        "missing": [] if path.exists() else [relative_path],
    }


def feature_check(label: str, checks: list[dict[str, Any]]) -> dict[str, Any]:
    failures = [item for item in checks if not item["ok"]]
    detail = "已具备"
    if failures:
        parts = []
        for item in failures[:3]:
            missing = ", ".join(item.get("missing") or ["missing"])
            parts.append(f"{item.get('file', 'unknown')}: {missing}")
        detail = "; ".join(parts)
    return {
        "label": label,
        "ok": not failures,
        "detail": detail,
        "checks": checks,
    }


def phase(name: str, label: str, checks: list[dict[str, Any]]) -> dict[str, Any]:
    failures = [item for item in checks if not item["ok"]]
    return {
        "name": name,
        "label": label,
        "ready": not failures,
        "detail": "已通过" if not failures else "; ".join(item["detail"] for item in failures[:3]),
        "checks": checks,
    }


def build_feature_phases(root: Path) -> list[dict[str, Any]]:
    return [
        phase(
            "p0-account-data-integrity",
            "P0 账号与数据不丢",
            [
                feature_check(
                    "手机号恢复、关注恢复与退出登录",
                    [
                        check_file(root, "server.py", ["/auth/restore", "/auth/restore-follows", "/auth/logout"]),
                        check_file(root, "app.js", ["/auth/restore", "/auth/restore-follows", "/auth/logout"]),
                    ],
                ),
                feature_check(
                    "发布前后数据快照与回归测试",
                    [
                        check_file(root, "package.json", ['"snapshot:prod"', '"test:api"']),
                        check_exists(root, "scripts/production_snapshot.py"),
                        check_file(root, "scripts/production_snapshot.py", ["write_manifest", "prune_snapshots"]),
                        check_file(
                            root,
                            "tests/api/test_persistence.py",
                            [
                                "production_snapshot_metric_comparison_rejects_regressions",
                                "production_snapshot_manifest_records_local_backups",
                                "production_snapshot_prune_keeps_recent_and_latest_files",
                            ],
                        ),
                        check_file(root, "tests/api/test_social.py", ["follow_state_survives_login_and_server_restart"]),
                    ],
                ),
                feature_check(
                    "多身份消息与预约隔离",
                    [
                        check_file(root, "tests/api/test_social.py", ["multi_identity_threads_are_scoped_to_current_identity"]),
                        check_file(root, "tests/api/test_booking.py", ["multi_identity_bookings_are_scoped_to_current_identity"]),
                    ],
                ),
            ],
        ),
        phase(
            "p0-media-production",
            "P0 头像、图片、视频生产化",
            [
                feature_check(
                    "对象存储、multipart 上传与缩略图",
                    [
                        check_file(root, "server.py", ["FITHUB_MEDIA_STORAGE_PROVIDER", "media/upload-file", "thumbnail"]),
                        check_file(root, "tests/api/test_content.py", ["multipart_media_upload_returns_reusable_asset_payload", "video_post_persists_thumbnail"]),
                        check_file(root, "tests/api/test_tencent_cos_media.py", ["upload_media_asset_uses_cos_provider_and_public_url"]),
                    ],
                ),
                feature_check(
                    "小程序真实文件上传链路",
                    [
                        check_file(root, "wechat-miniprogram/utils/api.js", ["wx.uploadFile"]),
                        check_file(root, "wechat-miniprogram/pages/publish/index.js", ["chooseMedia", "/media/upload-file"]),
                    ],
                ),
            ],
        ),
        phase(
            "p0-instant-feedback",
            "P0 关键操作即时反馈",
            [
                feature_check(
                    "关注、点赞、收藏、私信不走全量阻塞同步",
                    [
                        check_file(root, "app.js", ["postWithoutStateSync(`${API_BASE}/follow/toggle`"]),
                        check_file(root, "app.js", ["postWithoutStateSync(`${API_BASE}/post/like`"]),
                        check_file(root, "app.js", ["postWithoutStateSync(`${API_BASE}/post/favorite-toggle`"]),
                        check_file(root, "app.js", ["postWithoutStateSync(`${API_BASE}/message/send`"]),
                    ],
                ),
                feature_check(
                    "互动回归测试覆盖点赞、收藏、评论与通知",
                    [
                        check_file(root, "tests/api/test_content.py", ["like_favorite_comment_and_notifications_surface"]),
                    ],
                ),
            ],
        ),
        phase(
            "p1-miniapp-core",
            "P1 小程序核心闭环",
            [
                feature_check(
                    "小程序主要页面与登录入口",
                    [
                        check_exists(root, "wechat-miniprogram/pages/home/index.js"),
                        check_exists(root, "wechat-miniprogram/pages/discover/index.js"),
                        check_exists(root, "wechat-miniprogram/pages/publish/index.js"),
                        check_exists(root, "wechat-miniprogram/pages/booking/index.js"),
                        check_exists(root, "wechat-miniprogram/pages/me/index.js"),
                        check_file(root, "server.py", ["/auth/wechat-mini-login"]),
                    ],
                ),
                feature_check(
                    "小程序生产检查与域名清单",
                    [
                        check_file(root, "package.json", ['"check:miniapp"', '"check:wechat-domains"']),
                        check_exists(root, "scripts/check_miniprogram.py"),
                        check_exists(root, "scripts/wechat_domain_manifest.py"),
                    ],
                ),
            ],
        ),
        phase(
            "p1-provider-booking",
            "P1 教练与健身房预约能力",
            [
                feature_check(
                    "教练/健身房发布可预约时间与订单可见",
                    [
                        check_file(root, "server.py", ["/availability/create", "/availability/delete", "/booking/create"]),
                        check_file(root, "app.js", ["/availability/create", "/availability/delete", "/booking/create"]),
                        check_file(root, "tests/api/test_booking.py", ["booking_surfaces_for_both_outgoing_and_incoming_sides"]),
                    ],
                ),
            ],
        ),
        phase(
            "p1-safety-ops",
            "P1 内容安全、举报与运营后台",
            [
                feature_check(
                    "举报、审核队列与管理员接口",
                    [
                        check_file(root, "server.py", ["/report/create", "/admin/moderation", "/admin/moderation/resolve", "review_media_safety", "media-upload"]),
                        check_file(root, "tests/api/test_content.py", ["risky_post_comment_and_message_are_queued_for_moderation", "risky_media_upload_is_queued_for_moderation", "user_report_is_persisted_and_admin_endpoint_is_protected"]),
                    ],
                ),
                feature_check(
                    "运营审核后台页面",
                    [
                        check_exists(root, "admin.html"),
                        check_exists(root, "admin.css"),
                        check_exists(root, "admin.js"),
                        check_file(root, "server.py", ["/admin/profile/moderation", "/admin/content/moderation", "ensure_profile_not_suspended"]),
                        check_file(root, "scripts/deploy_tencent_static.py", ["admin.html", "admin.js"]),
                        check_file(root, "tests/api/test_content.py", ["admin_can_suspend_and_restore_reported_profile", "admin_can_hide_and_restore_reported_post"]),
                        check_file(root, "tests/e2e/admin.spec.js", ["运营审核后台可以查看并处理媒体风险队列", "运营审核后台可以限制并恢复风险内容作者", "运营审核后台可以隐藏并恢复风险动态"]),
                    ],
                ),
                feature_check(
                    "拉黑与账号删除",
                    [
                        check_file(root, "server.py", ["/block/toggle", "/account/delete-request"]),
                        check_file(root, "tests/api/test_content.py", ["private_message_does_not_require_follow_but_respects_block"]),
                        check_file(root, "tests/api/test_auth.py", ["account_deletion_request"]),
                    ],
                ),
            ],
        ),
        phase(
            "p2-observability",
            "P2 生产监控与问题定位",
            [
                feature_check(
                    "慢接口、前端错误与媒体上传失败监控",
                    [
                        check_file(root, "server.py", ["/monitor/event", "/admin/monitor", "monitorEvents"]),
                        check_file(root, "app.js", ["api-slow", "frontend-error", "media-upload-failed"]),
                        check_file(
                            root,
                            "tests/api/test_monitoring.py",
                            [
                                "monitor_event_endpoint_records_sanitized_event_and_requires_admin_token",
                                "monitor_events_are_capped_and_classified",
                            ],
                        ),
                    ],
                ),
            ],
        ),
        phase(
            "p2-launch-runbook",
            "P2 上线执行计划与证据",
            [
                feature_check(
                    "腾讯云上线计划、微信域名清单与最终证据",
                    [
                        check_file(root, "package.json", ['"plan:tencent-launch"', '"evidence:tencent-launch"']),
                        check_file(root, "scripts/tencent_launch_plan.py", ["wechatDomains", "manualChecks", "request 合法域名", "downloadFile 合法域名", "每日生产快照计划"]),
                        check_file(root, "deploy/tencent-cloud/launch-plan.example.json", ["mediaOrigin", "miniappAppId", "cosSecretId", "mediaMaintenanceToken"]),
                        check_file(root, "docs/fithub-release-runbook.md", ["微信公众平台后台配置", "发布前人工核对", "每日生产快照"]),
                    ],
                ),
            ],
        ),
    ]


def build_report(
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
    launch_report = tencent_launch_gate.build_gate(
        root=root,
        env_file=Path(env_file),
        api_origin=api_origin,
        web_origin=web_origin,
        media_origin=media_origin,
        expected_ip=expected_ip,
        check_domain_network=check_domain_network,
        check_acme=check_acme,
        check_tls=check_tls,
        check_live=check_live,
        require_cos_media=require_cos_media,
    )
    launch_blockers = [
        f"{item.get('label')}: {item.get('detail')}"
        for item in launch_report.get("phases", [])
        if not item.get("ready")
    ]
    production_detail = "已通过" if launch_report["ready"] else "；".join(launch_blockers[:3]) or f"{launch_report['blockerCount']} 个上线阻断阶段未通过"
    production_phase = {
        "name": "p0-domestic-production",
        "label": "P0 国内生产链路",
        "ready": bool(launch_report["ready"]),
        "detail": production_detail,
        "payload": launch_report,
    }
    phases = [production_phase, *build_feature_phases(root)]
    blockers = [item for item in phases if not item["ready"]]
    return {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "ready" if not blockers else "blocked",
        "ready": not blockers,
        "blockerCount": len(blockers),
        "phases": phases,
        "nextSteps": launch_report.get("nextSteps") or [],
    }


def render_markdown(report: dict[str, Any]) -> str:
    status = report.get("status") or report.get("overallStatus") or ("ready" if report.get("ready") else "blocked")
    blocker_count = int(report.get("blockerCount") or 0)
    lines = [
        "# FitHub 上架前大升级总门禁",
        "",
        f"- 生成时间：{report['generatedAt']}",
        f"- 状态：{status}",
        f"- 阻断阶段数：{blocker_count}",
        "",
    ]
    for item in report["phases"]:
        mark = "OK" if item["ready"] else "BLOCKED"
        lines.append(f"- [{mark}] {item['label']}：{item['detail']}")
        nested_blockers = [
            f"{phase.get('label')}：{phase.get('detail')}"
            for phase in (item.get("payload") or {}).get("phases", [])
            if not phase.get("ready")
        ]
        for nested in nested_blockers[:5]:
            lines.append(f"  - {nested}")
    lines.append("")
    if bool(report.get("ready")):
        lines.append("结论：上架前总门禁通过，可以进入真机全量验收和提审准备。")
    else:
        lines.append(f"结论：还有 {blocker_count} 个阶段未通过，不要提交小程序审核或面向正式用户发布。")
        next_steps = list(report.get("nextSteps") or [])
        if next_steps:
            lines.extend(["", "下一步建议："])
            for index, step in enumerate(next_steps, start=1):
                lines.append(f"{index}. {step}")
    lines.append("")
    return "\n".join(lines)


def print_markdown(report: dict[str, Any]) -> None:
    print(render_markdown(report), end="")


def report_stem(report: dict[str, Any]) -> str:
    timestamp = str(report.get("generatedAt") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    safe_timestamp = timestamp.replace("-", "").replace(":", "").replace("T", "-").replace("Z", "Z")
    return f"fithub-prelaunch-gate-{safe_timestamp}"


def write_outputs(report: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = report_stem(report)
    markdown_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"markdown": str(markdown_path), "json": str(json_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the FitHub prelaunch product and production readiness gate.")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--env-file", default=str(TENCENT_ENV))
    parser.add_argument("--api-origin", default="")
    parser.add_argument("--web-origin", default="")
    parser.add_argument("--media-origin", default="")
    parser.add_argument("--expected-ip", default="")
    parser.add_argument("--check-domain-network", action="store_true")
    parser.add_argument("--check-acme", action="store_true")
    parser.add_argument("--check-tls", action="store_true")
    parser.add_argument("--check-live", action="store_true")
    parser.add_argument("--allow-non-cos-media", action="store_true")
    parser.add_argument("--output-dir", default="", help="Write markdown and JSON reports to this directory.")
    parser.add_argument("--soft-fail", action="store_true", help="Always exit 0 after writing/printing the report.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = build_report(
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
        print(f"FitHub prelaunch gate failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_markdown(report)
    if args.output_dir:
        paths = write_outputs(report, Path(args.output_dir))
        print(f"\n报告已写入：{paths['markdown']}")
        print(f"JSON 已写入：{paths['json']}")
    if args.soft_fail:
        return 0
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
