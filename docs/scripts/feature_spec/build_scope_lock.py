#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from typing import Dict, List, Optional

from feature_spec_common import (
    derive_feature_title,
    extract_section_body,
    get_standard_paths,
    latest_feedback_candidate,
    parse_markdown_table,
    parse_tracking_block,
    read_text_if_exists,
    resolve_feature_dir,
    resolve_repo_root,
    write_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature_reference")
    parser.add_argument("--repo-root")
    parser.add_argument("--feature-title")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def is_generated_placeholder(row: Dict[str, str], column_name: str, expected_text: str) -> bool:
    return row.get("Source") == "Generated" and row.get(column_name, "").strip() == expected_text


def extract_scope_lines(section_body: Optional[str], limit: int = 10) -> List[str]:
    if not section_body:
        return []
    result: List[str] = []
    for raw_line in section_body.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith(("- ", "* ")):
            result.append(stripped[2:].strip())
        elif re.match(r"^\d+\.\s+", stripped):
            result.append(re.split(r"^\d+\.\s+", stripped, maxsplit=1)[1].strip())
    return result[:limit]


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    feature_dir = resolve_feature_dir(repo_root, args.feature_reference)
    feature_title = derive_feature_title(feature_dir, args.feature_title)
    paths = get_standard_paths(feature_dir)

    business_text = read_text_if_exists(paths["business"]) or ""
    questions = parse_markdown_table(read_text_if_exists(paths["open_questions"]))
    decisions = parse_markdown_table(read_text_if_exists(paths["decision_log"]))
    tracking = parse_tracking_block(business_text)
    pending_feedback = latest_feedback_candidate(feature_dir, include_processed=False)

    blocking = [
        row
        for row in questions
        if not is_generated_placeholder(row, "Question", "No explicit open questions captured yet.")
        and row.get("Status") == "Blocking"
        and row.get("Blocking", "Yes") != "No"
    ]
    open_decisions = [
        row
        for row in decisions
        if not is_generated_placeholder(row, "Decision / Candidate", "No explicit decisions recorded yet.")
        and row.get("Status") == "Open"
    ]
    approved_decisions = [
        row
        for row in decisions
        if not is_generated_placeholder(row, "Decision / Candidate", "No explicit decisions recorded yet.")
        and row.get("Status") == "Approved"
    ]
    deferred = [
        row
        for row in decisions
        if not is_generated_placeholder(row, "Decision / Candidate", "No explicit decisions recorded yet.")
        and row.get("Status") == "Deferred"
    ]
    ready = not blocking and not open_decisions and pending_feedback is None
    scope_lines = extract_scope_lines(extract_section_body(business_text, "Scope"), limit=10)

    lines = [
        f"# Scope Lock — {feature_title}",
        "",
        "## Readiness",
        f"- Ready for engineering handoff: {'Yes' if ready else 'No'}",
        f"- Status: {'ready' if ready else 'blocked'}",
        f"- Blocking questions remaining: {len(blocking)}",
        f"- Open decisions remaining: {len(open_decisions)}",
        f"- Pending feedback rounds remaining: {1 if pending_feedback else 0}",
        f"- Tracker/reference status: {'configured' if tracking else 'not configured'}",
        "",
        "## Locked Scope Snapshot",
    ]
    if scope_lines:
        lines.extend([f"- {item}" for item in scope_lines])
    else:
        lines.append("- Scope needs structured bullets before lock.")
    lines.append("")

    lines.extend(["## Approved Decisions"])
    if approved_decisions:
        lines.extend([f"- {row['Decision / Candidate']}" for row in approved_decisions])
    else:
        lines.append("- No decisions are marked Approved yet.")
    lines.append("")

    lines.extend(["## Deferred Items"])
    if deferred:
        lines.extend([f"- {row['Decision / Candidate']}" for row in deferred])
    else:
        lines.append("- No deferred decisions are currently logged.")
    lines.append("")

    lines.extend(["## Unresolved Blockers"])
    if blocking:
        lines.extend([f"- {row['Question']}" for row in blocking])
    elif pending_feedback:
        lines.append(f"- Incoming feedback round `{pending_feedback['name']}` still needs reconciliation.")
    else:
        lines.append("- No blocking questions remain.")
    lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    if args.write:
        write_text(paths["scope_lock"], content)

    payload = {
        "featureDir": str(feature_dir),
        "scopeLockPath": str(paths["scope_lock"]),
        "readyForEngineeringHandoff": ready,
        "blockingQuestions": len(blocking),
        "openDecisions": len(open_decisions),
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Scope lock: {payload['scopeLockPath']}")
        print(f"Ready for handoff: {payload['readyForEngineeringHandoff']}")
        if args.write:
            print("Updated scope-lock.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
