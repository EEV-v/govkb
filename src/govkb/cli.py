"""Command-line entrypoint for govkb."""

from __future__ import annotations

import argparse
from pathlib import Path

from govkb.commands.apply import run_codex_apply
from govkb.commands.capabilities import run_capabilities
from govkb.commands.candidates import run_candidates
from govkb.commands.convert import run_convert
from govkb.commands.create_capability import run_create_capability
from govkb.commands.install import run_install
from govkb.commands.init import run_init
from govkb.commands.init_kb import run_init_kb
from govkb.commands.promote import run_promote
from govkb.commands.promotions import run_promotions
from govkb.commands.proposals import run_proposals
from govkb.commands.remediate import run_remediate
from govkb.commands.review_memory import run_review_memory
from govkb.commands.status import run_status
from govkb.commands.validate import run_validate


def build_parser() -> argparse.ArgumentParser:
    """Build the govkb CLI parser."""
    parser = argparse.ArgumentParser(prog="govkb", description="Governed knowledge tooling.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Scaffold a project .governed package.")
    init_parser.add_argument("--dest", type=Path, default=Path.cwd(), help="Project root to scaffold.")
    init_parser.add_argument("--project-id", help="Explicit governed project id.")
    init_parser.add_argument("--project-name", help="Explicit governed project name.")
    init_parser.set_defaults(handler=run_init)

    install_parser = subparsers.add_parser("install", help="Install governed support into a project.")
    install_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to install into.")
    install_parser.add_argument("--project-id", help="Explicit governed project id when scaffolding.")
    install_parser.add_argument("--project-name", help="Explicit governed project name when scaffolding.")
    install_parser.add_argument("--codex-home", type=Path, help="Codex home override for local materialization.")
    install_parser.add_argument("--release", help="Release id to apply.")
    install_parser.add_argument("--revision", help="Git revision override.")
    install_parser.add_argument("--preview", action="store_true", help="Show install actions without changing files.")
    install_parser.add_argument("--cron", action="store_true", help="Install a project-scoped memory-review cron job.")
    install_parser.add_argument("--schedule", default="15 8 * * *", help="Cron schedule used with --cron.")
    install_parser.set_defaults(handler=run_install)

    validate_parser = subparsers.add_parser("validate", help="Validate a project .governed package.")
    validate_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to validate.")
    validate_parser.add_argument("--strict", action="store_true", help="Run strict governed skill package quality checks.")
    validate_parser.add_argument("--json", action="store_true", help="Emit machine-readable validation output.")
    validate_parser.set_defaults(handler=run_validate)

    remediate_parser = subparsers.add_parser("remediate", help="Build governed package remediation reports.")
    remediate_subparsers = remediate_parser.add_subparsers(dest="remediation_action", required=True)

    remediate_project_parser = remediate_subparsers.add_parser(
        "project",
        help="Inspect one governed project and produce a remediation report.",
    )
    remediate_project_parser.add_argument(
        "project_root",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Project root to inspect.",
    )
    remediate_project_parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write a markdown report under .governed/reports/remediation when Git ownership is verified.",
    )
    remediate_project_parser.add_argument(
        "--report-root",
        type=Path,
        help="Override the remediation report directory.",
    )
    remediate_project_parser.add_argument("--json", action="store_true", help="Emit machine-readable remediation output.")
    remediate_project_parser.set_defaults(handler=run_remediate)

    init_kb_parser = subparsers.add_parser("init-kb", help="Bootstrap governed capability knowledge base files.")
    init_kb_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to bootstrap.")
    init_kb_parser.add_argument("--capability", help="Bootstrap one capability id.")
    init_kb_parser.add_argument("--all", action="store_true", help="Bootstrap all governed capabilities.")
    init_kb_parser.add_argument("--codex-home", type=Path, help="Codex home override for local rematerialization after KB bootstrap.")
    init_kb_parser.set_defaults(handler=run_init_kb)

    apply_parser = subparsers.add_parser("apply", help="Materialize governed content into an assistant target.")
    apply_subparsers = apply_parser.add_subparsers(dest="assistant", required=True)

    apply_codex_parser = apply_subparsers.add_parser("codex", help="Preview or apply the Codex adapter.")
    apply_codex_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root to apply from.")
    apply_codex_parser.add_argument("--release", help="Release id to apply.")
    apply_codex_parser.add_argument("--revision", help="Git revision override.")
    apply_codex_parser.add_argument("--codex-home", type=Path, help="Codex home override for local materialization.")
    apply_codex_parser.add_argument("--preview", action="store_true", help="Show what would be applied without materializing files.")
    apply_codex_parser.set_defaults(handler=run_codex_apply)

    status_parser = subparsers.add_parser("status", help="Show governed package and local state summary.")
    status_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to inspect.")
    status_parser.add_argument("--codex-home", type=Path, help="Codex home override for install-state inspection.")
    status_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON for extension integrations.")
    status_parser.set_defaults(handler=run_status)

    capabilities_parser = subparsers.add_parser("capabilities", help="List, rename, or merge governed capabilities.")
    capabilities_subparsers = capabilities_parser.add_subparsers(dest="capability_action", required=True)

    capabilities_list_parser = capabilities_subparsers.add_parser("list", help="List governed capabilities.")
    capabilities_list_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to inspect.")
    capabilities_list_parser.add_argument("--json", action="store_true", help="Emit machine-readable capability details.")
    capabilities_list_parser.set_defaults(handler=run_capabilities)

    capabilities_rename_parser = capabilities_subparsers.add_parser("rename", help="Rename one governed capability.")
    capabilities_rename_parser.add_argument("old_capability_id", help="Existing governed capability id.")
    capabilities_rename_parser.add_argument("new_capability_id", help="New governed capability id.")
    capabilities_rename_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root that owns .governed.")
    capabilities_rename_parser.add_argument("--json", action="store_true", help="Emit machine-readable rename output.")
    capabilities_rename_parser.set_defaults(handler=run_capabilities)

    capabilities_merge_parser = capabilities_subparsers.add_parser("merge", help="Merge one governed capability into another.")
    capabilities_merge_parser.add_argument("source_capability_id", help="Capability id to merge and remove.")
    capabilities_merge_parser.add_argument("target_capability_id", help="Capability id that keeps the merged guidance.")
    capabilities_merge_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root that owns .governed.")
    capabilities_merge_parser.add_argument("--json", action="store_true", help="Emit machine-readable merge output.")
    capabilities_merge_parser.set_defaults(handler=run_capabilities)

    review_parser = subparsers.add_parser("review-memory", help="Run assistant memory review.")
    review_parser.add_argument("--assistant", required=True, choices=("codex",), help="Assistant to review.")
    review_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root to inspect.")
    review_parser.add_argument("--dry-run", action="store_true", help="Generate reports and patches without editing memory.")
    review_parser.add_argument("--inventory-json", action="store_true", help="Emit session inventory JSON without AI classification.")
    review_parser.add_argument("--progress-jsonl", action="store_true", help="Emit structured progress events as JSONL on stdout.")
    review_parser.add_argument("--lookback-days", type=float, help="Override incremental selection window.")
    review_parser.add_argument("--max-sessions", type=int, help="Maximum sessions to classify in one run.")
    review_parser.add_argument("--verbose", action="store_true", help="Write sanitized classifier inputs to the memory-review log dir.")
    review_parser.add_argument("--codex-timeout", type=int, help="Per-session codex exec timeout in seconds.")
    review_parser.add_argument(
        "--classifier-codex-home",
        type=Path,
        help="Codex home used only for nested classifier auth/config; output state still uses CODEX_HOME.",
    )
    review_parser.add_argument("--codex-model", help="Codex model used for nested semantic classification.")
    review_parser.add_argument(
        "--codex-reasoning",
        choices=("low", "medium", "high", "xhigh"),
        help="Codex reasoning effort used for nested semantic classification.",
    )
    review_parser.add_argument("--session-file", type=Path, help="Classify one explicit session JSONL file.")
    review_parser.add_argument(
        "--no-auto-promote",
        dest="auto_promote",
        action="store_false",
        help="Do not run the automated non-mutating promotion check after local memory apply.",
    )
    review_parser.set_defaults(auto_promote=True)
    review_parser.set_defaults(handler=run_review_memory)

    candidates_parser = subparsers.add_parser("candidates", help="Inspect or stage governed capability candidates.")
    candidates_subparsers = candidates_parser.add_subparsers(dest="candidate_action", required=True)

    candidates_stage_parser = candidates_subparsers.add_parser("stage", help="Stage a capability candidate from a session.")
    candidates_stage_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root that owns .governed.")
    candidates_stage_parser.add_argument("--assistant", default="codex", choices=("codex",), help="Assistant that produced the session.")
    candidates_stage_parser.add_argument("--session-file", type=Path, required=True, help="Session JSONL file to inspect.")
    candidates_stage_parser.add_argument(
        "--semantic-seed-file",
        type=Path,
        help="Optional JSON file with semantic candidate metadata and fact overrides.",
    )
    candidates_stage_parser.set_defaults(handler=run_candidates)

    candidates_list_parser = candidates_subparsers.add_parser("list", help="List staged capability candidates.")
    candidates_list_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to inspect.")
    candidates_list_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON for extension integrations.")
    candidates_list_parser.set_defaults(handler=run_candidates)

    candidates_auto_parser = candidates_subparsers.add_parser(
        "auto-create-ready",
        help="Create governed capabilities from ready candidates when project policy allows it.",
    )
    candidates_auto_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root that owns .governed.")
    candidates_auto_parser.add_argument("--assistant", default="codex", choices=("codex",), help="Assistant to materialize after auto-create.")
    candidates_auto_parser.add_argument("--codex-home", type=Path, help="Codex home override for local materialization.")
    candidates_auto_parser.set_defaults(handler=run_candidates)

    proposals_parser = subparsers.add_parser("proposals", help="Inspect, show, or apply capability-evolution proposals.")
    proposals_subparsers = proposals_parser.add_subparsers(dest="proposal_action", required=True)

    proposals_list_parser = proposals_subparsers.add_parser("list", help="List staged capability-evolution proposals.")
    proposals_list_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to inspect.")
    proposals_list_parser.add_argument("--json", action="store_true", help="Emit machine-readable proposal summaries.")
    proposals_list_parser.set_defaults(handler=run_proposals)

    proposals_show_parser = proposals_subparsers.add_parser("show", help="Show one staged capability-evolution proposal.")
    proposals_show_parser.add_argument("proposal_id", help="Proposal id to show.")
    proposals_show_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root that owns .governed.")
    proposals_show_parser.add_argument("--json", action="store_true", help="Emit machine-readable proposal detail.")
    proposals_show_parser.set_defaults(handler=run_proposals)

    proposals_apply_parser = proposals_subparsers.add_parser("apply", help="Apply one approved capability-evolution proposal.")
    proposals_apply_parser.add_argument("proposal_id", help="Proposal id to apply.")
    proposals_apply_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root that owns .governed.")
    proposals_apply_parser.set_defaults(handler=run_proposals)

    proposals_report_parser = proposals_subparsers.add_parser("report", help="Group staged proposals and show advisory quality warnings.")
    proposals_report_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to inspect.")
    proposals_report_parser.add_argument("--json", action="store_true", help="Emit machine-readable proposal report.")
    proposals_report_parser.set_defaults(handler=run_proposals)

    proposals_review_parser = proposals_subparsers.add_parser("review", help="Show the actionable proposal review queue.")
    proposals_review_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to inspect.")
    proposals_review_parser.add_argument(
        "--action",
        choices=("all", "inspect-safety", "manual-review", "merge-first", "reject-duplicate"),
        default="all",
        help="Limit the queue to one recommended action.",
    )
    proposals_review_parser.add_argument("--json", action="store_true", help="Emit machine-readable review steps.")
    proposals_review_parser.set_defaults(handler=run_proposals)

    convert_parser = subparsers.add_parser("convert", help="Convert local assistant artifacts into governed packages.")
    convert_subparsers = convert_parser.add_subparsers(dest="convert_action", required=True)

    convert_skill_parser = convert_subparsers.add_parser("skill", help="Preview or write one local Codex skill conversion.")
    convert_skill_parser.add_argument("skill", help="Codex skill name under --codex-home/skills or an explicit skill directory path.")
    convert_skill_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root that owns .governed.")
    convert_skill_parser.add_argument("--codex-home", type=Path, help="Codex home used to resolve skill names.")
    convert_skill_parser.add_argument("--capability-id", help="Explicit target governed capability id.")
    convert_skill_parser.add_argument("--write", action="store_true", help="Write the converted governed package. Omit for preview.")
    convert_skill_parser.add_argument("--json", action="store_true", help="Emit machine-readable conversion output.")
    convert_skill_parser.set_defaults(handler=run_convert)

    promote_parser = subparsers.add_parser("promote", help="Promote safe local governed assistant memory changes into the repo package.")
    promote_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to promote from.")
    promote_parser.add_argument("--release", help="Release id to promote.")
    promote_parser.add_argument("--assistant", default="codex", choices=("codex",), help="Assistant to promote from.")
    promote_parser.add_argument("--codex-home", type=Path, help="Codex home override for local state inspection.")
    promote_parser.add_argument("--preview", action="store_true", help="Show safe promotions without editing repo files.")
    promote_parser.add_argument("--auto", action="store_true", help="Run automated promotion in an isolated git worktree when possible.")
    promote_parser.set_defaults(handler=run_promote)

    promotions_parser = subparsers.add_parser("promotions", help="Inspect isolated automated promotion worktrees and lifecycle state.")
    promotions_subparsers = promotions_parser.add_subparsers(dest="promotion_action", required=True)

    promotions_list_parser = promotions_subparsers.add_parser("list", help="List isolated promotion review worktrees.")
    promotions_list_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to inspect.")
    promotions_list_parser.add_argument("--codex-home", type=Path, help="Codex home override for promotion worktree inspection.")
    promotions_list_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON for integrations.")
    promotions_list_parser.set_defaults(handler=run_promotions)

    promotions_show_parser = promotions_subparsers.add_parser("show", help="Show one isolated promotion digest and git status.")
    promotions_show_parser.add_argument("promotion", help="Promotion run id, branch name, or worktree path.")
    promotions_show_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root to inspect.")
    promotions_show_parser.add_argument("--codex-home", type=Path, help="Codex home override for promotion worktree inspection.")
    promotions_show_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON for integrations.")
    promotions_show_parser.set_defaults(handler=run_promotions)

    promotions_review_parser = promotions_subparsers.add_parser(
        "mark-reviewed",
        help="Record a GovKB lifecycle decision for one isolated promotion without changing Git history.",
    )
    promotions_review_parser.add_argument("promotion", help="Promotion run id, branch name, or worktree path.")
    promotions_review_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root to inspect.")
    promotions_review_parser.add_argument("--codex-home", type=Path, help="Codex home override for promotion worktree inspection.")
    promotions_review_parser.add_argument("--decision", required=True, choices=("accepted", "rejected"), help="Lifecycle review decision to record.")
    promotions_review_parser.add_argument("--reason", required=True, help="Human-readable review reason.")
    promotions_review_parser.add_argument("--reviewer", help="Reviewer name or id.")
    promotions_review_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON for integrations.")
    promotions_review_parser.set_defaults(handler=run_promotions)

    promotions_apply_parser = promotions_subparsers.add_parser(
        "apply",
        help="Apply an accepted isolated promotion into the active project without committing.",
    )
    promotions_apply_parser.add_argument("promotion", help="Promotion run id, branch name, or worktree path.")
    promotions_apply_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root to apply into.")
    promotions_apply_parser.add_argument("--codex-home", type=Path, help="Codex home override for promotion worktree inspection.")
    promotions_apply_parser.add_argument(
        "--force",
        action="store_true",
        help="Apply despite active .governed changes, an unaccepted lifecycle state, or HEAD mismatch.",
    )
    promotions_apply_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON for integrations.")
    promotions_apply_parser.set_defaults(handler=run_promotions)

    promotions_archive_parser = promotions_subparsers.add_parser(
        "archive",
        help="Archive one promotion in GovKB lifecycle metadata without changing Git history.",
    )
    promotions_archive_parser.add_argument("promotion", help="Promotion run id, branch name, or worktree path.")
    promotions_archive_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root to inspect.")
    promotions_archive_parser.add_argument("--codex-home", type=Path, help="Codex home override for promotion worktree inspection.")
    promotions_archive_parser.add_argument("--reason", help="Human-readable archive reason.")
    promotions_archive_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON for integrations.")
    promotions_archive_parser.set_defaults(handler=run_promotions)

    promotions_cleanup_parser = promotions_subparsers.add_parser(
        "cleanup",
        help="Preview or remove non-actionable isolated promotion review worktrees.",
    )
    promotions_cleanup_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to inspect.")
    promotions_cleanup_parser.add_argument("--codex-home", type=Path, help="Codex home override for promotion worktree inspection.")
    promotions_cleanup_parser.add_argument("--preview", action="store_true", help="Show cleanup-eligible worktrees without changing files.")
    promotions_cleanup_parser.add_argument("--apply", action="store_true", help="Remove eligible worktrees and mark lifecycle metadata cleaned.")
    promotions_cleanup_parser.add_argument("--reason", help="Human-readable cleanup reason recorded in lifecycle metadata.")
    promotions_cleanup_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON for integrations.")
    promotions_cleanup_parser.set_defaults(handler=run_promotions)

    create_parser = subparsers.add_parser("create", help="Scaffold governed objects.")
    create_subparsers = create_parser.add_subparsers(dest="create_target", required=True)

    capability_parser = create_subparsers.add_parser("capability", help="Create a governed capability scaffold.")
    capability_parser.add_argument("capability_id", nargs="?", help="Capability id to scaffold. Optional with --from-candidate.")
    capability_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root that owns .governed.")
    capability_parser.add_argument("--from-candidate", help="Create the capability from a staged candidate id.")
    capability_parser.add_argument("--no-init-kb", action="store_true", help="Skip automatic KB bootstrap when creating from candidate.")
    capability_parser.set_defaults(handler=run_create_capability)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the govkb CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler")
    return int(handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
