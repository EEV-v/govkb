"""Validation command."""

from __future__ import annotations

import sys
from pathlib import Path

from govkb.core.contracts import load_project_bundle


def run_validate(args) -> int:
    """Validate a governed project package."""
    project_root = Path(args.project_root).resolve()
    bundle, result = load_project_bundle(project_root)

    print(f"Project root: {bundle.project_root}")
    print(f"Governed root: {bundle.governed_root}")
    print(f"Capabilities loaded: {len(bundle.capabilities)}")
    print(f"Adapters loaded: {len(bundle.adapters)}")
    print(f"Releases loaded: {len(bundle.releases)}")

    for message in result.warnings:
        print(f"warning: {message.location}: {message.message}")
    for message in result.errors:
        print(f"error: {message.location}: {message.message}", file=sys.stderr)

    if result.errors:
        print(f"Validation failed with {len(result.errors)} error(s).", file=sys.stderr)
        return 1

    print("Validation passed.")
    return 0
