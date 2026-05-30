"""Use-case tests for governed learning improvement proposal reports."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import io
import json
import tempfile
from pathlib import Path
import unittest

from govkb.commands.proposals import run_proposals
from govkb.core.proposal_report import build_proposal_report_payload
from govkb.core.proposal_report import build_proposal_review_payload
from govkb.core.proposals import stage_proposal

try:
    from memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper
except ModuleNotFoundError:  # pragma: no cover - supports module-style unittest invocation.
    from tests.memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper


class GovernedLearningImprovementsUseCaseTests(unittest.TestCase):
    """Phase 0 proposal grouping and advisory warning behavior."""

    def test_uc_1_groups_similar_proposals_and_keeps_unrelated_work_separate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability("clearing-qa-on-staging")
            helper.seed_capability("clearing-devops-delivery")
            self._stage_runbook(
                helper,
                proposal_id="qa-dvca-aggregate-payout-e2e-runbook",
                target_capability="clearing-qa-on-staging",
                output_path=".governed/capabilities/clearing-qa-on-staging/runbooks/dvca-aggregate-payout-e2e.md",
                purpose="Capture reusable DVCA aggregate dividend payout E2E QA runbook.",
            )
            self._stage_runbook(
                helper,
                proposal_id="qa-on-staging-dvca-payout-e2e-runbook",
                target_capability="clearing-qa-on-staging",
                output_path=".governed/capabilities/clearing-qa-on-staging/runbooks/dvca-payout-e2e.md",
                purpose="Add a reusable DVCA dividend payout E2E staging QA runbook.",
            )
            self._stage_runbook(
                helper,
                proposal_id="clearing-qa-on-staging-golden-lineage-runbook",
                target_capability="clearing-qa-on-staging",
                output_path=".governed/capabilities/clearing-qa-on-staging/runbooks/golden-historical-lineage-qa.md",
                purpose="Document Golden historical lineage QA sequence.",
            )
            self._stage_runbook(
                helper,
                proposal_id="clearing-devops-delivery-mirror-stale-ref-precheck",
                target_capability="clearing-devops-delivery",
                output_path=".governed/capabilities/clearing-devops-delivery/runbooks/adl-mirror-stale-ref-precheck.md",
                purpose="Document ETNA to Adelphi stale mirror ref diagnostics.",
            )

            payload = build_proposal_report_payload(project_root)

            grouped_ids = [set(group["proposalIds"]) for group in payload["groups"]]
            self.assertIn(
                {"qa-dvca-aggregate-payout-e2e-runbook", "qa-on-staging-dvca-payout-e2e-runbook"},
                grouped_ids,
            )
            self.assertIn({"clearing-qa-on-staging-golden-lineage-runbook"}, grouped_ids)
            self.assertIn({"clearing-devops-delivery-mirror-stale-ref-precheck"}, grouped_ids)
            dvca_group = next(
                group
                for group in payload["groups"]
                if set(group["proposalIds"])
                == {"qa-dvca-aggregate-payout-e2e-runbook", "qa-on-staging-dvca-payout-e2e-runbook"}
            )
            self.assertEqual(dvca_group["recommendedAction"], "merge-first")
            self.assertIn("weak-verification", dvca_group["warningCodes"])

    def test_uc_2_report_is_read_only_and_surfaces_script_quality_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability("clearing-prod-to-staging-replay")
            self._stage_script_without_draft(helper)
            proposal_path = (
                project_root
                / ".governed"
                / "review-proposals"
                / "clearing-prod-to-staging-replay-golden-conflict-replay-script"
                / "proposal.toml"
            )
            before = proposal_path.read_text(encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_proposals(
                    argparse.Namespace(proposal_action="report", project_root=project_root, json=True)
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(proposal_path.read_text(encoding="utf-8"), before)
            payload = json.loads(output.getvalue())
            group = payload["groups"][0]
            self.assertEqual(group["recommendedAction"], "inspect-safety")
            self.assertIn("missing-draft-output", group["warningCodes"])
            self.assertIn("missing-dry-run", group["warningCodes"])
            self.assertIn("weak-script-verification", group["warningCodes"])

    def test_report_text_output_summarizes_groups_and_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability("clearing-qa-on-staging")
            self._stage_runbook(
                helper,
                proposal_id="qa-dvca-aggregate-payout-e2e-runbook",
                target_capability="clearing-qa-on-staging",
                output_path=".governed/capabilities/clearing-qa-on-staging/runbooks/dvca-aggregate-payout-e2e.md",
                purpose="Capture reusable DVCA aggregate dividend payout E2E QA runbook.",
            )

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_proposals(
                    argparse.Namespace(proposal_action="report", project_root=project_root, json=False)
                )

            self.assertEqual(exit_code, 0)
            text = output.getvalue()
            self.assertIn("Proposals: 1", text)
            self.assertIn("action=manual-review", text)
            self.assertIn("qa-dvca-aggregate-payout-e2e-runbook", text)

    def test_review_queue_prioritizes_safety_and_emits_next_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability("clearing-prod-to-staging-replay")
            helper.seed_capability("clearing-qa-on-staging")
            self._stage_script_without_draft(helper)
            self._stage_runbook(
                helper,
                proposal_id="qa-dvca-aggregate-payout-e2e-runbook",
                target_capability="clearing-qa-on-staging",
                output_path=".governed/capabilities/clearing-qa-on-staging/runbooks/dvca-aggregate-payout-e2e.md",
                purpose="Capture reusable DVCA aggregate dividend payout E2E QA runbook.",
            )

            payload = build_proposal_review_payload(project_root)

            self.assertEqual(payload["groups"][0]["recommendedAction"], "inspect-safety")
            self.assertIn("commands", payload["groups"][0])
            self.assertIn("govkb proposals show", payload["groups"][0]["commands"][0])
            manual_group = next(group for group in payload["groups"] if group["recommendedAction"] == "manual-review")
            self.assertTrue(any("govkb proposals apply" in step for step in manual_group["nextSteps"]))

    def test_review_command_filters_by_recommended_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability("clearing-prod-to-staging-replay")
            helper.seed_capability("clearing-qa-on-staging")
            self._stage_script_without_draft(helper)
            self._stage_runbook(
                helper,
                proposal_id="qa-dvca-aggregate-payout-e2e-runbook",
                target_capability="clearing-qa-on-staging",
                output_path=".governed/capabilities/clearing-qa-on-staging/runbooks/dvca-aggregate-payout-e2e.md",
                purpose="Capture reusable DVCA aggregate dividend payout E2E QA runbook.",
            )

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_proposals(
                    argparse.Namespace(
                        proposal_action="review",
                        project_root=project_root,
                        action="inspect-safety",
                        json=True,
                    )
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["summary"]["actionFilter"], "inspect-safety")
            self.assertEqual(payload["summary"]["reviewGroupCount"], 1)
            self.assertEqual(payload["groups"][0]["recommendedAction"], "inspect-safety")

    def _stage_runbook(
        self,
        helper: MemoryReviewCapabilityEvolutionTestHelper,
        *,
        proposal_id: str,
        target_capability: str,
        output_path: str,
        purpose: str,
    ) -> None:
        payload = helper.proposal_payload(
            proposal_id=proposal_id,
            target_capability=target_capability,
            proposal_type="runbook",
            safety_class="docs_only",
            output_path=output_path,
            draft_output=f"# {proposal_id}\n\n{purpose}\n",
        )
        payload["purpose"] = purpose
        payload["verification_command"] = "n/a docs-only"
        payload["evidence"] = "Synthetic governed learning fixture with sanitized proposal metadata."
        stage_proposal(
            helper._require_project_root(),
            payload,
            source_run_id="run-1",
            source_session_id="session-1",
        )

    def _stage_script_without_draft(self, helper: MemoryReviewCapabilityEvolutionTestHelper) -> None:
        payload = helper.proposal_payload(
            proposal_id="clearing-prod-to-staging-replay-golden-conflict-replay-script",
            target_capability="clearing-prod-to-staging-replay",
            proposal_type="script",
            safety_class="mutating_with_dry_run",
            output_path=(
                ".governed/capabilities/clearing-prod-to-staging-replay/"
                "scripts/prepare_golden_conflicts_replay.py"
            ),
            draft_output="",
        )
        payload.pop("draft_output", None)
        payload["purpose"] = "Prepare Golden conflict replay SQL with maintainer approval."
        payload["verification_command"] = "python3 scripts/prepare_golden_conflicts_replay.py"
        payload["evidence"] = "Synthetic governed learning fixture with sanitized proposal metadata."
        stage_proposal(
            helper._require_project_root(),
            payload,
            source_run_id="run-1",
            source_session_id="session-1",
        )


if __name__ == "__main__":
    unittest.main()
