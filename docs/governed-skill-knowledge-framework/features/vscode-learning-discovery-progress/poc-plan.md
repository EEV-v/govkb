# VS Code Learning Discovery and Progress - PoC Plan

Last updated: 2026-05-10

## Mode

baseline-vs-candidate

The PoC proves what the current GovKB CLI and VS Code extension already support, then identifies the missing contracts required for the candidate Learning UX.

## Evidence Strategy

- Use current source code and tests under `/Users/vasilevevgeny/code/govkb`.
- Use synthetic test fixtures already present in `tests/test_memory_review.py` and `vscode-extension/src/test/fixtures/**`.
- Avoid raw Codex session transcripts and avoid real `$CODEX_HOME` state.
- Prefer direct command output from the current checkout for CLI and extension behavior.
- Treat Python 3.11+ as a precondition because `pyproject.toml` declares `requires-python = ">=3.11"` and the code imports `tomllib`.

## Assertions

| Assertion | Method | Command/File | Expected Result |
|---|---|---|---|
| A1 Current CLI supports bounded review but not inventory/progress flags. | CLI help inspection | Working dir: `/Users/vasilevevgeny/code/govkb`; `PYTHONPATH=src <python3.11+> -m govkb.cli review-memory --help` | Help lists `--lookback-days`, `--max-sessions`, `--dry-run`, and `--codex-timeout`; help does not list `--inventory-json` or `--progress-jsonl`. |
| A2 Session discovery can run independently inside the adapter. | Existing unittest fixtures | Working dir: `/Users/vasilevevgeny/code/govkb`; `PYTHONPATH=src <python3.11+> -m unittest tests.test_memory_review.MemoryReviewHelperTests.test_packaged_scheduler_falls_back_to_file_only_sessions_when_index_is_missing tests.test_memory_review.MemoryReviewHelperTests.test_packaged_scheduler_skips_index_rows_without_session_files -v` | Adapter selects sessions and reports missing index rows without invoking classifier fixtures. |
| A3 Classifier failures are already categorized as deferred/retryable report outcomes. | Existing unittest fixtures | Working dir: `/Users/vasilevevgeny/code/govkb`; `PYTHONPATH=src <python3.11+> -m unittest tests.test_memory_review.MemoryReviewHelperTests.test_packaged_scheduler_defers_sessions_when_classifier_times_out tests.test_memory_review.MemoryReviewHelperTests.test_packaged_scheduler_defers_sessions_when_classifier_hits_usage_limit -v` | Timeout and usage-limit failures are deferred in report rows and do not stage candidates. |
| A4 Public review-memory wrapper forwards bounded classifier options. | Existing unittest fixtures | Working dir: `/Users/vasilevevgeny/code/govkb`; `PYTHONPATH=src <python3.11+> -m unittest tests.test_review_memory_command -v` | Wrapper forwards max sessions, timeout, model/reasoning, classifier home, session file, and auto-promotion options. |
| A5 Extension command builder has bounded dry-run/apply wiring. | Existing Node tests | Working dir: `/Users/vasilevevgeny/code/govkb/vscode-extension`; `npm test` | Extension tests pass and include dry-run/apply command builder coverage. |
| A6 Extension parser/view layer rejects raw report transcript summaries. | Existing Node tests | Working dir: `/Users/vasilevevgeny/code/govkb/vscode-extension`; `npm test` | Report summary parser rejects `containsRawTranscript = true`; report rows show aggregate counts only. |
| A7 Candidate Learning UX contract needs new fixtures and parsers. | Source inventory | Files: `vscode-extension/src/types.ts`, `vscode-extension/src/jsonParsers.ts`, `vscode-extension/src/views/**` | No `LearningInventory`, `LearningProgressEvent`, or `learningView` types/parsers/views exist yet. |

## Data And Fixtures

Existing sanitized fixture sources:

- `tests/test_memory_review.py` creates synthetic JSONL session files in temporary directories.
- `vscode-extension/src/test/fixtures/report-summary.sample.json` contains aggregate report metadata only.
- `vscode-extension/src/test/fixtures/candidates.sample.json` contains staged candidate summaries only.
- `vscode-extension/src/test/fixtures/status.sample.json` contains governed status and skill update state.

Candidate fixtures to add during implementation planning:

- `vscode-extension/src/test/fixtures/learning-inventory.sample.json`
- `vscode-extension/src/test/fixtures/learning-progress.sample.jsonl`
- Python-side synthetic session inventory fixtures covering indexed, file-only, processed, missing-file, and lookback-filtered sessions.

No real local session transcripts are required for this PoC.

## Candidate Contracts

Inventory payload shape for planning:

```json
{
  "schemaVersion": 1,
  "projectRoot": "/tmp/govkb-project",
  "codexHome": "/tmp/codex-home",
  "lookbackDays": 90,
  "maxSessions": 5,
  "sessions": {
    "totalDiscovered": 12,
    "selectedForReview": 5,
    "alreadyProcessed": 3,
    "indexedRows": 10,
    "indexedMissingFiles": 1,
    "fileOnlyRecentUnprocessed": 2
  },
  "recommendedBatch": {
    "lookbackDays": 90,
    "maxSessions": 5,
    "reason": "Review a bounded recent backfill before expanding scope."
  }
}
```

Progress JSONL event shape for planning:

```jsonl
{"event":"run_started","runId":"2026-05-10T130000Z","dryRun":true,"lookbackDays":90,"maxSessions":5}
{"event":"session_selected","runId":"2026-05-10T130000Z","sessionId":"session-1","threadName":"Feature planning","updatedAt":"2026-04-24T09:12:57Z","status":"queued"}
{"event":"session_classifying","runId":"2026-05-10T130000Z","sessionId":"session-1","status":"classifying"}
{"event":"session_classified","runId":"2026-05-10T130000Z","sessionId":"session-1","status":"classified","targetSkill":"project-knowledge-steward","lessonCount":2,"candidateCount":0,"confidence":0.91,"decision":"would-apply"}
{"event":"artifact_written","runId":"2026-05-10T130000Z","kind":"report","path":"/tmp/codex-home/memories/govkb/projects/demo/codex-memory-review/reports/2026-05-10T130000Z-report.md"}
{"event":"run_finished","runId":"2026-05-10T130000Z","reviewed":1,"skipped":0,"deferred":0,"failed":0,"existingSkillUpdates":2,"stagedCandidates":0}
```

The shapes intentionally omit raw transcript content and hidden reasoning.

## Rerun Command

Working dir: `/Users/vasilevevgeny/code/govkb`

```bash
./docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/regenerate-poc-data.sh
```

The script writes command output under `docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/poc-evidence/`.

## Risks And Blockers

- `python3` on this workstation resolves to Python 3.9, which is below the repo requirement. The script checks for Python 3.11+ and fails with a clear message if no suitable interpreter is available.
- Current CLI help proves that inventory/progress flags are absent; implementation must add the public contract before extension UI can depend on it.
- Progress JSONL should avoid mixing with human logs. Implementation planning must decide whether events go to stdout, stderr, or an explicit file path.
- Current `load_sessions` returns selected sessions and discovery stats, but not total discovered, already processed, or lookback-window alternatives. Inventory implementation must expand the returned metadata.
- Extension test targeting should use the existing `npm test` script or compiled `out/test/suite/*.test.js`; passing TypeScript source paths through `node --test` is not a supported targeted-test shape in the current package script.
