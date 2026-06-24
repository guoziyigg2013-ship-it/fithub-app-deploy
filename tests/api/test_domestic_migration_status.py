import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STATUS_PATH = ROOT / "scripts" / "domestic_migration_status.py"
SPEC = importlib.util.spec_from_file_location("domestic_migration_status", STATUS_PATH)
domestic_migration_status = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(domestic_migration_status)


def write_app(root: Path, *, api_origin: str, api_base: str, appid: str) -> None:
    (root / "wechat-miniprogram").mkdir(parents=True, exist_ok=True)
    (root / "config.js").write_text(
        f'window.__FITHUB_CONFIG__ = {{ apiOrigin: "{api_origin}" }};\n',
        encoding="utf-8",
    )
    (root / "wechat-miniprogram" / "config.js").write_text(
        f'module.exports = {{ apiBase: "{api_base}" }};\n',
        encoding="utf-8",
    )
    (root / "wechat-miniprogram" / "project.config.json").write_text(
        '{"appid": "' + appid + '", "projectname": "fithub-miniprogram"}\n',
        encoding="utf-8",
    )


def write_cos_env(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "PORT=10000",
                "FITHUB_URL_PREFIX=/",
                "FITHUB_DATA_DIR=/data/fithub",
                "FITHUB_PUBLIC_API_ORIGIN=https://api.fithub.example.cn",
                "SUPABASE_URL=https://abcdefghijklmnopqrst.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY=" + "s" * 80,
                "FITHUB_SUPABASE_TABLE=fithub_app_state",
                "FITHUB_SUPABASE_ROW_ID=primary",
                "FITHUB_ADMIN_TOKEN=" + "a" * 32,
                "FITHUB_MEDIA_MAINTENANCE_TOKEN=" + "b" * 32,
                "FITHUB_MEDIA_STORAGE_PROVIDER=cos",
                "FITHUB_MEDIA_BUCKET=fithub-media",
                "FITHUB_TENCENT_COS_SECRET_ID=AKIDEXAMPLE",
                "FITHUB_TENCENT_COS_SECRET_KEY=cos-secret-key-example",
                "FITHUB_TENCENT_COS_REGION=ap-guangzhou",
                "FITHUB_TENCENT_COS_BUCKET=fithub-media-1250000000",
                "FITHUB_TENCENT_COS_PUBLIC_BASE_URL=https://media.fithub.example.cn",
                "FITHUB_IMAGE_UPLOAD_LIMIT_BYTES=10485760",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class DomesticMigrationStatusTests(unittest.TestCase):
    def test_report_blocks_render_touristappid_and_missing_env(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_app(
                root,
                api_origin="https://fithub-app-1btg.onrender.com",
                api_base="https://fithub-app-1btg.onrender.com/api",
                appid="touristappid",
            )

            report = domestic_migration_status.build_report(
                root=root,
                env_file=root / "deploy" / "tencent-cloud" / ".env.production",
            )

        self.assertFalse(report["ready"])
        self.assertGreaterEqual(report["blockerCount"], 4)
        details = "\n".join(str(item["detail"]) for item in report["items"])
        self.assertIn("onrender.com", details)
        self.assertIn("touristappid", details)
        next_steps = "\n".join(report["nextSteps"])
        self.assertIn("cutover:tencent", next_steps)
        self.assertIn("init:tencent-env", next_steps)
        self.assertIn("check:tencent-domains", next_steps)

    def test_report_passes_ready_static_configs_and_cos_env(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_app(
                root,
                api_origin="https://api.fithub.example.cn",
                api_base="https://api.fithub.example.cn/api",
                appid="wx1234567890abcdef",
            )
            env_file = root / "deploy" / "tencent-cloud" / ".env.production"
            write_cos_env(env_file)

            report = domestic_migration_status.build_report(root=root, env_file=env_file)

        self.assertTrue(report["ready"])
        self.assertEqual(report["blockerCount"], 0)
        self.assertEqual(report["nextSteps"], [])


if __name__ == "__main__":
    unittest.main()
