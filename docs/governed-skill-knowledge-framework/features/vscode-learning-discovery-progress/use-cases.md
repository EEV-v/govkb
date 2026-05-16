# VS Code Learning Discovery and Progress - Use Cases

Last updated: 2026-05-10

## Scope

These use cases cover a VS Code extension and GovKB CLI feature that makes project learning discovery visible before AI classification, shows live review progress during bounded batches, and separates existing skill updates from new capability candidates.

FeatureType: VSCodeExtension

## Actors

| Actor | Goal |
|---|---|
| New GovKB adopter | Understand that GovKB found project history and know what to run next. |
| Project maintainer | Backfill learning in bounded batches without losing track of progress or governance state. |
| AI-assisted developer | Review useful lessons, staged patches, and candidate proposals without reading raw session transcripts. |
| GovKB maintainer | Keep the extension thin, testable, and backed by structured CLI contracts. |

## Background

Given a trusted VS Code workspace with a selected GovKB project
And the GovKB CLI runtime is available through extension settings or runtime discovery
And `.governed/**` remains the governed source of truth
And `$CODEX_HOME/**` remains derived local assistant state
And the extension does not mutate governed or assistant-local files directly

## Scenarios

### UC-1: First setup shows learning inventory instead of empty candidates @smoke

Given the user has applied GovKB to a project with governed capabilities
And the project has Codex session metadata available
When the extension refreshes the GovKB learning surface
Then the UI shows session inventory for the selected project
And the UI shows installed learning targets or capabilities
And the UI does not present an empty candidates list as the only learning result
And the UI offers a next action to run bounded learning review

### UC-2: User can run cheap discovery before AI classification @smoke

Given the selected project has historical sessions
When the user runs `GovKB: Discover Learning Opportunities`
Then the extension invokes a read-only GovKB CLI inventory command
And the command does not invoke nested Codex classification
And the Learning view shows total project sessions, selected sessions for the current lookback, already processed sessions, missing indexed session files, and recommended batch scope
And no `.governed/**` or `$CODEX_HOME/skills/**` files are mutated

### UC-3: Bounded batch review uses explicit scope @regression

Given the Learning view has an inventory payload
When the user starts a dry-run learning batch with a selected lookback and maximum session count
Then the extension invokes `govkb review-memory` with `--dry-run`, `--lookback-days`, `--max-sessions`, and bounded `--codex-timeout`
And the UI shows the selected scope before the run starts
And the final summary includes reviewed, skipped, applied, staged, candidate, rejected, deferred, and failed counts

### UC-4: Live progress identifies each reviewed session @regression

Given a bounded learning batch is running
When the CLI emits structured progress events
Then the Learning view shows the current session id, thread name, updated timestamp, and status
And session status changes are visible for queued, prescreening, classifying, skipped, classified, deferred, and failed states
And the output channel still records the command and human-readable logs

### UC-5: Existing skill updates are separated from new capability candidates @regression

Given the classifier returns lessons for an existing governed capability
And no unmatched workflow candidate is created
When the run completes
Then the UI shows existing skill update counts and patch/report links
And the Candidates section says there are no staged new capability candidates
And the UI explains that useful learning can exist even when candidate count is zero

### UC-6: Dry-run versus apply semantics are explicit @regression

Given a dry-run report includes `Would Apply` lessons and staged patch previews
When the user views the learning run result
Then the UI labels those outcomes as previews
And the UI explains that dry-run writes reports and patches but does not stage `.governed/candidates`
And apply mode requires an explicit user action before memory files or candidate folders are changed through the CLI

### UC-7: Classifier failures are resumable and understandable @regression

Given nested Codex classification times out, hits usage limits, cannot find the executable, or has a connectivity failure
When a review batch encounters the failure
Then the UI shows the affected session as deferred or failed with a concise reason
And remaining unprocessed sessions are not silently marked complete
And the UI shows a retry action with the same scope or a smaller batch

### UC-8: Structured AI output is safe to inspect @regression

Given the classifier returns candidate decisions
When the extension renders the learning result
Then the UI may show target skill, memory section, lesson summary, confidence, validation decision, evidence summary, and semantic candidate summary
And the UI does not copy raw session transcripts into extension state or repo artifacts
And hidden model reasoning is not exposed

## Scenario Outlines

### UC-9: Inventory lookback communicates expected batch size @regression

Given a project has historical sessions across multiple date ranges
When the user selects `<lookback_days>` in the Learning view
Then the inventory shows `<expected_scope>` as selectable for review

Examples:

| lookback_days | expected_scope |
|---|---|
| 7 | recent project sessions only |
| 30 | recent project sessions only |
| 90 | larger backfill scope |
| 180 | full or near-full project backfill scope |

## Negative And Governance Cases

- The extension must not mutate `.governed/**` directly.
- The extension must not mutate `$CODEX_HOME/**` directly.
- Inventory mode must not call nested Codex.
- Dry-run must not be described as candidate creation.
- Raw session transcripts must not be shown by default or written into repo docs.
- A zero-candidate result must not be treated as a zero-learning result.
- Long-running classification must not look like a hung command when progress events are available.

## Traceability

| Requirement | Scenario(s) | Coverage |
|---|---|---|
| LD-01 | UC-1, UC-5 | Full |
| LD-02 | UC-2 | Full |
| LD-03 | UC-3, UC-9 | Full |
| LD-04 | UC-4, UC-7 | Full |
| LD-05 | UC-5, UC-6, UC-7 | Full |
| LD-06 | UC-5 | Full |
| LD-07 | UC-6 | Full |
| LD-08 | UC-3, UC-5, UC-6 | Full |
| LD-09 | UC-8 | Full |
| LD-10 | UC-2, UC-6, Negative And Governance Cases | Full |
| LD-11 | UC-3, UC-7, UC-9 | Full |
| LD-12 | UC-7, Negative And Governance Cases | Partial; cross-platform runtime discovery needs implementation plan detail. |

## Test Notes

| Scenario | Suggested Test Module | Notes |
|---|---|---|
| UC-1 | `vscode-extension/src/test/suite/views.test.ts` | Add Learning rows for inventory and non-empty capability targets. |
| UC-2 | `tests/test_vscode_learning_discovery_progress_use_cases.py`, `vscode-extension/src/test/suite/flows.test.ts` | Assert inventory mode does not call classifier or mutate memory. |
| UC-3 | `vscode-extension/src/test/suite/govkbCli.test.ts`, `vscode-extension/src/test/suite/flows.test.ts` | Assert lookback/max-session/timeout flags. |
| UC-4 | `tests/test_vscode_learning_discovery_progress_use_cases.py`, `vscode-extension/src/test/suite/learningProgress.test.ts` | Use synthetic progress events. |
| UC-5 | `vscode-extension/src/test/suite/views.test.ts` | Assert existing updates and candidates render separately. |
| UC-6 | `vscode-extension/src/test/suite/views.test.ts` | Assert dry-run preview wording and apply action. |
| UC-7 | `tests/test_memory_review.py`, `vscode-extension/src/test/suite/learningProgress.test.ts` | Cover timeout/deferred/failed progress events. |
| UC-8 | `vscode-extension/src/test/suite/learningProgress.test.ts` | Assert parser rejects or ignores raw transcript fields. |
| UC-9 | `tests/test_vscode_learning_discovery_progress_use_cases.py` | Synthetic session metadata across lookback windows. |
