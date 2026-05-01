"""Smoke scaffold tests for VS Code Extension UI and Public Distribution."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from vscode_extension_public_distribution_test_helper import VscodeExtensionPublicDistributionTestHelper


class VscodeExtensionPublicDistributionSmokeTests(unittest.TestCase):
    """Happy-path scaffolds for local verification."""

    def test_smoke_one_click_setup_for_trusted_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            helper = VscodeExtensionPublicDistributionTestHelper(self, root=root)
            helper.record_step("Given the workspace is trusted")
            helper.record_step("And the selected project does not have `.governed/`")
            helper.record_step("And the GovKB CLI runtime is available through configured settings")
            helper.record_step("When the user runs `GovKB: One-Click Setup Current Project`")
            helper.record_step("Then project status refreshes after setup")
            self.skipTest("Scaffold only: implement smoke flow for UC-1.")

    def test_smoke_one_click_apply_for_valid_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            helper = VscodeExtensionPublicDistributionTestHelper(self, root=root)
            helper.record_step("Given the workspace is trusted")
            helper.record_step("And the selected project has a valid `.governed/` package")
            helper.record_step("And a Codex home is configured or discoverable")
            helper.record_step("When the user runs `GovKB: One-Click Apply Current Project`")
            helper.record_step("Then the extension refreshes project status after apply")
            self.skipTest("Scaffold only: implement smoke flow for UC-4.")


if __name__ == "__main__":
    unittest.main()

