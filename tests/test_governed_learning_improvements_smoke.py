"""Smoke tests for governed learning improvement proposal reporting."""

from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from govkb.core.proposal_report import build_proposal_report_payload
from govkb.core.proposals import stage_proposal

try:
    from memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper
except ModuleNotFoundError:  # pragma: no cover - supports module-style unittest invocation.
    from tests.memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper


class GovernedLearningImprovementsSmokeTests(unittest.TestCase):
    """Minimal end-to-end report payload smoke coverage."""

    def test_proposal_report_payload_includes_summary_groups_and_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability()
            proposal = helper.proposal_payload()
            proposal["verification_command"] = "n/a"
            stage_proposal(project_root, proposal, source_run_id="run-1", source_session_id="session-1")

            payload = build_proposal_report_payload(project_root)

            self.assertEqual(payload["summary"]["proposalCount"], 1)
            self.assertEqual(payload["summary"]["groupCount"], 1)
            self.assertGreaterEqual(payload["summary"]["warningCount"], 1)
            self.assertEqual(payload["groups"][0]["proposalIds"], ["release-validation-script"])
            self.assertIn("weak-verification", payload["groups"][0]["warningCodes"])


if __name__ == "__main__":
    unittest.main()
