"""Candidate capability commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tomllib

from govkb.adapters.codex.materialize import apply_codex_materialization
from govkb.core.automation import automation_policy_from_manifest
from govkb.core.candidates import candidate_default_capability_id
from govkb.core.candidates import candidate_is_review_approved
from govkb.core.candidates import list_candidates
from govkb.core.candidates import load_candidate
from govkb.core.candidates import stage_candidate_from_session
from govkb.core.contracts import load_project_bundle
from govkb.core.install_state import default_codex_home
from govkb.core.ids import normalize_identifier
from govkb.core.project import resolve_project_root
from govkb.commands.create_capability import run_create_capability


def _candidate_summary(candidate_root: Path, data: dict[str, object]) -> dict[str, object]:
    proposal = data.get("proposal") if isinstance(data.get("proposal"), dict) else {}
    suggested = proposal.get("capability_id") if isinstance(proposal, dict) else None
    status = data.get("status")
    candidate_id = data.get("id")
    occurrences = data.get("occurrences")
    normalized_status = status.strip() if isinstance(status, str) else "unknown"
    return {
        "id": candidate_id if isinstance(candidate_id, str) and candidate_id else candidate_root.name,
        "status": normalized_status,
        "occurrences": occurrences if isinstance(occurrences, int) and not isinstance(occurrences, bool) else 0,
        "suggestedCapabilityId": suggested if isinstance(suggested, str) and suggested else None,
        "activationState": "activated" if normalized_status == "activated" else "not-activated",
        "path": str(candidate_root),
    }


def build_candidates_payload(project_root: Path) -> dict[str, object]:
    """Build the machine-readable candidate list payload."""
    resolved_root = Path(project_root).resolve()
    candidates: list[dict[str, object]] = []
    for candidate_root in list_candidates(resolved_root):
        data = tomllib.loads((candidate_root / "candidate.toml").read_text(encoding="utf-8"))
        candidates.append(_candidate_summary(candidate_root, data))
    return {
        "schemaVersion": 1,
        "projectRoot": str(resolved_root),
        "candidates": candidates,
    }


def run_candidates(args) -> int:
    """Run candidate subcommands."""
    action = getattr(args, "candidate_action", "")
    if action == "stage":
        return _run_stage(args)
    if action == "list":
        return _run_list(args)
    if action == "auto-create-ready":
        return _run_auto_create_ready(args)
    print(f"error: unsupported candidates action: {action}", file=sys.stderr)
    return 1


def _run_stage(args) -> int:
    project_root = Path(args.project_root).resolve()
    session_file = Path(args.session_file).expanduser().resolve()
    if not session_file.is_file():
        print(f"error: session file not found: {session_file}", file=sys.stderr)
        return 1
    semantic_seed = None
    semantic_seed_file = getattr(args, "semantic_seed_file", None)
    if semantic_seed_file:
        seed_path = Path(semantic_seed_file).expanduser().resolve()
        if not seed_path.is_file():
            print(f"error: semantic seed file not found: {seed_path}", file=sys.stderr)
            return 1
        try:
            semantic_seed = json.loads(seed_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"error: invalid semantic seed file {seed_path}: {exc}", file=sys.stderr)
            return 1
        if semantic_seed is not None and not isinstance(semantic_seed, dict):
            print(f"error: semantic seed file must contain one JSON object: {seed_path}", file=sys.stderr)
            return 1
    try:
        result = stage_candidate_from_session(project_root, session_file, semantic_seed=semantic_seed)
    except Exception as exc:
        print(f"error: could not stage candidate: {exc}", file=sys.stderr)
        return 1
    created = "created" if result.created else "updated"
    print(
        f"{created} candidate {result.candidate_id}: "
        f"status={result.status} occurrences={result.occurrences} "
        f"suggested={result.default_capability_id} path={result.candidate_root}"
    )
    return 0


def _run_list(args) -> int:
    project_root = Path(args.project_root).resolve()
    if getattr(args, "json", False):
        print(json.dumps(build_candidates_payload(project_root), indent=2, sort_keys=True))
        return 0

    candidates = list_candidates(project_root)
    if not candidates:
        print("No candidates found.")
        return 0
    for candidate_root in candidates:
        data = tomllib.loads((candidate_root / "candidate.toml").read_text(encoding="utf-8"))
        proposal = data.get("proposal") if isinstance(data.get("proposal"), dict) else {}
        suggested = proposal.get("capability_id") if isinstance(proposal, dict) else None
        parts = [
            str(data.get("id", candidate_root.name)),
            f"status={data.get('status', 'unknown')}",
            f"occurrences={data.get('occurrences', 0)}",
        ]
        if isinstance(suggested, str) and suggested:
            parts.append(f"suggested={suggested}")
        parts.append(f"path={candidate_root}")
        print(" ".join(parts))
    return 0


def _scope_is_complete(candidate_data: dict[str, object]) -> bool:
    scope = candidate_data.get("scope")
    if not isinstance(scope, dict):
        return False
    summary = scope.get("summary")
    in_scope = scope.get("in_scope")
    return isinstance(summary, str) and bool(summary.strip()) and isinstance(in_scope, list) and len(in_scope) > 0


def _candidate_status(candidate_data: dict[str, object]) -> str:
    status = candidate_data.get("status")
    return status.strip() if isinstance(status, str) else ""


def _candidate_occurrences(candidate_data: dict[str, object]) -> int:
    occurrences = candidate_data.get("occurrences")
    return occurrences if isinstance(occurrences, int) and not isinstance(occurrences, bool) else 0


def _auto_create_candidate_rows(project_root: Path, min_occurrences: int) -> tuple[list[tuple[str, str]], list[str]]:
    ready_rows: list[tuple[str, str]] = []
    skipped: list[str] = []
    for candidate_root in list_candidates(project_root):
        try:
            candidate_id = normalize_identifier(candidate_root.name)
            _, candidate_data = load_candidate(project_root, candidate_id)
        except Exception as exc:  # noqa: BLE001 - keep scanning remaining candidates.
            skipped.append(f"{candidate_root.name}: could not load candidate ({exc})")
            continue
        status = _candidate_status(candidate_data)
        if status == "activated":
            continue
        if status != "ready-for-review":
            skipped.append(f"{candidate_id}: status={status or 'unknown'}")
            continue
        occurrences = _candidate_occurrences(candidate_data)
        if occurrences < min_occurrences:
            skipped.append(f"{candidate_id}: occurrences={occurrences} below min={min_occurrences}")
            continue
        if not _scope_is_complete(candidate_data):
            skipped.append(f"{candidate_id}: scope metadata incomplete")
            continue
        if not candidate_is_review_approved(candidate_data):
            skipped.append(f"{candidate_id}: review status not approved")
            continue
        capability_id = candidate_default_capability_id(candidate_data, candidate_id)
        ready_rows.append((candidate_id, capability_id))
    return ready_rows, skipped


def _run_auto_create_ready(args) -> int:
    project_root = resolve_project_root(Path(args.project_root).resolve())
    bundle, result = load_project_bundle(project_root)
    for message in result.warnings:
        print(f"warning: {message.location}: {message.message}")
    for message in result.errors:
        print(f"error: {message.location}: {message.message}", file=sys.stderr)
    if result.errors:
        return 1

    policy = automation_policy_from_manifest(bundle.project_manifest)
    if not policy.auto_create_capabilities:
        print("Auto-create: disabled in .governed/project.toml")
        return 0

    ready_rows, skipped = _auto_create_candidate_rows(project_root, policy.auto_create_min_occurrences)
    existing_capability_ids = set(bundle.capabilities)
    planned_capability_ids = set(existing_capability_ids)
    created_rows: list[tuple[str, str]] = []

    for candidate_id, capability_id in ready_rows:
        if capability_id in planned_capability_ids:
            skipped.append(f"{candidate_id}: capability already exists or is already planned as {capability_id}")
            continue
        create_exit = run_create_capability(
            argparse.Namespace(
                capability_id=None,
                project_root=project_root,
                from_candidate=candidate_id,
                require_strict_activation=True,
            )
        )
        if create_exit != 0:
            skipped.append(f"{candidate_id}: strict activation gate failed for {capability_id}")
            continue
        created_rows.append((candidate_id, capability_id))
        planned_capability_ids.add(capability_id)

    if not created_rows:
        print("Auto-create: no ready candidates matched policy")
        for row in skipped:
            print(f"- skipped {row}")
        return 0

    if getattr(args, "assistant", "codex") != "codex":
        print(f"error: unsupported assistant: {args.assistant}", file=sys.stderr)
        return 1

    refreshed_bundle, refreshed_result = load_project_bundle(project_root)
    for message in refreshed_result.warnings:
        print(f"warning: {message.location}: {message.message}")
    for message in refreshed_result.errors:
        print(f"error: {message.location}: {message.message}", file=sys.stderr)
    if refreshed_result.errors:
        return 1

    codex_home = (getattr(args, "codex_home", None) or default_codex_home()).resolve()
    applied = apply_codex_materialization(
        project_root=project_root,
        bundle=refreshed_bundle,
        codex_home_override=codex_home,
        requested_release=None,
        requested_revision=None,
    )
    print(f"Auto-create: created {len(created_rows)} capability(s)")
    for candidate_id, capability_id in created_rows:
        print(f"- {candidate_id} -> {capability_id}")
    print(f"Auto-create: applied Codex materialization to {codex_home}")
    print(f"Auto-create: install state {applied.state_path}")
    for row in skipped:
        print(f"- skipped {row}")
    return 0
