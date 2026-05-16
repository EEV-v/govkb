# VS Code Learning Discovery and Progress - Implementation Plan

Last updated: 2026-05-10

## 0. Existing Code Inventory

| Category | Component | Location | Reuse Strategy |
|---|---|---|---|
| CLI parser | Main argparse surface | `src/govkb/cli.py` | Extend existing `review-memory` parser with inventory and progress flags. |
| CLI wrapper | Public memory-review command | `src/govkb/commands/review_memory.py` | Forward new flags to the packaged Codex adapter; keep subprocess streaming behavior. |
| Codex adapter | Memory-review scheduler | `src/govkb/adapters/codex/bin/codex-memory-review` | Extend `load_sessions`, `DiscoveryStats`, `process`, and report-writing paths rather than creating a parallel review engine. |
| Adapter helpers | Session signal extraction and target discovery | `src/govkb/adapters/codex/memory_review.py` and scheduler-local helpers | Reuse sanitized session parsing and governed target discovery; do not add raw transcript exposure. |
| Extension commands | CLI command builders and runner | `vscode-extension/src/govkbCli.ts` | Add inventory/progress command builders; reuse `runCliCommand` streaming callbacks. |
| Extension flows | Thin orchestration layer | `vscode-extension/src/flows.ts` | Add discovery and bounded review flows that delegate mutation to the CLI. |
| Extension settings | Runtime and review configuration | `vscode-extension/src/settings.ts`, `vscode-extension/package.json` | Add lookback and batch defaults; preserve command/runtime discovery behavior. |
| Extension parsers | JSON payload validators | `vscode-extension/src/jsonParsers.ts` | Add inventory parser; put progress JSONL reducer in a focused new module because it handles streaming state. |
| Extension views | Tree row models | `vscode-extension/src/views/*.ts`, `vscode-extension/src/views/simpleTree.ts` | Add one Learning view using existing `TreeRow` and `SimpleTreeProvider`. |
| Extension activation | View and command registration | `vscode-extension/src/extension.ts`, `vscode-extension/package.json` | Register new commands/view and refresh Learning alongside status, reports, candidates, and promotions. |
| Python tests | Memory review and command wrapper tests | `tests/test_memory_review.py`, `tests/test_review_memory_command.py` | Extend existing direct-function tests; use temp dirs and synthetic JSONL. |
| Extension tests | Command, parser, flow, view, packaging tests | `vscode-extension/src/test/suite/*.test.ts` | Add learning fixtures and assertions to existing test style. |
| Docs | Feature artifacts | `docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/**` | Keep implementation tied to requirements, PoC evidence, and review gate. |

## 0.5. Pre-flight Checklist

| Prerequisite | Status | Owner |
|---|---|---|
| Python 3.11+ available for tests | Required; default `/usr/bin/python3` on this workstation is 3.9, bundled Codex Python 3.12 works | Engineering |
| Node/npm dependencies installed for VS Code extension | Current `npm test` passes | Engineering |
| No raw Codex session transcripts in repo fixtures | Required; use synthetic JSONL only | Engineering |
| Extension remains a CLI orchestrator | Required; TypeScript must not write `.governed/**` or `$CODEX_HOME/**` directly | Engineering |
| Current PoC evidence regenerated | Complete under `poc-evidence/` | Engineering |

## 1. Scope And Boundaries

Implement a first-class VS Code Learning surface backed by explicit GovKB CLI contracts:

- Inventory-only discovery for project sessions and governed memory targets.
- Structured progress events during bounded memory-review batches.
- Extension commands, settings, parsers, and tree rows for inventory, active progress, existing skill updates, new candidates, reports, and next actions.
- Clear dry-run/apply semantics and zero-candidate explanations.

Out of scope:

- Raw transcript display.
- Automatic full historical backfill without user-selected scope.
- Direct TypeScript mutation of governed or assistant-local state.
- New assistant adapters beyond Codex.
- Redesigning candidate promotion flows or governed skill lifecycle.

## 2. Requirements Mapping

