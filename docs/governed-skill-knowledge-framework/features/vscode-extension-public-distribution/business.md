# VS Code Extension UI and Public Distribution

Last updated: 2026-04-25

Status: Draft spec

## Request

Create a VS Code extension UI for GovKB and prepare it for public distribution.

The extension should provide one-click setup and one-click apply for the currently open project with minimal user overhead. It should preserve the existing GovKB architecture: the Python `govkb` package remains the core engine, project `.governed/` packages remain the source of truth, and assistant-specific files remain derived outputs.

## Problem

GovKB is currently usable through the Python CLI, but that creates friction for public adoption:

- new users must discover and remember the right commands
- new users must manually install or configure too much before seeing value
- validation, status, candidates, reports, and materialized assistant state are spread across CLI output and filesystem paths
- real-life testing needs low-cost nested Codex defaults to be visible and repeatable
- public distribution needs a familiar install path, onboarding flow, and editor-native feedback
- governance boundaries need to be clear before users run commands that mutate project or assistant-local state

## Business Value

- Lower onboarding cost for new GovKB users.
- Make governed package health visible without requiring command-line fluency.
- Support public distribution through VSIX and the VS Code Marketplace.
- Keep governance behavior auditable by routing all mutations through the tested GovKB core.
- Improve real-life validation speed by exposing quota-safe model/reasoning settings in the UI.
- Create a distribution surface that can later support multiple assistant adapters without redesign.

## Users

| User | Need |
|---|---|
| Project maintainer | Initialize, validate, inspect, and review `.governed/` package health from VS Code. |
| AI-assisted developer | Run GovKB setup and memory-review checks without memorizing CLI flags. |
| Capability reviewer | Inspect staged candidates, generated reports, and materialized skill state before approving changes. |
| New public adopter | Install an extension, follow a guided setup, and understand prerequisites. |
| GovKB maintainer | Ship a public extension without duplicating core governance logic in TypeScript. |

## Scope

- Add a VS Code extension package as an optional UI wrapper over the existing Python GovKB CLI.
- Provide one-click project setup for the open workspace: detect prerequisites, provision or locate the GovKB CLI, initialize `.governed/` when missing, apply the Codex adapter, validate, and show status.
- Provide one-click apply for the open workspace: apply the current governed package to Codex using safe defaults and refresh status/reports.
- Provide command palette commands for common GovKB workflows.
- Provide a GovKB view or views for project status, capabilities, candidates, and memory-review reports.
- Provide settings for CLI path, Codex home, classifier model, classifier reasoning, and review timeout.
- Default real-life classifier runs to low-cost settings: `gpt-5.4-mini` with `low` reasoning.
- Gate trust-sensitive actions behind VS Code Workspace Trust.
- Package the extension as a `.vsix`.
- Prepare Marketplace metadata for public distribution.
- Add tests for command construction, trust gating, status parsing, and UI state behavior.

## Initial Command Surface

| VS Code Command | Underlying GovKB Command |
|---|---|
| `GovKB: One-Click Setup Current Project` | prerequisite check -> `govkb install <workspace> ...` -> `govkb init-kb <workspace> --all ...` -> `govkb status <workspace> ...` |
| `GovKB: One-Click Apply Current Project` | `govkb apply codex --project-root <workspace> ...` -> `govkb status <workspace> ...` |
| `GovKB: Install / Initialize Project` | `govkb install <workspace> ...` |
| `GovKB: Validate Project` | `govkb validate <workspace>` |
| `GovKB: Show Status` | `govkb status <workspace> --codex-home <home>` |
| `GovKB: Apply Codex Adapter` | `govkb apply codex --project-root <workspace> ...` |
| `GovKB: Review Memory Dry Run` | `govkb review-memory --assistant codex --project-root <workspace> --dry-run ...` |
| `GovKB: List Candidates` | `govkb candidates list <workspace>` |
| `GovKB: Auto-Create Ready Candidates` | `govkb candidates auto-create-ready --project-root <workspace> ...` |

## Initial UI Surface

