import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT_PATH = ROOT / "scripts" / "tencent_cloud_preflight.py"
SPEC = importlib.util.spec_from_file_location("tencent_cloud_preflight", PREFLIGHT_PATH)
tencent_cloud_preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tencent_cloud_preflight)


VALID_ENV = {
    "PORT": "10000",
    "FITHUB_URL_PREFIX": "/",
    "FITHUB_DATA_DIR": "/data/fithub",
    "FITHUB_PUBLIC_API_ORIGIN": "https://api.fithub.example.cn",
    "SUPABASE_URL": "https://abcdefghijklmnopqrst.supabase.co",
    "SUPABASE_SERVICE_ROLE_KEY": "x" * 80,
    "FITHUB_SUPABASE_TABLE": "fithub_app_state",
    "FITHUB_SUPABASE_ROW_ID": "primary",
    "FITHUB_ADMIN_TOKEN": "a" * 32,
    "FITHUB_MEDIA_MAINTENANCE_TOKEN": "b" * 32,
    "FITHUB_IMAGE_UPLOAD_LIMIT_BYTES": "10485760",
}


class TencentCloudPreflightTests(unittest.TestCase):
    def test_parse_env_file_reads_basic_dotenv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / ".env.production"
            path.write_text(
                "# comment\nPORT=10000\nFITHUB_PUBLIC_API_ORIGIN=\"https://api.fithub.example.cn\"\n",
                encoding="utf-8",
            )

            values = tencent_cloud_preflight.parse_env_file(path)

        self.assertEqual(values["PORT"], "10000")
        self.assertEqual(values["FITHUB_PUBLIC_API_ORIGIN"], "https://api.fithub.example.cn")

    def test_validate_env_rejects_placeholders_and_short_tokens(self):
        values = dict(VALID_ENV)
        values["FITHUB_PUBLIC_API_ORIGIN"] = "https://api.yourdomain.com"
        values["SUPABASE_URL"] = "https://your-real-project-ref.supabase.co"
        values["SUPABASE_SERVICE_ROLE_KEY"] = "replace-with-real-service-role-key"
        values["FITHUB_ADMIN_TOKEN"] = "short"

        failures = []
        tencent_cloud_preflight.validate_env(values, failures)

        self.assertTrue(any("FITHUB_PUBLIC_API_ORIGIN" in item for item in failures))
        self.assertTrue(any("SUPABASE_URL" in item for item in failures))
        self.assertTrue(any("SUPABASE_SERVICE_ROLE_KEY" in item for item in failures))
        self.assertTrue(any("FITHUB_ADMIN_TOKEN" in item for item in failures))

    def test_validate_env_accepts_ready_values(self):
        failures = []

        tencent_cloud_preflight.validate_env(dict(VALID_ENV), failures)

        self.assertEqual(failures, [])

    def test_validate_env_accepts_tencent_cos_media_storage(self):
        values = dict(VALID_ENV)
        values.update(
            {
                "FITHUB_MEDIA_STORAGE_PROVIDER": "cos",
                "FITHUB_TENCENT_COS_SECRET_ID": "AKIDEXAMPLE",
                "FITHUB_TENCENT_COS_SECRET_KEY": "cos-secret-key-example",
                "FITHUB_TENCENT_COS_REGION": "ap-guangzhou",
                "FITHUB_TENCENT_COS_BUCKET": "fithub-media-1250000000",
                "FITHUB_TENCENT_COS_PUBLIC_BASE_URL": "https://media.fithub.example.cn",
            }
        )
        failures = []

        tencent_cloud_preflight.validate_env(values, failures)

        self.assertEqual(failures, [])

    def test_validate_env_rejects_incomplete_tencent_cos_media_storage(self):
        values = dict(VALID_ENV)
        values["FITHUB_MEDIA_STORAGE_PROVIDER"] = "cos"
        failures = []

        tencent_cloud_preflight.validate_env(values, failures)

        self.assertTrue(any("FITHUB_TENCENT_COS_SECRET_ID" in item for item in failures))
        self.assertTrue(any("FITHUB_TENCENT_COS_BUCKET" in item for item in failures))

    def test_validate_live_backend_rejects_local_fallback(self):
        original_fetch_json = tencent_cloud_preflight.fetch_json
        tencent_cloud_preflight.fetch_json = lambda _url, timeout=10: {
            "status": "degraded",
            "storage": {
                "loadedFrom": "local-fallback",
                "remoteWriteProtected": True,
                "supabaseWritable": False,
            },
        }

        try:
            failures = []
            tencent_cloud_preflight.validate_live_backend("https://api.fithub.example.cn", failures)
        finally:
            tencent_cloud_preflight.fetch_json = original_fetch_json

        self.assertTrue(any("local-fallback" in item for item in failures))
        self.assertTrue(any("not writable" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