| Requirement | Behavior | Location | New/Modify | Notes |
|---|---|---|---|---|
| REQ-VLDP-01 | Show learning readiness and session inventory after setup/apply. | `vscode-extension/src/views/learningView.ts`, `extension.ts` | New view, modify refresh wiring | Combine status capabilities, inventory, reports, candidates, and pending memory summaries. |
| REQ-VLDP-02 | Separate cheap discovery from classification. | `codex-memory-review`, `review_memory.py`, `govkbCli.ts`, `flows.ts` | Modify CLI and extension | Add `--inventory-json`; no nested Codex call in inventory mode. |
| REQ-VLDP-03 | Bounded review scope with lookback and max sessions. | `package.json`, `settings.ts`, `govkbCli.ts`, `flows.ts` | Modify | Add `reviewLookbackDays`; expose batch scope in Learning view and review command. |
| REQ-VLDP-04 | Live per-session progress. | `codex-memory-review`, `learningProgress.ts`, `extension.ts` | Modify plus new module | Add `--progress-jsonl`; parse streamed events while command runs. |
| REQ-VLDP-05 | Explain no visible output. | `learningProgress.ts`, `learningView.ts`, `reports.ts` | New/modify | Use counts and reason fields for skipped, deferred, failed, dry-run previews, and zero candidates. |
| REQ-VLDP-06 | Separate existing skill updates from new candidates. | `learningView.ts`, `statusRows`, `candidateRows` | New/modify | Learning view shows existing updates from progress/report/status separately from Candidates. |
| REQ-VLDP-07 | Dry-run versus apply semantics explicit. | `learningView.ts`, `package.json`, `flows.ts` | New/modify | Keep existing dry-run/apply commands; add Learning batch commands and labels. |
| REQ-VLDP-08 | Open latest report and patch previews. | `reports.ts`, `extension.ts`, `learningView.ts` | Modify | Reuse report open command; add patch preview commands only for paths reported by CLI. |
| REQ-VLDP-09 | Safe structured classifier output. | `codex-memory-review`, `learningProgress.ts`, `jsonParsers.ts` | Modify/new | Emit target skill, lesson/candidate counts, confidence, validation decision, and summaries only. |
| REQ-VLDP-10 | Preserve governance boundaries. | All extension code | Constraint | Mutations continue through CLI only. |
| REQ-VLDP-11 | Batch/resumable backfill. | `codex-memory-review`, `learningView.ts` | Modify/new | Inventory reports selected, processed, deferred, failed, and recommended next scope. |
| REQ-VLDP-12 | Cross-platform behavior and runtime blockers. | `runtimeDiscovery.ts`, `settings.ts`, `flows.ts` | Modify | Surface Python/runtime failures as blockers; do not hard-code macOS-only behavior. |

## 3. Design

### CLI Inventory Contract

Add `govkb review-memory --assistant codex --project-root <root> --inventory-json [--lookback-days N] [--max-sessions N]`.

Adapter behavior:

- Configure review scope and load memory-review state.
- Discover sessions and governed memory targets.
- Do not call nested Codex classification.
- Do not write reports, patches, candidates, skills, local memory, or state advancement.
- Emit one JSON object to stdout.

Planned payload:

```json
{
  "schemaVersion": 1,
  "projectRoot": "/tmp/project",
  "codexHome": "/tmp/codex-home",
  "lookbackDays": 90,
  "maxSessions": 5,
  "sessions": {
    "totalDiscovered": 12,
    "selectedForReview": 5,
    "selectedIndexed": 4,
    "selectedFileOnly": 1,
    "alreadyProcessed": 3,
    "indexedRows": 10,
    "indexedMissingFiles": 1,
    "fileOnlyRecentUnprocessed": 2
  },
  "memoryTargets": [
    {"capabilityId": "project-knowledge-steward", "skillId": "govkb-demo-project-knowledge-steward"}
  ],
  "recommendedBatch": {
    "lookbackDays": 90,
    "maxSessions": 5,
    "dryRun": true,
    "reason": "Review a bounded recent backfill before expanding scope."
  }
}
```

### Progress Event Contract

Add `--progress-jsonl` as an opt-in streaming flag.

When enabled:

- JSONL events go to stdout.
- Human log lines go to stderr and the existing log file.
- Existing report and patch artifacts are still written.
- Progress event payloads exclude raw transcript text and hidden reasoning.

Planned event names:

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

### Extension Learning Surface

Add a new `govkb.learning` view in the GovKB activity container.

Rows should show:

- Selected project and current scope.
- Inventory count: total discovered, selected for review, already processed, missing indexed files.
- Installed memory targets/capabilities count.
- Active run session status and latest structured classifier decision.
- Existing skill update counts.
- New candidate counts.
- Deferred/failed/skipped counts with reasons.
- Latest report and patch preview actions.
- Next actions: Discover Learning, Review Learning Dry Run, Apply Learning Review, Increase Lookback, Refresh Reports.

