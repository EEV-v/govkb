"""Use-case tests for Governed Skill Quality Gates."""

from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

try:
    from governed_skill_quality_gates_test_helper import GovernedSkillQualityGatesTestHelper
except ModuleNotFoundError:  # pragma: no cover - supports module-style unittest invocation.
    from tests.governed_skill_quality_gates_test_helper import GovernedSkillQualityGatesTestHelper


class GovernedSkillQualityGatesUseCaseTests(unittest.TestCase):
    """Traceable BDD scenario coverage."""

    def test_uc_1_strict_validation_passes_complete_approved_package(self) -> None:
        """UC-1: Strict validation passes a complete approved package."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = GovernedSkillQualityGatesTestHelper(self, root=Path(temp_dir))
            helper.record_step("Given a capability package with required files and lifecycle approval metadata")
            helper.seed_project()
            helper.seed_capability()
            helper.record_step("When the maintainer runs strict validation")
            result = helper.strict_result("release-validation-workflow", activation_required=True)
            helper.record_step("Then validation exits successfully")
            self.assertTrue(result.ok, [issue.as_dict() for issue in result.issues])

    def test_uc_2_normal_validation_remains_backward_compatible(self) -> None:
        """UC-2: Normal validation remains backward-compatible."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = GovernedSkillQualityGatesTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            helper.seed_capability(
                approved=False,
                memory_body=helper.memory_text(
                    title="Release Validation Workflow",
                    command_bullet="- TODO: add durable verification commands.",
                ),
            )
            exit_code, stdout, stderr = helper.run_validate(strict=False)
            self.assertEqual(exit_code, 0, stderr)
            self.assertIn("Validation passed.", stdout)

    def test_uc_3_placeholder_memory_blocks_activation_readiness(self) -> None:
        """UC-3: Placeholder memory blocks activation readiness."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = GovernedSkillQualityGatesTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            helper.seed_capability(
                memory_body=helper.memory_text(
                    title="Release Validation Workflow",
                    command_bullet="- TODO: add durable verification commands.",
                ),
            )
            result = helper.strict_result("release-validation-workflow", activation_required=True)
            self.assertTrue(any(issue.rule_id == "GSK-MEMORY-001" for issue in result.errors))

    def test_uc_4_invalid_project_references_block_activation_readiness(self) -> None:
        """UC-4: Invalid project references block activation readiness."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = GovernedSkillQualityGatesTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            helper.seed_capability(
                memory_body=helper.memory_text(
                    title="Release Validation Workflow",
                    command_bullet="- Use `docs/missing-runbook.md` before signoff.",
                ),
            )
            result = helper.strict_result("release-validation-workflow", activation_required=True)
            self.assertTrue(any(issue.rule_id == "GSK-PATH-001" for issue in result.errors))

    def test_uc_5_credential_paths_and_token_like_content_are_rejected(self) -> None:
        """UC-5: Credential paths and token-like content are rejected."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = GovernedSkillQualityGatesTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            helper.seed_capability(
                memory_body=helper.memory_text(
                    title="Release Validation Workflow",
                    command_bullet="- Never inspect `~/.ssh/id_rsa` or OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz123456.",
                ),
            )
            result = helper.strict_result("release-validation-workflow", activation_required=True)
            messages = "\n".join(issue.message for issue in result.errors)
            self.assertTrue(any(issue.rule_id == "GSK-SAFETY-001" for issue in result.errors))
            self.assertNotIn("sk-proj-", messages)

    def test_uc_6_package_owned_tools_require_visible_safety_documentation(self) -> None:
        """UC-6: Package-owned tools require visible safety documentation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = GovernedSkillQualityGatesTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            capability_root = helper.seed_capability()
            scripts_root = capability_root / "tools" / "scripts"
            scripts_root.mkdir(parents=True, exist_ok=True)
            (scripts_root / "cleanup.sh").write_text("#!/usr/bin/env bash\nrm -rf tmp-output\n", encoding="utf-8")
            result = helper.strict_result("release-validation-workflow", activation_required=True)
            self.assertTrue(any(issue.rule_id == "GSK-TOOLS-001" for issue in result.warnings))
            self.assertTrue(any(issue.rule_id == "GSK-TOOLS-002" for issue in result.warnings))

    def test_uc_8_generic_ids_require_justification_and_approval_before_activation(self) -> None:
        """UC-8: Generic ids require justification and approval before activation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = GovernedSkillQualityGatesTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            helper.seed_capability("local-stack-workflow", scope_justification=None)
            result = helper.strict_result("local-stack-workflow", activation_required=True)
            self.assertTrue(any(issue.rule_id == "GSK-ID-002" for issue in result.errors))

    def test_uc_9_strict_issue_reporting_uses_stable_fields(self) -> None:
        """UC-9: Strict issue reporting uses stable severity and rule ids."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = GovernedSkillQualityGatesTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            helper.seed_capability(
                memory_body=helper.memory_text(
                    title="Release Validation Workflow",
                    command_bullet="- TODO: add durable verification commands.",
                ),
            )
            result = helper.strict_result("release-validation-workflow", activation_required=True)
            issue_payload = result.errors[0].as_dict()
            self.assertEqual(set(issue_payload), {"severity", "ruleId", "location", "message"})
            self.assertTrue(issue_payload["ruleId"].startswith("GSK-"))


if __name__ == "__main__":
    unittest.main()
