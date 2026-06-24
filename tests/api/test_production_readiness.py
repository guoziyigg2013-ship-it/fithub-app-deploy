import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
READINESS_PATH = ROOT / "scripts" / "production_readiness.py"
SPEC = importlib.util.spec_from_file_location("production_readiness", READINESS_PATH)
production_readiness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(production_readiness)


class ProductionReadinessTests(unittest.TestCase):
    def test_custom_production_url_rejects_temporary_hosts(self):
        failures = []

        production_readiness.validate_https_custom_url(
            "Backend URL",
            "https://fithub-app-1btg.onrender.com",
            failures,
        )

        self.assertTrue(any("approved custom production domain" in item for item in failures))

    def test_supabase_url_rejects_nxdomain(self):
        original_dns_status = production_readiness.public_dns_status
        production_readiness.public_dns_status = lambda host: {
            "ok": False,
            "status": "NXDOMAIN",
            "answers": 0,
            "error": "",
        }

        try:
            failures = []
            production_readiness.validate_supabase_url("https://missing-project.supabase.co", failures)
        finally:
            production_readiness.public_dns_status = original_dns_status

        self.assertTrue(any("not publicly resolvable" in item and "NXDOMAIN" in item for item in failures))

    def test_static_config_detects_current_prelaunch_blockers(self):
        failures = []

        production_readiness.validate_static_configs(failures, skip_dns=True)

        self.assertTrue(any("AppID" in item and "touristappid" in item for item in failures))

    def test_static_config_rejects_legacy_render_and_tourist_values(self):
        original_read_text = production_readiness.read_text

        def fake_read_text(path):
            path = Path(path)
            if path.name == "project.config.json":
                return '{"appid": "touristappid"}'
            if path.name == "config.js" and path.parent.name == "wechat-miniprogram":
                return 'module.exports = { apiBase: "https://fithub-app-1btg.onrender.com/api" };'
            return 'window.__FITHUB_CONFIG__ = { apiOrigin: "https://fithub-app-1btg.onrender.com" };'

        production_readiness.read_text = fake_read_text
        try:
            failures = []
            production_readiness.validate_static_configs(failures, skip_dns=True)
        finally:
            production_readiness.read_text = original_read_text

        self.assertTrue(any("Web apiOrigin" in item and "custom production domain" in item for item in failures))
        self.assertTrue(any("AppID" in item and "touristappid" in item for item in failures))
        self.assertTrue(any("Mini Program apiBase" in item and "custom production domain" in item for item in failures))

    def test_static_config_accepts_ready_values(self):
        original_read_text = production_readiness.read_text
        original_dns_status = production_readiness.public_dns_status

        def fake_read_text(path):
            path = Path(path)
            if path.name == "project.config.json":
                return '{"appid": "wx1234567890abcdef"}'
            if path.name == "config.js" and path.parent.name == "wechat-miniprogram":
                return 'module.exports = { apiBase: "https://api.fithub.example.com/api" };'
            return 'window.FITHUB_CONFIG = { apiOrigin: "https://api.fithub.example.com" };'

        production_readiness.read_text = fake_read_text
        production_readiness.public_dns_status = lambda host: {
            "ok": True,
            "status": "0",
            "answers": 1,
            "error": "",
        }

        try:
            failures = []
            production_readiness.validate_static_configs(
                failures,
                supabase_url="https://abcdefghijklmnopqrst.supabase.co",
            )
        finally:
            production_readiness.read_text = original_read_text
            production_readiness.public_dns_status = original_dns_status

        self.assertEqual(failures, [])

    def test_live_backend_rejects_degraded_storage_payload(self):
        original_fetch_json = production_readiness.fetch_json
        production_readiness.fetch_json = lambda _url, timeout=20: {
            "status": "degraded",
            "storage": {
                "loadedFrom": "local-fallback",
                "remoteWriteProtected": True,
                "supabaseWritable": False,
            },
            "remoteRows": {
                "reachable": False,
                "error": "dns failed",
            },
            "media": {"storageProvider": "inline"},
        }

        try:
            failures = []
            production_readiness.validate_live_backend("https://api.fithub.example.com", failures)
        finally:
            production_readiness.fetch_json = original_fetch_json

        self.assertTrue(any("local-fallback" in item for item in failures))
        self.assertTrue(any("not writable" in item for item in failures))
        self.assertTrue(any("remote rows" in item and "dns failed" in item for item in failures))

    def test_live_backend_can_require_tencent_cos_media(self):
        original_fetch_json = production_readiness.fetch_json
        production_readiness.fetch_json = lambda _url, timeout=20: {
            "status": "ok",
            "storage": {
                "loadedFrom": "supabase",
                "remoteWriteProtected": False,
                "supabaseWritable": True,
            },
            "remoteRows": {"reachable": True},
            "media": {"storageProvider": "supabase"},
        }

        try:
            failures = []
            production_readiness.validate_live_backend(
                "https://api.fithub.example.com",
                failures,
                require_cos_media=True,
            )
        finally:
            production_readiness.fetch_json = original_fetch_json

        self.assertTrue(any("Tencent COS" in item for item in failures))

    def test_live_backend_accepts_tencent_cos_media_when_required(self):
        original_fetch_json = production_readiness.fetch_json
        production_readiness.fetch_json = lambda _url, timeout=20: {
            "status": "ok",
            "storage": {
                "loadedFrom": "supabase",
                "remoteWriteProtected": False,
                "supabaseWritable": True,
            },
            "remoteRows": {"reachable": True},
            "media": {"storageProvider": "cos"},
        }

        try:
            failures = []
            production_readiness.validate_live_backend(
                "https://api.fithub.example.com",
                failures,
                require_cos_media=True,
            )
        finally:
            production_readiness.fetch_json = original_fetch_json

        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
