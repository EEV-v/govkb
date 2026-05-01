#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from feature_spec_common import (
    build_review_round_paths,
    derive_feature_title,
    latest_feedback_candidate,
    normalize_text,
    now_iso,
    parse_reconciliation_status,
    read_text_if_exists,
    read_review_state,
    resolve_feature_dir,
    resolve_repo_root,
    review_round_label,
    update_round_state,
    write_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature_reference")
    parser.add_argument("--repo-root")
    parser.add_argument("--feature-title")
    parser.add_argument("--reviewed-doc")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def significant_lines(text: str) -> List[str]:
    lines: List[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped in {"---", "##", "#"}:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        cleaned = stripped.lstrip("-* ")
        cleaned = re.sub(r"^\d+\.\s+", "", cleaned)
        cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if cleaned:
            lines.append(cleaned)
    return lines


def unique_preserve(lines: List[str]) -> List[str]:
    result: List[str] = []
    seen: set[str] = set()
    for line in lines:
        key = normalize_text(line)
        if key and key not in seen:
            result.append(line)
            seen.add(key)
    return result


def classify_added(line: str) -> str:
    lowered = line.casefold()
    if "?" in line:
        return "needs_clarification"
    if any(token in lowered for token in ["phase 1", "phase 2", "phase 3", "when available", "future", "later scope"]):
        return "deferred"
    if any(
        token in lowered
        for token in [
            "sla",
            "owner",
            "escalation",
            "approval",
            "override",
            "lifecycle",
            "retention",
            "service layer",
            "api",
            "field level",
            "must",
            "require",
            "daily",
        ]
    ):
        return "candidate_addition"
    return "candidate_addition"


def build_reconciliation_template(
    *,
    feature_title: str,
    source_name: str,
    change_log_name: str,
    candidate_additions: List[str],
    clarify: List[str],
    deferred: List[str],
    removed: List[str],
) -> str:
    lines = [
        f"# Review Round Reconciliation — {feature_title}",
        "",
        f"Last updated: {now_iso()}",
        "",
        "## Source Round",
        f"- Source feedback: `{source_name}`",
        f"- Change log: `{change_log_name}`",
        "",
        "## Workflow Status",
        "- Classification complete: No",
        "- Promote source document as canonical: No",
        "- Canonical business.md updated manually: No",
        "- Round processed: No",
        "",
        "## Candidate Additions To Evaluate",
    ]
    if candidate_additions:
        lines.extend([f"- {line}" for line in candidate_additions])
    else:
        lines.append("- No clear candidate additions were detected.")
    lines.extend(["", "## Clarifications To Resolve"])
    if clarify:
        lines.extend([f"- {line}" for line in clarify])
    else:
        lines.append("- No explicit clarification items were detected.")
    lines.extend(["", "## Deferred / Later Scope"])
    if deferred:
        lines.extend([f"- {line}" for line in deferred])
    else:
        lines.append("- No explicit later-scope additions were detected.")
    lines.extend(["", "## Removed Or Narrowed Statements"])
    if removed:
        lines.extend([f"- {line}" for line in removed])
    else:
        lines.append("- No material removals were detected.")
    lines.extend(
        [
            "",
            "## Rejected / Not Merging",
            "- Add explicit bullets here when business wording should not be merged into `business.md`.",
            "",
            "## Merge Notes",
            "- Keep the copied source snapshot immutable.",
            "- Update `business.md` only after candidate additions are confirmed.",
            "- Set `Promote source document as canonical: Yes` only if the returned source document should replace `business.md` wholesale.",
            "- Set `Canonical business.md updated manually: Yes` if changes were merged selectively into `business.md`.",
            "- Mark `Classification complete: Yes` once the sections above reflect the intended disposition.",
            "- Mark `Round processed: Yes` only after the canonical draft is updated and the round is fully reconciled.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_change_log(feature_dir: Path, feature_title: str, reviewed_doc: Path) -> Dict[str, object]:
    business_path = feature_dir / "business.md"
    business_text = read_text_if_exists(business_path)
    reviewed_text = read_text_if_exists(reviewed_doc)
    if not business_text or not reviewed_text:
        raise RuntimeError("Both business.md and reviewed doc content are required.")

    base_lines = significant_lines(business_text)
    new_lines = significant_lines(reviewed_text)
    diff = list(difflib.ndiff(base_lines, new_lines))
    additions = unique_preserve([line[2:] for line in diff if line.startswith("+ ")])
    removals = unique_preserve([line[2:] for line in diff if line.startswith("- ")])

    candidate_additions = [line for line in additions if classify_added(line) == "candidate_addition"]
    deferred = [line for line in additions if classify_added(line) == "deferred"]
    clarify = [line for line in additions if classify_added(line) == "needs_clarification"]
    removed = removals

    round_paths = build_review_round_paths(feature_dir, reviewed_doc)
    snapshot_path = round_paths["snapshot"]
    change_log_path = round_paths["change_log"]
    reconciliation_path = round_paths["reconciliation"]

    lines = [
        f"# Review Round Diff — {feature_title}",
        "",
        "## Compared Documents",
        f"- Canonical: `{business_path.name}`",
        f"- Source feedback: `{reviewed_doc.name}`",
        "",
        "## Diff Totals",
        f"- Additions: {len(additions)}",
        f"- Removals: {len(removals)}",
        f"- Net: {len(additions) - len(removals)}",
        "",
        "## Candidate Additions To Evaluate",
    ]
    if candidate_additions:
        lines.extend([f"- {line}" for line in candidate_additions])
    else:
        lines.append("- No clear candidate additions detected.")
    lines.extend(["", "## Needs Clarification"])
    if clarify:
        lines.extend([f"- {line}" for line in clarify])
    else:
        lines.append("- No question-like additions detected.")
    lines.extend(["", "## Deferred / Later Scope"])
    if deferred:
        lines.extend([f"- {line}" for line in deferred])
    else:
        lines.append("- No explicit later-scope additions detected.")
    lines.extend(["", "## Removed Or Narrowed Statements"])
    if removed:
        lines.extend([f"- {line}" for line in removed])
    else:
        lines.append("- No material removals detected.")
    lines.extend(
        [
            "",
            "## Reconciliation Note",
            "- Use the paired `*-reconciliation.md` file to record accepted, rejected, deferred, and clarify decisions for this round.",
            "- Reviewed snapshots stay immutable; do not overwrite `business.md` automatically.",
            "",
        ]
    )

    reconciliation_content = build_reconciliation_template(
        feature_title=feature_title,
        source_name=reviewed_doc.name,
        change_log_name=change_log_path.name,
        candidate_additions=candidate_additions,
        clarify=clarify,
        deferred=deferred,
        removed=removed,
    )
    existing_reconciliation = read_text_if_exists(reconciliation_path)
    reconciliation_status = parse_reconciliation_status(existing_reconciliation)

    if reconciliation_status.get("roundProcessed"):
        state_status = "reconciled"
    elif reconciliation_status.get("classificationComplete"):
        state_status = "classified"
    else:
        state_status = "diffed"

    return {
        "featureTitle": feature_title,
        "feedbackCandidate": {
            "path": str(reviewed_doc),
            "name": reviewed_doc.name,
            "roundKey": review_round_label(reviewed_doc),
        },
        "snapshotPath": str(snapshot_path),
        "changeLogPath": str(change_log_path),
        "reconciliationPath": str(reconciliation_path),
        "additions": len(additions),
        "removals": len(removals),
        "stateStatus": state_status,
        "reconciliationStatus": reconciliation_status,
        "content": "\n".join(lines).rstrip() + "\n",
        "snapshotContent": reviewed_text,
        "reconciliationContent": reconciliation_content,
    }


def ensure_round_paths_safe(feature_dir: Path, result: Dict[str, object], reviewed_doc: Path) -> None:
    round_key = result["feedbackCandidate"]["roundKey"]
    state_entry = read_review_state(feature_dir).get("rounds", {}).get(round_key)
    if state_entry and state_entry.get("sourceName") != reviewed_doc.name:
        raise RuntimeError(
            f"Round label collision for `{round_key}`. Existing round points to `{state_entry.get('sourceName')}`; "
            f"rename the new feedback file or pass `--reviewed-doc` explicitly with a distinct source artifact."
        )

    snapshot_path = Path(result["snapshotPath"])
    snapshot_content = str(result["snapshotContent"])
    if snapshot_path.exists():
        existing_snapshot = snapshot_path.read_text(encoding="utf-8")
        if existing_snapshot != snapshot_content:
            raise RuntimeError(
                f"Immutable snapshot already exists with different content: {snapshot_path}. "
                "Rename the source file to start a new review round instead of overwriting archived evidence."
            )


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    feature_dir = resolve_feature_dir(repo_root, args.feature_reference)
    feature_title = derive_feature_title(feature_dir, args.feature_title)

    if args.reviewed_doc:
        reviewed_doc = Path(args.reviewed_doc).resolve()
    else:
        candidate = latest_feedback_candidate(feature_dir, include_processed=False)
        if candidate is None:
            candidate = latest_feedback_candidate(feature_dir, include_processed=True)
        reviewed_doc = Path(candidate["path"]).resolve() if candidate else None
    if reviewed_doc is None:
        raise RuntimeError(f"No feedback document found under {feature_dir}")

    result = build_change_log(feature_dir, feature_title, reviewed_doc)
    if args.write:
        ensure_round_paths_safe(feature_dir, result, reviewed_doc)
        snapshot_path = Path(result["snapshotPath"])
        change_log_path = Path(result["changeLogPath"])
        if not snapshot_path.exists():
            write_text(snapshot_path, result["snapshotContent"])
        if not change_log_path.exists():
            write_text(change_log_path, result["content"])
        reconciliation_path = Path(result["reconciliationPath"])
        if not reconciliation_path.exists():
            write_text(reconciliation_path, result["reconciliationContent"])
        update_round_state(
            feature_dir,
            result["feedbackCandidate"]["roundKey"],
            {
                "label": result["feedbackCandidate"]["roundKey"],
                "sourcePath": result["feedbackCandidate"]["path"],
                "sourceName": result["feedbackCandidate"]["name"],
                "changeLogPath": result["changeLogPath"],
                "reconciliationPath": result["reconciliationPath"],
                "snapshotPath": result["snapshotPath"],
                "status": result["stateStatus"],
                "updatedAt": now_iso(),
                "canonicalUpdated": bool(
                    result["reconciliationStatus"].get("promoteSourceDocument")
                    or result["reconciliationStatus"].get("canonicalUpdatedManually")
                ),
            },
        )

    payload = {key: value for key, value in result.items() if key not in {"content", "snapshotContent", "reconciliationContent"}}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Feedback source: {result['feedbackCandidate']['name']}")
        print(f"Reviewed snapshot: {payload['snapshotPath']}")
        print(f"Change log: {payload['changeLogPath']}")
        print(f"Reconciliation: {payload['reconciliationPath']}")
        print(f"Additions: {payload['additions']} | Removals: {payload['removals']}")
        if args.write:
            print("Stored immutable source snapshot, round diff, and reconciliation surface under review-rounds/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
