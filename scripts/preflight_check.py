#!/usr/bin/env python3
"""Run the local FitHub preflight checks before deployment."""

from __future__ import annotations

import argparse
import os
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
    parser = argparse.ArgumentParser(
        description="Run syntax, API, and Playwright preflight checks."
    )
    parser.add_argument("--skip-syntax", action="store_true")
    parser.add_argument("--skip-api", action="store_true")
    parser.add_argument("--skip-e2e", action="store_true")
    args = parser.parse_args()

    steps: list[tuple[str, list[str]]] = []
    if not args.skip_syntax:
        steps.append(("Node syntax check", ["node", "--check", "app.js"]))
        steps.append(("Python syntax check", ["python3", "-m", "py_compile", "server.py"]))
        steps.append(("WeChat Mini Program scaffold check", ["python3", "scripts/check_miniprogram.py"]))
    if not args.skip_api:
        steps.append(
            (
                "API regression suite",
                ["python3", "-m", "unittest", "discover", "-s", "tests/api", "-p", "test_*.py", "-v"],
            )
        )
    if not args.skip_e2e:
        steps.append(
            (
                "Playwright UI regression suite",
                ["npx", "playwright", "test", "tests/e2e", "--reporter=line", "--timeout=30000"],
            )
        )

    if not steps:
        print("No checks selected. Nothing to do.")
        return 0

    print("FitHub preflight checks")
    print(f"Workspace: {ROOT}")
    print(f"Selected steps: {len(steps)}")

    overall_started_at = time.time()
    for label, cmd in steps:
        ok, _elapsed = run_step(label, cmd)
        if not ok:
            print("\nPreflight aborted after first failure.")
            return 1

    total_elapsed = time.time() - overall_started_at
    print(f"\nAll preflight checks passed in {total_elapsed:.1f}s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
