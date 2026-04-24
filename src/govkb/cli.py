"""Command-line entrypoint for govkb."""

from __future__ import annotations

import argparse
from pathlib import Path

from govkb.commands.apply import run_codex_apply
from govkb.commands.candidates import run_candidates
from govkb.commands.create_capability import run_create_capability
from govkb.commands.install import run_install
from govkb.commands.init import run_init
from govkb.commands.init_kb import run_init_kb
from govkb.commands.promote import run_promote
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
    validate_parser.set_defaults(handler=run_validate)

    init_kb_parser = subparsers.add_parser("init-kb", help="Bootstrap governed capability knowledge base files.")
    init_kb_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to bootstrap.")
    init_kb_parser.add_argument("--capability", help="Bootstrap one capability id.")
    init_kb_parser.add_argument("--all", action="store_true", help="Bootstrap all governed capabilities.")
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
    status_parser.set_defaults(handler=run_status)

    review_parser = subparsers.add_parser("review-memory", help="Run assistant memory review.")
    review_parser.add_argument("--assistant", required=True, choices=("codex",), help="Assistant to review.")
    review_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root to inspect.")
    review_parser.add_argument("--dry-run", action="store_true", help="Generate reports and patches without editing memory.")
    review_parser.add_argument("--lookback-days", type=float, help="Override incremental selection window.")
    review_parser.add_argument("--max-sessions", type=int, help="Maximum sessions to classify in one run.")
    review_parser.add_argument("--verbose", action="store_true", help="Write sanitized classifier inputs to the memory-review log dir.")
    review_parser.add_argument("--codex-timeout", type=int, help="Per-session codex exec timeout in seconds.")
    review_parser.add_argument("--session-file", type=Path, help="Classify one explicit session JSONL file.")
    review_parser.add_argument(
        "--no-auto-promote",
        dest="auto_promote",
        action="store_false",
        help="Do not promote safe governed memory changes back into the repo after apply.",
    )
    review_parser.set_defaults(auto_promote=True)
    review_parser.set_defaults(handler=run_review_memory)

    candidates_parser = subparsers.add_parser("candidates", help="Inspect or stage governed capability candidates.")
    candidates_subparsers = candidates_parser.add_subparsers(dest="candidate_action", required=True)

    candidates_stage_parser = candidates_subparsers.add_parser("stage", help="Stage a capability candidate from a session.")
    candidates_stage_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root that owns .governed.")
    candidates_stage_parser.add_argument("--assistant", default="codex", choices=("codex",), help="Assistant that produced the session.")
    candidates_stage_parser.add_argument("--session-file", type=Path, required=True, help="Session JSONL file to inspect.")
    candidates_stage_parser.set_defaults(handler=run_candidates)

    candidates_list_parser = candidates_subparsers.add_parser("list", help="List staged capability candidates.")
    candidates_list_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to inspect.")
    candidates_list_parser.set_defaults(handler=run_candidates)

    candidates_auto_parser = candidates_subparsers.add_parser(
        "auto-create-ready",
        help="Create governed capabilities from ready candidates when project policy allows it.",
    )
    candidates_auto_parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root that owns .governed.")
    candidates_auto_parser.add_argument("--assistant", default="codex", choices=("codex",), help="Assistant to materialize after auto-create.")
    candidates_auto_parser.add_argument("--codex-home", type=Path, help="Codex home override for local materialization.")
    candidates_auto_parser.set_defaults(handler=run_candidates)

    promote_parser = subparsers.add_parser("promote", help="Promote safe local governed assistant memory changes into the repo package.")
    promote_parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd(), help="Project root to promote from.")
    promote_parser.add_argument("--release", help="Release id to promote.")
    promote_parser.add_argument("--assistant", default="codex", choices=("codex",), help="Assistant to promote from.")
    promote_parser.add_argument("--codex-home", type=Path, help="Codex home override for local state inspection.")
    promote_parser.add_argument("--preview", action="store_true", help="Show safe promotions without editing repo files.")
    promote_parser.add_argument("--auto", action="store_true", help="Mark this promotion as an automated scheduler promotion.")
    promote_parser.set_defaults(handler=run_promote)

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
