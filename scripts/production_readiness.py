#!/usr/bin/env python3
"""Validate FitHub production configuration before WeChat Mini Program review."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
MINIAPP_ROOT = ROOT / "wechat-miniprogram"
DEFAULT_BACKEND = "https://fithub-app-1btg.onrender.com"
DISALLOWED_PRODUCTION_HOST_PARTS = ("onrender.com", "pages.dev", "trycloudflare.com", "localhost", "127.0.0.1")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_js_string_property(text: str, key: str) -> str:
    match = re.search(rf"{re.escape(key)}\s*:\s*[\"']([^\"']+)[\"']", text)
    return match.group(1).strip() if match else ""


def fail_list_add(failures: list[str], message: str) -> None:
    failures.append(message)


def validate_https_custom_url(label: str, value: str, failures: list[str], *, require_api_suffix: bool = False) -> None:
    if not value:
        fail_list_add(failures, f"{label} is missing.")
        return
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "https":
        fail_list_add(failures, f"{label} must use HTTPS: {value}")
    host = (parsed.hostname or "").lower()
    if not host:
        fail_list_add(failures, f"{label} is missing a valid host: {value}")
    for part in DISALLOWED_PRODUCTION_HOST_PARTS:
        if part in host:
            fail_list_add(failures, f"{label} must use an approved custom production domain, not {host}.")
            break
    if require_api_suffix and not value.rstrip("/").endswith("/api"):
        fail_list_add(failures, f"{label} should point to the /api root: {value}")


def public_dns_status(host: str) -> dict[str, Any]:
    host = str(host or "").strip().lower()
    if not host:
        return {"ok": False, "status": "missing", "answers": 0, "error": "missing host"}
    url = "https://cloudflare-dns.com/dns-query?name=" + urllib.parse.quote(host) + "&type=A"
    try:
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/dns-json", "User-Agent": "FitHubReadiness/1.0"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8") or "{}")
        status = int(payload.get("Status") or 0)
        answers = payload.get("Answer") or []
        return {
            "ok": status == 0 and bool(answers),
            "status": "NXDOMAIN" if status == 3 else str(status),
            "answers": len(answers),
            "error": "",
        }
    except Exception as exc:
        return {"ok": False, "status": "error", "answers": 0, "error": str(exc)}


def validate_supabase_url(raw_url: str, failures: list[str], *, skip_dns: bool = False) -> None:
    raw_url = str(raw_url or "").strip().rstrip("/")
    if not raw_url:
        fail_list_add(failures, "SUPABASE_URL is missing.")
        return
    parsed = urllib.parse.urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host:
        fail_list_add(failures, f"SUPABASE_URL must be a complete HTTPS Project URL: {raw_url}")
        return
    if not host.endswith(".supabase.co"):
        fail_list_add(failures, f"SUPABASE_URL host should end with .supabase.co: {host}")
    if any(token in raw_url.lower() for token in ("你的", "your", "project", "placeholder", "<", ">", "{", "}")):
        fail_list_add(failures, "SUPABASE_URL still looks like a placeholder.")
    if not skip_dns:
        dns = public_dns_status(host)
        if not dns["ok"]:
            fail_list_add(
                failures,
                f"SUPABASE_URL host is not publicly resolvable: {host} "
                f"(public DNS status={dns['status']}, error={dns['error'] or 'none'}).",
            )


def validate_static_configs(failures: list[str], *, supabase_url: str = "", skip_dns: bool = False) -> None:
    web_config = read_text(ROOT / "config.js")
    web_api_origin = extract_js_string_property(web_config, "apiOrigin")
    validate_https_custom_url("Web apiOrigin", web_api_origin, failures)

    project_config = json.loads(read_text(MINIAPP_ROOT / "project.config.json"))
    appid = str(project_config.get("appid") or "").strip()
    if not appid or appid == "touristappid":
        fail_list_add(failures, "Mini Program AppID must be a real AppID, not touristappid.")
    elif not appid.startswith("wx"):
        fail_list_add(failures, "Mini Program AppID should start with wx.")

    mini_config = read_text(MINIAPP_ROOT / "config.js")
    mini_api_base = extract_js_string_property(mini_config, "apiBase")
    validate_https_custom_url("Mini Program apiBase", mini_api_base, failures, require_api_suffix=True)

    if supabase_url:
        validate_supabase_url(supabase_url, failures, skip_dns=skip_dns)


def fetch_json(url: str, *, timeout: int = 20) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "FitHubReadiness/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8") or "{}")


def validate_live_backend(backend_url: str, failures: list[str]) -> None:
    backend_url = backend_url.rstrip("/")
    validate_https_custom_url("Backend URL", backend_url, failures)
    try:
        storage = fetch_json(f"{backend_url}/api/storage/status?remote=1", timeout=30)
    except Exception as exc:
        fail_list_add(failures, f"Backend storage status is unreachable: {exc}")
        return

    storage_info = storage.get("storage") or {}
    remote_rows = storage.get("remoteRows") or {}
    if storage.get("status") != "ok":
        fail_list_add(failures, f"Backend storage status must be ok, got {storage.get('status')}.")
    if storage_info.get("loadedFrom") == "local-fallback":
        fail_list_add(failures, "Backend is serving from local-fallback.")
    if storage_info.get("remoteWriteProtected"):
        fail_list_add(failures, "Backend remote writes are protected; production data may not persist.")
    if not storage_info.get("supabaseWritable"):
        fail_list_add(failures, "Backend persistent storage is not writable.")
    if remote_rows and not remote_rows.get("reachable"):
        fail_list_add(failures, f"Backend remote rows are unreachable: {remote_rows.get('error') or 'unknown error'}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate FitHub production readiness gates.")
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND)
    parser.add_argument("--supabase-url", default=os.getenv("SUPABASE_URL", ""))
    parser.add_argument("--skip-live", action="store_true", help="Only validate static repository configuration.")
    parser.add_argument("--skip-supabase-dns", action="store_true", help="Do not query public DNS for SUPABASE_URL.")
    args = parser.parse_args()

    failures: list[str] = []
    validate_static_configs(failures, supabase_url=args.supabase_url, skip_dns=args.skip_supabase_dns)
    if not args.skip_live:
        validate_live_backend(args.backend_url, failures)

    if failures:
        print("FitHub production readiness failed:")
        for index, failure in enumerate(failures, start=1):
            print(f"{index}. {failure}")
        return 1

    print("FitHub production readiness passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
