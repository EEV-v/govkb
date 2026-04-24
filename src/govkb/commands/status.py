"""Status command."""

from __future__ import annotations

from pathlib import Path

from govkb.core.contracts import load_project_bundle
from govkb.core.install_state import install_state_path
from govkb.core.install_state import load_install_state
from govkb.core.kb_bootstrap import bundle_kb_health_messages


def run_status(args) -> int:
    """Show a governed package summary."""
    bundle, result = load_project_bundle(Path(args.project_root).resolve())
    print(f"Project root: {bundle.project_root}")
    print(f"Governed root: {bundle.governed_root}")
    print(f"Project id: {bundle.project_id or '<unknown>'}")
    print(f"Current release: {bundle.project_manifest_current_release or 'unreleased'}")
    print(f"Capabilities: {len(bundle.capabilities)}")
    print(f"Adapters: {len(bundle.adapters)}")
    print(f"Releases: {len(bundle.releases)}")
    for message in result.warnings:
        print(f"warning: {message.location}: {message.message}")
    if bundle.project_id and args.codex_home:
        state_path = install_state_path(Path(args.codex_home).resolve(), bundle.project_id, "codex")
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
