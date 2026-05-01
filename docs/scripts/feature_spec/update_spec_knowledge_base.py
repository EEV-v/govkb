#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

from feature_spec_common import (
    DEFAULT_SPEC_KB_FILE,
    derive_feature_title,
    get_standard_paths,
    latest_change_log,
    read_text_if_exists,
    resolve_feature_dir,
    resolve_repo_root,
    write_text,
)


SECTION_TITLES = [
    "Common Review Patterns",
    "Recurring Open-question Categories",
    "Stable Owners By Domain",
    "Standard Decision Heuristics",
    "Common Acceptance-criteria Templates",
    "Recurring Scope Traps",
    "Domain-specific Evidence Expectations",
    "Examples of good review-pack wording",
    "Learned Patterns",
]


RULES = [
    ("local execution trust", ["workspace trust", "trusted workspace", "local execution"], "If a feature runs local commands, ask for trust, project-root selection, and mutation boundaries in the same review round."),
    ("structured cli output", ["json", "structured output", "cli"], "If UI code reads CLI results, decide the machine-readable output contract before implementation planning."),
    ("assistant state boundary", ["assistant-local", "source of truth", "derived"], "When assistant-local state is involved, record which files are canonical and which are derived outputs."),
    ("first slice packaging", ["vsix", "package", "marketplace"], "Separate local packaging proof from public distribution readiness when both appear in one feature."),
    ("runtime provisioning", ["runtime", "install", "configuration"], "Runtime setup should name whether the first slice guides existing local setup, downloads dependencies, or bundles them."),
    ("telemetry posture", ["telemetry", "privacy"], "Treat telemetry as off until product and privacy owners explicitly approve the data contract."),
    ("memory review mode", ["memory-review", "dry-run", "apply"], "Memory-review dry-run and mutation/apply mode are separate governance decisions."),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature_reference")
    parser.add_argument("--repo-root")
    parser.add_argument("--change-log")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def ensure_kb_template(content: str) -> str:
    if content.strip():
        return content
    lines = ["# Feature Spec Knowledge Base", "", "Cross-feature reusable learning for business-spec convergence.", ""]
    for title in SECTION_TITLES:
        lines.extend([f"## {title}", "- _No reusable notes recorded yet._", ""])
    return "\n".join(lines).rstrip() + "\n"


def append_unique_bullets(content: str, heading: str, bullets: List[str]) -> str:
    marker = f"## {heading}\n"
    if marker not in content:
        content = content.rstrip() + f"\n\n{marker}- _No reusable notes recorded yet._\n"
    prefix, rest = content.split(marker, 1)
    section_body, suffix = (rest.split("\n## ", 1) + [""])[:2]
    existing_lines = [line.strip() for line in section_body.splitlines() if line.strip().startswith("-")]
    existing_normalized = {line.casefold() for line in existing_lines}
    body_lines = [line for line in section_body.splitlines() if line.strip() and line.strip() != "- _No reusable notes recorded yet._"]
    for bullet in bullets:
        candidate = f"- {bullet}"
        if candidate.casefold() not in existing_normalized:
            body_lines.append(candidate)
            existing_normalized.add(candidate.casefold())
    if not body_lines:
        body_lines = ["- _No reusable notes recorded yet._"]
    rebuilt = marker + "\n".join(body_lines).rstrip() + "\n"
    if suffix:
        rebuilt += "\n## " + suffix.lstrip()
    return prefix + rebuilt


def derive_lessons(source_text: str) -> Dict[str, List[str]]:
    lowered = source_text.casefold()
    result: Dict[str, List[str]] = {title: [] for title in SECTION_TITLES}
    for _, tokens, lesson in RULES:
        if tokens[0] in lowered and any(token in lowered for token in tokens):
            if "trust" in lesson or "canonical" in lesson:
                result["Common Review Patterns"].append(lesson)
            elif "machine-readable" in lesson:
                result["Standard Decision Heuristics"].append(lesson)
            elif "packaging proof" in lesson or "Runtime setup" in lesson:
                result["Recurring Scope Traps"].append(lesson)
            elif "telemetry" in lesson:
                result["Stable Owners By Domain"].append(lesson)
            elif "Memory-review" in lesson:
                result["Recurring Open-question Categories"].append(lesson)
    if "good wording" not in lowered and "Requested Business Response" in source_text:
        result["Examples of good review-pack wording"].append("Review packs work better when they ask business to approve scope, answer blockers, and mark deferred items explicitly.")
    return {key: value for key, value in result.items() if value}


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    feature_dir = resolve_feature_dir(repo_root, args.feature_reference)
    feature_title = derive_feature_title(feature_dir)
    change_log_path = Path(args.change_log).resolve() if args.change_log else latest_change_log(feature_dir)
    source_parts = [feature_title]
    if change_log_path and change_log_path.exists():
        source_parts.append(read_text_if_exists(change_log_path) or "")
    review_pack = read_text_if_exists(get_standard_paths(feature_dir)["review_pack"])
    if review_pack:
        source_parts.append(review_pack)
    source_text = "\n\n".join(source_parts)

    kb_path = (repo_root / DEFAULT_SPEC_KB_FILE).resolve()
    content = ensure_kb_template(read_text_if_exists(kb_path) or "")
    lessons = derive_lessons(source_text)
    for heading, bullets in lessons.items():
        content = append_unique_bullets(content, heading, bullets)

    if args.write:
        write_text(kb_path, content)

    payload = {
        "featureDir": str(feature_dir),
        "knowledgeBasePath": str(kb_path),
        "changeLogPath": str(change_log_path) if change_log_path else None,
        "sectionsUpdated": sorted(lessons.keys()),
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Knowledge base: {payload['knowledgeBasePath']}")
        print(f"Sections updated: {', '.join(payload['sectionsUpdated']) if payload['sectionsUpdated'] else 'none'}")
        if args.write:
            print("Updated shared spec knowledge base")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
