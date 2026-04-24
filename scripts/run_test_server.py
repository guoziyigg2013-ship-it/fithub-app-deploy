import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER_FILE = ROOT / "server.py"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()

    temp_root = Path(tempfile.mkdtemp(prefix="fithub-e2e-"))
    data_dir = temp_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.update(
        {
            "FITHUB_DATA_DIR": str(data_dir),
            "FITHUB_PUBLIC_API_ORIGIN": "",
            "FITHUB_SMS_DEV_MODE": "true",
            "SUPABASE_URL": "",
            "SUPABASE_SERVICE_ROLE_KEY": "",
            "PYTHONUNBUFFERED": "1",
        }
    )

    process = subprocess.Popen(
        [sys.executable, str(SERVER_FILE), "--host", "127.0.0.1", "--port", str(args.port)],
        cwd=str(ROOT),
        env=env,
    )

    try:
        raise SystemExit(process.wait())
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
