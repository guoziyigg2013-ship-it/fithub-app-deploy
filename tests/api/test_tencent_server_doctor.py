import importlib.util
import socket
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCTOR_PATH = ROOT / "scripts" / "tencent_server_doctor.py"
SPEC = importlib.util.spec_from_file_location("tencent_server_doctor", DOCTOR_PATH)
tencent_server_doctor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tencent_server_doctor)


def write_env(path: Path, port: int = 10000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"PORT={port}",
                "FITHUB_URL_PREFIX=/",
                "FITHUB_DATA_DIR=/data/fithub",
                "FITHUB_PUBLIC_API_ORIGIN=https://api.fithub.example.cn",
                "SUPABASE_URL=https://abcdefghijklmnopqrst.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY=" + "s" * 80,
                "FITHUB_SUPABASE_TABLE=fithub_app_state",
                "FITHUB_SUPABASE_ROW_ID=primary",
                "FITHUB_ADMIN_TOKEN=" + "a" * 32,
                "FITHUB_MEDIA_MAINTENANCE_TOKEN=" + "b" * 32,
                "",
            ]
        ),
        encoding="utf-8",
    )


class TencentServerDoctorTests(unittest.TestCase):
    def test_valid_env_passes_when_external_checks_are_skipped(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env.production"
            compose_file = Path(temp_dir) / "docker-compose.yml"
            write_env(env_file, port=10000)
            compose_file.write_text("services: {}\n", encoding="utf-8")

            failures, warnings = tencent_server_doctor.inspect_server(
                env_file=env_file,
                compose_file=compose_file,
                check_docker=False,
                check_compose=False,
                check_port=False,
                min_free_mb=1,
            )

        self.assertEqual(failures, [])
        self.assertEqual(warnings, [])

    def test_missing_env_file_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            failures, _warnings = tencent_server_doctor.inspect_server(
                env_file=Path(temp_dir) / "missing.env",
                compose_file=Path(temp_dir) / "missing-compose.yml",
                check_docker=False,
                check_compose=False,
                check_port=False,
                min_free_mb=1,
            )

        self.assertTrue(any("Missing env file" in item for item in failures))

    def test_port_conflict_is_reported(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock, tempfile.TemporaryDirectory() as temp_dir:
            sock.bind(("127.0.0.1", 0))
            sock.listen(1)
            port = sock.getsockname()[1]
            env_file = Path(temp_dir) / ".env.production"
            compose_file = Path(temp_dir) / "docker-compose.yml"
            write_env(env_file, port=port)
            compose_file.write_text("services: {}\n", encoding="utf-8")

            failures, _warnings = tencent_server_doctor.inspect_server(
                env_file=env_file,
                compose_file=compose_file,
                check_docker=False,
                check_compose=False,
                check_port=True,
                min_free_mb=1,
            )

        self.assertTrue(any("already in use" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
