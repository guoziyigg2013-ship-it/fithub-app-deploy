import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "scripts" / "tencent_launch_plan.py"
SPEC = importlib.util.spec_from_file_location("tencent_launch_plan", PLAN_PATH)
tencent_launch_plan = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tencent_launch_plan)


READY_CONFIG = {
    "apiOrigin": "https://api.fithub.cn",
    "webOrigin": "https://app.fithub.cn",
    "mediaOrigin": "https://media.fithub.cn",
    "miniappAppId": "wx1234567890abcdef",
    "serverIp": "1.2.3.4",
    "sshUser": "root",
    "sshKey": "~/.ssh/fithub-tencent",
    "certEmail": "ops@fithub.cn",
    "supabaseUrl": "https://abcdefghijklmnopqrst.supabase.co",
    "supabaseServiceRoleKey": "s" * 80,
    "cosSecretId": "AKIDFITHUBPRODUCTION",
    "cosSecretKey": "cos-secret-key-production",
    "cosBucket": "fithub-media-1250000000",
}


class TencentLaunchPlanTests(unittest.TestCase):
    def test_empty_config_reports_missing_inputs(self):
        plan = tencent_launch_plan.build_plan({})

        self.assertFalse(plan["ready"])
        self.assertIn("apiOrigin", plan["missing"])
        self.assertIn("serverIp", plan["missing"])
        self.assertIn("supabaseServiceRoleKey", plan["missing"])

    def test_ready_config_builds_secret_safe_plan(self):
        plan = tencent_launch_plan.build_plan(dict(READY_CONFIG))

        self.assertTrue(plan["ready"])
        rendered = "\n".join(step["display"] for step in plan["steps"])
        self.assertIn("check:tencent-launch", rendered)
        self.assertIn("deploy:tencent-remote", rendered)
        self.assertIn("<SUPABASE_SERVICE_ROLE_KEY>", rendered)
        self.assertIn("<COS_SECRET_KEY>", rendered)
        self.assertNotIn("s" * 80, rendered)
        self.assertNotIn("cos-secret-key-production", rendered)

    def test_load_config_reads_json_object(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "launch.json"
            path.write_text(json.dumps(READY_CONFIG), encoding="utf-8")

            loaded = tencent_launch_plan.load_config(path)

        self.assertEqual(loaded["apiOrigin"], READY_CONFIG["apiOrigin"])


if __name__ == "__main__":
    unittest.main()
