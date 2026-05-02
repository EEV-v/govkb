"""Capability scaffold command."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
import tomllib

from govkb.core.candidates import candidate_default_capability_id
from govkb.core.candidates import candidate_is_review_approved
from govkb.core.candidates import candidate_review_metadata
from govkb.core.candidates import load_candidate
from govkb.core.candidates import mark_candidate_activated
from govkb.core.contracts import load_project_bundle
from govkb.core.governed_skill import validate_governed_skill_package
from govkb.core.ids import normalize_identifier
from govkb.core.init_prompt import initialize_kb_prompt_text
from govkb.core.kb_bootstrap import bootstrap_capability
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
sections = [
  "Working Agreement",
  "Stable Workflows",
  "Commands And Verification",
  "Code And Docs Map",
  "Authority Rules",
]

[bootstrap]
profile = "workflow"
repo_roots = ["."]
authority_paths = []
seed_paths = []

[kb_health]
requires_verification_commands = true
requires_repo_map = true
required_sections = ["Working Agreement", "Stable Workflows", "Commands And Verification", "Code And Docs Map"]
"""


def _memory_text(capability_id: str) -> str:
    title = capability_id.replace("-", " ").title()
    return (
        f"# {title}\n\n"
        "## Working Agreement\n\n"
        "- TODO: add durable guidance for this capability.\n\n"
        "## Stable Workflows\n\n"
        "- Add stable workflow steps here after bootstrap or repeated evidence.\n\n"
        "## Commands And Verification\n\n"
        "- Add durable verification commands here after bootstrap or repeated evidence.\n\n"
        "## Code And Docs Map\n\n"
        "- Add repo-relative code and docs locations here after bootstrap or repeated evidence.\n\n"
        "## Authority Rules\n\n"
        "- Add authority rules here when one governed file should win over broader docs.\n"
    )


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


