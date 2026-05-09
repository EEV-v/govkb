"""Governed package remediation report helpers."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from datetime import datetime
from datetime import timezone
from pathlib import Path
import subprocess

from govkb.core.automation import AutomationPolicy
from govkb.core.automation import automation_policy_from_manifest
from govkb.core.contracts import ProjectBundle
from govkb.core.contracts import ValidationMessage
from govkb.core.contracts import load_project_bundle
from govkb.core.governed_skill import StrictIssue
from govkb.core.governed_skill import validate_governed_skill_bundle
from govkb.core.project import governed_root as build_governed_root
from govkb.core.project import resolve_project_root


SCHEMA_VERSION = 1
STRICT_ACTIVATION_REQUIRED = True

RULE_OPTION_MAP = {
    "GSK-ID-002": "demote-or-deprecate",
    "GSK-PATH-001": "repair-paths-after-approval",
    "GSK-MEMORY-001": "repair-memory-after-approval",
    "GSK-SAFETY-001": "remove-unsafe-content",
    "GSK-LIFECYCLE-001": "approval-required",
}

OPTION_RATIONALE = {
    "demote-or-deprecate": (
        "Weak or generic active capability scope should be reviewed; if it is wrong-domain, "
        "demote it to a candidate or mark it deprecated before repair in place."
    ),
    "repair-paths-after-approval": (
        "Invalid repository or package path references should be corrected or removed only after maintainer approval."
    ),
    "repair-memory-after-approval": (
        "Memory or instructions need evidence-grounded repair before the capability is treated as strict-valid."
    ),
    "remove-unsafe-content": (
        "Unsafe local credential or token-like content must be removed before the capability can be trusted."
    ),
    "approval-required": (
        "Activation requires explicit lifecycle approval metadata from a reviewer."
    ),
    "review-required": (
        "Strict validation found an issue that requires maintainer review before package mutation."
    ),
    "review-warning": (
        "Strict validation found a warning that should be reviewed before broad rollout."
    ),
}


@dataclass(frozen=True)
class GitOwnership:
    """Git ownership state for a governed project."""

    is_git_repository: bool
    git_root: Path | None
    governed_owned_by_git_root: bool
    dirty: bool
    status_short: str
    blocker: str | None

    @property
    def can_write_durable_report(self) -> bool:
        """Return whether a durable `.governed` report write is allowed."""
        return self.is_git_repository and self.governed_owned_by_git_root

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable ownership payload."""
        return {
            "isGitRepository": self.is_git_repository,
            "gitRoot": str(self.git_root) if self.git_root else None,
            "governedOwnedByGitRoot": self.governed_owned_by_git_root,
            "dirty": self.dirty,
            "statusShort": self.status_short,
            "blocker": self.blocker,
            "canWriteDurableReport": self.can_write_durable_report,
        }


@dataclass(frozen=True)
class RemediationIssue:
    """Strict issue enriched with the owning capability id when known."""

    severity: str
    rule_id: str
    location: str
    message: str
    capability_id: str | None

    def as_dict(self) -> dict[str, str | None]:
        """Return a JSON-serializable issue payload."""
        return {
            "severity": self.severity,
            "ruleId": self.rule_id,
            "location": self.location,
            "message": self.message,
            "capabilityId": self.capability_id,
        }


