#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
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


def extract_scope_lines(business_text: str, limit: int = 8) -> List[str]:
    headings = ["Scope", "Purpose & Scope", "Request", "Acceptance Criteria"]
    lines: List[str] = []
    for heading in headings:
        section_body = extract_section_body(business_text, heading)
        if not section_body:
            continue
        for raw_line in section_body.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            if stripped.startswith(("- ", "* ")):
                lines.append(stripped[2:].strip())
            elif re.match(r"^\d+\.\s+", stripped):
                lines.append(re.split(r"^\d+\.\s+", stripped, maxsplit=1)[1].strip())
        if lines:
            return lines[:limit]
        prose = [line.strip() for line in section_body.splitlines() if line.strip() and not line.strip().startswith("## ")]
        if prose:
            return prose[: min(limit, 3)]
    return []


def concrete_rows(rows: List[Dict[str, str]], *, text_key: str, placeholder_text: str) -> List[Dict[str, str]]:
    return [row for row in rows if not is_generated_placeholder(row, text_key, placeholder_text)]


def note_suffix(row: Dict[str, str], default_note: str) -> str:
    note = (row.get("Notes") or "").strip()
    if not note or note == default_note:
        return ""
    return f" — {outward_text(note)}"


def message_note_suffix(row: Dict[str, str], default_note: str) -> str:
    note = (row.get("Notes") or "").strip()
    if not note or note == default_note:
        return ""
    return f" — {outward_text(note)}"


def outward_text(text: str) -> str:
    return (
        text.replace(" `business.md`", "")
        .replace(" (business.md)", "")
        .replace(" from `business.md`", "")
        .replace(" from business.md", "")
    )


