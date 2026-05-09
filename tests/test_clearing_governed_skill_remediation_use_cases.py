"""Use-case tests for Clearing Governed Skill Remediation."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import unittest

try:
    from clearing_governed_skill_remediation_test_helper import ClearingGovernedSkillRemediationTestHelper
except ModuleNotFoundError:  # pragma: no cover - supports module-style unittest invocation.
    from tests.clearing_governed_skill_remediation_test_helper import ClearingGovernedSkillRemediationTestHelper

from govkb.core.remediation import remediation_option_for_rule


class ClearingGovernedSkillRemediationUseCaseTests(unittest.TestCase):
    """Traceable BDD scenario coverage."""

    def test_uc_1_build_remediation_report_from_strict_validation(self) -> None:
        """UC-1: Build remediation report from strict validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = ClearingGovernedSkillRemediationTestHelper(self, root=Path(temp_dir))
            helper.record_step("Given a governed project contains a weak active capability such as `local-stack-workflow`")
            helper.seed_project()
            helper.seed_local_stack_workflow(command_bullet="- Run `README.md` before changing the local stack.")
            helper.record_step("When the maintainer runs a remediation report command for the project")
            report = helper.build_report()
            helper.record_step("Then GovKB runs strict governed skill validation in activation-readiness mode")
            self.assertEqual(report.status, "action-required")
            self.assertTrue(any(issue.rule_id == "GSK-ID-002" for issue in report.strict_issues))
            helper.record_step("And the report recommends maintainer approval before capability package files are changed")
            self.assertTrue(all(recommendation.approval_required for recommendation in report.recommendations))

    def test_uc_2_prefer_demote_or_deprecate_for_weak_generic_capability(self) -> None:
        """UC-2: Prefer demotion or deprecation for weak generic active capability."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = ClearingGovernedSkillRemediationTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            helper.seed_local_stack_workflow(command_bullet="- Run `README.md` before changing the local stack.")
            report = helper.build_report()
            matching = [
                recommendation
                for recommendation in report.recommendations
                if recommendation.capability_id == "local-stack-workflow"
            ]
            self.assertTrue(matching)
            self.assertEqual(matching[0].option, "demote-or-deprecate")
            self.assertIn("GSK-ID-002", matching[0].rule_ids)

    def test_uc_3_invalid_repo_paths_become_repair_actions_not_automatic_edits(self) -> None:
        """UC-3: Invalid repo paths become repair actions, not automatic edits."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = ClearingGovernedSkillRemediationTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            helper.seed_local_stack_workflow(
                capability_id="clearing-stack-workflow",
                scope_justification="Clearing local stack workflow.",
                command_bullet="- Run `docs/missing-runbook.md` before changing the local stack.",
            )
            before = helper.capability_file_snapshot()
            report = helper.build_report()
            after = helper.capability_file_snapshot()
            self.assertEqual(before, after)
            self.assertTrue(any(issue.rule_id == "GSK-PATH-001" for issue in report.strict_issues))
            self.assertTrue(
                any(
                    recommendation.option == "repair-paths-after-approval"
                    for recommendation in report.recommendations
                )
            )

    def test_uc_4_candidate_auto_create_policy_is_visible_and_constrained(self) -> None:
        """UC-4: Candidate auto-create policy is visible and constrained."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = ClearingGovernedSkillRemediationTestHelper(self, root=Path(temp_dir))
            helper.seed_project(auto_create=True, min_occurrences=3)
            report = helper.build_report()
            payload = report.as_dict()
            automation = payload["automation"]
            self.assertEqual(
                automation,
                {
                    "autoCreateCapabilities": True,
                    "autoCreateMinOccurrences": 3,
                    "strictActivationRequired": True,
                    "recommendation": (
                        "Auto-create is enabled but constrained by candidate review approval and strict activation; "
                        "disable it during manual remediation if a freeze window is required."
                    ),
                },
            )

    def test_uc_5_non_git_project_blocks_durable_report_write(self) -> None:
        """UC-5: Unowned or non-Git project roots block durable report writes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = ClearingGovernedSkillRemediationTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            helper.seed_local_stack_workflow(command_bullet="- Run `README.md` before changing the local stack.")
            exit_code, stdout, stderr = helper.run_remediate_project(write_report=True)
            self.assertEqual(exit_code, 1)
            self.assertIn("could not write remediation report", stderr)
            self.assertIn("project root is not inside a Git repository", stderr)
            self.assertNotIn("Report:", stdout)
            self.assertFalse((helper.project_root / ".governed" / "reports").exists())

    def test_uc_5_git_project_without_governed_root_blocks_report_write(self) -> None:
        """UC-5: Git ownership alone is not enough without a governed package."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ClearingService"
            project_root.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True, text=True)
            helper = ClearingGovernedSkillRemediationTestHelper(self, root=Path(temp_dir))
            helper.project_root = project_root
            exit_code, _, stderr = helper.run_remediate_project(write_report=True)
            self.assertEqual(exit_code, 1)
            self.assertIn("governed root does not exist", stderr)
            self.assertFalse((project_root / ".governed").exists())

    def test_uc_7_useful_project_knowledge_steward_memory_is_preserved(self) -> None:
        """UC-7: Useful project-knowledge-steward memory is preserved."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = ClearingGovernedSkillRemediationTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            report = helper.build_report()
            self.assertEqual(report.status, "clean")
            self.assertFalse(
                any(
                    recommendation.capability_id == "project-knowledge-steward"
                    for recommendation in report.recommendations
                )
            )

    def test_uc_8_machine_readable_report_output_is_safe_for_tools(self) -> None:
        """UC-8: Machine-readable report output is safe for tools."""
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = ClearingGovernedSkillRemediationTestHelper(self, root=Path(temp_dir))
            helper.seed_project()
            helper.seed_local_stack_workflow(
                capability_id="clearing-stack-workflow",
                scope_justification="Clearing local stack workflow.",
                command_bullet=(
                    "- Never store OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz123456 in governed memory."
                ),
            )
            exit_code, stdout, stderr = helper.run_remediate_project(json_output=True)
            self.assertEqual(exit_code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["schemaVersion"], 1)
            self.assertTrue(any(issue["ruleId"] == "GSK-SAFETY-001" for issue in payload["strictIssues"]))
            self.assertNotIn("sk-proj-", stdout)

    def test_uc_9_strict_issue_category_maps_to_remediation_option(self) -> None:
        """UC-9: Strict issue category maps to remediation option."""
        cases = {
            "GSK-ID-002": "demote-or-deprecate",
            "GSK-PATH-001": "repair-paths-after-approval",
            "GSK-MEMORY-001": "repair-memory-after-approval",
            "GSK-SAFETY-001": "remove-unsafe-content",
            "GSK-LIFECYCLE-001": "approval-required",
        }
        for rule_id, expected in cases.items():
            with self.subTest(rule_id=rule_id):
                self.assertEqual(remediation_option_for_rule(rule_id), expected)


if __name__ == "__main__":
    unittest.main()
