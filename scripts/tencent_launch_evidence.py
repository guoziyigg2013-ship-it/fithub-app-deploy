#!/usr/bin/env python3
"""Write a FitHub Tencent Cloud launch evidence report.

The report is meant for the final mainland-China cutover: it records the
current Git revision, configured domains, release archive checksum, migration
readiness status, and optional production data snapshot metrics.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_tencent_release
import domestic_migration_status
import production_snapshot


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / "reports"


def run_git(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip()


def latest_release_archive(dist_dir: Path) -> Path | None:
    candidates = sorted(
        dist_dir.glob("fithub-tencent-release-*.tar.gz"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def release_info(path: Path | None) -> dict[str, Any]:
    if not path:
        return {"present": False, "path": "", "sha256": "", "sizeBytes": 0}
    return {
        "present": path.exists(),
        "path": str(path),
        "sha256": build_tencent_release.file_sha256(path) if path.exists() else "",
        "sizeBytes": path.stat().st_size if path.exists() else 0,
    }


def snapshot_info(path: Path | None) -> dict[str, Any]:
    if not path:
        return {"present": False, "path": "", "metrics": {}}
    if not path.exists():
        return {"present": False, "path": str(path), "metrics": {}}
    snapshot = production_snapshot.load_json(path)
    return {
        "present": True,
        "path": str(path),
        "metrics": production_snapshot.extract_metrics(snapshot),
    }


def build_evidence(
    *,
    frontend_url: str,
    backend_url: str,
    release_archive: Path | None = None,
    snapshot_path: Path | None = None,
    check_live: bool = False,
    require_cos_media: bool = True,
) -> dict[str, Any]:
    configs = domestic_migration_status.read_configs(ROOT)
    release_archive = release_archive or latest_release_archive(ROOT / "dist")
    domestic_report = domestic_migration_status.build_report(
        root=ROOT,
        backend_url=backend_url,
        check_live=check_live,
        require_cos_media=require_cos_media,
    )
    return {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git": {
            "branch": run_git(["branch", "--show-current"]),
            "commit": run_git(["rev-parse", "HEAD"]),
            "shortCommit": run_git(["rev-parse", "--short", "HEAD"]),
            "dirty": bool(run_git(["status", "--porcelain"])),
        },
        "urls": {
            "frontend": frontend_url.rstrip("/") + "/" if frontend_url else "",
            "backend": backend_url.rstrip("/") if backend_url else "",
            "configuredWebApiOrigin": configs.get("webApiOrigin", ""),
            "configuredMiniappApiBase": configs.get("miniappApiBase", ""),
            "miniappAppId": configs.get("miniappAppId", ""),
        },
        "release": release_info(release_archive),
        "snapshot": snapshot_info(snapshot_path),
        "domesticMigration": domestic_report,
    }


def status_mark(ok: bool) -> str:
    return "OK" if ok else "BLOCKED"


def render_markdown(evidence: dict[str, Any]) -> str:
    lines: list[str] = []
    git = evidence["git"]
    urls = evidence["urls"]
    release = evidence["release"]
    snapshot = evidence["snapshot"]
    migration = evidence["domesticMigration"]
    lines.extend(
        [
            "# FitHub 腾讯云国内上线证据报告",
            "",
            f"- 生成时间：{evidence['generatedAt']}",
            f"- Git 分支：{git['branch'] or 'unknown'}",
            f"- Git 提交：{git['shortCommit'] or 'unknown'}",
            f"- 工作区是否有未提交改动：{'是' if git['dirty'] else '否'}",
            "",
            "## 域名与配置",
            "",
            f"- 用户访问域名：{urls['frontend'] or '未提供'}",
            f"- API 域名：{urls['backend'] or '未提供'}",
            f"- Web config apiOrigin：{urls['configuredWebApiOrigin'] or '缺失'}",
            f"- 小程序 apiBase：{urls['configuredMiniappApiBase'] or '缺失'}",
            f"- 小程序 AppID：{urls['miniappAppId'] or '缺失'}",
            "",
            "## 发布包",
            "",
        ]
    )
    if release["present"]:
        lines.extend(
            [
                f"- 发布包：{release['path']}",
                f"- SHA256：{release['sha256']}",
                f"- 大小：{release['sizeBytes']} bytes",
            ]
        )
    else:
        lines.append("- 发布包：未找到")

    lines.extend(["", "## 国内迁移状态", ""])
    for item in migration["items"]:
        lines.append(f"- [{status_mark(bool(item['ok']))}] {item['label']}：{item['detail']}")
    lines.extend(["", f"结论：{migration['status']}，阻断项 {migration['blockerCount']} 个。", ""])

    lines.extend(["## 数据快照", ""])
    if snapshot["present"]:
        lines.append(f"- 快照文件：{snapshot['path']}")
        for key in production_snapshot.CRITICAL_METRIC_KEYS:
            lines.append(f"- {key}: {int(snapshot['metrics'].get(key) or 0)}")
    else:
        lines.append("- 快照文件：未提供或不存在")

    lines.extend(
        [
            "",
            "## 上线判定",
            "",
            "- `domesticMigration.status` 必须为 `ready`。",
            "- 发布包 SHA256 必须与实际上传到腾讯云服务器的文件一致。",
            "- 数据快照关键指标发布前后不能异常下降。",
            "- 最终还需要运行 `npm run check:final -- --production-frontend-url ... --production-backend-url ... --verify-frontend-api-origin --require-cos-media`。",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(evidence: dict[str, Any], output_dir: Path, *, output: str = "") -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%SZ", time.gmtime())
    markdown_path = Path(output) if output else output_dir / f"fithub-tencent-launch-evidence-{stamp}.md"
    json_path = markdown_path.with_suffix(".json")
    markdown_path.write_text(render_markdown(evidence), encoding="utf-8")
    json_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return markdown_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a FitHub Tencent Cloud launch evidence report.")
    parser.add_argument("--frontend-url", default="", help="Final user-facing web URL, e.g. https://app.yourdomain.com/")
    parser.add_argument("--backend-url", default="", help="Final API URL, e.g. https://api.yourdomain.com")
    parser.add_argument("--release-archive", default="", help="Release archive to record. Defaults to latest dist archive.")
    parser.add_argument("--snapshot", default="", help="Optional production snapshot JSON to summarize.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--output", default="", help="Optional markdown output path.")
    parser.add_argument("--check-live", action="store_true", help="Include live backend readiness in the report.")
    parser.add_argument("--allow-non-cos-media", action="store_true", help="Do not require Tencent COS media in readiness.")
    args = parser.parse_args()

    try:
        evidence = build_evidence(
            frontend_url=args.frontend_url,
            backend_url=args.backend_url,
            release_archive=Path(args.release_archive).expanduser() if args.release_archive else None,
            snapshot_path=Path(args.snapshot).expanduser() if args.snapshot else None,
            check_live=args.check_live,
            require_cos_media=not args.allow_non_cos_media,
        )
        markdown_path, json_path = write_outputs(evidence, Path(args.output_dir), output=args.output)
    except (OSError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"FitHub launch evidence failed: {exc}", file=sys.stderr)
        return 1

    print(f"Launch evidence written: {markdown_path}")
    print(f"Launch evidence JSON: {json_path}")
    if not evidence["domesticMigration"]["ready"]:
        print("Warning: domestic migration is still blocked. Do not treat this report as approval to launch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
