"""Governed capability management commands."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from govkb.core.capability_management import capability_summary_payload
from govkb.core.capability_management import merge_capabilities
from govkb.core.capability_management import rename_capability


def run_capabilities(args) -> int:
    """Run governed capability management subcommands."""
    action = getattr(args, "capability_action", "")
    if action == "list":
        return _run_list(args)
    if action == "rename":
        return _run_rename(args)
    if action == "merge":
        return _run_merge(args)
    print(f"error: unsupported capabilities action: {action}", file=sys.stderr)
    return 1


def _run_list(args) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        payload = capability_summary_payload(project_root)
    except Exception as exc:
        print(f"error: could not list capabilities: {exc}", file=sys.stderr)
        return 1
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print(f"Project: {payload['projectRoot']}")
    print(f"Governed root: {payload['governedRoot']}")
    print(f"Capabilities: {len(payload['capabilities'])}")
    for item in payload["capabilities"]:
        if not isinstance(item, dict):
            continue
        print(f"- {item.get('id')}: {item.get('name')} ({item.get('description')})")
    return 0


def _run_rename(args) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        result = rename_capability(project_root, args.old_capability_id, args.new_capability_id)
    except Exception as exc:
        print(f"error: could not rename capability: {exc}", file=sys.stderr)
        return 1
    if getattr(args, "json", False):
        print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"Renamed governed capability: {result.details['oldCapabilityId']} -> {result.details['newCapabilityId']}")
        print(f"Review changed files before committing: {len(result.changed_files)}")
    return 0


def _run_merge(args) -> int:
    project_root = Path(args.project_root).resolve()
    try:
        result = merge_capabilities(project_root, args.source_capability_id, args.target_capability_id)
    except Exception as exc:
        print(f"error: could not merge capabilities: {exc}", file=sys.stderr)
        return 1
    if getattr(args, "json", False):
        print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
    else:
        print(
            "Merged governed capability: "
            f"{result.details['sourceCapabilityId']} -> {result.details['targetCapabilityId']}"
        )
        print(f"Report: {result.details['reportPath']}")
        print(f"Review changed files before committing: {len(result.changed_files)}")
    return 0
