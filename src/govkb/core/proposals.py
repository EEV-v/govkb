"""Capability-evolution proposal storage and application."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any
import tomllib

from govkb.core.contracts import load_project_bundle
from govkb.core.governed_skill import validate_governed_skill_package
from govkb.core.ids import normalize_identifier
from govkb.core.install_state import iso_utc_now
from govkb.core.project import resolve_project_root


ALLOWED_PROPOSAL_TYPES = {
    "script",
    "wrapper",
    "prompt",
    "runbook",
    "instructions_update",
}
ALLOWED_SAFETY_CLASSES = {
    "read_only",
    "mutating_with_dry_run",
    "docs_only",
    "prompt_only",
    "instructions_only",
}
ALLOWED_DECISION_STATUSES = {
    "needs-rework",
    "merge-required",
    "needs-evidence",
    "superseded",
    "rejected",
}
SCRIPT_TYPES = {"script", "wrapper"}
MUTATING_PATTERNS = (
    re.compile(r"\brm\s+-"),
    re.compile(r"\bmv\s+"),
    re.compile(r"\bcp\s+"),
    re.compile(r"\bsed\s+-i\b"),
    re.compile(r"\b(write_text|unlink|rmtree|remove|rename)\b"),
)
TOKEN_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"(?i)\b[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY|APIKEY)[A-Z0-9_]*\b\s*[:=]\s*\S+"),
)
CREDENTIAL_PATH_PATTERNS = (
    re.compile(r"(?:^|[\s`])~/(?:\.ssh|\.aws|\.azure|\.config/gcloud|\.kube)(?:/|[\s`]|$)"),
    re.compile(r"(?:^|[/\s`])\.(?:netrc|npmrc|pypirc|env|env\.local)(?:$|[\s`])"),
    re.compile(r"(?:^|[/\s`])(?:id_rsa|id_ed25519)(?:$|[\s`])"),
    re.compile(r"(?i)(?:^|[/\s`])[^`\s]*(?:\.pem|\.key|\.p12)(?:$|[\s`])"),
    re.compile(
        r"(?i)(?:^|[\s`])(?:~?/|\.?/|[A-Za-z0-9_.-]+/)[^`\s]*"
        r"(?:credential|credentials|secret|secrets|token|service-account)[^`\s]*(?:$|[\s`])"
    ),
)
RAW_TRANSCRIPT_PATTERNS = (
    re.compile(r'"type"\s*:\s*"event_msg"'),
    re.compile(r'"payload"\s*:\s*\{'),
    re.compile(r"(?i)\braw (assistant |codex )?transcript\b"),
    re.compile(r"(?i)\bsession transcript\b"),
)
PRIVATE_EVIDENCE_PATTERNS = (
    re.compile(r"(?i)\bcustomer identifier\b"),
    re.compile(r"(?i)\bproduction evidence\b"),
    re.compile(r"(?i)\bprod token\b"),
)


class ProposalError(ValueError):
    """A proposal cannot be loaded, staged, or applied safely."""


@dataclass(frozen=True)
class ProposalStageResult:
    """Result of staging one proposal."""

    proposal_id: str
    proposal_root: Path
    status: str
    created: bool


@dataclass(frozen=True)
class ProposalApplyResult:
    """Result of applying one proposal."""

    proposal_id: str
    proposal_root: Path
    output_paths: tuple[Path, ...]
    strict_issue_count: int


@dataclass(frozen=True)
class ProposalApprovalResult:
    """Result of approving one proposal for application."""

    proposal_id: str
    proposal_root: Path
    approver: str
    approved_at: str
    status: str


@dataclass(frozen=True)
class ProposalDecisionResult:
    """Result of recording a review decision for one proposal."""

    proposal_id: str
    proposal_root: Path
    status: str
    reviewer: str
    reviewed_at: str


def proposals_root(project_root: Path) -> Path:
    """Return the project-owned review proposal root."""
    return resolve_project_root(project_root) / ".governed" / "review-proposals"


def list_proposals(project_root: Path) -> tuple[Path, ...]:
    """List proposal directories with metadata."""
    root = proposals_root(project_root)
    if not root.is_dir():
        return ()
    return tuple(sorted(path for path in root.iterdir() if (path / "proposal.toml").is_file()))


def load_proposal(project_root: Path, proposal_id: str) -> tuple[Path, dict[str, Any]]:
    """Load one proposal by id."""
    normalized = normalize_identifier(proposal_id)
    proposal_root = proposals_root(project_root) / normalized
    proposal_path = proposal_root / "proposal.toml"
    if not proposal_path.is_file():
        raise ProposalError(f"proposal not found: {normalized}")
    try:
        data = tomllib.loads(proposal_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ProposalError(f"invalid proposal metadata: {proposal_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ProposalError(f"invalid proposal metadata: {proposal_path}")
    return proposal_root, data


def proposal_summary(proposal_root: Path, data: dict[str, Any]) -> dict[str, object]:
    """Build a stable machine-readable proposal summary."""
    proposal_id = _string(data.get("id")) or proposal_root.name
    output_paths = _string_list(data.get("output_paths"))
    return {
        "id": proposal_id,
        "status": _string(data.get("status")) or "unknown",
        "targetCapability": _string(data.get("target_capability")),
        "proposalType": _string(data.get("proposal_type")),
        "safetyClass": _string(data.get("safety_class")),
        "outputPaths": output_paths,
        "sourceSessionId": _string(data.get("source_session_id")),
        "sourceRunId": _string(data.get("source_run_id")),
        "path": str(proposal_root),
    }


def build_proposals_payload(project_root: Path) -> dict[str, object]:
    """Build the machine-readable proposal list payload."""
    resolved_root = resolve_project_root(project_root).resolve()
    proposals: list[dict[str, object]] = []
    for proposal_root in list_proposals(resolved_root):
        try:
            data = tomllib.loads((proposal_root / "proposal.toml").read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            continue
        proposals.append(proposal_summary(proposal_root, data))
    return {
        "schemaVersion": 1,
        "projectRoot": str(resolved_root),
        "proposals": proposals,
    }


def stage_proposal(
    project_root: Path,
    proposal: dict[str, Any],
    *,
    source_run_id: str,
    source_session_id: str,
    source_thread_name: str | None = None,
) -> ProposalStageResult:
    """Stage one classifier proposal under `.governed/review-proposals`."""
    resolved_root = resolve_project_root(project_root).resolve()
    metadata, body, draft_output = _normalize_stage_metadata(
        resolved_root,
        proposal,
        source_run_id=source_run_id,
        source_session_id=source_session_id,
        source_thread_name=source_thread_name,
    )
    proposal_id = str(metadata["id"])
    proposal_root = proposals_root(resolved_root) / proposal_id
    created = not proposal_root.exists()
    if proposal_root.exists():
        try:
            _, existing = load_proposal(resolved_root, proposal_id)
        except ProposalError:
            existing = {}
        existing_status = _string(existing.get("status"))
        if existing_status in {"approved", "applied"}:
            raise ProposalError(f"refusing to overwrite {existing_status} proposal: {proposal_id}")

    proposal_root.mkdir(parents=True, exist_ok=True)
    _write_metadata(proposal_root / "proposal.toml", metadata)
    (proposal_root / "proposal.md").write_text(body, encoding="utf-8")
    if draft_output:
        (proposal_root / "draft-output.md").write_text(draft_output.rstrip() + "\n", encoding="utf-8")
    return ProposalStageResult(proposal_id=proposal_id, proposal_root=proposal_root, status="staged", created=created)


def apply_proposal(project_root: Path, proposal_id: str) -> ProposalApplyResult:
    """Apply one approved proposal to its governed capability package."""
    resolved_root = resolve_project_root(project_root).resolve()
    proposal_root, data = load_proposal(resolved_root, proposal_id)
    _validate_approval(data)
    metadata = _normalize_loaded_metadata(resolved_root, data)
    draft_path = proposal_root / "draft-output.md"
    if not draft_path.is_file():
        raise ProposalError(f"proposal has no draft output: {draft_path}")
    draft_output = draft_path.read_text(encoding="utf-8")
    if not draft_output.strip():
        raise ProposalError(f"proposal draft output is empty: {draft_path}")
    _validate_safe_text(draft_output, "draft-output.md")
    _validate_script_safety(metadata, draft_output)

    output_paths = tuple((resolved_root / path).resolve() for path in metadata["output_paths"])
    backups: dict[Path, str | None] = {}
    try:
        for output_path in output_paths:
            if output_path.exists():
                existing = output_path.read_text(encoding="utf-8", errors="replace")
                if existing != draft_output:
                    raise ProposalError(f"refusing to overwrite existing file without replace metadata: {output_path}")
                backups[output_path] = existing
                continue
            backups[output_path] = None
            output_path.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write_text(output_path, draft_output.rstrip() + "\n")

        bundle, result = load_project_bundle(resolved_root)
        if result.errors:
            raise ProposalError("; ".join(f"{message.location}: {message.message}" for message in result.errors))
        target_capability = str(metadata["target_capability"])
        strict_result = validate_governed_skill_package(resolved_root, bundle.capabilities[target_capability])
        if strict_result.errors:
            first = strict_result.errors[0]
            raise ProposalError(f"strict validation failed: {first.rule_id}: {first.location}: {first.message}")

        applied = dict(data)
        applied["status"] = "applied"
        applied["updated_at"] = iso_utc_now()
        applied["application"] = {
            "applied_at": applied["updated_at"],
            "applier": "govkb proposals apply",
            "strict_issue_count": len(strict_result.issues),
        }
        _write_metadata(proposal_root / "proposal.toml", applied)
        _update_proposal_body_status(proposal_root, "applied")
        return ProposalApplyResult(
            proposal_id=str(metadata["id"]),
            proposal_root=proposal_root,
            output_paths=output_paths,
            strict_issue_count=len(strict_result.issues),
        )
    except Exception:
        _restore_outputs(backups)
        raise


def approve_proposal(
    project_root: Path,
    proposal_id: str,
    *,
    approver: str,
    approved_at: str | None = None,
    notes: str | None = None,
) -> ProposalApprovalResult:
    """Mark one proposal as approved after validating its staged artifact."""
    resolved_root = resolve_project_root(project_root).resolve()
    proposal_root, data = load_proposal(resolved_root, proposal_id)
    if _string(data.get("status")) == "applied":
        raise ProposalError("cannot approve an already applied proposal")

    approver = approver.strip()
    if not approver:
        raise ProposalError("proposal approval requires approver")

    metadata = _normalize_loaded_metadata(resolved_root, data)
    draft_output = _load_draft_output(proposal_root)
    _validate_safe_text(draft_output, "draft-output.md")
    _validate_script_safety(metadata, draft_output)

    approved = dict(data)
    approved["status"] = "approved"
    approved["updated_at"] = iso_utc_now()
    timestamp = approved_at.strip() if isinstance(approved_at, str) and approved_at.strip() else approved["updated_at"]
    approval = dict(approved.get("approval") if isinstance(approved.get("approval"), dict) else {})
    approval["status"] = "approved"
    approval["approver"] = approver
    approval["approved_at"] = timestamp
    if notes is not None and notes.strip():
        approval["notes"] = notes.strip()
    approved["approval"] = approval
    _write_metadata(proposal_root / "proposal.toml", approved)
    _update_proposal_body_status(proposal_root, "approved")
    return ProposalApprovalResult(
        proposal_id=str(metadata["id"]),
        proposal_root=proposal_root,
        approver=approver,
        approved_at=timestamp,
        status="approved",
    )


def decide_proposal(
    project_root: Path,
    proposal_id: str,
    *,
    status: str,
    reviewer: str,
    reason: str,
    next_action: str | None = None,
    reviewed_at: str | None = None,
) -> ProposalDecisionResult:
    """Record a non-apply review decision for one proposal."""
    resolved_root = resolve_project_root(project_root).resolve()
    proposal_root, data = load_proposal(resolved_root, proposal_id)
    if _string(data.get("status")) == "applied":
        raise ProposalError("cannot decide an already applied proposal")

    status = status.strip()
    if status not in ALLOWED_DECISION_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_DECISION_STATUSES))
        raise ProposalError(f"unsupported proposal decision status: {status}; expected one of: {allowed}")
    reviewer = reviewer.strip()
    if not reviewer:
        raise ProposalError("proposal decision requires reviewer")
    reason = reason.strip()
    if not reason:
        raise ProposalError("proposal decision requires reason")
    if next_action is not None:
        next_action = next_action.strip()

    decided = dict(data)
    decided["status"] = status
    decided["updated_at"] = iso_utc_now()
    timestamp = reviewed_at.strip() if isinstance(reviewed_at, str) and reviewed_at.strip() else decided["updated_at"]
    approval = dict(decided.get("approval") if isinstance(decided.get("approval"), dict) else {})
    if approval:
        approval["status"] = "pending"
        decided["approval"] = approval
    review = dict(decided.get("review") if isinstance(decided.get("review"), dict) else {})
    review["decision"] = status
    review["reviewer"] = reviewer
    review["reviewed_at"] = timestamp
    review["reason"] = reason
    if next_action:
        review["next_action"] = next_action
    decided["review"] = review
    _write_metadata(proposal_root / "proposal.toml", decided)
    _update_proposal_body_status(proposal_root, status)
    return ProposalDecisionResult(
        proposal_id=_string(decided.get("id")) or proposal_root.name,
        proposal_root=proposal_root,
        status=status,
        reviewer=reviewer,
        reviewed_at=timestamp,
    )


def _normalize_stage_metadata(
    project_root: Path,
    proposal: dict[str, Any],
    *,
    source_run_id: str,
    source_session_id: str,
    source_thread_name: str | None,
) -> tuple[dict[str, Any], str, str | None]:
    target_capability = _required_string(proposal, "target_capability")
    proposal_type = _required_string(proposal, "proposal_type")
    proposal_id = normalize_identifier(_string(proposal.get("proposal_id")) or f"{target_capability}-{proposal_type}")
    now = iso_utc_now()
    metadata: dict[str, Any] = {
        "proposal_version": 1,
        "id": proposal_id,
        "status": "staged",
        "created_at": now,
        "updated_at": now,
        "source_run_id": source_run_id,
        "source_session_id": source_session_id,
        "source_thread_name": source_thread_name or "",
        "target_capability": target_capability,
        "proposal_type": proposal_type,
        "safety_class": _required_string(proposal, "safety_class"),
        "confidence": _confidence(proposal.get("confidence")),
        "sensitivity": _required_string(proposal, "sensitivity"),
        "output_paths": _normalize_output_paths(project_root, target_capability, proposal.get("output_paths")),
        "verification_command": _required_string(proposal, "verification_command"),
        "purpose": _required_string(proposal, "purpose"),
        "inputs": _string_list(proposal.get("inputs")),
        "outputs": _string_list(proposal.get("outputs")),
        "cron_apply_reason": _string(proposal.get("cron_apply_reason")) or "cron stages proposals only; maintainer approval is required before apply",
        "approval": {
            "status": "pending",
            "approver": "",
            "approved_at": "",
        },
    }
    _validate_metadata(project_root, metadata)
    body = _proposal_body(metadata, _required_string(proposal, "evidence"))
    draft_output = _string(proposal.get("draft_output"))
    if draft_output:
        _validate_safe_text(draft_output, "draft_output")
        _validate_script_safety(metadata, draft_output)
    return metadata, body, draft_output


def _normalize_loaded_metadata(project_root: Path, data: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(data)
    metadata["target_capability"] = _required_string(metadata, "target_capability")
    metadata["proposal_type"] = _required_string(metadata, "proposal_type")
    metadata["safety_class"] = _required_string(metadata, "safety_class")
    metadata["sensitivity"] = _required_string(metadata, "sensitivity")
    metadata["output_paths"] = _normalize_output_paths(project_root, metadata["target_capability"], metadata.get("output_paths"))
    metadata["verification_command"] = _required_string(metadata, "verification_command")
    metadata["purpose"] = _required_string(metadata, "purpose")
    _validate_metadata(project_root, metadata)
    return metadata


def _validate_metadata(project_root: Path, metadata: dict[str, Any]) -> None:
    bundle, result = load_project_bundle(project_root)
    if result.errors:
        first = result.errors[0]
        raise ProposalError(f"governed project is not valid: {first.location}: {first.message}")
    target_capability = str(metadata["target_capability"])
    if target_capability not in bundle.capabilities:
        raise ProposalError(f"unknown target capability: {target_capability}")
    proposal_type = str(metadata["proposal_type"])
    if proposal_type not in ALLOWED_PROPOSAL_TYPES:
        raise ProposalError(f"unsupported proposal type: {proposal_type}")
    safety_class = str(metadata["safety_class"])
    if safety_class not in ALLOWED_SAFETY_CLASSES:
        raise ProposalError(f"unsupported safety class: {safety_class}")
    sensitivity = str(metadata["sensitivity"])
    if sensitivity != "clean":
        raise ProposalError("proposal includes or may include sensitive content")
    if not metadata["output_paths"]:
        raise ProposalError("proposal must include at least one output path")
    for label in ("purpose", "verification_command"):
        _validate_safe_text(str(metadata.get(label, "")), label)


def _validate_approval(data: dict[str, Any]) -> None:
    approval = data.get("approval")
    approval = approval if isinstance(approval, dict) else {}
    root_status = _string(data.get("status"))
    approval_status = _string(approval.get("status"))
    approver = _string(approval.get("approver")) or _string(approval.get("reviewer"))
    approved_at = _string(approval.get("approved_at"))
    if root_status != "approved" and approval_status != "approved":
        raise ProposalError("proposal must be approved before apply")
    if not approver or not approved_at:
        raise ProposalError("proposal approval requires approver and approved_at")


def _load_draft_output(proposal_root: Path) -> str:
    draft_path = proposal_root / "draft-output.md"
    if not draft_path.is_file():
        raise ProposalError(f"proposal has no draft output: {draft_path}")
    draft_output = draft_path.read_text(encoding="utf-8")
    if not draft_output.strip():
        raise ProposalError(f"proposal draft output is empty: {draft_path}")
    return draft_output


def _normalize_output_paths(project_root: Path, target_capability: str, raw_paths: Any) -> tuple[str, ...]:
    values = _string_list(raw_paths)
    if not values:
        raise ProposalError("proposal must include output_paths")
    capability_root = (project_root / ".governed" / "capabilities" / target_capability).resolve()
    normalized: list[str] = []
    for value in values:
        path = Path(value)
        if path.is_absolute() or value.startswith("~") or ".." in path.parts:
            raise ProposalError(f"unsafe output path: {value}")
        if path.parts[:3] == (".governed", "capabilities", target_capability):
            rel_path = path
        elif path.parts[:2] == (".governed", "capabilities"):
            raise ProposalError(f"output path targets a different capability: {value}")
        else:
            rel_path = Path(".governed") / "capabilities" / target_capability / path
        output_path = (project_root / rel_path).resolve()
        try:
            output_path.relative_to(capability_root)
        except ValueError as exc:
            raise ProposalError(f"output path must stay under target capability: {value}") from exc
        if output_path == capability_root:
            raise ProposalError(f"output path must be a file under the target capability: {value}")
        normalized.append(rel_path.as_posix())
    return tuple(dict.fromkeys(normalized))


def _validate_script_safety(metadata: dict[str, Any], text: str) -> None:
    proposal_type = str(metadata.get("proposal_type", ""))
    if proposal_type not in SCRIPT_TYPES:
        return
    safety_class = str(metadata.get("safety_class", ""))
    if safety_class == "read_only" and any(pattern.search(text) for pattern in MUTATING_PATTERNS):
        raise ProposalError("read-only script proposal contains likely mutating operations")
    if safety_class == "mutating_with_dry_run" and "--dry-run" not in text and "--preview" not in text:
        raise ProposalError("mutating script proposal must document --dry-run or --preview behavior")


def _validate_safe_text(text: str, label: str) -> None:
    for pattern in (*TOKEN_PATTERNS, *CREDENTIAL_PATH_PATTERNS, *RAW_TRANSCRIPT_PATTERNS, *PRIVATE_EVIDENCE_PATTERNS):
        if pattern.search(text):
            raise ProposalError(f"{label} contains unsafe or sensitive content")


def _proposal_body(metadata: dict[str, Any], evidence: str) -> str:
    _validate_safe_text(evidence, "evidence")
    lines = [
        f"# Capability Evolution Proposal: {metadata['id']}",
        "",
        f"- Status: {metadata['status']}",
        f"- Target capability: `{metadata['target_capability']}`",
        f"- Proposal type: `{metadata['proposal_type']}`",
        f"- Safety class: `{metadata['safety_class']}`",
        f"- Source review: `{metadata['source_run_id']}`",
        f"- Source session: `{metadata['source_session_id']}`",
        "",
        "## Purpose",
        "",
        str(metadata["purpose"]),
        "",
        "## Evidence Summary",
        "",
        evidence.strip(),
        "",
        "## Inputs",
        "",
    ]
    inputs = metadata.get("inputs")
    lines.extend(f"- {item}" for item in inputs if isinstance(item, str)) if inputs else lines.append("- None")
    lines.extend(["", "## Outputs", ""])
    outputs = metadata.get("outputs")
    lines.extend(f"- {item}" for item in outputs if isinstance(item, str)) if outputs else lines.append("- None")
    lines.extend(
        [
            "",
            "## Output Paths",
            "",
            *[f"- `{path}`" for path in metadata["output_paths"]],
            "",
            "## Verification",
            "",
            f"- `{metadata['verification_command']}`",
            "",
            "## Cron Safety",
            "",
            str(metadata["cron_apply_reason"]),
            "",
        ]
    )
    return "\n".join(lines)


def _write_metadata(path: Path, data: dict[str, Any]) -> None:
    lines: list[str] = []
    scalar_keys = [
        "proposal_version",
        "id",
        "status",
        "created_at",
        "updated_at",
        "source_run_id",
        "source_session_id",
        "source_thread_name",
        "target_capability",
        "proposal_type",
        "safety_class",
        "confidence",
        "sensitivity",
        "output_paths",
        "verification_command",
        "purpose",
        "inputs",
        "outputs",
        "cron_apply_reason",
    ]
    for key in scalar_keys:
        if key not in data:
            continue
        lines.append(f"{key} = {_toml_value(data[key])}")
    approval = data.get("approval")
    if isinstance(approval, dict):
        lines.extend(["", "[approval]"])
        for key in ("status", "approver", "reviewer", "approved_at", "notes"):
            if key in approval:
                lines.append(f"{key} = {_toml_value(approval[key])}")
    review = data.get("review")
    if isinstance(review, dict):
        lines.extend(["", "[review]"])
        for key in ("decision", "reviewer", "reviewed_at", "reason", "next_action"):
            if key in review:
                lines.append(f"{key} = {_toml_value(review[key])}")
    application = data.get("application")
    if isinstance(application, dict):
        lines.extend(["", "[application]"])
        for key in ("applied_at", "applier", "strict_issue_count"):
            if key in application:
                lines.append(f"{key} = {_toml_value(application[key])}")
    _atomic_write_text(path, "\n".join(lines).rstrip() + "\n")


def _update_proposal_body_status(proposal_root: Path, status: str) -> None:
    body_path = proposal_root / "proposal.md"
    if not body_path.is_file():
        return
    lines = body_path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith("- Status: "):
            lines[index] = f"- Status: {status}"
            _atomic_write_text(body_path, "\n".join(lines).rstrip() + "\n")
            return


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def _restore_outputs(backups: dict[Path, str | None]) -> None:
    for path, content in reversed(tuple(backups.items())):
        if content is None:
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
            continue
        _atomic_write_text(path, content)


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    if value is None:
        return json.dumps("")
    return json.dumps(str(value))


def _required_string(data: dict[str, Any], key: str) -> str:
    value = _string(data.get(key))
    if not value:
        raise ProposalError(f"proposal missing required field: {key}")
    return value


def _string(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _string_list(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())


def _confidence(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    return max(0.0, min(float(value), 1.0))
