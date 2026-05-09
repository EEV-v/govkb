"""Promote local governed assistant changes back into the repo package."""

from __future__ import annotations

import sys

from govkb.adapters.codex.promote import promote_codex_memory_in_isolated_worktree
from govkb.adapters.codex.promote import promote_codex_memory
from govkb.core.contracts import load_project_bundle


def run_promote(args) -> int:
    """Run governed promotion for an assistant target."""
    assistant = getattr(args, "assistant", "codex")
    if assistant != "codex":
        print(f"error: unsupported assistant for promote: {assistant}", file=sys.stderr)
        return 2

    auto = getattr(args, "auto", False)
    requested_preview = getattr(args, "preview", False)
    if auto and not requested_preview:
        result = promote_codex_memory_in_isolated_worktree(
            project_root=args.project_root.resolve(),
            codex_home_override=getattr(args, "codex_home", None),
        )
    else:
        bundle, validation = load_project_bundle(args.project_root)
        for warning in validation.warnings:
            print(f"warning: {warning.location}: {warning.message}", file=sys.stderr)
        if validation.errors:
            for error in validation.errors:
                print(f"error: {error.location}: {error.message}", file=sys.stderr)
            return 1

        result = promote_codex_memory(
            project_root=args.project_root.resolve(),
            bundle=bundle,
            codex_home_override=getattr(args, "codex_home", None),
            preview=requested_preview,
            auto=auto,
            write_report=not auto,
        )

    print(f"Project: {result.project_id}")
    print("Assistant: codex")
    print(f"Mode: {'preview' if result.preview else 'apply'}")
    print(f"Trigger: {'auto' if result.auto else 'manual'}")
    print(f"Codex home: {result.codex_home}")
    print(f"Install state: {result.state_path}")
    print(f"Promoted: {result.promoted_count}")
    print(f"Rejected: {result.rejected_count}")
    print(f"Git: {result.git.message}")
    if auto:
        if result.isolation is not None:
            print(f"Auto isolation: {result.isolation.message}")
            if result.isolation.branch is not None:
                print(f"Auto branch: {result.isolation.branch}")
            if result.isolation.worktree_root is not None:
                print(f"Auto worktree: {result.isolation.worktree_root}")
        else:
            print("Auto trigger: active repo mutation skipped; run without --auto after review to promote.")
    if result.git.root is not None:
        print(f"Git root: {result.git.root}")
    if result.git.status_after:
        print("Git status after:")
        for line in result.git.status_after:
            print(f"  {line}")
    if result.report_path:
        print(f"Report: {result.report_path}")
    if result.digest_path:
        print(f"Digest: {result.digest_path}")
    if not result.items:
        print("No local governed memory changes to promote.")
    for item in result.items:
        status = "promoted" if item.promoted else "not promoted"
        print(f"- {item.capability_id}: {status}; {item.reason}")
        for addition in item.additions:
            print(f"  + {addition}")
    return 1 if result.rejected_count else 0
