"""Use-case scaffold tests for VS Code Guided Daily Workflow UI."""

from __future__ import annotations

import unittest

from vscode_guided_daily_workflow_ui_test_helper import VscodeGuidedDailyWorkflowUiTestHelper


class VscodeGuidedDailyWorkflowUiUseCaseTests(unittest.TestCase):
    """Traceable BDD scenario scaffolds."""

    def setUp(self) -> None:
        self.helper = VscodeGuidedDailyWorkflowUiTestHelper(self)

    def test_uc_1_show_one_primary_next_action(self) -> None:
        """UC-1: Show One Primary Next Action."""
        self.helper.record_step("Given status, learning inventory, promotions, reports, and candidates have been refreshed")
        self.helper.record_step("When the user opens GovKB Home")
        self.helper.record_step("Then the UI shows one primary next action")
        self.helper.record_step("And supporting badges explain project health, install state, learning availability, and promotion state")
        self.helper.record_step("And advanced actions remain available without competing with the primary action")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-1.")

    def test_uc_2_guide_first_setup_and_apply(self) -> None:
        """UC-2: Guide First Setup And Apply."""
        self.helper.record_step("Given the selected workspace is not initialized or Codex materialization is missing")
        self.helper.record_step("When the user opens GovKB Home")
        self.helper.record_step("Then the primary action is setup or apply")
        self.helper.record_step("And the UI explains the blocker without raw command syntax")
        self.helper.record_step("And running the action delegates to the existing setup or apply flow")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-2.")

    def test_uc_3_run_learning_review_from_daily_flow(self) -> None:
        """UC-3: Run Learning Review From Daily Flow."""
        self.helper.record_step("Given learning inventory reports reviewable sessions")
        self.helper.record_step("When the user chooses the primary review action")
        self.helper.record_step("Then the UI runs a bounded dry-run by default")
        self.helper.record_step("And live progress shows the current session, reviewed count, learned count, failed count, and latest report link")
        self.helper.record_step("And the output channel remains available for full command logs")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-3.")

    def test_uc_4_review_and_finalize_promotion_without_worktree_confusion(self) -> None:
        """UC-4: Review And Finalize Promotion Without Worktree Confusion."""
        self.helper.record_step("Given a promotion is ready for review or accepted")
        self.helper.record_step("When the user opens GovKB Home")
        self.helper.record_step("Then the digest summary and lifecycle state are visible")
        self.helper.record_step("And ready promotions expose accept and reject actions")
        self.helper.record_step("And accepted promotions expose finalize as the primary action")
        self.helper.record_step("And opening a worktree is secondary, not the default path")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-4.")

    def test_uc_5_detect_applied_changes_that_need_commit(self) -> None:
        """UC-5: Detect Applied Changes That Need Commit."""
        self.helper.record_step("Given an accepted promotion was finalized into the active project")
        self.helper.record_step("When the active project contains matching .governed changes not yet committed")
        self.helper.record_step("Then GovKB Home shows commit required")
        self.helper.record_step("And the UI does not present the promotion as fully finalized")
        self.helper.record_step("And after commit and refresh, the UI no longer shows commit required")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-5.")

    def test_uc_6_use_picker_driven_skill_management(self) -> None:
        """UC-6: Use Picker-Driven Skill Management."""
        self.helper.record_step("Given local Codex skills and governed capabilities are discoverable")
        self.helper.record_step("When the user chooses convert, rename, or merge from GovKB Home or Governed Skills")
        self.helper.record_step("Then the UI uses picker-driven selection with descriptions and details")
        self.helper.record_step("And already governed or materialized skills are hidden from conversion choices")
        self.helper.record_step("And manual entry is available only as an explicit fallback")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-6.")

    def test_uc_7_keep_native_tree_views_compact(self) -> None:
        """UC-7: Keep Native Tree Views Compact."""
        self.helper.record_step("Given GovKB Home is available")
        self.helper.record_step("When the user opens Status, Learning, Promotions, Reports, Candidates, or Governed Skills tree views")
        self.helper.record_step("Then each view shows compact summaries and state-appropriate inline actions")
        self.helper.record_step("And raw paths, duplicate worktrees, and finalized promotions are hidden unless needed for troubleshooting")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-7.")

    def test_uc_8_preserve_governance_boundaries(self) -> None:
        """UC-8: Preserve Governance Boundaries."""
        self.helper.record_step("Given the user runs any Home action that mutates project or assistant-local state")
        self.helper.record_step("When the extension executes the action")
        self.helper.record_step("Then the mutation is performed through the GovKB CLI flow")
        self.helper.record_step("And the webview or tree view code does not directly write .governed/** or $CODEX_HOME/**")
        self.helper.record_step("And refresh reloads state from CLI-backed sources after completion")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-8.")

    def test_uc_9_primary_action_selection_by_state(self) -> None:
        """UC-9: Primary Action Selection By State."""
        examples = {
            "not initialized": "setup",
            "apply available": "apply governed skills",
            "learned updates pending": "create review worktree",
            "promotion ready for review": "inspect digest",
            "promotion accepted": "finalize accepted updates",
            "applied promotion with dirty governed files": "commit governed updates",
            "clean current project": "review another learning batch",
        }
        for state, expected in examples.items():
            with self.subTest(state=state, expected=expected):
                self.helper.record_step(f"Given the dashboard model receives {state}")
                self.helper.record_step("When it derives the primary next action")
                self.helper.record_step(f"Then the primary action is {expected}")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-9.")


if __name__ == "__main__":
    unittest.main()