The first implementation can use settings-backed defaults instead of a full wizard:

- `govkb.reviewLookbackDays`: default 90.
- `govkb.reviewMaxSessions`: change product default to 5 unless tests or packaging constraints require keeping 1 for local VSIX validation.
- `govkb.reviewTimeoutSeconds`: keep current default 180.

## 4. Integration Points

| Integration | Contract |
|---|---|
| `src/govkb/cli.py` | Add argparse flags and pass them through `args`. |
| `src/govkb/commands/review_memory.py` | Forward `--inventory-json` and `--progress-jsonl`; keep `CODEX_HOME` environment behavior. |
| `codex-memory-review` | Implement inventory mode, progress emitter, expanded discovery stats, and safe artifact events. |
| `vscode-extension/src/govkbCli.ts` | Add `reviewMemoryInventoryCommand` and progress-enabled review command builder. |
| `vscode-extension/src/flows.ts` | Add `discoverLearning` and `reviewLearningBatch` flows with streaming progress callbacks. |
| `vscode-extension/src/extension.ts` | Register commands, providers, startup refresh, monitor refresh, and Learning row updates. |
| `vscode-extension/package.json` | Contribute commands, view, title actions, settings, and activation events. |
| `vscode-extension/src/types.ts` | Add inventory, progress event, and learning state types. |
| `vscode-extension/src/jsonParsers.ts` | Parse inventory JSON and reject raw transcript fields. |
| `vscode-extension/src/learningProgress.ts` | Parse JSONL chunks and reduce events into active learning run state. |
| `vscode-extension/src/views/learningView.ts` | Convert status/inventory/progress/reports/candidates into `TreeRow[]`. |

## 5. Application Logic

### Adapter Logic

1. Expand `DiscoveryStats` with `total_discovered`, `already_processed`, `selected_before_limit`, and `selected_after_limit`.
2. Keep `load_sessions(args, state)` as the single selection source.
3. Add `build_inventory_payload(args, state, sessions, discovery, targets, scoped_project_root)`.
4. In `process(args)`, after session and target discovery, exit early for `args.inventory_json`.
5. Add a small progress emitter with `emit(event: str, **payload)` and no-op behavior unless `args.progress_jsonl` is enabled.
6. Emit events around prescreening, classification, candidate validation, deferred/failure handling, patch/report writes, and final summary.
7. Keep state advancement rules unchanged: no state advancement when deferred or failed; dry-run remains report/patch preview only.

### Extension Logic

1. `discoverLearning` runs inventory command, parses JSON, updates Learning rows.
2. `reviewLearningBatch` runs dry-run/apply command with explicit lookback, max sessions, timeout, and `--progress-jsonl`.
3. Stdout streaming is parsed by `learningProgress.ts`; stderr remains human-readable output channel text.
4. On completion, refresh reports, candidates, promotions, and status as existing commands do.
5. If no candidates are found, Learning rows still show reviewed/skipped/deferred/existing update counts and report links.
6. If runtime or Python import fails, show a blocker with the exact executable and stderr summary.

## 6. Data Consistency And Safety

- Inventory mode is read-only and must not update state, reports, patches, candidates, skills, or memory files.
- Progress mode must not expose raw session transcript text, sanitized prompts, or hidden reasoning in event payloads.
- Extension state is non-authoritative; it can cache the latest inventory/progress rows but cannot write governed or assistant-local files.
- Existing report and patch files remain the durable audit surface.
- Use temp dirs in tests for `CODEX_HOME`, project roots, session files, report dirs, state dirs, and generated patches.
- Existing `--verbose` sanitized classifier input behavior remains opt-in and log-file based.

## 7. Testing Strategy

