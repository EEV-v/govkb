# VS Code Extension UI and Public Distribution - Requirements Catalog

Last updated: 2026-04-25

PoC scope: prove the current GovKB CLI baseline, define the first-slice JSON CLI contracts needed by the VS Code extension, and identify which extension behaviors must be proven after the TypeScript package is scaffolded.

| ID | Requirement | Source | PoC Assertion | Scenario(s) | Status |
|---|---|---|---|---|---|
| REQ-VSCODE-01 | Add a VS Code extension package under `vscode-extension/` with manifest, source, tests, README, changelog, license handling, and local VSIX packaging support. | `business.md`, `scope-lock.md` | A-10 | UC-9 | Planned; extension package not present yet. |
| REQ-VSCODE-02 | Keep the extension as a thin orchestration layer over GovKB CLI and do not reimplement governance logic in TypeScript. | `business.md`, `decision-log.md` D1 | A-01, A-05 | UC-1, UC-4, UC-5, UC-6 | PoC ready; current CLI command surface exists. |
| REQ-VSCODE-03 | One-click setup for a trusted selected workspace runs through GovKB CLI setup commands and refreshes status. | `business.md`, `scope-lock.md`, `spec-handoff.md` | A-04, A-05 | UC-1 | Partially proven by current Python install/apply/init-kb/status tests; extension orchestration still planned. |
| REQ-VSCODE-04 | If GovKB runtime is unavailable, one-click setup stops before mutation and presents exactly one install/configuration action. | `open-questions.md` Q1, `decision-log.md` D12 | A-07 | UC-2 | Planned; requires extension runtime resolver tests. |
| REQ-VSCODE-05 | Commands that execute local tools or mutate project or assistant-local files are blocked when Workspace Trust is not granted. | `business.md`, `decision-log.md` D3 | A-06 | UC-3 | Planned; requires extension trust gate tests. |
| REQ-VSCODE-06 | One-click apply invokes `govkb apply codex --project-root <workspace> --codex-home <codexHome>`, refreshes status, and does not run memory-review mutation. | `business.md`, `decision-log.md` D6, D14 | A-04, A-05 | UC-4 | Partially proven by current Python apply tests; extension command construction still planned. |
| REQ-VSCODE-07 | Memory review from the UI is dry-run only in the first slice and uses default model `gpt-5.4-mini`, reasoning `low`, and timeout `180` unless settings override them. | `scope-lock.md`, `decision-log.md` D4, D14 | A-08 | UC-5 | PoC ready; current Python wrapper supports these flags. |
| REQ-VSCODE-08 | Add machine-readable JSON output for project status including validation status, KB health, project id, releases, adapters, capabilities, and Codex install-state summary. | `context.md`, `decision-log.md` D10 | A-02, A-11 | UC-6 | Current gap confirmed; proposed contract fixture created. |
| REQ-VSCODE-09 | Add machine-readable JSON output for candidate listing including candidate id, status, occurrences, suggested capability id, activation state, and path. | `context.md`, `decision-log.md` D10 | A-03, A-12 | UC-6 | Current gap confirmed; proposed contract fixture created. |
| REQ-VSCODE-10 | Reports view summarizes memory-review reports with failed/deferred/learned/staged counts, classifier settings, and report path without copying raw transcript content into extension state. | `business.md`, `use-cases.md`, `scope-lock.md` | A-09, A-13 | UC-7 | Planned; sanitized fixture contract created. |
| REQ-VSCODE-11 | Extension command execution uses argument-array process spawning and never shell interpolation for GovKB commands. | `context.md`, `spec-handoff.md` | A-05 | UC-1, UC-4, UC-5, UC-6 | Planned; requires TypeScript command construction tests. |
| REQ-VSCODE-12 | Settings resolve `govkb.command`, `govkb.pythonPath`, `govkb.setupMode`, `govkb.codexHome`, classifier model/reasoning, review timeout, and dry-run default. | `scope-lock.md`, `context.md` | A-05, A-08 | UC-1, UC-4, UC-5 | Planned; requires extension settings tests. |
| REQ-VSCODE-13 | Multi-root workspaces stop on ambiguity and require one explicit project selection before CLI invocation. | `open-questions.md` Q7, `decision-log.md` D11 | A-14 | UC-8 | Planned; requires extension project selection tests. |
| REQ-VSCODE-14 | Packaging excludes local reports, Codex homes, `.governed` project data, private paths, and generated test output. | `business.md`, `use-cases.md` | A-10 | UC-9 | Planned; requires `.vscodeignore` and packaging check. |
| REQ-VSCODE-15 | The Python GovKB core test suite remains green after extension integration. | `business.md`, `spec-handoff.md` | A-04 | UC-1, UC-4, UC-6 | Baseline targeted tests are rerunnable now; full suite required after implementation. |

