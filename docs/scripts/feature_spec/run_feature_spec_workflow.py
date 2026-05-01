#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from feature_spec_common import (
    get_standard_paths,
    latest_feedback_candidate,
    parse_reconciliation_status,
    read_text_if_exists,
    resolve_feature_dir,
    resolve_repo_root,
    set_reconciliation_status,
    update_round_state,
    write_text,
    now_iso,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature_reference")
    parser.add_argument("--repo-root")
    parser.add_argument("--feature-title")
    parser.add_argument("--tracker-label", action="append")
    parser.add_argument("--tracker-id", action="append")
    parser.add_argument("--tracker-url", action="append")
    parser.add_argument("--require-tracker", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--reconcile-latest-reviewed", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def run_json(script_name: str, *extra: str) -> Dict[str, Any]:
    command = ["python3", str(SCRIPT_DIR / script_name), *extra, "--json"]
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return json.loads(completed.stdout)


def maybe_reconcile_business(feature_dir: Path) -> Dict[str, Any]:
    candidate = latest_feedback_candidate(feature_dir, include_processed=False)
    if not candidate:
        return {"applied": False, "reason": "No unreconciled feedback candidate found."}
    if candidate.get("kind") != "reviewed_doc":
        return {
            "applied": False,
            "reason": "Only reviewed source snapshots can be promoted into canonical business.md automatically.",
            "feedbackCandidate": candidate,
        }

    reconciliation_path = Path(candidate["reconciliationPath"])
    reconciliation_text = read_text_if_exists(reconciliation_path)
    if not reconciliation_text:
        return {
            "applied": False,
            "reason": "Missing reconciliation surface for the latest feedback round.",
            "reconciliationPath": str(reconciliation_path),
        }

    status = parse_reconciliation_status(reconciliation_text)
    if not status.get("classificationComplete"):
        return {
            "applied": False,
            "reason": "Classification is not marked complete for the latest feedback round.",
            "feedbackCandidate": candidate,
            "reconciliationPath": str(reconciliation_path),
        }

    source_path = Path(candidate["path"])
    business_path = feature_dir / "business.md"
    canonical_updated = False
    if status.get("promoteSourceDocument"):
        business_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
        canonical_updated = True
    elif status.get("canonicalUpdatedManually"):
        canonical_updated = True
    else:
        return {
            "applied": False,
            "reason": "Reconciliation is classified, but canonical update intent is not recorded.",
            "feedbackCandidate": candidate,
            "reconciliationPath": str(reconciliation_path),
        }

    updated_reconciliation = set_reconciliation_status(reconciliation_text, roundProcessed=True)
    write_text(reconciliation_path, updated_reconciliation)
    update_round_state(
        feature_dir,
        candidate["roundKey"],
        {
            "label": candidate["roundKey"],
            "sourcePath": candidate["path"],
            "sourceName": candidate["name"],
            "changeLogPath": candidate["changeLogPath"],
            "reconciliationPath": candidate["reconciliationPath"],
            "snapshotPath": candidate["snapshotPath"],
            "status": "reconciled",
            "updatedAt": now_iso(),
            "canonicalUpdated": canonical_updated,
        },
    )

    return {
        "applied": True,
        "feedbackCandidate": candidate,
        "reconciliationPath": str(reconciliation_path),
        "canonicalUpdated": canonical_updated,
        "promotedSourceDocument": bool(status.get("promoteSourceDocument")),
        "manualCanonicalUpdateRecorded": bool(status.get("canonicalUpdatedManually")),
        "target": str(business_path),
    }


def existing_path_str(path: Path) -> str | None:
    return str(path) if path.exists() else None


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    feature_dir = resolve_feature_dir(repo_root, args.feature_reference)
    paths = get_standard_paths(feature_dir)

    steps: List[Dict[str, Any]] = []

    intake = run_json(
        "build_spec_brief.py",
        args.feature_reference,
        "--repo-root",
        str(repo_root),
        *(["--feature-title", args.feature_title] if args.feature_title else []),
        "--write",
    )
    steps.append({"step": "intake", "result": intake})

    tracker_cmd = [args.feature_reference, "--repo-root", str(repo_root), "--write-artifacts"]
    if args.feature_title:
        tracker_cmd.extend(["--feature-title", args.feature_title])
    for label in args.tracker_label or []:
        tracker_cmd.extend(["--tracker-label", label])
    for identifier in args.tracker_id or []:
        tracker_cmd.extend(["--tracker-id", identifier])
    for url in args.tracker_url or []:
        tracker_cmd.extend(["--tracker-url", url])
    if args.require_tracker:
        tracker_cmd.append("--require-tracker")
    tracker = run_json("reconcile_feature_tracking.py", *tracker_cmd)
    steps.append({"step": "tracker-sync", "result": tracker})

    questions = run_json(
        "update_question_manager.py",
        args.feature_reference,
        "--repo-root",
        str(repo_root),
        *(["--feature-title", args.feature_title] if args.feature_title else []),
        "--write",
    )
    steps.append({"step": "question-manager", "result": questions})

    latest_feedback = latest_feedback_candidate(feature_dir, include_processed=True)
    pending_feedback = latest_feedback_candidate(feature_dir, include_processed=False)

    review_diff = None
    current_feedback = pending_feedback or latest_feedback
    existing_round_package = bool(
        current_feedback
        and Path(current_feedback["snapshotPath"]).exists()
        and Path(current_feedback["changeLogPath"]).exists()
        and Path(current_feedback["reconciliationPath"]).exists()
    )
    if current_feedback and current_feedback.get("processed"):
        review_diff = {
            "reused": True,
            "reason": f"Latest feedback round `{current_feedback['name']}` is already reconciled; reusing the stored round package.",
            "feedbackCandidate": current_feedback,
        }
        steps.append({"step": "review-diff", "result": review_diff})
    elif existing_round_package:
        review_diff = {
            "reused": True,
            "reason": f"Existing review-round package already exists for `{current_feedback['name']}`.",
            "feedbackCandidate": current_feedback,
        }
        steps.append({"step": "review-diff", "result": review_diff})
    else:
        try:
            review_diff = run_json(
                "diff_review_round.py",
                args.feature_reference,
                "--repo-root",
                str(repo_root),
                *(["--feature-title", args.feature_title] if args.feature_title else []),
                "--write",
            )
            steps.append({"step": "review-diff", "result": review_diff})
        except subprocess.CalledProcessError as exc:
            reason = (exc.stderr or exc.stdout or str(exc)).strip()
            if "No feedback document found" in reason:
                steps.append({"step": "review-diff", "result": {"skipped": True, "reason": "No feedback document found."}})
            else:
                steps.append({"step": "review-diff", "result": {"blocked": True, "reason": reason}})

    latest_feedback = latest_feedback_candidate(feature_dir, include_processed=True)
    pending_feedback = latest_feedback_candidate(feature_dir, include_processed=False)

    reconcile_result = {"applied": False}
    if args.reconcile_latest_reviewed and args.apply:
        reconcile_result = maybe_reconcile_business(feature_dir)
        steps.append({"step": "reconcile-latest-reviewed", "result": reconcile_result})
        intake = run_json(
            "build_spec_brief.py",
            args.feature_reference,
            "--repo-root",
            str(repo_root),
            *(["--feature-title", args.feature_title] if args.feature_title else []),
            "--write",
        )
        questions = run_json(
            "update_question_manager.py",
            args.feature_reference,
            "--repo-root",
            str(repo_root),
            *(["--feature-title", args.feature_title] if args.feature_title else []),
            "--write",
        )
        steps.extend(
            [
                {"step": "intake-refresh", "result": intake},
                {"step": "question-manager-refresh", "result": questions},
            ]
        )
        latest_feedback = latest_feedback_candidate(feature_dir, include_processed=True)
        pending_feedback = latest_feedback_candidate(feature_dir, include_processed=False)

    blockers: List[str] = []
    tracker_ready = bool(tracker.get("trackerReady", not tracker.get("missing")))
    if not tracker_ready:
        blockers.append("Tracker/reference linkage is incomplete; keep this feature in local drafting mode until the reference state is explicit.")
    if pending_feedback:
        blockers.append(
            f"Incoming feedback round `{pending_feedback['name']}` is not fully reconciled yet; update the paired reconciliation file before continuing."
        )
    review_pack = None
    kb = None
    scope_lock = None
    handoff = None

    if pending_feedback:
        steps.append(
            {
                "step": "review-pack",
                "result": {
                    "skipped": True,
                    "reason": f"Latest feedback round `{pending_feedback['name']}` is still pending reconciliation.",
                },
            }
        )
        steps.append(
            {
                "step": "knowledge-base",
                "result": {"skipped": True, "reason": "Update shared lessons after the feedback round is reconciled."},
            }
        )
        steps.append(
            {
                "step": "scope-lock",
                "result": {"skipped": True, "reason": "Scope lock stays blocked while feedback reconciliation is pending."},
            }
        )
        steps.append(
            {
                "step": "spec-handoff",
                "result": {"skipped": True, "reason": "Engineering handoff is blocked while feedback reconciliation is pending."},
            }
        )
    else:
        review_pack = run_json(
            "build_review_pack.py",
            args.feature_reference,
            "--repo-root",
            str(repo_root),
            *(["--feature-title", args.feature_title] if args.feature_title else []),
            "--write",
        )
        steps.append({"step": "review-pack", "result": review_pack})

        kb = run_json("update_spec_knowledge_base.py", args.feature_reference, "--repo-root", str(repo_root), "--write")
        steps.append({"step": "knowledge-base", "result": kb})

        scope_lock = run_json(
            "build_scope_lock.py",
            args.feature_reference,
            "--repo-root",
            str(repo_root),
            *(["--feature-title", args.feature_title] if args.feature_title else []),
            "--write",
        )
        steps.append({"step": "scope-lock", "result": scope_lock})

        if scope_lock.get("blockingQuestions"):
            blockers.append("Blocking questions remain unresolved.")
        if scope_lock.get("openDecisions"):
            blockers.append("Open decisions remain unresolved.")

        handoff = run_json(
            "build_spec_handoff.py",
            args.feature_reference,
            "--repo-root",
            str(repo_root),
            *(["--feature-title", args.feature_title] if args.feature_title else []),
            "--write",
        )
        steps.append({"step": "spec-handoff", "result": handoff})

    if pending_feedback:
        current_stage = "review-reconciliation"
        next_action = f"Finish `{pending_feedback['name']}` reconciliation before generating a new review pack or handoff."
    elif not tracker_ready:
        current_stage = "tracker-sync"
        next_action = "Resolve or confirm the required tracker/reference, then refresh tracking in the feature artifacts."
    elif questions.get("questionCount") or questions.get("decisionCount"):
        current_stage = "questions-and-decisions"
        next_action = "Triage the remaining questions and decision candidates, then refresh the business review pack."
    else:
        current_stage = "review-ready"
        next_action = "Use the generated review pack for the next business loop, or proceed to scope lock if approval is already explicit."

    review_context = {
        "recommended": bool(tracker_ready and pending_feedback is None and review_pack is not None),
        "purpose": "Fresh second-pass review of outbound business artifacts against the canonical/base artifacts before external send.",
        "promptPath": str(repo_root / "docs/FEATURE_SPEC_COOKBOOK/FINAL_REVIEW_PROMPT.MD"),
        "recommendedAgentType": "explorer",
        "freshContextRequired": True,
        "forkContext": False,
        "baseArtifacts": {
            "business": str(paths["business"]),
            "specBrief": existing_path_str(paths["spec_brief"]),
            "openQuestions": existing_path_str(paths["open_questions"]),
            "decisionLog": existing_path_str(paths["decision_log"]),
        },
        "finalArtifacts": {
            "reviewPack": existing_path_str(paths["review_pack"]),
            "reviewMessage": existing_path_str(paths["review_message"]),
        },
        "latestFeedbackArtifacts": (
            {
                "source": latest_feedback["path"],
                "snapshot": latest_feedback.get("snapshotPath"),
                "changeLog": latest_feedback.get("changeLogPath"),
                "reconciliation": latest_feedback.get("reconciliationPath"),
                "processed": latest_feedback.get("processed", False),
                "stateStatus": latest_feedback.get("stateStatus"),
            }
            if latest_feedback
            else None
        ),
        "workflowSummary": {
            "currentStage": current_stage,
            "trackerReady": tracker_ready,
            "pendingFeedback": pending_feedback["name"] if pending_feedback else None,
            "readyForBusinessReview": bool(tracker_ready and pending_feedback is None and review_pack is not None),
            "readyForEngineeringHandoff": bool(handoff and handoff.get("readyForEngineeringCookbook")) and not blockers,
            "questionCount": questions.get("questionCount", 0),
            "decisionCount": questions.get("decisionCount", 0),
        },
        "reviewerChecklist": [
            "Confirm business-review-pack.md and business-review-message.md match business.md.",
            "Confirm blocking questions and decisions match the current ledgers.",
            "Confirm asks are concrete and business-usable.",
            "Confirm readiness wording matches tracker/reference state and feedback reconciliation state.",
            "Confirm the outbound message does not omit an important ask from the pack.",
        ],
    }

    payload = {
        "featureDir": str(feature_dir),
        "steps": steps,
        "latestFeedbackCandidate": latest_feedback,
        "pendingFeedbackCandidate": pending_feedback,
        "trackerReady": tracker_ready,
        "currentStage": current_stage,
        "blockingReason": blockers[0] if blockers else None,
        "nextAction": next_action,
        "blockers": blockers,
        "readyForBusinessReview": tracker_ready and pending_feedback is None and review_pack is not None,
        "readyForEngineeringHandoff": bool(handoff and handoff.get("readyForEngineeringCookbook")) and not blockers,
        "reviewContext": review_context,
        "artifacts": {key: str(path) for key, path in paths.items()},
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Feature folder: {feature_dir}")
        for step in steps:
            print(f"- {step['step']}")
        if latest_feedback:
            print(f"Latest feedback candidate: {latest_feedback['name']}")
        if blockers:
            print("Blockers:")
            for blocker in blockers:
                print(f"  - {blocker}")
        else:
            print("No active blockers in the generated workflow state.")
        print(f"Ready for business review: {payload['readyForBusinessReview']}")
        print(f"Ready for engineering handoff: {payload['readyForEngineeringHandoff']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
