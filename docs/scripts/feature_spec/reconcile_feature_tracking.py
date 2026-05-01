#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

from feature_spec_common import (
    build_tracking_lines,
    derive_feature_title,
    ensure_tracking_block,
    get_standard_paths,
    parse_tracking_block,
    read_text_if_exists,
    resolve_feature_dir,
    resolve_repo_root,
    write_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record optional GovKB feature-spec tracker or reference links in local artifacts."
    )
    parser.add_argument("feature_reference", help="Feature folder path or slug under the GovKB feature root.")
    parser.add_argument("--repo-root")
    parser.add_argument("--feature-title")
    parser.add_argument("--tracker-label", action="append", help="Reference label to write in the Tracking block.")
    parser.add_argument("--tracker-id", action="append", help="Reference identifier to write in the Tracking block.")
    parser.add_argument("--tracker-url", action="append", help="Reference URL to write in the Tracking block.")
    parser.add_argument(
        "--require-tracker",
        action="store_true",
        help="Treat a missing tracker/reference as a workflow blocker.",
    )
    parser.add_argument("--write-artifacts", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def as_list(values: Sequence[str] | None) -> List[str]:
    return list(values or [])


def trackers_from_args(args: argparse.Namespace) -> List[Dict[str, str]]:
    labels = as_list(args.tracker_label)
    ids = as_list(args.tracker_id)
    urls = as_list(args.tracker_url)
    count = max(len(labels), len(ids), len(urls))
    trackers: List[Dict[str, str]] = []
    for index in range(count):
        label = labels[index] if index < len(labels) else "Reference"
        identifier = ids[index] if index < len(ids) else ""
        url = urls[index] if index < len(urls) else ""
        if not identifier and not url:
            continue
        trackers.append({"label": label, "id": identifier, "url": url})
    return trackers


def merge_trackers(existing: Dict[str, Dict[str, str]], provided: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    merged: Dict[str, Dict[str, str]] = {
        label: {"label": label, "id": value.get("id", ""), "url": value.get("url", "")}
        for label, value in existing.items()
    }
    for tracker in provided:
        label = (tracker.get("label") or "Reference").strip()
        merged[label] = {
            "label": label,
            "id": (tracker.get("id") or "").strip(),
            "url": (tracker.get("url") or "").strip(),
        }
    return list(merged.values())


def incomplete_trackers(trackers: Sequence[Dict[str, str]]) -> List[str]:
    missing: List[str] = []
    for tracker in trackers:
        label = tracker.get("label") or "Reference"
        if not tracker.get("id"):
            missing.append(f"{label}: id")
        if not tracker.get("url"):
            missing.append(f"{label}: url")
    return missing


def update_tracking_artifacts(feature_dir: Path, trackers: Sequence[Dict[str, str]]) -> List[str]:
    tracking_lines = build_tracking_lines(trackers)
    if not tracking_lines:
        return []

    paths = get_standard_paths(feature_dir)
    artifact_keys = [
        "business",
        "spec_brief",
        "review_pack",
        "review_message",
        "scope_lock",
        "spec_handoff",
    ]
    updated: List[str] = []
    for key in artifact_keys:
        path = paths[key]
        content = read_text_if_exists(path)
        if content is None:
            continue
        write_text(path, ensure_tracking_block(content, tracking_lines))
        updated.append(str(path))
    return updated


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    feature_dir = resolve_feature_dir(repo_root, args.feature_reference)
    feature_title = derive_feature_title(feature_dir, args.feature_title)
    business_text = read_text_if_exists(get_standard_paths(feature_dir)["business"]) or ""

    existing = parse_tracking_block(business_text)
    provided = trackers_from_args(args)
    trackers = merge_trackers(existing, provided)
    missing_fields = incomplete_trackers(trackers)
    missing = []
    if args.require_tracker and not trackers:
        missing.append("tracker-reference")
    missing.extend(missing_fields)

    updated_paths: List[str] = []
    if args.write_artifacts and trackers and not missing_fields:
        updated_paths = update_tracking_artifacts(feature_dir, trackers)

    tracker_ready = not missing
    linkage_status = "configured" if trackers else "not-configured"
    if missing_fields:
        linkage_status = "incomplete"
    if args.require_tracker and not trackers:
        linkage_status = "missing-required"

    payload: Dict[str, Any] = {
        "featureDir": str(feature_dir),
        "featureTitle": feature_title,
        "trackerReady": tracker_ready,
        "missing": missing,
        "linkageStatus": [linkage_status],
        "resolvedTrackers": trackers,
        "updatedPaths": updated_paths,
        "confirmationRequired": bool(missing),
        "recommendedActions": [],
    }
    if args.require_tracker and not trackers:
        payload["recommendedActions"].append("Add a tracker/reference id and URL, or rerun without --require-tracker.")
    if missing_fields:
        payload["recommendedActions"].append("Provide both id and URL for every tracker/reference entry.")
    if not trackers and not args.require_tracker:
        payload["recommendedActions"].append("No tracker/reference configured; this is allowed for local GovKB specs.")

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Feature folder: {feature_dir}")
        print(f"Tracker/reference status: {linkage_status}")
        if trackers:
            for tracker in trackers:
                print(f"- {tracker['label']}: {tracker.get('id') or '(missing id)'} {tracker.get('url') or '(missing url)'}")
        if updated_paths:
            print("Updated artifacts:")
            for path in updated_paths:
                print(f"- {path}")
        if missing:
            print("Missing:")
            for item in missing:
                print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
