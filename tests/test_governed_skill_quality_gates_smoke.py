"""Smoke tests for Governed Skill Quality Gates."""

from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

try:
    from governed_skill_quality_gates_test_helper import GovernedSkillQualityGatesTestHelper
except ModuleNotFoundError:  # pragma: no cover - supports module-style unittest invocation.
    from tests.governed_skill_quality_gates_test_helper import GovernedSkillQualityGatesTestHelper


class GovernedSkillQualityGatesSmokeTests(unittest.TestCase):
    """Happy-path and CLI smoke coverage."""

    def test_smoke_strict_valid_package_passes_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = GovernedSkillQualityGatesTestHelper(self, root=Path(temp_dir))
            helper.record_step("Given a strict-valid governed skill package")
            helper.seed_project()
            helper.seed_capability()
            helper.record_step("When the maintainer runs `govkb validate --strict`")
            exit_code, stdout, stderr = helper.run_validate(strict=True)
            helper.record_step("Then strict validation passes")
            self.assertEqual(exit_code, 0, stderr)
            self.assertIn("Strict validation passed.", stdout)

    def test_smoke_strict_cli_reports_structured_issue(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = GovernedSkillQualityGatesTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            helper.seed_capability(
                memory_body=helper.memory_text(
                    title="Release Validation Workflow",
                    command_bullet="- TODO: add durable verification commands.",
                ),
            )
            exit_code, _, stderr = helper.run_validate(strict=True)
            self.assertEqual(exit_code, 1)
            self.assertIn("strict error: GSK-MEMORY-001:", stderr)


if __name__ == "__main__":
    unittest.main()
