# VS Code Extension UI and Public Distribution - PoC Plan

Last updated: 2026-04-25

## Mode

Fixture validation with current-code baseline inspection.

This PoC proves what can be proven before implementation planning: the existing GovKB CLI command surface, current non-JSON status/candidate behavior, low-cost memory-review wrapper support, and the proposed sanitized JSON contracts that the VS Code extension should consume after JSON CLI support is added.

## Evidence Strategy

- Inspect current Python command registration and command handlers under `src/govkb/`.
- Run current CLI help commands from `/home/ev/code/govkb` to prove the baseline command surface.
- Run targeted Python tests that already cover install, apply, init-kb/status health, candidates, and review-memory command wrapper behavior.
- Define sanitized JSON output fixtures under `poc-artifacts/` for future Python JSON CLI tests and TypeScript parser tests.
- Mark extension package, Workspace Trust, multi-root, and VSIX packaging assertions as planned until `vscode-extension/` exists.

## Assertions

| Assertion | Method | Command/File | Expected Result |
|---|---|---|---|
| A-01 CLI baseline exposes required commands | CLI help | From `/home/ev/code/govkb`: `PYTHONPATH=src python3 -m govkb.cli --help` plus subcommand help captured by `regenerate-poc-data.sh` | Help output includes `install`, `init-kb`, `validate`, `status`, `apply codex`, `review-memory`, and `candidates list`. |
| A-02 Current `status` command lacks durable JSON output | Source inspection and CLI help | `src/govkb/cli.py`, `src/govkb/commands/status.py`, `poc-artifacts/current-cli-baseline.txt` | Baseline confirms `status` prints human text and has no `--json` flag; implementation must add JSON mode. |
| A-03 Current `candidates list` command lacks durable JSON output | Source inspection and CLI help | `src/govkb/cli.py`, `src/govkb/commands/candidates.py`, `poc-artifacts/current-cli-baseline.txt` | Baseline confirms candidates list prints human text and has no `--json` flag; implementation must add JSON mode. |
| A-04 Existing Python setup/apply/candidate/review-memory behavior remains testable | Unit tests | From `/home/ev/code/govkb`: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests/test_install.py tests/test_apply.py tests/test_init_kb.py tests/test_candidates.py tests/test_review_memory_command.py -v` | Targeted tests pass before extension work begins. |
| A-05 Extension command construction must use argument arrays | Future TypeScript unit tests | `vscode-extension/src/test/govkbCli.test.ts` | Tests assert each command is represented as executable plus argument array, not a shell string. |
| A-06 Workspace Trust blocks execution and mutation before CLI invocation | Future TypeScript unit tests | `vscode-extension/src/test/trust.test.ts` | Untrusted workspace test records zero CLI invocations and one Workspace Trust action. |
| A-07 Missing runtime stops setup on exactly one blocker | Future TypeScript unit tests | `vscode-extension/src/test/setupFlow.test.ts` | Missing `govkb` command produces one install/configuration action and no project mutation command. |
| A-08 Memory-review dry-run defaults are commandable | Python wrapper test plus future TypeScript test | `tests/test_review_memory_command.py`, `vscode-extension/src/test/memoryReview.test.ts` | Model `gpt-5.4-mini`, reasoning `low`, timeout, dry-run, and no apply mode are asserted. |
| A-09 Reports parser uses sanitized report summaries only | Future TypeScript fixture test | `poc-artifacts/report-summary.sample.json`, `vscode-extension/src/test/reports.test.ts` | Summary includes counts and local report path but no raw transcript text. |
| A-10 VSIX packaging excludes private/generated state | Future packaging check | `vscode-extension/.vscodeignore`, `npx @vscode/vsce package --no-dependencies` | VSIX contains extension assets only and excludes Codex homes, reports, `.governed` project data, and generated test output. |
| A-11 Status JSON contract is stable enough for Python and TypeScript tests | Fixture inspection | `poc-artifacts/status.sample.json`, `poc-artifacts/json-cli-contracts.md` | Fixture covers project, validation, KB health, capabilities, adapters, release, and Codex install-state fields. |
| A-12 Candidates JSON contract is stable enough for Python and TypeScript tests | Fixture inspection | `poc-artifacts/candidates.sample.json`, `poc-artifacts/json-cli-contracts.md` | Fixture covers candidate id, status, occurrences, suggested capability id, activation state, and path. |
| A-13 Report summary contract avoids transcript leakage | Fixture inspection | `poc-artifacts/report-summary.sample.json`, `poc-artifacts/json-cli-contracts.md` | Fixture carries aggregate counts and report path only; `containsRawTranscript` is false. |
| A-14 Multi-root selection is explicit | Future TypeScript unit tests | `vscode-extension/src/test/projectSelection.test.ts` | Multiple candidate roots cause a single project-selection prompt before any CLI command runs. |

## Data And Fixtures

| Fixture | Purpose |
|---|---|
| `poc-artifacts/status.sample.json` | Candidate JSON contract for `govkb status --json`. |
| `poc-artifacts/candidates.sample.json` | Candidate JSON contract for `govkb candidates list --json`. |
| `poc-artifacts/report-summary.sample.json` | Candidate extension-side report summary contract. |
| `poc-artifacts/json-cli-contracts.md` | Human-readable contract notes for implementation planning. |
| `poc-artifacts/current-cli-baseline.txt` | Generated current CLI help baseline. |
| `poc-artifacts/targeted-python-tests.txt` | Generated targeted Python test output. |

## Rerun Command

From `/home/ev/code/govkb`:

```bash
bash docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/regenerate-poc-data.sh
```

The script writes only under `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/poc-artifacts/`.

## Risks And Blockers

| Risk / Blocker | Impact | Handling |
|---|---|---|
| `vscode-extension/` does not exist yet. | Workspace Trust, command construction, view parsing, settings, packaging, and multi-root assertions cannot be executed yet. | Carry these as implementation-plan tasks with explicit future tests. |
| JSON CLI output is not implemented yet. | Durable extension views cannot safely depend on current human CLI text. | Treat JSON output as Phase 0 or Phase 1 implementation prerequisite. |
| Report summaries may come from local Codex memory-review output. | Risk of copying raw local transcript content into extension state. | Use aggregate-only parser fixtures and never persist transcript text in extension state. |
| Marketplace identity is deferred. | Public Marketplace package cannot be finalized in first engineering slice. | Local VSIX can use provisional package metadata; public branding remains outside first slice. |

