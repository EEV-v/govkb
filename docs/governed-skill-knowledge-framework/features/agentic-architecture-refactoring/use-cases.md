# Agentic Architecture Refactoring - Use Cases

Last updated: 2026-05-16

## Scope

This feature covers architecture and refactoring improvements that make GovKB safer and clearer as an agentic app: ownership documentation, centralized VS Code action metadata, idempotent promotion lifecycle operations, stale worktree cleanup, governed skill display improvements, and regression tests for dry-run/no-write behavior.

## Actors

| Actor | Goal |
|---|---|
| Daily GovKB user | Understand the next safe action without reading raw worktree paths or command names. |
| Skill maintainer | Convert, rename, merge, and inspect governed skills without manual path typing when data is discoverable. |
| Project maintainer | Review, finalize, archive, and clean promotion worktrees without duplicate or stale state. |
| GovKB engineer | Refactor CLI and extension code without drifting from authoritative state ownership rules. |

## Background

Given a GovKB repository with Python CLI commands under `src/govkb/`
And a VS Code extension under `vscode-extension/`
And governed project source under `.governed/**`
And assistant-local output under a configured `CODEX_HOME`

## Scenarios

### UC-1: Maintainer can inspect the agentic state ownership map @smoke

Given the repository contains governed skills, Codex materialization, promotion worktrees, lifecycle metadata, and VS Code derived state
When a maintainer opens the architecture ownership document
Then the document identifies which stores are authoritative, derived, generated, or disposable
And it names the command or module responsible for each mutation path

### UC-2: VS Code actions use one registry for user-facing commands @smoke

Given the extension exposes Home actions, tree row actions, and command palette commands
When an engineer adds or changes a GovKB user action
Then the action id, label, icon, command id, description, and basic precondition live in one typed registry where practical
And tests detect drift between the registry and `vscode-extension/package.json`

### UC-3: Finalizing an accepted promotion is safe to rerun @regression

Given a promotion is accepted and has already been applied to the active project
When the user invokes finalize again from the CLI or VS Code
Then GovKB reports that the promotion is already applied or has no remaining files to copy
And it does not duplicate worktrees, rewrite unrelated project files, or hang the UI progress state

### UC-4: Cleanup previews stale and duplicate promotion worktrees @regression

Given a project has ready, accepted, applied, archived, and duplicate promotion worktrees
When the user runs promotion cleanup in preview mode
Then GovKB lists only cleanup-eligible artifacts
And it excludes the current actionable ready or accepted promotion
And no filesystem files or lifecycle metadata are removed

### UC-5: Cleanup apply removes only eligible artifacts @regression

Given the user reviewed a cleanup preview
When the user runs promotion cleanup in apply mode
Then GovKB removes only the selected or eligible stale worktrees under the computed promotions root
And it preserves sidecar lifecycle metadata with a cleanup marker that records what was removed
And cleaned promotions no longer appear in the default actionable promotions list
And project `.governed/**` and materialized Codex skills are unchanged

### UC-6: Governed skill management avoids manual entry when data is discoverable @regression

Given local Codex skills include already governed, already materialized, and standalone source skills
When the user opens Convert Existing Skill To Governed
Then already governed or materialized skills are hidden from the default picker
And standalone source skills are selectable with name and description
And manual path entry remains available as an explicit fallback item

### UC-7: Governed skills show human-readable summaries @regression

Given a governed capability has a name, description, aliases, lifecycle state, and optional user-facing summary
When the user views governed skills in VS Code
Then the row or detail view shows a business-readable summary before raw file paths
And opening raw `instructions.md` remains available for maintainers who need it

### UC-8: Governance boundary blocks direct UI mutation @regression

Given a VS Code action would change project source, local Codex output, promotion metadata, or worktree contents
When that action is executed
Then the extension invokes a GovKB CLI-backed command or existing flow wrapper
And tests avoid using the user's real home directory, Codex home, or raw assistant transcripts

## Scenario Outlines

### UC-9: Action registry maps lifecycle state to next action @regression

Given project status has <state>
When Home builds its primary action
Then the primary action is <expected>

Examples:

| state | expected |
|---|---|
| missing status | Set up GovKB |
| apply available | Apply latest governed skills |
| ready promotion | Review learning digest |
| accepted promotion | Finalize accepted updates |
| applied promotion with dirty governed files | Commit governed updates |
| current project with review inventory | Review next learning batch |

## Negative And Governance Cases

- Cleanup preview must not delete files.
- Cleanup apply must reject paths outside the computed promotions root.
- Registry refactors must not remove existing command ids without migration.
- Human-facing summaries must not embed raw assistant transcript content.
- UI state must not mark a promotion as complete while `.governed/**` still has relevant uncommitted changes.

## Traceability

| Requirement | Scenario(s) | Coverage |
|---|---|---|
| REQ-AAR-01 | UC-1 | Architecture ownership map. |
| REQ-AAR-02 | UC-2, UC-9 | Centralized extension action metadata and state mapping. |
| REQ-AAR-03 | UC-3, UC-9 | Idempotent promotion lifecycle and UI state. |
| REQ-AAR-04 | UC-4, UC-5 | Stale and duplicate worktree cleanup. |
| REQ-AAR-05 | UC-8 | CLI mutation boundary. |
| REQ-AAR-06 | UC-6 | Picker-driven conversion and manual fallback. |
| REQ-AAR-07 | UC-7 | Human-readable governed skill summaries. |
| REQ-AAR-08 | UC-3, UC-4, UC-5, UC-8, UC-9 | Dry-run/no-write, temp-dir, idempotency, and state tests. |
| REQ-AAR-09 | UC-1, UC-8 | Phased, reversible refactoring with governance boundaries. |

## Test Notes

| Scenario | Suggested Test Module | Notes |
|---|---|---|
| UC-1 | `tests/test_agentic_architecture_refactoring_smoke.py` | Assert ownership doc exists and names core stores. |
| UC-2, UC-9 | `vscode-extension/src/test/suite/actionRegistry.test.ts` | Assert registry parity with manifest and Home primary actions. |
| UC-3 | `tests/test_agentic_architecture_refactoring_use_cases.py` | Extend promotion fixture and rerun apply/finalize. |
| UC-4, UC-5 | `tests/test_agentic_architecture_refactoring_use_cases.py` | Use temporary project/Codex home and synthetic promotion worktrees. |
| UC-6 | `vscode-extension/src/test/suite/localSkills.test.ts` or existing extension tests | Verify default exclusion and manual fallback. |
| UC-7 | `vscode-extension/src/test/suite/views.test.ts` | Verify summary labels avoid raw path-first UX. |
| UC-8 | `vscode-extension/src/test/suite/actionRegistry.test.ts`, Python temp-dir tests | Verify mutation actions map to CLI-backed commands. |
