import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = ROOT / "scripts" / "tencent_launch_evidence.py"
SPEC = importlib.util.spec_from_file_location("tencent_launch_evidence", EVIDENCE_PATH)
tencent_launch_evidence = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tencent_launch_evidence)


class TencentLaunchEvidenceTests(unittest.TestCase):
    def test_render_markdown_includes_domains_release_and_blockers(self):
        evidence = {
            "generatedAt": "2026-06-24T00:00:00Z",
            "git": {"branch": "main", "shortCommit": "abc1234", "dirty": False},
            "urls": {
                "frontend": "https://app.fithub.example.cn/",
                "backend": "https://api.fithub.example.cn",
                "configuredWebApiOrigin": "https://api.fithub.example.cn",
                "configuredMiniappApiBase": "https://api.fithub.example.cn/api",
                "miniappAppId": "wx1234567890abcdef",
            },
            "release": {"present": True, "path": "/tmp/release.tar.gz", "sha256": "sha256-demo", "sizeBytes": 123},
            "snapshot": {"present": True, "path": "/tmp/snapshot.json", "metrics": {"real_profiles": 9, "real_follows": 3}},
            "domesticMigration": {
                "status": "blocked",
                "blockerCount": 1,
                "ready": False,
                "items": [{"label": "小程序 AppID", "ok": False, "detail": "touristappid"}],
            },
        }

        markdown = tencent_launch_evidence.render_markdown(evidence)

        self.assertIn("https://app.fithub.example.cn/", markdown)
        self.assertIn("sha256-demo", markdown)
        self.assertIn("[BLOCKED] 小程序 AppID", markdown)
        self.assertIn("real_profiles: 9", markdown)

    def test_write_outputs_creates_markdown_and_json(self):
        evidence = {
            "generatedAt": "2026-06-24T00:00:00Z",
            "git": {"branch": "main", "shortCommit": "abc1234", "dirty": False},
            "urls": {
                "frontend": "",
                "backend": "",
                "configuredWebApiOrigin": "",
                "configuredMiniappApiBase": "",
                "miniappAppId": "",
            },
            "release": {"present": False, "path": "", "sha256": "", "sizeBytes": 0},
            "snapshot": {"present": False, "path": "", "metrics": {}},
            "domesticMigration": {"status": "blocked", "blockerCount": 0, "ready": False, "items": []},
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_path, json_path = tencent_launch_evidence.write_outputs(evidence, Path(temp_dir))

            self.assertTrue(markdown_path.exists())
            self.assertTrue(json_path.exists())
            self.assertIn("FitHub 腾讯云国内上线证据报告", markdown_path.read_text(encoding="utf-8"))

    def test_build_evidence_records_release_sha_and_snapshot_metrics(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive = root / "release.tar.gz"
            archive.write_bytes(b"release")
            snapshot = root / "snapshot.json"
            snapshot.write_text('{"metrics": {"real_profiles": 2, "real_follows": 1}}', encoding="utf-8")

            with mock.patch.object(
                tencent_launch_evidence.domestic_migration_status,
                "read_configs",
                return_value={
                    "webApiOrigin": "https://api.fithub.example.cn",
                    "miniappApiBase": "https://api.fithub.example.cn/api",
                    "miniappAppId": "wx1234567890abcdef",
                },
            ), mock.patch.object(
                tencent_launch_evidence.domestic_migration_status,
                "build_report",
                return_value={"status": "ready", "ready": True, "blockerCount": 0, "items": []},
            ), mock.patch.object(tencent_launch_evidence, "run_git", return_value="abc1234"):
                evidence = tencent_launch_evidence.build_evidence(
                    frontend_url="https://app.fithub.example.cn",
                    backend_url="https://api.fithub.example.cn",
                    release_archive=archive,
                    snapshot_path=snapshot,
                )

        self.assertTrue(evidence["release"]["present"])
        self.assertEqual(evidence["snapshot"]["metrics"]["real_profiles"], 2)
        self.assertEqual(evidence["domesticMigration"]["status"], "ready")


if __name__ == "__main__":
    unittest.main()