def _candidate_memory_text(candidate_root: Path, capability_id: str, candidate_data: dict[str, object]) -> str:
    title = capability_id.replace("-", " ").title()
    proposal = candidate_data.get("proposal") if isinstance(candidate_data.get("proposal"), dict) else {}
    scope = candidate_data.get("scope") if isinstance(candidate_data.get("scope"), dict) else {}
    summary = proposal.get("summary") if isinstance(proposal, dict) else None
    scope_summary = scope.get("summary") if isinstance(scope, dict) else None
    facts_path = candidate_root / "candidate-facts.toml"
    facts_by_section: dict[str, list[str]] = {
        "Working Agreement": [],
        "Stable Workflows": [],
        "Commands And Verification": [],
        "Code And Docs Map": [],
        "Authority Rules": [],
    }
    if facts_path.is_file():
        data = tomllib.loads(facts_path.read_text(encoding="utf-8"))
        for row in data.get("facts", ()):
            if not isinstance(row, dict):
                continue
            fact = row.get("fact")
            section = row.get("section")
            if not isinstance(fact, str) or not fact.strip():
                continue
            if not isinstance(section, str) or not section.strip():
                continue
            facts_by_section.setdefault(section, [])
            if fact not in facts_by_section[section]:
                facts_by_section[section].append(fact)

    lines = [f"# {title}", ""]
    if isinstance(summary, str) and summary.strip():
        lines.append(f"Candidate summary: {summary.strip()}")
        lines.append("")
    if isinstance(scope_summary, str) and scope_summary.strip():
        lines.append(f"Scope summary: {scope_summary.strip()}")
        lines.append("")

    for section in ("Working Agreement", "Stable Workflows", "Commands And Verification", "Code And Docs Map", "Authority Rules"):
        lines.append(f"## {section}")
        lines.append("")
        facts = facts_by_section.get(section, [])
        if facts:
            lines.extend(f"- {fact}" for fact in facts)
        elif section == "Working Agreement":
            if isinstance(scope_summary, str) and scope_summary.strip():
                lines.append(f"- Keep this capability focused on {scope_summary.strip().rstrip('.')}.")
            else:
                lines.append("- Keep this capability focused on the reusable workflow captured by the activated candidate.")
        elif section == "Stable Workflows":
            lines.append("- Use this section for recurring project workflow patterns observed across sessions.")
        elif section == "Commands And Verification":
            lines.append("- Use this section for durable validation commands, evidence expectations, and safety checks.")
        elif section == "Code And Docs Map":
            lines.append("- Use this section for durable repo-relative code, test, and docs locations.")
        else:
            lines.append("- Use this section for durable authority rules when one governed source should win.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


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


def _contract_with_activation_lifecycle(text: str, candidate_data: dict[str, object], candidate_id: str) -> str:
    if "[lifecycle]" in text:
        return text
    review = candidate_review_metadata(candidate_data)
    scope = candidate_data.get("scope") if isinstance(candidate_data.get("scope"), dict) else {}
    scope_summary = scope.get("summary") if isinstance(scope, dict) else None
    justification = (
        str(scope_summary).strip()
        if isinstance(scope_summary, str) and scope_summary.strip()
        else f"Candidate {candidate_id} was approved for governed capability activation."
    )
    return (
        text.rstrip()
        + "\n\n"
        + "[lifecycle]\n"
        + 'state = "active"\n'
        + f"scope_justification = {json_string(justification)}\n\n"
        + "[lifecycle.approval]\n"
        + 'status = "approved"\n'
        + f"reviewer = {json_string(review.get('reviewer', 'unknown-reviewer'))}\n"
        + f"approved_at = {json_string(review.get('approved_at', 'unknown'))}\n"
    )


def json_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


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
        require_strict_activation = bool(getattr(args, "require_strict_activation", False))
        if require_strict_activation:
            if not candidate_is_review_approved(candidate_data):
                print(f"error: candidate {candidate_id} is not approved for activation", file=sys.stderr)
                return 1
            contract_text = _contract_with_activation_lifecycle(contract_text, candidate_data, candidate_id)
        if not getattr(args, "capability_id", None):
            print(f"Using suggested capability id: {capability_id}")
        capability_root = governed_root / "capabilities" / capability_id
        if capability_root.exists():
            print(f"error: capability already exists: {capability_root}", file=sys.stderr)
            return 1
        instructions_path = candidate_root / "draft-instructions.md"
        if not instructions_path.is_file():
            print(f"error: candidate draft instructions not found: {instructions_path}", file=sys.stderr)
            return 1
        try:
            capability_root.mkdir(parents=True, exist_ok=False)
            references_root = capability_root / "references"
            prompts_root = capability_root / "prompts"
            references_root.mkdir(parents=True, exist_ok=False)
            prompts_root.mkdir(parents=True, exist_ok=False)
            (capability_root / "capability.contract.toml").write_text(contract_text, encoding="utf-8")
            (capability_root / "instructions.md").write_text(instructions_path.read_text(encoding="utf-8"), encoding="utf-8")
            (references_root / "long-term-memory.md").write_text(
                _candidate_memory_text(candidate_root, capability_id, candidate_data),
                encoding="utf-8",
            )
            (prompts_root / "initialize-kb.md").write_text(
                _candidate_prompt_text(capability_id, candidate_id, candidate_data),
                encoding="utf-8",
            )
            refreshed_bundle, refreshed_result = load_project_bundle(project_root)
            for message in refreshed_result.warnings:
                print(f"warning: {message.location}: {message.message}")
            for message in refreshed_result.errors:
                print(f"error: {message.location}: {message.message}", file=sys.stderr)
            if refreshed_result.errors:
                shutil.rmtree(capability_root, ignore_errors=True)
                return 1
            if not getattr(args, "no_init_kb", False):
                bootstrap_result = bootstrap_capability(project_root, refreshed_bundle.capabilities[capability_id], candidate_root=candidate_root)
                if bootstrap_result.added_facts:
                    print(f"Bootstrapped KB for {capability_id}: {len(bootstrap_result.added_facts)} bullet(s)")
                else:
                    print(f"warning: {capability_id}: bootstrap found no new durable KB facts")
            if require_strict_activation:
                strict_result = validate_governed_skill_package(
                    project_root,
                    refreshed_bundle.capabilities[capability_id],
                    activation_required=True,
                )
                for issue in strict_result.issues:
                    stream = sys.stderr if issue.severity == "error" else sys.stdout
                    print(f"strict {issue.severity}: {issue.rule_id}: {issue.location}: {issue.message}", file=stream)
                if strict_result.errors:
                    shutil.rmtree(capability_root, ignore_errors=True)
                    return 1
            mark_candidate_activated(project_root, candidate_id, capability_id)
        except Exception as exc:
            shutil.rmtree(capability_root, ignore_errors=True)
            print(f"error: could not create capability from candidate {candidate_id}: {exc}", file=sys.stderr)
            return 1
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
