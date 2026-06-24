import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_PATH = ROOT / "scripts" / "tencent_remote_bootstrap.py"
SPEC = importlib.util.spec_from_file_location("tencent_remote_bootstrap", BOOTSTRAP_PATH)
tencent_remote_bootstrap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tencent_remote_bootstrap)


class TencentRemoteBootstrapTests(unittest.TestCase):
    def write_file(self, root: Path, name: str, body: str = "#!/usr/bin/env sh\necho ok\n") -> Path:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def test_build_steps_uploads_and_runs_bootstrap_script(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            bootstrap_file = self.write_file(root, "bootstrap-server.sh")

            steps = tencent_remote_bootstrap.build_steps(
                host="1.2.3.4",
                user="ubuntu",
                port=2222,
                identity_file=Path("~/.ssh/fithub").expanduser(),
                remote_dir="/srv/fithub",
                bootstrap_file=bootstrap_file,
            )

        self.assertEqual([step.label for step in steps], ["Upload server bootstrap script", "Run server bootstrap script"])
        display_text = "\n".join(step.display() for step in steps)
        self.assertIn("ubuntu@1.2.3.4", display_text)
        self.assertIn("-P 2222", display_text)
        self.assertIn("-p 2222", display_text)
        self.assertIn("/tmp/fithub-bootstrap-server.sh", display_text)
        self.assertIn("FITHUB_REMOTE_DIR=/srv/fithub", display_text)

    def test_validate_local_inputs_rejects_missing_bootstrap_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(FileNotFoundError):
                tencent_remote_bootstrap.validate_local_inputs(Path(temp_dir) / "missing.sh")


if __name__ == "__main__":
    unittest.main()
