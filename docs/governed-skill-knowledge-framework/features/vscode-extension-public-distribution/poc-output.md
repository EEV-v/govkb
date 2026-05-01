# VS Code Extension UI and Public Distribution - PoC Output

Last updated: 2026-04-25

## Summary

Phase 3 PoC is complete for the locked first slice.

The current GovKB Python CLI already exposes the command surface the extension needs to orchestrate, and targeted baseline tests pass. The PoC also confirms a current implementation gap: `govkb status` and `govkb candidates list` only expose human-readable output and do not yet provide a durable `--json` mode for extension views.

Sanitized JSON contract fixtures were added under `poc-artifacts/` so the implementation plan can make JSON CLI support a first prerequisite instead of letting the extension parse human CLI text.

## Run Metadata

| Field | Value |
|---|---|
| Working directory | `/home/ev/code/govkb` |
| Rerun command | `bash docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/regenerate-poc-data.sh` |
| Run status | Passed |
| Targeted Python tests | 33 tests passed |
| CLI baseline evidence | `poc-artifacts/current-cli-baseline.txt` |
| Test output evidence | `poc-artifacts/targeted-python-tests.txt` |

## Assertion Results

| Assertion | Result | Evidence | Notes |
|---|---|---|---|
| A-01 CLI baseline exposes required commands | Passed | `poc-artifacts/current-cli-baseline.txt` | Help output includes `install`, `init-kb`, `validate`, `status`, `apply codex`, `review-memory`, and `candidates list`. |
| A-02 Current `status` command lacks durable JSON output | Passed | `src/govkb/cli.py`, `src/govkb/commands/status.py`, `poc-artifacts/current-cli-baseline.txt` | Gap confirmed: `govkb status --help` has `--codex-home` only, no `--json`. |
| A-03 Current `candidates list` command lacks durable JSON output | Passed | `src/govkb/cli.py`, `src/govkb/commands/candidates.py`, `poc-artifacts/current-cli-baseline.txt` | Gap confirmed: `govkb candidates list --help` has no `--json`. |
| A-04 Existing Python setup/apply/candidate/review-memory behavior remains testable | Passed | `poc-artifacts/targeted-python-tests.txt` | `python3 -m unittest tests/test_install.py tests/test_apply.py tests/test_init_kb.py tests/test_candidates.py tests/test_review_memory_command.py -v` ran 33 tests successfully. |
| A-05 Extension command construction must use argument arrays | Not Run | Future `vscode-extension/src/test/govkbCli.test.ts` | Blocked until extension scaffold exists. |
| A-06 Workspace Trust blocks execution and mutation before CLI invocation | Not Run | Future `vscode-extension/src/test/trust.test.ts` | Blocked until extension scaffold exists. |
| A-07 Missing runtime stops setup on exactly one blocker | Not Run | Future `vscode-extension/src/test/setupFlow.test.ts` | Blocked until extension scaffold exists. |
| A-08 Memory-review dry-run defaults are commandable | Passed | `tests/test_review_memory_command.py`, `poc-artifacts/targeted-python-tests.txt` | Existing Python wrapper test proves low-cost classifier options are passed through. Extension settings test still needed. |
| A-09 Reports parser uses sanitized report summaries only | Not Run | `poc-artifacts/report-summary.sample.json` | Fixture exists; parser implementation is future work. |
| A-10 VSIX packaging excludes private/generated state | Not Run | Future `.vscodeignore` and package command | Blocked until extension scaffold exists. |
| A-11 Status JSON contract is stable enough for Python and TypeScript tests | Passed | `poc-artifacts/status.sample.json`, `poc-artifacts/json-cli-contracts.md` | Contract fixture covers project, validation, KB health, capabilities, adapters, release, and Codex install-state fields. |
| A-12 Candidates JSON contract is stable enough for Python and TypeScript tests | Passed | `poc-artifacts/candidates.sample.json`, `poc-artifacts/json-cli-contracts.md` | Contract fixture covers candidate id, status, occurrences, suggested capability id, activation state, and path. |
| A-13 Report summary contract avoids transcript leakage | Passed | `poc-artifacts/report-summary.sample.json`, `poc-artifacts/json-cli-contracts.md` | Contract fixture uses aggregate counts and local report path only. |
| A-14 Multi-root selection is explicit | Not Run | Future `vscode-extension/src/test/projectSelection.test.ts` | Blocked until extension scaffold exists. |

## Outliers

- `business.md` still describes Marketplace metadata as part of broad scope, but `scope-lock.md` and `spec-handoff.md` defer final public Marketplace branding. This PoC treats local VSIX packaging as first-slice scope and Marketplace publishing metadata as a later public-release gate.
- Current `govkb status` has useful human output and test coverage through `tests/test_init_kb.py`, but there is no dedicated `tests/test_status.py` yet. JSON status work should add focused tests rather than relying only on broader init-kb tests.
- `govkb candidates list` currently reads candidate TOML and prints compact text. JSON output should preserve the same source of truth and avoid adding extension-only candidate derivation.

## Open Gaps

| Gap | Required Next Handling |
|---|---|
| JSON mode for `status` and `candidates list` is absent. | Put JSON CLI support in the first implementation phase before durable extension views. |
| Extension package does not exist. | Scaffold `vscode-extension/` with tests for command construction, settings, trust, setup/apply flows, views, and packaging. |
| Report summary parser is not implemented. | Use sanitized fixture-driven TypeScript tests; do not copy raw transcript content into extension state. |
| VSIX package exclusion rules are not defined. | Add `.vscodeignore` and a local package verification command in the implementation plan. |

## Recommendation

Proceed to Phase 4 implementation planning.

The plan should start with a reusable JSON output layer in the Python CLI, then scaffold the VS Code extension as a thin argument-array command runner over that CLI. Production implementation should remain blocked until `review.md` says `Ready for Implementation: Yes`.

