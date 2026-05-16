# VS Code Guided Daily Workflow UI - Use Cases

Last updated: 2026-05-16

## Scope

Feature type: VSCodeExtension.

The feature adds a guided GovKB Home surface and refines native extension flows so everyday users can discover the next action, perform review and promotion steps, and manage governed skills without raw command decoding.

## Actors

| Actor | Goal |
|---|---|
| GovKB daily user | Open the extension and know the next action for a project. |
| Learning reviewer | Inspect generated learning updates, accept or reject them, and finalize accepted updates. |
| Skill maintainer | Convert, rename, and merge governed skills without manual path typing when choices are discoverable. |
| Troubleshooter | Open output, reports, or source files when a workflow fails. |

## Background

Given a VS Code workspace contains or remembers a GovKB project root
And the GovKB extension can run the configured GovKB CLI
And CLI mutations remain the source of truth for `.governed/**` and `$CODEX_HOME/**`

## Scenarios

### UC-1: Show One Primary Next Action @smoke

Given status, learning inventory, promotions, reports, and candidates have been refreshed
When the user opens GovKB Home
Then the UI shows one primary next action
And supporting badges explain project health, install state, learning availability, and promotion state
And advanced actions remain available without competing with the primary action

### UC-2: Guide First Setup And Apply @smoke

Given the selected workspace is not initialized or Codex materialization is missing
When the user opens GovKB Home
Then the primary action is setup or apply
And the UI explains the blocker without raw command syntax
And running the action delegates to the existing setup or apply flow

### UC-3: Run Learning Review From Daily Flow @regression

Given learning inventory reports reviewable sessions
When the user chooses the primary review action
Then the UI runs a bounded dry-run by default
And live progress shows the current session, reviewed count, learned count, failed count, and latest report link
And the output channel remains available for full command logs

### UC-4: Review And Finalize Promotion Without Worktree Confusion @regression

Given a promotion is ready for review or accepted
When the user opens GovKB Home
Then the digest summary and lifecycle state are visible
And ready promotions expose accept and reject actions
And accepted promotions expose finalize as the primary action
And opening a worktree is secondary, not the default path

### UC-5: Detect Applied Changes That Need Commit @regression

Given an accepted promotion was finalized into the active project
When the active project contains matching `.governed` changes not yet committed
Then GovKB Home shows commit required
And the UI does not present the promotion as fully finalized
And after commit and refresh, the UI no longer shows commit required

### UC-6: Use Picker-Driven Skill Management @regression

Given local Codex skills and governed capabilities are discoverable
When the user chooses convert, rename, or merge from GovKB Home or Governed Skills
Then the UI uses picker-driven selection with descriptions and details
And already governed or materialized skills are hidden from conversion choices
And manual entry is available only as an explicit fallback

### UC-7: Keep Native Tree Views Compact @regression

Given GovKB Home is available
When the user opens Status, Learning, Promotions, Reports, Candidates, or Governed Skills tree views
Then each view shows compact summaries and state-appropriate inline actions
And raw paths, duplicate worktrees, and finalized promotions are hidden unless needed for troubleshooting

### UC-8: Preserve Governance Boundaries @regression

Given the user runs any Home action that mutates project or assistant-local state
When the extension executes the action
Then the mutation is performed through the GovKB CLI flow
And the webview or tree view code does not directly write `.governed/**` or `$CODEX_HOME/**`
And refresh reloads state from CLI-backed sources after completion

## Scenario Outlines

### UC-9: Primary Action Selection By State @regression

Given the dashboard model receives `<state>`
When it derives the primary next action
Then the primary action is `<expected>`

Examples:

| state | expected |
|---|---|
| not initialized | setup |
| apply available | apply governed skills |
| learned updates pending | create review worktree |
| promotion ready for review | inspect digest |
| promotion accepted | finalize accepted updates |
| applied promotion with dirty governed files | commit governed updates |
| clean current project | review another learning batch |

## Negative And Governance Cases

- Webview rendering must not require network access or remote scripts.
- Raw session transcripts must never appear in Home model, HTML, tests, or report summaries.
- A failed CLI command must leave the dashboard refreshable and must not mark a workflow complete.
- Duplicate promotion worktrees should collapse into one actionable row or card.
- Applied and committed promotions should not continue to show as pending work.

## Traceability

| Requirement | Scenario(s) | Coverage |
|---|---|---|
| One primary next action | UC-1, UC-9 | Dashboard model and Home rendering. |
| Explicit daily flow | UC-2, UC-3, UC-4, UC-5 | Setup, learning, promotion, finalization, commit. |
| Polished controls | UC-1, UC-6, UC-7 | Icons, buttons, picker flows, compact trees. |
| Promotion clarity | UC-4, UC-5, UC-9 | Digest-first review and lifecycle state. |
| Picker-driven skill management | UC-6 | Conversion, rename, merge selection. |
| Hide stale or duplicate work | UC-5, UC-7, UC-9 | Finalized and duplicate promotion behavior. |
| CLI mutation boundary | UC-8 | Extension remains orchestration layer. |
| Safe troubleshooting | UC-3, UC-8, Negative Cases | Output channel and refreshable failures. |

## Test Notes

| Scenario | Suggested Test Module | Notes |
|---|---|---|
| UC-1 | `vscode-extension/src/test/suite/homeState.test.ts` | Pure dashboard model assertions. |
| UC-2 | `vscode-extension/src/test/suite/flows.test.ts`, `homeState.test.ts` | Reuse setup/apply flows. |
| UC-3 | `vscode-extension/src/test/suite/learningProgress.test.ts`, `homeState.test.ts` | Reuse progress reducer. |
| UC-4 | `vscode-extension/src/test/suite/promotionReview.test.ts`, `homeState.test.ts` | Promotion lifecycle cards. |
| UC-5 | `vscode-extension/src/test/suite/views.test.ts`, `homeState.test.ts` | Existing pending-commit logic should be shared. |
| UC-6 | `vscode-extension/src/test/suite/localSkills.test.ts`, `flows.test.ts` | Picker filtering and command flow. |
| UC-7 | `vscode-extension/src/test/suite/views.test.ts` | Tree row compactness and icons. |
| UC-8 | `vscode-extension/src/test/suite/flows.test.ts` | Assert commands go through CLI builders. |
| UC-9 | `vscode-extension/src/test/suite/homeState.test.ts` | Table-driven model test. |
