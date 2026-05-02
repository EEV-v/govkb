"""Validation command."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from govkb.core.contracts import load_project_bundle
from govkb.core.governed_skill import validate_governed_skill_bundle
from govkb.core.kb_bootstrap import bundle_kb_health_messages


def run_validate(args) -> int:
    """Validate a governed project package."""
    project_root = Path(args.project_root).resolve()
    bundle, result = load_project_bundle(project_root)
    strict_result = None
    if getattr(args, "strict", False):
        strict_result = validate_governed_skill_bundle(project_root, bundle)

    kb_health = bundle_kb_health_messages(project_root, bundle)
    if getattr(args, "json", False):
        payload = {
            "projectRoot": str(bundle.project_root),
            "governedRoot": str(bundle.governed_root),
            "capabilitiesLoaded": len(bundle.capabilities),
            "adaptersLoaded": len(bundle.adapters),
            "releasesLoaded": len(bundle.releases),
            "errors": [{"location": message.location, "message": message.message} for message in result.errors],
            "warnings": [
                {"location": message.location, "message": message.message}
                for message in (*result.warnings, *kb_health)
            ],
            "valid": not result.errors and (strict_result is None or strict_result.ok),
        }
        if strict_result is not None:
            payload["strictIssues"] = [issue.as_dict() for issue in strict_result.issues]
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload["valid"] else 1

    print(f"Project root: {bundle.project_root}")
    print(f"Governed root: {bundle.governed_root}")
    print(f"Capabilities loaded: {len(bundle.capabilities)}")
    print(f"Adapters loaded: {len(bundle.adapters)}")
    print(f"Releases loaded: {len(bundle.releases)}")

    for message in result.warnings:
        print(f"warning: {message.location}: {message.message}")
    for message in kb_health:
        print(f"warning: {message.location}: {message.message}")
    for message in result.errors:
        print(f"error: {message.location}: {message.message}", file=sys.stderr)
    if strict_result is not None:
        for issue in strict_result.issues:
            stream = sys.stderr if issue.severity == "error" else sys.stdout
            print(f"strict {issue.severity}: {issue.rule_id}: {issue.location}: {issue.message}", file=stream)

    strict_errors = strict_result.errors if strict_result is not None else ()
    if result.errors or strict_errors:
        error_count = len(result.errors) + len(strict_errors)
        print(f"Validation failed with {error_count} error(s).", file=sys.stderr)
        return 1

    if strict_result is not None:
        print("Strict validation passed.")
    print("Validation passed.")
    return 0
