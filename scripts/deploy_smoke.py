#!/usr/bin/env python3
"""Run a small post-deploy smoke test against the fixed domains."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_FRONTEND = "https://fithub-cn.pages.dev/"
DEFAULT_BACKEND = "https://fithub-app-1btg.onrender.com"


def fetch_text(url: str) -> tuple[int, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "FitHubSmoke/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.getcode(), body


def fetch_json(url: str) -> tuple[int, dict]:
    code, body = fetch_text(url)
    return code, json.loads(body)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the FitHub deploy smoke test.")
    parser.add_argument("--frontend-url", default=DEFAULT_FRONTEND)
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND)
    args = parser.parse_args()

    frontend_url = args.frontend_url.rstrip("/") + "/"
    backend_url = args.backend_url.rstrip("/")

    try:
        print(f"Checking frontend: {frontend_url}")
        code, html = fetch_text(frontend_url)
        ensure(code == 200, f"Frontend returned {code}")
        ensure("FitHub" in html or "探索" in html, "Frontend shell does not look like FitHub")
        print("  OK frontend shell")

        print(f"Checking backend health: {backend_url}/healthz")
        code, health = fetch_text(f"{backend_url}/healthz")
        ensure(code == 200, f"Health endpoint returned {code}")
        ensure("ok" in health.lower(), "Health endpoint did not return ok")
        print("  OK backend health")

        print(f"Checking backend bootstrap: {backend_url}/api/bootstrap")
        code, bootstrap = fetch_json(f"{backend_url}/api/bootstrap")
        ensure(code == 200, f"Bootstrap returned {code}")
        ensure(isinstance(bootstrap, dict), "Bootstrap payload is not an object")
        ensure("profiles" in bootstrap, "Bootstrap missing profiles")
        ensure("session" in bootstrap, "Bootstrap missing session")
        ensure(
            any(key in bootstrap for key in ("notifications", "threads", "bookings", "posts")),
            "Bootstrap missing any user-content collections",
        )
        print("  OK bootstrap payload")

        print("\nSmoke test passed.")
        return 0
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"\nSmoke test failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
