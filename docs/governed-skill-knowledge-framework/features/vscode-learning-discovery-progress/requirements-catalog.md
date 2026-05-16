# VS Code Learning Discovery and Progress - Requirements Catalog

Last updated: 2026-05-10

| ID | Requirement | Source | PoC Assertion | Scenario(s) | Status |
|---|---|---|---|---|---|
| REQ-VLDP-01 | The extension must show useful learning readiness after setup/apply, including installed capabilities and session inventory. | LD-01 | Existing status exposes capabilities and install state, but there is no learning inventory payload or Learning view yet. | UC-1, UC-5 | Baseline gap |
| REQ-VLDP-02 | The extension must separate cheap session discovery from AI classification. | LD-02 | Current `govkb review-memory` help has no inventory-only flag; `load_sessions` can select sessions without classification and can be exposed as a CLI contract. | UC-2 | Feasible, missing CLI surface |
| REQ-VLDP-03 | Users must be able to choose bounded review scope with lookback and max sessions. | LD-03 | CLI supports `--lookback-days` and `--max-sessions`; extension command builder currently forwards `--max-sessions` but not lookback selection. | UC-3, UC-9 | Partially covered |
| REQ-VLDP-04 | Long-running review must expose live per-session progress. | LD-04 | Current extension streams stdout/stderr to the output channel, but current CLI emits no structured per-session JSONL progress contract. | UC-4, UC-7 | Baseline gap |
| REQ-VLDP-05 | Review output must explain zero visible output reasons. | LD-05 | Current Python tests prove deferred classifier reasons are captured in reports; extension summarizes report counts but does not expose a zero-candidate explanation model. | UC-5, UC-6, UC-7 | Partially covered |
| REQ-VLDP-06 | Existing skill memory updates must be separated from new capability candidates. | LD-06 | Status exposes pending local memory and candidates list is separate; current views do not combine those into one Learning surface. | UC-5 | Partially covered |
| REQ-VLDP-07 | Dry-run versus apply semantics must be explicit. | LD-07 | CLI has `--dry-run`; extension has separate dry-run/apply commands; current Candidates view still uses dry-run as the empty-list discovery action without explaining report-only output. | UC-3, UC-6 | Partially covered |
| REQ-VLDP-08 | Users must be able to open latest reports and patch previews from learning UX. | LD-08 | Reports view can open report summaries; patch previews exist on disk but are not surfaced from a Learning view. | UC-5, UC-6 | Partially covered |
| REQ-VLDP-09 | The extension must show safe structured classifier output without raw transcripts. | LD-09 | Report parser rejects raw transcript summaries; no parser/model exists yet for structured progress classifier decisions. | UC-8 | Partially covered |
| REQ-VLDP-10 | TypeScript extension code must not mutate `.governed/**` or `$CODEX_HOME/**` directly. | LD-10 | Current extension delegates setup, apply, candidates, promotions, and memory review to GovKB CLI commands. | UC-2, UC-6 | Covered by existing pattern |
| REQ-VLDP-11 | Backfill must be batchable and resumable when full review cannot finish in one run. | LD-11 | CLI has `--max-sessions`, processed-session state, and deferred-session behavior; extension does not expose reviewed/deferred/remaining session progress. | UC-3, UC-7, UC-9 | Partially covered |
| REQ-VLDP-12 | UX must be cross-platform in behavior with explicit runtime discovery/settings. | LD-12 | Extension has runtime discovery for GovKB command and settings for executable paths; Python CLI requires 3.11+, so the UI must surface interpreter/runtime blockers clearly. | UC-7, Negative And Governance Cases | Partially covered |

## PoC Status Legend

| Status | Meaning |
|---|---|
| Covered by existing pattern | Current code already demonstrates the implementation approach. |
| Partially covered | Current code has reusable pieces, but the user-visible contract is incomplete. |
| Feasible, missing CLI surface | Current internals can support the behavior, but no public CLI/API exists yet. |
| Baseline gap | The behavior is absent and needs a planned implementation step. |
