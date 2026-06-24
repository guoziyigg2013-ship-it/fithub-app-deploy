import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "scripts" / "trial_readiness_gate.py"
SPEC = importlib.util.spec_from_file_location("trial_readiness_gate", GATE_PATH)
trial_readiness_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trial_readiness_gate)


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_feature_inventory(root: Path, *, appid: str = "touristappid") -> None:
    write(root / "config.js", 'window.__FITHUB_CONFIG__ = { apiOrigin: "https://api.example.cn" };\n')
    write(root / "wechat-miniprogram" / "config.js", 'module.exports = { apiBase: "https://api.example.cn/api" };\n')
    write(root / "wechat-miniprogram" / "project.config.json", f'{{"appid": "{appid}"}}\n')
    write(
        root / "package.json",
        '{"scripts":{"snapshot:prod":"python3 scripts/production_snapshot.py","test:api":"python3 -m unittest","check:miniapp":"python3 scripts/check_miniprogram.py","check:wechat-domains":"python3 scripts/wechat_domain_manifest.py"}}',
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
                "/block/toggle",
                "/account/delete-request",
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
            ]
        ),
    )
    write(root / "scripts" / "production_snapshot.py")
    write(root / "scripts" / "check_miniprogram.py")
    write(root / "scripts" / "wechat_domain_manifest.py")
    write(root / "tests" / "api" / "test_persistence.py", "production_snapshot_metric_comparison_rejects_regressions")
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
                "user_report_is_persisted_and_admin_endpoint_is_protected",
                "private_message_does_not_require_follow_but_respects_block",
            ]
        ),
    )
    write(root / "tests" / "api" / "test_tencent_cos_media.py", "upload_media_asset_uses_cos_provider_and_public_url")
    write(root / "tests" / "api" / "test_auth.py", "account_deletion_request")
    for rel in [
        "wechat-miniprogram/pages/home/index.js",
        "wechat-miniprogram/pages/discover/index.js",
        "wechat-miniprogram/pages/booking/index.js",
        "wechat-miniprogram/pages/me/index.js",
    ]:
        write(root / rel)
    write(root / "wechat-miniprogram/pages/publish/index.js", "chooseMedia\n/media/upload-file")
    write(root / "wechat-miniprogram/utils/api.js", "wx.uploadFile")


class TrialReadinessGateTests(unittest.TestCase):
    def test_trial_gate_passes_current_runtime_without_formal_appid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_feature_inventory(root)
            with (
                mock.patch.object(
                    trial_readiness_gate,
                    "phase_frontend",
                    return_value=trial_readiness_gate.phase("trial-fixed-frontend", "前端", True, "ok"),
                ),
                mock.patch.object(
                    trial_readiness_gate,
                    "phase_backend",
                    return_value=trial_readiness_gate.phase("trial-cloudbase-api", "后端", True, "ok"),
                ),
            ):
                report = trial_readiness_gate.build_report(
                    root=root,
                    frontend_url="https://app.example.cn/fithub/",
                    backend_url="https://api.example.cn",
                )

        self.assertTrue(report["ready"])
        self.assertEqual(report["blockerCount"], 0)
        self.assertIn("替换真实微信小程序 AppID", "\n".join(report["formalPrelaunchPending"]))

    def test_trial_gate_blocks_when_feature_inventory_is_incomplete(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_feature_inventory(root)
            (root / "wechat-miniprogram" / "utils" / "api.js").write_text("wx.request", encoding="utf-8")
            with (
                mock.patch.object(
                    trial_readiness_gate,
                    "phase_frontend",
                    return_value=trial_readiness_gate.phase("trial-fixed-frontend", "前端", True, "ok"),
                ),
                mock.patch.object(
                    trial_readiness_gate,
                    "phase_backend",
                    return_value=trial_readiness_gate.phase("trial-cloudbase-api", "后端", True, "ok"),
                ),
            ):
                report = trial_readiness_gate.build_report(
                    root=root,
                    frontend_url="https://app.example.cn/fithub/",
                    backend_url="https://api.example.cn",
                )

        self.assertFalse(report["ready"])
        inventory = next(item for item in report["phases"] if item["name"] == "trial-feature-inventory")
        self.assertFalse(inventory["ready"])
        self.assertIn("wx.uploadFile", inventory["detail"])

    def test_render_markdown_separates_trial_result_from_formal_pending_items(self):
        report = {
            "generatedAt": "2026-06-24T10:00:00Z",
            "status": "ready",
            "ready": True,
            "frontendUrl": "https://app.example.cn/fithub/",
            "backendUrl": "https://api.example.cn",
            "blockerCount": 0,
            "phases": [
                {
                    "name": "trial-fixed-frontend",
                    "label": "腾讯云固定试运行入口",
                    "ready": True,
                    "detail": "ok",
                }
            ],
            "formalPrelaunchPending": ["替换真实微信小程序 AppID"],
        }

        markdown = trial_readiness_gate.render_markdown(report)

        self.assertIn("腾讯云固定试运行入口可继续给测试用户使用", markdown)
        self.assertIn("正式提审前仍需完成", markdown)
        self.assertIn("替换真实微信小程序 AppID", markdown)

    def test_backend_phase_accepts_plain_text_healthz(self):
        storage_payload = {
            "status": "ok",
            "storage": {
                "remoteConfigured": True,
                "loadedFrom": "cloudbase",
                "remoteWriteProtected": False,
                "remoteWritable": True,
            },
            "metrics": {"real_profiles": 1},
            "media": {"storageProvider": "inline"},
        }
        bootstrap_payload = {"profiles": [{"id": "p1"}]}
        with (
            mock.patch.object(
                trial_readiness_gate.deploy_smoke,
                "fetch_text_with_retries",
                return_value=(200, "ok", 0.1),
            ),
            mock.patch.object(
                trial_readiness_gate.deploy_smoke,
                "fetch_json",
                side_effect=[(200, storage_payload, 0.2), (200, bootstrap_payload, 0.3)],
            ),
        ):
            result = trial_readiness_gate.phase_backend(
                "https://api.example.cn",
                min_real_profiles=0,
                require_cos_media=False,
            )

        self.assertTrue(result["ready"])
        self.assertEqual(result["payload"]["health"], "ok")


if __name__ == "__main__":
    unittest.main()
