"""Use-case scaffold tests for VS Code Extension UI and Public Distribution."""

from __future__ import annotations

import unittest

from vscode_extension_public_distribution_test_helper import VscodeExtensionPublicDistributionTestHelper


class VscodeExtensionPublicDistributionUseCaseTests(unittest.TestCase):
    """Traceable BDD scenario scaffolds."""

    def setUp(self) -> None:
        self.helper = VscodeExtensionPublicDistributionTestHelper(self)

    def test_uc_1_one_click_setup_completes_for_trusted_project(self) -> None:
        """UC-1: One-click setup completes for a trusted project."""
        self.helper.record_step("Given the workspace is trusted")
        self.helper.record_step("And the selected project does not have `.governed/`")
        self.helper.record_step("And the GovKB CLI runtime is available through configured settings")
        self.helper.record_step("When the user runs `GovKB: One-Click Setup Current Project`")
        self.helper.record_step("Then the extension runs the setup sequence through GovKB CLI commands")
        self.helper.record_step("And `.governed/` is initialized through `govkb install`")
        self.helper.record_step("And Codex materialization is applied through the CLI")
        self.helper.record_step("And starter KB bootstrap runs through `govkb init-kb --all`")
        self.helper.record_step("And project status refreshes after setup")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-1.")

    def test_uc_2_one_click_setup_stops_on_one_runtime_blocker(self) -> None:
        """UC-2: One-click setup stops on one runtime blocker."""
        self.helper.record_step("Given the workspace is trusted")
        self.helper.record_step("And no usable GovKB CLI runtime is detected")
        self.helper.record_step("When the user runs `GovKB: One-Click Setup Current Project`")
        self.helper.record_step("Then the extension does not run project mutation commands")
        self.helper.record_step("And the setup flow presents exactly one install or configuration action")
        self.helper.record_step("And the output channel records the blocked setup step")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-2.")

    def test_uc_3_untrusted_workspace_blocks_local_execution(self) -> None:
        """UC-3: Untrusted workspace blocks local execution."""
        self.helper.record_step("Given the workspace is not trusted")
        self.helper.record_step("When the user invokes a command that executes local tools or mutates project or assistant-local files")
        self.helper.record_step("Then the extension blocks the command before invoking the GovKB CLI")
        self.helper.record_step("And the user sees a Workspace Trust action")
        self.helper.record_step("And no `.governed/` or `$CODEX_HOME` files are changed by the extension")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-3.")

    def test_uc_4_one_click_apply_materializes_governed_package_only(self) -> None:
        """UC-4: One-click apply materializes governed package only."""
        self.helper.record_step("Given the workspace is trusted")
        self.helper.record_step("And the selected project has a valid `.governed/` package")
        self.helper.record_step("And a Codex home is configured or discoverable")
        self.helper.record_step("When the user runs `GovKB: One-Click Apply Current Project`")
        self.helper.record_step("Then the extension invokes `govkb apply codex --project-root <workspace> --codex-home <codexHome>`")
        self.helper.record_step("And the extension refreshes project status after apply")
        self.helper.record_step("And the flow does not run memory-review mutation")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-4.")

    def test_uc_5_memory_review_runs_dry_run_with_quota_safe_defaults(self) -> None:
        """UC-5: Memory review runs dry-run with quota-safe defaults."""
        self.helper.record_step("Given the workspace is trusted")
        self.helper.record_step("And the GovKB CLI runtime is available")
        self.helper.record_step("When the user runs `GovKB: Review Memory Dry Run`")
        self.helper.record_step("Then the extension invokes `govkb review-memory --assistant codex --project-root <workspace> --dry-run`")
        self.helper.record_step("And the command includes `--codex-model gpt-5.4-mini`")
        self.helper.record_step("And the command includes `--codex-reasoning low`")
        self.helper.record_step("And the command includes `--codex-timeout 180` unless settings override them")
        self.helper.record_step("And the command includes `--max-sessions 1` unless settings override it")
        self.helper.record_step("And the UI also exposes `GovKB: Review Memory Apply` for trusted workspaces")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-5.")

    def test_uc_6_status_and_candidate_views_use_machine_readable_cli_output(self) -> None:
        """UC-6: Status and candidate views use machine-readable CLI output."""
        self.helper.record_step("Given the selected project has `.governed/`")
        self.helper.record_step("And the GovKB CLI supports extension-facing JSON output for status and candidates")
        self.helper.record_step("When the user opens the GovKB views")
        self.helper.record_step("Then the extension requests machine-readable status and candidate data from the CLI")
        self.helper.record_step("And the status view shows validation health, project id, adapters, capabilities, and local install state")
        self.helper.record_step("And the candidates view shows candidate id, status, occurrences, and activation state")
        self.helper.record_step("And the extension does not parse durable state from human-formatted CLI text")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-6.")

    def test_uc_7_reports_view_summarizes_without_raw_transcript_leakage(self) -> None:
        """UC-7: Reports view summarizes memory-review reports without raw transcript leakage."""
        self.helper.record_step("Given the selected project has GovKB memory-review report files under the configured Codex home")
        self.helper.record_step("When the user opens the Reports view")
        self.helper.record_step("Then the extension lists report summaries with failed sessions, deferred sessions, classifier model, reasoning, and report path")
        self.helper.record_step("And raw session transcript content is not copied into extension state")
        self.helper.record_step("And the user can open the report file for full local inspection")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-7.")

    def test_uc_8_multi_root_ambiguity_requires_explicit_project_selection(self) -> None:
        """UC-8: Multi-root ambiguity requires explicit project selection."""
        self.helper.record_step("Given the VS Code window has multiple workspace folders")
        self.helper.record_step("And more than one folder could be treated as a GovKB project")
        self.helper.record_step("When the user runs a GovKB command")
        self.helper.record_step("Then the extension stops before running the GovKB CLI")
        self.helper.record_step("And the user is asked to select exactly one project root")
        self.helper.record_step("And subsequent command construction uses the selected root as `--project-root` or positional project root consistently")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-8.")

    def test_uc_9_vsix_packaging_excludes_local_private_state(self) -> None:
        """UC-9: VSIX packaging excludes local private state."""
        self.helper.record_step("Given the extension package is built as a local `.vsix`")
        self.helper.record_step("When packaging runs")
        self.helper.record_step("Then the package includes extension source, manifest, README, changelog, and required assets")
        self.helper.record_step("And the package excludes local reports, Codex homes, `.governed` project data, private paths, and generated test output")
        self.helper.record_step("And the package can be installed locally for manual verification")
        self.skipTest("Scaffold only: implement helper calls and assertions for UC-9.")


if __name__ == "__main__":
    unittest.main()
