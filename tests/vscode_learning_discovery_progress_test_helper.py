"""Helper scaffold for VS Code Learning Discovery and Progress tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class VscodeLearningDiscoveryProgressTestHelper:
    """Feature-specific helper API scaffold."""

    def __init__(self, test_case: Any, root: Path | None = None) -> None:
        self.test_case = test_case
        self.root = root
        self.steps: list[str] = []

    def record_step(self, step: str) -> None:
        self.steps.append(step)

    # Setup
    def configure_project_root(self, project_name: str) -> Path:
        raise NotImplementedError("TODO: implement project root setup helper.")

    def configure_codex_home(self) -> Path:
        raise NotImplementedError("TODO: implement disposable Codex home setup helper.")

    def configure_review_scope(self, lookback_days: int, max_sessions: int) -> None:
        raise NotImplementedError("TODO: implement review scope setup helper.")

    def configure_extension_settings(self) -> None:
        raise NotImplementedError("TODO: implement extension settings setup helper.")

    # Seeding
    def seed_governed_capabilities(self) -> None:
        raise NotImplementedError("TODO: implement governed capability fixture helper.")

    def seed_session_metadata(self) -> None:
        raise NotImplementedError("TODO: implement synthetic session metadata helper.")

    def seed_processed_session_state(self) -> None:
        raise NotImplementedError("TODO: implement processed session state helper.")

    def seed_memory_review_report(self) -> None:
        raise NotImplementedError("TODO: implement report fixture helper.")

    def seed_candidate_summary(self) -> None:
        raise NotImplementedError("TODO: implement candidate fixture helper.")

    def seed_progress_events(self) -> None:
        raise NotImplementedError("TODO: implement progress JSONL fixture helper.")

    # Execution
    def execute_learning_discovery(self) -> None:
        raise NotImplementedError("TODO: implement inventory command execution helper.")

    def execute_learning_batch_dry_run(self) -> None:
        raise NotImplementedError("TODO: implement dry-run batch execution helper.")

    def execute_learning_batch_apply(self) -> None:
        raise NotImplementedError("TODO: implement apply batch execution helper.")

    def execute_progress_stream_reduction(self) -> None:
        raise NotImplementedError("TODO: implement progress reducer execution helper.")

    def execute_extension_refresh(self) -> None:
        raise NotImplementedError("TODO: implement extension refresh flow helper.")

    # Assertions
    def assert_inventory_is_visible(self) -> None:
        raise NotImplementedError("TODO: implement inventory visibility assertion helper.")

    def assert_classifier_was_not_invoked(self) -> None:
        raise NotImplementedError("TODO: implement no-classifier assertion helper.")

    def assert_no_governed_or_skill_mutation(self) -> None:
        raise NotImplementedError("TODO: implement no-mutation assertion helper.")

    def assert_bounded_review_command(self) -> None:
        raise NotImplementedError("TODO: implement bounded command assertion helper.")

    def assert_progress_rows_are_visible(self) -> None:
        raise NotImplementedError("TODO: implement progress row assertion helper.")

    def assert_existing_updates_separate_from_candidates(self) -> None:
        raise NotImplementedError("TODO: implement existing-update separation assertion helper.")

    def assert_dry_run_apply_semantics(self) -> None:
        raise NotImplementedError("TODO: implement dry-run/apply assertion helper.")

    def assert_retryable_failure_is_visible(self) -> None:
        raise NotImplementedError("TODO: implement retryable failure assertion helper.")

    def assert_structured_output_has_no_raw_transcript(self) -> None:
        raise NotImplementedError("TODO: implement safe structured output assertion helper.")

    def assert_lookback_scope(self, lookback_days: int, expected_scope: str) -> None:
        raise NotImplementedError("TODO: implement lookback scope assertion helper.")

    # Cleanup
    def cleanup(self) -> None:
        raise NotImplementedError("TODO: implement cleanup helper.")