| Test Type | Location | Coverage |
|---|---|---|
| Python smoke/use-case scaffold | `tests/test_vscode_learning_discovery_progress_smoke.py` | Inventory JSON shape and no-classifier behavior for UC-1/UC-2. |
| Python regression scaffold | `tests/test_vscode_learning_discovery_progress_use_cases.py` | Progress events, dry-run/apply summaries, deferred/failure reasons, zero-candidate explanations. |
| Python helper | `tests/vscode_learning_discovery_progress_test_helper.py` | Synthetic project/session fixtures and adapter patching helpers. |
| Existing Python tests | `tests/test_memory_review.py` | Expanded `DiscoveryStats`, adapter progress emission, session filtering, deferred state behavior. |
| Command wrapper tests | `tests/test_review_memory_command.py` | Forward `--inventory-json`, `--progress-jsonl`, lookback, timeout, max sessions, and no-auto-promote. |
| Extension command tests | `vscode-extension/src/test/suite/govkbCli.test.ts` | Inventory/progress command builders and lookback settings. |
| Extension parser tests | `vscode-extension/src/test/suite/jsonParsers.test.ts`, new `learningProgress.test.ts` | Inventory JSON validation, JSONL chunk parsing, raw transcript rejection, run state reduction. |
| Extension flow tests | `vscode-extension/src/test/suite/flows.test.ts` | Discover Learning and Review Learning Batch command order, progress callback updates, refresh sequence. |
| Extension view tests | `vscode-extension/src/test/suite/views.test.ts` | Learning rows for empty, inventory-loaded, active, zero-candidate, deferred, failed, existing-update, and report-link states. |
| Packaging tests | `vscode-extension/src/test/suite/packaging.test.ts` | New commands, settings, activation events, and `govkb.learning` view contribution. |
| Extension host smoke | `vscode-extension/src/test/host/suite/index.ts` | New commands are contributed and extension activates with Learning view. |

## 8. Verification Commands

| Command | Working Dir | Purpose | Preconditions |
|---|---|---|---|
| `PYTHONPATH=src <python3.11+> -m govkb.cli review-memory --help` | `/Users/vasilevevgeny/code/govkb` | Verify new public flags are visible. | Python 3.11+. |
| `PYTHONPATH=src <python3.11+> -m unittest tests.test_review_memory_command tests.test_memory_review -v` | `/Users/vasilevevgeny/code/govkb` | Target adapter and wrapper tests. | Python 3.11+. |
| `PYTHONPATH=src <python3.11+> -m unittest tests.test_vscode_learning_discovery_progress_smoke tests.test_vscode_learning_discovery_progress_use_cases -v` | `/Users/vasilevevgeny/code/govkb` | Run new scaffolded feature tests. | Python 3.11+. |
| `PYTHONPATH=src <python3.11+> -m unittest discover -s tests -v` | `/Users/vasilevevgeny/code/govkb` | Full Python regression. | Python 3.11+. |
| `npm test` | `/Users/vasilevevgeny/code/govkb/vscode-extension` | Compile and run extension unit tests. | Node/npm dependencies installed. |
| `npm run test:host` | `/Users/vasilevevgeny/code/govkb/vscode-extension` | Extension-host smoke. | VS Code test executable available. |
| `./docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/regenerate-poc-data.sh` | `/Users/vasilevevgeny/code/govkb` | Reproduce PoC baseline after changes. | Python 3.11+, npm. |

## 9. Implementation Phases

### Phase 0 - Shape And Contracts

Scope:

- Add Python/TypeScript test scaffolds and sanitized fixtures first.
- Lock CLI payload/event names and extension type names.

Files:

- `tests/vscode_learning_discovery_progress_test_helper.py`
- `tests/test_vscode_learning_discovery_progress_smoke.py`
- `tests/test_vscode_learning_discovery_progress_use_cases.py`
- `vscode-extension/src/test/fixtures/learning-inventory.sample.json`
- `vscode-extension/src/test/fixtures/learning-progress.sample.jsonl`
- `vscode-extension/src/types.ts`

Verify:

- New tests import or skip cleanly.
- Existing tests remain green.

Rollback:

- Remove scaffold files and fixture references; no runtime behavior changes in this phase.

### Phase 1 - Core Behavior

Scope:

- Implement inventory payload and progress event emission inside the Codex adapter.
- Add CLI parser/wrapper forwarding.

Files:

- `src/govkb/cli.py`
- `src/govkb/commands/review_memory.py`
- `src/govkb/adapters/codex/bin/codex-memory-review`
- `tests/test_review_memory_command.py`
- `tests/test_memory_review.py`
- New feature Python tests from Phase 0.

Verify:

- CLI help includes `--inventory-json` and `--progress-jsonl`.
- Inventory mode exits 0 with JSON and does not call classifier.
- Progress mode emits JSONL events for success, skipped, deferred, and failed paths.

