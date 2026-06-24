import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELEASE_PATH = ROOT / "scripts" / "build_tencent_release.py"
SPEC = importlib.util.spec_from_file_location("build_tencent_release", RELEASE_PATH)
build_tencent_release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_tencent_release)


class TencentReleaseTests(unittest.TestCase):
    def test_release_safe_allows_example_env_but_rejects_real_envs_and_data(self):
        self.assertTrue(build_tencent_release.is_release_safe(Path("deploy/tencent-cloud/.env.production.example")))
        self.assertFalse(build_tencent_release.is_release_safe(Path("deploy/tencent-cloud/.env.production")))
        self.assertFalse(build_tencent_release.is_release_safe(Path(".env.production")))
        self.assertFalse(build_tencent_release.is_release_safe(Path("data/shared_state.json")))
        self.assertFalse(build_tencent_release.is_release_safe(Path("backups/fithub-production-snapshot.json")))

    def test_file_sha256_returns_stable_digest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "payload.txt"
            path.write_text("fithub\n", encoding="utf-8")

            self.assertEqual(
                build_tencent_release.file_sha256(path),
                "2bfc5e7b003e3259bf0f81c7f76ab4bfb94d51267784bc7ab7d93ea9bf31f224",
            )


if __name__ == "__main__":
    unittest.main()
