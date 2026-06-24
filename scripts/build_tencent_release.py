#!/usr/bin/env python3
"""Build a clean FitHub release archive for Tencent Cloud servers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / "dist"
SECRET_NAME_FRAGMENTS = (".env", "secret", "service_role", "token")
EXCLUDED_PREFIXES = (
    ".git/",
    "backups/",
    "data/",
    "dist/",
    "logs/",
    "node_modules/",
    "playwright-report/",
    "test-results/",
    "tmp/",
)


def git_tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def is_release_safe(path: Path) -> bool:
    normalized = path.as_posix()
    if any(normalized.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    name = path.name.lower()
    if name == ".env.production.example":
        return True
    if any(fragment in name for fragment in SECRET_NAME_FRAGMENTS):
        return False
    return True


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_archive(root: Path, output_dir: Path, *, version: str = "") -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    version = version or timestamp
    archive_path = output_dir / f"fithub-tencent-release-{version}.tar.gz"
    manifest_path = archive_path.with_suffix(archive_path.suffix + ".manifest.json")

    tracked_files = [path for path in git_tracked_files(root) if is_release_safe(path)]
    if not tracked_files:
        raise RuntimeError("No release files found.")

    with tarfile.open(archive_path, "w:gz") as archive:
        for relative_path in tracked_files:
            archive.add(root / relative_path, arcname=f"fithub-app-deploy/{relative_path.as_posix()}")

    manifest = {
        "archive": archive_path.name,
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
        "sha256": file_sha256(archive_path),
        "fileCount": len(tracked_files),
        "files": [path.as_posix() for path in tracked_files],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return archive_path, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Tencent Cloud release archive for FitHub.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--version", default="", help="Optional archive version suffix.")
    args = parser.parse_args()

    try:
        archive_path, manifest_path = build_archive(ROOT, Path(args.output_dir), version=args.version)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Tencent release build failed: {exc}", file=sys.stderr)
        return 1

    print(f"Release archive: {archive_path}")
    print(f"Manifest: {manifest_path}")
    print(f"SHA256: {file_sha256(archive_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
