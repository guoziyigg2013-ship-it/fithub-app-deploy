import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REMOTE_PATH = ROOT / "scripts" / "tencent_remote_deploy.py"
SPEC = importlib.util.spec_from_file_location("tencent_remote_deploy", REMOTE_PATH)
tencent_remote_deploy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tencent_remote_deploy)


class TencentRemoteDeployTests(unittest.TestCase):
    def write_file(self, root: Path, name: str, body: str = "x") -> Path:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def test_build_steps_creates_safe_dry_run_plan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive = self.write_file(root, "fithub-tencent-release-demo.tar.gz", "archive")
            env_file = self.write_file(root, ".env.production", "SUPABASE_SERVICE_ROLE_KEY=secret")
            nginx_file = self.write_file(root, "nginx-fithub.conf", "server {}")

            steps = tencent_remote_deploy.build_steps(
                host="1.2.3.4",
                user="ubuntu",
                port=2222,
                identity_file=Path("~/.ssh/fithub").expanduser(),
                archive=archive,
                env_file=env_file,
                nginx_file=nginx_file,
                remote_dir="/srv/fithub",
                check_public=True,
                restart_nginx=True,
            )

        labels = [step.label for step in steps]
        self.assertEqual(labels[0], "Create remote release directory")
        self.assertIn("Upload production env", labels)
        self.assertIn("Install and reload Nginx config", labels)
        self.assertEqual(labels[-1], "Run Tencent Cloud deployment")
        display_text = "\n".join(step.display() for step in steps)
        self.assertIn("ubuntu@1.2.3.4", display_text)
        self.assertIn("-P 2222", display_text)
        self.assertIn("FITHUB_DEPLOY_CHECK_PUBLIC=1 ./deploy.sh", display_text)
        self.assertIn("<local .env.production>", display_text)
        self.assertNotIn("SUPABASE_SERVICE_ROLE_KEY=secret", display_text)

    def test_build_steps_can_skip_nginx(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive = self.write_file(root, "fithub-tencent-release-demo.tar.gz")
            env_file = self.write_file(root, ".env.production")

            steps = tencent_remote_deploy.build_steps(
                host="server.example.cn",
                archive=archive,
                env_file=env_file,
                nginx_file=None,
            )

        labels = [step.label for step in steps]
        self.assertNotIn("Upload Nginx config", labels)
        self.assertIn("Run Tencent Cloud deployment", labels)

    def test_validate_local_inputs_rejects_missing_env(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive = self.write_file(root, "fithub-tencent-release-demo.tar.gz")

            with self.assertRaises(FileNotFoundError):
                tencent_remote_deploy.validate_local_inputs(
                    archive,
                    root / ".env.production",
                    None,
                )


if __name__ == "__main__":
    unittest.main()
