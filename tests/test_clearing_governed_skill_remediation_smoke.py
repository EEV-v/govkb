"""Smoke tests for Clearing Governed Skill Remediation."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import tempfile
from pathlib import Path
import unittest

try:
    from clearing_governed_skill_remediation_test_helper import ClearingGovernedSkillRemediationTestHelper
except ModuleNotFoundError:  # pragma: no cover - supports module-style unittest invocation.
    from tests.clearing_governed_skill_remediation_test_helper import ClearingGovernedSkillRemediationTestHelper

from govkb.cli import main


class ClearingGovernedSkillRemediationSmokeTests(unittest.TestCase):
    """Happy-path remediation report coverage."""

    def test_smoke_git_owned_project_writes_report_only(self) -> None:
        """UC-6: Owned Git project can write a report without changing capability packages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = ClearingGovernedSkillRemediationTestHelper(self, root=Path(temp_dir))
            helper.record_step("Given the inspected project root is inside the Git repository that owns `.governed`")
            helper.seed_project(git=True)
            helper.seed_local_stack_workflow(command_bullet="- Run `README.md` before changing the local stack.")
            before = helper.capability_file_snapshot()
            helper.record_step("When the maintainer asks GovKB to write the remediation report")
            exit_code, stdout, stderr = helper.run_remediate_project(write_report=True)
            helper.record_step("Then GovKB creates a markdown report under `.governed/reports/remediation/`")
            self.assertEqual(exit_code, 0, stderr)
            self.assertIn("Report:", stdout)
            report_root = helper.project_root / ".governed" / "reports" / "remediation"
            self.assertTrue((report_root / "latest-remediation-report.md").is_file())
            reports = sorted(report_root.glob("*-remediation-report.md"))
            self.assertTrue(reports)
            self.assertIn("GSK-ID-002", reports[-1].read_text(encoding="utf-8"))
            helper.record_step("And no files under `.governed/capabilities/` are created, removed, or rewritten")
            self.assertEqual(before, helper.capability_file_snapshot())

    def test_smoke_cli_help_includes_write_report(self) -> None:
        stdout = io.StringIO()
        with self.assertRaises(SystemExit) as raised:
            with redirect_stdout(stdout):
                main(["remediate", "project", "--help"])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn("--write-report", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