def build_documents(feature_dir: Path, feature_title: str) -> Dict[str, str]:
    paths = get_standard_paths(feature_dir)
    business_text = read_text_if_exists(paths["business"]) or ""
    tracking = parse_tracking_block(business_text)
    question_rows = parse_markdown_table(read_text_if_exists(paths["open_questions"]))
    decision_rows = parse_markdown_table(read_text_if_exists(paths["decision_log"]))
    pending_feedback = latest_feedback_candidate(feature_dir, include_processed=False)
    latest_feedback = latest_feedback_candidate(feature_dir, include_processed=True)

    blocking_questions = [
        row
        for row in concrete_rows(question_rows, text_key="Question", placeholder_text="No explicit open questions captured yet.")
        if row.get("Status") == "Blocking" and row.get("Blocking", "Yes") != "No"
    ]
    deferred_questions = [
        row
        for row in concrete_rows(question_rows, text_key="Question", placeholder_text="No explicit open questions captured yet.")
        if row.get("Status") == "Deferred"
    ]
    open_decisions = [
        row
        for row in concrete_rows(decision_rows, text_key="Decision / Candidate", placeholder_text="No explicit decisions recorded yet.")
        if row.get("Status") == "Open"
    ]
    scope_confirmation_rows = [
        row
        for row in blocking_questions
        if "initial scope" in row.get("Question", "").casefold() or "scope" in row.get("Question", "").casefold()
    ]
    scope_confirmation_questions = {row.get("Question", "") for row in scope_confirmation_rows}
    deferred_decisions = [
        row
        for row in concrete_rows(decision_rows, text_key="Decision / Candidate", placeholder_text="No explicit decisions recorded yet.")
        if row.get("Status") == "Deferred"
    ]
    scope_lines = extract_scope_lines(business_text, limit=8)
    tracker_configured = bool(tracking)
    feedback_ready = pending_feedback is None
    review_ready = feedback_ready

    pack_lines = [
        f"# Business Review Pack — {feature_title}",
        "",
        "## Review Readiness",
        f"- Ready to send for business review: {'Yes' if review_ready else 'No'}",
        f"- Tracker/reference status: {'configured' if tracker_configured else 'not configured'}",
        f"- Feedback reconciliation clear: {'Yes' if feedback_ready else 'No'}",
        f"- Pending feedback round: `{pending_feedback['name']}`" if pending_feedback else "- Pending feedback round: none",
        (
            "- External send guard: satisfied."
            if review_ready
            else "- Do not send this pack externally until pending feedback is reconciled."
        ),
        "",
        "## Scope Snapshot",
    ]
    if scope_lines:
        pack_lines.extend([f"- {line}" for line in scope_lines])
    else:
        pack_lines.append("- Scope summary still needs a clearer section in business.md before review.")
    pack_lines.append("")

    if scope_confirmation_rows:
        pack_lines.extend(["## Scope To Confirm"])
        for row in scope_confirmation_rows[:3]:
            pack_lines.append(
                f"- {outward_text(row['Question'])}"
                f"{note_suffix(row, 'Needs business answer or explicit deferral.')}"
            )
        pack_lines.append("")

    pack_lines.extend(["## Decisions To Confirm"])
    if open_decisions:
        for row in open_decisions[:8]:
            pack_lines.append(
                f"- {outward_text(row['Decision / Candidate'])}"
                f"{note_suffix(row, 'Promote to Approved / Deferred / Rejected during review.')}"
            )
    else:
        pack_lines.append("- No explicit open decisions are currently tracked.")
    pack_lines.append("")

    pack_lines.extend(["## Blocking Questions"])
    if blocking_questions:
        for row in blocking_questions[:10]:
            if row.get("Question", "") in scope_confirmation_questions:
                continue
            pack_lines.append(
                f"- {outward_text(row['Question'])}"
                f"{note_suffix(row, 'Needs business answer or explicit deferral.')}"
            )
    else:
        pack_lines.append("- No blocking questions are currently tracked.")
    pack_lines.append("")

    if deferred_questions or deferred_decisions:
        pack_lines.extend(["## Deferred / Later Scope"])
        for row in deferred_questions[:6]:
            pack_lines.append(f"- Question deferred: {row['Question']}")
        for row in deferred_decisions[:6]:
            pack_lines.append(f"- Decision deferred: {row['Decision / Candidate']}")
        pack_lines.append("")

    pack_lines.extend(
        [
            "## Requested Business Response",
            (
                "- Confirm which proposed scope items are approved now, which should move to a later phase, and which remain out of scope."
                if scope_confirmation_rows
                else "- Confirm which scope items are approved for the next iteration."
            ),
            "- Answer blocking questions directly or mark them as deferred.",
            "- Mark any decision candidates that should become approved policy.",
            "- Call out wording that is misleading, incomplete, or too broad.",
            "",
        ]
    )

    requested_response_lines: List[str] = []
    if pending_feedback:
        requested_response_lines.append(f"- reconcile feedback in `{pending_feedback['name']}` before sending a new review pack")
    if scope_confirmation_rows:
        for row in scope_confirmation_rows[:2]:
            requested_response_lines.append(
                f"- confirm scope: {outward_text(row['Question'])}"
                f"{message_note_suffix(row, 'Needs business answer or explicit deferral.')}"
            )
    if blocking_questions:
        for row in blocking_questions[:4]:
            if row.get("Question", "") in scope_confirmation_questions:
                continue
            requested_response_lines.append(
                f"- answer blocker: {outward_text(row['Question'])}"
                f"{message_note_suffix(row, 'Needs business answer or explicit deferral.')}"
            )
    if open_decisions:
        for row in open_decisions[:6]:
            requested_response_lines.append(
                f"- confirm decision: {outward_text(row['Decision / Candidate'])}"
                f"{message_note_suffix(row, 'Promote to Approved / Deferred / Rejected during review.')}"
            )
    requested_response_lines.append("- flag any wording that is misleading, incomplete, or too broad")
    if not requested_response_lines:
        requested_response_lines.append("- confirm the current wording and scope, or mark any sections that still need revision")

    message_lines = [
        f"Subject: {feature_title} — business review pack",
        "",
        f"Team,",
        "",
        f"We prepared the current review pack for `{feature_title}`.",
        "",
        "Current readiness:",
        f"- Ready to send: {'Yes' if review_ready else 'No'}",
        f"- Tracker/reference status: {'configured' if tracker_configured else 'not configured'}",
        f"- Feedback reconciliation clear: {'Yes' if feedback_ready else 'No'}",
        (
            "- Latest feedback round has been incorporated."
            if latest_feedback and latest_feedback.get("processed")
            else "- Latest feedback is still under review."
            if latest_feedback
            else "- Latest feedback candidate: none"
        ),
        "",
        "Requested response:",
        *requested_response_lines,
        "",
        "Thanks,",
        "GovKB Engineering",
        "",
    ]

    return {
        "reviewPack": "\n".join(pack_lines).rstrip() + "\n",
        "reviewMessage": "\n".join(message_lines).rstrip() + "\n",
    }


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    feature_dir = resolve_feature_dir(repo_root, args.feature_reference)
    feature_title = derive_feature_title(feature_dir, args.feature_title)
    paths = get_standard_paths(feature_dir)
    docs = build_documents(feature_dir, feature_title)

    if args.write:
        write_text(paths["review_pack"], docs["reviewPack"])
        write_text(paths["review_message"], docs["reviewMessage"])

    payload = {
        "featureDir": str(feature_dir),
        "featureTitle": feature_title,
        "reviewPackPath": str(paths["review_pack"]),
        "reviewMessagePath": str(paths["review_message"]),
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Review pack: {payload['reviewPackPath']}")
        print(f"Review message: {payload['reviewMessagePath']}")
        if args.write:
            print("Updated business-review-pack.md and business-review-message.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
