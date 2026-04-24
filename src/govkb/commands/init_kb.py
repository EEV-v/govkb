"""KB bootstrap command."""

from __future__ import annotations

import os
from pathlib import Path
import sys

from govkb.adapters.codex.materialize import apply_codex_materialization
from govkb.core.contracts import load_project_bundle
from govkb.core.ids import normalize_identifier
from govkb.core.install_state import default_codex_home
from govkb.core.install_state import install_state_path
from govkb.core.install_state import load_install_state
from govkb.core.kb_bootstrap import bootstrap_capability
from govkb.core.kb_bootstrap import bundle_kb_health_messages
from govkb.core.project import resolve_project_root


def _validation_exit(project_root: Path) -> int:
    bundle, result = load_project_bundle(project_root)
    health_messages = bundle_kb_health_messages(project_root, bundle)
    for message in result.warnings:
        print(f"warning: {message.location}: {message.message}")
    for message in health_messages:
        print(f"warning: {message.location}: {message.message}")
    for message in result.errors:
        print(f"error: {message.location}: {message.message}", file=sys.stderr)
    if result.errors:
        print("Validation result: failed", file=sys.stderr)
        return 1
    print("Validation result: ok")
    return 0


def _maybe_rematerialize_codex(project_root: Path, bundle, codex_home_override: Path | None) -> None:
    if "codex" not in bundle.adapters:
        return

    project_id = bundle.project_id
    if not project_id:
        return

    codex_home = (
        codex_home_override.resolve()
        if codex_home_override is not None
        else default_codex_home()
    )
    state_path = install_state_path(codex_home, project_id, "codex")
    install_state = load_install_state(state_path)
    if codex_home_override is None and install_state is None:
        return

    applied = apply_codex_materialization(
        project_root=project_root,
        bundle=bundle,
        codex_home_override=codex_home,
        requested_release=None,
        requested_revision=None,
    )
    print(f"Rematerialized Codex capabilities: {len(applied.capabilities)}")
    for item in applied.capabilities:
        print(f"- {item.capability_id} -> {item.materialized_skill_id}: {item.target_path}")
    for warning in applied.warnings:
        print(f"warning: {warning}")


def run_init_kb(args) -> int:
    """Bootstrap governed capability knowledge bases."""
    project_root = resolve_project_root(Path(args.project_root).resolve())
    bundle, result = load_project_bundle(project_root)
    for message in result.warnings:
        print(f"warning: {message.location}: {message.message}")
    for message in result.errors:
        print(f"error: {message.location}: {message.message}", file=sys.stderr)
    if result.errors:
        return 1

    requested_capability = getattr(args, "capability", None)
    run_all = bool(getattr(args, "all", False))
    if not requested_capability and not run_all:
        print("error: pass --capability <id> or --all", file=sys.stderr)
        return 1
    if requested_capability and run_all:
        print("error: choose either --capability or --all", file=sys.stderr)
        return 1

    capability_ids: list[str]
    if requested_capability:
        capability_id = normalize_identifier(requested_capability)
        if capability_id not in bundle.capabilities:
            print(f"error: unknown capability: {capability_id}", file=sys.stderr)
            return 1
        capability_ids = [capability_id]
    else:
        capability_ids = list(sorted(bundle.capabilities))

    for capability_id in capability_ids:
        contract = bundle.capabilities[capability_id]
        result_row = bootstrap_capability(project_root, contract)
        print(f"Capability: {capability_id}")
        print(f"Memory: {result_row.memory_path}")
        if result_row.added_facts:
            print("Added bullets:")
            for fact in result_row.added_facts:
                print(f"- {fact}")
        else:
            print("Added bullets: No KB update")
        print("Evidence files:")
        if result_row.evidence_paths:
            for path in result_row.evidence_paths:
                print(f"- {path}")
        else:
            print("- none")
        for warning in result_row.warnings:
            print(f"warning: {capability_id}: {warning}")

    codex_home_override = getattr(args, "codex_home", None)
    if codex_home_override is None:
        configured = os.environ.get("CODEX_HOME", "").strip()
        if configured:
            codex_home_override = Path(configured).expanduser()
    _maybe_rematerialize_codex(project_root, bundle, codex_home_override)

    print(f"Validation command: govkb validate {project_root}")
    return _validation_exit(project_root)
