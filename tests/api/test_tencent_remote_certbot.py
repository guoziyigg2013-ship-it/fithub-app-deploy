import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CERTBOT_PATH = ROOT / "scripts" / "tencent_remote_certbot.py"
SPEC = importlib.util.spec_from_file_location("tencent_remote_certbot", CERTBOT_PATH)
tencent_remote_certbot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tencent_remote_certbot)


class TencentRemoteCertbotTests(unittest.TestCase):
    def test_parse_domains_accepts_api_web_and_dedupes(self):
        domains = tencent_remote_certbot.parse_domains(
            "https://api.fithub.example.cn",
            "https://app.fithub.example.cn/",
            ["api.fithub.example.cn"],
        )

        self.assertEqual(domains, ["api.fithub.example.cn", "app.fithub.example.cn"])

    def test_parse_domains_rejects_temporary_hosts(self):
        with self.assertRaisesRegex(ValueError, "onrender.com"):
            tencent_remote_certbot.parse_domains("https://fithub-app-1btg.onrender.com")

    def test_render_acme_config_replaces_placeholders(self):
        rendered = tencent_remote_certbot.render_acme_config(["api.fithub.example.cn", "app.fithub.example.cn"])

        self.assertIn("server_name api.fithub.example.cn app.fithub.example.cn;", rendered)
        self.assertNotIn("api.yourdomain.com", rendered)
        self.assertIn("/.well-known/acme-challenge/", rendered)

    def test_build_steps_uploads_config_and_runs_certbot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            acme_config = Path(temp_dir) / "acme.conf"
            acme_config.write_text("server {}", encoding="utf-8")
            steps, domains = tencent_remote_certbot.build_steps(
                host="1.2.3.4",
                user="ubuntu",
                port=2222,
                identity_file=Path("~/.ssh/fithub").expanduser(),
                api_origin="https://api.fithub.example.cn",
                web_origin="https://app.fithub.example.cn",
                email="ops@example.cn",
                staging=True,
                acme_config=acme_config,
            )

        self.assertEqual(domains, ["api.fithub.example.cn", "app.fithub.example.cn"])
        self.assertEqual([step.label for step in steps], ["Upload ACME bootstrap Nginx config", "Issue Let's Encrypt certificate"])
        display_text = "\n".join(step.display() for step in steps)
        self.assertIn("ubuntu@1.2.3.4", display_text)
        self.assertIn("-P 2222", display_text)
        self.assertIn("certbot certonly", display_text)
        self.assertIn("-d api.fithub.example.cn", display_text)
        self.assertIn("-d app.fithub.example.cn", display_text)
        self.assertIn("--staging", display_text)


if __name__ == "__main__":
    unittest.main()
