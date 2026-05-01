# VS Code Extension UI and Public Distribution - Implementation Summary Phase 0

## Completed

- Added additive `--json` support for `govkb status`.
- Added additive `--json` support for `govkb candidates list`.
- Preserved existing human-readable output as the default.
- Added Python JSON contract tests for status and candidates.

## Files Changed

- `src/govkb/cli.py`
- `src/govkb/commands/status.py`
- `src/govkb/commands/candidates.py`
- `tests/test_status_json.py`
- `tests/test_candidates_json.py`

## Verification

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests/test_status_json.py tests/test_candidates_json.py tests/test_candidates.py -v`
- `PYTHONPATH=src python3 -m govkb.cli status /tmp/govkb-vscode-smoke.fgQkik/DemoProject --codex-home /tmp/govkb-vscode-smoke.fgQkik/codex-home --json`
- `PYTHONPATH=src python3 -m govkb.cli candidates list /tmp/govkb-vscode-smoke.fgQkik/DemoProject --json`

## Deviations From Plan

- None.

## Next Phase

Phase 1 - Core extension package.

