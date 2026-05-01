# VS Code Extension UI and Public Distribution - Use Cases

Last updated: 2026-04-25

## Scope

These use cases cover the locked first engineering slice: a WSL/Linux-focused local VSIX proof that wraps the existing GovKB CLI, adds machine-readable CLI output for extension views, gates local execution behind Workspace Trust, and supports one-click setup/apply for one selected project.

## Actors

| Actor | Goal |
|---|---|
| New GovKB adopter | Install the VSIX, open a project, and complete setup without memorizing CLI commands. |
| Project maintainer | Inspect `.governed/` health, capabilities, candidates, and reports inside VS Code. |
| AI-assisted developer | Apply the governed package to Codex and run memory-review dry-runs with safe defaults. |
| GovKB maintainer | Keep the extension thin and prove core behavior through existing CLI/tests. |

## Background

Given a WSL/Linux VS Code workspace
And the workspace is a local filesystem folder
And GovKB project source of truth remains `.governed/`
And Codex materialized files remain derived local output under `$CODEX_HOME`
And the extension must call the GovKB CLI instead of editing governed or assistant-local files directly

## Scenarios

### UC-1: One-click setup completes for a trusted project @smoke

Given the workspace is trusted
And the selected project does not have `.governed/`
And the GovKB CLI runtime is available through configured settings
When the user runs `GovKB: One-Click Setup Current Project`
Then the extension runs the setup sequence through GovKB CLI commands
And `.governed/` is initialized through `govkb install`
And Codex materialization is applied through the CLI
And starter KB bootstrap runs through `govkb init-kb --all`
And project status refreshes after setup

### UC-2: One-click setup stops on one runtime blocker @regression

Given the workspace is trusted
And no usable GovKB CLI runtime is detected
When the user runs `GovKB: One-Click Setup Current Project`
Then the extension does not run project mutation commands
And the setup flow presents exactly one install or configuration action
And the output channel records the blocked setup step

### UC-3: Untrusted workspace blocks local execution @regression

Given the workspace is not trusted
When the user invokes a command that executes local tools or mutates project or assistant-local files
Then the extension blocks the command before invoking the GovKB CLI
And the user sees a Workspace Trust action
And no `.governed/` or `$CODEX_HOME` files are changed by the extension

### UC-4: One-click apply materializes governed package only @smoke

Given the workspace is trusted
And the selected project has a valid `.governed/` package
And a Codex home is configured or discoverable
When the user runs `GovKB: One-Click Apply Current Project`
Then the extension invokes `govkb apply codex --project-root <workspace> --codex-home <codexHome>`
And the extension refreshes project status after apply
And the flow does not run memory-review mutation

### UC-5: Memory review runs dry-run with quota-safe defaults @regression

Given the workspace is trusted
And the GovKB CLI runtime is available
When the user runs `GovKB: Review Memory Dry Run`
Then the extension invokes `govkb review-memory --assistant codex --project-root <workspace> --dry-run`
And the command includes `--codex-model gpt-5.4-mini`
And the command includes `--codex-reasoning low`
And the command includes `--codex-timeout 180` unless settings override them
And the UI does not expose memory-review apply mode in the first slice

### UC-6: Status and candidate views use machine-readable CLI output @regression

Given the selected project has `.governed/`
And the GovKB CLI supports extension-facing JSON output for status and candidates
When the user opens the GovKB views
Then the extension requests machine-readable status and candidate data from the CLI
And the status view shows validation health, project id, adapters, capabilities, and local install state
And the candidates view shows candidate id, status, occurrences, and activation state
And the extension does not parse durable state from human-formatted CLI text

### UC-7: Reports view summarizes memory-review reports without raw transcript leakage @regression

Given the selected project has GovKB memory-review report files under the configured Codex home
When the user opens the Reports view
Then the extension lists report summaries with failed sessions, deferred sessions, classifier model, reasoning, and report path
And raw session transcript content is not copied into extension state
And the user can open the report file for full local inspection

### UC-8: Multi-root ambiguity requires explicit project selection @regression

Given the VS Code window has multiple workspace folders
And more than one folder could be treated as a GovKB project
When the user runs a GovKB command
Then the extension stops before running the GovKB CLI
And the user is asked to select exactly one project root
And subsequent command construction uses the selected root as `--project-root` or positional project root consistently

### UC-9: VSIX packaging excludes local private state @regression

Given the extension package is built as a local `.vsix`
When packaging runs
Then the package includes extension source, manifest, README, changelog, and required assets
And the package excludes local reports, Codex homes, `.governed` project data, private paths, and generated test output
And the package can be installed locally for manual verification

## Negative And Governance Cases

- The extension must not mutate `.governed/` directly from TypeScript.
- The extension must not mutate `$CODEX_HOME` directly from TypeScript.
- The extension must not expose memory-review apply mode in the first slice.
- The extension must not collect telemetry in the first slice.
- The extension must not silently download or bundle the GovKB runtime in the first slice.
- The extension must not continue after multi-root project ambiguity without explicit selection.

## Traceability

| Requirement | Scenario(s) | Coverage |
|---|---|---|
| One-click setup | UC-1, UC-2 | Full |
| One-click apply | UC-4 | Full |
| Workspace Trust gating | UC-3 | Full |
| CLI remains core engine | UC-1, UC-4, UC-5, UC-6 | Full |
| `.governed/` source of truth | UC-1, UC-3, UC-4 | Full |
| Assistant-local files are derived | UC-3, UC-4 | Full |
| Low-cost memory-review defaults | UC-5 | Full |
| Status/candidates/report visibility | UC-6, UC-7 | Full |
| Raw transcript protection | UC-7 | Full |
| Multi-root handling | UC-8 | First-slice coverage |
| Local VSIX packaging | UC-9 | Full for first slice |
| Marketplace publishing | Deferred | Not in first engineering slice |
| macOS/Windows native support | Deferred | Not in first engineering slice |

## Test Notes

| Scenario | Suggested Test Module | Notes |
|---|---|---|
| UC-1 | `vscode-extension/src/test/setupFlow.test.ts` | Mock CLI runner and assert command sequence. |
| UC-2 | `vscode-extension/src/test/setupFlow.test.ts` | Simulate missing runtime and assert one blocker action. |
| UC-3 | `vscode-extension/src/test/trust.test.ts` | Mock untrusted workspace and assert no CLI invocation. |
| UC-4 | `vscode-extension/src/test/applyFlow.test.ts` | Assert argument-array command construction. |
| UC-5 | `vscode-extension/src/test/memoryReview.test.ts` | Assert dry-run defaults and no apply-mode command. |
| UC-6 | `tests/test_<json_cli_feature>.py`, `vscode-extension/src/test/views.test.ts` | Add Python tests for JSON CLI output and extension parser tests. |
| UC-7 | `vscode-extension/src/test/reports.test.ts` | Use sanitized report fixtures only. |
| UC-8 | `vscode-extension/src/test/projectSelection.test.ts` | Mock multi-root workspace folders. |
| UC-9 | `vscode-extension` package test/CI command | Define exact packaging command in implementation plan. |

