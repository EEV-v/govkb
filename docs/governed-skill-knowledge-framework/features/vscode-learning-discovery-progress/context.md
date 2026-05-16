# VS Code Learning Discovery and Progress - Implementation Context

Last updated: 2026-05-10

## Objective

Add a learning-focused VS Code experience for GovKB that makes session discovery, memory-review scope, live per-session progress, dry-run/apply semantics, existing skill updates, and new capability candidates visible and actionable.

## Source Artifacts

- `docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/business.md`
- `README.md`
- `docs/README.md`
- `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/context.md`
- `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/use-cases.md`
- `src/govkb/cli.py`
- `src/govkb/commands/review_memory.py`
- `src/govkb/adapters/codex/bin/codex-memory-review`
- `vscode-extension/src/extension.ts`
- `vscode-extension/src/govkbCli.ts`
- `vscode-extension/src/flows.ts`
- `vscode-extension/src/views/candidatesView.ts`
- `vscode-extension/src/views/reportsView.ts`
- `vscode-extension/src/types.ts`
- `vscode-extension/src/settings.ts`
- `tests/test_review_memory_command.py`
- `tests/test_memory_review.py`
- `vscode-extension/src/test/suite/govkbCli.test.ts`
- `vscode-extension/src/test/suite/flows.test.ts`
- `vscode-extension/src/test/suite/views.test.ts`

No repo-local instruction file was found under the checked names `AGENTS.md`, `.github/copilot-instructions.md`, `CLAUDE.md`, or `.cursorrules`; apply the active session instructions.

## Existing Patterns

| Pattern Type | Existing Example | Location | Reuse? |
|---|---|---|---|
| CLI-owned behavior | Extension builds argument arrays and spawns GovKB commands | `vscode-extension/src/govkbCli.ts` | Reuse. Add command builders for discovery/progress flags. |
| Thin extension flows | TypeScript orchestration delegates to CLI and parses JSON | `vscode-extension/src/flows.ts` | Reuse. Add learning discovery flow without direct file mutation. |
| Workspace trust gate | Mutating commands call `requireTrusted` before running | `vscode-extension/src/extension.ts` | Reuse for review/apply; inventory can be read-only but still executes local CLI. |
| Status view | Tree rows summarize parsed status payload | `vscode-extension/src/views/statusView.ts` | Reuse pattern for Learning view rows. |
| Candidate view | Lists `.governed/candidates` via `govkb candidates list --json` | `vscode-extension/src/views/candidatesView.ts` | Keep but clarify that candidates are only one learning output. |
| Report view | Summarizes memory-review markdown reports without raw transcript leakage | `vscode-extension/src/reports.ts`, `vscode-extension/src/views/reportsView.ts` | Reuse and link from Learning view. |
| Review CLI wrapper | Public CLI forwards `review-memory` flags to packaged adapter | `src/govkb/commands/review_memory.py` | Extend with inventory/progress flags. |
| Review session selection | Adapter loads Codex session files/index, applies lookback and max-session limits | `src/govkb/adapters/codex/bin/codex-memory-review` | Reuse; expose inventory before classification. |
| Review report | Adapter writes report, applied patch, and staged patch | `src/govkb/adapters/codex/bin/codex-memory-review` | Reuse; add structured progress stream and possibly JSON report metadata. |
| Python tests | Direct command and adapter tests use `unittest`, temp dirs, and patching | `tests/test_review_memory_command.py`, `tests/test_memory_review.py` | Reuse. |
| Extension tests | Node tests cover command builders, flows, parsing, and view rows | `vscode-extension/src/test/suite/*.test.ts` | Reuse. |

## Proposed New Components

