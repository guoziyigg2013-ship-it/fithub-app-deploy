#!/usr/bin/env python3
"""Create and compare FitHub production data snapshots.

The snapshot is intentionally admin-token protected because it can include
phone-linked accounts, messages, bookings, and media metadata.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BACKEND = "https://fithub-app-1btg.onrender.com"
DEFAULT_OUTPUT_DIR = ROOT / "backups"
CRITICAL_METRIC_KEYS = (
    "real_profiles",
    "phone_profiles",
    "accounts",
    "real_follows",
    "real_posts",
    "real_bookings",
    "real_threads",
    "real_checkins",
)


def fetch_json(url: str, *, token: str = "", timeout: int = 30) -> dict[str, Any]:
    headers = {"User-Agent": "FitHubSnapshot/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8") or "{}")
        if response.status != 200:
            raise RuntimeError(f"{url} returned {response.status}: {payload}")
        return payload


def extract_metrics(snapshot: dict[str, Any]) -> dict[str, int]:
    if not isinstance(snapshot, dict):
        return {}
    metrics = snapshot.get("metrics")
    if not isinstance(metrics, dict):
        storage = snapshot.get("storage")
        if isinstance(storage, dict):
            metrics = storage.get("metrics")
    if not isinstance(metrics, dict):
        return {}
    return {key: int(metrics.get(key) or 0) for key in CRITICAL_METRIC_KEYS}


def parse_allow_decrease(values: list[str]) -> dict[str, int]:
    allowances: dict[str, int] = {}
    for item in values:
        if ":" not in item:
            raise ValueError(f"--allow-decrease must use metric:count, got {item!r}")
        key, raw_count = item.split(":", 1)
        key = key.strip()
        if key not in CRITICAL_METRIC_KEYS:
            raise ValueError(f"Unknown metric {key!r}; expected one of {', '.join(CRITICAL_METRIC_KEYS)}")
        allowances[key] = max(0, int(raw_count.strip()))
    return allowances


def compare_metrics(
    current: dict[str, int],
    baseline: dict[str, int],
    *,
    allowances: dict[str, int] | None = None,
) -> list[str]:
    allowances = allowances or {}
    failures = []
    for key in CRITICAL_METRIC_KEYS:
        before = int(baseline.get(key) or 0)
        after = int(current.get(key) or 0)
        allowed_drop = int(allowances.get(key) or 0)
        if after + allowed_drop < before:
            failures.append(f"{key} dropped from {before} to {after} (allowed drop {allowed_drop})")
    return failures


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_snapshot(snapshot: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ", time.gmtime())
    target = output_dir / f"fithub-production-snapshot-{timestamp}.json"
    with target.open("w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return target


def print_metrics(metrics: dict[str, int]) -> None:
    for key in CRITICAL_METRIC_KEYS:
        print(f"  {key}: {int(metrics.get(key) or 0)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or compare FitHub production data snapshots.")
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND)
    parser.add_argument("--token", default=os.getenv("FITHUB_ADMIN_TOKEN", ""))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--compare", default="", help="Compare the current snapshot with a previous snapshot file.")
    parser.add_argument(
        "--allow-decrease",
        action="append",
        default=[],
        metavar="METRIC:COUNT",
        help="Allow a small expected metric drop while comparing snapshots.",
    )
    parser.add_argument("--min-real-profiles", type=int, default=1)
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Fetch public storage diagnostics only. This is useful when no admin token is available.",
    )
    args = parser.parse_args()

    backend_url = args.backend_url.rstrip("/")
    try:
        if args.status_only:
            snapshot = fetch_json(f"{backend_url}/api/storage/status?remote=1")
        else:
            if not args.token:
                raise RuntimeError("FITHUB_ADMIN_TOKEN or --token is required for full production snapshots.")
            snapshot = fetch_json(f"{backend_url}/api/admin/export", token=args.token)

        metrics = extract_metrics(snapshot)
        if not metrics:
            raise RuntimeError("Snapshot does not contain integrity metrics.")

        print("Current FitHub production metrics:")
        print_metrics(metrics)

        if args.min_real_profiles > 0 and metrics.get("real_profiles", 0) < args.min_real_profiles:
            raise RuntimeError(
                f"real_profiles is {metrics.get('real_profiles', 0)}, expected at least {args.min_real_profiles}."
            )

        if args.compare:
            baseline = load_json(Path(args.compare))
            baseline_metrics = extract_metrics(baseline)
            if not baseline_metrics:
                raise RuntimeError(f"Baseline snapshot {args.compare} does not contain integrity metrics.")
            failures = compare_metrics(metrics, baseline_metrics, allowances=parse_allow_decrease(args.allow_decrease))
            if failures:
                raise RuntimeError("Production metrics regressed: " + "; ".join(failures))
            print(f"Metrics comparison passed against {args.compare}.")

        target = write_snapshot(snapshot, Path(args.output_dir))
        print(f"Snapshot written: {target}")
        return 0
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Snapshot failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
