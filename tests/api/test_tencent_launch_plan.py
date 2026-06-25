import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout


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
    "adminToken": "admin-token-production-value",
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
        self.assertIn("snapshot:prod", rendered)
        self.assertIn("evidence:tencent-launch", rendered)
        self.assertIn("<SUPABASE_SERVICE_ROLE_KEY>", rendered)
        self.assertIn("<COS_SECRET_KEY>", rendered)
        self.assertIn("<FITHUB_ADMIN_TOKEN>", rendered)
        self.assertNotIn("s" * 80, rendered)
        self.assertNotIn("cos-secret-key-production", rendered)
        self.assertNotIn("admin-token-production-value", rendered)
        domains = {item["label"]: item["value"] for item in plan["wechatDomains"]}
        self.assertEqual(domains["request 合法域名"], READY_CONFIG["apiOrigin"])
        self.assertEqual(domains["uploadFile 合法域名"], READY_CONFIG["apiOrigin"])
        self.assertEqual(domains["downloadFile 合法域名"], READY_CONFIG["mediaOrigin"])
        manual = "\n".join(item["label"] + item["detail"] for item in plan["manualChecks"])
        self.assertIn("微信小程序真实 AppID", manual)
        self.assertIn("生产数据快照", manual)

    def test_markdown_includes_wechat_backend_and_manual_checks(self):
        plan = tencent_launch_plan.build_plan(dict(READY_CONFIG))
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            tencent_launch_plan.print_markdown(plan, Path("launch-plan.json"))

        markdown = buffer.getvalue()
        self.assertIn("微信公众平台后台配置", markdown)
        self.assertIn("request 合法域名", markdown)
        self.assertIn("downloadFile 合法域名", markdown)
        self.assertIn("发布前人工核对", markdown)
        self.assertIn("隐私协议与权限说明", markdown)

    def test_load_config_reads_json_object(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "launch.json"
            path.write_text(json.dumps(READY_CONFIG), encoding="utf-8")

            loaded = tencent_launch_plan.load_config(path)

        self.assertEqual(loaded["apiOrigin"], READY_CONFIG["apiOrigin"])


if __name__ == "__main__":
    unittest.main()
