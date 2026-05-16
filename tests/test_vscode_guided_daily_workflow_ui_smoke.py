"""Smoke scaffold tests for VS Code Guided Daily Workflow UI."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from vscode_guided_daily_workflow_ui_test_helper import VscodeGuidedDailyWorkflowUiTestHelper


class VscodeGuidedDailyWorkflowUiSmokeTests(unittest.TestCase):
    """Happy-path scaffolds for local verification."""

    def test_smoke_show_one_primary_next_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            helper = VscodeGuidedDailyWorkflowUiTestHelper(self, root=root)
            helper.record_step("Given status, learning inventory, promotions, reports, and candidates have been refreshed")
            helper.record_step("When the user opens GovKB Home")
            helper.record_step("Then the UI shows one primary next action")
            self.skipTest("Scaffold only: implement smoke flow for UC-1.")

    def test_smoke_guide_first_setup_and_apply(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            helper = VscodeGuidedDailyWorkflowUiTestHelper(self, root=root)
            helper.record_step("Given the selected workspace is not initialized or Codex materialization is missing")
            helper.record_step("When the user opens GovKB Home")
            helper.record_step("Then the primary action is setup or apply")
            self.skipTest("Scaffold only: implement smoke flow for UC-2.")


if __name__ == "__main__":
    unittest.main()