@dataclass(frozen=True)
class RemediationRecommendation:
    """Maintainer-reviewable remediation recommendation."""

    capability_id: str | None
    option: str
    severity: str
    rationale: str
    rule_ids: tuple[str, ...]
    locations: tuple[str, ...]
    approval_required: bool = True

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable recommendation payload."""
        return {
            "capabilityId": self.capability_id,
            "option": self.option,
            "severity": self.severity,
            "rationale": self.rationale,
            "ruleIds": list(self.rule_ids),
            "locations": list(self.locations),
            "approvalRequired": self.approval_required,
        }


@dataclass(frozen=True)
class RemediationReport:
    """Read-only remediation report for one governed project."""

    project_root: Path
    governed_root: Path
    project_id: str | None
    status: str
    load_errors: tuple[ValidationMessage, ...]
    load_warnings: tuple[ValidationMessage, ...]
    strict_issues: tuple[RemediationIssue, ...]
    automation_policy: AutomationPolicy
    git_ownership: GitOwnership
    recommendations: tuple[RemediationRecommendation, ...]
    report_path: Path | None = None

    @property
    def write_eligible(self) -> bool:
        """Return whether the default durable report path may be written."""
        return self.git_ownership.can_write_durable_report

    def with_report_path(self, report_path: Path) -> "RemediationReport":
        """Return a copy with the written report path attached."""
        return replace(self, report_path=report_path)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable report payload."""
        return {
            "schemaVersion": SCHEMA_VERSION,
            "projectRoot": str(self.project_root),
            "governedRoot": str(self.governed_root),
            "projectId": self.project_id,
            "status": self.status,
            "loadErrors": [_validation_message_dict(message) for message in self.load_errors],
            "loadWarnings": [_validation_message_dict(message) for message in self.load_warnings],
            "strictIssues": [issue.as_dict() for issue in self.strict_issues],
            "automation": {
                "autoCreateCapabilities": self.automation_policy.auto_create_capabilities,
                "autoCreateMinOccurrences": self.automation_policy.auto_create_min_occurrences,
                "strictActivationRequired": STRICT_ACTIVATION_REQUIRED,
                "recommendation": _automation_recommendation(self.automation_policy),
            },
            "gitOwnership": self.git_ownership.as_dict(),
            "recommendations": [recommendation.as_dict() for recommendation in self.recommendations],
            "writeEligible": self.write_eligible,
            "reportPath": str(self.report_path) if self.report_path else None,
        }


class RemediationWriteBlocked(RuntimeError):
    """Raised when a durable remediation report write is not allowed."""


def build_remediation_report(project_root: Path) -> RemediationReport:
    """Build a read-only remediation report for one governed project."""
    resolved_root = resolve_project_root(Path(project_root).expanduser().resolve())
    bundle, validation = load_project_bundle(resolved_root)
    strict_result = validate_governed_skill_bundle(
        resolved_root,
        bundle,
        activation_required=STRICT_ACTIVATION_REQUIRED,
    )
    strict_issues = tuple(_remediation_issue(issue, bundle) for issue in strict_result.issues)
    recommendations = build_recommendations(strict_issues)
    status = _report_status(validation.errors, strict_issues)
    return RemediationReport(
        project_root=bundle.project_root,
        governed_root=bundle.governed_root,
        project_id=bundle.project_id,
        status=status,
        load_errors=tuple(validation.errors),
        load_warnings=tuple(validation.warnings),
        strict_issues=strict_issues,
        automation_policy=automation_policy_from_manifest(bundle.project_manifest),
        git_ownership=inspect_git_ownership(bundle.project_root),
        recommendations=recommendations,
    )


def build_recommendations(issues: tuple[RemediationIssue, ...]) -> tuple[RemediationRecommendation, ...]:
    """Build stable recommendations from strict validation issues."""
    grouped: dict[tuple[str | None, str], list[RemediationIssue]] = {}
    for issue in issues:
        option = remediation_option_for_rule(issue.rule_id, issue.severity)
        grouped.setdefault((issue.capability_id, option), []).append(issue)

    recommendations: list[RemediationRecommendation] = []
    for (capability_id, option), group in sorted(
        grouped.items(),
        key=lambda item: (
            item[0][0] or "",
            _option_sort_key(item[0][1]),
            item[0][1],
        ),
    ):
        severity = _highest_severity(tuple(issue.severity for issue in group))
        recommendations.append(
            RemediationRecommendation(
                capability_id=capability_id,
                option=option,
                severity=severity,
                rationale=OPTION_RATIONALE[option],
                rule_ids=tuple(sorted({issue.rule_id for issue in group})),
                locations=tuple(issue.location for issue in group),
                approval_required=option != "review-warning",
            )
        )
    return tuple(recommendations)


def remediation_option_for_rule(rule_id: str, severity: str = "error") -> str:
    """Return the remediation option for one strict issue rule."""
    if rule_id in RULE_OPTION_MAP:
        return RULE_OPTION_MAP[rule_id]
    if severity == "warning":
        return "review-warning"
    return "review-required"


