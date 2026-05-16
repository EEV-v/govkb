"""Smoke scaffold tests for VS Code Learning Discovery and Progress."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tests.vscode_learning_discovery_progress_test_helper import VscodeLearningDiscoveryProgressTestHelper


class VscodeLearningDiscoveryProgressSmokeTests(unittest.TestCase):
    """Happy-path scaffolds for local verification."""

    def test_smoke_first_setup_shows_learning_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            helper = VscodeLearningDiscoveryProgressTestHelper(self, root=root)
            helper.record_step("Given the user has applied GovKB to a project with governed capabilities")
            helper.record_step("And the project has Codex session metadata available")
            helper.record_step("When the extension refreshes the GovKB learning surface")
            helper.record_step("Then the UI shows session inventory for the selected project")
            helper.record_step("And the UI offers a next action to run bounded learning review")
            self.skipTest("Scaffold only: implement smoke flow for UC-1.")

    def test_smoke_discovery_runs_without_ai_classification(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            helper = VscodeLearningDiscoveryProgressTestHelper(self, root=root)
            helper.record_step("Given the selected project has historical sessions")
            helper.record_step("When the user runs `GovKB: Discover Learning Opportunities`")
            helper.record_step("Then the extension invokes a read-only GovKB CLI inventory command")
            helper.record_step("And the command does not invoke nested Codex classification")
            helper.record_step("And no `.governed/**` or `$CODEX_HOME/skills/**` files are mutated")
            self.skipTest("Scaffold only: implement smoke flow for UC-2.")


if __name__ == "__main__":
    unittest.main()
