#!/usr/bin/env python3
"""Deploy the FitHub web shell to Tencent CloudBase static hosting."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV_ID = "zhangxin-zhinan-d4fwtsmr9a834d58"
DEFAULT_CLOUD_PATH = "fithub"
DEFAULT_OUTPUT_DIR = ROOT / "dist" / "fithub-cloudbase-static"
DEFAULT_PUBLIC_ORIGIN = "https://zhangxin-zhinan-d4fwtsmr9a834d58-1401297280.tcloudbaseapp.com"

STATIC_FILES = (
    "index.html",
    "mobile.html",
    "admin.html",
    "admin.css",
    "admin.js",
    "styles.css",
    "app.js",
    "sw.js",
    "config.js",
)
STATIC_DIRS = (
    "assets",
    "brand",
)


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_static_files(output_dir: Path) -> None:
    clean_dir(output_dir)
    for name in STATIC_FILES:
        source = ROOT / name
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, output_dir / name)

    for name in STATIC_DIRS:
        source = ROOT / name
        if source.exists():
            shutil.copytree(source, output_dir / name)


def deploy(output_dir: Path, env_id: str, cloud_path: str) -> None:
    cloud_path = cloud_path.strip().strip("/") or DEFAULT_CLOUD_PATH
    command = [
        "npx",
        "--yes",
        "-p",
        "@cloudbase/cli",
        "cloudbase",
        "hosting",
        "deploy",
        str(output_dir),
        cloud_path,
        "-e",
        env_id,
    ]
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy FitHub static web files to Tencent CloudBase hosting.")
    parser.add_argument("--env-id", default=DEFAULT_ENV_ID)
    parser.add_argument("--cloud-path", default=DEFAULT_CLOUD_PATH)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--public-origin", default=DEFAULT_PUBLIC_ORIGIN)
    parser.add_argument("--dry-run", action="store_true", help="Prepare the upload directory without calling CloudBase CLI.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    cloud_path = args.cloud_path.strip().strip("/") or DEFAULT_CLOUD_PATH

    try:
        copy_static_files(output_dir)
        print(f"Prepared static web files: {output_dir}")
        print(f"Target CloudBase path: {cloud_path}/")
        print(f"Expected URL: {args.public_origin.rstrip('/')}/{cloud_path}/")
        if not args.dry_run:
            deploy(output_dir, args.env_id, cloud_path)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Tencent static deploy failed: {exc}", file=sys.stderr)
        return 1

    print("Tencent static deploy complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
