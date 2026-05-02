"""Conversion commands."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from govkb.core.skill_conversion import build_conversion_plan
from govkb.core.skill_conversion import write_conversion_package


def run_convert(args) -> int:
    """Run conversion subcommands."""
    action = getattr(args, "convert_action", "")
    if action == "skill":
        return _run_convert_skill(args)
    print(f"error: unsupported convert action: {action}", file=sys.stderr)
    return 1


def _run_convert_skill(args) -> int:
    project_root = Path(args.project_root).resolve()
    codex_home = Path(args.codex_home).expanduser().resolve() if getattr(args, "codex_home", None) else None
    try:
        plan = build_conversion_plan(
            str(args.skill),
            project_root=project_root,
            codex_home=codex_home,
            capability_id=getattr(args, "capability_id", None),
        )
    except Exception as exc:
        print(f"error: could not build conversion plan: {exc}", file=sys.stderr)
        return 1

    if getattr(args, "write", False):
        try:
            result = write_conversion_package(plan)
        except Exception as exc:
            print(f"error: could not write converted package: {exc}", file=sys.stderr)
            return 1
        if getattr(args, "json", False):
            print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
        else:
            _print_plan(plan)
            if result.strict_issues:
                for issue in result.strict_issues:
                    print(f"strict {issue.severity}: {issue.rule_id}: {issue.location}: {issue.message}", file=sys.stderr)
                print("Conversion write failed strict validation; created package was removed.", file=sys.stderr)
                return 1
            print(f"Created governed capability package: {result.created_package}")
            print(f"Rollback: remove {result.created_package} or revert the repository change.")
        return 0 if not result.strict_issues else 1

    if getattr(args, "json", False):
        print(json.dumps(plan.as_dict(), indent=2, sort_keys=True))
    else:
        _print_plan(plan)
        print("Preview mode: no files were written.")
        print("Next safe action: rerun with --write after reviewing the plan.")
    return 0


def _print_plan(plan) -> None:
    print(f"Source skill: {plan.source_name}")
    print(f"Source path: {plan.source_path}")
    print(f"Target capability id: {plan.capability_id}")
    print(f"Target package: {plan.package_path}")
    print(f"Parity level: {plan.parity_level}")
    print(f"Strict validation: {plan.strict_status}")
    if plan.strict_issues:
        print("Strict issues:")
        for issue in plan.strict_issues:
            print(f"- {issue.severity}: {issue.rule_id}: {issue.location}: {issue.message}")
    print("Planned files:")
    for item in plan.planned_items:
        if item.destination:
            print(f"- {item.destination}: {item.action} from {item.source}")
    print("Rejected content:")
    if plan.rejected_items:
        for item in plan.rejected_items:
            print(f"- {item.source}: {item.reason}")
    else:
        print("- none")
    print("Manual review:")
    if plan.manual_review_items:
        for item in plan.manual_review_items:
            print(f"- {item.source}: {item.reason}")
    else:
        print("- none")
