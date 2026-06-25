import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "scripts" / "prelaunch_gate.py"
SPEC = importlib.util.spec_from_file_location("prelaunch_gate", GATE_PATH)
prelaunch_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prelaunch_gate)


READY_LAUNCH_REPORT = {
    "ready": True,
    "blockerCount": 0,
    "nextSteps": [],
    "phases": [],
}


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_minimal_configs(root: Path) -> None:
    write(root / "config.js", 'window.__FITHUB_CONFIG__ = { apiOrigin: "https://api.fithub.example.cn" };\n')
    write(root / "wechat-miniprogram" / "config.js", 'module.exports = { apiBase: "https://api.fithub.example.cn/api" };\n')
    write(root / "wechat-miniprogram" / "project.config.json", '{"appid": "wx1234567890abcdef"}\n')


def write_feature_inventory(root: Path, *, include_upload_file: bool = True) -> None:
    write_minimal_configs(root)
    write(
        root / "package.json",
        '{"scripts":{"snapshot:prod":"python3 scripts/production_snapshot.py","test:api":"python3 -m unittest","check:miniapp":"python3 scripts/check_miniprogram.py","check:wechat-domains":"python3 scripts/wechat_domain_manifest.py","plan:tencent-launch":"python3 scripts/tencent_launch_plan.py","evidence:tencent-launch":"python3 scripts/tencent_launch_evidence.py"}}',
    )
    write(
        root / "server.py",
        "\n".join(
            [
                "/auth/restore",
                "/auth/restore-follows",
                "/auth/logout",
                "FITHUB_MEDIA_STORAGE_PROVIDER",
                "media/upload-file",
                "thumbnail",
                "/auth/wechat-mini-login",
                "/availability/create",
                "/availability/delete",
                "/booking/create",
                "/report/create",
                "/admin/moderation",
                "/admin/moderation/resolve",
                "/admin/profile/moderation",
                "/admin/content/moderation",
                "ensure_profile_not_suspended",
                "review_media_safety",
                "media-upload",
                "/block/toggle",
                "/account/delete-request",
                "/monitor/event",
                "/admin/monitor",
                "monitorEvents",
            ]
        ),
    )
    write(
        root / "app.js",
        "\n".join(
            [
                "/auth/restore",
                "/auth/restore-follows",
                "/auth/logout",
                "postWithoutStateSync(`${API_BASE}/follow/toggle`",
                "postWithoutStateSync(`${API_BASE}/post/like`",
                "postWithoutStateSync(`${API_BASE}/post/favorite-toggle`",
                "postWithoutStateSync(`${API_BASE}/message/send`",
                "/availability/create",
                "/availability/delete",
                "/booking/create",
                "api-slow",
                "frontend-error",
                "media-upload-failed",
            ]
        ),
    )
    write(root / "scripts" / "production_snapshot.py", "write_manifest\nprune_snapshots")
    write(root / "scripts" / "check_miniprogram.py", "validate_discover_instant_interactions")
    write(root / "scripts" / "wechat_domain_manifest.py")
    write(root / "scripts" / "deploy_tencent_static.py", "admin.html\nadmin.js")
    write(root / "scripts" / "tencent_launch_plan.py", "wechatDomains\nmanualChecks\nrequest 合法域名\ndownloadFile 合法域名\n每日生产快照计划")
    write(root / "deploy" / "tencent-cloud" / "launch-plan.example.json", "mediaOrigin\nminiappAppId\ncosSecretId\nmediaMaintenanceToken")
    write(root / "docs" / "fithub-release-runbook.md", "微信公众平台后台配置\n发布前人工核对\n每日生产快照")
    write(
        root / "tests" / "api" / "test_persistence.py",
        "\n".join(
            [
                "production_snapshot_metric_comparison_rejects_regressions",
                "production_snapshot_manifest_records_local_backups",
                "production_snapshot_prune_keeps_recent_and_latest_files",
            ]
        ),
    )
    write(root / "tests" / "api" / "test_social.py", "follow_state_survives_login_and_server_restart\nmulti_identity_threads_are_scoped_to_current_identity")
    write(root / "tests" / "api" / "test_booking.py", "multi_identity_bookings_are_scoped_to_current_identity\nbooking_surfaces_for_both_outgoing_and_incoming_sides")
    write(
        root / "tests" / "api" / "test_content.py",
        "\n".join(
            [
                "multipart_media_upload_returns_reusable_asset_payload",
                "video_post_persists_thumbnail",
                "like_favorite_comment_and_notifications_surface",
                "risky_post_comment_and_message_are_queued_for_moderation",
                "risky_media_upload_is_queued_for_moderation",
                "user_report_is_persisted_and_admin_endpoint_is_protected",
                "admin_can_suspend_and_restore_reported_profile",
                "admin_can_hide_and_restore_reported_post",
                "admin_can_soft_delete_and_restore_reported_post",
                "private_message_does_not_require_follow_but_respects_block",
            ]
        ),
    )
    write(root / "tests" / "api" / "test_tencent_cos_media.py", "upload_media_asset_uses_cos_provider_and_public_url")
    write(root / "tests" / "api" / "test_auth.py", "account_deletion_request")
    write(root / "tests" / "e2e" / "admin.spec.js", "运营审核后台可以查看并处理媒体风险队列\n运营审核后台可以限制并恢复风险内容作者\n运营审核后台可以隐藏并恢复风险动态\n运营审核后台可以下架归档并恢复风险动态")
    write(
        root / "tests" / "api" / "test_monitoring.py",
        "monitor_event_endpoint_records_sanitized_event_and_requires_admin_token\nmonitor_events_are_capped_and_classified",
    )
    write(root / "tests" / "api" / "test_check_miniprogram.py", "discover_instant_interactions_rejects_full_reload_after_tap")
    for rel in ["admin.html", "admin.css", "admin.js"]:
        write(root / rel)
    for rel in [
        "wechat-miniprogram/pages/home/index.js",
        "wechat-miniprogram/pages/discover/index.js",
        "wechat-miniprogram/pages/booking/index.js",
        "wechat-miniprogram/pages/me/index.js",
    ]:
        write(root / rel)
    write(
        root / "wechat-miniprogram/pages/discover/index.js",
        "applyOptimisticPostMutation\nmergeConfirmedPost\ndesiredFollowing: true\nfavoritedByCurrentActor",
    )
    write(root / "wechat-miniprogram/pages/publish/index.js", "chooseMedia\n/media/upload-file")
    write(root / "wechat-miniprogram/utils/api.js", "wx.uploadFile" if include_upload_file else "wx.request")


