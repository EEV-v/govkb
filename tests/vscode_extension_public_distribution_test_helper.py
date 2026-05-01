"""Helper scaffold for VS Code Extension UI and Public Distribution tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class VscodeExtensionPublicDistributionTestHelper:
    """Feature-specific helper API scaffold."""

    def __init__(self, test_case: Any, root: Path | None = None) -> None:
        self.test_case = test_case
        self.root = root
        self.steps: list[str] = []

    def record_step(self, step: str) -> None:
        self.steps.append(step)

    # Setup
    def configure_trusted_workspace(self, project_root: Path) -> None:
        raise NotImplementedError("TODO: implement trusted workspace helper.")

    def configure_untrusted_workspace(self, project_root: Path) -> None:
        raise NotImplementedError("TODO: implement untrusted workspace helper.")

    def configure_govkb_runtime(self, command: str) -> None:
        raise NotImplementedError("TODO: implement runtime settings helper.")

    def configure_codex_home(self, codex_home: Path) -> None:
        raise NotImplementedError("TODO: implement Codex home settings helper.")

    def configure_multi_root_workspace(self, project_roots: list[Path]) -> None:
        raise NotImplementedError("TODO: implement multi-root helper.")

    # Seeding
    def seed_project_without_governed_package(self, project_root: Path) -> None:
        raise NotImplementedError("TODO: implement project seeding helper.")

    def seed_valid_governed_package(self, project_root: Path) -> None:
        raise NotImplementedError("TODO: implement governed package helper.")

    def seed_candidate_json_output(self, project_root: Path) -> None:
        raise NotImplementedError("TODO: implement candidate fixture helper.")

    def seed_memory_review_report(self, codex_home: Path) -> None:
        raise NotImplementedError("TODO: implement report fixture helper.")

    # Execution
    def execute_one_click_setup(self) -> None:
        raise NotImplementedError("TODO: implement setup execution helper.")

    def execute_one_click_apply(self) -> None:
        raise NotImplementedError("TODO: implement apply execution helper.")

    def execute_memory_review_dry_run(self) -> None:
        raise NotImplementedError("TODO: implement memory-review execution helper.")

    def execute_status_view_refresh(self) -> None:
        raise NotImplementedError("TODO: implement status view helper.")

    def execute_candidate_view_refresh(self) -> None:
        raise NotImplementedError("TODO: implement candidate view helper.")

    def execute_vsix_packaging(self) -> None:
        raise NotImplementedError("TODO: implement package execution helper.")

    # Assertions
    def assert_cli_sequence(self, expected_commands: list[list[str]]) -> None:
        raise NotImplementedError("TODO: implement CLI sequence assertion helper.")

    def assert_single_blocker_action(self) -> None:
        raise NotImplementedError("TODO: implement blocker assertion helper.")

    def assert_no_cli_invocation(self) -> None:
        raise NotImplementedError("TODO: implement no-invocation assertion helper.")

    def assert_status_view_uses_json(self) -> None:
        raise NotImplementedError("TODO: implement status view assertion helper.")

    def assert_candidate_view_uses_json(self) -> None:
        raise NotImplementedError("TODO: implement candidate view assertion helper.")

    def assert_report_summary_excludes_raw_transcript(self) -> None:
        raise NotImplementedError("TODO: implement report summary assertion helper.")

    def assert_package_excludes_private_state(self) -> None:
        raise NotImplementedError("TODO: implement package assertion helper.")

    # Cleanup
    def cleanup(self) -> None:
        raise NotImplementedError("TODO: implement cleanup helper.")

