"""Use-case scaffold tests for VS Code Learning Discovery and Progress."""

from __future__ import annotations

import unittest

from tests.vscode_learning_discovery_progress_test_helper import VscodeLearningDiscoveryProgressTestHelper


class VscodeLearningDiscoveryProgressUseCaseTests(unittest.TestCase):
    """Traceable BDD scenario scaffolds."""

    def setUp(self) -> None:
        self.helper = VscodeLearningDiscoveryProgressTestHelper(self)

    def test_uc_1_first_setup_shows_learning_inventory_instead_of_empty_candidates(self) -> None:
        """UC-1: First setup shows learning inventory instead of empty candidates."""
        self.helper.record_step("Given the user has applied GovKB to a project with governed capabilities")
        self.helper.record_step("And the project has Codex session metadata available")
        self.helper.record_step("When the extension refreshes the GovKB learning surface")
        self.helper.record_step("Then the UI shows session inventory for the selected project")
        self.helper.record_step("And the UI shows installed learning targets or capabilities")
        self.helper.record_step("And the UI does not present an empty candidates list as the only learning result")
        self.helper.record_step("And the UI offers a next action to run bounded learning review")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-1.")

    def test_uc_2_user_can_run_cheap_discovery_before_ai_classification(self) -> None:
        """UC-2: User can run cheap discovery before AI classification."""
        self.helper.record_step("Given the selected project has historical sessions")
        self.helper.record_step("When the user runs `GovKB: Discover Learning Opportunities`")
        self.helper.record_step("Then the extension invokes a read-only GovKB CLI inventory command")
        self.helper.record_step("And the command does not invoke nested Codex classification")
        self.helper.record_step(
            "And the Learning view shows total project sessions, selected sessions for the current lookback, already processed sessions, missing indexed session files, and recommended batch scope"
        )
        self.helper.record_step("And no `.governed/**` or `$CODEX_HOME/skills/**` files are mutated")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-2.")

    def test_uc_3_bounded_batch_review_uses_explicit_scope(self) -> None:
        """UC-3: Bounded batch review uses explicit scope."""
        self.helper.record_step("Given the Learning view has an inventory payload")
        self.helper.record_step("When the user starts a dry-run learning batch with a selected lookback and maximum session count")
        self.helper.record_step(
            "Then the extension invokes `govkb review-memory` with `--dry-run`, `--lookback-days`, `--max-sessions`, and bounded `--codex-timeout`"
        )
        self.helper.record_step("And the UI shows the selected scope before the run starts")
        self.helper.record_step(
            "And the final summary includes reviewed, skipped, applied, staged, candidate, rejected, deferred, and failed counts"
        )
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-3.")

    def test_uc_4_live_progress_identifies_each_reviewed_session(self) -> None:
        """UC-4: Live progress identifies each reviewed session."""
        self.helper.record_step("Given a bounded learning batch is running")
        self.helper.record_step("When the CLI emits structured progress events")
        self.helper.record_step("Then the Learning view shows the current session id, thread name, updated timestamp, and status")
        self.helper.record_step(
            "And session status changes are visible for queued, prescreening, classifying, skipped, classified, deferred, and failed states"
        )
        self.helper.record_step("And the output channel still records the command and human-readable logs")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-4.")

    def test_uc_5_existing_skill_updates_are_separated_from_new_capability_candidates(self) -> None:
        """UC-5: Existing skill updates are separated from new capability candidates."""
        self.helper.record_step("Given the classifier returns lessons for an existing governed capability")
        self.helper.record_step("And no unmatched workflow candidate is created")
        self.helper.record_step("When the run completes")
        self.helper.record_step("Then the UI shows existing skill update counts and patch/report links")
        self.helper.record_step("And the Candidates section says there are no staged new capability candidates")
        self.helper.record_step("And the UI explains that useful learning can exist even when candidate count is zero")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-5.")

    def test_uc_6_dry_run_versus_apply_semantics_are_explicit(self) -> None:
        """UC-6: Dry-run versus apply semantics are explicit."""
        self.helper.record_step("Given a dry-run report includes `Would Apply` lessons and staged patch previews")
        self.helper.record_step("When the user views the learning run result")
        self.helper.record_step("Then the UI labels those outcomes as previews")
        self.helper.record_step(
            "And the UI explains that dry-run writes reports and patches but does not stage `.governed/candidates`"
        )
        self.helper.record_step(
            "And apply mode requires an explicit user action before memory files or candidate folders are changed through the CLI"
        )
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-6.")

    def test_uc_7_classifier_failures_are_resumable_and_understandable(self) -> None:
        """UC-7: Classifier failures are resumable and understandable."""
        self.helper.record_step("Given nested Codex classification times out, hits usage limits, cannot find the executable, or has a connectivity failure")
        self.helper.record_step("When a review batch encounters the failure")
        self.helper.record_step("Then the UI shows the affected session as deferred or failed with a concise reason")
        self.helper.record_step("And remaining unprocessed sessions are not silently marked complete")
        self.helper.record_step("And the UI shows a retry action with the same scope or a smaller batch")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-7.")

    def test_uc_8_structured_ai_output_is_safe_to_inspect(self) -> None:
        """UC-8: Structured AI output is safe to inspect."""
        self.helper.record_step("Given the classifier returns candidate decisions")
        self.helper.record_step("When the extension renders the learning result")
        self.helper.record_step(
            "Then the UI may show target skill, memory section, lesson summary, confidence, validation decision, evidence summary, and semantic candidate summary"
        )
        self.helper.record_step("And the UI does not copy raw session transcripts into extension state or repo artifacts")
        self.helper.record_step("And hidden model reasoning is not exposed")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-8.")

    def test_uc_9_inventory_lookback_communicates_expected_batch_size(self) -> None:
        """UC-9: Inventory lookback communicates expected batch size."""
        examples = [
            ("7", "recent project sessions only"),
            ("30", "recent project sessions only"),
            ("90", "larger backfill scope"),
            ("180", "full or near-full project backfill scope"),
        ]
        for lookback_days, expected_scope in examples:
            with self.subTest(lookback_days=lookback_days, expected_scope=expected_scope):
                self.helper.record_step("Given a project has historical sessions across multiple date ranges")
                self.helper.record_step(f"When the user selects `{lookback_days}` in the Learning view")
                self.helper.record_step(f"Then the inventory shows `{expected_scope}` as selectable for review")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-9.")


if __name__ == "__main__":
    unittest.main()
