"""Governed capability listing and lifecycle management."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import tempfile

from govkb.core.contracts import CapabilityContract
from govkb.core.contracts import load_project_bundle
from govkb.core.ids import normalize_identifier
from govkb.core.install_state import iso_utc_now
from govkb.core.project import resolve_project_root


SECTION_PATTERN = re.compile(r"^##\s+(.+?)\s*$")
SCAFFOLD_BULLET_PATTERN = re.compile(r"^\s*-\s*(TODO:|Use this section|Add .+ here)", re.I)


@dataclass(frozen=True)
class CapabilityManagementResult:
    """Result payload for one governed capability management operation."""

    action: str
    project_root: Path
    changed_files: tuple[Path, ...]
    details: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "action": self.action,
            "projectRoot": str(self.project_root),
            "changedFiles": [str(path) for path in self.changed_files],
            **self.details,
        }


def capability_summary_payload(project_root: Path) -> dict[str, object]:
    """Return a detailed governed capability list for UI and CLI users."""
    resolved_root = resolve_project_root(project_root.resolve())
    bundle, result = load_project_bundle(resolved_root)
    if result.errors:
        message = "; ".join(f"{item.location}: {item.message}" for item in result.errors)
        raise ValueError(message)
    return {
        "schemaVersion": 1,
        "projectRoot": str(bundle.project_root),
        "governedRoot": str(bundle.governed_root),
        "capabilities": [_capability_payload(contract) for contract in sorted(bundle.capabilities.values(), key=lambda item: item.capability_id)],
    }


def rename_capability(project_root: Path, old_id: str, new_id: str) -> CapabilityManagementResult:
    """Rename one governed capability and preserve the old id as a routing alias."""
    resolved_root = resolve_project_root(project_root.resolve())
    old_capability_id = normalize_identifier(old_id)
    new_capability_id = normalize_identifier(new_id)
    if old_capability_id == new_capability_id:
        raise ValueError("old and new capability ids are the same")
    bundle, result = load_project_bundle(resolved_root)
    if result.errors:
        message = "; ".join(f"{item.location}: {item.message}" for item in result.errors)
        raise ValueError(message)
    contract = bundle.capabilities.get(old_capability_id)
    if contract is None:
        raise KeyError(f"capability not found: {old_capability_id}")
    if new_capability_id in bundle.capabilities:
        raise FileExistsError(f"target capability already exists: {new_capability_id}")
    old_root = contract.capability_root
    new_root = bundle.governed_root / "capabilities" / new_capability_id
    if new_root.exists():
        raise FileExistsError(f"target capability path already exists: {new_root}")

    original_contract_text = contract.source_path.read_text(encoding="utf-8")
    new_name = _title_for(new_capability_id)
    aliases = _merged_values(
        new_capability_id,
        new_capability_id.replace("-", " "),
        old_capability_id,
        old_capability_id.replace("-", " "),
        *contract.aliases,
    )
    try:
        old_root.rename(new_root)
        new_contract_path = new_root / "capability.contract.toml"
        updated = _replace_assignment(original_contract_text, "id", new_capability_id)
        updated = _replace_assignment(updated, "name", new_name)
        updated = _replace_list_assignment(updated, "aliases", aliases)
        new_contract_path.write_text(updated, encoding="utf-8")
        _validate_after_operation(resolved_root, new_capability_id)
    except Exception:
        if new_root.exists() and not old_root.exists():
            new_contract_path = new_root / "capability.contract.toml"
            if new_contract_path.exists():
                new_contract_path.write_text(original_contract_text, encoding="utf-8")
            new_root.rename(old_root)
        raise

    return CapabilityManagementResult(
        action="rename",
        project_root=resolved_root,
        changed_files=(new_contract_path,),
        details={
            "oldCapabilityId": old_capability_id,
            "newCapabilityId": new_capability_id,
            "oldPath": str(old_root),
            "newPath": str(new_root),
        },
    )


def merge_capabilities(project_root: Path, source_id: str, target_id: str) -> CapabilityManagementResult:
    """Merge one governed capability into another and remove the source package."""
    resolved_root = resolve_project_root(project_root.resolve())
    source_capability_id = normalize_identifier(source_id)
    target_capability_id = normalize_identifier(target_id)
    if source_capability_id == target_capability_id:
        raise ValueError("source and target capability ids are the same")
    bundle, result = load_project_bundle(resolved_root)
    if result.errors:
        message = "; ".join(f"{item.location}: {item.message}" for item in result.errors)
        raise ValueError(message)
    source = bundle.capabilities.get(source_capability_id)
    target = bundle.capabilities.get(target_capability_id)
    if source is None:
        raise KeyError(f"source capability not found: {source_capability_id}")
    if target is None:
        raise KeyError(f"target capability not found: {target_capability_id}")

    target_contract_text = target.source_path.read_text(encoding="utf-8")
    target_instructions_path = target.capability_root / "instructions.md"
    target_instructions_text = _read_text(target_instructions_path)
    target_memory_snapshots = {target_item.path: _read_text(target.capability_root / target_item.path) for target_item in target.targets}

    with tempfile.TemporaryDirectory(prefix="govkb-capability-merge-") as temp_dir:
        backup_root = Path(temp_dir) / source.capability_root.name
        shutil.copytree(source.capability_root, backup_root)
        report_path = _merge_report_path(bundle.governed_root, source_capability_id, target_capability_id)
        try:
            aliases = _merged_values(
                *target.aliases,
                source_capability_id,
                source_capability_id.replace("-", " "),
                *source.aliases,
            )
            hints = _merged_values(*target.hints, *source.hints)
            updated_contract = _replace_list_assignment(target_contract_text, "aliases", aliases)
            updated_contract = _replace_list_assignment(updated_contract, "hints", hints)
            target.source_path.write_text(updated_contract, encoding="utf-8")

            instruction_addition = _merged_instruction_text(source, report_path)
            target_instructions_path.write_text(
                _append_markdown_block(target_instructions_text, instruction_addition),
                encoding="utf-8",
            )

            memory_additions = _merge_memory_targets(source, target)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(
                _merge_report_text(source, target, report_path, memory_additions),
                encoding="utf-8",
            )
            shutil.rmtree(source.capability_root)
            _validate_after_operation(resolved_root, target_capability_id)
        except Exception:
            target.source_path.write_text(target_contract_text, encoding="utf-8")
            target_instructions_path.write_text(target_instructions_text, encoding="utf-8")
            for rel_path, text in target_memory_snapshots.items():
                (target.capability_root / rel_path).write_text(text, encoding="utf-8")
            if not source.capability_root.exists():
                shutil.copytree(backup_root, source.capability_root)
            if report_path.exists():
                report_path.unlink()
            raise

    changed_files = [target.source_path, target_instructions_path, report_path]
    changed_files.extend(target.capability_root / target_item.path for target_item in target.targets)
    return CapabilityManagementResult(
        action="merge",
        project_root=resolved_root,
        changed_files=tuple(dict.fromkeys(changed_files)),
        details={
            "sourceCapabilityId": source_capability_id,
            "targetCapabilityId": target_capability_id,
            "sourcePath": str(source.capability_root),
            "targetPath": str(target.capability_root),
            "reportPath": str(report_path),
            "memoryAdditions": memory_additions,
        },
    )


def _capability_payload(contract: CapabilityContract) -> dict[str, object]:
    return {
        "id": contract.capability_id,
        "name": contract.capability_name,
        "governed": contract.governed,
        "description": contract.description,
        "aliases": list(contract.aliases),
        "hints": list(contract.hints),
        "memoryEnabled": contract.memory_enabled,
        "requiresExplicitAcceptance": contract.requires_explicit_acceptance,
        "path": str(contract.capability_root),
        "instructionsPath": str(contract.capability_root / "instructions.md"),
        "memoryTargets": [
            {
                "name": target.name,
                "path": target.path,
                "absolutePath": str(contract.capability_root / target.path),
                "sections": list(target.sections),
            }
            for target in contract.targets
        ],
        "lifecycleState": contract.lifecycle.state,
        "migrationStatus": contract.migration_status,
    }


def _validate_after_operation(project_root: Path, required_capability_id: str) -> None:
    bundle, result = load_project_bundle(project_root)
    if result.errors:
        message = "; ".join(f"{item.location}: {item.message}" for item in result.errors)
        raise ValueError(f"governed package validation failed after operation: {message}")
    if required_capability_id not in bundle.capabilities:
        raise ValueError(f"governed package validation failed after operation: missing {required_capability_id}")


def _replace_assignment(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf'(?m)^{re.escape(key)}\s*=\s*".*?"\s*$')
    replacement = f"{key} = {json.dumps(value)}"
    if not pattern.search(text):
        raise ValueError(f"contract assignment not found: {key}")
    return pattern.sub(replacement, text, count=1)


def _replace_list_assignment(text: str, key: str, values: tuple[str, ...]) -> str:
    pattern = re.compile(rf"(?m)^{re.escape(key)}\s*=\s*\[.*?\]\s*$")
    replacement = f"{key} = {_toml_string_list(values)}"
    if not pattern.search(text):
        raise ValueError(f"contract list assignment not found: {key}")
    return pattern.sub(replacement, text, count=1)


def _toml_string_list(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(json.dumps(value) for value in values) + "]"


def _merged_values(*values: str) -> tuple[str, ...]:
    merged: list[str] = []
    seen: set[str] = set()
    for value in values:
        stripped = value.strip()
        if not stripped:
            continue
        key = stripped.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(stripped)
    return tuple(merged)


def _title_for(capability_id: str) -> str:
    return capability_id.replace("-", " ").title()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _append_markdown_block(text: str, block: str) -> str:
    base = text.rstrip()
    addition = block.strip()
    if not base:
        return addition + "\n"
    return base + "\n\n" + addition + "\n"


def _merged_instruction_text(source: CapabilityContract, report_path: Path) -> str:
    source_instructions = _read_text(source.capability_root / "instructions.md").strip()
    if source_instructions.startswith("# "):
        source_instructions = "\n".join(source_instructions.splitlines()[1:]).strip()
    return (
        f"## Merged Capability: {source.capability_name}\n\n"
        f"This capability absorbed `{source.capability_id}` through governed merge review. "
        f"Use the merged guidance only when it fits this capability's contract and current user request. "
        f"The merge report is `{report_path.relative_to(report_path.parents[3]).as_posix()}`.\n\n"
        "### Outcome\n\n"
        f"Preserve reusable behavior from `{source.capability_id}` while treating this capability's contract, "
        "memory targets, and authority rules as the active source of truth.\n\n"
        "### Success Criteria\n\n"
        "- Apply merged guidance only when it is durable, source-grounded, and within the surviving capability scope.\n"
        "- Prefer specific instructions from this capability when merged source wording conflicts or is narrower.\n"
        "- Keep session-specific, local-only, private, or unsafe source details out of future memory updates.\n"
        "- Use the merge report as the audit trail for what moved and what still needs review.\n\n"
        "### Source Guidance\n\n"
        f"{source_instructions or 'No source instructions were present.'}"
    )


def _merge_memory_targets(source: CapabilityContract, target: CapabilityContract) -> dict[str, int]:
    source_sections = _markdown_sections(_read_text(source.capability_root / "references" / "long-term-memory.md"))
    additions_by_target: dict[str, int] = {}
    for target_item in target.targets:
        target_path = target.capability_root / target_item.path
        target_text = _read_text(target_path)
        additions: dict[str, list[str]] = {}
        for section in target_item.sections:
            source_lines = _usable_bullet_lines(source_sections.get(section, []))
            if source_lines:
                additions[section] = source_lines
        if not additions:
            additions_by_target[target_item.path] = 0
            continue
        updated, count = _append_section_bullets(
            target_text,
            additions,
            source_id=source.capability_id,
        )
        target_path.write_text(updated, encoding="utf-8")
        additions_by_target[target_item.path] = count
    return additions_by_target


def _markdown_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = SECTION_PATTERN.match(line)
        if match:
            current = match.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def _usable_bullet_lines(lines: list[str]) -> list[str]:
    bullets: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        if SCAFFOLD_BULLET_PATTERN.search(stripped):
            continue
        bullets.append(stripped[2:].strip())
    return bullets


def _append_section_bullets(text: str, additions: dict[str, list[str]], *, source_id: str) -> tuple[str, int]:
    lines = text.rstrip().splitlines()
    existing_text = "\n".join(lines).lower()
    output: list[str] = []
    count = 0
    current: str | None = None
    for index, line in enumerate(lines):
        match = SECTION_PATTERN.match(line)
        if match:
            if current in additions:
                inserted, inserted_count = _render_missing_additions(additions[current], existing_text, source_id)
                if inserted:
                    if output and output[-1].strip():
                        output.append("")
                    output.extend(inserted)
                    count += inserted_count
            current = match.group(1).strip()
        output.append(line)
        if index == len(lines) - 1 and current in additions:
            inserted, inserted_count = _render_missing_additions(additions[current], existing_text, source_id)
            if inserted:
                if output and output[-1].strip():
                    output.append("")
                output.extend(inserted)
                count += inserted_count
    return "\n".join(output).rstrip() + "\n", count


def _render_missing_additions(additions: list[str], existing_text: str, source_id: str) -> tuple[list[str], int]:
    rendered: list[str] = []
    for addition in additions:
        if addition.lower() in existing_text:
            continue
        rendered.append(f"- Merged from {source_id}: {addition}")
    return rendered, len(rendered)


def _merge_report_path(governed_root: Path, source_id: str, target_id: str) -> Path:
    timestamp = iso_utc_now().replace("-", "").replace(":", "").replace(".", "")
    return governed_root / "reports" / "capability-management" / f"{timestamp}-{source_id}-into-{target_id}.md"


def _merge_report_text(
    source: CapabilityContract,
    target: CapabilityContract,
    report_path: Path,
    memory_additions: dict[str, int],
) -> str:
    lines = [
        f"# Capability Merge - {source.capability_id} into {target.capability_id}",
        "",
        f"- Source capability: {source.capability_id}",
        f"- Target capability: {target.capability_id}",
        f"- Report: {report_path.name}",
        "",
        "## Result",
        "",
        f"- Target `{target.capability_id}` now carries aliases and reusable guidance from `{source.capability_id}`.",
        f"- Source capability package `{source.capability_id}` was removed from active governed capabilities.",
        "- Review the active project diff before committing.",
        "- Treat this report as the audit trail for future questions about the merge.",
        "",
        "## Review Checklist",
        "",
        "- Confirm the surviving capability contract still describes the combined scope.",
        "- Confirm merged instructions do not depend on one-off session state, private workspace details, or local-only paths.",
        "- Confirm copied memory bullets are durable, sourced, and assigned to a configured target section.",
        "- Re-run governed validation after any manual edits prompted by this report.",
        "",
        "## Memory Additions",
        "",
    ]
    if memory_additions:
        lines.extend(f"- {path}: {count} bullet(s)" for path, count in sorted(memory_additions.items()))
    else:
        lines.append("- None")
    return "\n".join(lines).rstrip() + "\n"
