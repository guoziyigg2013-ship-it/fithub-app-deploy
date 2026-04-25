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
    parser.add_argument("--skip-smoke", action="store_true", help="Skip fixed-domain smoke test.")
    parser.add_argument("--skip-media-report", action="store_true", help="Skip read-only media storage report.")
    args = parser.parse_args()

    steps: list[tuple[str, list[str]]] = [
        ("Local preflight gate", ["python3", "scripts/preflight_check.py"]),
    ]
    if not args.skip_smoke:
        steps.append(("Fixed-domain smoke gate", ["python3", "scripts/deploy_smoke.py"]))
    if not args.skip_media_report:
        steps.append(("Media storage read-only report", ["python3", "scripts/media_maintenance.py"]))

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
