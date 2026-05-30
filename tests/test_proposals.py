"""Tests for capability-evolution proposal commands and core behavior."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import tempfile
from pathlib import Path
import unittest

from govkb.commands.proposals import run_proposals
from govkb.core.proposals import ProposalError
from govkb.core.proposals import apply_proposal
from govkb.core.proposals import build_proposals_payload
from govkb.core.proposals import stage_proposal

try:
    from memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper
except ModuleNotFoundError:  # pragma: no cover - supports module-style unittest invocation.
    from tests.memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper


class ProposalCoreCommandTests(unittest.TestCase):
    """Proposal storage, listing, showing, and apply behavior."""

    def test_stage_proposal_writes_reviewable_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability()

            result = stage_proposal(
                project_root,
                helper.proposal_payload(),
                source_run_id="run-1",
                source_session_id="session-1",
                source_thread_name="synthetic-session.jsonl",
            )

            self.assertTrue(result.created)
            proposal_root = project_root / ".governed" / "review-proposals" / "release-validation-script"
            self.assertEqual(result.proposal_root, proposal_root)
            metadata = (proposal_root / "proposal.toml").read_text(encoding="utf-8")
            self.assertIn('status = "staged"', metadata)
            self.assertIn('target_capability = "release-validation-workflow"', metadata)
            self.assertTrue((proposal_root / "proposal.md").is_file())
            self.assertTrue((proposal_root / "draft-output.md").is_file())

    def test_proposals_list_and_show_support_text_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability()
            stage_proposal(
                project_root,
                helper.proposal_payload(),
                source_run_id="run-1",
                source_session_id="session-1",
            )

            payload = build_proposals_payload(project_root)
            self.assertEqual(len(payload["proposals"]), 1)
            self.assertEqual(payload["proposals"][0]["id"], "release-validation-script")

            text_output = io.StringIO()
            with redirect_stdout(text_output):
                list_exit = run_proposals(
                    argparse.Namespace(proposal_action="list", project_root=project_root, json=False)
                )
            self.assertEqual(list_exit, 0)
            self.assertIn("release-validation-script status=staged", text_output.getvalue())

            show_output = io.StringIO()
            with redirect_stdout(show_output):
                show_exit = run_proposals(
                    argparse.Namespace(
                        proposal_action="show",
                        proposal_id="release-validation-script",
                        project_root=project_root,
                        json=True,
                    )
                )
            self.assertEqual(show_exit, 0)
            shown = json.loads(show_output.getvalue())
            self.assertEqual(shown["targetCapability"], "release-validation-workflow")

    def test_apply_requires_approval_and_writes_bounded_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability()
            stage_proposal(
                project_root,
                helper.proposal_payload(),
                source_run_id="run-1",
                source_session_id="session-1",
            )

            with self.assertRaisesRegex(ProposalError, "approved"):
                apply_proposal(project_root, "release-validation-script")

            helper.approve_proposal("release-validation-script")
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_proposals(
                    argparse.Namespace(
                        proposal_action="apply",
                        proposal_id="release-validation-script",
                        project_root=project_root,
                    )
                )

            self.assertEqual(exit_code, 0)
            target = (
                project_root
                / ".governed"
                / "capabilities"
                / "release-validation-workflow"
                / "tools"
                / "scripts"
                / "check_release.py"
            )
            self.assertTrue(target.is_file())
            self.assertIn("release validation ok", target.read_text(encoding="utf-8"))
            metadata = (
                project_root
                / ".governed"
                / "review-proposals"
                / "release-validation-script"
                / "proposal.toml"
            ).read_text(encoding="utf-8")
            self.assertIn('status = "applied"', metadata)
            body = (
                project_root
                / ".governed"
                / "review-proposals"
                / "release-validation-script"
                / "proposal.md"
            ).read_text(encoding="utf-8")
            self.assertIn("- Status: applied", body)

    def test_approve_command_records_review_metadata_and_enables_apply(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability()
            stage_proposal(
                project_root,
                helper.proposal_payload(),
                source_run_id="run-1",
                source_session_id="session-1",
            )

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_proposals(
                    argparse.Namespace(
                        proposal_action="approve",
                        proposal_id="release-validation-script",
                        project_root=project_root,
                        approver="test-reviewer",
                        approved_at="2026-05-28T00:00:00Z",
                        notes="Ready after maintainer review.",
                        json=False,
                    )
                )

            self.assertEqual(exit_code, 0)
            self.assertIn("Approved proposal release-validation-script", output.getvalue())
            metadata_path = project_root / ".governed" / "review-proposals" / "release-validation-script" / "proposal.toml"
            metadata = metadata_path.read_text(encoding="utf-8")
            self.assertIn('status = "approved"', metadata)
            self.assertIn('approver = "test-reviewer"', metadata)
            self.assertIn('approved_at = "2026-05-28T00:00:00Z"', metadata)
            self.assertIn('notes = "Ready after maintainer review."', metadata)

            apply_output = io.StringIO()
            with redirect_stdout(apply_output):
                apply_exit = run_proposals(
                    argparse.Namespace(
                        proposal_action="apply",
                        proposal_id="release-validation-script",
                        project_root=project_root,
                    )
                )
            self.assertEqual(apply_exit, 0)
            self.assertIn("Applied proposal release-validation-script", apply_output.getvalue())

    def test_decide_command_records_non_apply_review_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability()
            stage_proposal(
                project_root,
                helper.proposal_payload(),
                source_run_id="run-1",
                source_session_id="session-1",
            )
            helper.approve_proposal("release-validation-script")

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_proposals(
                    argparse.Namespace(
                        proposal_action="decide",
                        proposal_id="release-validation-script",
                        project_root=project_root,
                        status="needs-rework",
                        reviewer="test-reviewer",
                        reviewed_at="2026-05-28T01:00:00Z",
                        reason="Draft needs a real verification command.",
                        next_action="Replace the draft and rerun proposal review.",
                        json=False,
                    )
                )

            self.assertEqual(exit_code, 0)
            self.assertIn("Recorded proposal decision release-validation-script", output.getvalue())
            metadata = (
                project_root
                / ".governed"
                / "review-proposals"
                / "release-validation-script"
                / "proposal.toml"
            ).read_text(encoding="utf-8")
            self.assertIn('status = "needs-rework"', metadata)
            self.assertIn("[approval]", metadata)
            self.assertIn('status = "pending"', metadata)
            self.assertIn("[review]", metadata)
            self.assertIn('decision = "needs-rework"', metadata)
            self.assertIn('reviewer = "test-reviewer"', metadata)
            self.assertIn('reason = "Draft needs a real verification command."', metadata)
            body = (
                project_root
                / ".governed"
                / "review-proposals"
                / "release-validation-script"
                / "proposal.md"
            ).read_text(encoding="utf-8")
            self.assertIn("- Status: needs-rework", body)

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                apply_exit = run_proposals(
                    argparse.Namespace(
                        proposal_action="apply",
                        proposal_id="release-validation-script",
                        project_root=project_root,
                    )
                )
            self.assertEqual(apply_exit, 1)
            self.assertIn("proposal must be approved before apply", stderr.getvalue())

    def test_approve_rejects_proposal_without_draft_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability()
            payload = helper.proposal_payload()
            payload.pop("draft_output")
            stage_proposal(project_root, payload, source_run_id="run-1", source_session_id="session-1")

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = run_proposals(
                    argparse.Namespace(
                        proposal_action="approve",
                        proposal_id="release-validation-script",
                        project_root=project_root,
                        approver="test-reviewer",
                        approved_at=None,
                        notes=None,
                        json=False,
                    )
                )

            self.assertEqual(exit_code, 1)
            self.assertIn("proposal has no draft output", stderr.getvalue())

    def test_invalid_proposal_paths_and_sensitive_content_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability()

            with self.assertRaisesRegex(ProposalError, "unsafe output path"):
                stage_proposal(
                    project_root,
                    helper.proposal_payload(output_path="../escape.py"),
                    source_run_id="run-1",
                    source_session_id="session-1",
                )

            sensitive = helper.proposal_payload()
            sensitive["evidence"] = "OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz123456"
            with self.assertRaisesRegex(ProposalError, "unsafe or sensitive"):
                stage_proposal(project_root, sensitive, source_run_id="run-1", source_session_id="session-1")

    def test_mutating_script_requires_dry_run_or_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability()

            with self.assertRaisesRegex(ProposalError, "read-only script proposal"):
                stage_proposal(
                    project_root,
                    helper.proposal_payload(draft_output="from pathlib import Path\nPath('x').write_text('y')\n"),
                    source_run_id="run-1",
                    source_session_id="session-1",
                )

            with self.assertRaisesRegex(ProposalError, "dry-run or --preview"):
                stage_proposal(
                    project_root,
                    helper.proposal_payload(
                        safety_class="mutating_with_dry_run",
                        draft_output="from pathlib import Path\nPath('x').write_text('y')\n",
                    ),
                    source_run_id="run-1",
                    source_session_id="session-1",
                )

    def test_apply_refuses_to_overwrite_existing_different_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            capability_root = helper.seed_capability()
            existing = capability_root / "tools" / "scripts" / "check_release.py"
            existing.parent.mkdir(parents=True, exist_ok=True)
            existing.write_text("# existing\n", encoding="utf-8")
            stage_proposal(
                project_root,
                helper.proposal_payload(),
                source_run_id="run-1",
                source_session_id="session-1",
            )
            helper.approve_proposal("release-validation-script")

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = run_proposals(
                    argparse.Namespace(
                        proposal_action="apply",
                        proposal_id="release-validation-script",
                        project_root=project_root,
                    )
                )

            self.assertEqual(exit_code, 1)
            self.assertIn("refusing to overwrite existing file", stderr.getvalue())
            self.assertEqual(existing.read_text(encoding="utf-8"), "# existing\n")


if __name__ == "__main__":
    unittest.main()
