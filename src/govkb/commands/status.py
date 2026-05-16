"""Status command."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from govkb.core.contracts import load_project_bundle
from govkb.core.contracts import ProjectBundle
from govkb.core.contracts import ValidationResult
from govkb.core.install_state import install_state_path
from govkb.core.install_state import load_install_state
from govkb.core.kb_bootstrap import bundle_kb_health_messages
from govkb.adapters.codex.promote import promote_codex_memory


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


def _git_output(project_root: Path, args: list[str]) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(project_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    output = proc.stdout.strip()
    return output or None


def _project_git_payload(project_root: Path) -> dict[str, Any]:
    revision = _git_output(project_root, ["rev-parse", "--verify", "HEAD"])
    status = _git_output(project_root, ["status", "--short", "--", ".governed"])
    return {
        "gitRevision": revision,
        "governedDirty": bool(status),
        "governedStatus": status.splitlines() if status else [],
    }


def _local_memory_update_payload(bundle: ProjectBundle, codex_home: Path | None, validation: ValidationResult) -> dict[str, Any]:
    if codex_home is None or validation.errors:
        return {
            "available": False,
            "safePromotionCount": 0,
            "rejectedCount": 0,
            "pendingCount": 0,
            "items": [],
        }
    result = promote_codex_memory(
        project_root=bundle.project_root,
        bundle=bundle,
        codex_home_override=codex_home,
        preview=True,
        auto=True,
        write_report=False,
    )
    items = [
        {
            "capabilityId": item.capability_id,
            "reason": item.reason,
            "additions": len(item.additions),
            "repoPath": str(item.repo_path),
            "localPath": str(item.local_path),
        }
        for item in result.items
    ]
    safe_count = sum(1 for item in result.items if item.reason.startswith("staged:") and item.additions)
    rejected_count = sum(1 for item in result.items if item.reason.startswith("rejected"))
    return {
        "available": bool(result.items),
        "safePromotionCount": safe_count,
        "rejectedCount": rejected_count,
        "pendingCount": len(result.items),
        "items": items,
    }


def _skill_update_payload(
    project_git: dict[str, Any],
    install_state: dict[str, Any],
    local_memory: dict[str, Any],
) -> dict[str, Any]:
    applied_revision = install_state.get("appliedRevision")
    git_revision = project_git.get("gitRevision")
    governed_dirty = bool(project_git.get("governedDirty"))
    if install_state.get("status") == "missing":
        state = "not-applied"
    elif install_state.get("status") != "present":
        state = "unknown"
    elif governed_dirty:
        state = "workspace-changes"
    elif local_memory["safePromotionCount"] or local_memory["rejectedCount"]:
        state = "learned-updates"
    elif git_revision and applied_revision and git_revision != applied_revision:
        state = "apply-available"
    else:
        state = "current"

    return {
        "state": state,
        "repoRevision": git_revision,
        "appliedRevision": applied_revision,
        "governedDirty": governed_dirty,
        "pendingLocalMemory": local_memory,
    }


def build_status_payload(project_root: Path, codex_home: Path | None = None) -> tuple[ProjectBundle, ValidationResult, dict[str, Any]]:
    """Build the machine-readable project status payload."""
    bundle, result = load_project_bundle(project_root.resolve())
    kb_health = bundle_kb_health_messages(bundle.project_root, bundle) if bundle.governed_root.is_dir() else ()
    project_git = _project_git_payload(bundle.project_root)
    install_state = _install_state_payload(bundle, codex_home)
    local_memory = _local_memory_update_payload(bundle, codex_home, result)
    payload: dict[str, Any] = {
        "schemaVersion": 1,
        "projectRoot": str(bundle.project_root),
        "governedRoot": str(bundle.governed_root),
        "project": {
            "id": bundle.project_id,
            "currentRelease": bundle.project_manifest_current_release or "unreleased",
            **project_git,
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
                "path": str(capability.capability_root),
                "instructionsPath": str(capability.capability_root / "instructions.md"),
                "memoryTargets": [
                    {
                        "name": target.name,
                        "path": target.path,
                        "absolutePath": str(capability.capability_root / target.path),
                        "sections": list(target.sections),
                    }
                    for target in capability.targets
                ],
                "aliases": list(capability.aliases),
                "lifecycleState": capability.lifecycle.state,
                "migrationStatus": capability.migration_status,
            }
            for capability in sorted(bundle.capabilities.values(), key=lambda item: item.capability_id)
        ],
        "adapters": sorted(bundle.adapters),
        "releases": sorted(bundle.releases),
        "installState": {
            "codex": install_state,
        },
        "skillUpdates": _skill_update_payload(project_git, install_state, local_memory),
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
    skill_updates = payload["skillUpdates"]
    local_memory = skill_updates["pendingLocalMemory"]
    print(f"Skill updates: {skill_updates['state']}")
    if local_memory["available"]:
        print(
            "Local memory pending: "
            f"{local_memory['pendingCount']} item(s), "
            f"{local_memory['safePromotionCount']} safe, "
            f"{local_memory['rejectedCount']} rejected"
        )
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
