# VS Code Learning Discovery and Progress - PoC Parity Review

Last updated: 2026-05-12

## Verdict

Ready for Merge: Yes

## Summary

The implementation matches the accepted PoC direction. The previous gaps are now backed by executable behavior:

- `govkb review-memory` exposes `--inventory-json` and `--progress-jsonl`.
- Inventory mode is read-only and does not classify sessions.
- Progress mode emits safe JSONL lifecycle events.
- The VS Code extension has Learning commands, parsers, state reduction, and a Learning view.
- Existing skill updates, new capability candidates, reports, dry-run, and apply actions are visible as separate concepts.
- Accepted promotion worktrees can now be explicitly applied into the active project without committing, and duplicate equivalent promotion rows are compacted in the VS Code Promotions view.

## Requirement Parity

| Requirement | PoC Assertion | Implementation Evidence | Result | Notes |
|---|---|---|---|---|
| REQ-VLDP-01 | A1, A7 | `vscode-extension/src/views/learningView.ts`, `vscode-extension/src/extension.ts`, `views.test.ts` | PASS | Learning readiness and inventory rows are now available. |
| REQ-VLDP-02 | A2 | `--inventory-json`, `test_packaged_scheduler_inventory_json_is_read_only` | PASS | Inventory does not call classifier or write review artifacts. |
| REQ-VLDP-03 | A1, A5 | `reviewLookbackDays`, `reviewMaxSessions`, `reviewMemoryInventoryCommand`, `reviewMemoryProgressCommand` | PASS | Extension now passes lookback and max sessions. |
| REQ-VLDP-04 | A7 | `--progress-jsonl`, `learningProgress.ts`, `test_packaged_scheduler_progress_jsonl_reports_session_lifecycle` | PASS | Live session lifecycle is machine-readable. |
| REQ-VLDP-05 | A3, A6 | Deferred/failure tests, `learningRows`, report summaries | PASS | Zero-candidate and deferred paths have separate counts/reasons. |
| REQ-VLDP-06 | A6, A7 | `learningRows` separates existing updates and new candidates | PASS | Existing memory promotions are not collapsed into candidate count. |
| REQ-VLDP-07 | A1, A5 | Existing dry-run/apply commands plus `reviewLearningDryRun` and `reviewLearningApply` | PASS | Dry-run/apply are separate commands and row actions. |
| REQ-VLDP-08 | A6 | `Latest report` Learning row reuses report open commands | PASS | Patch preview paths are emitted as artifacts; report opening is implemented. |
| REQ-VLDP-09 | A6, A7 | Progress parser ignores raw transcript fields; report parser still rejects transcript summaries | PASS | Progress payloads include structured counts and omit transcript text. |
| REQ-VLDP-10 | A5 | Extension still delegates all filesystem mutations to CLI commands | PASS | TypeScript stores UI state only. |
| REQ-VLDP-11 | A2, A3 | Inventory counts, progress run summary, deferred state tests | PASS | Batch progress and retryable failures are visible. |
| REQ-VLDP-12 | A5 | Runtime settings and blocker paths preserved; Python 3.11+ documented in evidence | PASS | Cross-platform runtime behavior is setting-driven; no macOS-only UI path was added. |

## Scenario Parity

| Scenario | Test/Verification | Result | Notes |
|---|---|---|---|
| UC-1 | `learningRows show discovery action before inventory loads`; extension manifest contributes `govkb.learning` | PASS | First setup can show a Learning surface before candidates exist. |
| UC-2 | `test_packaged_scheduler_inventory_json_is_read_only`; `discoverLearning parses inventory payload` | PASS | Discovery is read-only and classifier-free. |
| UC-3 | `memory review inventory command uses read-only discovery flags`; `runLearningReviewBatch reduces progress stream` | PASS | Bounded review uses lookback, max sessions, timeout, and progress mode. |
| UC-4 | `parseLearningProgressChunk handles chunked JSONL events`; adapter progress lifecycle test | PASS | Per-session progress is structured and chunk-safe. |
| UC-5 | `learningRows separate existing updates from candidates` | PASS | Existing updates and new candidates render separately. |
| UC-6 | Learning dry-run/apply commands in package manifest and extension command registration | PASS | Semantics are explicit at command and view level. |
| UC-7 | Existing deferred timeout/usage/transport tests plus progress deferred event support | PASS | Retryable failures remain reportable and can be rendered. |
| UC-8 | `parseLearningProgressChunk ignores raw transcript events` | PASS | Unsafe progress fields are ignored. |
| UC-9 | Inventory fixture and parser cover lookback/max-session scope | PASS | Interactive scope selection remains a post-merge UX enhancement. |

## Command Evidence

| Command | Working Dir | Result | Evidence |
|---|---|---|---|
| `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli review-memory --help` | `/Users/vasilevevgeny/code/govkb` | PASS | Help includes `--inventory-json` and `--progress-jsonl`. |
| `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_review_memory_command tests.test_memory_review -v` | `/Users/vasilevevgeny/code/govkb` | PASS | 29 tests passed. |
| `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests` | `/Users/vasilevevgeny/code/govkb` | PASS | 143 tests passed, 22 skipped scaffold tests. |
| `npm test` | `/Users/vasilevevgeny/code/govkb/vscode-extension` | PASS | 85 tests passed. |
| `npm run test:host` | `/Users/vasilevevgeny/code/govkb/vscode-extension` | PASS | Extension host exited 0. |
| `./docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/regenerate-poc-data.sh` | `/Users/vasilevevgeny/code/govkb` | PASS | Refreshed PoC evidence under `poc-evidence/`. |
| Disposable temp-project inventory command | `/Users/vasilevevgeny/code/govkb` | PASS | Returned JSON inventory and routed index-missing log to stderr. |
| `scripts/govkb-dev validate /Users/vasilevevgeny/code/Etna/Clearing --strict --json` | `/Users/vasilevevgeny/code/govkb` | PASS | Clearing strict validation returned no errors or warnings. |
| `scripts/govkb-dev promote /Users/vasilevevgeny/code/Etna/Clearing --codex-home /Users/vasilevevgeny/.codex --auto` | `/Users/vasilevevgeny/code/govkb` | PASS | Duplicate prevention reused an existing equivalent isolated promotion instead of creating another worktree. |

## Deviations

| Deviation | Approved? | Reason | Follow-up |
|---|---|---|---|
| Inventory mode returns JSON even when no memory targets exist. | Yes | First-run UX should explain empty target state instead of failing. | Learning view can add more specific "apply skills first" wording later. |
| First implementation uses settings-backed scope instead of interactive scope picker. | Yes | Approved plan prioritized stable CLI contracts and view state first. | Add QuickPick or input controls after manual VS Code testing. |
| `reviewMaxSessions` default changed from 1 to 5. | Yes | Product UX requires useful first-run batches. | Reassess after manual Clearing review cost/timing. |

## Risks

- Progress events are UI state and do not replace durable report markdown.
- Apply-mode manual testing should start in a disposable project before Clearing.
- Python 3.11+ remains required; VS Code blockers need to stay explicit when users configure an older interpreter.

## Required Fixes Before Merge

None.

## Post-merge Follow-ups

- Add interactive lookback and max-session selection from the Learning view.
- Add direct patch preview commands for `artifact_written` patch paths.
- Reinstall the VSIX and run manual VS Code testing against a disposable project, then Clearing dry-run only.
- Add optional duplicate promotion cleanup/archive UX after validating the compacted Promotions view.
