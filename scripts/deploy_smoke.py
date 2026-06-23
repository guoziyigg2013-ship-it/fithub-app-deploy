#!/usr/bin/env python3
"""Run a small post-deploy smoke test against the fixed domains."""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional


DEFAULT_FRONTEND = "https://fithub-cn.pages.dev/"
DEFAULT_BACKEND = "https://fithub-app-1btg.onrender.com"
DEFAULT_MAX_FRONTEND_SECONDS = 3.0
DEFAULT_MAX_HEALTH_SECONDS = 3.0
DEFAULT_MAX_STORAGE_SECONDS = 5.0
DEFAULT_MAX_BOOTSTRAP_SECONDS = 8.0
DEFAULT_MIN_REAL_PROFILES = 1


def fetch_text(url: str, *, timeout: int = 20) -> tuple[int, str, float]:
    request = urllib.request.Request(url, headers={"User-Agent": "FitHubSmoke/1.0"})
    started_at = time.time()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.getcode(), body, time.time() - started_at


def fetch_text_with_retries(url: str, *, attempts: int = 1, timeout: int = 20, delay: float = 2.0) -> tuple[int, str, float]:
    last_error: Optional[BaseException] = None
    for attempt in range(1, attempts + 1):
        try:
            return fetch_text(url, timeout=timeout)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, socket.timeout) as exc:
            last_error = exc
            if attempt >= attempts:
                break
            print(f"  Attempt {attempt} timed out or failed, retrying in {delay:.0f}s ...")
            time.sleep(delay)
    raise RuntimeError(f"{url} unavailable after {attempts} attempt(s): {last_error}")


def fetch_json(url: str, *, attempts: int = 1, timeout: int = 20, delay: float = 2.0) -> tuple[int, dict, float]:
    code, body, elapsed = fetch_text_with_retries(url, attempts=attempts, timeout=timeout, delay=delay)
    return code, json.loads(body), elapsed


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def ensure_elapsed(label: str, elapsed: float, max_seconds: float) -> None:
    if max_seconds <= 0:
        return
    ensure(
        elapsed <= max_seconds,
        f"{label} took {elapsed:.2f}s, exceeding the {max_seconds:.2f}s production limit.",
    )


