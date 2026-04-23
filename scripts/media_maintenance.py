#!/usr/bin/env python3
"""Inspect and clean stale media objects stored in Supabase Storage."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from server import (  # noqa: E402
    collect_referenced_media_paths,
    collect_session_draft_media_paths,
    delete_media_asset,
    iter_media_bucket_objects,
    load_state,
    now_utc,
    parse_optional_iso_datetime,
    supabase_media_storage_enabled,
)


def derive_object_timestamp(path, entry):
    for key in ("updated_at", "created_at", "last_accessed_at"):
        parsed = parse_optional_iso_datetime(entry.get(key))
        if parsed:
            return parsed

    parts = [segment for segment in str(path or "").split("/") if segment]
    if len(parts) >= 4 and all(part.isdigit() for part in parts[1:4]):
        year, month, day = (int(parts[1]), int(parts[2]), int(parts[3]))
        try:
            return now_utc().replace(year=year, month=month, day=day, hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            return None
    return None


def collect_bucket_inventory():
    inventory = []
    for entry in iter_media_bucket_objects():
        path = str(entry.get("path") or "").strip().lstrip("/")
        if not path:
            continue
        timestamp = derive_object_timestamp(path, entry)
        inventory.append(
            {
                "path": path,
                "createdAt": timestamp,
                "sizeBytes": int((entry.get("metadata") or {}).get("size") or entry.get("size") or 0),
            }
        )
    return inventory


def classify_media_objects(state, *, stale_after_hours):
    referenced = collect_referenced_media_paths(state)
    draft_paths = collect_session_draft_media_paths(state)
    inventory = collect_bucket_inventory()
    cutoff = now_utc() - timedelta(hours=max(1, stale_after_hours))

    report = {
        "referenced": [],
        "activeDrafts": [],
        "orphanCandidates": [],
        "recentUnreferenced": [],
    }

    for item in inventory:
        path = item["path"]
        created_at = item["createdAt"]
        if path in referenced:
            report["referenced"].append(item)
            continue
        if path in draft_paths:
            report["activeDrafts"].append(item)
            continue
        if created_at and created_at >= cutoff:
            report["recentUnreferenced"].append(item)
            continue
        report["orphanCandidates"].append(item)

    return report


def summarize_group(items):
    summary = Counter()
    total_bytes = 0
    for item in items:
        category = item["path"].split("/", 1)[0] if item.get("path") else "unknown"
        summary[category] += 1
        total_bytes += int(item.get("sizeBytes") or 0)
    return summary, total_bytes


def print_report(report):
    for key, label in (
        ("referenced", "已被引用"),
        ("activeDrafts", "会话中的草稿"),
        ("recentUnreferenced", "最近未引用（暂不删除）"),
        ("orphanCandidates", "过期未引用候选"),
    ):
        summary, total_bytes = summarize_group(report[key])
        print(f"\n{label}: {len(report[key])} 个对象 / {total_bytes} bytes")
        for category, count in summary.items():
            print(f"  - {category}: {count}")

    if report["orphanCandidates"]:
        print("\n前 20 个过期未引用对象：")
        for item in report["orphanCandidates"][:20]:
            created_at = item["createdAt"].isoformat() if item["createdAt"] else "unknown"
            print(f"  - {item['path']} ({item['sizeBytes']} bytes, {created_at})")


def delete_orphans(report):
    deleted = []
    for item in report["orphanCandidates"]:
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
    report = classify_media_objects(state, stale_after_hours=args.age_hours)
    print_report(report)

    if not args.delete:
        print("\n当前是只读报告模式；如需执行删除，请加 --delete。")
        return 0

    deleted = delete_orphans(report)
    print(f"\n已删除 {len(deleted)} 个对象。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
