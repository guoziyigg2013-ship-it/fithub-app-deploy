#!/usr/bin/env python3
"""Run the full FitHub acceptance gate before or after a release."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run_step(label: str, cmd: list[str]) -> tuple[bool, float]:
    print(f"\n==> {label}")
    print("$", " ".join(cmd))
    started_at = time.time()
    result = subprocess.run(cmd, cwd=ROOT)
    elapsed = time.time() - started_at
    if result.returncode != 0:
        print(f"[FAIL] {label} ({elapsed:.1f}s)")
        return False, elapsed
    print(f"[ OK ] {label} ({elapsed:.1f}s)")
    return True, elapsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the complete FitHub acceptance checklist.")
    parser.add_argument("--production-frontend-url", default="", help="Override frontend URL for fixed-domain smoke checks.")
    parser.add_argument("--production-backend-url", default="", help="Override backend URL for production readiness checks.")
    parser.add_argument(
        "--verify-frontend-api-origin",
        action="store_true",
        help="Require frontend config.js apiOrigin to match --production-backend-url.",
    )
    parser.add_argument("--skip-production-readiness", action="store_true", help="Skip production config readiness gate.")
    parser.add_argument("--skip-smoke", action="store_true", help="Skip fixed-domain smoke test.")
    parser.add_argument("--skip-media-report", action="store_true", help="Skip read-only media storage report.")
    parser.add_argument("--skip-production-snapshot", action="store_true", help="Skip admin-token production snapshot.")
    parser.add_argument("--require-cos-media", action="store_true", help="Require live production media storage to use Tencent COS.")
    parser.add_argument("--snapshot-baseline", default="", help="Compare production metrics with this previous snapshot file.")
    parser.add_argument("--run-production-write", action="store_true", help="Run write-path production acceptance with a test phone.")
    parser.add_argument("--production-write-phone", default="", help="Dedicated test phone for production write acceptance.")
    parser.add_argument("--production-write-code", default="", help="Register SMS code for production write acceptance.")
    parser.add_argument("--production-write-login-code", default="", help="Fresh-login SMS code for production write acceptance.")
    args = parser.parse_args()

    steps: list[tuple[str, list[str]]] = [
        ("Local preflight gate", ["python3", "scripts/preflight_check.py"]),
    ]
    if not args.skip_production_readiness:
        readiness_cmd = ["python3", "scripts/production_readiness.py"]
        if args.production_backend_url:
            readiness_cmd.extend(["--backend-url", args.production_backend_url])
        if args.require_cos_media:
            readiness_cmd.append("--require-cos-media")
        steps.append(("Production readiness gate", readiness_cmd))
    if not args.skip_smoke:
        smoke_cmd = ["python3", "scripts/deploy_smoke.py"]
        if args.production_frontend_url:
            smoke_cmd.extend(["--frontend-url", args.production_frontend_url])
        if args.production_backend_url:
            smoke_cmd.extend(["--backend-url", args.production_backend_url])
        if args.verify_frontend_api_origin:
            if not args.production_backend_url:
                print("--verify-frontend-api-origin requires --production-backend-url", file=sys.stderr)
                return 1
            smoke_cmd.extend(["--expect-frontend-api-origin", args.production_backend_url])
        if args.require_cos_media:
            smoke_cmd.append("--require-cos-media")
        steps.append(("Fixed-domain smoke gate", smoke_cmd))
    if not args.skip_media_report:
        steps.append(("Media storage read-only report", ["python3", "scripts/media_maintenance.py"]))
    if not args.skip_production_snapshot:
        snapshot_cmd = ["python3", "scripts/production_snapshot.py"]
        if args.snapshot_baseline:
            snapshot_cmd.extend(["--compare", args.snapshot_baseline])
        steps.append(("Production data snapshot", snapshot_cmd))
    if args.run_production_write:
        write_cmd = ["python3", "scripts/production_write_acceptance.py"]
        if args.production_backend_url:
            write_cmd.extend(["--backend-url", args.production_backend_url])
        if args.production_write_phone:
            write_cmd.extend(["--phone", args.production_write_phone])
        if args.production_write_code:
            write_cmd.extend(["--verification-code", args.production_write_code])
        if args.production_write_login_code:
            write_cmd.extend(["--login-verification-code", args.production_write_login_code])
        steps.append(("Production write-path acceptance", write_cmd))

    print("FitHub final acceptance")
    print(f"Workspace: {ROOT}")
    print(f"Selected steps: {len(steps)}")
    started_at = time.time()

    for label, cmd in steps:
        ok, _elapsed = run_step(label, cmd)
        if not ok:
            print("\nFinal acceptance aborted after first failure.")
            return 1

    print(f"\nFinal acceptance passed in {time.time() - started_at:.1f}s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