def validate_storage_status(
    storage_payload: dict,
    *,
    allow_local_storage: bool = False,
    min_real_profiles: int = DEFAULT_MIN_REAL_PROFILES,
) -> None:
    ensure(isinstance(storage_payload, dict), "Storage status payload is not an object")
    ensure("storage" in storage_payload and "metrics" in storage_payload, "Storage status missing diagnostics")

    storage = storage_payload.get("storage") or {}
    metrics = storage_payload.get("metrics") or {}
    remote_rows = storage_payload.get("remoteRows") or {}
    status = str(storage_payload.get("status") or "").lower()
    loaded_from = storage.get("loadedFrom")

    if not allow_local_storage:
        ensure(
            storage.get("supabaseConfigured"),
            "Production smoke requires persistent remote storage. Use --allow-local-storage only for dev.",
        )
        ensure(
            loaded_from != "local-fallback",
            "Backend is serving from local fallback; persistent writes are protected but production is degraded.",
        )
        ensure(
            status in {"ok", "healthy", ""},
            f"Backend storage status is {status or 'unknown'}, expected ok.",
        )
        ensure(
            not storage.get("remoteWriteProtected"),
            "Backend writes are remote-protected; production data may not persist.",
        )
        ensure(
            storage.get("supabaseWritable"),
            "Persistent storage is not writable; users may lose new registrations or interactions.",
        )
        if "reachable" in remote_rows:
            ensure(
                remote_rows.get("reachable"),
                f"Remote storage diagnostics are unreachable: {remote_rows.get('error') or 'unknown error'}",
            )

    if min_real_profiles > 0:
        ensure(
            int(metrics.get("real_profiles") or 0) >= min_real_profiles,
            f"real_profiles is {metrics.get('real_profiles')}; expected at least {min_real_profiles}. Production data may have collapsed.",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the FitHub deploy smoke test.")
    parser.add_argument("--frontend-url", default=DEFAULT_FRONTEND)
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND)
    parser.add_argument(
        "--allow-local-storage",
        action="store_true",
        help="Do not fail if the backend reports local JSON storage. Use only for local/dev smoke runs.",
    )
    parser.add_argument("--max-frontend-seconds", type=float, default=DEFAULT_MAX_FRONTEND_SECONDS)
    parser.add_argument("--max-health-seconds", type=float, default=DEFAULT_MAX_HEALTH_SECONDS)
    parser.add_argument("--max-storage-seconds", type=float, default=DEFAULT_MAX_STORAGE_SECONDS)
    parser.add_argument("--max-bootstrap-seconds", type=float, default=DEFAULT_MAX_BOOTSTRAP_SECONDS)
    parser.add_argument("--min-real-profiles", type=int, default=DEFAULT_MIN_REAL_PROFILES)
    args = parser.parse_args()

    frontend_url = args.frontend_url.rstrip("/") + "/"
    backend_url = args.backend_url.rstrip("/")

    try:
        print(f"Checking frontend: {frontend_url}")
        code, html, elapsed = fetch_text_with_retries(frontend_url, attempts=2, timeout=20)
        ensure(code == 200, f"Frontend returned {code}")
        ensure("FitHub" in html or "探索" in html, "Frontend shell does not look like FitHub")
        ensure_elapsed("Frontend shell", elapsed, args.max_frontend_seconds)
        print(f"  OK frontend shell ({elapsed:.2f}s)")

        print(f"Checking backend health: {backend_url}/healthz")
        code, health, elapsed = fetch_text_with_retries(f"{backend_url}/healthz", attempts=4, timeout=25, delay=3)
        ensure(code == 200, f"Health endpoint returned {code}")
        ensure("ok" in health.lower(), "Health endpoint did not return ok")
        ensure_elapsed("Backend health", elapsed, args.max_health_seconds)
        print(f"  OK backend health ({elapsed:.2f}s)")

        storage_status_url = f"{backend_url}/api/storage/status?remote=1"
        print(f"Checking backend storage status: {storage_status_url}")
        code, storage, elapsed = fetch_json(storage_status_url, attempts=3, timeout=30, delay=3)
        ensure(code == 200, f"Storage status returned {code}")
        ensure_elapsed("Storage status", elapsed, args.max_storage_seconds)
        validate_storage_status(
            storage,
            allow_local_storage=args.allow_local_storage,
            min_real_profiles=args.min_real_profiles,
        )
        print(f"  OK storage status ({storage.get('storage', {}).get('loadedFrom', 'unknown')}, {elapsed:.2f}s)")

        print(f"Checking backend bootstrap: {backend_url}/api/bootstrap")
        code, bootstrap, elapsed = fetch_json(f"{backend_url}/api/bootstrap", attempts=3, timeout=25, delay=3)
        ensure(code == 200, f"Bootstrap returned {code}")
        ensure(isinstance(bootstrap, dict), "Bootstrap payload is not an object")
        ensure("profiles" in bootstrap, "Bootstrap missing profiles")
        ensure("session" in bootstrap, "Bootstrap missing session")
        ensure_elapsed("Bootstrap", elapsed, args.max_bootstrap_seconds)
        ensure(
            any(key in bootstrap for key in ("notifications", "threads", "bookings", "posts")),
            "Bootstrap missing any user-content collections",
        )
        ensure(
            args.allow_local_storage or len(bootstrap.get("profiles") or []) >= args.min_real_profiles,
            f"Bootstrap returned only {len(bootstrap.get('profiles') or [])} profile(s); expected at least {args.min_real_profiles}.",
        )
        print(f"  OK bootstrap payload ({elapsed:.2f}s)")

        print("\nSmoke test passed.")
        return 0
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"\nSmoke test failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