| UI Area | Behavior |
|---|---|
| Status bar | Shows whether the active workspace has `.governed/`, validation health, and local install drift when known. |
| Setup button | Runs one-click setup for the current project and reports the next required user action only when blocked. |
| Apply button | Applies the governed package to Codex for the current project and refreshes status. |
| GovKB project view | Lists project id, capabilities, adapter state, install state, and latest reports. |
| Candidates view | Lists staged candidates, status, occurrence count, suggested capability id, and activation state. |
| Reports view | Lists memory-review reports with failed, deferred, learned, staged, and candidate activity summaries. |
| Output channel | Streams GovKB command output with clear command labels and exit status. |
| Quick picks | Collects safe command parameters such as project id, project name, model, reasoning, and dry-run mode. |

## Governance And Security

- The extension must not store raw transcript content in repo artifacts or extension state.
- The extension must not mutate `.governed/` or assistant-local files directly; it must call the GovKB CLI.
- Trust-sensitive commands must be disabled or blocked when the workspace is not trusted.
- Workspace settings that influence command execution must be treated as trust-sensitive.
- Secrets and Codex auth files must not be displayed, copied, logged, or packaged.
- Dry-run should be the default for memory review from the UI until the user explicitly chooses an apply path.
- One-click setup/apply may mutate the open project and assistant-local derived outputs only after Workspace Trust is granted and the action is explicitly invoked.
- If a prerequisite cannot be satisfied automatically, the extension must stop and present one concrete next action rather than opening a long manual checklist.
- Public Marketplace packaging must not include local test data, private paths, generated reports, or user Codex state.

## Acceptance Criteria

1. A user can install the extension from a local `.vsix`, open a project, and run `GovKB: One-Click Setup Current Project`.
2. One-click setup either completes project initialization, Codex materialization, KB bootstrap, validation, and status refresh, or stops on exactly one actionable blocker.
3. One-click setup handles a missing GovKB CLI by provisioning it automatically when the selected distribution model supports that, or by presenting one install action when automatic provisioning is not available.
4. A trusted workspace can run install/init, validate, status, apply, memory-review dry-run, and candidate listing through VS Code commands.
5. `GovKB: One-Click Apply Current Project` applies the current governed package to Codex and refreshes status without requiring users to enter command flags.
6. An untrusted workspace blocks commands that execute local tools or mutate workspace/assistant-local files.
7. The default memory-review UI path uses `gpt-5.4-mini`, `low` reasoning, and a configurable timeout.
8. The status UI shows `.governed` health, capabilities, install-state presence, and latest report summaries.
9. Candidate UI shows staged, ready, and activated candidates without exposing raw transcript content.
10. Command output is captured in a GovKB output channel and reports non-zero exits clearly.
11. The extension can be packaged with `@vscode/vsce` into a `.vsix`.
12. Marketplace metadata exists for public distribution: README, CHANGELOG, LICENSE handling, icon decision, categories, tags, and publisher fields.
13. Extension tests cover one-click setup orchestration, one-click apply orchestration, command construction, settings resolution, workspace trust behavior, and parsing of representative GovKB CLI output.
14. The Python GovKB core test suite remains green after extension integration.

## Non-goals

- Reimplement GovKB core governance or classification logic in TypeScript.
- Directly edit Codex skill files from the extension.
- Require users to manually run CLI commands for the normal setup/apply happy path.
- Replace `govkb` CLI commands with VS Code-only core behavior.
- Implement a cloud service or hosted knowledge backend.
- Support VS Code Web as part of the first distribution slice.
- Manage cron or OS scheduled tasks in the first slice.
- Add full Claude or Copilot adapters as part of the VS Code extension feature.
- Publish to Marketplace before publisher identity, branding, license, and public README are confirmed.

## Open Questions

1. What is the exact runtime provisioning mechanism for one-click setup: bundled wheel, downloaded package, embedded source, or guided local install action?
2. What publisher id, extension name, icon, and Marketplace branding should be used?
3. Should the first public release support only local Linux/WSL and macOS, or must Windows native paths be supported at launch?
4. Should memory review apply mode be available in the first UI release, or should the extension start with dry-run only?
5. Should the extension collect telemetry, and if yes, what minimal opt-in events are acceptable?
6. Should scheduler setup remain CLI-only for the first release?
7. How should multiple workspace folders be handled when more than one folder contains `.governed/`?
