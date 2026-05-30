"""Tests for GovKB doctor diagnostics."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest

from govkb.commands.apply import run_codex_apply
from govkb.commands.doctor import build_doctor_payload
from govkb.commands.doctor import run_doctor
from govkb.commands.install import _cron_line
from govkb.core.proposals import stage_proposal

try:
    from memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper
except ModuleNotFoundError:  # pragma: no cover - supports module-style unittest invocation.
    from tests.memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper


class DoctorCommandTests(unittest.TestCase):
    """Read-only health, cron, proposal, and install-state diagnostics."""

    def test_doctor_json_reports_status_memory_review_cron_and_proposals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            helper.seed_capability()
            codex_home = Path(temp_dir) / "codex-home"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    run_codex_apply(
                        argparse.Namespace(
                            project_root=project_root,
                            release=None,
                            revision="doctor-test",
                            codex_home=codex_home,
                            preview=False,
                        )
                    ),
                    0,
                )
            stage_proposal(
                project_root,
                helper.proposal_payload(proposal_type="runbook", safety_class="docs_only"),
                source_run_id="run-1",
                source_session_id="session-1",
            )
            state_dir = codex_home / "memories" / "govkb" / "projects" / "demo-project" / "codex-memory-review"
            state_dir.mkdir(parents=True)
            (state_dir / "state.json").write_text(
                json.dumps(
                    {
                        "processed_sessions": {"session-1": "2026-05-30T07:00:00Z"},
                        "last_successful_updated_at": "2026-05-30T07:00:00Z",
                        "last_run_at": "2026-05-30T08:00:00Z",
                    }
                ),
                encoding="utf-8",
            )
            report_dir = state_dir / "reports"
            report_dir.mkdir()
            (report_dir / "2026-05-30T080000Z-report.md").write_text(
                "\n".join(
                    [
                        "# Codex Memory Review - 2026-05-30",
                        "",
                        "- Mode: apply",
                        "- Sessions processed: 1",
                        "- Skipped before classification: 0",
                        "- Deferred sessions: 0",
                        "- Applied: 0",
                        "- Staged: 1",
                        "- Capability candidates: 0",
                        "- Capability evolution proposals: 1",
                        "- Rejected capability evolution proposals: 0",
                        "- Rejected: 0",
                        "- Failed sessions: 0",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            cron = _cron_line(project_root.resolve(), codex_home.resolve(), "15 8 * * *") + "\n"

            with patch("govkb.commands.doctor._read_crontab", return_value=(0, cron, "")):
                payload = build_doctor_payload(project_root, codex_home)

            self.assertEqual(payload["schemaVersion"], 1)
            self.assertEqual(payload["validation"]["status"], "ok")
            self.assertEqual(payload["installState"]["codex"]["appliedRevision"], "doctor-test")
            self.assertEqual(payload["memoryReview"]["state"]["status"], "present")
            self.assertEqual(payload["memoryReview"]["state"]["processedSessionCount"], 1)
            self.assertEqual(payload["memoryReview"]["latestRun"]["status"], "completed")
            self.assertEqual(payload["memoryReview"]["latestRun"]["counts"]["staged"], 1)
            self.assertEqual(payload["cron"]["status"], "installed")
            self.assertEqual(payload["proposalQueue"]["summary"]["proposalCount"], 1)

    def test_doctor_text_reports_missing_cron_and_report_recommendations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            project_root = helper.seed_project()
            codex_home = Path(temp_dir) / "codex-home"

            output = io.StringIO()
            with patch("govkb.commands.doctor._read_crontab", return_value=(1, "", "no crontab for user")):
                with redirect_stdout(output):
                    exit_code = run_doctor(
                        argparse.Namespace(project_root=project_root, codex_home=codex_home, json=False)
                    )

            self.assertEqual(exit_code, 0)
            text = output.getvalue()
            self.assertIn("Cron: missing", text)
            self.assertIn("Memory review: state=missing | latest=missing", text)
            self.assertIn("govkb install", text)
            self.assertIn("govkb review-memory", text)
            self.assertFalse(text.lstrip().startswith("{"))


if __name__ == "__main__":
    unittest.main()
