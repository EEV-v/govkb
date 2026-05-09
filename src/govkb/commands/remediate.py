"""Remediation report command."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from govkb.core.remediation import RemediationWriteBlocked
from govkb.core.remediation import build_remediation_report
from govkb.core.remediation import write_remediation_report


def run_remediate(args) -> int:
    """Run remediation subcommands."""
    action = getattr(args, "remediation_action", "")
    if action == "project":
        return _run_project(args)
    print(f"error: unsupported remediate action: {action}", file=sys.stderr)
    return 1


def _run_project(args) -> int:
    project_root = Path(args.project_root).expanduser().resolve()
    report = build_remediation_report(project_root)
    if getattr(args, "write_report", False):
        try:
            report = write_remediation_report(report, getattr(args, "report_root", None))
        except RemediationWriteBlocked as exc:
            if getattr(args, "json", False):
                payload = report.as_dict()
                payload["writeError"] = str(exc)
                print(json.dumps(payload, indent=2, sort_keys=True))
            print(f"error: could not write remediation report: {exc}", file=sys.stderr)
            return 1

    if getattr(args, "json", False):
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
        return 0

    print(f"Project root: {report.project_root}")
    print(f"Governed root: {report.governed_root}")
    print(f"Remediation status: {report.status}")
    print(f"Strict issues: {len(report.strict_issues)}")
    print(f"Recommendations: {len(report.recommendations)}")
    print(
        "Auto-create: "
        f"{'enabled' if report.automation_policy.auto_create_capabilities else 'disabled'} "
        f"(min occurrences={report.automation_policy.auto_create_min_occurrences}, strict activation required)"
    )
    if report.git_ownership.can_write_durable_report:
        print(f"Git ownership: ok ({report.git_ownership.git_root})")
    else:
        print(f"Git ownership: blocked ({report.git_ownership.blocker})")
    for recommendation in report.recommendations:
        rule_ids = ", ".join(recommendation.rule_ids)
        capability = recommendation.capability_id or "<project>"
        print(f"- {capability}: {recommendation.option} [{rule_ids}]")
    if report.report_path:
        print(f"Report: {report.report_path}")
    else:
        print("No files written. Use --write-report to create a durable remediation report.")
    return 0
