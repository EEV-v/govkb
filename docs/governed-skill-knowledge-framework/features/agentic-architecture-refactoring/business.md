# Agentic Architecture Refactoring

## Stakeholder Need

GovKB is now used as an everyday agentic operations surface: it manages governed skills, local Codex materialization, learning review batches, isolated promotion worktrees, conversion of existing skills, and VS Code guidance for the next action. The product has enough behavior that small architectural drift now turns into user confusion. Users have seen duplicate or stale worktrees, unclear finalization states, already governed skills appearing in conversion choices, and command labels that do not explain what to do next.

A review of `/Users/vasilevevgeny/code/caveman` identified reusable product-engineering patterns for agentic apps: a documented source-of-truth map, one central registry for supported actions/targets, idempotent install or mutation flows, dry-run and no-write tests, human-readable skill summaries beside machine-facing instructions, and explicit cleanup of stale mirrors. GovKB should reuse those practices where they fit its domain without importing Caveman behavior, tone, or installer mechanics.

## Business Goals

- Make GovKB architecture easier to reason about by documenting which files and stores are authoritative, derived, generated, or disposable.
- Reduce VS Code UI drift by centralizing action labels, icons, command ids, preconditions, and next-action semantics.
- Make promotion, conversion, cleanup, and finalization flows safe to rerun without creating duplicate worktrees or stale UI states.
- Improve everyday UI explanations by showing human-readable state summaries instead of raw paths and command names.
- Add regression tests that prove preview and dry-run paths do not mutate user state.
- Preserve the existing trust boundary: Python CLI/library code owns mutation, while the VS Code extension guides and invokes CLI-backed flows.

## Requirements

| ID | Requirement |
|---|---|
| REQ-AAR-01 | GovKB must have a maintained architecture ownership map that distinguishes repo source, derived Codex output, isolated promotion worktrees, report artifacts, lifecycle metadata, VS Code derived state, and disposable test state. |
| REQ-AAR-02 | VS Code action metadata must be centralized so Home, tree views, command palette contributions, quick picks, and tests use the same labels, icons, command ids, and preconditions where practical. |
| REQ-AAR-03 | Promotion lifecycle operations must be idempotent: accepting, rejecting, finalizing, archiving, and cleanup should be safe to rerun and should report "already done" states instead of hanging or duplicating work. |
| REQ-AAR-04 | GovKB must expose a clear cleanup path for stale, archived, applied, or duplicate isolated promotion worktrees without removing current actionable reviews or sidecar lifecycle audit metadata. |
| REQ-AAR-05 | The VS Code extension must continue to mutate project and assistant-local state only through existing or new GovKB CLI commands. |
| REQ-AAR-06 | Conversion and skill-management UX must use discoverable selections, hide already governed or materialized skills by default, and reserve manual entry for explicit override. |
| REQ-AAR-07 | Governed skills must have user-facing summaries suitable for UI display without requiring users to open raw `instructions.md` first. |
| REQ-AAR-08 | Tests must cover dry-run or preview paths, no-write guarantees, idempotent reruns, duplicate/stale state compaction, and local-state isolation with temporary directories. |
| REQ-AAR-09 | Refactoring must be phased and reversible; no phase may require changing existing `.governed/**` package semantics without a migration plan. |

## Non-Goals

- Replacing the GovKB CLI with direct VS Code filesystem mutations.
- Copying Caveman wording, compression behavior, hooks, or cross-agent installer mechanics.
- Automatically committing project changes.
- Removing existing CLI commands.
- Storing raw assistant session transcript content in repository artifacts.
- Building a generic framework for every possible agentic app before GovKB's concrete workflow is stabilized.

## User-Visible Outcomes

- A user can open the GovKB sidebar and see a trustworthy next action.
- A user can tell which promotion is current, which is duplicate, which is finalized, and which stale worktrees are safe to archive or remove.
- A user can finalize accepted learning updates and see clear follow-up: review Git changes, commit, then reapply Codex materialization if needed.
- A user can convert one selected skill without typing a path when the skill is discoverable.
- A maintainer can inspect one architecture document to understand where GovKB state lives and what owns it.

## Constraints

- Keep `.governed/**` as project-owned source of truth.
- Keep `$CODEX_HOME/**` as derived assistant-local output.
- Keep isolated promotion worktrees under `$CODEX_HOME/memories/govkb/worktrees/<project>/` as review artifacts until explicitly finalized or archived.
- Use synthetic fixtures and temporary directories in tests.
- Keep the extension compatible with the VS Code API range declared in `vscode-extension/package.json`.