| Component | Purpose | Notes |
|---|---|---|
| `govkb review-memory --inventory-json` or equivalent | Cheap project-scoped session inventory without AI classification | Should report total project sessions, selectable sessions by lookback, already processed count, recent count, missing indexed files, and recommended batch. |
| `govkb review-memory --progress-jsonl` | Structured per-session event stream while review runs | Events should be safe for UI and exclude raw transcript content. |
| `vscode-extension/src/views/learningView.ts` | Tree rows for inventory, active run progress, existing updates, candidates, skipped/deferred/failed counts, and next actions | Replaces the impression that Candidates is the only learning surface. |
| `vscode-extension/src/learningProgress.ts` | Parse progress JSONL events and maintain active run state | Keep parser deterministic and testable. |
| `vscode-extension/src/learningInventory.ts` | Parse inventory payload and convert to UI model | Use fixtures in tests. |
| New extension command `govkb.discoverLearning` | Run cheap inventory and refresh Learning view | Should not run classifier. |
| New extension command `govkb.reviewLearningBatch` | Prompt for lookback/max-sessions/mode and run bounded review | Can start as settings-backed defaults if QuickPick UX is deferred. |
| Settings for learning review scope | Defaults for lookback and batch size | Existing `reviewMaxSessions` default is 1; feature should make this visible and user-controlled. |
| Tests for inventory/progress | Python and TypeScript fixtures | Must avoid raw transcripts. |

## Data Flow

1. Extension resolves selected project root and GovKB runtime.
2. Extension runs a cheap inventory command.
3. CLI adapter scans session metadata and project roots but does not call nested Codex.
4. Extension renders discovered project session counts, scope choices, and likely next actions.
5. User starts a bounded dry-run or apply batch.
6. CLI emits progress JSONL events while also writing existing report/patch artifacts.
7. Extension parses events and updates Learning rows plus output channel text.
8. On completion, extension refreshes reports, candidates, promotions, and status.

## Domain Entities

| Entity | Fields | Notes |
|---|---|---|
| Learning inventory | project root, codex home, lookback windows, total sessions, selected sessions, already processed, indexed missing files, file-only count | No AI classification. |
| Review batch | dry-run/apply, lookback days, max sessions, timeout, classifier model/reasoning, selected sessions | User-controllable scope. |
| Session progress event | run id, session id, thread name, updated at, status, message, target skills, counts | Must not include raw transcript. |
| Classifier decision | target skill, memory section, lesson summary, confidence, validation decision, semantic candidate summary | Structured output only. |
| Learning outcome | existing skill update, staged patch, new capability candidate, skipped, rejected, deferred, failed | Separate candidates from existing capability memory updates. |

## Command Map

| Task | Command | Working Dir | Preconditions |
|---|---|---|---|
| Run Python tests | `python3 -m unittest discover -s tests -v` | `/Users/vasilevevgeny/code/govkb` | Python can import `govkb`. |
| Verify CLI help | `PYTHONPATH=src python3 -m govkb.cli --help` | `/Users/vasilevevgeny/code/govkb` | Source checkout. |
| Current memory dry-run | `PYTHONPATH=src python3 -m govkb.cli review-memory --assistant codex --project-root <project> --dry-run --max-sessions 1 --codex-timeout 180` | `/Users/vasilevevgeny/code/govkb` | Project has governed package and Codex home. |
| Proposed inventory check | `PYTHONPATH=src python3 -m govkb.cli review-memory --assistant codex --project-root <project> --inventory-json --lookback-days 180` | `/Users/vasilevevgeny/code/govkb` | To be implemented. No classifier required. |
| Proposed progress run | `PYTHONPATH=src python3 -m govkb.cli review-memory --assistant codex --project-root <project> --dry-run --lookback-days 180 --max-sessions 5 --progress-jsonl --codex-timeout 180` | `/Users/vasilevevgeny/code/govkb` | To be implemented. |
| Run extension unit tests | `npm test` | `/Users/vasilevevgeny/code/govkb/vscode-extension` | `npm install` completed. |
| Run extension host smoke | `npm run test:host` | `/Users/vasilevevgeny/code/govkb/vscode-extension` | VS Code executable available. |

## APIs And CLI Surface

Current CLI:

- `govkb review-memory --assistant codex --project-root <project> [--dry-run] [--lookback-days N] [--max-sessions N] [--codex-timeout N]`

Needed additions:

- Inventory mode that exits after discovery and emits JSON.
- Progress event mode that emits newline-delimited JSON events during review.
- Public wrapper flags in `src/govkb/cli.py` and forwarding in `src/govkb/commands/review_memory.py`.
- Extension command builders and parsers for those payloads.

Candidate event names should be stable enough for UI/tests, for example:

- `run_started`
- `inventory`
- `session_selected`
- `session_skipped`
- `session_classifying`
- `session_classified`
- `session_deferred`
- `session_failed`
- `artifact_written`
- `run_finished`

## Storage

