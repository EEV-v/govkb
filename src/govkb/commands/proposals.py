"""Capability-evolution proposal commands."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from govkb.core.project import resolve_project_root
from govkb.core.proposals import ProposalError
from govkb.core.proposals import apply_proposal
from govkb.core.proposals import build_proposals_payload
from govkb.core.proposals import list_proposals
from govkb.core.proposals import load_proposal
from govkb.core.proposals import proposal_summary


def run_proposals(args) -> int:
    """Run proposal subcommands."""
    action = getattr(args, "proposal_action", "")
    if action == "list":
        return _run_list(args)
    if action == "show":
        return _run_show(args)
    if action == "apply":
        return _run_apply(args)
    print(f"error: unsupported proposals action: {action}", file=sys.stderr)
    return 1


def _run_list(args) -> int:
    project_root = resolve_project_root(Path(args.project_root).resolve())
    if getattr(args, "json", False):
        print(json.dumps(build_proposals_payload(project_root), indent=2, sort_keys=True))
        return 0
    proposals = list_proposals(project_root)
    if not proposals:
        print("No proposals found.")
        return 0
    for proposal_root in proposals:
        try:
            _, data = load_proposal(project_root, proposal_root.name)
        except ProposalError as exc:
            print(f"warning: {proposal_root}: {exc}", file=sys.stderr)
            continue
        row = proposal_summary(proposal_root, data)
        output_paths = row.get("outputPaths")
        first_path = output_paths[0] if isinstance(output_paths, list) and output_paths else None
        parts = [
            str(row.get("id") or proposal_root.name),
            f"status={row.get('status') or 'unknown'}",
            f"target={row.get('targetCapability') or 'unknown'}",
            f"type={row.get('proposalType') or 'unknown'}",
            f"safety={row.get('safetyClass') or 'unknown'}",
        ]
        if first_path:
            parts.append(f"path={first_path}")
        parts.append(f"folder={proposal_root}")
        print(" ".join(parts))
    return 0


def _run_show(args) -> int:
    project_root = resolve_project_root(Path(args.project_root).resolve())
    try:
        proposal_root, data = load_proposal(project_root, args.proposal_id)
    except ProposalError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if getattr(args, "json", False):
        payload = proposal_summary(proposal_root, data)
        payload["bodyPath"] = str(proposal_root / "proposal.md")
        payload["draftOutputPath"] = str(proposal_root / "draft-output.md")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print(f"Proposal: {data.get('id', proposal_root.name)}")
    print(f"Status: {data.get('status', 'unknown')}")
    print(f"Target capability: {data.get('target_capability', 'unknown')}")
    print(f"Type: {data.get('proposal_type', 'unknown')}")
    print(f"Safety: {data.get('safety_class', 'unknown')}")
    print(f"Output paths: {', '.join(data.get('output_paths', [])) if isinstance(data.get('output_paths'), list) else ''}")
    print(f"Folder: {proposal_root}")
    body = proposal_root / "proposal.md"
    if body.is_file():
        print("")
        print(body.read_text(encoding="utf-8").rstrip())
    return 0


def _run_apply(args) -> int:
    project_root = resolve_project_root(Path(args.project_root).resolve())
    try:
        result = apply_proposal(project_root, args.proposal_id)
    except ProposalError as exc:
        print(f"error: could not apply proposal: {exc}", file=sys.stderr)
        return 1
    print(f"Applied proposal {result.proposal_id}: path={result.proposal_root}")
    for output_path in result.output_paths:
        print(f"- wrote {output_path}")
    print(f"Strict validation issues: {result.strict_issue_count}")
    return 0
