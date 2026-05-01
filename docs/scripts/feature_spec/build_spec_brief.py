#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from feature_spec_common import (
    build_tracking_lines,
    derive_feature_title,
    extract_question_lines,
    extract_section_body,
    extract_summary_paragraph,
    get_standard_paths,
    latest_feedback_candidate,
    list_feedback_candidates,
    parse_tracking_block,
    read_text_if_exists,
    resolve_feature_dir,
    resolve_repo_root,
    today_iso,
    write_text,
)


SECTION_ORDER = [
    "Request",
    "Problem",
    "Business Value",
    "Scope",
    "Acceptance Criteria",
    "Non-goals",
    "Open Questions",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature_reference")
    parser.add_argument("--repo-root")
    parser.add_argument("--feature-title")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def extract_bullets(section_body: Optional[str], limit: int = 8) -> List[str]:
    if not section_body:
        return []
    bullets: List[str] = []
    for line in section_body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("- ", "* ")):
            bullets.append(stripped[2:].strip())
        elif re.match(r"^\d+\.\s+", stripped):
            bullets.append(re.split(r"^\d+\.\s+", stripped, maxsplit=1)[1].strip())
    return bullets[:limit]


def build_source_artifacts(feature_dir: Path) -> List[str]:
    artifacts = ["business.md"]
    for name in [
        "business-context.md",
        "context.md",
        "use-cases.md",
        "poc-output.md",
        "poc-output.sql",
        "requirements-catalog.md",
        "implementation-plan.md",
    ]:
        if (feature_dir / name).exists():
            artifacts.append(name)
    feedback_docs = [candidate["name"] for candidate in list_feedback_candidates(feature_dir, include_processed=True)]
    for name in feedback_docs:
        if name not in artifacts:
            artifacts.append(name)
    return artifacts


def build_spec_brief(feature_dir: Path, feature_title: str) -> Dict[str, Any]:
    paths = get_standard_paths(feature_dir)
    business_text = read_text_if_exists(paths["business"])
    if not business_text:
        raise RuntimeError(f"Missing business.md in {feature_dir}")

    tracking = parse_tracking_block(business_text)
    summary = extract_summary_paragraph(business_text)
    request = extract_section_body(business_text, "Request")
    problem = extract_section_body(business_text, "Problem")
    business_value = extract_bullets(extract_section_body(business_text, "Business Value"), limit=6)
    scope_snapshot = extract_bullets(extract_section_body(business_text, "Scope"), limit=10)
    acceptance_snapshot = extract_bullets(extract_section_body(business_text, "Acceptance Criteria"), limit=8)
    open_questions = extract_question_lines(business_text)[:10]
    source_artifacts = build_source_artifacts(feature_dir)
    feedback_candidates = list_feedback_candidates(feature_dir, include_processed=True)
    latest_feedback = latest_feedback_candidate(feature_dir, include_processed=True)
    pending_feedback = latest_feedback_candidate(feature_dir, include_processed=False)

    lines = [
        f"# Spec Brief — {feature_title}",
        "",
        f"Last updated: {today_iso()}",
        "",
    ]

    tracking_lines = build_tracking_lines(
        [{"label": label, **value} for label, value in tracking.items()]
    )
    if tracking_lines:
        lines.extend(["## Tracking", *tracking_lines, ""])

    lines.extend(
        [
            "## Objective",
            request or summary or "Canonical feature objective still needs a concise statement in business.md.",
            "",
            "## Source Artifacts",
        ]
    )
    lines.extend([f"- `{artifact}`" for artifact in source_artifacts])
    lines.append("")

    if problem:
        lines.extend(["## Problem Statement", problem, ""])

    lines.extend(["## Business Value Snapshot"])
    if business_value:
        lines.extend([f"- {item}" for item in business_value])
    else:
        lines.append("- Capture business-value bullets in business.md before review.")
    lines.append("")

    lines.extend(["## Scope Snapshot"])
    if scope_snapshot:
        lines.extend([f"- {item}" for item in scope_snapshot])
    else:
        lines.append("- Scope still needs explicit bullets or numbered items.")
    lines.append("")

    lines.extend(["## Acceptance Snapshot"])
    if acceptance_snapshot:
        lines.extend([f"- {item}" for item in acceptance_snapshot])
    else:
        lines.append("- Acceptance criteria are still missing or unstructured.")
    lines.append("")

    lines.extend(["## Review Readiness"])
    lines.append(f"- Open questions captured: {len(open_questions)}")
    lines.append(f"- Feedback source documents found: {len(feedback_candidates)}")
    lines.append(f"- Tracker/reference status: {'configured' if tracking else 'not configured'}")
    if latest_feedback:
        lines.append(f"- Latest feedback candidate: `{latest_feedback['name']}`")
    lines.append(f"- Pending feedback reconciliation: {'Yes' if pending_feedback else 'No'}")
    lines.append("")

    if open_questions:
        lines.extend(["## Current Open Questions", *[f"- {item}" for item in open_questions], ""])

    return {
        "featureTitle": feature_title,
        "outputPath": str(paths["spec_brief"]),
        "tracking": tracking,
        "sourceArtifacts": source_artifacts,
        "openQuestionsCount": len(open_questions),
        "content": "\n".join(lines).rstrip() + "\n",
    }


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    feature_dir = resolve_feature_dir(repo_root, args.feature_reference)
    feature_title = derive_feature_title(feature_dir, args.feature_title)
    result = build_spec_brief(feature_dir, feature_title)

    if args.write:
        write_text(Path(result["outputPath"]), result["content"])

    payload = {key: value for key, value in result.items() if key != "content"}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Spec brief: {result['outputPath']}")
        print(f"Source artifacts: {', '.join(result['sourceArtifacts'])}")
        print(f"Open questions captured: {result['openQuestionsCount']}")
        if args.write:
            print("Wrote spec-brief.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
