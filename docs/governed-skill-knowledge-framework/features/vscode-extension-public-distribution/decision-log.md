# Decision Log - VS Code Extension UI and Public Distribution

Last updated: 2026-04-25

| ID | Decision / Candidate | Status | Owner | Source | Notes |
|---|---|---|---|---|---|
| D1 | Keep the Python GovKB package and CLI as the core engine; the VS Code extension is a UI/orchestration layer. | Approved | Engineering | Existing GovKB architecture | Prevents duplicate governance logic and keeps tests centered in the core. |
| D2 | Keep `.governed/` as the repo source of truth; extension state is never authoritative. | Approved | Engineering | Existing GovKB architecture | Extension may inspect and call CLI commands but should not own governed state. |
| D3 | Gate local command execution and mutation paths behind Workspace Trust. | Approved | Engineering/Security | VS Code Workspace Trust docs | Required for credible public distribution. |
| D4 | Default classifier settings in the UI to `gpt-5.4-mini`, `low` reasoning, and `180` second timeout. | Approved | Engineering | MVP+ test plan | Preserves quota-safe real-life validation defaults. |
| D5 | The normal UX must be one-click setup for the open project. | Approved | Product | User direction | Setup should detect prerequisites, initialize `.governed`, apply Codex, bootstrap KB, validate, and show status with minimal user input. |
| D6 | The normal UX must include one-click apply for the open project. | Approved | Product | User direction | Apply should materialize the current governed package to Codex and refresh status without requiring CLI flags. |
| D7 | One-click flows may stop only on explicit blockers and should show one concrete next action. | Approved | Product | User direction | Avoid long setup checklists in the happy path. |
| D8 | Support local `.vsix` packaging before Marketplace publishing. | Approved | Product | business-context.md | First engineering slice targets local VSIX proof; public Marketplace publish remains deferred until publisher and branding are confirmed. |
| D9 | Defer scheduler/cron management from the first UI slice. | Approved | Product/Engineering | business.md | First release focuses on explicit user-triggered commands and status. |
| D10 | Add machine-readable JSON output to GovKB CLI for extension-facing status/candidates/reports. | Approved | Engineering | context.md | Required to avoid brittle parsing in status/candidates/report views. |
| D11 | Start with single-selected-workspace behavior for multi-root VS Code windows. | Approved | Engineering | context.md | Multi-root ambiguity should stop on one project-selection action. |
| D12 | Use guided local install/runtime configuration for the first one-click setup slice instead of bundling or downloading GovKB automatically. | Approved | Product/Engineering | open-questions.md | Missing runtime should present exactly one install/configuration action. |
| D13 | Limit launch platform support to WSL/Linux for the first VSIX proof. | Approved | Product/Engineering | open-questions.md | macOS and Windows native path handling are deferred follow-ups. |
| D14 | Keep memory-review mutation out of the first UI release. | Approved | Product/Governance | open-questions.md | UI runs memory review as dry-run; one-click apply only materializes governed packages. |
| D15 | Ship first release with no telemetry. | Approved | Product/Security | open-questions.md | Avoids privacy work and public extension disclosure risk in the first slice. |
