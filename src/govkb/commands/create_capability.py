"""Capability scaffold command."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

from govkb.core.candidates import candidate_default_capability_id
from govkb.core.candidates import load_candidate
from govkb.core.candidates import mark_candidate_activated
from govkb.core.ids import normalize_identifier
from govkb.core.init_prompt import initialize_kb_prompt_text
from govkb.core.project import resolve_project_root


def _contract_text(capability_id: str) -> str:
    capability_name = capability_id.replace("-", " ").title()
    return f"""contract_version = 1

[capability]
id = "{capability_id}"
name = "{capability_name}"
governed = true
description = "TODO: describe when this capability should be used."

[routing]
aliases = []
hints = []
negative_hints = []

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = ["Working Agreement"]
"""


def _memory_text(capability_id: str) -> str:
    title = capability_id.replace("-", " ").title()
    return f"# {title}\n\n## Working Agreement\n\n- TODO: add durable guidance for this capability.\n"


def _instructions_text(capability_id: str) -> str:
    title = capability_id.replace("-", " ").title()
    return (
        f"# {title}\n\n"
        "Use this governed capability when the task matches its routing contract.\n\n"
        "## Load references first\n\n"
        "- Always read `references/long-term-memory.md` before acting.\n\n"
        "## Workflow\n\n"
        "- TODO: describe the stable workflow for this capability.\n"
    )


def _candidate_prompt_text(capability_id: str, candidate_id: str, candidate_data: dict[str, object]) -> str:
    proposal = candidate_data.get("proposal") if isinstance(candidate_data.get("proposal"), dict) else {}
    scope = candidate_data.get("scope") if isinstance(candidate_data.get("scope"), dict) else {}
    summary = proposal.get("summary") if isinstance(proposal, dict) else None
    scope_summary = scope.get("summary") if isinstance(scope, dict) else None
    return initialize_kb_prompt_text(
        capability_id=capability_id,
        capability_name=capability_id.replace("-", " ").title(),
        summary=summary if isinstance(summary, str) else None,
        scope_summary=scope_summary if isinstance(scope_summary, str) else None,
        candidate_id=candidate_id,
    )


def _candidate_contract_text(candidate_root: Path, capability_id: str, candidate_id: str) -> str:
    contract_path = candidate_root / "draft-capability.contract.toml"
    if not contract_path.is_file():
        raise FileNotFoundError(f"candidate draft contract not found: {contract_path}")
    text = contract_path.read_text(encoding="utf-8")
    capability_name = capability_id.replace("-", " ").title()
    text = re.sub(r'(?m)^id = ".+?"$', f'id = "{capability_id}"', text, count=1)
    text = re.sub(r'(?m)^name = ".+?"$', f'name = "{capability_name}"', text, count=1)
    if capability_id != candidate_id:
        aliases = [
            f"${capability_id}",
            capability_id,
            capability_id.replace("-", " "),
            f"${candidate_id}",
            candidate_id,
            candidate_id.replace("-", " "),
        ]
        alias_text = "[" + ", ".join(f'"{alias}"' for alias in dict.fromkeys(aliases)) + "]"
        text = re.sub(r"(?m)^aliases = \[.*?\]$", f"aliases = {alias_text}", text, count=1)
    return text


def run_create_capability(args) -> int:
    """Scaffold a governed capability under an existing `.governed` package."""
    requested_root = Path(args.project_root).resolve()
    project_root = resolve_project_root(requested_root)
    governed_root = project_root / ".governed"
    if not governed_root.is_dir():
        print(f"error: {governed_root} does not exist; run govkb init first", file=sys.stderr)
        return 1

    from_candidate = getattr(args, "from_candidate", None)
    if from_candidate:
        candidate_id = normalize_identifier(from_candidate)
        try:
            candidate_root, candidate_data = load_candidate(project_root, candidate_id)
            requested_capability_id = getattr(args, "capability_id", None)
            capability_id = normalize_identifier(requested_capability_id) if requested_capability_id else candidate_default_capability_id(candidate_data, candidate_id)
            contract_text = _candidate_contract_text(candidate_root, capability_id, candidate_id)
        except Exception as exc:
            print(f"error: could not load candidate {candidate_id}: {exc}", file=sys.stderr)
            return 1
        if not getattr(args, "capability_id", None):
            print(f"Using suggested capability id: {capability_id}")
        capability_root = governed_root / "capabilities" / capability_id
        if capability_root.exists():
            print(f"error: capability already exists: {capability_root}", file=sys.stderr)
            return 1
        instructions_path = candidate_root / "draft-instructions.md"
        references_source = candidate_root / "references"
        if not instructions_path.is_file():
            print(f"error: candidate draft instructions not found: {instructions_path}", file=sys.stderr)
            return 1
        if not references_source.is_dir():
            print(f"error: candidate references not found: {references_source}", file=sys.stderr)
            return 1
        capability_root.mkdir(parents=True, exist_ok=False)
        (capability_root / "capability.contract.toml").write_text(contract_text, encoding="utf-8")
        (capability_root / "instructions.md").write_text(instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
        shutil.copytree(references_source, capability_root / "references")
        prompts_root = capability_root / "prompts"
        prompts_root.mkdir(parents=True, exist_ok=False)
        (prompts_root / "initialize-kb.md").write_text(
            _candidate_prompt_text(capability_id, candidate_id, candidate_data),
            encoding="utf-8",
        )
        mark_candidate_activated(project_root, candidate_id, capability_id)
        print(f"Created capability from candidate: {capability_root}")
        return 0

    requested_capability_id = getattr(args, "capability_id", None)
    if not requested_capability_id:
        print("error: capability_id is required unless --from-candidate is used", file=sys.stderr)
        return 1
    capability_id = normalize_identifier(requested_capability_id)
    capability_root = governed_root / "capabilities" / capability_id
    if capability_root.exists():
        print(f"error: capability already exists: {capability_root}", file=sys.stderr)
        return 1

    references_root = capability_root / "references"
    prompts_root = capability_root / "prompts"
    references_root.mkdir(parents=True, exist_ok=False)
    prompts_root.mkdir(parents=True, exist_ok=False)
    (capability_root / "capability.contract.toml").write_text(_contract_text(capability_id), encoding="utf-8")
    (capability_root / "instructions.md").write_text(_instructions_text(capability_id), encoding="utf-8")
    (references_root / "long-term-memory.md").write_text(_memory_text(capability_id), encoding="utf-8")
    (prompts_root / "initialize-kb.md").write_text(
        initialize_kb_prompt_text(
            capability_id=capability_id,
            capability_name=capability_id.replace("-", " ").title(),
        ),
        encoding="utf-8",
    )

    print(f"Created capability scaffold: {capability_root}")
    return 0