class PrelaunchGateTests(unittest.TestCase):
    def test_current_prelaunch_shape_is_blocked_by_production_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write(root / "config.js", 'window.__FITHUB_CONFIG__ = { apiOrigin: "https://fithub-app-1btg.onrender.com" };\n')
            write(root / "wechat-miniprogram" / "config.js", 'module.exports = { apiBase: "https://fithub-app-1btg.onrender.com/api" };\n')
            write(root / "wechat-miniprogram" / "project.config.json", '{"appid": "touristappid"}\n')

            report = prelaunch_gate.build_report(
                root=root,
                env_file=root / "deploy" / "tencent-cloud" / ".env.production",
            )

        self.assertFalse(report["ready"])
        self.assertGreaterEqual(report["blockerCount"], 1)
        self.assertEqual(report["phases"][0]["name"], "p0-domestic-production")
        self.assertFalse(report["phases"][0]["ready"])
        self.assertIn("国内生产配置", report["phases"][0]["detail"])

    def test_ready_launch_and_feature_inventory_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_feature_inventory(root)

            with mock.patch.object(prelaunch_gate.tencent_launch_gate, "build_gate", return_value=READY_LAUNCH_REPORT):
                report = prelaunch_gate.build_report(root=root)

        self.assertTrue(report["ready"])
        self.assertEqual(report["blockerCount"], 0)

    def test_missing_miniapp_file_upload_blocks_media_phase(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_feature_inventory(root, include_upload_file=False)

            with mock.patch.object(prelaunch_gate.tencent_launch_gate, "build_gate", return_value=READY_LAUNCH_REPORT):
                report = prelaunch_gate.build_report(root=root)

        self.assertFalse(report["ready"])
        media_phase = next(item for item in report["phases"] if item["name"] == "p0-media-production")
        self.assertFalse(media_phase["ready"])
        self.assertIn("wx.uploadFile", media_phase["detail"])

    def test_write_outputs_creates_markdown_and_json_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "reports"
            report = {
                "generatedAt": "2026-06-24T09:40:00Z",
                "status": "blocked",
                "ready": False,
                "blockerCount": 1,
                "phases": [
                    {
                        "name": "p0-domestic-production",
                        "label": "P0 国内生产链路",
                        "ready": False,
                        "detail": "API 仍是 Render",
                    }
                ],
                "nextSteps": ["切换到腾讯云 API"],
            }

            paths = prelaunch_gate.write_outputs(report, output_dir)

            markdown = Path(paths["markdown"]).read_text(encoding="utf-8")
            payload = Path(paths["json"]).read_text(encoding="utf-8")

        self.assertIn("FitHub 上架前大升级总门禁", markdown)
        self.assertIn("[BLOCKED] P0 国内生产链路", markdown)
        self.assertIn("切换到腾讯云 API", markdown)
        self.assertIn('"status": "blocked"', payload)

    def test_markdown_includes_nested_launch_blockers(self):
        report = {
            "generatedAt": "2026-06-24T09:40:00Z",
            "status": "blocked",
            "ready": False,
            "blockerCount": 1,
            "phases": [
                {
                    "name": "p0-domestic-production",
                    "label": "P0 国内生产链路",
                    "ready": False,
                    "detail": "国内生产配置: 当前 AppID=touristappid",
                    "payload": {
                        "phases": [
                            {
                                "label": "国内生产配置",
                                "ready": False,
                                "detail": "当前 AppID=touristappid",
                            },
                            {
                                "label": "固定域名输入",
                                "ready": True,
                                "detail": "已通过",
                            },
                        ]
                    },
                }
            ],
            "nextSteps": ["替换真实 AppID"],
        }

        markdown = prelaunch_gate.render_markdown(report)

        self.assertIn("国内生产配置：当前 AppID=touristappid", markdown)
        self.assertNotIn("固定域名输入：已通过", markdown)


if __name__ == "__main__":
    unittest.main()
