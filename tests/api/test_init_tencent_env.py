import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INIT_PATH = ROOT / "scripts" / "init_tencent_env.py"
PREFLIGHT_PATH = ROOT / "scripts" / "tencent_cloud_preflight.py"

INIT_SPEC = importlib.util.spec_from_file_location("init_tencent_env", INIT_PATH)
init_tencent_env = importlib.util.module_from_spec(INIT_SPEC)
INIT_SPEC.loader.exec_module(init_tencent_env)

PREFLIGHT_SPEC = importlib.util.spec_from_file_location("tencent_cloud_preflight", PREFLIGHT_PATH)
tencent_cloud_preflight = importlib.util.module_from_spec(PREFLIGHT_SPEC)
PREFLIGHT_SPEC.loader.exec_module(tencent_cloud_preflight)


class InitTencentEnvTests(unittest.TestCase):
    def test_build_env_values_generates_valid_tokens_and_passes_preflight(self):
        values = init_tencent_env.build_env_values(
            api_origin="https://api.fithub.example.cn",
            state_provider="supabase",
            supabase_url="https://abcdefghijklmnopqrst.supabase.co",
            supabase_service_role_key="s" * 80,
        )
        failures = []

        tencent_cloud_preflight.validate_env(values, failures)

        self.assertEqual(failures, [])
        self.assertGreaterEqual(len(values["FITHUB_ADMIN_TOKEN"]), 24)
        self.assertGreaterEqual(len(values["FITHUB_MEDIA_MAINTENANCE_TOKEN"]), 24)

    def test_build_env_values_rejects_placeholder_api_origin(self):
        with self.assertRaisesRegex(ValueError, "placeholder|FITHUB_PUBLIC_API_ORIGIN"):
            init_tencent_env.build_env_values(
                api_origin="https://api.yourdomain.com",
                state_provider="supabase",
                supabase_url="https://abcdefghijklmnopqrst.supabase.co",
                supabase_service_role_key="s" * 80,
            )

    def test_build_env_values_accepts_cloudbase_state_storage(self):
        values = init_tencent_env.build_env_values(
            api_origin="https://api.fithub.example.cn",
            cloudbase_env_id="zhangxin-zhinan-d4fwtsmr9a834d58",
            cloudbase_api_key="cloudbase-api-key-example",
        )
        failures = []

        tencent_cloud_preflight.validate_env(values, failures)

        self.assertEqual(failures, [])
        self.assertEqual(values["FITHUB_STATE_STORAGE_PROVIDER"], "cloudbase")
        self.assertEqual(values["FITHUB_CLOUDBASE_COLLECTION"], "fithub_app_state")

    def test_build_env_values_accepts_tencent_cos_media_storage(self):
        values = init_tencent_env.build_env_values(
            api_origin="https://api.fithub.example.cn",
            state_provider="supabase",
            supabase_url="https://abcdefghijklmnopqrst.supabase.co",
            supabase_service_role_key="s" * 80,
            media_storage_provider="cos",
            cos_secret_id="AKIDEXAMPLE",
            cos_secret_key="cos-secret-key-example",
            cos_region="ap-guangzhou",
            cos_bucket="fithub-media-1250000000",
            cos_public_base_url="https://media.fithub.example.cn",
        )
        failures = []

        tencent_cloud_preflight.validate_env(values, failures)

        self.assertEqual(failures, [])
        self.assertEqual(values["FITHUB_MEDIA_STORAGE_PROVIDER"], "cos")
        self.assertEqual(values["FITHUB_TENCENT_COS_BUCKET"], "fithub-media-1250000000")

    def test_build_env_values_rejects_incomplete_tencent_cos_media_storage(self):
        with self.assertRaisesRegex(ValueError, "FITHUB_TENCENT_COS_SECRET_ID"):
            init_tencent_env.build_env_values(
                api_origin="https://api.fithub.example.cn",
                state_provider="supabase",
                supabase_url="https://abcdefghijklmnopqrst.supabase.co",
                supabase_service_role_key="s" * 80,
                media_storage_provider="cos",
            )

    def test_render_env_roundtrips_through_preflight_parser(self):
        values = init_tencent_env.build_env_values(
            api_origin="https://api.fithub.example.cn",
            state_provider="supabase",
            supabase_url="https://abcdefghijklmnopqrst.supabase.co",
            supabase_service_role_key="s" * 80,
            admin_token="a" * 32,
            media_maintenance_token="b" * 32,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / ".env.production"
            init_tencent_env.write_text_securely(path, init_tencent_env.render_env(values))
            parsed = tencent_cloud_preflight.parse_env_file(path)

        self.assertEqual(parsed["FITHUB_PUBLIC_API_ORIGIN"], "https://api.fithub.example.cn")
        self.assertEqual(parsed["FITHUB_ADMIN_TOKEN"], "a" * 32)
        self.assertEqual(parsed["FITHUB_MEDIA_STORAGE_PROVIDER"], "supabase")

    def test_render_nginx_config_replaces_domain(self):
        rendered = init_tencent_env.render_nginx_config("https://api.fithub.example.cn")

        self.assertIn("server_name api.fithub.example.cn;", rendered)
        self.assertNotIn("api.yourdomain.com", rendered)

    def test_render_nginx_config_can_include_web_domain(self):
        rendered = init_tencent_env.render_nginx_config(
            "https://api.fithub.example.cn",
            "https://app.fithub.example.cn",
        )

        self.assertIn("server_name api.fithub.example.cn app.fithub.example.cn;", rendered)
        self.assertNotIn("app.yourdomain.com", rendered)


if __name__ == "__main__":
    unittest.main()