def inspect_git_ownership(project_root: Path) -> GitOwnership:
    """Inspect whether `.governed` is owned by the project's Git root."""
    resolved_root = Path(project_root).expanduser().resolve()
    rev_parse = _run_git(resolved_root, "rev-parse", "--show-toplevel")
    if rev_parse is None:
        return GitOwnership(
            is_git_repository=False,
            git_root=None,
            governed_owned_by_git_root=False,
            dirty=False,
            status_short="",
            blocker="git executable is not available",
        )
    if rev_parse.returncode != 0:
        return GitOwnership(
            is_git_repository=False,
            git_root=None,
            governed_owned_by_git_root=False,
            dirty=False,
            status_short="",
            blocker="project root is not inside a Git repository",
        )

    git_root = Path(rev_parse.stdout.strip()).resolve()
    governed_root = build_governed_root(resolved_root).resolve()
    governed_owned = _path_is_relative_to(governed_root, git_root)
    status = _run_git(resolved_root, "status", "--short")
    status_short = status.stdout if status and status.returncode == 0 else ""
    blocker = None if governed_owned else "governed root is not owned by the detected Git repository"
    return GitOwnership(
        is_git_repository=True,
        git_root=git_root,
        governed_owned_by_git_root=governed_owned,
        dirty=bool(status_short.strip()),
        status_short=status_short,
        blocker=blocker,
    )