Rollback:

- Remove new flags and adapter helper code; keep old `review-memory` dry-run/apply behavior unchanged.

### Phase 2 - Command Or Adapter Integration

Scope:

- Add extension command builders, settings, parsers, and progress reducer.
- Add flow-level tests for discovery and bounded review.

Files:

- `vscode-extension/src/govkbCli.ts`
- `vscode-extension/src/settings.ts`
- `vscode-extension/src/jsonParsers.ts`
- `vscode-extension/src/learningProgress.ts`
- `vscode-extension/src/flows.ts`
- `vscode-extension/src/test/suite/govkbCli.test.ts`
- `vscode-extension/src/test/suite/settings.test.ts`
- `vscode-extension/src/test/suite/jsonParsers.test.ts`
- `vscode-extension/src/test/suite/learningProgress.test.ts`
- `vscode-extension/src/test/suite/flows.test.ts`

Verify:

- `npm test` passes.
- Parser tests reject raw transcript fields in progress/inventory payloads.

Rollback:

- Remove new settings, command builders, parser exports, and flow functions; existing dry-run/apply commands remain available.

### Phase 3 - End-to-End Or Workflow Behavior

Scope:

- Add Learning view, command registration, startup/monitor refresh integration, and report/candidate/status refresh sequencing.

Files:

- `vscode-extension/src/views/learningView.ts`
- `vscode-extension/src/extension.ts`
- `vscode-extension/package.json`
- `vscode-extension/src/test/suite/views.test.ts`
- `vscode-extension/src/test/suite/packaging.test.ts`
- `vscode-extension/src/test/host/suite/index.ts`

Verify:

- `npm test` passes.
- `npm run test:host` passes.
- Manual VS Code check shows Learning view and commands.

Rollback:

- Remove `govkb.learning` contribution and command registrations; leave CLI inventory/progress available for non-extension use.

### Phase 4 - Docs, Packaging, Or Optional UI

Scope:

- Update feature docs and extension user-facing descriptions.
- Reinstall or package VSIX only after tests pass.

Files:

- `README.md` or `docs/README.md` if extension usage docs need an update.
- `docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/poc-output.md`
- `docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/poc-parity-review.md` in later cookbook phase.

Verify:

- Full Python tests.
- Full extension unit tests.
- Extension-host smoke.
- Manual VS Code smoke against a disposable project or Clearing only with explicit user confirmation.

Rollback:

- Revert docs/package metadata for the feature and reinstall the previous VSIX if manual extension testing exposes a blocker.

## 10. Rollback Plan

- CLI flags are additive. If extension UI has issues, disable/hide new extension commands while leaving CLI inventory/progress available for debugging.
- If progress stream corrupts output, keep `--progress-jsonl` off by default and fall back to current stdout/stderr logs and report summaries.
- If inventory counts are wrong, remove the Learning inventory refresh and use existing status/reports/candidates views until adapter counts are corrected.
- If extension refresh loops cause noise, set monitor interval to disabled by default and keep manual refresh commands.
- No rollback step should delete user `.governed/**`, `$CODEX_HOME/**`, session files, reports, or local memory.

## 11. Open Questions

| Question | Proposed Decision | Blocking? |
|---|---|---|
| Should progress JSONL go to stdout, stderr, or a file? | Stdout for JSONL when `--progress-jsonl` is enabled; human logs move to stderr in that mode. | No; plan adopts this contract. |
| What default lookback should the extension use? | 90 days for discovery, with explicit setting and visible scope. | No |
| What default max sessions should the extension use? | 5 for product UX, unless packaging validation requires keeping 1 temporarily. | No |
| Should dry-run create non-mutating candidate preview folders? | No in this feature; show report/patch previews and existing update counts instead. | No |
| Should apply mode over batch size greater than one require confirmation? | Yes in UI flow, after Phase 3 if not blocking unit behavior. | No |

## 12. Ready Checklist

| Item | Status |
|---|---|
| Requirements mapped to implementation locations | Ready |
| PoC assertions carried into phases | Ready |
| CLI contract is additive and testable | Ready |
| Extension remains a CLI orchestrator | Ready |
| Raw transcript leakage is explicitly blocked | Ready |
| Tests use temp dirs and sanitized fixtures | Ready |
| Verification commands include full Python and extension suites | Ready |
| Rollback is explicit by phase | Ready |
