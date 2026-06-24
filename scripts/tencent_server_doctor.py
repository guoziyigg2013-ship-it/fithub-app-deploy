#!/usr/bin/env python3
"""Inspect a Tencent Cloud host before or after deploying FitHub."""

from __future__ import annotations

import argparse
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tencent_cloud_preflight


ROOT = Path(__file__).resolve().parent.parent
TENCENT_DIR = ROOT / "deploy" / "tencent-cloud"
DEFAULT_ENV_FILE = TENCENT_DIR / ".env.production"
DEFAULT_COMPOSE_FILE = TENCENT_DIR / "docker-compose.yml"


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_command(cmd: list[str], *, cwd: Path | None = None, timeout: int = 20) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    return result.returncode == 0, result.stdout.strip() or result.stderr.strip()


def port_is_free(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def local_health_ok(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=4) as response:
            return response.status == 200 and "ok" in response.read().decode("utf-8", errors="ignore").lower()
    except Exception:
        return False


def disk_free_mb(path: Path) -> int:
    target = path
    while not target.exists() and target != target.parent:
        target = target.parent
    usage = shutil.disk_usage(target)
    return int(usage.free / 1024 / 1024)


def docker_compose_command() -> list[str]:
    ok, _output = run_command(["docker", "compose", "version"], timeout=10)
    if ok:
        return ["docker", "compose"]
    if command_exists("docker-compose"):
        return ["docker-compose"]
    return []


def inspect_server(
    *,
    env_file: Path = DEFAULT_ENV_FILE,
    compose_file: Path = DEFAULT_COMPOSE_FILE,
    min_free_mb: int = 1024,
    check_docker: bool = True,
    check_compose: bool = True,
    check_port: bool = True,
    allow_running_service: bool = False,
    check_public: bool = False,
    backend_url: str = "",
) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    values: dict[str, str] = {}

    if not env_file.exists():
        failures.append(f"Missing env file: {env_file}")
    else:
        try:
            values = tencent_cloud_preflight.parse_env_file(env_file)
            tencent_cloud_preflight.validate_env(values, failures)
        except OSError as exc:
            failures.append(f"Cannot read env file: {exc}")

    if not compose_file.exists():
        failures.append(f"Missing compose file: {compose_file}")

    free_mb = disk_free_mb(env_file.parent if env_file.parent.exists() else ROOT)
    if free_mb < min_free_mb:
        failures.append(f"Not enough free disk space near {env_file.parent}: {free_mb}MB < {min_free_mb}MB.")

    if check_docker:
        if not command_exists("docker"):
            failures.append("docker is not installed or not in PATH.")
        else:
            ok, output = run_command(["docker", "info"], timeout=20)
            if not ok:
                failures.append(f"docker daemon is not ready: {output}")

    if check_compose and compose_file.exists() and env_file.exists():
        ok, output = tencent_cloud_preflight.run_compose_config(compose_file, env_file)
        if not ok:
            failures.append(f"Docker Compose config failed: {output}")

    if check_port and values:
        port = int(values.get("PORT") or 10000)
        if not port_is_free(port):
            if allow_running_service and local_health_ok(port):
                warnings.append(f"Port {port} is already used by a healthy FitHub service.")
            else:
                failures.append(f"Port {port} is already in use. Stop the old service or rerun with --allow-running-service.")

    if check_public:
        public_url = backend_url.strip().rstrip("/") or values.get("FITHUB_PUBLIC_API_ORIGIN", "").rstrip("/")
        if not public_url:
            failures.append("Public backend URL is required for --check-public.")
        else:
            tencent_cloud_preflight.validate_live_backend(public_url, failures)

    return failures, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Tencent Cloud host readiness for FitHub.")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE))
    parser.add_argument("--compose-file", default=str(DEFAULT_COMPOSE_FILE))
    parser.add_argument("--min-free-mb", type=int, default=1024)
    parser.add_argument("--skip-docker", action="store_true")
    parser.add_argument("--skip-compose", action="store_true")
    parser.add_argument("--skip-port", action="store_true")
    parser.add_argument("--allow-running-service", action="store_true")
    parser.add_argument("--check-public", action="store_true", help="Check public HTTPS backend and remote storage.")
    parser.add_argument("--backend-url", default="", help="Override public API origin for --check-public.")
    args = parser.parse_args()

    failures, warnings = inspect_server(
        env_file=Path(args.env_file),
        compose_file=Path(args.compose_file),
        min_free_mb=args.min_free_mb,
        check_docker=not args.skip_docker,
        check_compose=not args.skip_compose,
        check_port=not args.skip_port,
        allow_running_service=args.allow_running_service,
        check_public=args.check_public,
        backend_url=args.backend_url,
    )

    if warnings:
        print("FitHub Tencent server doctor warnings:")
        for index, warning in enumerate(warnings, start=1):
            print(f"{index}. {warning}")

    if failures:
        print("FitHub Tencent server doctor failed:")
        for index, failure in enumerate(failures, start=1):
            print(f"{index}. {failure}")
        return 1

    print("FitHub Tencent server doctor passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
