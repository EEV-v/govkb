# VS Code Learning Discovery and Progress - PoC Output

Last updated: 2026-05-10

## Summary

The baseline supports several pieces needed for a useful Learning UX:

- The CLI already has bounded review controls: `--dry-run`, `--lookback-days`, `--max-sessions`, and `--codex-timeout`.
- The memory-review adapter already has deterministic session selection helpers and synthetic tests for file-only discovery, missing index rows, retryable classifier failures, and candidate staging.
- The extension already delegates mutations to GovKB CLI commands, streams process output, summarizes reports, lists candidates, and rejects raw transcript report payloads.

The missing product contract is clear:

- No inventory-only CLI mode exists.
- No structured progress JSONL stream exists.
- No extension Learning view, inventory parser, or progress-event parser exists.
- Extension review settings expose max sessions and timeout but not lookback/window selection.

## Assertion Results

| Assertion | Result | Evidence | Notes |
|---|---|---|---|
| A1 Current CLI supports bounded review but not inventory/progress flags. | Passed | `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli review-memory --help` exited 0. | Help includes bounded review flags and has no `--inventory-json` or `--progress-jsonl`. |
| A2 Session discovery can run independently inside the adapter. | Passed | Targeted Python unittest with synthetic sessions exited 0. | `load_sessions` tests covered file-only fallback and missing indexed files. |
| A3 Classifier failures are categorized as deferred/retryable report outcomes. | Passed | Targeted Python unittest exited 0. | Timeout and usage-limit tests assert deferred rows and no staging. |
| A4 Public review-memory wrapper forwards bounded classifier options. | Passed | `tests.test_review_memory_command` exited 0. | Wrapper passes low-cost model/reasoning, timeout, classifier home, session file, and auto-promotion options. |
| A5 Extension command builder has bounded dry-run/apply wiring. | Passed | `npm test` in `/Users/vasilevevgeny/code/govkb/vscode-extension` exited 0 with 69 passing tests. | Existing coverage includes dry-run/apply command builders and flow behavior. |
| A6 Extension parser/view layer rejects raw report transcript summaries. | Passed | `npm test` in `/Users/vasilevevgeny/code/govkb/vscode-extension` exited 0 with 69 passing tests. | Existing JSON parser rejects raw transcript report summaries. |
| A7 Candidate Learning UX contract needs new fixtures and parsers. | Passed | Source inspection of `vscode-extension/src/types.ts`, `vscode-extension/src/jsonParsers.ts`, and `vscode-extension/src/views/**`. | No learning inventory/progress types or Learning view currently exist. |

## Command Results

Python evidence used the bundled Codex Python runtime because this shell's default `/usr/bin/python3` is Python 3.9.

Post-implementation note: `poc-evidence/` was regenerated after implementation, so the current evidence files now show the implemented `--inventory-json` and `--progress-jsonl` flags and the expanded extension test count. The baseline assertions below remain the pre-implementation PoC observations; final parity is recorded in `poc-parity-review.md`.

Generated evidence files are under `poc-evidence/`:

- `python-version.txt`
- `review-memory-help.txt`
- `python-targeted-tests.txt`
- `vscode-extension-tests.txt`
- `source-inventory.txt`

```text
Python 3.12.13
```

Targeted Python baseline:

```text
Ran 6 tests in 0.026s
OK
```

Extension baseline:

```text
tests 69
pass 69
fail 0
```

CLI help baseline:

```text
usage: govkb review-memory [-h] --assistant {codex}
                           [--project-root PROJECT_ROOT] [--dry-run]
                           [--lookback-days LOOKBACK_DAYS]
                           [--max-sessions MAX_SESSIONS] [--verbose]
                           [--codex-timeout CODEX_TIMEOUT]
                           [--classifier-codex-home CLASSIFIER_CODEX_HOME]
                           [--codex-model CODEX_MODEL]
                           [--codex-reasoning {low,medium,high,xhigh}]
                           [--session-file SESSION_FILE] [--no-auto-promote]
```

## Outliers

- Running `PYTHONPATH=src python3 -m govkb.cli review-memory --help` with `/usr/bin/python3` failed because Python 3.9 does not include `tomllib`. This is expected against the declared `requires-python = ">=3.11"` requirement, but the extension should surface this as a runtime blocker rather than a vague command failure.
- Passing TypeScript source test paths as extra arguments to the current `npm test` script caused Node to try importing uncompiled `.ts` paths. The reliable baseline command is the package script as written: `npm test`.

## Open Gaps

- Add inventory JSON CLI mode and Python tests proving it does not call nested Codex and does not mutate governed or assistant-local state.
- Add progress JSONL event emission with safe event payloads and Python tests for selected, skipped, classifying, classified, deferred, failed, artifact, and finished events.
- Add TypeScript types/parsers for learning inventory and progress events.
- Add a VS Code Learning view that combines inventory, active run state, existing skill memory updates, new candidates, reports, and next actions.
- Add extension settings/commands for lookback selection and first-run recommended batch scope.
- Add extension tests for zero-candidate but non-zero-learning output.

## Recommendation

Proceed to `implementation-plan.md`.

The plan should split implementation into four phases:

1. CLI inventory contract.
2. CLI progress event contract.
3. Extension parsers/commands/settings.
4. Learning view and refresh wiring.

This keeps governance intact because the extension remains a CLI orchestrator and the CLI remains the only owner of `.governed/**` and `$CODEX_HOME/**` mutations.