| Location | Purpose | Ownership |
|---|---|---|
| `<project>/.governed/**` | Governed source package, candidates, reports | CLI-owned mutations only. |
| `$CODEX_HOME/skills/**` | Materialized Codex skills and local memory | CLI-owned derived output. |
| `$CODEX_HOME/memories/govkb/projects/<project-id>/codex-memory-review/**` | Review state, reports, patches, logs | CLI-owned derived output. |
| VS Code workspace state | Remembered selected project root and active UI state | Extension-owned, non-authoritative. |
| Extension output channel | Live diagnostics | Ephemeral. |

## Security And Governance

- Do not store raw session transcripts in repo artifacts or extension state.
- Do not show raw transcripts by default.
- Do not expose hidden chain-of-thought or model reasoning.
- Show safe structured classifier results: lesson summary, confidence, target skill, decision, and rationale already present in report artifacts.
- Preserve dry-run/apply distinction.
- Preserve CLI as the only writer for `.governed/**` and `$CODEX_HOME/**`.
- Treat Codex auth failures, usage limits, connectivity errors, and timeouts as explicit deferred/error outcomes.

## Tests

| Area | Test Location | Coverage |
|---|---|---|
| Inventory CLI | `tests/test_memory_review.py`, `tests/test_review_memory_command.py` | Session counts, project filtering, lookback, processed state, no classifier invocation. |
| Progress CLI | `tests/test_memory_review.py` | JSONL events for selected, skipped, classifying, classified, deferred, failed, artifacts, finished. |
| Extension command builders | `vscode-extension/src/test/suite/govkbCli.test.ts` | Inventory and progress flags, lookback/max-session settings. |
| Extension parser | `vscode-extension/src/test/suite/jsonParsers.test.ts` or new parser tests | Inventory payload and JSONL progress events. |
| Extension flows | `vscode-extension/src/test/suite/flows.test.ts` | Discover learning, bounded dry-run/apply flow, refresh behavior. |
| Extension views | `vscode-extension/src/test/suite/views.test.ts` | Learning rows distinguish inventory, existing updates, candidates, skipped/deferred/failed. |

## Observability

- Output channel should keep the exact command and exit code.
- Learning view should expose live progress independent of output channel.
- Reports remain durable audit artifacts.
- Progress events should include report and patch paths when available.
- If a run ends with zero candidates, the UI should show reviewed/skipped/applied/staged/deferred counts and explanation.

## Open Questions

| # | Question | Blocking? | Owner |
|---|---|---|---|
| 1 | Should inventory mode be a subcommand, e.g. `govkb review-memory inventory`, or a flag on `review-memory`? | Yes | Engineering |
| 2 | Should progress JSONL be emitted to stdout, stderr, or an explicit file to avoid mixing with human logs? | Yes | Engineering |
| 3 | Should dry-run candidate previews be persisted as a non-mutating sidecar artifact, or remain report-only until apply? | No | Product/Governance |
| 4 | What default lookback should the extension recommend for first run: 30, 90, or 180 days? | No | Product |
| 5 | Should apply-mode review require an extra confirmation when batch size is greater than one? | No | Product/Governance |

## Assumptions

| # | Assumption | Risk If Wrong |
|---|---|---|
| 1 | Users need inventory before classifier work more than they need one-click full backfill. | UI may still feel too manual for small projects. |
| 2 | JSONL events are sufficient for live VS Code progress. | A file-based event stream may be needed if stdout must remain human-readable. |
| 3 | Existing report/patch artifacts remain the durable audit surface. | Additional durable run metadata may be needed for better restart/resume UX. |
| 4 | The extension can keep a single Learning view rather than adding many separate views. | Navigation may become crowded if learning outcomes grow. |

## Traceability

| Context Section | business.md Source |
|---|---|
| Objective | Objective, LD-01 through LD-12 |
| Proposed New Components | LD-02, LD-03, LD-04, LD-06, LD-08 |
| Data Flow | LD-02, LD-04, LD-11 |
| Domain Entities | LD-01, LD-04, LD-05, LD-06, LD-09 |
| APIs And CLI Surface | LD-02, LD-03, LD-04 |
| Security And Governance | LD-09, LD-10, Non-Goals |
| Tests | Success Criteria |
| Observability | LD-04, LD-05, LD-08 |
