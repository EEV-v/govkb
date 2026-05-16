"""Helper scaffold for VS Code Guided Daily Workflow UI tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class VscodeGuidedDailyWorkflowUiTestHelper:
    """Feature-specific helper API scaffold."""

    def __init__(self, test_case: Any, root: Path | None = None) -> None:
        self.test_case = test_case
        self.root = root
        self.steps: list[str] = []

    def record_step(self, step: str) -> None:
        self.steps.append(step)

    # Setup
    def configure_extension_settings(self, value: dict[str, Any]) -> None:
        raise NotImplementedError("TODO: implement setup helper.")

    def configure_project_status(self, value: dict[str, Any]) -> None:
        raise NotImplementedError("TODO: implement setup helper.")

    # Seeding
    def seed_learning_inventory(self, value: dict[str, Any]) -> None:
        raise NotImplementedError("TODO: implement seeding helper.")

    def seed_promotion_summary(self, value: dict[str, Any]) -> None:
        raise NotImplementedError("TODO: implement seeding helper.")

    def seed_local_skill_inventory(self, value: list[dict[str, Any]]) -> None:
        raise NotImplementedError("TODO: implement seeding helper.")

    # Execution
    def execute_build_home_model(self) -> None:
        raise NotImplementedError("TODO: implement execution helper.")

    def execute_home_action(self, action_id: str) -> None:
        raise NotImplementedError("TODO: implement execution helper.")

    def execute_refresh_tree_views(self) -> None:
        raise NotImplementedError("TODO: implement execution helper.")

    # Assertions
    def assert_primary_action(self, expected: str) -> None:
        raise NotImplementedError("TODO: implement assertion helper.")

    def assert_compact_tree_rows(self) -> None:
        raise NotImplementedError("TODO: implement assertion helper.")

    def assert_cli_mutation_boundary_preserved(self) -> None:
        raise NotImplementedError("TODO: implement assertion helper.")

    def assert_no_raw_transcript_content(self) -> None:
        raise NotImplementedError("TODO: implement assertion helper.")

    # Cleanup
    def cleanup(self) -> None:
        raise NotImplementedError("TODO: implement cleanup helper.")
