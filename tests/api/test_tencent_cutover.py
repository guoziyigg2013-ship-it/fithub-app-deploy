import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CUTOVER_PATH = ROOT / "scripts" / "tencent_cutover.py"
SPEC = importlib.util.spec_from_file_location("tencent_cutover", CUTOVER_PATH)
tencent_cutover = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tencent_cutover)


def write_minimal_repo(root: Path) -> None:
    (root / "wechat-miniprogram").mkdir(parents=True)
    (root / "config.js").write_text(
        'window.__FITHUB_CONFIG__ = { apiOrigin: "https://fithub-app-1btg.onrender.com" };\n',
        encoding="utf-8",
    )
    (root / "wechat-miniprogram" / "config.js").write_text(
        'module.exports = { apiBase: "https://fithub-app-1btg.onrender.com/api" };\n',
        encoding="utf-8",
    )
    (root / "wechat-miniprogram" / "project.config.json").write_text(
        json.dumps({"appid": "touristappid", "projectname": "fithub-miniprogram"}, indent=2) + "\n",
        encoding="utf-8",
    )


class TencentCutoverTests(unittest.TestCase):
    def test_rejects_render_api_origin(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_repo(root)

            with self.assertRaisesRegex(ValueError, "临时域名"):
                tencent_cutover.run_cutover(
                    root=root,
                    api_origin="https://fithub-app-1btg.onrender.com",
                    miniapp_appid="wx1234567890abcdef",
                    state_provider="supabase",
                    supabase_url="https://abcdefghijklmnopqrst.supabase.co",
                    supabase_service_role_key="s" * 80,
                    skip_release=True,
                )

    def test_dry_run_does_not_modify_configs_or_write_env(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_repo(root)
            web_before = (root / "config.js").read_text(encoding="utf-8")
            env_output = root / "deploy" / "tencent-cloud" / ".env.production"

            result = tencent_cutover.run_cutover(
                root=root,
                api_origin="https://api.fithub.example.cn",
                web_origin="https://app.fithub.example.cn",
                miniapp_appid="wx1234567890abcdef",
                state_provider="supabase",
                supabase_url="https://abcdefghijklmnopqrst.supabase.co",
                supabase_service_role_key="s" * 80,
                write_env=True,
                env_output=env_output,
                skip_release=True,
            )

            self.assertEqual(result.api_origin, "https://api.fithub.example.cn")
            self.assertEqual((root / "config.js").read_text(encoding="utf-8"), web_before)
            self.assertFalse(env_output.exists())

    def test_apply_updates_configs_and_writes_tencent_runtime_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_repo(root)
            env_output = root / "deploy" / "tencent-cloud" / ".env.production"
            nginx_output = root / "deploy" / "tencent-cloud" / "nginx-fithub.conf"

            result = tencent_cutover.run_cutover(
                root=root,
                api_origin="https://api.fithub.example.cn",
                web_origin="https://app.fithub.example.cn",
                miniapp_appid="wx1234567890abcdef",
                state_provider="supabase",
                supabase_url="https://abcdefghijklmnopqrst.supabase.co",
                supabase_service_role_key="s" * 80,
                admin_token="a" * 32,
                media_maintenance_token="b" * 32,
                apply=True,
                write_env=True,
                env_output=env_output,
                nginx_output=nginx_output,
                skip_release=True,
            )

            self.assertIn('apiOrigin: "https://api.fithub.example.cn"', (root / "config.js").read_text())
            self.assertIn('apiBase: "https://api.fithub.example.cn/api"', (root / "wechat-miniprogram" / "config.js").read_text())
            project = json.loads((root / "wechat-miniprogram" / "project.config.json").read_text())
            self.assertEqual(project["appid"], "wx1234567890abcdef")
            self.assertIn("FITHUB_PUBLIC_API_ORIGIN=https://api.fithub.example.cn", env_output.read_text())
            self.assertIn("server_name api.fithub.example.cn app.fithub.example.cn;", nginx_output.read_text())
            self.assertEqual(result.archive_path, None)


if __name__ == "__main__":
    unittest.main()
