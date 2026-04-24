#!/usr/bin/env python3
"""Dry-run inventory for migrating local Codex skills to govkb capabilities.

This PoC is intentionally read-only against the skill source tree. It writes
evidence only under the feature folder output directory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


DEFAULT_SKILLS_ROOT = Path("/mnt/c/Users/Ev/.codex/skills")
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "poc-artifacts"

NEGATIVE_HINTS = [
    "codex-memory-review",
    "govkb install",
    "govkb apply",
    "report output",
    "cron schedule",
]


@dataclass
class SkillInventory:
    skill_id: str
    source_path: str
    name: str
    description: str
    track: str
    reasons: list[str]
    has_memory: bool
    memory_files: list[str]
    has_references: bool
    reference_files: list[str]
    has_scripts: bool
    script_files: list[str]
    has_agents: bool
    requires_explicit_acceptance: bool
    proposed_contract: str | None
    risk_notes: list[str]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def extract_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    block = text[4:end].strip()
    result: dict[str, str] = {}
    current_key: str | None = None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if re.match(r"^[A-Za-z0-9_-]+:\s*", line):
            key, value = line.split(":", 1)
            current_key = key.strip()
            result[current_key] = value.strip()
        elif current_key:
            result[current_key] = f"{result[current_key]} {line.strip()}".strip()
    return result


def discover_skill_dirs(skills_root: Path) -> list[Path]:
    direct = [p.parent for p in skills_root.glob("*/SKILL.md")]
    system = [p.parent for p in skills_root.glob(".system/*/SKILL.md")]
    return sorted(direct + system, key=lambda p: (".system" not in p.parts, str(p).lower()))


def relative_list(root: Path, paths: Iterable[Path]) -> list[str]:
    return sorted(str(p.relative_to(root)).replace("\\", "/") for p in paths)


def find_files(root: Path, patterns: list[str]) -> list[Path]:
    found: list[Path] = []
    for pattern in patterns:
        found.extend(root.glob(pattern))
    return sorted({p for p in found if p.is_file()})


def safe_toml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def human_name(skill_id: str, fallback: str) -> str:
    if fallback:
        return fallback
    clean = skill_id.split("/", 1)[-1].replace("-", " ")
    return clean.title()


def compact_description(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def derive_hints(skill_id: str, description: str) -> list[str]:
    base = skill_id.split("/", 1)[-1].replace("-", " ")
    hints = {base}
    desc = compact_description(description).lower()
    for phrase in re.split(r"[.;]", desc):
        phrase = phrase.strip()
        if not phrase:
            continue
        phrase = re.sub(r"^(use when codex needs to|use when asked to|use when)\s+", "", phrase)
        parts = re.split(r",| and | or | especially | including | where ", phrase)
        for part in parts:
            candidate = re.sub(r"\s+", " ", part).strip(" .")
            words = candidate.split()
            if 2 <= len(words) <= 7:
                hints.add(candidate)
    filtered = [
        h
        for h in sorted(hints)
        if not any(noise in h for noise in ["codex needs", "use when", "this skill"])
    ]
    return filtered[:12]


def classify(skill_id: str, description: str, has_memory: bool, is_system: bool) -> tuple[str, list[str], list[str]]:
    reasons: list[str] = []
    risk_notes: list[str] = []
    local_id = skill_id.split("/", 1)[-1]

    if is_system:
        return "adapter-local only", ["system skill is assistant/runtime owned"], []

    if not local_id.startswith("clearing-"):
        return "adapter-local only", ["not project-specific Clearing knowledge"], []

    if has_memory:
        reasons.append("has durable memory file")
        if local_id.startswith("clearing-review-"):
            reasons.append("reviewer capability with project-domain routing")
        if local_id in {
            "clearing-bugfixer",
            "clearing-master-reviewer",
            "clearing-qa-on-staging",
            "clearing-feature-estimator",
        }:
            reasons.append("project workflow knowledge keeper")
        return "governed capability now", reasons, risk_notes

    if any(token in local_id for token in ["review", "bugfix", "qa", "estimator"]):
        risk_notes.append("looks project-domain but has no durable memory file yet")

    return "legacy keep until migrated", [
        "project-specific skill without first-wave memory evidence",
        "keep operationally available until contract parity is proven",
    ], risk_notes


def contract_text(item: SkillInventory) -> str:
    aliases = [
        f"${item.skill_id.split('/', 1)[-1]}",
        item.name,
        item.skill_id.split("/", 1)[-1].replace("-", " "),
    ]
    hints = derive_hints(item.skill_id, item.description)
    requires = "true" if item.requires_explicit_acceptance else "false"
    description = compact_description(item.description)
    if len(description) > 500:
        description = description[:497].rstrip() + "..."

    def array(values: list[str]) -> str:
        body = ",\n  ".join(safe_toml_string(v) for v in values)
        return "[\n  " + body + "\n]"

    return "\n".join(
        [
            "contract_version = 1",
            "",
            "[capability]",
            f"id = {safe_toml_string(item.skill_id.split('/', 1)[-1])}",
            f"name = {safe_toml_string(item.name)}",
            "governed = true",
            f"description = {safe_toml_string(description)}",
            "",
            "[routing]",
            f"aliases = {array(sorted(set(aliases)))}",
            f"hints = {array(hints)}",
            f"negative_hints = {array(NEGATIVE_HINTS)}",
            "",
            "[memory]",
            "enabled = true",
            "auto_apply_min_confidence = 0.85",
            f"requires_explicit_acceptance = {requires}",
            "",
            "[memory.targets.main]",
            'path = "references/long-term-memory.md"',
            "sections = [",
            '  "Repository Best Practices",',
            '  "Stable Risk Patterns",',
            '  "Operational Checklist"',
            "]",
            "",
            "[migration]",
            'source_adapter = "codex"',
            f"source_path = {safe_toml_string(item.source_path)}",
            'status = "poc-dry-run"',
            "",
        ]
    )


def inventory_skill(skill_dir: Path, skills_root: Path) -> SkillInventory:
    skill_md = skill_dir / "SKILL.md"
    text = read_text(skill_md)
    frontmatter = extract_frontmatter(text)
    local_id = skill_dir.name
    is_system = skill_dir.parent.name == ".system"
    skill_id = f".system/{local_id}" if is_system else local_id
    name = frontmatter.get("name", local_id)
    description = compact_description(frontmatter.get("description", ""))

    memory_files = find_files(skill_dir, ["**/*memory*.md", "**/*MEMORY*.md", "**/*long-term*.md"])
    reference_files = find_files(skill_dir, ["references/**/*"])
    script_files = find_files(skill_dir, ["scripts/**/*"])
    agent_files = find_files(skill_dir, ["agents/**/*"])

    combined_text = text
    for ref in reference_files[:20]:
        combined_text += "\n" + read_text(ref)

    requires_explicit_acceptance = bool(
        re.search(r"explicit\s+(user\s+)?acceptance|requires\s+explicit\s+accept", combined_text, re.I)
    )

    track, reasons, risk_notes = classify(skill_id, description, bool(memory_files), is_system)

    item = SkillInventory(
        skill_id=skill_id,
        source_path=str(skill_dir),
        name=human_name(local_id, name),
        description=description,
        track=track,
        reasons=reasons,
        has_memory=bool(memory_files),
        memory_files=relative_list(skill_dir, memory_files),
        has_references=bool(reference_files),
        reference_files=relative_list(skill_dir, reference_files),
        has_scripts=bool(script_files),
        script_files=relative_list(skill_dir, script_files),
        has_agents=bool(agent_files),
        requires_explicit_acceptance=requires_explicit_acceptance,
        proposed_contract=None,
        risk_notes=risk_notes,
    )

    if track == "governed capability now":
        item.proposed_contract = f"proposed-contracts/{local_id}/capability.contract.toml"
    return item


def validate_inventory(items: list[SkillInventory]) -> list[str]:
    errors: list[str] = []
    seen = set()
    for item in items:
        if item.skill_id in seen:
            errors.append(f"duplicate skill id: {item.skill_id}")
        seen.add(item.skill_id)
        if not item.track:
            errors.append(f"unclassified skill: {item.skill_id}")
        if item.has_memory and item.track != "governed capability now":
            errors.append(f"memory-bearing skill not governed-now: {item.skill_id}")
        if item.proposed_contract and item.proposed_contract.startswith(("/", "..")):
            errors.append(f"unsafe proposed contract path: {item.skill_id}")
    return errors


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown_report(path: Path, items: list[SkillInventory], summary: dict[str, object]) -> None:
    rows = []
    for item in sorted(items, key=lambda x: x.skill_id):
        rows.append(
            "| {id} | {track} | {memory} | {acceptance} | {reasons} |".format(
                id=item.skill_id,
                track=item.track,
                memory="yes" if item.has_memory else "no",
                acceptance="yes" if item.requires_explicit_acceptance else "no",
                reasons="<br>".join(item.reasons + item.risk_notes),
            )
        )

    text = "\n".join(
        [
            "# GovKB Skill Inventory Dry Run",
            "",
            f"- Run at: `{summary['run_at_utc']}`",
            f"- Skills root: `{summary['skills_root']}`",
            f"- Skills scanned: `{summary['total_skills']}`",
            f"- Governed capability now: `{summary['tracks']['governed capability now']}`",
            f"- Legacy keep until migrated: `{summary['tracks']['legacy keep until migrated']}`",
            f"- Adapter-local only: `{summary['tracks']['adapter-local only']}`",
            f"- Memory-bearing skills: `{summary['memory_bearing_skills']}`",
            f"- Generated contract candidates: `{summary['generated_contracts']}`",
            f"- Validation status: `{summary['validation_status']}`",
            "",
            "## Skill Classification",
            "",
            "| Skill | Track | Memory | Explicit Acceptance | Reason |",
            "|---|---|---:|---:|---|",
            *rows,
            "",
            "## Interpretation",
            "",
            "- `governed capability now`: first-wave repo contract candidates.",
            "- `legacy keep until migrated`: project-specific skills that should remain working until parity is proven.",
            "- `adapter-local only`: assistant/runtime/personal helpers that should not become project source of truth.",
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def write_contracts(output_dir: Path, items: list[SkillInventory]) -> None:
    contracts_root = output_dir / "proposed-contracts"
    for item in items:
        if item.track != "governed capability now":
            continue
        local_id = item.skill_id.split("/", 1)[-1]
        target = contracts_root / local_id / "capability.contract.toml"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contract_text(item), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skills-root", type=Path, default=DEFAULT_SKILLS_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    skills_root = args.skills_root.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    skill_dirs = discover_skill_dirs(skills_root)
    items = [inventory_skill(path, skills_root) for path in skill_dirs]
    errors = validate_inventory(items)
    write_contracts(output_dir, items)

    tracks = {
        "governed capability now": 0,
        "legacy keep until migrated": 0,
        "adapter-local only": 0,
    }
    for item in items:
        tracks[item.track] = tracks.get(item.track, 0) + 1

    inventory_payload = [asdict(item) for item in sorted(items, key=lambda x: x.skill_id)]
    digest = hashlib.sha256(json.dumps(inventory_payload, sort_keys=True).encode("utf-8")).hexdigest()
    summary: dict[str, object] = {
        "run_at_utc": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "skills_root": str(skills_root),
        "output_dir": str(output_dir),
        "total_skills": len(items),
        "tracks": tracks,
        "memory_bearing_skills": sum(1 for item in items if item.has_memory),
        "approval_gated_skills": sum(1 for item in items if item.requires_explicit_acceptance),
        "generated_contracts": sum(1 for item in items if item.proposed_contract),
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "inventory_sha256": digest,
    }

    write_json(output_dir / "skill-inventory.json", {"summary": summary, "skills": inventory_payload})
    write_json(output_dir / "summary.json", summary)
    write_markdown_report(output_dir / "skill-inventory.md", items, summary)

    print(f"skills scanned: {len(items)}")
    print(f"validation: {summary['validation_status']}")
    print(f"summary: {output_dir / 'summary.json'}")
    print(f"inventory: {output_dir / 'skill-inventory.md'}")
    print(f"contracts: {output_dir / 'proposed-contracts'}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
