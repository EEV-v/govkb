"""Use-case tests for memory-review capability-evolution behavior."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import importlib.machinery
import importlib.util
import io
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest

import govkb

try:
    from memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper
except ModuleNotFoundError:  # pragma: no cover - supports module-style unittest invocation.
    from tests.memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper


def load_scheduler():
    script_path = Path(next(iter(govkb.__path__))).resolve() / "adapters" / "codex" / "bin" / "codex-memory-review"
    loader = importlib.machinery.SourceFileLoader("govkb_mrce_scheduler_use_cases", str(script_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise AssertionError(f"Could not load scheduler spec from {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


class MemoryReviewCapabilityEvolutionUseCaseTests(unittest.TestCase):
    """Traceable BDD scenario coverage."""

    def test_uc_1_no_proposal_opportunities_preserve_report_behavior(self) -> None:
        """UC-1: No proposal opportunities preserve existing memory-review behavior."""
        scheduler = load_scheduler()
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_root = Path(temp_dir) / "reports"
            original_report_dir = scheduler.REPORT_DIR
            original_log = scheduler.log
            try:
                scheduler.REPORT_DIR = reports_root
                scheduler.log = lambda _message: None
                report_path = scheduler.write_report(
                    "2026-05-28T000000Z",
                    scheduler.DiscoveryStats(
                        indexed_rows=0,
                        indexed_missing_files=0,
                        file_only_recent_unprocessed=0,
                        selected_indexed=0,
                        selected_file_only=0,
                        total_discovered=0,
                        already_processed=0,
                        selected_before_limit=0,
                    ),
                    [],
                    skipped=[],
                    deferred=[],
                    applied=[],
                    staged=[],
                    candidate_stage_requests=[],
                    candidate_auto_create_results=[],
                    rejected=[],
                    failed=[],
                    dry_run=True,
                    proposal_stage_requests=[],
                    proposal_rejections=[],
                )
            finally:
                scheduler.REPORT_DIR = original_report_dir
                scheduler.log = original_log

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("## Capability Evolution Proposals", report)
            self.assertIn("## Rejected Capability Evolution Proposals", report)
            self.assertIn("- Capability evolution proposals: 0", report)

    def test_uc_5_dry_run_reports_proposals_without_staging_files(self) -> None:
        """UC-5: Scheduled cron and dry-run review remain stage-only for executable artifacts."""
        scheduler = load_scheduler()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, root)
            project_root = helper.seed_project()
            capability_root = helper.seed_capability()
            session_path = root / "session.jsonl"
            session_path.write_text(
                "\n".join(
                    [
                        json.dumps({"type": "session_meta", "payload": {"id": "session-1", "cwd": str(project_root)}}),
                        json.dumps({"type": "event_msg", "payload": {"type": "user_message", "message": "make reusable helper"}}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            target = scheduler.MemoryTarget(
                skill="govkb-demo-project-release-validation-workflow",
                capability_id="release-validation-workflow",
                project_id="demo-project",
                path=capability_root / "references" / "long-term-memory.md",
                requires_explicit_acceptance=False,
                headings=("Working Agreement", "Stable Workflows", "Commands And Verification", "Code And Docs Map"),
                content=(capability_root / "references" / "long-term-memory.md").read_text(encoding="utf-8"),
                aliases=("release-validation-workflow",),
                hints=("release validation",),
                negative_hints=(),
                project_root=project_root,
            )
            session = scheduler.SessionRef(
                id="session-1",
                thread_name="session.jsonl",
                updated_at="2026-05-28T00:00:00Z",
                path=session_path,
                indexed=True,
            )
            state_dir = root / "state"
            reports_root = state_dir / "reports"
            logs_root = state_dir / "logs"
            original_state_dir = scheduler.STATE_DIR
            original_report_dir = scheduler.REPORT_DIR
            original_log_dir = scheduler.LOG_DIR
            original_state_file = scheduler.STATE_FILE
            try:
                scheduler.STATE_DIR = state_dir
                scheduler.REPORT_DIR = reports_root
                scheduler.LOG_DIR = logs_root
                scheduler.STATE_FILE = state_dir / "state.json"
                stdout = io.StringIO()
                stderr = io.StringIO()
                with patch.object(
                    scheduler,
                    "load_sessions",
                    return_value=(
                        [session],
                        scheduler.DiscoveryStats(
                            indexed_rows=1,
                            indexed_missing_files=0,
                            file_only_recent_unprocessed=0,
                            selected_indexed=1,
                            selected_file_only=0,
                            total_discovered=1,
                            already_processed=0,
                            selected_before_limit=1,
                        ),
                    ),
                ), patch.object(
                    scheduler,
                    "discover_memory_targets",
                    return_value={target.skill: target},
                ), patch.object(
                    scheduler,
                    "targets_for_session",
                    return_value={target.skill: target},
                ), patch.object(
                    scheduler,
                    "prescreen_session",
                    return_value=(True, "synthetic proposal session"),
                ), patch.object(
                    scheduler,
                    "should_stage_capability_candidate",
                    return_value=False,
                ), patch.object(
                    scheduler,
                    "classify_session",
                    return_value={
                        "session_id": "session-1",
                        "candidates": [],
                        "semantic_candidate": None,
                        "capability_evolution_proposals": [helper.proposal_payload()],
                    },
                ), redirect_stdout(stdout), redirect_stderr(stderr):
                    exit_code = scheduler.process(
                        argparse.Namespace(
                            dry_run=True,
                            inventory_json=False,
                            progress_jsonl=True,
                            lookback_days=90,
                            max_sessions=5,
                            verbose=False,
                            codex_timeout=30,
                            codex_model=None,
                            codex_reasoning=None,
                            classifier_codex_home=None,
                            session_file=None,
                            resolved_project_root=project_root,
                            auto_promote=False,
                        )
                    )
            finally:
                scheduler.STATE_DIR = original_state_dir
                scheduler.REPORT_DIR = original_report_dir
                scheduler.LOG_DIR = original_log_dir
                scheduler.STATE_FILE = original_state_file

            self.assertEqual(exit_code, 0)
            self.assertFalse((project_root / ".governed" / "review-proposals").exists())
            events = [json.loads(line) for line in stdout.getvalue().splitlines()]
            classified = next(event for event in events if event["event"] == "session_classified")
            self.assertEqual(classified["proposalCount"], 1)
            report_path = next(reports_root.glob("*-report.md"))
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("## Capability Evolution Proposals", report)
            self.assertIn("release-validation-script", report)

    def test_uc_5_invalid_proposal_staging_does_not_block_session_state(self) -> None:
        """UC-5: Invalid generated proposals are rejected without repeating learned session tails."""
        scheduler = load_scheduler()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, root)
            project_root = helper.seed_project()
            capability_root = helper.seed_capability()
            session_path = root / "session.jsonl"
            session_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": "2026-05-28T00:00:00Z",
                                "type": "session_meta",
                                "payload": {"id": "session-1", "cwd": str(project_root)},
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": "2026-05-28T00:10:00Z",
                                "type": "event_msg",
                                "payload": {"type": "user_message", "message": "make reusable helper"},
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            memory_path = capability_root / "references" / "long-term-memory.md"
            target = scheduler.MemoryTarget(
                skill="govkb-demo-project-release-validation-workflow",
                capability_id="release-validation-workflow",
                project_id="demo-project",
                path=memory_path,
                requires_explicit_acceptance=False,
                headings=("Working Agreement", "Stable Workflows", "Commands And Verification", "Code And Docs Map"),
                content=memory_path.read_text(encoding="utf-8"),
                aliases=("release-validation-workflow",),
                hints=("release validation",),
                negative_hints=(),
                project_root=project_root,
            )
            session = scheduler.SessionRef(
                id="session-1",
                thread_name="session.jsonl",
                updated_at="2026-05-28T00:10:00Z",
                path=session_path,
                indexed=True,
                review_after="2026-05-28T00:00:00Z",
            )
            proposal = helper.proposal_payload(proposal_id="unsafe-helper")
            proposal_failure = scheduler.proposal_stage_failure(
                {
                    "session_id": "session-1",
                    "target_capability": "release-validation-workflow",
                    "proposal_type": "script",
                    "proposal_id": "unsafe-helper",
                },
                "mutating script proposal must document --dry-run or --preview behavior",
            )
            state_dir = root / "state"
            reports_root = state_dir / "reports"
            logs_root = state_dir / "logs"
            original_state_dir = scheduler.STATE_DIR
            original_report_dir = scheduler.REPORT_DIR
            original_log_dir = scheduler.LOG_DIR
            original_state_file = scheduler.STATE_FILE
            try:
                scheduler.STATE_DIR = state_dir
                scheduler.REPORT_DIR = reports_root
                scheduler.LOG_DIR = logs_root
                scheduler.STATE_FILE = state_dir / "state.json"
                stdout = io.StringIO()
                stderr = io.StringIO()
                with patch.object(
                    scheduler,
                    "load_sessions",
                    return_value=(
                        [session],
                        scheduler.DiscoveryStats(
                            indexed_rows=1,
                            indexed_missing_files=0,
                            file_only_recent_unprocessed=0,
                            selected_indexed=1,
                            selected_file_only=0,
                            total_discovered=1,
                            already_processed=0,
                            selected_before_limit=1,
                        ),
                    ),
                ), patch.object(
                    scheduler,
                    "discover_memory_targets",
                    return_value={target.skill: target},
                ), patch.object(
                    scheduler,
                    "targets_for_session",
                    return_value={target.skill: target},
                ), patch.object(
                    scheduler,
                    "prescreen_session",
                    return_value=(True, "synthetic proposal session"),
                ), patch.object(
                    scheduler,
                    "should_stage_capability_candidate",
                    return_value=False,
                ), patch.object(
                    scheduler,
                    "run_candidate_auto_create",
                    return_value=(0, []),
                ), patch.object(
                    scheduler,
                    "run_proposal_staging",
                    return_value=([], [proposal_failure]),
                ), patch.object(
                    scheduler,
                    "classify_session",
                    return_value={
                        "session_id": "session-1",
                        "candidates": [],
                        "semantic_candidate": None,
                        "capability_evolution_proposals": [proposal],
                    },
                ), redirect_stdout(stdout), redirect_stderr(stderr):
                    exit_code = scheduler.process(
                        argparse.Namespace(
                            dry_run=False,
                            inventory_json=False,
                            progress_jsonl=True,
                            lookback_days=90,
                            max_sessions=5,
                            verbose=False,
                            codex_timeout=30,
                            codex_model=None,
                            codex_reasoning=None,
                            classifier_codex_home=None,
                            session_file=None,
                            resolved_project_root=project_root,
                            auto_promote=False,
                        )
                    )
            finally:
                scheduler.STATE_DIR = original_state_dir
                scheduler.REPORT_DIR = original_report_dir
                scheduler.LOG_DIR = original_log_dir
                scheduler.STATE_FILE = original_state_file

            self.assertEqual(exit_code, 0)
            state = json.loads((state_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["processed_sessions"]["session-1"], "2026-05-28T00:10:00Z")
            events = [json.loads(line) for line in stdout.getvalue().splitlines()]
            self.assertEqual(events[-1]["event"], "run_finished")
            self.assertEqual(events[-1]["status"], "completed")
            self.assertEqual(events[-1]["stagedProposals"], 0)
            report = next(reports_root.glob("*-report.md")).read_text(encoding="utf-8")
            self.assertIn("## Rejected Capability Evolution Proposals", report)
            self.assertIn("mutating script proposal must document", report)

    def test_uc_10_supported_proposal_types_validate(self) -> None:
        """UC-10: Supported proposal types are accepted when paths and safety metadata are valid."""
        from govkb.core.proposals import ProposalError
        from govkb.core.proposals import stage_proposal

        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability()

            accepted = ["script", "wrapper", "prompt", "runbook", "instructions_update"]
            for proposal_type in accepted:
                with self.subTest(proposal_type=proposal_type):
                    stage_proposal(
                        project_root,
                        helper.proposal_payload(
                            proposal_id=f"{proposal_type}-proposal",
                            proposal_type=proposal_type,
                            output_path=f".governed/capabilities/release-validation-workflow/{proposal_type}.md",
                            safety_class="read_only" if proposal_type in {"script", "wrapper"} else "docs_only",
                            draft_output=f"# {proposal_type}\n",
                        ),
                        source_run_id="run-1",
                        source_session_id=f"session-{proposal_type}",
                    )

            with self.assertRaisesRegex(ProposalError, "unsupported proposal type"):
                stage_proposal(
                    project_root,
                    helper.proposal_payload(proposal_id="new-capability", proposal_type="new_capability"),
                    source_run_id="run-1",
                    source_session_id="session-new",
                )


if __name__ == "__main__":
    unittest.main()
