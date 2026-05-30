# Governed Learning Improvements - Use Cases

Last updated: 2026-05-29

## Scope

GovKB CLI and automation improvements for proposal review, memory-review health, incremental review quality, capability maturity, and VS Code freshness. Clearing is a consumer fixture, not the owner of implementation code.

Feature type: `CLI`, `Automation`, and later optional `VSCodeExtension`.

## Actors

| Actor | Goal |
|---|---|
| GovKB maintainer | Improve governed learning reliability without weakening safety gates. |
| Project maintainer | Understand proposal queues, health, and skill freshness quickly. |
| VS Code user | See whether visible GovKB state is stale or current. |

## Background

Given a GovKB checkout with existing CLI commands
And a project `.governed/` package with capabilities and optional staged proposals
And a Codex home with memory-review reports and state
And reports must not persist raw session transcript rows

## Scenarios

### UC-1: Proposal Queue Groups Similar Work @smoke

Given the proposal queue contains two DVCA payout runbook proposals with similar target capability and output intent
And the queue contains unrelated Golden lineage and mirror diagnostic proposals
When the maintainer runs the proposal review report
Then the report groups the similar DVCA proposals together
And the report keeps unrelated proposals in separate groups
And each group shows target capability, proposal ids, output paths, confidence, safety class, and recommended next action

### UC-2: Proposal Quality Warnings Are Advisory @regression

Given a staged runbook proposal has weak or placeholder verification
And a staged script proposal has `safety_class = "mutating_with_dry_run"`
When the maintainer runs the proposal review report
Then the docs-only proposal receives a warning to add review evidence when needed
And the script proposal must show dry-run or preview behavior, help or compile verification, mutation class, and audit/log expectations
And no proposal files are changed by the report command

### UC-3: Memory Review Health Is Visible In One Report @smoke

Given a project has a memory-review cron entry
And the latest memory-review report has a completed or failed status
And status JSON can identify repo and applied materialization revisions
When the maintainer runs the memory-review health report
Then the report shows cron presence, daemon state when available, latest run id, latest report path, run status, reviewed/applied/staged/rejected/proposal counts, state advancement timestamp, selected backlog count, proposal queue count, applied revision, and repo revision
And unavailable local checks are reported as unavailable rather than crashing

### UC-4: Self-Generated Session Tails Are Skipped @regression

Given a processed session has new rows after `reviewAfter`
And the new rows are only assistant progress messages, tool-call records, token counts, or memory-review report output
When memory review selects sessions for classification
Then the session is not sent to the classifier
And the report or inventory records a skip reason
And future user-authored rows after that marker remain eligible

### UC-5: User Decisions After A Processed Marker Are Still Reviewed @regression

Given a processed session has new rows after `reviewAfter`
And the new rows include a user decision such as approving a proposal direction or changing scope
When memory review selects sessions for classification
Then only the rows after `reviewAfter` are sanitized and sent to the classifier
And the report includes the session with the `reviewAfter` timestamp

### UC-6: Capability Maturity Score Explains Next Investment @regression

Given one capability has only long-term memory
And one capability has memory plus runbooks
And one capability has runbooks, scripts, and tests
When the maintainer runs the maturity report
Then each capability receives a level from L1 to L5
And the report explains the missing artifact type needed for the next level
And staged proposals can be counted as pending maturity improvements without being treated as applied files

### UC-7: VS Code Freshness Check Identifies Stale Layers @regression

Given the extension package version is older than the repo package version
Or the installed materialization revision differs from the project repo revision
When the maintainer runs the VS Code/GovKB doctor check
Then the report identifies which layer is stale: extension package, CLI path, materialized skills, or governed repo
And it prints the exact reinstall or apply command needed
And it does not mutate VS Code or project state

## Negative And Governance Cases

- Proposal report commands must not apply, approve, reject, or delete proposals.
- Memory-review health commands must not run classification.
- Tests must use temp project roots and disposable Codex homes instead of user-home session logs.
- Raw transcript content must not appear in docs, JSON report fixtures, or committed test fixtures.

## Traceability

| Requirement | Scenario(s) | Coverage |
|---|---|---|
| AC1 | UC-1, UC-2 | Full |
| AC2 | UC-3 | Full |
| AC3 | UC-4, UC-5 | Full |
| AC4 | UC-2 | Full |
| AC5 | UC-6 | Full |
| AC6 | UC-7 | Full |
| AC7 | UC-1 through UC-7 | Full |

## Test Notes

| Scenario | Suggested Test Module | Notes |
|---|---|---|
| UC-1 | `tests/test_governed_learning_improvements_use_cases.py` | Temp project with staged proposal fixtures. |
| UC-2 | `tests/test_governed_learning_improvements_use_cases.py` | Assert warnings and read-only behavior. |
| UC-3 | `tests/test_governed_learning_improvements_use_cases.py` | Temp Codex home with report/state fixtures. |
| UC-4 | `tests/test_memory_review.py` | Extend existing session selection tests. |
| UC-5 | `tests/test_memory_review.py` | Mixed tail with user row. |
| UC-6 | `tests/test_governed_learning_improvements_use_cases.py` | Temp capability tree. |
| UC-7 | `tests/test_governed_learning_improvements_use_cases.py` | Mock package/status metadata. |

