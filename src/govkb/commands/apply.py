"""Apply command."""

from __future__ import annotations

import sys
from pathlib import Path

from govkb.adapters.codex.materialize import apply_codex_materialization
from govkb.adapters.codex.materialize import preview_codex_materialization
from govkb.core.contracts import load_project_bundle


def run_codex_apply(args) -> int:
    """Preview or apply the first Codex materialization flow."""
    project_root = Path(args.project_root).resolve()
    bundle, result = load_project_bundle(project_root)

    for message in result.errors:
        print(f"error: {message.location}: {message.message}", file=sys.stderr)
    if result.errors:
        return 1

    if args.preview:
        preview = preview_codex_materialization(
            project_root=project_root,
            bundle=bundle,
            codex_home_override=args.codex_home,
            requested_release=args.release,
            requested_revision=args.revision,
        )
        print(f"Project: {preview.project_id}")
        print("Assistant: codex")
        print(f"Selected release: {preview.selected_release}")
        print(f"Selected revision: {preview.selected_revision}")
        print(f"Codex home: {preview.codex_home}")
        print(f"Install state: {preview.state_path}")
        print(f"Capabilities planned: {len(preview.capabilities)}")
        for item in preview.capabilities:
            print(
                f"- {item.capability_id} -> {item.materialized_skill_id}: {item.target_path} "
                f"(source={item.source_mode}; files={item.file_count})"
            )
        for warning in preview.warnings:
            print(f"warning: {warning}")
        return 0

    applied = apply_codex_materialization(
        project_root=project_root,
        bundle=bundle,
        codex_home_override=args.codex_home,
        requested_release=args.release,
        requested_revision=args.revision,
    )
    print(f"Project: {applied.project_id}")
    print("Assistant: codex")
    print(f"Selected release: {applied.selected_release}")
    print(f"Selected revision: {applied.selected_revision}")
    print(f"Codex home: {applied.codex_home}")
    print(f"Install state: {applied.state_path}")
    print(f"Capabilities materialized: {len(applied.capabilities)}")
    for item in applied.capabilities:
        backup_note = f"; backup={item.backup_path}" if item.backup_path else ""
        print(
            f"- {item.capability_id} -> {item.materialized_skill_id}: {item.target_path} "
            f"(source={item.source_mode}; files={item.file_count}{backup_note})"
        )
    for warning in applied.warnings:
        print(f"warning: {warning}")
    return 0
