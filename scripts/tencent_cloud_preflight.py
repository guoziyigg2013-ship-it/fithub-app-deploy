#!/usr/bin/env python3
"""Validate Tencent Cloud server configuration before running FitHub in production."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
TENCENT_DIR = ROOT / "deploy" / "tencent-cloud"
DEFAULT_ENV_FILE = TENCENT_DIR / ".env.production"
DEFAULT_COMPOSE_FILE = TENCENT_DIR / "docker-compose.yml"
DISALLOWED_HOST_PARTS = ("onrender.com", "pages.dev", "trycloudflare.com", "localhost", "127.0.0.1")
PLACEHOLDER_TOKENS = ("yourdomain", "your-real", "replace-with", "example.com", "你的", "占位", "<", ">", "{", "}")
REQUIRED_KEYS = (
    "PORT",
    "FITHUB_URL_PREFIX",
    "FITHUB_DATA_DIR",
    "FITHUB_PUBLIC_API_ORIGIN",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "FITHUB_SUPABASE_TABLE",
    "FITHUB_SUPABASE_ROW_ID",
    "FITHUB_ADMIN_TOKEN",
    "FITHUB_MEDIA_MAINTENANCE_TOKEN",
)
NUMERIC_LIMIT_KEYS = (
    "FITHUB_SUPABASE_TIMEOUT",
    "FITHUB_SUPABASE_REFRESH_COOLDOWN_SECONDS",
    "FITHUB_SUPABASE_BACKUP_RETENTION",
    "FITHUB_SUPABASE_PRUNE_INTERVAL_SECONDS",
    "FITHUB_IMAGE_UPLOAD_LIMIT_BYTES",
    "FITHUB_VIDEO_UPLOAD_LIMIT_BYTES",
    "FITHUB_THUMB_UPLOAD_LIMIT_BYTES",
)


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        values[key.strip()] = value
    return values


def looks_placeholder(value: str) -> bool:
    lowered = str(value or "").strip().lower()
    return not lowered or any(token in lowered for token in PLACEHOLDER_TOKENS)


def host_is_custom_https(url: str) -> tuple[bool, str]:
    parsed = urllib.parse.urlparse(str(url or "").strip())
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host:
        return False, "must be a complete HTTPS URL"
    if any(part in host for part in DISALLOWED_HOST_PARTS):
        return False, f"must not use temporary host {host}"
    if looks_placeholder(url):
        return False, "still looks like a placeholder"
    return True, host


def validate_env(values: dict[str, str], failures: list[str]) -> None:
    for key in REQUIRED_KEYS:
        if not values.get(key):
            failures.append(f"{key} is required in .env.production.")

    if values.get("PORT") and values["PORT"] != "10000":
        failures.append("PORT should stay 10000 so Docker, healthcheck, and Nginx agree.")
    if values.get("FITHUB_URL_PREFIX") and values["FITHUB_URL_PREFIX"] != "/":
        failures.append("FITHUB_URL_PREFIX should be / for production root deployment.")
    data_dir = values.get("FITHUB_DATA_DIR", "")
    if data_dir and not data_dir.startswith("/"):
        failures.append("FITHUB_DATA_DIR should be an absolute container path such as /data/fithub.")

    public_origin = values.get("FITHUB_PUBLIC_API_ORIGIN", "")
    ok, detail = host_is_custom_https(public_origin)
    if not ok:
        failures.append(f"FITHUB_PUBLIC_API_ORIGIN {detail}: {public_origin}")

    supabase_url = values.get("SUPABASE_URL", "")
    parsed_supabase = urllib.parse.urlparse(supabase_url)
    supabase_host = (parsed_supabase.hostname or "").lower()
    if parsed_supabase.scheme != "https" or not supabase_host.endswith(".supabase.co") or looks_placeholder(supabase_url):
        failures.append("SUPABASE_URL must be the real Supabase Project URL, not a placeholder.")

    service_role_key = values.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if looks_placeholder(service_role_key) or len(service_role_key) < 40:
        failures.append("SUPABASE_SERVICE_ROLE_KEY must be the real service_role key.")

    for key in ("FITHUB_ADMIN_TOKEN", "FITHUB_MEDIA_MAINTENANCE_TOKEN"):
        value = values.get(key, "")
        if looks_placeholder(value) or len(value) < 24:
            failures.append(f"{key} must be a long random production token.")

    for key in NUMERIC_LIMIT_KEYS:
        value = values.get(key, "")
        if value and (not value.isdigit() or int(value) <= 0):
            failures.append(f"{key} must be a positive integer.")


def run_compose_config(compose_file: Path, env_file: Path) -> tuple[bool, str]:
    env = os.environ.copy()
    env.update(parse_env_file(env_file))
    commands = (["docker", "compose"], ["docker-compose"])
    last_error = ""
    for base_cmd in commands:
        try:
            result = subprocess.run(
                [*base_cmd, "-f", str(compose_file), "config"],
                cwd=compose_file.parent,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            last_error = str(exc)
            continue
        if result.returncode == 0:
            return True, result.stdout
        last_error = result.stderr or result.stdout
    return False, last_error or "docker compose is not available"


def fetch_json(url: str, *, timeout: int = 10) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "FitHubTencentPreflight/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8") or "{}")


def validate_live_backend(backend_url: str, failures: list[str]) -> None:
    backend_url = backend_url.strip().rstrip("/")
    ok, detail = host_is_custom_https(backend_url)
    if not ok:
        failures.append(f"Backend URL {detail}: {backend_url}")
        return
    try:
        storage = fetch_json(f"{backend_url}/api/storage/status?remote=1", timeout=20)
    except Exception as exc:
        failures.append(f"Backend storage endpoint is unreachable: {exc}")
        return
    storage_info = storage.get("storage") or {}
    if storage.get("status") != "ok":
        failures.append(f"Backend storage status must be ok, got {storage.get('status')}.")
    if storage_info.get("loadedFrom") == "local-fallback":
        failures.append("Backend must not serve from local-fallback.")
    if storage_info.get("remoteWriteProtected"):
        failures.append("Backend remote writes are protected.")
    if not storage_info.get("supabaseWritable"):
        failures.append("Backend persistent storage is not writable.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate FitHub Tencent Cloud production env and runtime.")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE))
    parser.add_argument("--compose-file", default=str(DEFAULT_COMPOSE_FILE))
    parser.add_argument("--skip-compose", action="store_true")
    parser.add_argument("--backend-url", default="", help="Optional live API origin to validate after deployment.")
    args = parser.parse_args()

    env_file = Path(args.env_file)
    compose_file = Path(args.compose_file)
    failures: list[str] = []

    if not env_file.exists():
        failures.append(f"Missing env file: {env_file}")
    else:
        try:
            values = parse_env_file(env_file)
            validate_env(values, failures)
        except OSError as exc:
            failures.append(f"Cannot read env file: {exc}")

    if not compose_file.exists():
        failures.append(f"Missing compose file: {compose_file}")
    elif not args.skip_compose and env_file.exists():
        ok, output = run_compose_config(compose_file, env_file)
        if not ok:
            failures.append(f"Docker Compose config failed: {output}")

    if args.backend_url:
        validate_live_backend(args.backend_url, failures)

    if failures:
        print("FitHub Tencent Cloud preflight failed:")
        for index, failure in enumerate(failures, start=1):
            print(f"{index}. {failure}")
        return 1

    print("FitHub Tencent Cloud preflight passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
