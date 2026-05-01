#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from typing import Dict, List, Optional

from feature_spec_common import (
    derive_feature_title,
    get_standard_paths,
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


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    feature_dir = resolve_feature_dir(repo_root, args.feature_reference)
    feature_title = derive_feature_title(feature_dir, args.feature_title)
    paths = get_standard_paths(feature_dir)

    business_text = read_text_if_exists(paths["business"]) or ""
    tracking = parse_tracking_block(business_text)
    questions = parse_markdown_table(read_text_if_exists(paths["open_questions"]))
    decisions = parse_markdown_table(read_text_if_exists(paths["decision_log"]))
    scope_lock_text = read_text_if_exists(paths["scope_lock"]) or ""
    scope_lock_lower = scope_lock_text.casefold()
    ready = any(
        marker in scope_lock_lower
        for marker in [
            "ready for engineering handoff: yes",
            "ready for engineering cookbook: yes",
            "status: locked",
            "engineering may proceed",
        ]
    )

    approved = [
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
    unresolved = [
        row
        for row in questions
        if not is_generated_placeholder(row, "Question", "No explicit open questions captured yet.")
        and row.get("Status") == "Blocking"
        and row.get("Blocking", "Yes") != "No"
    ]

    lines = [
        f"# Spec Handoff — {feature_title}",
        "",
        "## Handoff Status",
        f"- Ready for engineering cookbook: {'Yes' if ready else 'No'}",
        f"- Status: {'ready' if ready else 'blocked'}",
        f"- Blocking questions remaining: {len(unresolved)}",
        f"- Approved decisions captured: {len(approved)}",
        f"- Deferred decisions captured: {len(deferred)}",
        "",
        "## Required Inputs For Engineering",
        "- business.md",
        "- business-context.md",
        "- context.md",
        "- spec-brief.md",
        "- open-questions.md",
        "- decision-log.md",
        "- scope-lock.md",
        "",
        "## Approved Decisions",
    ]
    if approved:
        lines.extend([f"- {row['Decision / Candidate']}" for row in approved])
    else:
        lines.append("- No decisions are marked Approved yet.")
    lines.append("")

    lines.extend(["## Deferred / Watch Items"])
    if deferred:
        lines.extend([f"- {row['Decision / Candidate']}" for row in deferred])
    else:
        lines.append("- No deferred decisions are logged.")
    lines.append("")

    lines.extend(["## Remaining Blockers"])
    if unresolved:
        lines.extend([f"- {row['Question']}" for row in unresolved])
    else:
        lines.append("- No blocking questions remain.")
    lines.append("")

    lines.extend(["## Tracker Context"])
    if tracking:
        for label, value in tracking.items():
            lines.append(f"- {label}: `{value['id']}` {value['url']}")
    else:
        lines.append("- Tracker references are not populated yet.")
    lines.append("")

    lines.extend(
        [
            "## Next Step",
            "- Once this handoff is ready, continue with `docs/COOKBOOK/COOKBOOK.MD` for use cases, PoC, and implementation phases.",
            "",
        ]
    )

    content = "\n".join(lines).rstrip() + "\n"
    if args.write:
        write_text(paths["spec_handoff"], content)

    payload = {
        "featureDir": str(feature_dir),
        "specHandoffPath": str(paths["spec_handoff"]),
        "readyForEngineeringCookbook": ready,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Spec handoff: {payload['specHandoffPath']}")
        print(f"Ready for engineering cookbook: {payload['readyForEngineeringCookbook']}")
        if args.write:
            print("Updated spec-handoff.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
