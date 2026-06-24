import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SMOKE_PATH = ROOT / "scripts" / "deploy_smoke.py"
SPEC = importlib.util.spec_from_file_location("deploy_smoke", SMOKE_PATH)
deploy_smoke = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(deploy_smoke)


def healthy_storage_payload(**overrides):
    payload = {
        "status": "ok",
        "storage": {
            "loadedFrom": "supabase",
            "supabaseConfigured": True,
            "supabaseWritable": True,
            "remoteWriteProtected": False,
        },
        "metrics": {
            "real_profiles": 90,
            "real_follows": 125,
            "real_posts": 29,
            "real_threads": 4,
        },
        "remoteRows": {
            "reachable": True,
            "primaryRowPresent": True,
        },
        "media": {
            "storageProvider": "cos",
            "bucket": "fithub-media-1250000000",
        },
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(payload.get(key), dict):
            payload[key].update(value)
        else:
            payload[key] = value
    return payload


class DeploySmokeGuardTests(unittest.TestCase):
    def setUp(self):
        self.original_public_dns = deploy_smoke.public_dns_diagnostic
        deploy_smoke.public_dns_diagnostic = lambda host: "publicDns=NXDOMAIN" if host else ""

    def tearDown(self):
        deploy_smoke.public_dns_diagnostic = self.original_public_dns

    def test_storage_status_accepts_healthy_remote_state(self):
        deploy_smoke.validate_storage_status(healthy_storage_payload(), min_real_profiles=1)

    def test_storage_status_rejects_local_fallback(self):
        payload = healthy_storage_payload(
            status="degraded",
            storage={
                "loadedFrom": "local-fallback",
                "supabaseWritable": False,
                "remoteWriteProtected": True,
            },
            supabase={"host": "example.supabase.co", "hasServiceRoleKey": True},
            remoteRows={"reachable": False, "error": "dns failed"},
        )

        with self.assertRaisesRegex(RuntimeError, "local fallback.*example\\.supabase\\.co.*NXDOMAIN.*dns failed"):
            deploy_smoke.validate_storage_status(payload, min_real_profiles=1)

    def test_storage_status_failure_includes_runtime_dns_diagnostics(self):
        payload = healthy_storage_payload(
            status="degraded",
            storage={
                "loadedFrom": "local-fallback",
                "supabaseWritable": False,
                "remoteWriteProtected": True,
            },
            supabase={"host": "missing.supabase.co", "hasServiceRoleKey": True},
            supabaseDns={"resolved": False, "error": "[Errno -2] Name or service not known", "flags": []},
        )

        with self.assertRaisesRegex(RuntimeError, "NXDOMAIN.*runtimeDnsResolved=False.*Name or service not known"):
            deploy_smoke.validate_storage_status(payload, min_real_profiles=1)

    def test_storage_status_rejects_unwritable_remote_storage(self):
        payload = healthy_storage_payload(storage={"supabaseWritable": False})

        with self.assertRaisesRegex(RuntimeError, "not writable"):
            deploy_smoke.validate_storage_status(payload, min_real_profiles=1)

    def test_storage_status_rejects_collapsed_profile_metrics(self):
        payload = healthy_storage_payload(metrics={"real_profiles": 0})

        with self.assertRaisesRegex(RuntimeError, "real_profiles"):
            deploy_smoke.validate_storage_status(payload, min_real_profiles=1)

    def test_storage_status_accepts_cos_media_when_required(self):
        deploy_smoke.validate_storage_status(
            healthy_storage_payload(),
            min_real_profiles=1,
            require_cos_media=True,
        )

    def test_storage_status_rejects_non_cos_media_when_required(self):
        payload = healthy_storage_payload(media={"storageProvider": "supabase"})

        with self.assertRaisesRegex(RuntimeError, "Tencent COS"):
            deploy_smoke.validate_storage_status(payload, min_real_profiles=1, require_cos_media=True)

    def test_storage_status_rejects_unreachable_remote_rows(self):
        payload = healthy_storage_payload(remoteRows={"reachable": False, "error": "dns failed"})

        with self.assertRaisesRegex(RuntimeError, "unreachable"):
            deploy_smoke.validate_storage_status(payload, min_real_profiles=1)

    def test_elapsed_guard_rejects_slow_production_response(self):
        with self.assertRaisesRegex(RuntimeError, "exceeding"):
            deploy_smoke.ensure_elapsed("Backend health", 21.6, 3.0)

    def test_elapsed_guard_can_be_disabled_for_local_runs(self):
        deploy_smoke.ensure_elapsed("Local dev", 99.0, 0)


if __name__ == "__main__":
    unittest.main()
