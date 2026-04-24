#!/usr/bin/env python3
"""Inspect and clean stale media objects stored in Supabase Storage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from server import (  # noqa: E402
    build_media_maintenance_report,
    delete_media_asset,
    load_state,
    supabase_media_storage_enabled,
)


def print_report(report):
    summary_map = report.get("summary") or {}
    groups = report.get("report") or {}
    for key, label in (
        ("referenced", "已被引用"),
        ("activeDrafts", "会话中的草稿"),
        ("recentUnreferenced", "最近未引用（暂不删除）"),
        ("orphanCandidates", "过期未引用候选"),
    ):
        items = groups.get(key, [])
        summary = summary_map.get(key, {})
        print(f"\n{label}: {len(items)} 个对象 / {int(summary.get('sizeBytes') or 0)} bytes")
        for category, count in (summary.get("byCategory") or {}).items():
            print(f"  - {category}: {count}")

    if groups.get("orphanCandidates"):
        print("\n前 20 个过期未引用对象：")
        for item in groups["orphanCandidates"][:20]:
            created_at = item.get("createdAt") or "unknown"
            print(f"  - {item['path']} ({item['sizeBytes']} bytes, {created_at})")


def delete_orphans(report):
    deleted = []
    for item in (report.get("report") or {}).get("orphanCandidates", []):
        deleted.extend(delete_media_asset({"storagePath": item["path"]}))
    return deleted


def main():
    parser = argparse.ArgumentParser(description="Inspect and clean stale FitHub media objects.")
    parser.add_argument("--age-hours", type=int, default=24, help="Delete/report only objects older than this age.")
    parser.add_argument("--delete", action="store_true", help="Actually delete orphan candidate objects.")
    args = parser.parse_args()

    if not supabase_media_storage_enabled():
        print("Supabase Storage 未启用，跳过媒体清理。")
        return 0

    state = load_state()
    report = build_media_maintenance_report(state, stale_after_hours=args.age_hours, delete=args.delete)
    print_report(report)

    if not args.delete:
        print("\n当前是只读报告模式；如需执行删除，请加 --delete。")
        return 0

    deleted = report.get("deletedPaths") or delete_orphans(report)
    print(f"\n已删除 {len(deleted)} 个对象。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
