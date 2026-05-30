"""Read-only proposal queue reporting and quality warnings."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
from typing import Any

from govkb.core.project import resolve_project_root
from govkb.core.proposals import ProposalError
from govkb.core.proposals import list_proposals
from govkb.core.proposals import load_proposal


COMMON_TOPIC_TOKENS = {
    "check",
    "checklist",
    "clearing",
    "docs",
    "e2e",
    "helper",
    "on",
    "proposal",
    "qa",
    "report",
    "review",
    "runbook",
    "script",
    "staging",
    "sync",
    "tool",
    "workflow",
}
SCRIPT_TYPES = {"script", "wrapper"}
WEAK_VERIFICATION_VALUES = {
    "",
    "n/a",
    "n/a docs-only",
    "none",
    "no code execution required",
}
REVIEW_ACTIONS = {"inspect-safety", "manual-review", "merge-first", "reject-duplicate"}
REVIEW_ACTION_PRIORITY = {
    "inspect-safety": 0,
    "merge-first": 1,
    "reject-duplicate": 2,
    "manual-review": 3,
}


def build_proposal_report_payload(project_root: Path) -> dict[str, Any]:
    """Build an advisory read-only report for staged capability-evolution proposals."""
    resolved_root = resolve_project_root(project_root).resolve()
    proposals = _proposal_items(resolved_root)
    groups = _proposal_groups(proposals)
    warning_count = sum(len(item["warnings"]) for item in proposals)
    return {
        "schemaVersion": 1,
        "projectRoot": str(resolved_root),
        "summary": {
            "proposalCount": len(proposals),
            "groupCount": len(groups),
            "warningCount": warning_count,
            "actionCounts": dict(sorted(_count_by(groups, "recommendedAction").items())),
        },
        "groups": groups,
        "proposals": proposals,
    }


def build_proposal_review_payload(project_root: Path, action: str | None = None) -> dict[str, Any]:
    """Build an actionable read-only maintainer review queue for staged proposals."""
    report = build_proposal_report_payload(project_root)
    normalized_action = _normalize_action_filter(action)
    groups = [
        _review_group(report["projectRoot"], group)
        for group in report["groups"]
        if normalized_action is None or group["recommendedAction"] == normalized_action
    ]
    groups.sort(key=lambda group: (group["priority"], group["id"]))
    return {
        "schemaVersion": 1,
        "projectRoot": report["projectRoot"],
        "summary": {
            **report["summary"],
            "reviewGroupCount": len(groups),
            "actionFilter": normalized_action or "all",
        },
        "groups": groups,
    }


def _proposal_items(project_root: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    output_path_counts: dict[str, int] = defaultdict(int)
    loaded: list[tuple[Path, dict[str, Any]]] = []
    for proposal_root in list_proposals(project_root):
        try:
            _, data = load_proposal(project_root, proposal_root.name)
        except ProposalError as exc:
            items.append(
                {
                    "id": proposal_root.name,
                    "status": "invalid",
                    "targetCapability": None,
                    "proposalType": None,
                    "safetyClass": None,
                    "confidence": None,
                    "purpose": "",
                    "outputPaths": [],
                    "path": str(proposal_root),
                    "draftOutputPath": None,
                    "topicTokens": [],
                    "warnings": [{"code": "invalid-metadata", "message": str(exc)}],
                }
            )
            continue
        loaded.append((proposal_root, data))
        for output_path in _string_list(data.get("output_paths")):
            output_path_counts[output_path] += 1

    for proposal_root, data in loaded:
        item = _proposal_item(proposal_root, data)
        item["warnings"] = _proposal_warnings(item, proposal_root, data, output_path_counts)
        items.append(item)
    return sorted(items, key=lambda item: str(item["id"]))


def _proposal_item(proposal_root: Path, data: dict[str, Any]) -> dict[str, Any]:
    output_paths = _string_list(data.get("output_paths"))
    text = " ".join(
        [
            _string(data.get("id")),
            _string(data.get("purpose")),
            " ".join(output_paths),
        ]
    )
    return {
        "id": _string(data.get("id")) or proposal_root.name,
        "status": _string(data.get("status")) or "unknown",
        "targetCapability": _string(data.get("target_capability")),
        "proposalType": _string(data.get("proposal_type")),
        "safetyClass": _string(data.get("safety_class")),
        "confidence": _number(data.get("confidence")),
        "purpose": _string(data.get("purpose")),
        "verificationCommand": _string(data.get("verification_command")),
        "outputPaths": output_paths,
        "path": str(proposal_root),
        "draftOutputPath": str(proposal_root / "draft-output.md") if (proposal_root / "draft-output.md").is_file() else None,
        "topicTokens": sorted(_topic_tokens(text)),
    }


def _proposal_warnings(
    item: dict[str, Any],
    proposal_root: Path,
    data: dict[str, Any],
    output_path_counts: dict[str, int],
) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    confidence = item.get("confidence")
    if isinstance(confidence, int | float) and confidence < 0.85:
        warnings.append(
            {
                "code": "low-confidence",
                "message": f"confidence {confidence:.2f} is below the 0.85 auto-apply threshold",
            }
        )

    verification = _string(data.get("verification_command"))
    if _normalize_text(verification) in WEAK_VERIFICATION_VALUES:
        warnings.append(
            {
                "code": "weak-verification",
                "message": "verification command is placeholder or too weak for maintainer review",
            }
        )

    repeated_paths = [path for path in item["outputPaths"] if output_path_counts[path] > 1]
    if repeated_paths:
        warnings.append(
            {
                "code": "duplicate-output-path",
                "message": "another proposal targets the same output path: " + ", ".join(repeated_paths),
            }
        )

    proposal_type = str(item.get("proposalType") or "")
    safety_class = str(item.get("safetyClass") or "")
    draft_path = proposal_root / "draft-output.md"
    draft_text = draft_path.read_text(encoding="utf-8", errors="replace") if draft_path.is_file() else ""
    combined = "\n".join([draft_text, verification, _string(data.get("purpose"))])
    if proposal_type in SCRIPT_TYPES:
        if not draft_text.strip():
            warnings.append(
                {
                    "code": "missing-draft-output",
                    "message": "script or wrapper proposal has no draft output to review",
                }
            )
        if safety_class == "mutating_with_dry_run" and "--dry-run" not in combined and "--preview" not in combined:
            warnings.append(
                {
                    "code": "missing-dry-run",
                    "message": "mutating script proposal should document --dry-run or --preview behavior",
                }
            )
        verification_lower = verification.lower()
        if not any(token in verification_lower for token in ("--help", "py_compile", "compile", "unittest", "pytest")):
            warnings.append(
                {
                    "code": "weak-script-verification",
                    "message": "script proposal should include help, compile, or focused test verification",
                }
            )
    return warnings


def _proposal_groups(proposals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    parent = {str(item["id"]): str(item["id"]) for item in proposals}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for index, left in enumerate(proposals):
        for right in proposals[index + 1 :]:
            if _related(left, right):
                union(str(left["id"]), str(right["id"]))

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in proposals:
        grouped[find(str(item["id"]))].append(item)

    groups = [_group_payload(items) for items in grouped.values()]
    groups.sort(key=lambda group: (group["recommendedAction"], group["id"]))
    return groups


def _related(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if not left.get("targetCapability") or left.get("targetCapability") != right.get("targetCapability"):
        return False
    if left.get("proposalType") != right.get("proposalType"):
        return False
    left_paths = set(left.get("outputPaths") or [])
    right_paths = set(right.get("outputPaths") or [])
    if left_paths & right_paths:
        return True
    left_tokens = set(left.get("topicTokens") or [])
    right_tokens = set(right.get("topicTokens") or [])
    if not left_tokens or not right_tokens:
        return False
    overlap = len(left_tokens & right_tokens)
    union_count = len(left_tokens | right_tokens)
    return overlap >= 2 and (overlap / union_count) >= 0.35


def _group_payload(items: list[dict[str, Any]]) -> dict[str, Any]:
    items = sorted(items, key=lambda item: str(item["id"]))
    warning_codes = sorted({warning["code"] for item in items for warning in item["warnings"]})
    output_paths = sorted({path for item in items for path in item.get("outputPaths", [])})
    group_id = "group-" + str(items[0]["id"])
    action = _recommended_action(items, warning_codes, output_paths)
    return {
        "id": group_id,
        "proposalIds": [item["id"] for item in items],
        "targetCapabilities": sorted({item.get("targetCapability") for item in items if item.get("targetCapability")}),
        "proposalTypes": sorted({item.get("proposalType") for item in items if item.get("proposalType")}),
        "safetyClasses": sorted({item.get("safetyClass") for item in items if item.get("safetyClass")}),
        "outputPaths": output_paths,
        "warningCodes": warning_codes,
        "recommendedAction": action,
        "reason": _recommendation_reason(action, items, warning_codes, output_paths),
    }


def _recommended_action(items: list[dict[str, Any]], warning_codes: list[str], output_paths: list[str]) -> str:
    if any(code in warning_codes for code in ("missing-dry-run", "missing-draft-output", "weak-script-verification")):
        return "inspect-safety"
    if len(items) > 1:
        if len(output_paths) == 1:
            return "reject-duplicate"
        return "merge-first"
    return "manual-review"


def _review_group(project_root: str, group: dict[str, Any]) -> dict[str, Any]:
    action = str(group["recommendedAction"])
    show_commands = [
        f"govkb proposals show {proposal_id} --project-root {project_root}"
        for proposal_id in group["proposalIds"]
    ]
    return {
        "id": group["id"],
        "priority": REVIEW_ACTION_PRIORITY.get(action, 99),
        "recommendedAction": action,
        "proposalIds": group["proposalIds"],
        "targetCapabilities": group["targetCapabilities"],
        "warningCodes": group["warningCodes"],
        "outputPaths": group["outputPaths"],
        "reason": group["reason"],
        "nextSteps": _review_next_steps(project_root, action, group, show_commands),
        "commands": show_commands,
    }


def _review_next_steps(
    project_root: str,
    action: str,
    group: dict[str, Any],
    show_commands: list[str],
) -> list[str]:
    if action == "inspect-safety":
        return [
            "Inspect every proposal in this group before applying anything.",
            "Require visible draft output, dry-run or preview behavior for mutating scripts, and focused verification.",
            *show_commands,
        ]
    if action == "merge-first":
        return [
            "Compare the related proposals and reconcile them into one maintained artifact before applying.",
            "Apply only the preferred proposal after stale alternatives are rejected or restaged.",
            *show_commands,
        ]
    if action == "reject-duplicate":
        return [
            "Multiple related proposals target the same output path; keep one and reject the duplicate proposal folder.",
            *show_commands,
        ]
    proposal_id = str(group["proposalIds"][0]) if group["proposalIds"] else ""
    apply_command = f"govkb proposals apply {proposal_id} --project-root {project_root}" if proposal_id else ""
    steps = [
        "Review the proposal body and draft output.",
        *show_commands,
    ]
    if apply_command:
        steps.append(apply_command)
    return steps


def _normalize_action_filter(action: str | None) -> str | None:
    if action in (None, "", "all"):
        return None
    if action not in REVIEW_ACTIONS:
        raise ValueError(f"unsupported review action filter: {action}")
    return action


def _recommendation_reason(
    action: str,
    items: list[dict[str, Any]],
    warning_codes: list[str],
    output_paths: list[str],
) -> str:
    if action == "inspect-safety":
        return "one or more script/wrapper quality warnings require maintainer review"
    if action == "reject-duplicate":
        return "multiple related proposals target the same output path"
    if action == "merge-first":
        return "multiple related proposals should be reconciled before applying one governed artifact"
    if warning_codes:
        return "proposal has advisory warnings"
    return "proposal is unique in the current queue"


def _topic_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]{3,}", text.lower())
        if token not in COMMON_TOPIC_TOKENS and not token.isdigit()
    }


def _count_by(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for item in items:
        counts[str(item.get(key) or "unknown")] += 1
    return counts


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _number(value: object) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    return None


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())