def render_remediation_markdown(report: RemediationReport) -> str:
    """Render a remediation report as markdown."""
    lines = [
        "# Governed Package Remediation Report",
        "",
        f"Generated: {_timestamp()}",
        f"Project root: `{report.project_root}`",
        f"Governed root: `{report.governed_root}`",
        f"Project id: `{report.project_id or '<unknown>'}`",
        f"Status: `{report.status}`",
        "",
        "## Write Policy",
        "",
        "- This report does not change `.governed/capabilities/` files.",
        "- Capability repair, demotion, deprecation, rename, or replacement requires maintainer approval.",
        "- Durable report writes require the Git repository that owns `.governed`.",
        "",
        "## Automation Policy",
        "",
        f"- auto_create_capabilities: `{str(report.automation_policy.auto_create_capabilities).lower()}`",
        f"- auto_create_min_occurrences: `{report.automation_policy.auto_create_min_occurrences}`",
        f"- strict_activation_required: `{str(STRICT_ACTIVATION_REQUIRED).lower()}`",
        f"- recommendation: { _automation_recommendation(report.automation_policy) }",
        "",
        "## Git Ownership",
        "",
        f"- is_git_repository: `{str(report.git_ownership.is_git_repository).lower()}`",
        f"- git_root: `{report.git_ownership.git_root or '<none>'}`",
        f"- governed_owned_by_git_root: `{str(report.git_ownership.governed_owned_by_git_root).lower()}`",
        f"- dirty: `{str(report.git_ownership.dirty).lower()}`",
        f"- blocker: {report.git_ownership.blocker or 'none'}",
        "",
        "## Load Messages",
        "",
    ]
    if report.load_errors or report.load_warnings:
        lines.append("| Type | Location | Message |")
        lines.append("|---|---|---|")
        for message in report.load_errors:
            lines.append(f"| error | `{message.location}` | {message.message} |")
        for message in report.load_warnings:
            lines.append(f"| warning | `{message.location}` | {message.message} |")
    else:
        lines.append("No base package load errors or warnings.")

    lines.extend(["", "## Strict Issues", ""])
    if report.strict_issues:
        lines.append("| Severity | Rule | Capability | Location | Message |")
        lines.append("|---|---|---|---|---|")
        for issue in report.strict_issues:
            lines.append(
                f"| {issue.severity} | `{issue.rule_id}` | `{issue.capability_id or '<project>'}` "
                f"| `{issue.location}` | {issue.message} |"
            )
    else:
        lines.append("No strict governed skill issues found.")

    lines.extend(["", "## Recommendations", ""])
    if report.recommendations:
        lines.append("| Capability | Option | Severity | Rule IDs | Approval Required | Rationale |")
        lines.append("|---|---|---|---|---|---|")
        for recommendation in report.recommendations:
            rule_ids = ", ".join(f"`{rule_id}`" for rule_id in recommendation.rule_ids)
            lines.append(
                f"| `{recommendation.capability_id or '<project>'}` | `{recommendation.option}` | "
                f"{recommendation.severity} | {rule_ids} | "
                f"`{str(recommendation.approval_required).lower()}` | {recommendation.rationale} |"
            )
    else:
        lines.append("No remediation recommendations. Preserve existing durable memory.")

    lines.extend(
        [
            "",
            "## Next Steps",
            "",
            "1. Review this report with the maintainer.",
            "2. For weak or wrong-domain capabilities, choose demotion, deprecation, rename, replacement, or repair.",
            "3. Re-run strict validation after approved package changes.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_remediation_report(report: RemediationReport, report_root: Path | None = None) -> RemediationReport:
    """Write a durable markdown remediation report when Git ownership allows it."""
    if not report.governed_root.is_dir():
        raise RemediationWriteBlocked("governed root does not exist; choose a project root with .governed")
    if not report.git_ownership.can_write_durable_report:
        blocker = report.git_ownership.blocker or "durable report writes require Git ownership of .governed"
        raise RemediationWriteBlocked(blocker)

    target_root = (report_root or report.governed_root / "reports" / "remediation").expanduser().resolve()
    git_root = report.git_ownership.git_root
    if git_root is None or not _path_is_relative_to(target_root, git_root):
        raise RemediationWriteBlocked("report root is not inside the owning Git repository")

    target_root.mkdir(parents=True, exist_ok=True)
    report_path = target_root / f"{_filename_timestamp()}-remediation-report.md"
    markdown = render_remediation_markdown(report.with_report_path(report_path))
    report_path.write_text(markdown, encoding="utf-8")
    latest_path = target_root / "latest-remediation-report.md"
    latest_path.write_text(markdown, encoding="utf-8")
    return report.with_report_path(report_path)


def _remediation_issue(issue: StrictIssue, bundle: ProjectBundle) -> RemediationIssue:
    return RemediationIssue(
        severity=issue.severity,
        rule_id=issue.rule_id,
        location=issue.location,
        message=issue.message,
        capability_id=_capability_id_for_location(issue.location, bundle),
    )


def _capability_id_for_location(location: str, bundle: ProjectBundle) -> str | None:
    location_path = _path_from_location(location)
    for capability_id, contract in sorted(bundle.capabilities.items()):
        capability_root = contract.capability_root.resolve()
        if location_path is not None and _path_is_relative_to(location_path, capability_root):
            return capability_id
        if str(location).startswith(str(capability_root)):
            return capability_id
    return None


def _path_from_location(location: str) -> Path | None:
    raw_path = location
    if ":" in raw_path:
        raw_path = raw_path.split(":", 1)[0]
    try:
        return Path(raw_path).expanduser().resolve()
    except OSError:
        return None


def _report_status(load_errors: list[ValidationMessage], strict_issues: tuple[RemediationIssue, ...]) -> str:
    if load_errors:
        return "invalid-governed-package"
    if any(issue.severity == "error" for issue in strict_issues):
        return "action-required"
    if strict_issues:
        return "review-required"
    return "clean"


def _validation_message_dict(message: ValidationMessage) -> dict[str, str]:
    return {"location": message.location, "message": message.message}


def _automation_recommendation(policy: AutomationPolicy) -> str:
    if not policy.auto_create_capabilities:
        return "Auto-create is disabled in .governed/project.toml."
    return (
        "Auto-create is enabled but constrained by candidate review approval and strict activation; "
        "disable it during manual remediation if a freeze window is required."
    )


def _highest_severity(severities: tuple[str, ...]) -> str:
    order = {"error": 0, "warning": 1, "info": 2}
    return min(severities, key=lambda severity: order.get(severity, 99)) if severities else "info"


def _option_sort_key(option: str) -> int:
    order = {
        "remove-unsafe-content": 0,
        "demote-or-deprecate": 1,
        "repair-paths-after-approval": 2,
        "repair-memory-after-approval": 3,
        "approval-required": 4,
        "review-required": 5,
        "review-warning": 6,
    }
    return order.get(option, 99)


def _run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            ["git", "-C", str(project_root), *args],
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError:
        return None


def _path_is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _filename_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
