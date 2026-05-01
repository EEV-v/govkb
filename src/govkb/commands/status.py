"""Status command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from govkb.core.contracts import load_project_bundle
from govkb.core.contracts import ProjectBundle
from govkb.core.contracts import ValidationResult
from govkb.core.install_state import install_state_path
from govkb.core.install_state import load_install_state
from govkb.core.kb_bootstrap import bundle_kb_health_messages


def _validation_message_payload(message) -> dict[str, str]:
    return {"location": message.location, "message": message.message}


def _install_state_payload(bundle: ProjectBundle, codex_home: Path | None) -> dict[str, Any]:
    if codex_home is None:
        return {
            "status": "not-requested",
            "statePath": None,
            "appliedRevision": None,
            "appliedRelease": None,
            "appliedAt": None,
            "materializedCapabilities": [],
        }
    if not bundle.project_id:
        return {
            "status": "unavailable",
            "statePath": None,
            "appliedRevision": None,
            "appliedRelease": None,
            "appliedAt": None,
            "materializedCapabilities": [],
        }

    state_path = install_state_path(codex_home.resolve(), bundle.project_id, "codex")
    state = load_install_state(state_path)
    if state is None:
        return {
            "status": "missing",
            "statePath": str(state_path),
            "appliedRevision": None,
            "appliedRelease": None,
            "appliedAt": None,
            "materializedCapabilities": [],
        }

    capabilities: list[dict[str, str | None]] = []
    for capability in state.get("capabilities", []):
        if not isinstance(capability, dict):
            continue
        capability_id = capability.get("capability_id")
        materialized = capability.get("materialized_skill_id")
        capabilities.append(
            {
                "capabilityId": capability_id if isinstance(capability_id, str) else None,
                "materializedSkillId": materialized if isinstance(materialized, str) else None,
            }
        )

    return {
        "status": "present",
        "statePath": str(state_path),
        "appliedRevision": state.get("revision"),
        "appliedRelease": state.get("release"),
        "appliedAt": state.get("applied_at"),
        "materializedCapabilities": capabilities,
    }


def build_status_payload(project_root: Path, codex_home: Path | None = None) -> tuple[ProjectBundle, ValidationResult, dict[str, Any]]:
    """Build the machine-readable project status payload."""
    bundle, result = load_project_bundle(project_root.resolve())
    kb_health = bundle_kb_health_messages(bundle.project_root, bundle) if bundle.governed_root.is_dir() else ()
    payload: dict[str, Any] = {
        "schemaVersion": 1,
        "projectRoot": str(bundle.project_root),
        "governedRoot": str(bundle.governed_root),
        "project": {
            "id": bundle.project_id,
            "currentRelease": bundle.project_manifest_current_release or "unreleased",
        },
        "validation": {
            "status": "error" if result.errors else "ok",
            "warnings": [_validation_message_payload(message) for message in result.warnings],
            "errors": [_validation_message_payload(message) for message in result.errors],
        },
        "kbHealth": {
            "warnings": [_validation_message_payload(message) for message in kb_health],
            "suggestedRemediation": "govkb init-kb --all" if kb_health else None,
        },
        "capabilities": [
            {
                "id": capability.capability_id,
                "name": capability.capability_name,
                "governed": capability.governed,
                "description": capability.description,
                "memoryEnabled": capability.memory_enabled,
                "requiresExplicitAcceptance": capability.requires_explicit_acceptance,
            }
            for capability in sorted(bundle.capabilities.values(), key=lambda item: item.capability_id)
        ],
        "adapters": sorted(bundle.adapters),
        "releases": sorted(bundle.releases),
        "installState": {
            "codex": _install_state_payload(bundle, codex_home),
        },
    }
    return bundle, result, payload


def run_status(args) -> int:
    """Show a governed package summary."""
    codex_home = Path(args.codex_home).resolve() if args.codex_home else None
    bundle, result, payload = build_status_payload(Path(args.project_root).resolve(), codex_home)
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1 if result.errors else 0

    print(f"Project root: {bundle.project_root}")
    print(f"Governed root: {bundle.governed_root}")
    print(f"Project id: {bundle.project_id or '<unknown>'}")
    print(f"Current release: {bundle.project_manifest_current_release or 'unreleased'}")
    print(f"Capabilities: {len(bundle.capabilities)}")
    print(f"Adapters: {len(bundle.adapters)}")
    print(f"Releases: {len(bundle.releases)}")
    for message in result.warnings:
        print(f"warning: {message.location}: {message.message}")
    if bundle.project_id and codex_home:
        state_path = install_state_path(codex_home, bundle.project_id, "codex")
        state = load_install_state(state_path)
        if state is None:
            print(f"Codex install state: missing ({state_path})")
        else:
            print(f"Codex install state: {state_path}")
            print(f"Applied revision: {state.get('revision', '<unknown>')}")
            print(f"Applied release: {state.get('release', '<unknown>')}")
            print(f"Applied at: {state.get('applied_at', '<unknown>')}")
            print(f"Materialized capabilities: {len(state.get('capabilities', []))}")
            for capability in state.get("capabilities", []):
                if not isinstance(capability, dict):
                    continue
                capability_id = capability.get("capability_id", "<unknown>")
                skill_id = capability.get("materialized_skill_id") or capability_id
                print(f"- {capability_id} -> {skill_id}")
    kb_health = bundle_kb_health_messages(bundle.project_root, bundle)
    if kb_health:
        print(f"KB health warnings: {len(kb_health)}")
        for message in kb_health:
            print(f"- {message.message}")
        print("Suggested remediation: govkb init-kb --all")
    else:
        print("KB health warnings: none")
    if result.errors:
        print(f"Validation status: {len(result.errors)} error(s)")
        return 1
    print("Validation status: ok")
    return 0
